#!/usr/bin/env python3
"""Real candidate API/DB verification; exact UUID fixtures only; no membership mutation."""
import concurrent.futures
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import urllib.request
import urllib.error
from uuid import uuid4
ROOT=Path(os.environ['ACADEMY_RUNTIME_ROOT'])
sys.path.insert(0,str(ROOT))
from content.validate_package import compute_digest
spec=importlib.util.spec_from_file_location('live_helper',ROOT/'backend/tests/test_integration.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
checks=[]; package_ids=[]; course_ids=[]
def check(label,actual,expected):
    if actual!=expected: raise AssertionError(f'{label}: expected {expected}, got {actual}')
    checks.append(label)
def raw(body,token=None,path='/api/content-packages'):
    headers={'Content-Type':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    req=urllib.request.Request(h.API+path,body,headers)
    try:r=urllib.request.urlopen(req,timeout=20)
    except urllib.error.HTTPError as e:r=e
    data=r.read()
    try:value=json.loads(data)
    except ValueError:value=None
    return r.status,value

def send(p,token):return raw(json.dumps(p,ensure_ascii=False).encode(),token)
def resign(p):p['integrity']['digest']=compute_digest(p);return p

tokens={name:h.login(name)['access_token'] for name in ('reviewer-a','learner-a','learner-b')}
r,a,b=[tokens[n] for n in ('reviewer-a','learner-a','learner-b')]
p=json.loads((ROOT/'content/examples/agent-engineering-basics.fa.json').read_text())
p['packageId']=str(uuid4());resign(p)
try:
    check('anonymous admission',send(p,None)[0],401)
    check('learner admission',send(p,a)[0],403)
    for label,payload,expected in [('duplicate keys',b'{"x":1,"x":2}',422),('nonobject',b'[]',422),('deep JSON',b'{"x":'+b'['*2000+b'0'+b']'*2000+b'}',422),('oversize',b' '*(131073),413)]:
        check(label,raw(payload,r)[0],expected)
    bad=copy.deepcopy(p);bad['course']['title']='tampered'
    check('checksum tamper',send(bad,r)[0],422)
    bad=copy.deepcopy(p);bad['tenantId']=h.B;resign(bad)
    check('caller tenant field',send(bad,r)[0],422)
    bad=copy.deepcopy(p);bad['course']['title']='title\x00invalid';resign(bad)
    check('PostgreSQL NUL rejection',send(bad,r)[0],422)
    bad=copy.deepcopy(p);bad['version']='1'*1000+'.0.0';resign(bad)
    check('indexed version bound',send(bad,r)[0],422)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        imports=list(pool.map(lambda _:send(p,r),range(4)))
    check('concurrent import statuses',[s for s,_ in imports],[200]*4)
    check('exactly one import effect',sum(not x['replayed'] for _,x in imports),1)
    check('same imported package',len({x['id'] for _,x in imports}),1)
    status,item=imports[0];check('draft import',status,200);package_ids.append(item['id'])
    check('draft state',item['status'],'draft')
    check('import replay',send(p,r)[1]['replayed'],True)
    bad=copy.deepcopy(p);bad['course']['title']='conflicting immutable revision';resign(bad)
    check('version digest conflict',send(bad,r)[0],409)
    path='/api/content-packages/'+item['id']+'/publish'
    intent={'expected_digest':item['digest'],'expected_revision':1}
    check('learner publication',h.request(path,a,intent)[0],403)
    check('stale publish',h.request(path,r,dict(intent,expected_revision=8))[0],409)
    check('wrong digest',h.request(path,r,dict(intent,expected_digest='0'*64))[0],409)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        publications=list(pool.map(lambda _:h.request(path,r,intent),range(4)))
    check('concurrent publish statuses',[s for s,_ in publications],[200]*4)
    check('exactly one publish effect',sum(not x['replayed'] for _,x in publications),1)
    course=publications[0][1]['course_id'];course_ids.append(course)
    check('same published course',len({x['course_id'] for _,x in publications}),1)
    check('cross tenant export',h.request('/api/courses/'+course+'/package',b)[0],404)
    check('exact export',h.request('/api/courses/'+course+'/package',a)[1],p)
    status,courses=h.request('/api/courses',a);check('course listing',status,200)
    entry=next(c for c in courses if c['id']==course)
    check('metadata objectives',entry['metadata']['objectives'],p['course']['objectives'])
    check('lesson text',entry['lessons'][0]['content'],p['course']['lessons'][0]['content'])
    check('enroll',h.request('/api/courses/'+course+'/enroll',a,{})[0],200)
    for lesson in entry['lessons']:
        check('complete '+str(lesson['position']),h.request(f'/api/courses/{course}/lessons/{lesson["id"]}/complete',a,{})[0],200)
    check('configured assessment minimum',h.request('/api/courses/'+course+'/submissions',a,{'content':'x'*40})[0],422)
    check('assessment maximum exceeded',h.request('/api/courses/'+course+'/submissions',a,{'content':'ش'*10001})[0],422)
    check('valid maximum Persian assessment',h.request('/api/courses/'+course+'/submissions',a,{'content':'ش'*10000})[0],200)
    status,tool=h.request('/api/tools/invoke',a,{'name':'learning.progress','arguments':{}})
    check('bounded progress tool succeeds',status,200)
    check('progress tool version',tool['version'],'2')
    check('progress tool aggregate-only shape',set(tool['result']),{'enrolled_courses','completed_lessons','submission_records_by_status','scope'})
    check('progress tool small result',len(json.dumps(tool).encode())<2048,True)
    expected_count=int(h.sql(f"SELECT count(*) FROM completions c JOIN enrollments e ON c.enrollment_id=e.id WHERE e.subject='{h.SA}';").stdout.strip())
    check('progress tool actual own count',tool['result']['completed_lessons'],expected_count)
    # Published rows are immutable under actual application role.
    result=h.sql(f"BEGIN; SET LOCAL ROLE academy_app; SET LOCAL app.subject='00000000-0000-4000-8000-000000000003'; SET LOCAL app.tenant_id='{h.A}'; UPDATE content_packages SET revision=999 WHERE id='{item['id']}'; ROLLBACK;")
    check('published update denied by RLS','UPDATE 0' in result.stdout,True)
    result=h.sql(f"BEGIN; SET LOCAL ROLE academy_app; SET LOCAL app.subject='{h.SA}'; SET LOCAL app.tenant_id='{h.A}'; INSERT INTO courses(id,tenant_id,title,description) VALUES('{uuid4()}','{h.A}','Forbidden','Synthetic'); ROLLBACK;",check=False)
    check('learner direct catalog insert denied',result.returncode!=0,True)
    new=copy.deepcopy(p);new['version']='1.0.1';resign(new)
    status,next_item=send(new,r);check('new version import',status,200);package_ids.append(next_item['id'])
    status,published=h.request('/api/content-packages/'+next_item['id']+'/publish',r,{'expected_digest':next_item['digest'],'expected_revision':1})
    check('new version publish',status,200);course_ids.append(published['course_id'])
    check('new version separate course',published['course_id']!=course,True)
    check('old version unchanged',h.request('/api/courses/'+course+'/package',a)[1],p)
finally:
    # Recover all rows for this run's unique portable package identity, even after assertion failure.
    for owned_id in h.sql(f"SELECT id FROM content_packages WHERE package_id='{p['packageId']}';").stdout.splitlines():
        if owned_id and owned_id not in package_ids: package_ids.append(owned_id)
    if package_ids or course_ids:
        for pid in package_ids:
            owned=h.sql(f"SELECT course_id FROM content_packages WHERE id='{pid}' AND course_id IS NOT NULL;").stdout.strip()
            if owned and owned not in course_ids: course_ids.append(owned)
        commands=[]
        for c in course_ids:
            commands.extend([f"DELETE FROM completions WHERE enrollment_id IN (SELECT id FROM enrollments WHERE course_id='{c}')",f"DELETE FROM submissions WHERE course_id='{c}'",f"DELETE FROM enrollments WHERE course_id='{c}'"])
        for pid in package_ids:commands.append(f"DELETE FROM content_packages WHERE id='{pid}'")
        for c in course_ids:commands.extend([f"DELETE FROM lessons WHERE course_id='{c}'",f"DELETE FROM courses WHERE id='{c}'"])
        h.sql('BEGIN; '+'; '.join(commands)+'; COMMIT;')
        for pid in package_ids:check('exact package cleanup',h.sql(f"SELECT count(*) FROM content_packages WHERE id='{pid}';").stdout.strip(),'0')
print(json.dumps({'result':'PASS','checks':checks,'check_count':len(checks),'scope':'real loopback candidate API/Keycloak/Postgres; exact-owned fixtures removed; audit retained'},indent=2))
