"""Run only after the coordinator freezes writes. Candidate project only.
Lifecycle changes, encrypted recovery into disposable databases, and read sampling.
No credentials, tokens, database rows, or plaintext backups are emitted.
"""
import datetime,hashlib,importlib.util,json,os,pathlib,secrets,statistics,subprocess,time,urllib.request
ROOT=pathlib.Path(os.environ['ACADEMY_RUNTIME_ROOT']).resolve()
OUT=pathlib.Path(__file__).resolve().parents[2]/'evidence/security-content'
settings=dict(x.split('=',1) for x in (ROOT/'infra/runtime/.env').read_text().splitlines() if '=' in x)
assert settings['ACADEMY_PROJECT']=='nikway-academy-content', 'Refuse non-candidate project'
assert settings['ACADEMY_API_PORT']=='18600', 'Refuse unexpected candidate ports'
compose=[str(ROOT/'scripts/local-compose.sh')]
def run(args,data=None,timeout=240,env=None):
 p=subprocess.run(args,cwd=ROOT,input=data,capture_output=True,timeout=timeout,env=env)
 if p.returncode:raise RuntimeError('Scoped command failed: '+str(args[0])+' exit '+str(p.returncode)+'; diagnostic withheld')
 return p.stdout

def canonical(raw):
 tables={};name=None;rows=[]
 for line in raw.splitlines():
  if line.startswith(b'COPY ') and line.endswith(b' FROM stdin;'): name=line.decode();rows=[]
  elif name and line==b'\\.':
   tables[name]={'rows':len(rows),'sha256':hashlib.sha256(b'\n'.join(sorted(rows))).hexdigest()};name=None
  elif name:rows.append(line)
 assert tables and name is None
 return tables

def snapshot():
 out={}
 for db in ['academy','keycloak']:
  args=compose+['exec','-T','postgres','pg_dump','-U','postgres','-d',db,'--data-only']
  if db=='keycloak':
   for table in ['realm','user_entity','credential','client','keycloak_role','user_role_mapping','user_attribute','protocol_mapper','protocol_mapper_config']:args+=['--table='+table]
  out[db]=canonical(run(args))
 return out

def identities(project):
 ids=run(['docker','ps','-aq','--filter','label=com.docker.compose.project='+project]).decode().split()
 return [json.loads(run(['docker','inspect','--format','{"name":{{json .Name}},"id":{{json .Id}},"image":{{json .Image}},"started":{{json .State.StartedAt}}}',i])) for i in ids]

receipt={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'project':settings['ACADEMY_PROJECT'],'scope':'Synthetic candidate only; baseline preserved'}
baseline=identities('nikway-academy-local'); initial=snapshot();receipt['initial_persistence']=initial
before=identities(settings['ACADEMY_PROJECT'])
start=time.monotonic()
run([str(ROOT/'scripts/local-stop.sh')]);run(compose+['start']);run(['python3',str(ROOT/'scripts/local-ready.py')])
receipt['stop_start_seconds']=round(time.monotonic()-start,3)
assert snapshot()==initial,'Persistence changed after stop/start'
receipt['stop_start_persistence']='PASS'
start=time.monotonic();run([str(ROOT/'scripts/local-restart.sh')]);receipt['restart_seconds']=round(time.monotonic()-start,3)
assert snapshot()==initial,'Persistence changed after restart'
receipt['restart_persistence']='PASS'
receipt['persistence_scope']='Every Academy table; 9 stable identity/configuration tables. Keycloak session/lock tables excluded from lifecycle equality; every table covered by separate recovery.'
passfile=ROOT/'infra/runtime/final-content-recovery-passphrase'
if not passfile.exists():passfile.write_text(secrets.token_urlsafe(48));passfile.chmod(0o600)
env=os.environ.copy();env['BACKUP_PASSPHRASE_FILE']=str(passfile)
receipt['recovery']={}
for db in ['academy','keycloak']:
 backup=run([str(ROOT/'scripts/backup-local.sh'),db],env=env).decode().strip()
 checked=json.loads(run(['python3',str(ROOT/'scripts/restore-local-verify.py'),backup],env=env))
 receipt['recovery'][db]={'status':checked['status'],'tables':checked['tables'],'total_rows':checked['total_rows'],'method':checked['method'],'encrypted_backup_sha256':hashlib.sha256((ROOT/backup).read_bytes()).hexdigest(),'table_evidence':checked['table_evidence']}

spec=importlib.util.spec_from_file_location('local_oidc',ROOT/'scripts/local_oidc.py');oidc=importlib.util.module_from_spec(spec);spec.loader.exec_module(oidc)
token=oidc.login('learner-a')['access_token']
def sample(path,authenticated=False):
 values=[]
 for _ in range(50):
  req=urllib.request.Request('http://localhost:18501'+path,headers={'Authorization':'Bearer '+token} if authenticated else {})
  start=time.perf_counter()
  with urllib.request.urlopen(req,timeout=15) as response:
   assert response.status==200;response.read()
  values.append((time.perf_counter()-start)*1000)
 ordered=sorted(values)
 return {'samples':len(values),'errors':0,'median_ms':round(statistics.median(values),3),'p95_ms':round(ordered[47],3),'max_ms':round(max(values),3),'scope':'Serial loopback read samples; no concurrency/throughput/capacity claim'}
receipt['health_sample']=sample('/api/health');receipt['authenticated_courses_sample']=sample('/api/courses',True)
ids=run(compose+['ps','-q']).decode().split()
receipt['resources']=[json.loads(x) for x in run(['docker','stats','--no-stream','--format','{{json .}}']+ids).decode().splitlines()]
after=identities(settings['ACADEMY_PROJECT']);receipt['final_images']=after
assert {(x['name'],x['image']) for x in before}=={(x['name'],x['image']) for x in after},'Images changed during lifecycle drill'
assert identities('nikway-academy-local')==baseline,'Frozen baseline identity/start timestamps changed'
receipt['baseline_identity_unchanged']=True
receipt['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUT/'final-content-runtime-validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ['project','stop_start_persistence','restart_persistence','baseline_identity_unchanged','health_sample','authenticated_courses_sample']},indent=2))
