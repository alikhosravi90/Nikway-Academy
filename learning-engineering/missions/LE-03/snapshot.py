"""Export pinned tracked sources from one Git repository; refuse existing snapshots."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent
SOURCES = {
 'le': ('3ff3f5df28d3f39968e42ba583b61e2a1dcf1b1b', ['learning-engineering/engine','learning-engineering/schemas','learning-engineering/records']),
 'cf': ('32423ee7963a213fc5ecd89457d42a1c63491385', ['content_factory/cf']),
 'academy': ('7364427aee7e69ff2e872e66bafb8df129faeaad', ['content','contracts/content-package.schema.json','backend/app/rules.py','backend/app/content_api.py']),
}
def snapshot(destination=None, repo=None, receipt_path=None):
    destination=Path(destination) if destination is not None else ROOT/'.snapshots'
    repo=Path(repo) if repo is not None else Path(os.environ.get('LE03_SOURCE_REPO',str(ROOT.parents[2])))
    receipt_path=Path(receipt_path) if receipt_path is not None else ROOT/'evidence/sources.json'
    # Never overlay an old export with a new one. Failed runs also require a fresh destination.
    destination.mkdir(parents=True,exist_ok=False)
    receipt = {}
    for name,(sha,paths) in SOURCES.items():
        archive = subprocess.check_output(['git','-C',str(repo),'archive',sha,*paths])
        target=destination/name; target.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar: tar.extractall(target,filter='data')
        receipt[name]={'repository':str(repo),'pinnedCommit':sha,'observedHead':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),'archiveSha256':hashlib.sha256(archive).hexdigest(),'files':{str(p.relative_to(target)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(target.rglob('*')) if p.is_file()}}
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__': snapshot()
