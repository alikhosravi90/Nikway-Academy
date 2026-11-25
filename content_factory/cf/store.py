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

    def create_revision(self,ctx,data:ComponentInput,expected_revision:int):
        require(ctx,'author')
        payload=data.model_dump(); raw=canonical(payload)
        with self.db.transaction(ctx) as c:
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
        data.update(revisionId=rid,revisionNumber=row['number'],checksum=row['digest'],reviewStatus=row['state'],creator=row['creator'],publishedAt=None,deprecatedAt=None)
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
