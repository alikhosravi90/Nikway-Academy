"""Validate local semantic authoring assets; no duplicate record graph traversal."""
import json
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator
from .knowledge import RELATIONS, SCHEMA as RECORD_SCHEMA

SCHEMAS = Path(__file__).resolve().parents[1] / 'schemas'

def validate_semantics(ontology, glossary, records):
    """Return structural and vocabulary consistency errors; never approve semantics."""
    errors = []
    for name, value in [('ontology', ontology), ('glossary', glossary)]:
        schema = json.loads((SCHEMAS / f'{name}.schema.json').read_text())
        errors.extend(f'{name.upper()}_SCHEMA: {list(e.path)} {e.message}'
                      for e in Draft202012Validator(schema).iter_errors(value))
    if errors:
        return errors  # shape must be safe before semantic access
    domains = [d['id'] for d in ontology['domains']]
    for code, values in [('DOMAIN', domains), ('TERM', [e['id'] for e in glossary['entries']]),
                         ('RELATION', [r['type'] for r in ontology['relationTypes']])]:
        errors.extend(f'DUPLICATE_{code}: {v}' for v, n in Counter(values).items() if n > 1)
    domain_set = set(domains)
    for entry in glossary['entries']:
        errors.extend(f'GLOSSARY_DOMAIN: {entry["id"]} {d}' for d in entry['domainIds'] if d not in domain_set)
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get('domainIds'), list):
            errors.append('RECORD_DOMAIN: malformed record domainIds')
            continue
        errors.extend(f'RECORD_DOMAIN: {record.get("id")} {d}' for d in record['domainIds']
                      if not isinstance(d, str) or d not in domain_set)
    kinds = set(RECORD_SCHEMA['properties']['kind']['enum'])
    relations = set(RECORD_SCHEMA['properties']['relations']['items']['properties']['type']['enum'])
    if set(ontology['entityKinds']) != kinds:
        errors.append('ENTITY_ENUM: ontology differs from record schema')
    if {r['type'] for r in ontology['relationTypes']} != relations:
        errors.append('RELATION_ENUM: ontology differs from record schema')
    for relation in ontology['relationTypes']:
        name = relation['type']
        a, b = set(relation['fromKinds']), set(relation['toKinds'])
        if not a <= kinds or not b <= kinds:
            errors.append(f'RELATION_KIND: {name}')
        if name in RELATIONS:
            expected_a, expected_b = RELATIONS[name]
            expected_a = kinds if expected_a is None else expected_a
        elif name == 'prerequisiteOf':
            expected_a = expected_b = {'Concept','Competency','LearningObjective','Curriculum'}
        elif name in {'derivesFrom','supersedes'}:
            expected_a = expected_b = kinds
        else:
            continue
        if (a != expected_a or b != expected_b or
            relation['sameKindRequired'] != (name in {'prerequisiteOf','derivesFrom','supersedes'}) or
            relation['acyclic'] != (name in {'prerequisiteOf','supersedes'})):
            errors.append(f'RELATION_DEFINITION: {name} differs from executable vocabulary')
    return errors
