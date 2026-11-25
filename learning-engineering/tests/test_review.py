import copy
import unittest
from test_exchange import source
try:
    from engine.review import review_revision
except ImportError: review_revision=None
class ReviewTests(unittest.TestCase):
    def setUp(self): self.assertTrue(callable(review_revision),'review workflow missing')
    def test_review_creates_revision_preserving_original(self):
        records=[source()]; before=copy.deepcopy(records)
        result=review_revision(records,'LE-SRC-TEST','0.1.0','0.2.0','independent-fixture-reviewer','2026-11-25T12:00:00Z')
        self.assertEqual(records,before); self.assertEqual(len(result),2)
        self.assertEqual(result[-1]['review']['status'],'reviewed')
        self.assertEqual(result[-1]['relations'][-1]['type'],'supersedes')
        self.assertEqual(result[-1]['rights']['status'],'pending verification')
    def test_self_review_rejected(self):
        with self.assertRaises(ValueError): review_revision([source()],'LE-SRC-TEST','0.1.0','0.2.0','test','2026-11-25T12:00:00Z')
    def test_missing_record_rejected(self):
        with self.assertRaises(ValueError): review_revision([source()],'LE-MISSING','0.1.0','0.2.0','other','2026-11-25T12:00:00Z')
    def test_non_increasing_version_rejected(self):
        with self.assertRaises(ValueError): review_revision([source()],'LE-SRC-TEST','0.1.0','0.1.0','other','2026-11-25T12:00:00Z')
    def test_skip_proposed_rejected(self):
        r=source(); r['review'].update(status='reviewed',reviewer='other',reviewedAt='2026-11-25T12:00:00Z')
        with self.assertRaises(ValueError): review_revision([r],'LE-SRC-TEST','0.1.0','0.2.0','third','2026-11-25T12:00:00Z')
