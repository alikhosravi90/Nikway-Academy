import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from test_exchange import source

class CLITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name); self.records=self.path/'records.json'
        self.records.write_text(json.dumps([source()],ensure_ascii=False))
    def run_cli(self,*args):
        return subprocess.run([sys.executable,'-m','engine.cli',*map(str,args)],capture_output=True,text=True)
    def test_validate_and_search(self):
        r=self.run_cli('validate',self.records); self.assertEqual(r.returncode,0,r.stderr)
        r=self.run_cli('search',self.records,'آزمون'); self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout)[0]['id'],'LE-SRC-TEST')
    def test_render(self):
        r=self.run_cli('render',self.records); self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('آزمون',r.stdout)
    def test_delivery_fails(self):
        r=self.run_cli('validate',self.records,'--delivery'); self.assertEqual(r.returncode,1)
        self.assertIn('RIGHTS_PENDING',r.stdout)
    def test_accumulate_refuses_overwrite(self):
        new=self.path/'new.json'; item=source(); item['version']='0.2.0'; new.write_text(json.dumps([item]))
        out=self.path/'accumulated.json'
        r=self.run_cli('accumulate',self.records,new,out); self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(len(json.loads(out.read_text())),2)
        before=out.read_bytes(); r=self.run_cli('accumulate',self.records,new,out)
        self.assertNotEqual(r.returncode,0); self.assertEqual(before,out.read_bytes())
    def test_export_import(self):
        out=self.path/'package.json'; store=self.path/'store.json'
        r=self.run_cli('export',self.records,out,'--package-id','test','--revision','0.1.0'); self.assertEqual(r.returncode,0,r.stderr)
        r=self.run_cli('import',out,store,'--consumer','learning-os'); self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'],'quarantined')
    def test_invalid_json_fails_cleanly(self):
        self.records.write_text('{')
        r=self.run_cli('validate',self.records); self.assertEqual(r.returncode,1)
        self.assertNotIn('Traceback',r.stderr)

    def test_review_cli_creates_new_revision(self):
        out=self.path/'reviewed.json'
        r=self.run_cli('review',self.records,'LE-SRC-TEST','0.1.0','0.2.0',out,'--reviewer','other','--reviewed-at','2026-11-25T12:00:00Z')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(out.read_text())[-1]['review']['status'],'reviewed')
