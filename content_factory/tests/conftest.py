import copy
import json
import os
from pathlib import Path
import pytest
from cf.db import Database
from cf.store import Repository

@pytest.fixture
def db():
    return Database(os.environ['CF_DATABASE_URL'])

@pytest.fixture
def repo(db, tmp_path):
    return Repository(db, tmp_path / 'objects')

@pytest.fixture
def identities(db):
    # Each test receives new tenant IDs and independent active principals.
    import uuid
    tenant = str(uuid.uuid4())
    other = str(uuid.uuid4())
    tokens = {name: db.provision(t, role) for name,t,role in [
        ('author',tenant,'author'), ('reviewer',tenant,'reviewer'),
        ('consumer',tenant,'consumer'), ('other',other,'author')]}
    return {k: db.authenticate(v) for k,v in tokens.items()}, tokens

@pytest.fixture
def content():
    return copy.deepcopy(json.loads((Path(__file__).parents[1]/'fixtures/pdca.json').read_text()))
