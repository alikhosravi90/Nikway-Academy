"""Run the PDCA example through the actual local HTTP API; never publish."""
import io
import json
from pathlib import Path
import sys
from uuid import uuid4
import zipfile
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.local import load,ROOT
from cf.db import Database
from cf.consumer import LocalConsumer
from cf.contracts import ComponentInput
from cf.store import sha,canonical


def run(destination):
    cfg=load(); dest=Path(destination); dest.mkdir(parents=True,exist_ok=True)
    fixture=json.loads((ROOT/'fixtures/pdca.json').read_text()); fixture['id']='pdca-'+uuid4().hex[:10]
    base='http://127.0.0.1:18500'
    client=httpx.Client(base_url=base,timeout=15)
    def call(method,path,role='author',body=None,raw=False):
        response=client.request(method,path,headers={'Authorization':'Bearer '+cfg['tokens'][role]},json=body)
        response.raise_for_status()
        return response.content if raw else response.json()
    run=call('POST','/v1/pipelines',body={'component':fixture,'objective':'آزمایش تولید درس، متن و آزمون PDCA با استفاده مجدد در دو دوره'})
    produced=call('POST',f"/v1/pipelines/{run['id']}/do")
    checked=call('POST',f"/v1/pipelines/{run['id']}/check")
    rid=produced['revisionId']
    call('POST',f'/v1/revisions/{rid}/review','reviewer',{'note':'Automated synthetic local fixture review only; human editorial/rights gate remains pending.'})
    a=call('POST',f"/v1/pipelines/{run['id']}/act",'reviewer',{'courseId':'continuous-improvement-foundations','idempotencyKey':str(uuid4())})
    b=call('POST','/v1/candidates','reviewer',{'courseId':'practical-process-improvement','revisionIds':[rid],'idempotencyKey':str(uuid4())})
    db=Database(cfg['database']); consumer=LocalConsumer(db); ctx=db.authenticate(cfg['tokens']['consumer'])
    event=next(x for x in call('GET','/v1/events','consumer') if x['payload']['candidateId']==a['id'])
    fetch=lambda cid:call('GET','/v1/candidates/'+cid,'consumer')
    first=consumer.accept(ctx,event,fetch); replay=consumer.accept(ctx,event,fetch)
    package=consumer.deliver(ctx,a['id'],fetch,lambda cid:call('GET','/v1/candidates/'+cid+'/package','consumer',raw=True))
    (dest/'pdca-learner-candidate.zip').write_bytes(package)
    instructor=call('GET','/v1/candidates/'+a['id']+'/package','reviewer',raw=True)
    (dest/'pdca-instructor-candidate.zip').write_bytes(instructor)
    with zipfile.ZipFile(io.BytesIO(package)) as z:
        for name in ('lesson.html','text.md','quiz.json','manifest.json'): (dest/name).write_bytes(z.read(name))
    # New revision must not alter either existing course's pinned dependency.
    fixture['semanticVersion']='1.0.1'; fixture['body']['summary']+=' نسخه دوم برای آزمون پایداری ارجاع دوره‌ها.'
    updated=call('POST','/v1/components',body={'component':fixture,'expectedRevision':1})
    unchanged=fetch(a['id'])['components']==a['components'] and fetch(b['id'])['components']==b['components']
    report={'scope':'REAL_LOCAL_HTTP_SYNTHETIC_CONTENT','publication':'NOT_RELEASED','pipelineRun':run['id'],'pdcaCheck':checked['checks'],'revisionId':rid,'newRevisionId':updated['revisionId'],'courses':[a,b],'sameRevisionInTwoCourses':a['components']==b['components'],'pinnedAfterUpdate':unchanged,'consumer':{'kind':'LOCAL_CONTRACT_ADAPTER_NOT_RUNNING_LEARNING_OS','first':first,'replay':replay},'files':{p.name:sha(p.read_bytes()) for p in dest.iterdir() if p.is_file() and p.name!='demo-evidence.json'},'humanApproval':'PENDING'}
    (dest/'demo-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    (ROOT/'evidence/local-http-demo.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'sameRevisionInTwoCourses':report['sameRevisionInTwoCourses'],'pinnedAfterUpdate':unchanged,'candidateIds':[a['id'],b['id']],'publication':'NOT_RELEASED'},indent=2))

if __name__=='__main__': run(sys.argv[1] if len(sys.argv)>1 else ROOT/'.runtime/demo')
