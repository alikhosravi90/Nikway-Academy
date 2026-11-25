#!/usr/bin/env python3
"""Generate local synthetic configuration once, preserving existing credentials."""
import json, os, secrets
from pathlib import Path
os.umask(0o077)
r = Path(__file__).resolve().parents[1] / 'infra/runtime'
r.mkdir(parents=True, exist_ok=True)
paths = [r / x for x in ('.env','init.sql','academy-realm.json','credentials.json')]
if all(p.exists() for p in paths):
    print('Existing local configuration preserved.'); raise SystemExit
if any(p.exists() for p in paths):
    raise SystemExit('Partial configuration: inspect before recovery; no credentials changed.')
ui_port = int(os.environ.get('ACADEMY_UI_PORT','18401'))
api_port = int(os.environ.get('ACADEMY_API_PORT','18400'))
idp_port = int(os.environ.get('ACADEMY_IDP_PORT','18480'))
project = os.environ.get('ACADEMY_PROJECT','nikway-academy-local')
import re
if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,50}',project) or not all(1024 <= n <= 65535 for n in (ui_port,api_port,idp_port)):
    raise SystemExit('Invalid local project or port')
names = ['POSTGRES_PASSWORD','KEYCLOAK_DB_PASSWORD','KEYCLOAK_ADMIN_PASSWORD','ACADEMY_APP_PASSWORD','ACADEMY_OWNER_PASSWORD']
pw = {k: secrets.token_hex(24) for k in names}
sql = ''
for role, key in [('academy_owner','ACADEMY_OWNER_PASSWORD'),('academy_app','ACADEMY_APP_PASSWORD'),('keycloak','KEYCLOAK_DB_PASSWORD')]:
    sql += f"CREATE ROLE {role} LOGIN PASSWORD '{pw[key]}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;\n"
sql += '''CREATE DATABASE academy OWNER academy_owner;
CREATE DATABASE keycloak OWNER keycloak;
REVOKE CONNECT ON DATABASE academy FROM PUBLIC;
GRANT CONNECT ON DATABASE academy TO academy_owner, academy_app;
REVOKE CONNECT ON DATABASE keycloak FROM PUBLIC;
GRANT CONNECT ON DATABASE keycloak TO keycloak;
\\connect academy
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO academy_app;
'''
pw.update(ACADEMY_PROJECT=project,ACADEMY_UI_PORT=str(ui_port),ACADEMY_API_PORT=str(api_port),ACADEMY_IDP_PORT=str(idp_port))
users, creds = [], {}
for n, name, tenant, role in [(1,'learner-a',1,'learner'),(2,'learner-b',2,'learner'),(3,'reviewer-a',1,'reviewer')]:
    password = secrets.token_hex(18)
    creds[name] = {'username':name,'password':password}
    users.append(dict(id=f'00000000-0000-4000-8000-{n:012d}',username=name,enabled=True,emailVerified=True,firstName='Synthetic',lastName=name,email=f'{name}@example.invalid',attributes={'tenant_id':[f'10000000-0000-4000-8000-{tenant:012d}']},realmRoles=[role],credentials=[{'type':'password','value':password,'temporary':False}]))
mappers = [dict(name='api-audience',protocol='openid-connect',protocolMapper='oidc-audience-mapper',config={'included.custom.audience':'academy-api','access.token.claim':'true','id.token.claim':'false'}),dict(name='tenant-id',protocol='openid-connect',protocolMapper='oidc-usermodel-attribute-mapper',config={'user.attribute':'tenant_id','claim.name':'tenant_id','jsonType.label':'String','access.token.claim':'true','id.token.claim':'true'})]
client = dict(clientId='academy-web',enabled=True,protocol='openid-connect',publicClient=True,standardFlowEnabled=True,directAccessGrantsEnabled=False,redirectUris=[f'http://localhost:{ui_port}/*',f'http://127.0.0.1:{ui_port}/*'],webOrigins=[f'http://localhost:{ui_port}',f'http://127.0.0.1:{ui_port}'],attributes={'pkce.code.challenge.method':'S256'},protocolMappers=mappers)
realm = dict(realm='academy',enabled=True,registrationAllowed=False,resetPasswordAllowed=False,sslRequired='none',roles={'realm':[{'name':'learner'},{'name':'reviewer'}]},users=users,clients=[client])
for p, content in zip(paths, [''.join(f'{k}={v}\n' for k,v in pw.items()),sql,json.dumps(realm,indent=2),json.dumps(creds,indent=2)]):
    p.write_text(content+'\n'); p.chmod(0o600)
# Import must be readable by the unprivileged container uid; parent directory stays private.
paths[1].chmod(0o644)
paths[2].chmod(0o644)
print('Generated configuration under infra/runtime; credentials not printed.')
