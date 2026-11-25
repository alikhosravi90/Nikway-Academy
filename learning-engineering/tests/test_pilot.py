import unittest
try:
    from engine.pilot import run_pilot
except ImportError:
    run_pilot=None
class PilotTests(unittest.TestCase):
    def test_reference_chain_and_quarantined_roundtrip(self):
        self.assertTrue(callable(run_pilot),'pilot missing')
        r=run_pilot()
        self.assertEqual(r['status'],'PASS_LOCAL_SYNTHETIC')
        self.assertEqual(r['recordCount'],10)
        self.assertEqual(len(r['chain']),9)
        self.assertEqual(r['contentFactory'],'quarantined')
        self.assertEqual(r['learningOS'],'quarantined')
        self.assertTrue(r['replayUnchanged'])
        self.assertFalse(r['learnerEffectivenessMeasured'])
