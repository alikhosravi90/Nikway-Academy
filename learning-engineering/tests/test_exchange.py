import json
from pathlib import Path
import tempfile
import unittest
try:
    from engine.exchange import build_package, receive_package
except ImportError:
    build_package = receive_package = None

def source():
    return {'id':'LE-SRC-TEST','version':'0.1.0','kind':'Source',
        'title':{'fa':'آزمون','en':'Test'},'summary':{'fa':'نمونه','en':'Synthetic'},
        'domainIds':['LE-IMP'],'relations':[],
        'provenance':{'claimType':'synthetic','evidenceRefs':[]},
        'review':{'status':'proposed','author':'test','reviewer':None,'reviewedAt':None},
        'rights':{'status':'pending verification','license':'UNKNOWN','evidenceUrls':[],'allowedUses':[]},
        'data':{'canonicalUrl':'https://example.org/source','issuer':'Synthetic','edition':'test','verificationStatus':'pending verification'}}

class ExchangeTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(callable(build_package), 'exchange implementation missing')
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.store = Path(self.tmp.name)/'receipt.json'
        self.context = {'producer':'learning-engineering','consumer':'content-factory','scope':'local-fixture'}
        self.package = build_package([source()], 'pdca-fixture', '0.1.0')
    def test_round_trip_quarantines_pending_preserves_fa(self):
        result = receive_package(self.package,self.store,self.context)
        self.assertEqual(result['status'],'quarantined')
        self.assertEqual(json.loads(self.store.read_text())['packages'][0]['package']['objects'][0]['title']['fa'],'آزمون')
    def test_idempotent_replay(self):
        first=receive_package(self.package,self.store,self.context); before=self.store.read_bytes()
        self.assertEqual(receive_package(self.package,self.store,self.context),first)
        self.assertEqual(before,self.store.read_bytes())
    def test_tampering_rejected_without_write(self):
        self.package['objects'][0]['title']['en']='Tamper'
        with self.assertRaisesRegex(ValueError,'DIGEST_MISMATCH'): receive_package(self.package,self.store,self.context)
        self.assertFalse(self.store.exists())
    def test_conflicting_revision_rejected(self):
        receive_package(self.package,self.store,self.context); before=self.store.read_bytes()
        changed=source(); changed['title']['en']='Changed'
        with self.assertRaisesRegex(ValueError,'REVISION_CONFLICT'): receive_package(build_package([changed],'pdca-fixture','0.1.0'),self.store,self.context)
        self.assertEqual(before,self.store.read_bytes())
    def test_unsupported_version(self):
        self.package['contractVersion']='9.0.0'
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_VERSION'): receive_package(self.package,self.store,self.context)
    def test_wrong_context_rejected(self):
        with self.assertRaisesRegex(ValueError,'ACCESS_DENIED'): receive_package(self.package,self.store,dict(self.context,scope='production'))
        self.assertFalse(self.store.exists())
    def test_dependency_manifest_mismatch(self):
        self.package['dependencyManifest']=[]
        with self.assertRaises(ValueError): receive_package(self.package,self.store,self.context)
    def test_unknown_payload_fields_rejected(self):
        self.package['tenantId']='arbitrary'
        with self.assertRaises(ValueError): receive_package(self.package,self.store,self.context)
    def test_empty_package_rejected(self):
        with self.assertRaises(ValueError): build_package([], 'empty','0.1.0')
    def test_historical_package_preserved_on_new_revision(self):
        receive_package(self.package,self.store,self.context)
        changed=source(); changed['version']='0.2.0'
        receive_package(build_package([changed],'pdca-fixture','0.2.0'),self.store,self.context)
        entries=json.loads(self.store.read_text())['packages']
        self.assertEqual([e['package']['packageRevision'] for e in entries],['0.1.0','0.2.0'])
        self.assertEqual(entries[0]['package'],self.package)
    def test_forged_stored_receipt_not_trusted(self):
        receive_package(self.package,self.store,self.context)
        state=json.loads(self.store.read_text()); state['packages'][0]['receipt']['status']='accepted'
        self.store.write_text(json.dumps(state))
        with self.assertRaisesRegex(ValueError,'CORRUPT_STORE'):
            receive_package(self.package,self.store,self.context)
    def test_record_revision_conflict_across_packages(self):
        receive_package(self.package,self.store,self.context)
        changed=source(); changed['title']['en']='Different same record revision'
        other=build_package([changed],'other-package','0.1.0')
        with self.assertRaisesRegex(ValueError,'RECORD_REVISION_CONFLICT'):
            receive_package(other,self.store,self.context)
    def test_package_schema_includes_record_shape(self):
        from engine.exchange import package_validator
        invalid=dict(self.package,objects=[{}])
        self.assertTrue(list(package_validator().iter_errors(invalid)))
    def test_export_unknown_domain_rejected(self):
        record=source(); record['domainIds']=['LE-NOTREGISTERED']
        with self.assertRaisesRegex(ValueError,'INVALID_RECORDS'): build_package([record],'unknown','0.1.0')
if __name__ == '__main__': unittest.main()
