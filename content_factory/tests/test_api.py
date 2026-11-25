import pytest
from fastapi.testclient import TestClient
from cf.api import create_app

@pytest.fixture
def client(repo):
    with TestClient(create_app(repo)) as client: yield client

def test_api_auth_roles_and_forbidden_tenant(client,identities,content):
    _,tokens=identities
    assert client.get('/v1/components').status_code==401
    a={'Authorization':'Bearer '+tokens['author']}
    forged={**content,'tenant':'other'}
    assert client.post('/v1/components',headers=a,json={'component':forged,'expectedRevision':0}).status_code==422
    r=client.post('/v1/components',headers=a,json={'component':content,'expectedRevision':0})
    assert r.status_code==201
    rid=r.json()['revisionId']
    assert client.get('/v1/revisions/'+rid,headers={'Authorization':'Bearer '+tokens['other']}).status_code==404
    assert client.get('/v1/revisions/'+rid,headers={'Authorization':'Bearer '+tokens['consumer']}).status_code==403
    assert client.post('/v1/revisions/'+rid+'/review',headers=a,json={'note':'self'}).status_code==403

def test_api_token_revocation_and_payload_bound(client,repo,identities):
    _,tokens=identities; headers={'Authorization':'Bearer '+tokens['author']}
    assert client.get('/v1/components',headers=headers).status_code==200
    repo.db.revoke(tokens['author'])
    assert client.get('/v1/components',headers=headers).status_code==401
    assert client.post('/v1/components',headers={'Content-Type':'application/json'},content=b'x'*300001).status_code==413

def test_no_release_endpoint(client):
    assert client.post('/v1/releases',json={}).status_code==404
