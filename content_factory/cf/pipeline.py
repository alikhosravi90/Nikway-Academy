from uuid import uuid4
from psycopg.types.json import Jsonb
from .contracts import ComponentInput
from .store import require
from .errors import DomainError

class Pipeline:
    def __init__(self,repo): self.repo=repo

    def plan(self,ctx,component:ComponentInput,objective):
        require(ctx,'author')
        if not objective.strip(): raise DomainError('objective required')
        rid=str(uuid4()); data={'id':rid,'objective':objective,'component':component.model_dump(),'owner':ctx.subject}
        with self.repo.db.transaction(ctx) as c:
            c.execute("INSERT INTO pipeline_runs VALUES(%s,%s,'planned',%s)",(ctx.tenant,rid,Jsonb(data)))
            self.repo.event(c,ctx,'pipeline.planned',{'runId':rid})
        return {**data,'state':'planned'}

    def _load(self,c,run_id,state):
        row=c.execute('SELECT * FROM pipeline_runs WHERE run_id=%s FOR UPDATE',(run_id,)).fetchone()
        if not row: raise DomainError('pipeline not found',404)
        if row['state']!=state: raise DomainError('invalid PDCA transition')
        return row['data']

    def _save(self,c,ctx,data,state):
        c.execute('UPDATE pipeline_runs SET state=%s,data=%s WHERE run_id=%s',(state,Jsonb(data),data['id']))
        self.repo.event(c,ctx,'pipeline.'+state,{'runId':data['id']})
        return {**data,'state':state}

    def do(self,ctx,run_id):
        require(ctx,'author')
        with self.repo.db.transaction(ctx) as c:
            data=self._load(c,run_id,'planned')
            if data['owner']!=ctx.subject: raise DomainError('pipeline owner required',403)
            r=self.repo.create_revision(ctx,ComponentInput(**data['component']),0,connection=c)
            data['revisionId']=r['revisionId']
            return self._save(c,ctx,data,'produced')

    def check(self,ctx,run_id):
        require(ctx,'author','reviewer')
        with self.repo.db.transaction(ctx) as c:
            data=self._load(c,run_id,'produced')
            r=self.repo._read(c,ctx,data['revisionId'])
            checks={'rights':r['rightsStatus']!='unknown' and r['license']!='UNKNOWN' and all(x['rights']!='unknown' for x in r['provenance']), 'accessibility':all(r['accessibility'].values()),'outcomes':all(q['outcomeId'] in r['learningOutcomeIds'] for q in r['body']['questions']), 'integrity':True}
            data['checks']={**checks,'passed':all(checks.values()),'humanReview':'PENDING'}
            return self._save(c,ctx,data,'checked')

    def act(self,ctx,run_id,course_id,key):
        require(ctx,'reviewer')
        with self.repo.db.transaction(ctx) as c:
            data=self._load(c,run_id,'checked')
            if not data['checks']['passed']: raise DomainError('PDCA checks failed; revise plan')
            m=self.repo.prepare(ctx,course_id,[data['revisionId']],key,connection=c)
            data['candidateId']=m['id']; self._save(c,ctx,data,'acted')
            return m
