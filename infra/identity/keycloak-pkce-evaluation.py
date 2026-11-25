"""Synthetic isolated Keycloak PKCE and verified access-token contract checks."""
import base64,hashlib,html,http.cookiejar,json,pathlib,re,secrets,urllib.error,urllib.parse,urllib.request,uuid,time
import jwt,os
VARIANT=os.environ.get("KEYCLOAK_EVALUATION_VARIANT","base")
assert VARIANT in ("base","custom")
ROOT=pathlib.Path(__file__).resolve().parents[2]
ISSUER='http://localhost:18680/realms/academy'; IDP=ISSUER+'/protocol/openid-connect'; REDIRECT='http://localhost:18601/'
creds=json.loads((ROOT/'infra/runtime/keycloak-evaluation/infra/runtime/credentials.json').read_text())
class CookiePolicy(http.cookiejar.DefaultCookiePolicy):
 def return_ok_secure(self,cookie,request):
  return True if urllib.parse.urlsplit(request.full_url).hostname=='localhost' else super().return_ok_secure(cookie,request)
class StopRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
def login(name,wrong=False):
 v=secrets.token_urlsafe(48);state=secrets.token_urlsafe(24)
 q=dict(client_id='academy-web',redirect_uri=REDIRECT,response_type='code',scope='openid',state=state,code_challenge=base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).decode().rstrip('='),code_challenge_method='S256')
 op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar(policy=CookiePolicy())),StopRedirect())
 page=op.open(IDP+'/auth?'+urllib.parse.urlencode(q),timeout=15).read().decode()
 action=html.unescape(re.search(r'<form[^>]+action="([^"]+)"',page).group(1))
 try:resp=op.open(action,urllib.parse.urlencode(dict(username=name,password=creds[name]['password'],credentialId='')).encode(),timeout=15)
 except urllib.error.HTTPError as e:resp=e
 values=urllib.parse.parse_qs(urllib.parse.urlsplit(resp.headers.get('Location','')).query)
 assert values.get('state')==[state]
 payload=dict(grant_type='authorization_code',client_id='academy-web',code=values['code'][0],redirect_uri=REDIRECT,code_verifier='invalid-verifier' if wrong else v)
 try:resp=op.open(IDP+'/token',urllib.parse.urlencode(payload).encode(),timeout=15)
 except urllib.error.HTTPError as e:resp=e
 return resp.status,json.load(resp)
keyclient=jwt.PyJWKClient(IDP+'/certs')
results=[]
for i,name in enumerate(['learner-a','learner-b','reviewer-a'],1):
 started=time.monotonic();status,t=login(name);assert status==200
 key=keyclient.get_signing_key_from_jwt(t['access_token'])
 c=jwt.decode(t['access_token'],key.key,algorithms=['RS256'],audience='academy-api',issuer=ISSUER,options={'require':['exp','iat','sub','aud','iss']})
 assert c['sub']==f'00000000-0000-4000-8000-{i:012d}'
 results.append({'user':name,'verified_access_token_contract':True,'login_ms':round((time.monotonic()-started)*1000,2)})
status,_=login('learner-a',True);assert status==400
q=urllib.parse.urlencode(dict(client_id='academy-web',redirect_uri=REDIRECT,response_type='code',scope='openid',state='negative-test'))
try:r=urllib.request.build_opener(StopRedirect()).open(IDP+'/auth?'+q,timeout=15)
except urllib.error.HTTPError as e:r=e
assert r.status==400 or 'error=invalid_request' in r.headers.get('Location','')
out={'scope':'Isolated Keycloak '+VARIANT+' variant; H2 disposable database, no Academy API regression or production claim','users':results,'wrong_verifier_rejected':True,'missing_PKCE_rejected':True,'gate':'PKCE subset passes; consult exact image scan and full regression gate'}
(ROOT/('evidence/security-content/keycloak-'+VARIANT+'-pkce.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
