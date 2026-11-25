import copy
import json
import unittest
from datetime import datetime, timezone
import tempfile
import snapshot
from pathlib import Path
import bridge

class IntegrationTests(unittest.TestCase):
    def test_real_three_engine_draft_path(self):
        result = bridge.run()
        self.assertEqual(result['scope'], 'offline-real-module-draft')
        self.assertEqual(result['academy']['lifecycle'], 'draft')
        self.assertFalse(result['promotionAllowed'])
        self.assertEqual(result['academy']['course']['objectives'][0]['id'], 'le-obj-pdca')
        self.assertEqual(result['component']['learningOutcomeIds'], ['LE-OBJ-PDCA'])
        self.assertEqual(result['component']['rightsStatus'], 'internal_trial_only')
        self.assertIn('LE_RIGHTS_PENDING', result['blockers'])
        self.assertNotIn('answer', result['learnerQuiz'][0]['questions'][0])
        self.assertEqual(result['moduleChecks'], ['learning-engineering.exchange', 'content-factory.contracts+render', 'academy.content.validate_package'])

    def test_tampered_cf_rendition_rejected(self):
        component = bridge.to_component(bridge.source_package())
        parts = bridge.build_package({'id':'draft'}, [dict(component, revisionId='draft')])
        parts['text.md'] += b'changed'
        with self.assertRaisesRegex(ValueError, 'CF_RENDITION_DIGEST_MISMATCH'):
            bridge.to_academy(component, parts)

    def test_redigested_changed_source_is_not_supported(self):
        package = bridge.source_package()
        package['objects'][0]['title']['en'] += ' changed'
        package['payloadDigest'] = bridge.exchange.digest({k:v for k,v in package.items() if k!='payloadDigest'})
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_SOURCE_DIGEST'):
            bridge.to_component(package)

    def test_created_at_is_current_execution_time(self):
        before = datetime.now(timezone.utc)
        package = bridge.run()['academy']
        created = datetime.fromisoformat(package['provenance']['createdAt'].replace('Z','+00:00'))
        self.assertGreaterEqual(created, before)
        self.assertLessEqual(created, datetime.now(timezone.utc))

    def test_snapshot_uses_one_repo_and_refuses_stale_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)/'snapshots'
            snapshot.snapshot(destination=target, repo=bridge.ROOT.parents[2], receipt_path=Path(temp)/'sources.json')
            self.assertTrue((target/'cf/content_factory/cf/render.py').is_file())
            self.assertTrue((target/'academy/content/validate_package.py').is_file())
            (target/'stale.py').write_text('stale')
            with self.assertRaises(FileExistsError):
                snapshot.snapshot(destination=target, repo=bridge.ROOT.parents[2], receipt_path=Path(temp)/'sources.json')

    def test_tampered_le_package_rejected(self):
        package = bridge.source_package()
        package['objects'][0]['title']['en'] += ' changed'
        with self.assertRaisesRegex(ValueError, 'DIGEST_MISMATCH'):
            bridge.to_component(package)

    def test_unexpected_objective_rejected(self):
        package = bridge.source_package()
        for record in package['objects']:
            if record['id'] == 'LE-OBJ-PDCA': record['id'] = 'different'
        with self.assertRaises(ValueError): bridge.to_component(package)

    def test_academy_cannot_accept_untranslated_cf_object(self):
        result = bridge.run()
        with self.assertRaises(ValueError): bridge.academy.load_package(json.dumps(result['component']).encode())

    def test_academy_checksum_and_unknown_fields_fail_closed(self):
        package = bridge.run()['academy']
        package['course']['title'] += 'tampered'
        with self.assertRaisesRegex(ValueError, 'checksum'): bridge.academy.load_package(json.dumps(package).encode())
        package = bridge.run()['academy']
        package['approved'] = True
        with self.assertRaises(ValueError): bridge.academy.load_package(json.dumps(package).encode())

    def test_cf_rejects_question_without_objective_binding(self):
        component = bridge.run()['component']
        component['body']['questions'][0]['outcomeId'] = 'unbound'
        with self.assertRaises(ValueError): bridge.ComponentInput.model_validate(component)

if __name__ == '__main__': unittest.main()
