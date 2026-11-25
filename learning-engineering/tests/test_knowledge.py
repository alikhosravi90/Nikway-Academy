import copy
import unittest
from pathlib import Path
from engine.knowledge import validate_records, accumulate, search, render_markdown, load_records

def source():
    return dict(id='LE-SOURCE-TEST',version='0.1.0',kind='Source',title={'fa':'يادگيري','en':'Learning'},summary={'fa':'خلاصه','en':'Summary'},domainIds=['LE-IMP'],relations=[],provenance={'claimType':'synthetic','evidenceRefs':[]},review={'status':'proposed','author':'fixture','reviewer':None,'reviewedAt':None},rights={'status':'pending verification','license':'UNKNOWN','evidenceUrls':[],'allowedUses':[]},data={'canonicalUrl':'UNKNOWN','issuer':'UNKNOWN','edition':'UNKNOWN','verificationStatus':'pending verification'})

class KnowledgeTests(unittest.TestCase):
    def test_accumulate_malformed_is_value_error(self):
        with self.assertRaises(ValueError): accumulate([source()],[{}])
    def test_empty_batch_invalid(self):
        self.assertTrue(validate_records([]))
    def test_supersedes_only_older_same_id(self):
        a=source(); b=source(); b['version']='0.2.0'
        a['relations']=[{'type':'supersedes','target':{'id':b['id'],'version':b['version']}}]
        self.assertTrue(validate_records([a,b]))
        b['relations']=a['relations']; a['relations']=[]
        self.assertTrue(validate_records([a,b]))
        b['relations']=[{'type':'supersedes','target':{'id':a['id'],'version':a['version']}}]
        self.assertEqual(validate_records([a,b]),[])
        a['id']='LE-DIFFERENT'; b['relations'][0]['target']['id']=a['id']
        self.assertTrue(validate_records([a,b]))
    def test_rubric_and_relation_alignment(self):
        records=load_records(Path(__file__).resolve().parents[1]/'records')
        by_kind={r['kind']:r for r in records}
        alternative=copy.deepcopy(by_kind['LearningObjective']); alternative['id']='LE-OBJ-ALTERNATIVE'
        records.append(alternative)
        rubric=by_kind['Rubric']; rubric['data']['objectiveRefs']=[{'id':alternative['id'],'version':alternative['version']}]
        rubric['relations']=[]
        self.assertTrue(any('RUBRIC_OBJECTIVE_MISMATCH' in e for e in validate_records(records)))
        rubric['data']['objectiveRefs']=copy.deepcopy(by_kind['Assessment']['data']['objectiveRefs'])
        by_kind['Assessment']['relations'].append({'type':'assesses','target':{'id':alternative['id'],'version':alternative['version']}})
        self.assertTrue(any('RELATION_DATA_MISMATCH' in e for e in validate_records(records)))
    def test_nonfinite_rejected(self):
        records=load_records(Path(__file__).resolve().parents[1]/'records')
        rubric=next(r for r in records if r['kind']=='Rubric')
        for value in (float('nan'),float('inf')):
            rubric['data']['criteria'][0]['maxScore']=value
            self.assertTrue(any('NONFINITE' in e for e in validate_records(records)))
    def test_draft_valid(self): self.assertEqual(validate_records([source()]), [])
    def test_wrong_relation_type(self):
        r=source(); r['relations']=[{'type':'explains','target':{'id':r['id'],'version':r['version']}}]
        self.assertTrue(validate_records([r]))
    def test_cycle(self):
        a=source(); b=source(); b['id']='LE-OTHER'
        for r,t in [(a,b),(b,a)]:
            r['kind']='Concept'; r['data']={'definition':r['summary'],'aliases':[]}
            r['relations']=[{'type':'prerequisiteOf','target':{'id':t['id'],'version':t['version']}}]
        self.assertTrue(any('PREREQUISITE_CYCLE' in e for e in validate_records([a,b])))
    def test_approved_source_needs_actual_locator(self):
        r=source(); r['review'].update(status='approved',reviewer='synthetic-reviewer',reviewedAt='2026-11-25T00:00:00Z')
        r['rights'].update(status='verified',license='synthetic-only',evidenceUrls=['https://example.invalid/fixture'],allowedUses=['fixture'])
        r['data']['verificationStatus']='verified'
        self.assertTrue(validate_records([r]))
    def test_nested_unknown_field(self):
        r=source(); r['data']['unexpected']='x'; self.assertTrue(validate_records([r]))
    def test_unknown_field(self):
        r=source(); r['surprise']=True
        self.assertTrue(validate_records([r]))
    def test_duplicate(self): self.assertTrue(validate_records([source(),source()]))
    def test_delivery_gate(self): self.assertTrue(validate_records([source()], delivery=True))
    def test_missing_reference(self):
        r=source(); r['relations']=[{'type':'cites','target':{'id':'LE-MISSING','version':'0.1.0'}}]
        self.assertTrue(validate_records([r]))
    def test_immutable_accumulation(self):
        r=source(); changed=copy.deepcopy(r); changed['title']['en']='Changed'
        with self.assertRaises(ValueError): accumulate([r],[changed])
        self.assertEqual(accumulate([r],[r]),[r])
    def test_persian_search(self): self.assertEqual(search([source()],'یادگیری'),[source()])
    def test_render(self): self.assertIn('LE-SOURCE-TEST',render_markdown([source()]))
    def test_reviewer_separation(self):
        r=source(); r['review'].update(status='reviewed',reviewer='fixture',reviewedAt='2026-11-25T00:00:00Z')
        self.assertTrue(validate_records([r]))

if __name__=='__main__': unittest.main()
