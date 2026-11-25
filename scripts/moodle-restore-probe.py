#!/usr/bin/env python3
"""Restore DB + files into fresh isolated containers/volumes; never overwrite live Moodle."""
import pathlib,subprocess,sys,json,secrets,time,urllib.request,hashlib,tarfile,io,os
root=pathlib.Path(__file__).resolve().parents[1]; folder=pathlib.Path(sys.argv[1]).resolve(); rt=root/'infra/moodle/runtime'
if not (folder/'COMPLETE').is_file(): raise SystemExit('Backup lacks COMPLETE marker; refusing partial backup.')
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=folder,check=True,capture_output=True)
probe=rt/('restore-probe-'+secrets.token_hex(4));probe.mkdir(mode=0o700)
project='nikway-moodle-restore-'+secrets.token_hex(4)
compose=probe/'compose.json'; passfile=rt/'backup_passphrase'
def run(args,data=None):return subprocess.run(args,input=data,check=True,capture_output=True).stdout
def decrypt(name):return run(['gpg','--batch','--pinentry-mode','loopback','--passphrase-file',str(passfile),'--decrypt',str(folder/name)])
config=decrypt('config.php.gpg').replace(b'http://localhost:18701',b'http://localhost:18702')
(probe/'config.php').write_bytes(config);(probe/'config.php').chmod(0o600)
image=run(['docker','inspect','nikway-academy-moodle-moodle-1','--format','{{.Image}}']).decode().strip()
dbimage=run(['docker','inspect','nikway-academy-moodle-db-1','--format','{{.Image}}']).decode().strip()
spec={'services':{'db':{'image':dbimage,'entrypoint':['sh','-c','cp /run/secrets/db_password /tmp/moodle-password; chown postgres:postgres /tmp/moodle-password; chmod 600 /tmp/moodle-password; exec docker-entrypoint.sh postgres'],'environment':{'POSTGRES_USER':'postgres','POSTGRES_DB':'moodle','POSTGRES_PASSWORD_FILE':'/run/secrets/postgres_password'},'volumes':['db:/var/lib/postgresql/data',f'{rt}/postgres_password:/run/secrets/postgres_password:ro',f'{rt}/db_password:/run/secrets/db_password:ro',f'{root}/infra/moodle/postgres-init.sh:/docker-entrypoint-initdb.d/10-moodle.sh:ro'],'mem_limit':'512m','cpus':1},'moodle':{'image':image,'ports':['127.0.0.1:18702:80'],'volumes':['data:/var/moodledata',f'{probe}/config.php:/run/moodle/config.php:ro'],'mem_limit':'768m','cpus':1}},'volumes':{'db':{},'data':{}},'networks':{'default':{'ipam':{'config':[{'subnet':'10.253.243.16/28'}]}}}}
compose.write_text(json.dumps(spec));compose.chmod(0o600)
c=['docker','compose','-p',project,'-f',str(compose)]
def exe(service,args,data=None):return run(c+['exec','-T',service]+args,data)
def rows(data):
 out={};table=None;lines=[]
 for line in data.splitlines():
  if line.startswith(b'COPY '):table=line.split(b' FROM stdin;')[0].decode();lines=[]
  elif table and line==b'\\.':out[table]=(len(lines),hashlib.sha256(b'\n'.join(sorted(lines))).hexdigest());table=None
  elif table:lines.append(line)
 return out
started=time.monotonic()
try:
 run(c+['up','-d','db'])
 for _ in range(60):
  try:
   exe('db',['pg_isready','-h','127.0.0.1','-U','postgres','-d','moodle'])
   assert exe('db',['psql','-U','postgres','-d','moodle','-At','-c',"SELECT 1 FROM pg_roles WHERE rolname='moodle'"]).strip()==b'1';break
  except (subprocess.CalledProcessError,AssertionError):time.sleep(1)
 else:raise RuntimeError('Probe DB readiness timeout')
 dump=decrypt('moodle.dump.gpg');original=exe('db',['pg_restore','--data-only','--file=-'],dump)
 exe('db',['pg_restore','-U','postgres','-d','moodle','--exit-on-error'],dump)
 restored=exe('db',['pg_dump','-U','postgres','-d','moodle','--data-only'])
 assert rows(original)==rows(restored),'DB digest mismatch'
 run(c+['up','-d','moodle'])
 payload=decrypt('moodledata.tgz.gpg')
 exe('moodle',['tar','-C','/var/moodledata','-xzf','-'],payload)
 with tarfile.open(fileobj=io.BytesIO(payload),mode='r:gz') as archive:
  expected={m.name.removeprefix('./'):hashlib.sha256(archive.extractfile(m).read()).hexdigest() for m in archive.getmembers() if m.isfile()}
 verify="""$a=json_decode(stream_get_contents(STDIN),true);foreach($a as $p=>$h){if(hash_file('sha256','/var/moodledata/'.$p)!==$h){exit(2);}}echo count($a);"""
 assert int(exe('moodle',['php','-r',verify],json.dumps(expected).encode()))==len(expected)
 exe('moodle',['chown','-R','www-data:www-data','/var/moodledata'])
 exe('moodle',['su','-s','/bin/sh','www-data','-c','php /var/www/moodle/admin/cli/maintenance.php --disable'])
 for _ in range(30):
  try:
   with urllib.request.urlopen('http://localhost:18702/login/index.php',timeout=5) as response:
    body=response.read();status=response.status
   assert status==200 and b'login' in body.lower();break
  except Exception:time.sleep(1)
 else:raise RuntimeError('Restored login page failed')
 courses=int(exe('db',['psql','-U','postgres','-d','moodle','-At','-c','SELECT count(*) FROM mdl_course']).decode())
 learning=json.loads(exe('db',['psql','-U','postgres','-d','moodle','-At','-c',"SELECT json_build_object('submitted_assignments',(SELECT count(*) FROM mdl_assign_submission WHERE status='submitted'),'graded_assignments',(SELECT count(*) FROM mdl_assign_grades WHERE grade>=0),'assignment_grade_min',(SELECT min(grade) FROM mdl_assign_grades WHERE grade>=0),'assignment_grade_max',(SELECT max(grade) FROM mdl_assign_grades WHERE grade>=0),'gradebook_nonnull',(SELECT count(*) FROM mdl_grade_grades WHERE finalgrade IS NOT NULL),'feedback_records',(SELECT count(*) FROM mdl_assignfeedback_comments))"]).decode())
 print(json.dumps({'status':'PASS','scope':'fresh isolated DB+data volumes and final app image','image':image,'database_image':dbimage,'tables':len(rows(original)),'rows':sum(n for n,h in rows(original).values()),'files_sha256_verified':len(expected),'courses':courses,'restored_learning_records':learning,'http_login_status':status,'elapsed_seconds':round(time.monotonic()-started,3),'probe_project':project,'live_data_untouched':True,'oidc_login_retested':False}))
finally:
 run(c+['down','-v'])
