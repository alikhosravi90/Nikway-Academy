#!/usr/bin/env python3
"""Wait for actual local API and identity availability; no credentials logged."""
import json, time, urllib.request
from pathlib import Path
values = dict(line.split("=",1) for line in (Path(__file__).resolve().parents[1]/"infra/runtime/.env").read_text().splitlines() if "=" in line)
api_port=values.get("ACADEMY_API_PORT","18400")
ui_port=values.get("ACADEMY_UI_PORT","18401")
idp_port=values.get("ACADEMY_IDP_PORT","18480")
checks = [(f'http://localhost:{api_port}/api/health','status','ok'),(f'http://localhost:{idp_port}/realms/academy/.well-known/openid-configuration','issuer',f'http://localhost:{idp_port}/realms/academy')]
for attempt in range(90):
    try:
        for url,key,value in checks:
            with urllib.request.urlopen(url,timeout=2) as response:
                if json.load(response).get(key) != value: raise ValueError('unexpected readiness response')
        with urllib.request.urlopen(f'http://localhost:{ui_port}/',timeout=2) as response:
            if response.status != 200: raise ValueError('UI unavailable')
        print(f'READY: http://localhost:{ui_port} (local synthetic MVP)')
        break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit('Readiness timeout; inspect scripts/local-compose.sh ps and service logs privately')
