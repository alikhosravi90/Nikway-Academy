"""Offline admission and exact-source preservation; no Docker/runtime calls."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('adapter', HERE / 'content-import.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class Admission(unittest.TestCase):
    def test_role_subjects_fail_closed_before_any_side_effect(self):
        source = adapter.ROOT / 'content/examples/agent-engineering-basics.fa.json'
        for role, subject in [
            ('learner', '00000000-0000-4000-8000-000000000002'),
            ('reviewer', '00000000-0000-4000-8000-000000000002'),
            ('learner', adapter.ROLE_SUBJECTS['reviewer']),
            ('reviewer', adapter.ROLE_SUBJECTS['learner']),
            ('learner', 'learner-a'), ('reviewer', 'reviewer-a'),
        ]:
            with self.subTest(role=role, subject=subject), tempfile.TemporaryDirectory() as temp:
                archive = Path(temp) / 'archive'
                with patch('sys.argv', ['adapter', str(source), '--archive', str(archive), '--container', 'unused', '--' + role, subject]), patch.object(subprocess, 'run') as run:
                    with self.assertRaises(ValueError):
                        adapter.main()
                    run.assert_not_called()
                    self.assertFalse(archive.exists())

    def test_exact_subjects_allowed(self):
        adapter.validate_enrolments([adapter.ROLE_SUBJECTS['learner']], [adapter.ROLE_SUBJECTS['reviewer']])

    def test_invalid_package_never_calls_docker_or_archives(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'bad.json'
            source.write_text('{"schemaVersion":"unknown"}')
            archive = Path(temp) / 'archive'
            with patch('sys.argv', ['adapter', str(source), '--archive', str(archive), '--container', 'unused']), patch.object(subprocess, 'run') as run:
                with self.assertRaises(ValueError):
                    adapter.main()
                run.assert_not_called()
                self.assertFalse(archive.exists())

    def test_preserves_exact_original_and_validates_before_execution(self):
        source = adapter.ROOT / 'content/examples/agent-engineering-basics.fa.json'
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.CompletedProcess([], 0, '{"status":"created"}', '')
            with patch('sys.argv', ['adapter', str(source), '--archive', temp, '--container', 'isolated']), patch.object(subprocess, 'run', return_value=result) as run, patch('builtins.print'):
                adapter.main()
                self.assertEqual(len(run.call_args_list), 3)
                envelope = json.loads(run.call_args_list[2].kwargs['input'])
                self.assertEqual(envelope['package']['packageId'], '74f529fe-c81d-4d0c-98c8-56c31cfdd001')
                self.assertEqual(next(Path(temp).glob('*.json')).read_bytes(), source.read_bytes())


if __name__ == '__main__':
    unittest.main()
