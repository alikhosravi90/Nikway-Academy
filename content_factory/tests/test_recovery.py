from pathlib import Path
from uuid import uuid4
import os
import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict,make_conninfo
import pytest
from cf.contracts import ComponentInput
from cf.recovery import backup,restore,integrity_report
from cf.db import Database
from cf.store import Repository,DomainError

@pytest.fixture
def restore_target():
    name='cf_restore_'+uuid4().hex
    admin=conninfo_to_dict(os.environ['CF_ADMIN_URL']); app=conninfo_to_dict(os.environ['CF_DATABASE_URL'])
    with psycopg.connect(os.environ['CF_ADMIN_URL'],autocommit=True) as c:
        c.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
    admin['dbname']=name; app['dbname']=name
    yield Database(make_conninfo(**app),make_conninfo(**admin))
    with psycopg.connect(os.environ['CF_ADMIN_URL'],autocommit=True) as c:
        c.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(name)))

def test_restore_rehydrates_matching_metadata_objects_and_search(repo,identities,content,tmp_path,restore_target):
    ctx,_=identities
    r=repo.create_revision(ctx['author'],ComponentInput(**content),0)
    repo.review(ctx['reviewer'],r['revisionId'],'synthetic review')
    m=repo.prepare(ctx['reviewer'],'course',[r['revisionId']],'backup')
    snap=tmp_path/'snapshot'; backup(repo,ctx['reviewer'],snap)
    restored=Repository(restore_target,tmp_path/'restored-objects')
    restore(restored,snap)
    assert restored.candidate(ctx['consumer'],m['id'])==m
    assert restored.get_revision(ctx['author'],r['revisionId'])['checksum']==r['checksum']
    assert restored.search(ctx['author'],'PDCA')[0]['revision_id']==r['revisionId']
    assert integrity_report(restored,ctx['reviewer'])['missing_or_corrupt']==[]
    with pytest.raises(DomainError): restore(restored,snap)

def test_backup_rejects_missing_object_and_reports_orphan(repo,identities,content,tmp_path):
    ctx,_=identities
    r=repo.create_revision(ctx['author'],ComponentInput(**content),0)
    digest=repo.put_object(ctx['author'].tenant,b'orphan after interrupted write')
    report=integrity_report(repo,ctx['reviewer'])
    assert digest in report['unreferenced_objects']
    repo.object_path(ctx['author'].tenant,r['checksum']).unlink()
    with pytest.raises(DomainError): backup(repo,ctx['reviewer'],tmp_path/'backup')
