from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
paths = sorted((root / 'architecture/v0.2').glob('*.md'))
ids = set()
errors = []
for p in paths:
    if p.name == 'README.md':
        continue
    s = p.read_text(encoding='utf-8')
    m = re.findall(r'\*\*Document ID:\*\* (ARC-\d+)', s)
    if len(m) != 1 or m[0] in ids:
        errors.append(f'{p}: missing or duplicate ID')
    else:
        ids.add(m[0])
    for field in ('Document revision', 'Review status', 'Owner role', 'Dependencies'):
        if f'**{field}:**' not in s:
            errors.append(f'{p}: missing {field}')
    for target in re.findall(r'\]\(([^)]+)\)', s):
        if target.startswith(('./', '../')) and not (p.parent / target.split('#')[0]).exists():
            errors.append(f'{p}: missing link {target}')
if len(ids) < 24:
    errors.append('Expected at least 24 architecture IDs')
print('\n'.join(errors) if errors else f'PASS: {len(ids)} architecture documents; metadata and relative links checked')
sys.exit(bool(errors))
