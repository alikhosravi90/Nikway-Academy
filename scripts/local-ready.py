#!/usr/bin/env python3
"""Wait for actual local API and identity availability; no credentials logged."""
import json, time, urllib.request
checks = [('http://localhost:18400/api/health','status','ok'),('http://localhost:18480/realms/academy/.well-known/openid-configuration','issuer','http://localhost:18480/realms/academy')]
for attempt in range(90):
    try:
        for url,key,value in checks:
            with urllib.request.urlopen(url,timeout=2) as response:
                if json.load(response).get(key) != value: raise ValueError('unexpected readiness response')
        with urllib.request.urlopen('http://localhost:18401/',timeout=2) as response:
            if response.status != 200: raise ValueError('UI unavailable')
        print('READY: http://localhost:18401 (local synthetic MVP)')
        break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit('Readiness timeout; inspect scripts/local-compose.sh ps and service logs privately')
