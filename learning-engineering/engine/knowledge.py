"""Offline structural knowledge checks; review labels are not trusted identities."""
import copy
import json
import math
import unicodedata
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'schemas' / 'record.schema.json'
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
RELATIONS = {
    'derived-from': ({'KnowledgeCard'}, {'Evidence'}),
    'explains': ({'KnowledgeCard'}, {'Concept'}),
    'develops': ({'Competency'}, {'Concept'}),
    'targets-competency': ({'LearningObjective'}, {'Competency'}),
    'includes-objective': ({'Curriculum'}, {'LearningObjective'}),
    'specifies': ({'ContentSpecification'}, {'LearningObjective'}),
    'assesses': ({'Assessment','Rubric'}, {'LearningObjective'}),
    'uses-rubric': ({'Assessment'}, {'Rubric'}),
    'cites': (None, {'Source'}),
    'supports': ({'Evidence'}, {'KnowledgeCard', 'Concept'}),
    'contradicts': ({'Evidence'}, {'KnowledgeCard', 'Concept'}),
    'defines': (None, {'Concept'}),
    'teaches': ({'ContentSpecification'}, {'LearningObjective'}),
}

def key(record): return (record['id'], record['version'])

def _version_order(version):
    # SemVer build metadata does not affect precedence; releases follow prereleases.
    value=version.split('+',1)[0]
    core, separator, pre=value.partition('-')
    identifiers=tuple((0,int(v)) if v.isdigit() else (1,v) for v in pre.split('.')) if separator else ()
    return (tuple(int(v) for v in core.split('.')), not bool(separator), identifiers)


def validate_records(records, delivery=False):
    """Return all discovered errors, never mutate or fetch remote references."""
    if not isinstance(records, list) or not records: return ['SCHEMA: records must be a nonempty array']
    errors, index, valid = [], {}, []
    for i, record in enumerate(records):
        values=[record]
        while values:
            value=values.pop()
            if isinstance(value,float) and not math.isfinite(value): errors.append(f'NONFINITE: record [{i}] contains a nonfinite number')
            elif isinstance(value,dict): values.extend(value.values())
            elif isinstance(value,list): values.extend(value)
        issues = sorted(VALIDATOR.iter_errors(record), key=lambda e: str(list(e.path)))
        errors.extend(f'SCHEMA [{i}] {".".join(map(str,e.path))}: {e.message}' for e in issues)
        if issues: continue
        k = key(record)
        if k in index: errors.append(f'DUPLICATE: {k}')
        else: index[k] = record
        valid.append(record)
    def resolve(owner, ref, kinds=None):
        target = index.get(key(ref))
        if target is None: errors.append(f'MISSING_REFERENCE: {key(owner)} -> {key(ref)}')
        elif kinds and target['kind'] not in kinds:
            errors.append(f'WRONG_REFERENCE_TYPE: {key(owner)} -> {key(ref)} expected {sorted(kinds)}')
        return target
    prerequisites = {}
    for r in valid:
        k, kind, data = key(r), r['kind'], r['data']
        ev = r['provenance']['evidenceRefs']
        if kind not in {'Source','Evidence'} and not ev: errors.append(f'LINEAGE_REQUIRED: {k}')
        for ref in ev: resolve(r, ref, {'Evidence'})
        for field, kinds in [('sourceRef',{'Source'}),('conceptRefs',{'Concept'}),('competencyRefs',{'Competency'}),('objectiveRefs',{'LearningObjective'}),('rubricRef',{'Rubric'}),('sequence',{'LearningObjective','ContentSpecification','Assessment'})]:
            if field in data:
                for ref in data[field] if isinstance(data[field],list) else [data[field]]: resolve(r,ref,kinds)
        if kind=='Assessment':
            rubric=index.get(key(data['rubricRef']))
            if rubric and rubric['kind']=='Rubric' and not {key(ref) for ref in data['objectiveRefs']} <= {key(ref) for ref in rubric['data']['objectiveRefs']}:
                errors.append(f'RUBRIC_OBJECTIVE_MISMATCH: {k}')
        mirrored={'explains':'conceptRefs','develops':'conceptRefs','targets-competency':'competencyRefs','includes-objective':'objectiveRefs','specifies':'objectiveRefs','assesses':'objectiveRefs','teaches':'objectiveRefs','uses-rubric':'rubricRef'}
        for relation in r['relations']:
            typ, ref = relation['type'], relation['target']
            source_kinds, target_kinds = RELATIONS.get(typ,(None,{kind}))
            if source_kinds and kind not in source_kinds: errors.append(f'WRONG_RELATION_SOURCE: {k} {typ}')
            resolve(r,ref,target_kinds)
            field=mirrored.get(typ)
            expected=None
            if field in data:
                refs=data[field] if isinstance(data[field],list) else [data[field]]
                expected={key(item) for item in refs}
            elif typ=='derived-from': expected={key(item) for item in ev}
            elif typ=='cites' and kind=='Evidence': expected={key(data['sourceRef'])}
            if expected is not None and key(ref) not in expected:
                errors.append(f'RELATION_DATA_MISMATCH: {k} {typ} -> {key(ref)}')
            if typ=='supersedes' and (ref['id']!=r['id'] or _version_order(ref['version']) >= _version_order(r['version'])):
                errors.append(f'INVALID_SUPERSEDES: {k} must supersede an older version of the same ID')
            if typ == 'prerequisiteOf':
                if kind not in {'Concept','Competency','LearningObjective','Curriculum'}: errors.append(f'WRONG_RELATION_SOURCE: {k} {typ}')
                prerequisites.setdefault(k,[]).append(key(ref))
        review, rights = r['review'], r['rights']
        if review['status'] in {'reviewed','approved'}:
            if not review['reviewer'] or review['reviewer'] == review['author'] or not review['reviewedAt']:
                errors.append(f'REVIEW_REQUIRED: {k} independent reviewer and date required')
        if rights['status']=='verified' and (rights['license']=='UNKNOWN' or not rights['evidenceUrls'] or not rights['allowedUses']): errors.append(f'RIGHTS_EVIDENCE_REQUIRED: {k}')
        if kind=='Source' and data['verificationStatus']=='verified':
            if any(data[f]=='UNKNOWN' for f in ('canonicalUrl','issuer','edition')) or not data['canonicalUrl'].startswith(('https://','http://')):
                errors.append(f'SOURCE_EVIDENCE_REQUIRED: {k}')
        if review['status']=='approved' or delivery:
            if rights['status'] != 'verified': errors.append(f'RIGHTS_PENDING: {k}')
            if kind=='Source' and data['verificationStatus']!='verified': errors.append(f'SOURCE_UNVERIFIED: {k}')
        if delivery and review['status']!='approved': errors.append(f'REVIEW_PENDING: {k}')
        if kind=='Rubric' and len({c['id'] for c in data['criteria']})!=len(data['criteria']): errors.append(f'DUPLICATE_CRITERION: {k}')
    # Approval cannot clear unresolved or unverified upstream evidence/rights.
    for r in valid:
        if r['review']['status'] != 'approved': continue
        pending=list(r['provenance']['evidenceRefs'])
        if r['kind']=='Evidence': pending.append(r['data']['sourceRef'])
        seen=set()
        while pending:
            ref=pending.pop(); target=index.get(key(ref))
            if not target or key(ref) in seen: continue
            seen.add(key(ref))
            if target['rights']['status']!='verified': errors.append(f'UPSTREAM_RIGHTS_PENDING: {key(r)} -> {key(ref)}')
            if target['kind']=='Source' and target['data']['verificationStatus']!='verified': errors.append(f'UPSTREAM_SOURCE_UNVERIFIED: {key(r)} -> {key(ref)}')
            if target['kind']=='Evidence': pending.append(target['data']['sourceRef'])
            pending.extend(target['provenance']['evidenceRefs'])
    # Iterative traversal avoids recursion failure on long prerequisite chains.
    done=set()
    for start in prerequisites:
        if start in done: continue
        active=set(); stack=[(start,False)]
        while stack:
            node, leaving=stack.pop()
            if leaving: active.discard(node); done.add(node); continue
            if node in active: errors.append(f'PREREQUISITE_CYCLE: {node}'); continue
            if node in done: continue
            active.add(node); stack.append((node,True))
            stack.extend((child,False) for child in prerequisites.get(node,[]))
    return errors

