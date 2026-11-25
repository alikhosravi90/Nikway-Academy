#!/usr/bin/env python3
"""Dependency and acceptance gates; no third-party packages required."""
import argparse
import copy
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def validate_manifest(data):
    missions = data['missions']
    ids = [m['mission_id'] for m in missions]
    require(len(ids) == 12 and set(ids) == {f'M{i:02}' for i in range(1, 13)}, 'mission IDs missing or duplicated')
    roles = [r for group in data['roles'].values() for r in group]
    require(len(data['roles']) == 4 and len(roles) == len(set(roles)) == 16, 'require sixteen unique roles in four slots')
    slots = {role: slot for slot, group in data['roles'].items() for role in group}
    index = {m['mission_id']: m for m in missions}
    visiting, visited = set(), set()
    def visit(mid):
        require(mid not in visiting, 'dependency cycle')
        if mid in visited:
            return
        visiting.add(mid)
        for dependency in index[mid]['dependencies']:
            require(dependency in index, 'unknown dependency')
            visit(dependency)
        visiting.remove(mid)
        visited.add(mid)
    for m in missions:
        mid = m['mission_id']
        visit(mid)
        require(m['owner_role'] in roles, 'unknown owner')
        require(m['issue_url'].startswith('https://github.com/alikhosravi90/Nikway-Academy/issues/'), 'missing real issue URL')
        require(m['objective'] and m['acceptance_criteria'] and m['tasks'], 'incomplete contract')
        require(m['status'] in {'planned','executing','verification','blocked','accepted'}, 'invalid status')
        if mid in {'M04','M05','M06'}:
            require('M03' in m['dependencies'], 'implementation missing governance gate')
        if m['status'] == 'accepted':
            require(bool(m['evidence']), 'accepted without evidence')
            review = m['independent_review']
            require(isinstance(review, dict) and review.get('result') == 'PASS', 'accepted without independent PASS')
            require(review.get('role') in slots and slots[review['role']] != slots[m['owner_role']], 'reviewer not independent')
            require(review.get('evidence_ref'), 'review evidence missing')
            require(all(index[d]['status'] == 'accepted' for d in m['dependencies']), 'dependency not accepted')
            require(all(t['status'] == 'accepted' for t in m['tasks']), 'unfinished accepted mission')
            for evidence in m['evidence']:
                require(isinstance(evidence, dict) and all(evidence.get(k) for k in ('commit','command','result','reference')), 'incomplete evidence receipt')

def validate_action(action, schema):
    require(set(action) == set(schema['required']), 'action fields missing or unknown')
    types = {'string': str, 'integer': int, 'number': (int,float), 'array': list, 'null': type(None)}
    for key, rule in schema['properties'].items():
        value = action[key]
        if 'enum' in rule:
            require(value in rule['enum'], f'{key}: enum')
        if 'type' in rule:
            ts = rule['type'] if isinstance(rule['type'], list) else [rule['type']]
            require(any(isinstance(value, types[t]) and not (isinstance(value,bool) and t in {'number','integer'}) for t in ts), f'{key}: type')
        if 'minLength' in rule:
            require(len(value) >= rule['minLength'], f'{key}: empty')
        if 'minimum' in rule:
            require(value >= rule['minimum'], f'{key}: minimum')
        if 'maximum' in rule:
            require(value <= rule['maximum'], f'{key}: maximum')
        if rule.get('type') == 'array':
            require(all(isinstance(x,str) for x in value), f'{key}: array item type')
    require(action['parent_issue'].startswith('https://github.com/alikhosravi90/Nikway-Academy/issues/'), 'action issue missing')
    require(action['acceptance_criteria'], 'action acceptance missing')
    for key in ('created_at', 'updated_at'):
        require(datetime.fromisoformat(action[key]).tzinfo is not None, 'timestamp must include timezone')
    if action['status'] in {'accepted','closed'}:
        require(action['evidence_refs'] and action['independent_reviewer'] and action['independent_reviewer'] != action['owner'], 'action acceptance lacks evidence/reviewer')
        roles = json.loads((ROOT/'missions/local-mvp/manifest.json').read_text())['roles']
        slots = {role: slot for slot, group in roles.items() for role in group}
        require(action['owner'] in slots and action['independent_reviewer'] in slots and slots[action['owner']] != slots[action['independent_reviewer']], 'action reviewer not independent')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT/'missions/local-mvp/manifest.json').read_text())
    schema = json.loads((ROOT/'contracts/local-mvp-action.schema.json').read_text())
    action = json.loads((ROOT/'contracts/local-mvp-action.example.json').read_text())
    validate_manifest(manifest)
    validate_action(action, schema)
    negatives = 0
    if args.self_test:
        for mutation in ['cycle','false_acceptance','missing_gate','same_slot_review']:
            bad = copy.deepcopy(manifest)
            if mutation == 'cycle':
                bad['missions'][0]['dependencies'] = ['M12']
            elif mutation == 'false_acceptance':
                bad['missions'][0]['status'] = 'accepted'
                bad['missions'][0]['evidence'] = []
                bad['missions'][0]['independent_review'] = None
            elif mutation == 'missing_gate':
                bad['missions'][3]['dependencies'] = ['M01']
            else:
                m = bad['missions'][0]
                m.update(status='accepted', evidence=[{'commit':'fixture','command':'fixture','result':'PASS','reference':'fixture'}], independent_review={'result':'PASS','role':'researcher_1','evidence_ref':'fixture'})
                for t in m['tasks']: t['status'] = 'accepted'
            try: validate_manifest(bad)
            except ValueError: negatives += 1
            else: raise ValueError('negative fixture incorrectly accepted: '+mutation)
        for patch in [{'cost_limit':1},{'timeout':0},{'attempt_count':4},{'status':'accepted'},{'unexpected':'value'}]:
            bad = dict(action, **patch)
            try: validate_action(bad, schema)
            except ValueError: negatives += 1
            else: raise ValueError('negative action incorrectly accepted')
    print(json.dumps({'result':'PASS','missions':12,'roles':16,'slots':4,'negative_fixtures':negatives,'runtime_acceptance':'NOT_ASSESSED'}))

if __name__ == '__main__':
    main()
