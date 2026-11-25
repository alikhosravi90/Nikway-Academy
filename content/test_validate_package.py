import copy
import json
from pathlib import Path
import unittest
from content.validate_package import compute_digest, load_package, validate_package

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.p=json.loads((Path(__file__).parent/'examples/agent-engineering-basics.fa.json').read_text())
    def check_bad(self, mutate):
        mutate(self.p); self.p['integrity']['digest']=compute_digest(self.p)
        self.assertTrue(validate_package(self.p))
    def test_original_roundtrip(self):
        self.assertEqual(load_package(json.dumps(self.p,ensure_ascii=False).encode()),self.p)
    def test_key_order_digest(self):
        self.assertEqual(compute_digest(dict(reversed(list(self.p.items())))),compute_digest(self.p))
    def test_tamper(self):
        self.p['course']['title']='changed';self.assertIn('checksum mismatch',validate_package(self.p))
    def test_unknown_field(self): self.check_bad(lambda p:p.update(tenantId='caller-chosen'))
    def test_missing_reference(self): self.check_bad(lambda p:p['course']['lessons'][0].update(objectiveIds=['missing']))
    def test_duplicate_id(self): self.check_bad(lambda p:p['course']['lessons'][1].update(id=p['course']['lessons'][0]['id']))
    def test_position_gap(self): self.check_bad(lambda p:p['course']['lessons'][1].update(position=3))
    def test_uncovered_objective(self): self.check_bad(lambda p:p['course']['objectives'].append(dict(p['course']['objectives'][0],id='new-objective')))
    def test_anchor_gap(self): self.check_bad(lambda p:p['course']['rubric']['criteria'][0]['anchors'].pop())
    def test_score_overflow(self): self.check_bad(lambda p:p['course']['rubric'].update(passScore=200))
    def test_wrong_rubric(self): self.check_bad(lambda p:p['course']['assessment'].update(rubricId='missing'))
    def test_character_bounds(self): self.check_bad(lambda p:p['course']['assessment'].update(minCharacters=9000,maxCharacters=100))
    def test_not_approval(self): self.check_bad(lambda p:p.update(lifecycle='published'))
    def test_third_party(self): self.check_bad(lambda p:p['rights'].update(containsThirdPartyMaterial=True))
    def test_duplicate_json(self):
        with self.assertRaises(ValueError):load_package(b'{"a":1,"a":2}')
    def test_deep_json(self):
        for depth in (25, 2000):
            with self.assertRaises(ValueError):
                load_package(b'{"nested":' + b'['*depth + b'0' + b']'*depth + b'}')
    def test_nonobject(self):
        for raw in (b'[]', b'null', b'true', b'1'):
            with self.assertRaises(ValueError): load_package(raw)
    def test_nonfinite(self):
        with self.assertRaises(ValueError):load_package(b'{"a":NaN}')
    def test_size(self):
        with self.assertRaises(ValueError):load_package(b' '*(128*1024+1))
    def test_unicode_normalization(self): self.check_bad(lambda p:p['course'].update(title='e\u0301'))
    def test_invalid_example(self):
        self.assertTrue(validate_package(json.loads((Path(__file__).parent/'examples/invalid-objective-reference.json').read_text())))

if __name__=='__main__': unittest.main()
