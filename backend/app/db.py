import os
from sqlalchemy import create_engine, text
engine = create_engine(os.environ['DATABASE_URL'], pool_size=5, max_overflow=5, pool_pre_ping=True)

def rows(conn, sql, **params):
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]

def one(conn, sql, **params):
    result = rows(conn, sql, **params)
    return result[0] if result else None
