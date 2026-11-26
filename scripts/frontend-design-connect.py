#!/usr/bin/env python3
"""Append only this loopback preview origin to the existing public Academy client."""
import json,os,urllib.request,urllib.parse
from pathlib import Path
path=Path(os.environ.get('ACADEMY_ENV_FILE','../content-integration/infra/runtime/.env'))
env=dict(line.split('=',1) for line in path.read_text().splitlines() if line and not line.startswith('#') and '=' in line)
origin='http://localhost:18901'; base='http://localhost:18580'
def request(path,body=None,method=None,token=None):
 headers={'Authorization':'Bearer '+token} if token else {}
 if isinstance(body,dict):body=json.dumps(body).encode();headers['Content-Type']='application/json'
 req=urllib.request.Request(base+path,data=body,headers=headers,method=method)
 with urllib.request.urlopen(req,timeout=10) as r:
  data=r.read();return json.loads(data) if data else None
body=urllib.parse.urlencode({'grant_type':'password','client_id':'admin-cli','username':'local-admin','password':env['KEYCLOAK_ADMIN_PASSWORD']}).encode()
token=request('/realms/master/protocol/openid-connect/token',body)['access_token']
clients=request('/admin/realms/academy/clients?clientId=academy-web',token=token)
assert len(clients)==1,'Expected exactly one existing Academy client'
c=clients[0]
original=json.dumps(c,sort_keys=True)
assert c['publicClient'] and c['standardFlowEnabled'] and not c.get('implicitFlowEnabled') and not c.get('serviceAccountsEnabled') and not c.get('directAccessGrantsEnabled') and c.get('attributes',{}).get('pkce.code.challenge.method')=='S256','Unexpected client security profile'
for key,value in [('redirectUris',origin+'/'),('webOrigins',origin)]:
 if value not in c.setdefault(key,[]):c[key].append(value)
attrs=c.setdefault('attributes',{});existing=attrs.get('post.logout.redirect.uris','');values=existing.split('##') if existing else []
if origin+'/' not in values:values.append(origin+'/')
attrs['post.logout.redirect.uris']='##'.join(values)
if json.dumps(c,sort_keys=True)!=original:
 request('/admin/realms/academy/clients/'+c['id'],c,'PUT',token)
print('PASS: appended only localhost:18901 preview redirect, logout and origin; preserved existing entries')
