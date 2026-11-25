#!/usr/bin/env python3
"""Real isolated disabled-tool API check; never restart the live API.
ACADEMY_RUNTIME_ROOT must point at the existing isolated local Compose checkout.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('real_checks',ROOT/'backend/tests/test_integration.py')
checks=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)
container='nikway-academy-kill-switch-'+uuid4().hex[:10]
compose=str(checks.ROOT/'scripts/local-compose.sh')
created=False
result={'check':'real_disabled_tool_boundary','result':'FAIL','public_deployment':False}
try:
    token=checks.login('learner-a')['access_token']
    command=[compose,'run','--no-deps','-d','--name',container,'-p','127.0.0.1:18402:8000','-e','TOOLS_ENABLED=false','api']
    subprocess.run(command,check=True,capture_output=True,text=True,timeout=60)
    created=True
    checks.API='http://localhost:18402'
    ready=False
    for _ in range(40):
        try:
            if checks.request('/api/health')[0]==200:
                ready=True;break
        except OSError: pass
        time.sleep(.25)
    if not ready: raise RuntimeError('Isolated API did not become ready')
    status,body=checks.request('/api/tools/invoke',token,{'name':'learning.progress','arguments':{}})
    if status!=403 or body.get('message')!='Tool execution disabled':
        raise RuntimeError('Disabled tool request did not fail closed')
    if checks.request('/api/me',token)[0]!=200:
        raise RuntimeError('Identity boundary unavailable during kill-switch test')
    result.update(result='PASS',http_status=status,reason=body['message'],real_oidc=True,image_id=subprocess.check_output(['docker','inspect','--format','{{.Image}}',container],text=True).strip())
finally:
    if created:
        subprocess.run(['docker','rm','-f',container],check=True,capture_output=True,text=True,timeout=30)
        result['test_container_removed']=True
    output=Path(os.environ.get('ACADEMY_KILL_SWITCH_EVIDENCE',str(ROOT/'evidence/local-mvp-governance-kill-switch.json')))
    output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
