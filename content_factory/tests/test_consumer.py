import copy
import json
import pytest
from cf.consumer import LocalConsumer
from cf.store import DomainError
from cf.contracts import ComponentInput

def setup_candidate(repo,ctx,content):
    r=repo.create_revision(ctx['author'],ComponentInput(**content),0)
    repo.review(ctx['reviewer'],r['revisionId'],'synthetic review')
    m=repo.prepare(ctx['reviewer'],'os-course',[r['revisionId']],'consumer-key')
    event=repo.events(ctx['consumer'])[-1]
    return r,m,event

def test_consumer_replay_and_withdrawal_at_delivery(repo,identities,content):
    ctx,_=identities; r,m,event=setup_candidate(repo,ctx,content)
    consumer=LocalConsumer(repo.db)
    fetch=lambda cid: repo.candidate(ctx['consumer'],cid)
    assert consumer.accept(ctx['consumer'],event,fetch)['replayed'] is False
    assert consumer.accept(ctx['consumer'],event,fetch)['replayed'] is True
    assert consumer.deliver(ctx['consumer'],m['id'],fetch,lambda cid:repo.package(ctx['consumer'],cid))[:2]==b'PK'
    repo.withdraw(ctx['reviewer'],r['revisionId'],'revoked')
    with pytest.raises(DomainError): consumer.deliver(ctx['consumer'],m['id'],fetch,lambda cid:repo.package(ctx['consumer'],cid))

def test_consumer_rejects_schema_digest_foreign_tenant_and_outage(repo,identities,content):
    ctx,_=identities; _,m,event=setup_candidate(repo,ctx,content)
    consumer=LocalConsumer(repo.db); fetch=lambda cid:repo.candidate(ctx['consumer'],cid)
    for field,value in [('schemaVersion','9.0.0'),('tenant','foreign')]:
        bad=copy.deepcopy(event); bad[field]=value
        with pytest.raises(DomainError): consumer.accept(ctx['consumer'],bad,fetch)
    bad=copy.deepcopy(event); bad['payload']['manifestDigest']='0'*64
    with pytest.raises(DomainError): consumer.accept(ctx['consumer'],bad,fetch)
    def outage(cid): raise ConnectionError('offline')
    with pytest.raises(ConnectionError): consumer.accept(ctx['consumer'],event,outage)
    assert consumer.accept(ctx['consumer'],event,fetch)['replayed'] is False
    with pytest.raises(ConnectionError): consumer.deliver(ctx['consumer'],m['id'],outage,lambda cid:b'')

def test_delivery_rejects_wrong_candidate_from_routing_mixup(repo,identities,content):
    ctx,_=identities
    _,m,_=setup_candidate(repo,ctx,content)
    consumer=LocalConsumer(repo.db)
    with pytest.raises(DomainError):
        consumer.deliver(ctx['consumer'],'different-requested-id',lambda _:m,lambda _:repo.package(ctx['consumer'],m['id']))