def _reject_constant(value):
    raise ValueError(f'NONFINITE: invalid JSON constant {value}')

def load_records(path):
    path=Path(path); records=[]
    for file in sorted(path.rglob('*.json')) if path.is_dir() else [path]:
        value=json.loads(file.read_text(encoding='utf-8'), parse_constant=_reject_constant)
        records.extend(value if isinstance(value,list) else [value])
    return records

def _normalize(text):
    return unicodedata.normalize('NFKC',text).translate(str.maketrans({'ي':'ی','ى':'ی','ك':'ک','\u200c':' '})).casefold()

def search(records, query):
    terms=_normalize(query).split()
    return [r for r in records if all(term in _normalize(json.dumps(r,ensure_ascii=False)) for term in terms)]

def render_markdown(records):
    lines=['# Learning Engineering knowledge index', '', 'Draft local projection; review labels are not identity verification.', '']
    for r in sorted(records,key=key):
        lines.extend([f"## {r['id']} @ {r['version']} — {r['title']['en']}", '', r['title']['fa'], '', f"Kind: {r['kind']} | Review: {r['review']['status']} | Rights: {r['rights']['status']}", '', r['summary']['en'], '', r['summary']['fa'], ''])
    return '\n'.join(lines)

def accumulate(existing, new):
    """Append revisions; exact replay is idempotent and conflicts fail atomically."""
    if not isinstance(existing,list) or not isinstance(new,list):
        raise ValueError('SCHEMA: accumulation inputs must be arrays')
    for record in existing+new:
        issues=list(VALIDATOR.iter_errors(record))
        if issues: raise ValueError('SCHEMA: '+ '; '.join(e.message for e in issues))
    result=copy.deepcopy(existing); index={}
    for record in existing:
        k=key(record)
        if k in index: raise ValueError(f'DUPLICATE: {k}')
        index[k]=record
    for record in new:
        k=key(record)
        if k in index:
            if record != index[k]: raise ValueError(f'REVISION_CONFLICT: {k}')
        else: index[k]=record; result.append(copy.deepcopy(record))
    errors=validate_records(result)
    if errors: raise ValueError('\n'.join(errors))
    return result
