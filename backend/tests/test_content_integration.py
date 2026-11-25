"""Operational portable content admission and complete synthetic learning lifecycle."""
import copy, json, sys, unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4
from test_integration import ROOT, login, request, sql, SA, SB
sys.path.insert(0,str(ROOT))
from content.validate_package import compute_digest, load_package

class ContentIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokens={name:login(name)['access_token'] for name in ('learner-a','learner-b','reviewer-a')}
        cls.template=load_package((ROOT/'content/examples/agent-engineering-basics.fa.json').read_bytes())
        cls.owned=[]
    @classmethod
    def tearDownClass(cls):
        sql(f"UPDATE memberships SET role='learner',active=true WHERE subject='{SB}'")
        for p in cls.owned:
            # Exact UUID fixtures only; append-only audit receipts remain.
            sql(f"BEGIN; DELETE FROM completions WHERE enrollment_id IN (SELECT id FROM enrollments WHERE course_id IN (SELECT course_id FROM content_packages WHERE package_id='{p}')); DELETE FROM submissions WHERE course_id IN (SELECT course_id FROM content_packages WHERE package_id='{p}'); DELETE FROM enrollments WHERE course_id IN (SELECT course_id FROM content_packages WHERE package_id='{p}'); CREATE TEMP TABLE owned_courses ON COMMIT DROP AS SELECT course_id FROM content_packages WHERE package_id='{p}'; DELETE FROM content_packages WHERE package_id='{p}'; DELETE FROM lessons WHERE course_id IN (SELECT course_id FROM owned_courses); DELETE FROM courses WHERE id IN (SELECT course_id FROM owned_courses); COMMIT;")
    def package(self):
        p=copy.deepcopy(self.template);p['packageId']=str(uuid4()); self.owned.append(p['packageId']);p['integrity']['digest']=compute_digest(p);return p
    def call(self,path,body=None,who='reviewer-a'):
        return request(path,self.tokens[who],body)
    def imported(self,p):
        status,row=self.call('/api/content-packages',p);self.assertEqual(status,200,row);return row
    def published(self,row):
        status,result=self.call('/api/content-packages/'+row['id']+'/publish',{'expected_digest':row['digest'],'expected_revision':row['revision']});self.assertEqual(status,200,result);return result
    def test_01_admission_authority_integrity_and_draft_visibility(self):
        p=self.package()
        self.assertEqual(request('/api/content-packages',payload=p)[0],401)
        self.assertEqual(self.call('/api/content-packages',p,'learner-a')[0],403)
        broken=copy.deepcopy(p);broken['course']['title']+='tampered';self.assertEqual(self.call('/api/content-packages',broken)[0],422)
        forged=copy.deepcopy(p);forged['tenant_id']='10000000-0000-4000-8000-000000000002';forged['integrity']['digest']=compute_digest(forged);self.assertEqual(self.call('/api/content-packages',forged)[0],422)
        row=self.imported(p);self.assertEqual(row['status'],'draft')
        status,courses=self.call('/api/courses',who='learner-a');self.assertEqual(status,200)
        self.assertFalse(any(c.get('metadata',{}).get('packageId')==p['packageId'] for c in courses))
        self.assertEqual(self.call('/api/content-packages',who='learner-a')[0],403)
        self.assertEqual(self.call('/api/content-packages/'+row['id']+'/publish',{'expected_digest':row['digest'],'expected_revision':99})[0],409)
        self.assertEqual(self.call('/api/content-packages/'+row['id']+'/publish',{'expected_digest':'0'*64,'expected_revision':1})[0],409)
    def test_02_concurrent_import_publish_and_conflict(self):
        p=self.package()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(lambda _:self.call('/api/content-packages',p),range(4)))
        self.assertTrue(all(s==200 for s,r in results),results);self.assertEqual(len({r['id'] for s,r in results}),1)
        row=results[0][1];body={'expected_digest':row['digest'],'expected_revision':1}
        with ThreadPoolExecutor(max_workers=4) as pool:
            published=list(pool.map(lambda _:self.call('/api/content-packages/'+row['id']+'/publish',body),range(4)))
        self.assertTrue(all(s==200 for s,r in published),published);self.assertEqual(len({r['course_id'] for s,r in published}),1)
        self.assertEqual(sum(not r['replayed'] for s,r in published),1)
        p['course']['title']+=' changed';p['integrity']['digest']=compute_digest(p)
        self.assertEqual(self.call('/api/content-packages',p)[0],409)
    def test_03_export_new_version_and_tenant_isolation(self):
        p=self.package();first=self.published(self.imported(p));course=first['course_id']
        self.assertEqual(self.call('/api/courses/'+course+'/enroll',{},'learner-a')[0],200)
        status,exported=self.call('/api/courses/'+course+'/package',who='learner-a');self.assertEqual(status,200);self.assertEqual(exported,p)
        self.assertEqual(load_package(json.dumps(exported,ensure_ascii=False).encode()),p)
        self.assertEqual(self.call('/api/courses/'+course+'/package',who='learner-b')[0],404)
        sql(f"UPDATE memberships SET role='reviewer' WHERE subject='{SB}'")
        try:
            self.assertEqual(self.call('/api/content-packages/'+first['id']+'/publish',{'expected_digest':first['digest'],'expected_revision':1},'learner-b')[0],404)
            other=self.call('/api/content-packages',p,'learner-b');self.assertEqual(other[0],200)
            body={'expected_digest':other[1]['digest'],'expected_revision':1}
            second=self.call('/api/content-packages/'+other[1]['id']+'/publish',body,'learner-b');self.assertEqual(second[0],200);self.assertNotEqual(second[1]['course_id'],course)
        finally:sql(f"UPDATE memberships SET role='learner' WHERE subject='{SB}'")
        p['version']='1.0.1';p['integrity']['digest']=compute_digest(p);new=self.published(self.imported(p));self.assertNotEqual(new['course_id'],course)
        courses=self.call('/api/courses',who='learner-a')[1];old=next(c for c in courses if c['id']==course);self.assertTrue(old['enrolled'])
    def test_04_full_learning_revision_and_human_acceptance(self):
        p=self.package();published=self.published(self.imported(p));cid=published['course_id']
        self.assertEqual(self.call('/api/courses/'+cid+'/enroll',{},'learner-a')[0],200)
        c=next(c for c in self.call('/api/courses',who='learner-a')[1] if c['id']==cid)
        self.assertEqual(c['metadata']['assessment'],p['course']['assessment'])
        for lesson in c['lessons']:self.assertEqual(self.call(f"/api/courses/{cid}/lessons/{lesson['id']}/complete",{},'learner-a')[0],200)
        self.assertEqual(self.call('/api/courses/'+cid+'/submissions',{'content':'x'*20},'learner-a')[0],422)
        evidence='مشاهده و هدف قابل سنجش، قرارداد ورودی و خروجی، مرز اختیار، آزمون منفی و شواهد اجرای قابل تکرار. '*5
        status,s=self.call('/api/courses/'+cid+'/submissions',{'content':evidence},'learner-a');self.assertEqual(status,200,s)
        status,r=self.call('/api/submissions/'+s['id']+'/review',{'decision':'revision_requested','feedback':'فرضیات را از مشاهده‌ها جدا کن.','expected_revision':1});self.assertEqual(status,200,r)
        status,s2=self.call('/api/courses/'+cid+'/submissions',{'content':evidence+' اصلاحیه: فرضیات صریح و محدودیت‌ها ثبت شدند.'},'learner-a');self.assertEqual(status,200,s2);self.assertNotEqual(s2['id'],s['id'])
        status,r=self.call('/api/submissions/'+s2['id']+'/review',{'decision':'accepted','feedback':'شواهد بازبینی شد؛ پذیرش آزمایشی انسانی، بدون ادعای گواهی مهارت.','expected_revision':1});self.assertEqual(status,200,r);self.assertEqual(r['status'],'accepted')
        records=self.call('/api/submissions',who='learner-a')[1];self.assertEqual(next(x for x in records if x['id']==s['id'])['status'],'revision_requested')
        self.assertEqual(next(x for x in records if x['id']==s2['id'])['status'],'accepted')
        status,tool=self.call('/api/tools/invoke',{'name':'learning.progress','arguments':{}},'learner-a')
        self.assertEqual(status,200,tool);self.assertEqual(tool['version'],'2')
        self.assertGreaterEqual(tool['result']['completed_lessons'],3)
        self.assertLess(len(json.dumps(tool).encode()),2048)

if __name__=='__main__':unittest.main()
