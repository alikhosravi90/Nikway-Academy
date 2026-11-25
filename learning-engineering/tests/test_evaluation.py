import importlib.util
import copy
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'missions/LE-04/evaluate.py'
class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(P.exists(),'evaluation analyzer missing')
        spec=importlib.util.spec_from_file_location('evaluate',P); self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
        self.data={'datasetKind':'synthetic','protocolVersion':'0.1.0','rubricVersion':'0.1.0','rows':[
          {'participantId':'P-001','phase':'pre','scores':dict(plan=1,do=1,check=0,act=0)},
          {'participantId':'P-001','phase':'post','scores':dict(plan=2,do=2,check=2,act=2)},
          {'participantId':'P-002','phase':'pre','scores':dict(plan=0,do=0,check=0,act=0)}]}
    def test_paired_denominator_and_missing(self):
        result=self.module.analyze(self.data)
        self.assertEqual(result['pairedCount'],1);self.assertEqual(result['meanPairedChange'],6)
        self.assertEqual(result['preOnlyCount'],1); self.assertEqual(result['transferCount'],0)
        self.assertEqual(result['declaredDatasetKind'],'synthetic');self.assertFalse(result['causalInference'])
    def test_duplicate_rejected(self):
        self.data['rows'].append(copy.deepcopy(self.data['rows'][0]))
        with self.assertRaises(ValueError):self.module.analyze(self.data)
    def test_out_of_range_and_boolean_rejected(self):
        for score in [3,-1,True,float('nan')]:
            self.data['rows'][0]['scores']['plan']=score
            with self.assertRaises(ValueError):self.module.analyze(self.data)
    def test_missing_score_is_not_zero(self):
        del self.data['rows'][0]['scores']['act']
        with self.assertRaises(ValueError):self.module.analyze(self.data)
    def test_unknown_personal_fields_rejected(self):
        self.data['rows'][0]['email']='not-to-be-stored'
        with self.assertRaises(ValueError):self.module.analyze(self.data)
    def test_empty_returns_no_result_not_success(self):
        self.data['rows']=[];r=self.module.analyze(self.data)
        self.assertIsNone(r['meanPairedChange']);self.assertEqual(r['status'],'NO_DATA')
    def test_observed_label_does_not_grant_approval(self):
        self.data['datasetKind']='observed-deidentified';r=self.module.analyze(self.data)
        self.assertFalse(r['consentVerified']);self.assertFalse(r['humanReviewVerified'])
    def test_incompatible_version_rejected(self):
        self.data['rubricVersion']='9.0.0'
        with self.assertRaises(ValueError):self.module.analyze(self.data)
