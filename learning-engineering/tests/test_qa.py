"""Independent adversarial QA. Local fixtures do not establish authorization."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from engine.knowledge import validate_records, accumulate
from engine.exchange import build_package, receive_package
from test_knowledge import source

def ref(r): return {'id':r['id'],'version':r['version']}
def graph():
    s=source(); e=copy.deepcopy(s)
    e.update(id='LE-EVD',kind='Evidence',data={'sourceRef':ref(s),'locator':'fixture','claim':s['summary'],'limitations':'Synthetic'})
    rows=[s,e]
    def add(kind,id,data):
        r=copy.deepcopy(s); r.update(kind=kind,id=id,data=data); r['provenance']['evidenceRefs']=[ref(e)]; rows.append(r); return r
    c=add('Concept','LE-CON',{'definition':s['summary'],'aliases':[]})
    co=add('Competency','LE-COMP',{'conceptRefs':[ref(c)],'performance':s['summary']})
    a=add('LearningObjective','LE-OBJ-A',{'competencyRefs':[ref(co)],'criterion':s['summary']})
    b=add('LearningObjective','LE-OBJ-B',{'competencyRefs':[ref(co)],'criterion':s['summary']})
    rub=add('Rubric','LE-RUB',{'objectiveRefs':[ref(a)],'criteria':[{'id':'one','description':s['summary'],'maxScore':2}]})
    add('Assessment','LE-ASSESS',{'objectiveRefs':[ref(a)],'rubricRef':ref(rub),'task':s['summary']})
    return rows

class IndependentQA(unittest.TestCase):
    def test_complete_fixture(self): self.assertEqual(validate_records(graph()),[])
    def test_malformed_nested(self):
        for value in [None,[],42,{},'bad']:
            with self.subTest(value=value):
                r=graph(); r[-1]['data']['rubricRef']=value; self.assertTrue(validate_records(r))
    def test_bilingual_required(self):
        r=graph(); del r[-1]['data']['task']['fa']; self.assertTrue(validate_records(r))
    def test_supersession_cycle(self):
        a=source(); b=copy.deepcopy(a); b['version']='0.2.0'
        a['relations']=[{'type':'supersedes','target':ref(b)}]; b['relations']=[{'type':'supersedes','target':ref(a)}]
        self.assertTrue(validate_records([a,b]))
    def test_rubric_alignment(self):
        r=graph(); r[-2]['data']['objectiveRefs']=[ref(r[-3])]; self.assertTrue(validate_records(r))
    def test_explicit_relation_alignment(self):
        r=graph(); r[-1]['relations']=[{'type':'assesses','target':ref(r[-3])}]; self.assertTrue(validate_records(r))
    def test_nonfinite_score(self):
        for value in [float('nan'),float('inf')]:
            with self.subTest(value=value):
                r=graph(); r[-2]['data']['criteria'][0]['maxScore']=value; self.assertTrue(validate_records(r))
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.store=Path(self.tmp.name)/'store.json'
        self.context={'producer':'learning-engineering','consumer':'content-factory','scope':'local-fixture'}
        self.package=build_package([source()],'qa-package','0.1.0')
    def test_forged_receipt(self):
        receive_package(self.package,self.store,self.context)
        state=json.loads(self.store.read_text()); state['packages'][0]['receipt']['status']='accepted'; self.store.write_text(json.dumps(state))
        try: receipt=receive_package(self.package,self.store,self.context)
        except ValueError: return
        self.assertEqual(receipt['status'],'quarantined')
    def test_cross_package_record_conflict(self):
        receive_package(self.package,self.store,self.context); before=self.store.read_bytes()
        r=source(); r['summary']['en']='Changed same immutable revision'
        with self.assertRaises(ValueError): receive_package(build_package([r],'different-package','0.1.0'),self.store,self.context)
        self.assertEqual(before,self.store.read_bytes())
    def test_malformed_store_fails_cleanly(self):
        for entry in [None,{}, {'package':None}, {'package':self.package}]:
            with self.subTest(entry=entry):
                self.store.write_text(json.dumps({'packages':[entry]})); before=self.store.read_bytes()
                with self.assertRaises(ValueError): receive_package(self.package,self.store,self.context)
                self.assertEqual(before,self.store.read_bytes())
    def test_claimed_approval_stays_quarantined(self):
        r=source(); r['review'].update(status='approved',reviewer='untrusted-claim',reviewedAt='2026-11-25T00:00:00Z')
        r['rights'].update(status='verified',license='fixture',evidenceUrls=['https://example.invalid/claim'],allowedUses=['fixture'])
        r['data'].update(verificationStatus='verified',canonicalUrl='https://example.invalid/source',issuer='Synthetic',edition='fixture')
        receipt=receive_package(build_package([r],'approved','0.1.0'),self.store,self.context)
        self.assertEqual(receipt['status'],'quarantined')
        self.assertIn('OWNER_ACCEPTANCE_AND_TRUSTED_ADAPTER_REQUIRED',receipt['reasons'])
