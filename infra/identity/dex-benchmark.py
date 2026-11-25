"""Loopback-only PKCE and token-contract probe; never prints tokens or secrets."""
import base64,hashlib,html,http.cookiejar,json,pathlib,re,secrets,time,urllib.request,urllib.parse,urllib.error,uuid
ROOT=pathlib.Path(__file__).resolve().parents[2]
creds=json.loads((ROOT/'infra/runtime/dex-benchmark/credentials.json').read_text())
issuer='http://localhost:18680/dex'; redirect='http://localhost:18601/'
class StopRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if newurl.startswith(redirect): return None
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def flow(wrong=False):
 verifier=secrets.token_urlsafe(48); state=secrets.token_urlsafe(24)
 challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
 op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),StopRedirect())
 args=dict(client_id='academy-web',redirect_uri=redirect,response_type='code',scope='openid profile email',state=state,code_challenge=challenge,code_challenge_method='S256')
 page=op.open(issuer+'/auth?'+urllib.parse.urlencode(args),timeout=15)
 body=page.read().decode(); action=re.search(r'<form[^>]*action="([^"]*)"',body)
 url=urllib.parse.urljoin(page.url,html.unescape(action.group(1)) if action else page.url)
 try: response=op.open(url,urllib.parse.urlencode({'login':creds['email'],'password':creds['password']}).encode(),timeout=15)
 except urllib.error.HTTPError as e:
  if e.code not in (302,303): raise RuntimeError('login HTTP '+str(e.code)) from None
  response=e
 values=urllib.parse.parse_qs(urllib.parse.urlsplit(response.headers.get('Location','')).query)
 assert values.get('state')==[state], 'state mismatch'
 payload=dict(grant_type='authorization_code',client_id='academy-web',code=values['code'][0],redirect_uri=redirect,code_verifier='wrong-verifier' if wrong else verifier)
 try:
  response=op.open(issuer+'/token',urllib.parse.urlencode(payload).encode(),timeout=15)
 except urllib.error.HTTPError as e: response=e
 return response.status,json.load(response)
start=time.monotonic(); status,token=flow(); elapsed=(time.monotonic()-start)*1000
assert status==200
raw=token['id_token'].split('.')[1];claims=json.loads(base64.urlsafe_b64decode(raw+'='*(-len(raw)%4)))
try: uuid.UUID(claims['sub']); valid_uuid=True
except ValueError:valid_uuid=False
accesspart=token['access_token'].split('.')[1]
accessclaims=json.loads(base64.urlsafe_b64decode(accesspart+'='*(-len(accesspart)%4)))
try: uuid.UUID(accessclaims['sub']); access_uuid=True
except ValueError: access_uuid=False
badstatus,bad=flow(True)
missing=urllib.parse.urlencode(dict(client_id='academy-web',redirect_uri=redirect,response_type='code',scope='openid',state='negative-test'))
try: response=urllib.request.build_opener(StopRedirect()).open(issuer+'/auth?'+missing,timeout=10)
except urllib.error.HTTPError as e:response=e
result={'scope':'Synthetic isolated Dex compatibility benchmark; ID token payload inspected, not accepted by Academy as access token.','image':'ghcr.io/dexidp/dex@sha256:65b72ca0f4b0bf6d4ada84ec21da8851782563404ac7b8f926923d27ceced9ab','pkce_S256_success':status==200,'wrong_verifier_rejected':badstatus==400,'missing_pkce_rejected':response.status==400 or ('error=invalid_request' in response.headers.get('Location','')),'one_login_ms':round(elapsed,2),'access_token_is_JWT':len(token['access_token'].split('.'))==3,'id_token_subject_is_UUID':valid_uuid,'id_token_audience':claims.get('aud'),'access_token_audience':accessclaims.get('aud'),'access_token_subject_is_UUID':access_uuid,'baseline_api_requires':'RS256 JWT access token, UUID subject, academy-api audience','persistent_storage_tested':False,'release_gate':'NO-GO: scanner findings and incompatible baseline token contract'}
(ROOT/'evidence/security-content/dex-benchmark.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
