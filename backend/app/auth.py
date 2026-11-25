import os
from dataclasses import dataclass
from uuid import UUID
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from .db import engine, one

bearer = HTTPBearer(auto_error=False)
issuer = os.environ['OIDC_ISSUER']
audience = os.environ.get('OIDC_AUDIENCE','academy-api')
jwks = jwt.PyJWKClient(os.environ['OIDC_JWKS_URL'], cache_jwk_set=True, lifespan=60, timeout=5)

@dataclass
class Context:
    conn: object
    sub: str
    tenant_id: str
    role: str

def decode_token(token, key):
    claims = jwt.decode(token, key, algorithms=['RS256'], audience=audience, issuer=issuer,
                        options={'require':['exp','iat','iss','aud','sub']})
    UUID(claims['sub'])
    return claims

def authenticated(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None:
        raise HTTPException(401, 'Authentication required', headers={'WWW-Authenticate':'Bearer'})
    try:
        key = jwks.get_signing_key_from_jwt(credentials.credentials)
        claims = decode_token(credentials.credentials, key.key)
    except (jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(401, 'Invalid or expired access token', headers={'WWW-Authenticate':'Bearer'})
    with engine.begin() as conn:
        conn.execute(text("SET LOCAL statement_timeout = '5s'"))
        # Control: per-transaction settings never survive pooled connection reuse.
        conn.execute(text("SELECT set_config('app.subject',:sub,true)"), {'sub':claims['sub']})
        member = one(conn,'SELECT tenant_id, role FROM memberships WHERE subject=:sub AND active',sub=claims['sub'])
        if not member:
            raise HTTPException(403, 'Active membership required')
        tenant = str(member['tenant_id'])
        conn.execute(text("SELECT set_config('app.tenant_id',:tenant,true)"), {'tenant':tenant})
        yield Context(conn, claims['sub'], tenant, member['role'])
