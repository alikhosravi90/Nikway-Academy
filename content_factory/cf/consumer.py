"""Local contract consumer. Not an installed Learning OS integration."""
import io
import json
import zipfile
from .store import canonical,sha,require
from .errors import DomainError

class LocalConsumer:
    def __init__(self,db): self.db=db

    def accept(self,ctx,event,fetch_manifest):
        require(ctx,'consumer')
        if event.get('schemaVersion')!='1.0.0' or event.get('type')!='content.candidate.prepared' or event.get('tenant')!=ctx.tenant:
            raise DomainError('unsupported event or tenant')
        try:
            eid=event['eventId']; payload=event['payload']; cid=payload['candidateId']
        except KeyError: raise DomainError('invalid event')
        manifest=fetch_manifest(cid)  # Fail closed on outage and current withdrawal.
        if manifest.get('schemaVersion')!='1.0.0' or manifest.get('status')!='candidate_local' or manifest.get('id')!=cid:
            raise DomainError('invalid manifest')
        if sha(canonical(manifest))!=payload.get('manifestDigest'): raise DomainError('manifest digest mismatch')
        digest=sha(canonical(event))
        with self.db.transaction(ctx) as c:
            inserted=c.execute('INSERT INTO receipts VALUES(%s,%s,%s) ON CONFLICT DO NOTHING RETURNING event_id',(ctx.tenant,eid,digest)).fetchone()
            row=c.execute('SELECT digest FROM receipts WHERE event_id=%s',(eid,)).fetchone()
            if row['digest']!=digest: raise DomainError('event replay conflict')
        return {'replayed':inserted is None,'candidateId':cid}

    def deliver(self,ctx,cid,fetch_manifest,fetch_package):
        require(ctx,'consumer')
        manifest=fetch_manifest(cid)  # Reauthorize every delivery; no offline fallback.
        if manifest.get('schemaVersion')!='1.0.0' or manifest.get('status')!='candidate_local' or manifest.get('id')!=cid:
            raise DomainError('unsupported manifest')
        payload=fetch_package(cid)
        if len(payload)>2_000_000: raise DomainError('package too large')
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as z:
                if set(z.namelist())!={'manifest.json','text.md','lesson.html','quiz.json'} or len(z.infolist())!=4 or sum(x.file_size for x in z.infolist())>4_000_000:
                    raise DomainError('invalid package members')
                m=json.loads(z.read('manifest.json'))
                if {k:m.get(k) for k in manifest}!=manifest or m.get('audience')!='learner': raise DomainError('package manifest mismatch')
                if set(m.get('files',{}))!={'text.md','lesson.html','quiz.json'}: raise DomainError('missing file checksums')
                if m['files']!=manifest.get('renditions',{}).get('learner'): raise DomainError('rendition binding mismatch')
                for name,digest in m['files'].items():
                    if sha(z.read(name))!=digest: raise DomainError('package integrity failure')
                quiz=json.loads(z.read('quiz.json'))
                if any('answer' in q or 'explanation' in q for item in quiz for q in item['questions']): raise DomainError('restricted answer in learner package')
        except (zipfile.BadZipFile,KeyError,ValueError,TypeError) as e:
            raise DomainError('invalid package') from e
        return payload
