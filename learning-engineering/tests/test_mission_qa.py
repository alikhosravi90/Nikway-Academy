"""Independent mission QA: local evidence cannot authorize release or human use."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

class MissionQATests(unittest.TestCase):
    def test_delivery_denial_is_structured_rights_and_review_failure(self):
        run = subprocess.run([sys.executable, '-m', 'engine.cli', 'validate', 'records', '--delivery'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(run.stderr, '')
        result = json.loads(run.stdout)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(len(result['errors']), 20)
        self.assertEqual({e.split(':', 1)[0] for e in result['errors']}, {'RIGHTS_PENDING', 'REVIEW_PENDING'})

    def test_all_rights_dossiers_preserve_operational_hold(self):
        files = list((ROOT/'missions/LE-01').glob('LE-SRC-*.json'))
        self.assertEqual(len(files), 29)
        for file in files:
            with self.subTest(file=file.name):
                dossier = json.loads(file.read_text())
                self.assertIs(dossier['rightsClearedForIntendedUse'], False)
                self.assertEqual(set(dossier['uses']), {'quotation','summary','translation','adaptation','redistribution','commercial_use'})

    def test_scientific_review_hashes_match_and_human_approval_absent(self):
        receipt = json.loads((ROOT/'missions/LE-02/review-receipt.json').read_text())
        self.assertIsNone(receipt['humanApproval'])
        self.assertEqual(receipt['reviewerType'], 'AI-agent')
        for entry in receipt['reviewedFiles']:
            with self.subTest(path=entry['path']):
                self.assertEqual(hashlib.sha256((ROOT.parent/entry['path']).read_bytes()).hexdigest(), entry['sha256'])

    def test_analyzer_hostile_shape_and_empty_results(self):
        spec = importlib.util.spec_from_file_location('le05_evaluate', ROOT/'missions/LE-04/evaluate.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        data = json.loads((ROOT/'missions/LE-04/dataset-empty.json').read_text())
        result = module.analyze(data)
        self.assertEqual(result['status'], 'NO_DATA')
        self.assertEqual(result['participantCount'], 0)
        self.assertEqual(result['pairedCount'], 0)
        self.assertIsNone(result['meanPairedChange'])
        self.assertTrue(all(v is None for v in result['phaseMeanScores'].values()))
        for row in [None, [], {'participantId':'P-001','phase':[], 'scores':{}}, {'participantId':'P-001','phase':'pre','scores':None}]:
            altered = copy.deepcopy(data)
            altered['rows'] = [row]
            with self.subTest(row=row), self.assertRaises(ValueError):
                module.analyze(altered)

    def test_missing_phases_are_not_zero_change_or_transfer_success(self):
        spec = importlib.util.spec_from_file_location('le05_evaluate_missing', ROOT/'missions/LE-04/evaluate.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        data = json.loads((ROOT/'missions/LE-04/dataset-empty.json').read_text())
        data['rows'] = [{'participantId':'P-001','phase':'pre','scores':dict(plan=2,do=2,check=2,act=2)}, {'participantId':'P-002','phase':'transfer','scores':dict(plan=0,do=0,check=0,act=0)}]
        result = module.analyze(data)
        self.assertEqual(result['pairedCount'], 0)
        self.assertIsNone(result['meanPairedChange'])
        self.assertEqual(result['preOnlyCount'], 1)
        self.assertEqual(result['transferCount'], 1)
        self.assertFalse(result['causalInference'])
        self.assertFalse(result['humanReviewVerified'])

class CIGateQATests(unittest.TestCase):
    def setUp(self):
        path = ROOT/'missions/LE-05/ci_gates.py'
        self.assertTrue(path.exists(), 'Structured CI gate helper missing')
        spec = importlib.util.spec_from_file_location('le05_ci_gates', path)
        self.gates = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.gates)

    def test_delivery_gate_requires_expected_structured_failure(self):
        valid = json.dumps({'status':'FAIL','errors':['RIGHTS_PENDING: item','REVIEW_PENDING: item']})
        self.assertTrue(self.gates.check_delivery_result(1, valid))
        for rc, output in [(0, valid), (2, valid), (127, ''), (1, 'Traceback'), (1, '{}'), (1, '[]'), (1, json.dumps({'status':'FAIL','errors':[]})), (1, json.dumps({'status':'FAIL','errors':['RIGHTS_PENDING: item']})), (1, json.dumps({'status':'FAIL','errors':['RIGHTS_PENDING: item','REVIEW_PENDING: item',42]}))]:
            with self.subTest(rc=rc, output=output):
                self.assertFalse(self.gates.check_delivery_result(rc, output))

    def test_empty_gate_requires_no_data_and_null_effect(self):
        valid = {'status':'NO_DATA','participantCount':0,'pairedCount':0,'meanPairedChange':None}
        self.assertTrue(self.gates.check_empty_result(0, json.dumps(valid)))
        for rc, output in [(1,json.dumps(valid)), (0,'Traceback'), (0,'{}'), (0,'[]')]:
            with self.subTest(rc=rc, output=output):
                self.assertFalse(self.gates.check_empty_result(rc, output))
        for key, value in [('status','DESCRIPTIVE_ONLY'),('participantCount',1),('pairedCount',1),('meanPairedChange',0)]:
            altered = dict(valid, **{key:value})
            with self.subTest(key=key):
                self.assertFalse(self.gates.check_empty_result(0, json.dumps(altered)))
