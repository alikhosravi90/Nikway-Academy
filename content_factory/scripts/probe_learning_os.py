"""Read-only probe of the existing local Academy; no login or data mutation."""
import json
from pathlib import Path
from datetime import datetime,timezone
import httpx
root=Path(__file__).resolve().parents[1]
base='http://127.0.0.1:18400'
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'target':base,'mode':'READ_ONLY','mutations':0}
try:
    with httpx.Client(timeout=5) as c:
        health=c.get(base+'/api/health'); health.raise_for_status()
        response=c.get(base+'/api/openapi.json'); response.raise_for_status(); api=response.json()
        report.update(health=health.json(),apiInfo=api['info'],paths=sorted(api['paths']))
        report['unauthenticatedCourseStatus']=c.get(base+'/api/courses').status_code
        report['contentImportEndpointPresent']='/api/content/import' in api['paths']
        report['versionedCandidateEndpointPresent']='/v1/candidates' in api['paths']
        report['result']='PARTIAL: live API reachable; versioned Content Factory ingestion/delivery contract absent'
except (httpx.HTTPError,ValueError) as e:
    report.update(result='BLOCKED: live API unavailable',errorType=type(e).__name__)
(root/'evidence/learning-os-probe.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
