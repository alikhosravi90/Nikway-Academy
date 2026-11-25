"""Bounded fallback when container-referenced OCI images are absent from daemon.
Docker export excludes mounted data volumes; only regular files/directories are
extracted, never following exported symlinks. This is a runtime-rootfs scan,
not proof that an inaccessible historical image was scanned.
"""
import datetime,hashlib,json,os,pathlib,subprocess,tarfile
os.umask(0o077)
ROOT=pathlib.Path(__file__).resolve().parents[2]
TOOL=ROOT.parent/'infrastructure/infra/runtime/tools/trivy';CACHE=ROOT.parent/'infrastructure/infra/runtime/trivy-cache'
out=[]
for service in ['frontend','postgres']:
 name='nikway-academy-content-'+service+'-1'
 def identity():return json.loads(subprocess.check_output(['docker','inspect','--format','{"container_id":{{json .Id}},"image_id":{{json .Image}},"started":{{json .State.StartedAt}}}',name]))
 before=identity();folder=ROOT/'infra/runtime'/('runtime-rootfs-'+service);folder.mkdir(mode=0o700,exist_ok=True)
 archive=folder/'rootfs.tar'
 with archive.open('wb') as stream:subprocess.run(['docker','export',name],stdout=stream,check=True)
 extracted=folder/'extracted';extracted.mkdir(mode=0o700,exist_ok=True)
 skipped=0;regular=0
 with tarfile.open(archive) as tf:
  for member in tf:
   if member.isfile() or member.isdir():tf.extract(member,extracted,filter='data');regular+=int(member.isfile())
   else:skipped+=1
 scan=folder/'scan.json'
 subprocess.run([str(TOOL),'rootfs','--quiet','--cache-backend','memory','--scanners','vuln','--format','json','--output',str(scan),'--cache-dir',str(CACHE),'--skip-db-update','--skip-java-db-update','--timeout','5m',str(extracted)],check=True,capture_output=True)
 report=json.loads(scan.read_text());findings=[v for r in report.get('Results',[]) for v in r.get('Vulnerabilities',[])]
 assert identity()==before,'Container identity changed during runtime-rootfs scan'
 out.append(dict(service=service,**before,High=sum(v['Severity']=='HIGH' for v in findings),Critical=sum(v['Severity']=='CRITICAL' for v in findings),regular_files=regular,skipped_nonregular_entries=skipped,export_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),scan_sha256=hashlib.sha256(scan.read_bytes()).hexdigest(),targets=[{'target':r['Target'].replace(str(extracted),'ROOTFS'),'type':r.get('Type')} for r in report.get('Results',[])]))
result={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Running container filesystem scans; inaccessible historical OCI manifests NOT scanned. docker export excludes mounted volumes. Regular files and directories extracted; symlinks/devices not followed. OS/language vulnerability analysis, no suppressions. Does not scan database contents or application logic.','scanner':'Trivy0.76.2 using recorded2026-11-25 DB snapshot','containers':out}
(ROOT/'evidence/security-content/final-content-rootfs.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
