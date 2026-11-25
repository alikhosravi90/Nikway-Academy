"""Generate isolated disposable Dex configuration; no baseline identities reused."""
import json, secrets, pathlib, bcrypt
root=pathlib.Path(__file__).resolve().parents[1]/'runtime'/'dex-benchmark'
root.mkdir(mode=0o700, parents=True, exist_ok=True)
password=secrets.token_urlsafe(32)
config={'issuer':'http://localhost:18680/dex','storage':{'type':'memory'},'web':{'http':'0.0.0.0:5556'},'oauth2':{'responseTypes':['code'],'skipApprovalScreen':True,'pkce':{'enforce':True,'codeChallengeMethodsSupported':['S256']}},'staticClients':[{'id':'academy-web','public':True,'redirectURIs':['http://localhost:18601/'],'name':'Isolated Academy benchmark'}],'enablePasswordDB':True,'staticPasswords':[{'email':'learner-a@example.invalid','hash':bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode(),'username':'learner-a','userID':'00000000-0000-4000-8000-000000000001'}]}
for name,value in [('config.json',config),('credentials.json',{'email':'learner-a@example.invalid','password':password})]:
 p=root/name;p.write_text(json.dumps(value));p.chmod(0o644 if name=='config.json' else 0o600)
print('Generated isolated runtime configuration (credentials not printed).')
