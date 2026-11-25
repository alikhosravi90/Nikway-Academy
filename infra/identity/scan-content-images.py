"""Scan immutable images selected from candidate Compose containers; no mutations."""
import concurrent.futures,datetime,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
TOOL=ROOT.parent/'infrastructure/infra/runtime/tools/trivy';CACHE=ROOT.parent/'infrastructure/infra/runtime/trivy-cache'
def output(cmd):return subprocess.check_output(cmd,text=True)
ids=output(['docker','ps','-aq','--filter','label=com.docker.compose.project=nikway-academy-content']).split()
images=[]
for cid in ids:
 x=json.loads(output(['docker','inspect','--format','{"container":{{json .Name}},"container_id":{{json .Id}},"image_id":{{json .Image}},"service":{{json (index .Config.Labels "com.docker.compose.service")}}}',cid]))
 if x['service'] in ['api','frontend','postgres','keycloak']:images.append(x)
assert len(images)==4

def scan(x):
 path=ROOT/'infra/runtime'/('final-content-scan-'+x['service']+'.json')
 available=subprocess.run(['docker','image','inspect',x['image_id']],capture_output=True).returncode==0
 if not available:
  x.update(scan_status='IMAGE_UNAVAILABLE',scope='Cannot inspect historical container image; separate runtime-rootfs receipt required',High=None,Critical=None)
  return x
 p=subprocess.run([str(TOOL),'image','--quiet','--cache-backend','memory','--scanners','vuln','--format','json','--output',str(path),'--cache-dir',str(CACHE),'--skip-db-update','--skip-java-db-update','--timeout','5m',x['image_id']],capture_output=True,timeout=330)
 if p.returncode:raise RuntimeError('Trivy failed for '+x['service'])
 data=json.loads(path.read_text());findings=[v for r in data['Results'] for v in r.get('Vulnerabilities',[])]
 x['scan_status']='PASS'
 x['High']=sum(v['Severity']=='HIGH' for v in findings);x['Critical']=sum(v['Severity']=='CRITICAL' for v in findings)
 x['raw_report_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();x['targets']=[{'target':r['Target'],'type':r.get('Type')} for r in data['Results']]
 assert data['Metadata']['ImageID']==x['image_id'],'Scanned identity mismatch'
 return x
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(scan,images))
out={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scanner':'Trivy0.76.2','scope':'Full selected runtime OS/language vulnerability scans; no suppressions; only High/Critical summarized; does not prove absence of unknown/application defects','database':json.loads((CACHE/'db/metadata.json').read_text()),'java_database':json.loads((CACHE/'java-db/metadata.json').read_text()),'images':results,'custom_maintenance':'Keycloak is locally maintained source/dependency build, not vendor-supported. Upstream tests skipped; local tests separate.'}
(ROOT/'evidence/security-content/final-content-images.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({x['service']:{'image_id':x['image_id'],'High':x['High'],'Critical':x['Critical']} for x in results},indent=2))
