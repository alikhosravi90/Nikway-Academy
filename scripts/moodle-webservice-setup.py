#!/usr/bin/env python3
"""Provision an explicitly read-only local service; never print credentials."""
import json, os, pathlib, subprocess
root = pathlib.Path(__file__).resolve().parents[1]
container = 'nikway-academy-moodle-moodle-1'
for source, target in [('infra/moodle/content-binding.php','/tmp/nikway-content-binding.php'),('infra/moodle/webservice-provision.php','/tmp/nikway-webservice-provision.php')]:
    subprocess.run(['docker','cp',str(root/source),f'{container}:{target}'],check=True,stdout=subprocess.DEVNULL)
result = subprocess.run(['docker','exec',container,'php','/tmp/nikway-webservice-provision.php'],check=True,capture_output=True)
data=json.loads(result.stdout)
out=root/'infra/moodle/runtime/webservice-tokens.json'
out.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
os.fchmod(fd,0o600)
with os.fdopen(fd,'w') as f: json.dump(data,f)
print('Read-only Moodle service configured; private token file written (0600); seven-day token lifetime.')
