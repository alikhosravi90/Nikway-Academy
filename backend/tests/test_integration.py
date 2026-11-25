"""Real loopback API + Keycloak PKCE + PostgreSQL security checks.
Run: ACADEMY_RUNTIME_ROOT=/path/to/runtime/checkout python3 -m unittest discover -s backend/tests -p test_integration.py -v
No tokens/passwords are printed or persisted. Only synthetic local fixture data is changed.
"""
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import html
import http.cookiejar
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import unittest
import urllib.error
import urllib.parse
import urllib.request
from uuid import uuid4

ROOT = Path(os.environ.get('ACADEMY_RUNTIME_ROOT', Path(__file__).resolve().parents[2]))
API = 'http://localhost:18400'
IDP = 'http://localhost:18480/realms/academy/protocol/openid-connect'
A = '10000000-0000-4000-8000-000000000001'
B = '10000000-0000-4000-8000-000000000002'
SA = '00000000-0000-4000-8000-000000000001'
SB = '00000000-0000-4000-8000-000000000002'

class LocalCookiePolicy(http.cookiejar.DefaultCookiePolicy):
    def return_ok_secure(self, cookie, request):
        # Match browser secure-context exception for loopback development only.
        if urllib.parse.urlsplit(request.full_url).hostname == 'localhost':
            return True
        return super().return_ok_secure(cookie,request)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def login(name):
    creds = json.loads((ROOT/'infra/runtime/credentials.json').read_text())[name]
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    state = secrets.token_urlsafe(16)
    redirect = 'http://localhost:18401/'
    query = urllib.parse.urlencode(dict(client_id='academy-web',redirect_uri=redirect,response_type='code',scope='openid',code_challenge=challenge,code_challenge_method='S256',state=state))
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar(policy=LocalCookiePolicy())),NoRedirect())
    response = opener.open(IDP+'/auth?'+query,timeout=15)
    page = response.read().decode()
    match = re.search(r'<form[^>]+action="([^"]+)"',page)
    if not match:
        raise RuntimeError('OIDC login form missing')
    action = html.unescape(match.group(1))
    data = urllib.parse.urlencode({'username':creds['username'],'password':creds['password'],'credentialId':''}).encode()
    try:
        response = opener.open(action,data,timeout=15)
    except urllib.error.HTTPError as error:
        if error.code not in (302,303):
            message = re.sub(r'<script\b[^>]*>.*?</script>', '', error.read().decode(), flags=re.S)
            message = re.sub('<[^>]*>', ' ', message)
            raise RuntimeError('OIDC login failed: '+' '.join(message.split())[:800]) from None
        response = error
    location = response.headers.get('Location','')
    values = urllib.parse.parse_qs(urllib.parse.urlsplit(location).query)
    if values.get('state') != [state] or 'code' not in values:
        raise RuntimeError('OIDC authorization code/state missing')
    payload = urllib.parse.urlencode(dict(grant_type='authorization_code',client_id='academy-web',code=values['code'][0],redirect_uri=redirect,code_verifier=verifier)).encode()
    return json.load(opener.open(IDP+'/token',payload,timeout=15))

