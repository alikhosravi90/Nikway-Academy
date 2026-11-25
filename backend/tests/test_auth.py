import os, time
os.environ.setdefault('DATABASE_URL','postgresql+psycopg://unused:unused@localhost/unused')
os.environ.setdefault('OIDC_ISSUER','http://localhost:18480/realms/academy')
os.environ.setdefault('OIDC_JWKS_URL','http://localhost:18480/realms/academy/protocol/openid-connect/certs')
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from app.auth import decode_token

@pytest.fixture(scope='module')
def keys():
    private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    return private,private.public_key()

def claims():
    return {'sub':'00000000-0000-4000-8000-000000000001','iss':os.environ['OIDC_ISSUER'],'aud':'academy-api','iat':int(time.time()),'exp':int(time.time())+60}

@pytest.mark.parametrize('change',[{'aud':'wrong'},{'iss':'http://attacker'},{'exp':1},{'sub':'not-a-uuid'}])
def test_reject_wrong_identity_boundary(keys,change):
    c=claims(); c.update(change)
    with pytest.raises((jwt.PyJWTError,ValueError)):
        decode_token(jwt.encode(c,keys[0],algorithm='RS256'),keys[1])

def test_verify_real_signature_and_required_expiry(keys):
    token=jwt.encode(claims(),keys[0],algorithm='RS256')
    assert decode_token(token,keys[1])['aud']=='academy-api'
    c=claims(); del c['exp']
    with pytest.raises(jwt.PyJWTError):
        decode_token(jwt.encode(c,keys[0],algorithm='RS256'),keys[1])
    with pytest.raises(jwt.PyJWTError):
        decode_token(jwt.encode(claims(),'a'*32,algorithm='HS256'),keys[1])
