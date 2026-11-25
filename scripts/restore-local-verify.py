#!/usr/bin/env python3
"""Verify encrypted dump restoration by per-table row counts and canonical COPY hashes.
Plaintext stays in process memory; output contains only counts/digests, never rows.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

root = Path(__file__).resolve().parents[1]
os.chdir(root)
if len(sys.argv) != 2 or not Path(sys.argv[1]).is_file():
    raise SystemExit('Usage: scripts/restore-local-verify.py ENCRYPTED_BACKUP')
passfile = os.environ.get('BACKUP_PASSPHRASE_FILE')
if not passfile:
    raise SystemExit('Set BACKUP_PASSPHRASE_FILE to a private local file.')
compose = ['scripts/local-compose.sh', 'exec', '-T', 'postgres']
def run(args, data=None):
    result = subprocess.run(args, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        # Avoid dumping plaintext row data from error messages.
        raise RuntimeError(f'Command failed: {args[0]} (exit {result.returncode}); diagnostic suppressed to protect backup data')
    return result.stdout

def canonical(data):
    result = {}; table = None; rows = []
    for line in data.splitlines():
        if line.startswith(b'COPY ') and line.endswith(b' FROM stdin;'):
            table = line.decode(); rows = []
        elif table is not None and line == b'\\.':
            result[table] = {'rows': len(rows), 'sha256': hashlib.sha256(b'\n'.join(sorted(rows))).hexdigest()}
            table = None
        elif table is not None:
            rows.append(line)
    if table is not None or not result:
        raise RuntimeError('Incomplete or empty COPY stream')
    return result

archive = run(['gpg', '--batch', '--pinentry-mode', 'loopback', '--passphrase-file', passfile, '--decrypt', sys.argv[1]])
expected = canonical(run(compose + ['pg_restore', '--data-only', '--file=-'], archive))
db = 'academy_restore_' + uuid.uuid4().hex[:16]
run(compose + ['createdb', '-U', 'postgres', db])
try:
    run(compose + ['pg_restore', '-U', 'postgres', '--exit-on-error', '-d', db], archive)
    actual = canonical(run(compose + ['pg_dump', '-U', 'postgres', '-d', db, '--data-only']))
    if expected != actual:
        raise RuntimeError('Restored table counts or canonical row digests differ from encrypted archive')
    print(json.dumps({'status': 'PASS', 'method': 'Encrypted archive COPY rows vs restored database COPY rows; each table rows sorted before SHA256', 'tables': len(actual), 'total_rows': sum(x['rows'] for x in actual.values()), 'table_evidence': actual}, indent=2))
finally:
    run(compose + ['dropdb', '-U', 'postgres', '--if-exists', db])
