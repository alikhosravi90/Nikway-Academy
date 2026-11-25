import copy
import pytest
import psycopg
from pydantic import ValidationError
from cf.contracts import ComponentInput
from cf.store import DomainError

def test_contract_rejects_unknown_fields_and_invalid_answer(content):
    with pytest.raises(ValidationError): ComponentInput(**content, tenant_id='forged')
    content['body']['questions'][0]['answer'] = 10
    with pytest.raises(ValidationError): ComponentInput(**content)

def test_revision_pins_body_and_rejects_stale(repo, identities, content):
    ctx,_=identities
    a=repo.create_revision(ctx['author'], ComponentInput(**content), 0)
    content['semanticVersion']='1.0.1'; content['body']['summary']='اصلاح محتوای آزمایشی'
    b=repo.create_revision(ctx['author'],ComponentInput(**content),1)
    assert a['revisionId'] != b['revisionId']
    assert repo.get_revision(ctx['author'],a['revisionId'])['body']['summary'] != content['body']['summary']
    with pytest.raises(DomainError,match='stale'): repo.create_revision(ctx['author'],ComponentInput(**content),1)

def test_review_requires_independent_reviewer_and_rights(repo,identities,content):
    ctx,_=identities
    content['license']='UNKNOWN'
    r=repo.create_revision(ctx['author'],ComponentInput(**content),0)
    with pytest.raises(DomainError): repo.review(ctx['author'],r['revisionId'],'checked')
    with pytest.raises(DomainError,match='rights'): repo.review(ctx['reviewer'],r['revisionId'],'checked')

def test_tenant_rls_and_search(repo,identities,content):
    ctx,_=identities
    r=repo.create_revision(ctx['author'],ComponentInput(**content),0)
    with pytest.raises(DomainError,match='not found'): repo.get_revision(ctx['other'],r['revisionId'])
    assert repo.search(ctx['other'],'PDCA') == []
    with repo.db.transaction(ctx['other']) as c:
        assert c.execute('SELECT count(*) AS n FROM revisions').fetchone()['n']==0
    assert len(repo.search(ctx['author'],'PDCA')) == 1

def test_immutable_database_and_object_tamper(repo,identities,content):
    ctx,_=identities
    r=repo.create_revision(ctx['author'],ComponentInput(**content),0)
    with pytest.raises(psycopg.Error):
        with repo.db.transaction(ctx['author']) as c:
            c.execute('UPDATE revisions SET digest=%s WHERE revision_id=%s',('0'*64,r['revisionId']))
    path=repo.object_path(ctx['author'].tenant,r['checksum'])
    path.write_bytes(b'tampered')
    with pytest.raises(DomainError,match='integrity'): repo.get_revision(ctx['author'],r['revisionId'])

def test_revoked_and_expired_credentials(db,identities):
    _,tokens=identities
    db.revoke(tokens['author'])
    with pytest.raises(DomainError): db.authenticate(tokens['author'])
    expired=db.provision('expired-tenant','author',seconds=-1)
    with pytest.raises(DomainError): db.authenticate(expired)

def test_broken_lineage_and_missing_source_rejected(repo,identities,content):
    ctx,_=identities
    content['derivedFrom']=['missing']
    with pytest.raises(DomainError): repo.create_revision(ctx['author'],ComponentInput(**content),0)
    content['derivedFrom']=[]; content['sourceEvidenceIds']=['missing']
    with pytest.raises(ValidationError): ComponentInput(**content)
