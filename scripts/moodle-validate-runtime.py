#!/usr/bin/env python3
"""Coordinated isolated Moodle lifecycle check; run only after test writers stop."""
import pathlib,subprocess,time,json,hashlib,urllib.request,statistics,datetime
root=pathlib.Path(__file__).resolve().parents[1]; c=[str(root/'scripts/moodle-compose.sh')]
def run(a):return subprocess.run(a,check=True,capture_output=True).stdout
def identity(project):
 ids=run(['docker','ps','-aq','--filter','label=com.docker.compose.project='+project]).decode().split()
 return [json.loads(run(['docker','inspect',i,'--format','{"id":{{json .Id}},"image":{{json .Image}},"started":{{json .State.StartedAt}}}']))for i in ids]
def snapshot():
 data=run(c+['exec','-T','db','pg_dump','-U','postgres','-d','moodle','--data-only']);out={};table=None;lines=[]
 for line in data.splitlines():
  if line.startswith(b'COPY '):table=line.split(b' FROM stdin;')[0].decode();lines=[]
  elif table and line==b'\\.':out[table]={'rows':len(lines),'sha256':hashlib.sha256(b'\n'.join(sorted(lines))).hexdigest()};table=None
  elif table:lines.append(line)
 return out
baseline={x:identity(x)for x in ['nikway-academy-local','nikway-academy-content']}
def ready():
 for _ in range(90):
  try:
   with urllib.request.urlopen('http://localhost:18701/login/index.php',timeout=3) as r:assert r.status==200
   return
  except Exception:time.sleep(1)
 raise RuntimeError('Moodle readiness timeout')
run(c+['stop','cron']);before=snapshot();checks=[]
try:
 for kind in ['stop-start','restart']:
  t=time.monotonic()
  if kind=='stop-start':run(c+['stop','moodle','db']);run(c+['start','db','moodle'])
  else:run(c+['restart','db','moodle'])
  ready();after=snapshot();
  stable_before={k:v for k,v in before.items() if not k.startswith('COPY public.mdl_sessions ')}
  stable_after={k:v for k,v in after.items() if not k.startswith('COPY public.mdl_sessions ')}
  if stable_before!=stable_after:
   changed={k:{'before':before.get(k),'after':after.get(k)}for k in set(before)|set(after) if before.get(k)!=after.get(k)}
   (root/'infra/moodle/runtime/lifecycle-differences.json').write_text(json.dumps(changed,indent=2))
   raise AssertionError(kind+' table digest mismatch; private differences recorded')
  checks.append({'operation':kind,'elapsed_seconds':round(time.monotonic()-t,3),'all_non_session_table_digests_equal':True,'excluded_table':'mdl_sessions: readiness HTTP requests create anonymous sessions'})
 timing=[]
 for _ in range(20):
  t=time.perf_counter()
  with urllib.request.urlopen('http://localhost:18701/login/index.php',timeout=5) as r:assert r.status==200;r.read()
  timing.append((time.perf_counter()-t)*1000)
 other={x:identity(x)for x in baseline};assert other==baseline,'Other project identity changed during test'
 print(json.dumps({'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','table_count':len(before),'compared_persistent_tables':len(before)-1,'session_exclusion_reason':'Health/readiness login requests intentionally create anonymous sessions; initial strict all-table comparison detected only this expected table change','rows':sum(x['rows']for x in before.values()),'table_digests':before,'lifecycle':checks,'unrelated_project_identity_unchanged':True,'login_page_sample':{'requests':20,'concurrency':1,'median_ms':round(statistics.median(timing),3),'p95_ms':round(sorted(timing)[18],3),'max_ms':round(max(timing),3),'scope':'Unauthenticated login page only; not learning throughput'}}))
finally:run(c+['start','cron'])
