from contextlib import nullcontext
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4
from psycopg.types.json import Jsonb
from .contracts import ComponentInput
from .errors import DomainError

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()

def sha(data): return hashlib.sha256(data).hexdigest()

def require(ctx,*roles):
    if ctx.role not in roles: raise DomainError('role not permitted',403)

class Repository:
    def __init__(self,db,root):
        self.db=db; self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)

    def object_path(self,tenant,digest):
        # Tenant name is never interpolated into a path.
        return self.root/sha(tenant.encode())/digest

    def put_object(self,tenant,data):
        digest=sha(data); p=self.object_path(tenant,digest)
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():
            if p.read_bytes()!=data: raise DomainError('object integrity failure')
            return digest
        temp=p.with_name('.'+str(uuid4()))
        try:
            with temp.open('xb') as f:
                f.write(data); f.flush(); os.fsync(f.fileno())
            try: os.link(temp,p)  # Never replace an existing object.
            except FileExistsError:
                if p.read_bytes()!=data: raise DomainError('object integrity failure')
        finally:
            temp.unlink(missing_ok=True)
        return digest

    def event(self,c,ctx,name,payload):
        eid=str(uuid4())
        envelope={'schemaVersion':'1.0.0','eventId':eid,'type':name,'tenant':ctx.tenant,'payload':payload}
        c.execute('INSERT INTO events VALUES(%s,%s,%s,now())',(ctx.tenant,eid,Jsonb(envelope)))
        return envelope

    def create_revision(self,ctx,data:ComponentInput,expected_revision:int,connection=None):
        require(ctx,'author')
        payload=data.model_dump(); raw=canonical(payload)
        with (nullcontext(connection) if connection is not None else self.db.transaction(ctx)) as c:
            c.execute('INSERT INTO heads(tenant,component_id) VALUES(%s,%s) ON CONFLICT DO NOTHING',(ctx.tenant,data.id))
            head=c.execute('SELECT number FROM heads WHERE component_id=%s FOR UPDATE',(data.id,)).fetchone()
            if head['number']!=expected_revision: raise DomainError('stale revision')
            for rid in data.derivedFrom+data.prerequisiteIds:
                self._read(c,ctx,rid)
            existing=c.execute('SELECT semantic_version FROM revisions WHERE component_id=%s ORDER BY number DESC LIMIT 1',(data.id,)).fetchone()
            if existing and tuple(map(int,data.semanticVersion.split('.'))) <= tuple(map(int,existing['semantic_version'].split('.'))):
                raise DomainError('semantic version must increase')
            digest=self.put_object(ctx.tenant,raw)
            rid=str(uuid4()); number=head['number']+1
            c.execute('INSERT INTO revisions(tenant,revision_id,component_id,number,semantic_version,digest,title,creator) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',(ctx.tenant,rid,data.id,number,data.semanticVersion,digest,data.title,ctx.subject))
            c.execute("INSERT INTO states(tenant,revision_id,state) VALUES(%s,%s,'draft')",(ctx.tenant,rid))
            c.execute('UPDATE heads SET number=%s WHERE component_id=%s',(number,data.id))
            self.event(c,ctx,'component.revision.created',{'revisionId':rid,'checksum':digest})
            return self._read(c,ctx,rid)

    def _read(self,c,ctx,rid):
        row=c.execute('SELECT r.*,s.state,s.reviewer FROM revisions r JOIN states s USING(tenant,revision_id) WHERE revision_id=%s',(rid,)).fetchone()
        if not row: raise DomainError('revision not found',404)
        try: raw=self.object_path(ctx.tenant,row['digest']).read_bytes()
        except FileNotFoundError: raise DomainError('object integrity failure: missing')
        if sha(raw)!=row['digest']: raise DomainError('object integrity failure: digest')
        data=json.loads(raw)
        data.update(revisionId=rid,revisionNumber=row['number'],checksum=row['digest'],reviewStatus=row['state'],creator=row['creator'],publishedAt=None,deprecatedAt=None,mediaRefs=[])
        return data

    def get_revision(self,ctx,rid):
        require(ctx,'author','reviewer')
        with self.db.transaction(ctx) as c: return self._read(c,ctx,rid)

    def review(self,ctx,rid,note):
        require(ctx,'reviewer')
        if not note.strip(): raise DomainError('review note required')
        with self.db.transaction(ctx) as c:
            c.execute('SELECT state FROM states WHERE revision_id=%s FOR UPDATE',(rid,))
            data=self._read(c,ctx,rid)
            if data['creator']==ctx.subject: raise DomainError('independent reviewer required',403)
            if data['reviewStatus']!='draft': raise DomainError('only draft can be reviewed')
            if data['rightsStatus']=='unknown' or data['license']=='UNKNOWN' or any(p['rights']=='unknown' for p in data['provenance']):
                raise DomainError('unresolved rights')
            if not all(data['accessibility'].values()): raise DomainError('accessibility check incomplete')
            c.execute("UPDATE states SET state='approved_local',reviewer=%s,note=%s,changed_at=now() WHERE revision_id=%s",(ctx.subject,note,rid))
            self.event(c,ctx,'component.revision.approved_local',{'revisionId':rid,'checksum':data['checksum'],'reviewer':ctx.subject,'note':note})
            return self._read(c,ctx,rid)

    def withdraw(self,ctx,rid,note):
        require(ctx,'reviewer')
        if not note.strip(): raise DomainError('withdrawal reason required')
        with self.db.transaction(ctx) as c:
            self._read(c,ctx,rid)
            c.execute("UPDATE states SET state='withdrawn',note=%s,changed_at=now() WHERE revision_id=%s",(note,rid))
            affected=c.execute('SELECT candidate_id FROM usages WHERE revision_id=%s',(rid,)).fetchall()
            self.event(c,ctx,'component.revision.withdrawn',{'revisionId':rid,'affected':[x['candidate_id'] for x in affected],'reason':note})
            return affected

    def search(self,ctx,query):
        require(ctx,'author','reviewer')
        with self.db.transaction(ctx) as c:
            return c.execute('SELECT revision_id,title,number FROM revisions WHERE title ILIKE %s ORDER BY component_id,number',('%'+query+'%',)).fetchall()

    def _dependencies(self,c,ctx,rids):
        found={}
        pending=list(rids)
        while pending:
            rid=pending.pop()
            if rid in found: continue
            # Lock state until the candidate transaction ends, including withdrawal races.
            c.execute('SELECT state FROM states WHERE revision_id=%s FOR SHARE',(rid,))
            data=self._read(c,ctx,rid)
            if data['reviewStatus']!='approved_local': raise DomainError('dependency not approved or withdrawn')
            found[rid]=data
            if len(found)>100: raise DomainError('dependency graph exceeds local limit')
            pending.extend(data['derivedFrom']+data['prerequisiteIds'])
        return found

    def prepare(self,ctx,course_id,rids,key,connection=None):
        require(ctx,'reviewer')
        if not course_id.strip() or not key.strip() or not rids or len(rids)!=len(set(rids)) or len(rids)>30:
            raise DomainError('invalid candidate request')
        request_digest=sha(canonical({'course':course_id,'revisions':rids}))
        with (nullcontext(connection) if connection is not None else self.db.transaction(ctx)) as c:
            c.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(ctx.tenant+':'+key,))
            existing=c.execute('SELECT manifest,request_digest FROM candidates WHERE request_key=%s',(key,)).fetchone()
            if existing:
                if existing['request_digest']!=request_digest: raise DomainError('idempotency key payload conflict')
                self._dependencies(c,ctx,[x['revisionId'] for x in existing['manifest']['dependencies']])
                return existing['manifest']
            deps=self._dependencies(c,ctx,rids)
            cid=str(uuid4())
            ref=lambda r:{'id':r['id'],'revisionId':r['revisionId'],'semanticVersion':r['semanticVersion'],'checksum':r['checksum']}
            manifest={'schemaVersion':'1.0.0','id':cid,'courseId':course_id,'status':'candidate_local','publication':'NOT_RELEASED','components':[ref(deps[r]) for r in rids],'dependencies':[ref(deps[r]) for r in sorted(deps)],'recipeVersion':'1.0.0'}
            from .render import build_package
            manifest['renditions']={}
            for audience in ('learner','instructor'):
                parts=build_package(manifest,[deps[r] for r in rids],instructor=audience=='instructor')
                manifest['renditions'][audience]={k:sha(v) for k,v in parts.items() if k!='manifest.json'}
            c.execute('INSERT INTO candidates(tenant,candidate_id,course_id,manifest,request_key,request_digest) VALUES(%s,%s,%s,%s,%s,%s)',(ctx.tenant,cid,course_id,Jsonb(manifest),key,request_digest))
            for rid in deps:
                c.execute('INSERT INTO usages VALUES(%s,%s,%s)',(ctx.tenant,cid,rid))
            self.event(c,ctx,'content.candidate.prepared',{'candidateId':cid,'manifestDigest':sha(canonical(manifest))})
            return manifest

    def _candidate(self,c,ctx,cid):
        row=c.execute('SELECT manifest FROM candidates WHERE candidate_id=%s',(cid,)).fetchone()
        if not row: raise DomainError('candidate not found',404)
        m=row['manifest']; self._dependencies(c,ctx,[x['revisionId'] for x in m['dependencies']])
        return m

    def candidate(self,ctx,cid):
        with self.db.transaction(ctx) as c: return self._candidate(c,ctx,cid)

    def package(self,ctx,cid):
        from .render import build_package, zip_package
        with self.db.transaction(ctx) as c:
            m=self._candidate(c,ctx,cid)
            contents=[self._read(c,ctx,r['revisionId']) for r in m['components']]
            return zip_package(build_package(m,contents,instructor=ctx.role in ('author','reviewer')))

    def events(self,ctx):
        require(ctx,'author','reviewer','consumer')
        with self.db.transaction(ctx) as c:
            rows=c.execute('SELECT payload FROM events ORDER BY created_at,event_id').fetchall()
            # Consumer gets delivery events only; never editorial notes or source evidence.
            return [r['payload'] for r in rows if ctx.role!='consumer' or r['payload']['type']=='content.candidate.prepared']
