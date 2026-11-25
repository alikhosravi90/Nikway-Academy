#!/usr/bin/env python3
"""Explicit synthetic runtime regression; does not restart containers or use browsers."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
p = argparse.ArgumentParser()
p.add_argument('--container', required=True)
p.add_argument('--archive', required=True)
p.add_argument('--evidence', type=Path, required=True)
a = p.parse_args()

def run(args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, check=True, **kwargs).stdout

run(['docker', 'cp', str(HERE / 'content-inspect.php'), a.container + ':/tmp/nikway-content-inspect.php'])
def inspect():
    return json.loads(run(['docker', 'exec', a.container, 'php', '/tmp/nikway-content-inspect.php']))

before = inspect()
source = ROOT / 'content/examples/agent-engineering-basics.fa.json'
command = ['python3', str(HERE / 'content-import.py'), str(source), '--archive', a.archive,
           '--container', a.container, '--learner', '00000000-0000-4000-8000-000000000001',
           '--reviewer', '00000000-0000-4000-8000-000000000003']
replay = json.loads(run(command))
after = inspect()
assert replay['status'] == 'existing'
assert before == after
assert after['course_count'] == 1
course = after['courses'][0]
assert (course['pages'], course['assignments'], course['rubric_criteria'], course['enrolments']) == (3, 1, 4, 2)
with tempfile.TemporaryDirectory() as temp:
    malformed = Path(temp) / 'invalid.json'
    invalid = json.loads(source.read_text())
    invalid['course']['lessons'][0]['content'] += 'tampered without new digest'
    malformed.write_text(json.dumps(invalid))
    badcommand = command.copy()
    badcommand[2] = str(malformed)
    bad = subprocess.run(badcommand, text=True, capture_output=True)
    assert bad.returncode != 0
    assert inspect() == after
receipt = {
    'status': 'PASS_LIMITED_LOCAL_SYNTHETIC',
    'observed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'first_creation': {'course_id': 6, 'status': 'created',
                       'initial_failure': 'Missing Moodle 5.3 gradingduedate default; transaction rolled back before corrected import'},
    'replay_status': replay['status'], 'before': before, 'after': after,
    'malformed_digest_rejected_no_effect': True,
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'container': json.loads(run(['docker', 'inspect', '--format', '{{json .}}', a.container]))['Image'],
    'boundary': 'Native import and idempotency only; browser SSO/submission/grading tested separately; no Academy status sync',
}
a.evidence.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
