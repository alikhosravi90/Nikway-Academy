import io
import json
import zipfile
import pytest
from cf.contracts import ComponentInput
from cf.pipeline import Pipeline
from cf.render import build_package, score
from cf.store import DomainError

def approved(repo,ctx,content):
    r=repo.create_revision(ctx['author'],ComponentInput(**content),0)
    return repo.review(ctx['reviewer'],r['revisionId'],'Synthetic automated fixture review; human gate pending')

def test_pdca_enforces_order_and_requires_review(repo,identities,content):
    ctx,_=identities; p=Pipeline(repo)
    run=p.plan(ctx['author'],ComponentInput(**content),'produce accessible lesson and quiz')
    with pytest.raises(DomainError): p.act(ctx['reviewer'],run['id'],'course-one','key')
    done=p.do(ctx['author'],run['id'])
    check=p.check(ctx['author'],run['id'])
    assert check['state']=='checked' and check['checks']['passed']
    with pytest.raises(DomainError): p.act(ctx['reviewer'],run['id'],'course-one','key')
    repo.review(ctx['reviewer'],done['revisionId'],'synthetic review')
    candidate=p.act(ctx['reviewer'],run['id'],'course-one','key')
    assert candidate['status']=='candidate_local'
    with pytest.raises(DomainError): p.do(ctx['author'],run['id'])

def test_two_course_reuse_pins_revisions_and_withdrawal(repo,identities,content):
    ctx,_=identities; r=approved(repo,ctx,content)
    a=repo.prepare(ctx['reviewer'],'course-one',[r['revisionId']],'a')
    b=repo.prepare(ctx['reviewer'],'course-two',[r['revisionId']],'b')
    assert a['components']==b['components']
    content['semanticVersion']='1.0.1'
    content['body']['summary']='متن اصلاح‌شده برای نسخه بعدی'
    newer=repo.create_revision(ctx['author'],ComponentInput(**content),1)
    assert repo.candidate(ctx['consumer'],a['id'])['components'][0]['revisionId']==r['revisionId']
    assert newer['revisionId']!=r['revisionId']
    affected=repo.withdraw(ctx['reviewer'],r['revisionId'],'synthetic withdrawal drill')
    assert {x['candidate_id'] for x in affected}=={a['id'],b['id']}
    with pytest.raises(DomainError): repo.candidate(ctx['consumer'],a['id'])

def test_prepare_idempotency_draft_and_cross_tenant(repo,identities,content):
    ctx,_=identities
    r=repo.create_revision(ctx['author'],ComponentInput(**content),0)
    with pytest.raises(DomainError): repo.prepare(ctx['reviewer'],'c',[r['revisionId']],'a')
    repo.review(ctx['reviewer'],r['revisionId'],'checked')
    a=repo.prepare(ctx['reviewer'],'c',[r['revisionId']],'a')
    assert repo.prepare(ctx['reviewer'],'c',[r['revisionId']],'a')==a
    with pytest.raises(DomainError): repo.prepare(ctx['reviewer'],'different',[r['revisionId']],'a')
    with pytest.raises(DomainError): repo.candidate(ctx['other'],a['id'])

def test_package_has_four_outputs_safe_html_and_scoring(repo,identities,content):
    ctx,_=identities; content['body']['summary']='<script>alert(1)</script>'
    r=approved(repo,ctx,content)
    m=repo.prepare(ctx['reviewer'],'course',[r['revisionId']],'a')
    parts=build_package(m,[r],instructor=False)
    assert {'text.md','lesson.html','quiz.json','manifest.json'}<=set(parts)
    assert '<script>' not in parts['lesson.html'].decode()
    assert '&lt;script&gt;' in parts['lesson.html'].decode()
    assert 'dir="rtl"' in parts['lesson.html'].decode()
    quiz=json.loads(parts['quiz.json'])
    assert 'answer' not in quiz[0]['questions'][0]
    assert score(r,{'q1':2,'q2':1})=={'correct':2,'total':2}
    assert score(r,{'q1':0,'q2':0})=={'correct':0,'total':2}
    with pytest.raises(DomainError): score(r,{'unknown':1})

def test_pipeline_unknown_rights_fails_check(repo,identities,content):
    ctx,_=identities; content['rightsStatus']='unknown'
    p=Pipeline(repo); run=p.plan(ctx['author'],ComponentInput(**content),'test')
    p.do(ctx['author'],run['id'])
    result=p.check(ctx['author'],run['id'])
    assert not result['checks']['passed']
    with pytest.raises(DomainError): p.act(ctx['reviewer'],run['id'],'course','key')

def test_transitive_dependency_withdrawal_blocks_candidate(repo,identities,content):
    ctx,_=identities; parent=approved(repo,ctx,content)
    content['id']='pdca-adaptation'; content['derivedFrom']=[parent['revisionId']]
    child=approved(repo,ctx,content)
    m=repo.prepare(ctx['reviewer'],'course',[child['revisionId']],'key')
    repo.withdraw(ctx['reviewer'],parent['revisionId'],'source revoked')
    with pytest.raises(DomainError): repo.candidate(ctx['consumer'],m['id'])
