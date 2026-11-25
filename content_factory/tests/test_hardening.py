import copy
from concurrent.futures import ThreadPoolExecutor
import io
import json
import zipfile
import pytest
from cf.contracts import ComponentInput
from cf.pipeline import Pipeline
from cf.consumer import LocalConsumer
from cf.render import zip_package
from cf.store import DomainError,canonical,sha

def test_concurrent_revision_writers_only_one_wins(repo,identities,content):
    ctx,_=identities
    repo.create_revision(ctx['author'],ComponentInput(**content),0)
    content['semanticVersion']='1.0.1'
    def write():
        try: return repo.create_revision(ctx['author'],ComponentInput(**content),1)['revisionNumber']
        except DomainError: return 'conflict'
    with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(lambda _:write(),range(2)))
    assert sorted(map(str,results))==['2','conflict']

def test_pipeline_failure_rolls_back_revision(repo,identities,content,monkeypatch):
    ctx,_=identities; pipeline=Pipeline(repo)
    run=pipeline.plan(ctx['author'],ComponentInput(**content),'failure injection')
    original=pipeline._save
    def fail(*args): raise RuntimeError('storage failed')
    monkeypatch.setattr(pipeline,'_save',fail)
    with pytest.raises(RuntimeError): pipeline.do(ctx['author'],run['id'])
    assert repo.search(ctx['author'],'PDCA')==[]
    monkeypatch.setattr(pipeline,'_save',original)
    assert pipeline.do(ctx['author'],run['id'])['state']=='produced'

def test_consumer_rejects_package_rehashed_by_attacker(repo,identities,content):
    ctx,_=identities
    r=repo.create_revision(ctx['author'],ComponentInput(**content),0)
    repo.review(ctx['reviewer'],r['revisionId'],'review')
    m=repo.prepare(ctx['reviewer'],'course',[r['revisionId']],'key')
    original=repo.package(ctx['consumer'],m['id'])
    with zipfile.ZipFile(io.BytesIO(original)) as z: parts={n:z.read(n) for n in z.namelist()}
    parts['lesson.html']=b'<html>changed without authority</html>'
    pm=json.loads(parts['manifest.json']); pm['files']['lesson.html']=sha(parts['lesson.html'])
    parts['manifest.json']=canonical(pm)
    with pytest.raises(DomainError): LocalConsumer(repo.db).deliver(ctx['consumer'],m['id'],lambda _:m,lambda _:zip_package(parts))