def request(path, token=None, payload=None, method=None):
    headers = {'Content-Type':'application/json'}
    if token: headers['Authorization'] = 'Bearer '+token
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(API+path,data,headers,method=method)
    try:
        response = urllib.request.urlopen(req,timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    raw = response.read()
    try: result=json.loads(raw)
    except json.JSONDecodeError: result={'non_json':True}
    return response.status,result

def sql(statement, check=True):
    result = subprocess.run([str(ROOT/'scripts/local-compose.sh'),'exec','-T','postgres','psql','-U','postgres','-d','academy','-At','-v','ON_ERROR_STOP=1','-c',statement],capture_output=True,text=True,timeout=20)
    if check and result.returncode:
        raise RuntimeError('Synthetic SQL fixture failed: '+result.stderr[-500:])
    return result

class RealIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sessions = {name:login(name) for name in ('learner-a','learner-b','reviewer-a')}
        cls.tokens = {name:session['access_token'] for name,session in sessions.items()}
        cls.id_token = sessions['learner-a']['id_token']
        cls.course,cls.first,cls.second,cls.workshop = [str(uuid4()) for _ in range(4)]
        cls.foreign_submission_ids = []
        sql(f"INSERT INTO courses VALUES ('{cls.course}','{A}','Integration fixture','Synthetic independent test'); INSERT INTO lessons VALUES ('{cls.first}','{A}','{cls.course}',1,'Observe','Synthetic'),('{cls.second}','{A}','{cls.course}',2,'Reflect','Synthetic'); INSERT INTO workshops VALUES ('{cls.workshop}','{A}','Capacity fixture','Synthetic independent test',1,now());")

    @classmethod
    def tearDownClass(cls):
        # Only UUIDs minted by this run; never delete seeded/catalog-wide data.
        foreign = ''.join(f"DELETE FROM submissions WHERE id='{sid}';" for sid in cls.foreign_submission_ids)
        sql(f"BEGIN; {foreign} DELETE FROM completions WHERE enrollment_id IN (SELECT id FROM enrollments WHERE course_id='{cls.course}'); DELETE FROM submissions WHERE course_id='{cls.course}'; DELETE FROM enrollments WHERE course_id='{cls.course}'; DELETE FROM lessons WHERE course_id='{cls.course}'; DELETE FROM courses WHERE id='{cls.course}'; DELETE FROM registrations WHERE workshop_id='{cls.workshop}'; DELETE FROM workshops WHERE id='{cls.workshop}'; COMMIT;")
        remaining = sql(f"SELECT (SELECT count(*) FROM courses WHERE id='{cls.course}')+(SELECT count(*) FROM workshops WHERE id='{cls.workshop}');").stdout.strip()
        if remaining != '0': raise AssertionError('Test fixture cleanup incomplete')
        # Audit records remain append-only and contain no evidence body/password/token.

    def test_01_identity_and_tenant_boundary(self):
        self.assertEqual(request('/api/me')[0],401)
        self.assertEqual(request('/api/me','invalid')[0],401)
        self.assertEqual(request('/api/me',self.id_token)[0],401)  # genuine Keycloak signature, wrong API audience
        token=self.tokens['learner-a']; chunks=token.split('.')
        claims=json.loads(base64.urlsafe_b64decode(chunks[1]+'==='));claims['sub']=SB
        chunks[1]=base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')
        self.assertEqual(request('/api/me','.'.join(chunks))[0],401)
        for user,tenant in [('learner-a',A),('learner-b',B)]:
            status,me=request('/api/me',self.tokens[user]);self.assertEqual(status,200);self.assertEqual(me['tenant_id'],tenant)
        foreign='20000000-0000-4000-8000-000000000002'
        for path,payload in [(f'/api/courses/{foreign}/enroll',{}),(f'/api/courses/{foreign}/lessons/30000000-0000-4000-8000-000000000021/complete',{}),(f'/api/courses/{foreign}/submissions',{'content':'Synthetic unauthorized cross tenant evidence.'}),('/api/workshops/40000000-0000-4000-8000-000000000002/register',{})]:
            self.assertEqual(request(path,token,payload)[0],404)
        self.assertEqual(request('/api/tools/invoke',token,{'name':'learning.progress','arguments':{'tenant_id':B}})[0],403)
        self.assertEqual(request('/api/tools/invoke',token,{'name':'shell.execute','arguments':{}})[0],403)
        self.assertEqual(request('/api/tools/invoke',token,{'name':'learning.progress','arguments':{}})[0],200)

    def test_02_rls_role_and_sql_negative_cases(self):
        result=sql("SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname='academy_app';").stdout.strip()
        self.assertEqual(result,'f|f')
        count=sql("SET ROLE academy_app; SELECT count(*) FROM courses;").stdout.strip().splitlines()[-1]
        self.assertEqual(count,'0')
        result=sql(f"BEGIN; SET ROLE academy_app; SELECT set_config('app.tenant_id','{A}',true); SELECT count(*) FROM courses WHERE tenant_id='{B}'; ROLLBACK;").stdout
        self.assertIn('\n0\n',result)
        result=sql(f"BEGIN; SET ROLE academy_app; SELECT set_config('app.tenant_id','{A}',true); INSERT INTO enrollments VALUES ('{uuid4()}','{B}','20000000-0000-4000-8000-000000000002','{SA}',now()); ROLLBACK;",check=False)
        self.assertNotEqual(result.returncode,0)
        for operation in ('UPDATE','DELETE'):
            grant=sql(f"SELECT has_table_privilege('academy_app','audit_events','{operation}');").stdout.strip()
            self.assertEqual(grant,'f','audit must remain append-only for app')

    def test_03_learning_review_and_replay(self):
        token=self.tokens['learner-a'];base=f'/api/courses/{self.course}'
        status,e=request(base+'/enroll',token,{});self.assertEqual(status,200)
        self.assertEqual(request(base+'/enroll',token,{})[1]['id'],e['id'])
        self.assertEqual(request(base+f'/lessons/{self.second}/complete',token,{})[0],409)
        for lesson in (self.first,self.second): self.assertEqual(request(base+f'/lessons/{lesson}/complete',token,{})[0],200)
        self.assertTrue(request(base+f'/lessons/{self.first}/complete',token,{})[1]['replayed'])
        payload={'content':'Synthetic observation, measured change, limitations and reflection.'}
        status,sub=request(base+'/submissions',token,payload);self.assertEqual(status,200)
        self.assertEqual(request(base+'/submissions',token,payload)[1]['id'],sub['id'])
        review={'decision':'accepted','feedback':'Synthetic independent rubric feedback.','expected_revision':1}
        path=f"/api/submissions/{sub['id']}/review"
        self.assertEqual(request(path,token,review)[0],403)
        self.assertEqual(request(path,self.tokens['reviewer-a'],review)[0],200)
        self.assertEqual(request(path,self.tokens['reviewer-a'],review)[0],409)
        foreign=str(uuid4())
        self.foreign_submission_ids.append(foreign)
        sql(f"INSERT INTO submissions(id,tenant_id,course_id,subject,content) VALUES('{foreign}','{B}','20000000-0000-4000-8000-000000000002','{SB}','Synthetic foreign submission content.');")
        self.assertEqual(request(f'/api/submissions/{foreign}/review',self.tokens['reviewer-a'],review)[0],404)
        for user in ('learner-a','reviewer-a'):
            status,items=request('/api/submissions',self.tokens[user]);self.assertEqual(status,200)
            self.assertFalse(any(i['id']==foreign for i in items))

    def test_04_reviewer_cannot_accept_own_evidence(self):
        token=self.tokens['reviewer-a'];base=f'/api/courses/{self.course}'
        self.assertEqual(request(base+'/enroll',token,{})[0],200)
        for lesson in (self.first,self.second): self.assertEqual(request(base+f'/lessons/{lesson}/complete',token,{})[0],200)
        for attempt in range(12):
            status,sub=request(base+'/submissions',token,{'content':f'Synthetic reviewer authored evidence for self-review denial {attempt}.'})
            self.assertEqual(status,200)
            response=request(f"/api/submissions/{sub['id']}/review",token,{'decision':'accepted','feedback':'Not allowed','expected_revision':1})
            self.assertEqual(response[0],409,f'Committed submission must exist before response: {response}')
            self.assertEqual(sql(f"SELECT status FROM submissions WHERE id='{sub['id']}';").stdout.strip(),'submitted')

    def test_05_capacity_concurrency(self):
        path=f'/api/workshops/{self.workshop}/register'
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(request,path,self.tokens[user],{}) for user in ('learner-a','reviewer-a')]
            statuses=sorted(f.result()[0] for f in futures)
        self.assertEqual(statuses,[200,409])
        self.assertEqual(sql(f"SELECT count(*) FROM registrations WHERE workshop_id='{self.workshop}';").stdout.strip(),'1')

    def test_06_tool_budget_concurrency(self):
        token=self.tokens['learner-b']
        self.assertEqual(request('/api/tools/invoke',token,{'name':'learning.progress','arguments':{},'tenant_id':A})[0],422)
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures=[pool.submit(request,'/api/tools/invoke',token,{'name':'learning.progress','arguments':{}}) for _ in range(25)]
            statuses=[f.result()[0] for f in futures]
        self.assertTrue(all(s in (200,403) for s in statuses))
        self.assertLessEqual(statuses.count(200),20,'concurrent budget must not overshoot')
        self.assertIn(403,statuses)
        self.assertEqual(request('/api/tools/invoke',token,{'name':'learning.progress','arguments':{}})[0],403)

    def test_07_revoked_membership(self):
        sql(f"UPDATE memberships SET active=false WHERE subject='{SA}';")
        try:
            self.assertEqual(request('/api/me',self.tokens['learner-a'])[0],403)
            self.assertEqual(request('/api/tools/invoke',self.tokens['learner-a'],{'name':'learning.progress','arguments':{}})[0],403)
        finally:
            sql(f"UPDATE memberships SET active=true WHERE subject='{SA}';")
        self.assertEqual(request('/api/me',self.tokens['learner-a'])[0],200)

if __name__=='__main__': unittest.main()
