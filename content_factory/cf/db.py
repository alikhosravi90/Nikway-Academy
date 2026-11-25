import hashlib
import secrets
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from .errors import DomainError

@dataclass(frozen=True)
class Context:
    tenant: str
    subject: str
    role: str

def digest_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

class Database:
    def __init__(self, dsn, admin_dsn=None):
        self.dsn=dsn
        self.admin_dsn=admin_dsn

    def initialize(self):
        if not self.admin_dsn: raise RuntimeError('admin connection required for migration only')
        with psycopg.connect(self.admin_dsn) as c:
            c.execute(Path(__file__).with_name('schema.sql').read_text())
            c.execute('GRANT SELECT ON principals TO cf_app')
            c.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON heads,revisions,states,candidates,usages,pipeline_runs,events,receipts TO cf_app')

    def provision(self, tenant, role, seconds=86400):
        # Operator-only bootstrap; never exposed over HTTP.
        import os
        admin=self.admin_dsn or os.environ.get('CF_ADMIN_URL')
        if not admin: raise RuntimeError('operator connection required')
        token=secrets.token_urlsafe(32)
        with psycopg.connect(admin) as c:
            c.execute("INSERT INTO principals(token_hash,subject,tenant,role,expires_at) VALUES(%s,%s,%s,%s,now()+(%s * interval '1 second'))",(digest_token(token),str(uuid4()),tenant,role,seconds))
        return token

    def revoke(self, token):
        import os
        with psycopg.connect(self.admin_dsn or os.environ['CF_ADMIN_URL']) as c:
            c.execute('UPDATE principals SET active=false WHERE token_hash=%s',(digest_token(token),))

    def authenticate(self, token):
        with psycopg.connect(self.dsn, row_factory=dict_row) as c:
            row=c.execute('SELECT tenant,subject,role FROM principals WHERE token_hash=%s AND active AND expires_at>now()',(digest_token(token),)).fetchone()
            if not row: raise DomainError('invalid or expired credential',401)
            return Context(**row)

    @contextmanager
    def transaction(self, ctx, snapshot=False):
        with psycopg.connect(self.dsn,row_factory=dict_row) as c:
            if snapshot:
                c.isolation_level=psycopg.IsolationLevel.REPEATABLE_READ
                c.read_only=True
            c.execute("SELECT set_config('cf.tenant',%s,true)",(ctx.tenant,))
            c.execute("SET LOCAL statement_timeout='5s'")
            yield c
