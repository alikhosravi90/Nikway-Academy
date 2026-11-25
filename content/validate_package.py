"""Strict portable package validation. Requires jsonschema==4.26.0."""
import hashlib
import json
from pathlib import Path
import unicodedata
from jsonschema import Draft202012Validator, FormatChecker

MAX_BYTES = 128 * 1024
SCHEMA = json.loads((Path(__file__).resolve().parents[1] / 'contracts/content-package.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

def compute_digest(package):
    payload = {k: v for k, v in package.items() if k != 'integrity'}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                   separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result

def load_package(raw: bytes):
    if len(raw) > MAX_BYTES:
        raise ValueError('package exceeds 128 KiB')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError('non-finite number')))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('invalid UTF-8 JSON') from exc
    errors = validate_package(value)
    if errors:
        raise ValueError('; '.join(errors))
    return value

def validate_package(package):
    errors = [f"{'/'.join(map(str, e.absolute_path)) or '$'}: {e.message}" for e in VALIDATOR.iter_errors(package)]
    if errors:
        return errors
    def walk(value):
        if isinstance(value, str) and unicodedata.normalize('NFC', value) != value:
            errors.append('all strings must use NFC Unicode normalization')
        elif isinstance(value, float):
            errors.append('floating point numbers forbidden')
        elif isinstance(value, dict):
            for key, item in value.items(): walk(key); walk(item)
        elif isinstance(value, list):
            for item in value: walk(item)
    walk(package)
    if len(json.dumps(package, ensure_ascii=False, allow_nan=False).encode()) > MAX_BYTES:
        errors.append('package exceeds 128 KiB')
    c = package['course']; objectives = [o['id'] for o in c['objectives']]
    lessons = c['lessons']; rubric = c['rubric']; criteria = rubric['criteria']
    for label, ids in [('objective', objectives), ('lesson', [l['id'] for l in lessons]), ('criterion', [x['id'] for x in criteria])]:
        if len(set(ids)) != len(ids): errors.append(f'duplicate {label} id')
    if [l['position'] for l in lessons] != list(range(1, len(lessons)+1)):
        errors.append('lessons must have contiguous ordered positions')
    for item in lessons + criteria:
        if len(set(item['objectiveIds'])) != len(item['objectiveIds']) or not set(item['objectiveIds']) <= set(objectives):
            errors.append('invalid objective references')
    if set(objectives) != {x for l in lessons for x in l['objectiveIds']} or set(objectives) != {x for q in criteria for x in q['objectiveIds']}:
        errors.append('every objective requires lesson and assessment coverage')
    for q in criteria:
        if sorted(a['score'] for a in q['anchors']) != list(range(q['maxScore']+1)):
            errors.append('rubric anchors must cover every score exactly once')
    if rubric['passScore'] > sum(q['maxScore'] for q in criteria): errors.append('passScore exceeds maximum')
    if c['assessment']['rubricId'] != rubric['id']: errors.append('assessment rubric reference mismatch')
    if c['assessment']['minCharacters'] > c['assessment']['maxCharacters']: errors.append('invalid assessment bounds')
    if package['provenance']['sources']: errors.append('third-party source admission unsupported in this local profile')
    if package['integrity']['digest'] != compute_digest(package): errors.append('checksum mismatch')
    return errors

if __name__ == '__main__':
    import sys
    try:
        load_package(Path(sys.argv[1]).read_bytes())
    except (ValueError, OSError) as exc:
        print(f'INVALID: {exc}'); sys.exit(1)
    print('VALID: offline contract and checksum only; human approval not established')
