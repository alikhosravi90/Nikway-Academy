#!/usr/bin/env python3
"""Operator-invoked creation of ONE dedicated local Moodle client; never edits existing clients/users."""
import argparse,json,os,secrets,urllib.request,urllib.parse,urllib.error
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--academy-runtime',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
s=dict(x.split('=',1) for x in (a.academy_runtime/'.env').read_text().splitlines() if '=' in x)
base='http://localhost:'+s.get('ACADEMY_IDP_PORT','18580')
data=urllib.parse.urlencode({'grant_type':'password','client_id':'admin-cli','username':'local-admin','password':s['KEYCLOAK_ADMIN_PASSWORD']}).encode()
try:
 token=json.load(urllib.request.urlopen(base+'/realms/master/protocol/openid-connect/token',data,timeout=15))['access_token']
 def call(path,body=None):
  req=urllib.request.Request(base+'/admin/realms/academy'+path,None if body is None else json.dumps(body).encode(),{'Authorization':'Bearer '+token,'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=15) as r:
   raw=r.read();return json.loads(raw) if raw else None
 name='nikway-moodle-local'
 desired={'clientId':name,'name':'NIKWAY Moodle isolated local pilot','enabled':True,'protocol':'openid-connect','publicClient':False,'clientAuthenticatorType':'client-secret','standardFlowEnabled':True,'implicitFlowEnabled':False,'directAccessGrantsEnabled':False,'serviceAccountsEnabled':False,'fullScopeAllowed':False,'redirectUris':['http://localhost:18701/auth/oidc/'],'webOrigins':[],'attributes':{'nikway.owner':'moodle-local-pilot-v1','pkce.code.challenge.method':'S256'},'defaultClientScopes':['profile','email'],'optionalClientScopes':[]}
 found=call('/clients?clientId='+name)
 if not found:
  desired['secret']=secrets.token_urlsafe(48);call('/clients',desired);found=call('/clients?clientId='+name)
 if len(found)!=1:raise RuntimeError('Dedicated client identity ambiguous')
 c=call('/clients/'+found[0]['id'])
 for k in ('clientId','enabled','protocol','publicClient','clientAuthenticatorType','standardFlowEnabled','implicitFlowEnabled','directAccessGrantsEnabled','serviceAccountsEnabled','fullScopeAllowed','redirectUris','webOrigins'):
  if c.get(k)!=desired[k]:raise RuntimeError('Unexpected existing dedicated client configuration: '+k)
 for k in ('defaultClientScopes','optionalClientScopes'):
  if sorted(c.get(k,[]))!=sorted(desired[k]):raise RuntimeError('Unexpected existing dedicated client scopes: '+k)
 if c.get('attributes',{}).get('pkce.code.challenge.method')!='S256':raise RuntimeError('PKCE policy mismatch')
 if c.get('attributes',{}).get('nikway.owner')!='moodle-local-pilot-v1':raise RuntimeError('Unowned existing client; refuse change')
 secret=call('/clients/'+c['id']+'/client-secret')['value']
 users=[]
 for sub,username in [('00000000-0000-4000-8000-000000000001','academy-learner-a'),('00000000-0000-4000-8000-000000000003','academy-reviewer-a')]:
  u=call('/users/'+sub)
  if u['id']!=sub or not u.get('enabled') or not u.get('email'):raise RuntimeError('Expected synthetic identity unavailable')
  users.append({'sub':sub,'username':sub,'email':u['email'],'firstname':u.get('firstName') or username,'lastname':u.get('lastName') or 'Local'})
 result={'client_id':name,'client_secret':secret,'issuer_base':base+'/realms/academy','authorization_endpoint':base+'/realms/academy/protocol/openid-connect/auth','token_endpoint':'http://keycloak:8080/realms/academy/protocol/openid-connect/token','userinfo_endpoint':'http://keycloak:8080/realms/academy/protocol/openid-connect/userinfo','users':users}
 a.output.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 if a.output.exists():
  if json.loads(a.output.read_text())!=result:raise RuntimeError('Private output differs; refusing overwrite')
 else:
  fd=os.open(a.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'w') as f:json.dump(result,f)
 print(json.dumps({'client':name,'created_or_verified':True,'allowed_subjects':len(users),'existing_clients_users_changed':False,'pkce':'S256_required','secret_logged':False}))
except (urllib.error.HTTPError,KeyError,RuntimeError) as e:
 raise SystemExit('Dedicated client setup failed: '+(str(e) if isinstance(e,RuntimeError) else type(e).__name__))
