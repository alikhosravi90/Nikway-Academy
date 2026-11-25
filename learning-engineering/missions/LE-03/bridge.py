"""Bounded original draft bridge. Format acceptance never grants rights or publication."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from uuid import NAMESPACE_URL, uuid5

ROOT=Path(__file__).resolve().parent
for path in ('le/learning-engineering','cf/content_factory','academy'):
    sys.path.insert(0,str(ROOT/'.snapshots'/path))
from engine import exchange
from cf.contracts import ComponentInput
from cf.render import build_package, zip_package
from content import validate_package as academy

BLOCKERS=['LE_RIGHTS_PENDING','HUMAN_CONTENT_REVIEW_REQUIRED','ACCESSIBILITY_UNTESTED',
          'AUTHENTICATED_ADMISSION_AND_DATABASE_DELIVERY_NOT_TESTED','SEMANTIC_MAPPING_NOT_OWNER_ACCEPTED']

def source_package():
    records=[json.loads(p.read_text()) for p in sorted((ROOT/'.snapshots/le/learning-engineering/records').glob('*.json'))]
    return exchange.build_package(records,'le03-pdca-draft','0.1.0')

def to_component(package):
    exchange._validate(package)
    if package['payloadDigest'] != '02cfa7b471a2e84df8c63ae52955561a37d819dc2e976d7f86090a5c79a8fba0':
        raise ValueError('UNSUPPORTED_SOURCE_DIGEST: only the exact pinned PDCA source is mapped')
    records={r['id']:r for r in package['objects']}
    for expected in ('LE-OBJ-PDCA','LE-COMP-PDCA','LE-ASSESS-PDCA','LE-RUBRIC-PDCA','LE-CONTENT-PDCA'):
        if expected not in records: raise ValueError('UNSUPPORTED_RECORD_MAPPING: '+expected)
    # Authored here as an original synthetic example; never passed off as LE-approved content.
    body={'summary':'Original synthetic draft: use a small reversible change to investigate incomplete handovers. No learning effectiveness or causal conclusion is established.',
          'sections':[{'title':'A bounded improvement cycle','text':'Plan: define incomplete handovers and aim for at most 6%. Do: trial a checklist for one fictional week, identify a fictional owner, a rollback and a stopping condition. Check: 12 incomplete handovers out of 100 is 12%; 5 out of 100 is 5%; the reduction is 7 percentage points. Act: consider continuing, revising or stopping, and collect comparable next-cycle data. Workload or staffing differences could explain the change; this comparison cannot establish causality.'}],
          'exercise':'Write a proposed plan, reversible trial, calculation and next decision for this fictional example in at most 500 words. Explain one alternative explanation and what data you would collect next.',
          'rubric':{'id':'LE-RUBRIC-PDCA','criteria':['State the problem and a measurable aim.','Specify a reversible trial with an owner and stopping rule.','Calculate 12%, 5% and 7 percentage points and describe uncertainty.','Justify a next action and specify next-cycle evidence.']},
          'questions':[{'id':'le03-rate','prompt':'What is the absolute reduction from 12% to 5%?','options':['7 percentage points','7 percent relative reduction'],'answer':0,'explanation':'Subtract 5 from 12 to obtain 7 percentage points.','outcomeId':'LE-OBJ-PDCA'}]}
    component={'schemaVersion':'1.0.0','id':'le03-pdca-original-draft','semanticVersion':'0.1.0','locale':'en-US','type':'lesson','title':'Synthetic PDCA handover exercise — unreviewed draft',
      'learningOutcomeIds':['LE-OBJ-PDCA'],'competencyIds':['LE-COMP-PDCA'],'prerequisiteIds':[],
      'sourceEvidenceIds':['LE03-ORIGINAL-DRAFT'],'license':'LicenseRef-NIKWAY-Local-Review','rightsStatus':'internal_trial_only',
      'accessibility':{'textAlternative':False,'readingOrder':False,'languageDeclared':True},
      'provenance':[{'id':'LE03-ORIGINAL-DRAFT','locator':'urn:nikway:le03:original-draft','rights':'original_synthetic','note':'New synthetic text authored for offline module tests. LE source rights remain pending; no distribution authorization.'}],
      'audience':'Fictional adult learner; offline integration only','durationMinutes':20,
      'derivedFrom':[package['payloadDigest']],'body':body}
    return ComponentInput.model_validate(component).model_dump()

def to_academy(component, parts):
    # Consume CF's actual rendered learner text; retain explicit outcome mapping.
    ComponentInput.model_validate(component)
    manifest=json.loads(parts['manifest.json'])
    if set(manifest.get('files',{})) != {'text.md','lesson.html','quiz.json'} or any(hashlib.sha256(parts[name]).hexdigest()!=digest for name,digest in manifest['files'].items()):
        raise ValueError('CF_RENDITION_DIGEST_MISMATCH')
    uid=lambda name:str(uuid5(NAMESPACE_URL,'nikway:LE03:offline-draft:'+name))
    oid=component['learningOutcomeIds'][0].lower()
    rubric_id='le-rubric-pdca'
    package={'schemaVersion':'1.0.0','packageId':uid('package'),'version':'0.1.0','lifecycle':'draft',
      'course':{'id':uid('course'),'title':component['title'],'description':component['body']['summary'],'language':component['locale'],
        'objectives':[{'id':oid,'description':'Apply a bounded improvement cycle to the synthetic handover scenario.','bloom':'apply','evidence':'A proposed written response assessed by a human; no response collected.'}],
        'lessons':[{'id':uid('lesson'),'position':1,'title':component['title'],'content':parts['text.md'].decode(),'objectiveIds':[oid],
                    'practice':{'prompt':component['body']['exercise'],'deliverable':'A synthetic exercise response of at most 500 words.'}}],
        'assessment':{'mode':'human_review','prompt':component['body']['exercise'],'minCharacters':20,'maxCharacters':10000,'rubricId':rubric_id},
        'rubric':{'id':rubric_id,'version':'0.1.0','criteria':[{'id':name,'description':desc,'objectiveIds':[oid],'maxScore':2,'anchors':[{'score':0,'description':'Absent or incorrect.'},{'score':1,'description':'Partially addressed.'},{'score':2,'description':'Fully addressed.'}]} for name,desc in zip(('plan','do','check','act'),component['body']['rubric']['criteria'])], 'passScore':8,'requiresHumanReview':True}},
      'provenance':{'producer':'offline-authoring','createdAt':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'author':'LE-03 synthetic adapter; unreviewed','sources':[]},
      'rights':{'license':'LicenseRef-NIKWAY-Local-Review','attribution':'Original LE-03 synthetic text; local format testing only. Upstream LE rights pending; no publication approval.','redistribution':'local-review-only','containsThirdPartyMaterial':False},
      'integrity':{'algorithm':'sha256','canonicalization':'nikway-json-v1','digest':''}}
    package['integrity']['digest']=academy.compute_digest(package)
    return academy.load_package(json.dumps(package,ensure_ascii=False).encode())

def run():
    source=source_package(); component=to_component(source)
    render_input=dict(component,revisionId='LE03-offline-original-draft')
    parts=build_package({'id':'le03-offline-candidate','status':'candidate_local','schemaVersion':'1.0.0'},[render_input])
    package=to_academy(component,parts)
    return {'scope':'offline-real-module-draft','promotionAllowed':False,'blockers':BLOCKERS,
      'moduleChecks':['learning-engineering.exchange','content-factory.contracts+render','academy.content.validate_package'],
      'sourcePayloadDigest':source['payloadDigest'],'sourceManifest':source['dependencyManifest'],'sourceRights':{r['id']:r['rights'] for r in source['objects']},
      'component':component,'academy':package,'learnerQuiz':json.loads(parts['quiz.json']),
      'cfZipSha256':hashlib.sha256(zip_package(parts)).hexdigest(),
      'mappingNotes':['LE objective exact ID -> CF learningOutcomeIds -> Academy lowercase objective ID.',
        'Academy has no competency or source-version fields; the integration receipt retains CF and source manifest provenance.',
        'Academy character bounds do not implement LE 500-word bound; human review remains required.',
        'CF multiple-choice self-check is newly authored formative material, not a replacement for the human rubric.',
        'Accessibility booleans are conservative draft declarations, not accessibility results.']}

if __name__=='__main__':
    receipt=run()
    (ROOT/'evidence/integration-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('PASS: offline real-module draft path. BLOCKED: promotion / authenticated delivery.')
