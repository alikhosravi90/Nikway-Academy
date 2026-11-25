"""Check delivered demo files against their report and package manifests."""
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile
root=Path(sys.argv[1]); report=json.loads((root/'demo-evidence.json').read_text())
for name,digest in report['files'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest, name
for name in ('pdca-learner-candidate.zip','pdca-instructor-candidate.zip'):
    with zipfile.ZipFile(root/name) as z:
        m=json.loads(z.read('manifest.json'))
        for filename,digest in m['files'].items():
            assert hashlib.sha256(z.read(filename)).hexdigest()==digest, (name,filename)
        assert m['publication']=='NOT_RELEASED'
print('PASS: exported files and package contents match recorded SHA-256 digests')
