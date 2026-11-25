import copy
import json
from pathlib import Path
import unittest
from engine.semantics import validate_semantics

ROOT = Path(__file__).resolve().parents[1]

class SemanticTests(unittest.TestCase):
    def setUp(self):
        self.ontology = json.loads((ROOT/'semantics/ontology.json').read_text())
        self.glossary = json.loads((ROOT/'semantics/glossary.json').read_text())
        self.records = [json.loads(p.read_text()) for p in (ROOT/'records').glob('*.json')]
    def errors(self): return validate_semantics(self.ontology,self.glossary,self.records)
    def test_current_artifacts(self): self.assertEqual(self.errors(),[])
    def test_duplicate_domain(self):
        self.ontology['domains'].append(copy.deepcopy(self.ontology['domains'][0]))
        self.assertTrue(any('DUPLICATE_DOMAIN' in e for e in self.errors()))
    def test_duplicate_term(self):
        self.glossary['entries'].append(copy.deepcopy(self.glossary['entries'][0]))
        self.assertTrue(any('DUPLICATE_TERM' in e for e in self.errors()))
    def test_glossary_unknown_domain(self):
        self.glossary['entries'][0]['domainIds']=['LE-UNKNOWN']
        self.assertTrue(any('GLOSSARY_DOMAIN' in e for e in self.errors()))
    def test_record_unknown_domain(self):
        self.records[0]['domainIds']=['LE-UNKNOWN']
        self.assertTrue(any('RECORD_DOMAIN' in e for e in self.errors()))
    def test_entity_enum_drift(self):
        self.ontology['entityKinds'].pop()
        self.assertTrue(any('ENTITY_ENUM' in e for e in self.errors()))
    def test_relation_enum_drift(self):
        self.ontology['relationTypes'].pop()
        self.assertTrue(any('RELATION_ENUM' in e for e in self.errors()))
    def test_relation_unknown_kind(self):
        self.ontology['relationTypes'][0]['toKinds']=['Unknown']
        self.assertTrue(any('RELATION_KIND' in e for e in self.errors()))
    def test_relation_range_drift(self):
        self.ontology['relationTypes'][0]['toKinds']=['Source']
        self.assertTrue(any('RELATION_DEFINITION' in e for e in self.errors()))
    def test_missing_fa(self):
        del self.glossary['entries'][0]['definition']['fa']
        self.assertTrue(any('GLOSSARY_SCHEMA' in e for e in self.errors()))
    def test_missing_en(self):
        del self.ontology['domains'][0]['preferredLabel']['en']
        self.assertTrue(any('ONTOLOGY_SCHEMA' in e for e in self.errors()))
    def test_bad_shape_returns_errors(self):
        self.assertTrue(validate_semantics([],{},[]))
    def test_extensible_term_count(self):
        term=copy.deepcopy(self.glossary['entries'][0]);term['id']='LE-TERM-NEW'
        self.glossary['entries'].append(term)
        self.assertEqual(self.errors(),[])
