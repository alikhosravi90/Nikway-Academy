#!/usr/bin/env python3
"""Validate before invoking the privileged Moodle core-API adapter."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from content.validate_package import load_package


ROLE_SUBJECTS = {
    'learner': '00000000-0000-4000-8000-000000000001',
    'reviewer': '00000000-0000-4000-8000-000000000003',
}


def validate_enrolments(learners, reviewers):
    for role, subjects in [('learner', learners), ('reviewer', reviewers)]:
        if any(subject != ROLE_SUBJECTS[role] for subject in subjects):
            raise ValueError(f'Unauthorized synthetic {role} subject')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package', type=Path)
    parser.add_argument('--archive', type=Path, required=True,
                        help='Private operator directory outside Moodle; exact original bytes retained')
    parser.add_argument('--container', required=True, help='Explicit isolated Moodle container name')
    parser.add_argument('--learner', action='append', default=[])
    parser.add_argument('--reviewer', action='append', default=[])
    args = parser.parse_args()
    raw = args.package.read_bytes()
    package = load_package(raw)  # No Docker calls or writes before strict admission succeeds.
    validate_enrolments(args.learner, args.reviewer)
    archive = args.archive.resolve()
    archive.mkdir(parents=True, exist_ok=True, mode=0o700)
    sha = hashlib.sha256(raw).hexdigest()
    original = archive / (sha + '.json')
    if original.exists():
        if original.read_bytes() != raw:
            raise ValueError('Archive collision')
    else:
        with original.open('xb') as stream:
            stream.write(raw)
        original.chmod(0o600)
    envelope = {'package': package, 'raw_sha256': sha,
                'learners': args.learner, 'reviewers': args.reviewer}
    # PHP is copied to a fixed ephemeral path, never a web-accessible upload.
    subprocess.run(['docker', 'cp', str(Path(__file__).with_suffix('.php')),
                    args.container + ':/tmp/nikway-content-import.php'], check=True)
    result = subprocess.run(['docker', 'exec', '-i', args.container, 'php',
                             '/tmp/nikway-content-import.php'],
                            input=json.dumps(envelope, ensure_ascii=False), text=True,
                            capture_output=True, check=True)
    receipt = json.loads(result.stdout)
    receipt.update(source_archive=str(original), raw_sha256=sha)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
