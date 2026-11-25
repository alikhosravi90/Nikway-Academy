"""Tenant-scoped consistent logical backup; credentials are deliberately excluded."""
import json
import shutil
from pathlib import Path
from psycopg import sql
from psycopg.types.json import Jsonb
from psycopg.conninfo import conninfo_to_dict
import psycopg
from .store import canonical,sha,require
from .errors import DomainError

TABLES=('heads','revisions','states','candidates','usages','pipeline_runs','events','receipts')
JSON_FIELDS={'manifest','data','payload'}

def integrity_report(repo,ctx):
    require(ctx,'reviewer')
    with repo.db.transaction(ctx) as c:
        rows=c.execute('SELECT revision_id,digest FROM revisions').fetchall()
    referenced={r['digest'] for r in rows}; bad=[]
    for row in rows:
        p=repo.object_path(ctx.tenant,row['digest'])
        if not p.exists() or sha(p.read_bytes())!=row['digest']: bad.append(row['revision_id'])
    directory=repo.object_path(ctx.tenant,'unused').parent
    present={p.name for p in directory.iterdir() if p.is_file()} if directory.exists() else set()
    return {'missing_or_corrupt':bad,'unreferenced_objects':sorted(present-referenced),'action':'report_only_no_deletion'}

def backup(repo,ctx,destination):
    require(ctx,'reviewer'); dest=Path(destination)
    dest.mkdir(parents=True,exist_ok=False)
    (dest/'objects').mkdir()
    # Immutable objects are written before their metadata commit and never deleted by the service.
    with repo.db.transaction(ctx,snapshot=True) as c:
        tables={t:c.execute(sql.SQL('SELECT * FROM {}').format(sql.Identifier(t))).fetchall() for t in TABLES}
        for row in tables['revisions']:
            src=repo.object_path(ctx.tenant,row['digest'])
            if not src.exists() or sha(src.read_bytes())!=row['digest']: raise DomainError('backup object integrity failure')
            shutil.copyfile(src,dest/'objects'/row['digest'])
    data={'schemaVersion':'1.0.0','tenant':ctx.tenant,'tables':tables,'credentials':'excluded; reprovision locally'}
    raw=json.dumps(data,ensure_ascii=False,sort_keys=True,default=str).encode()
    (dest/'snapshot.json').write_bytes(raw)
    (dest/'snapshot.sha256').write_text(sha(raw))
    return {'tenant':ctx.tenant,'revisions':len(tables['revisions']),'snapshotDigest':sha(raw)}

def restore(repo,snapshot):
    if not repo.db.admin_dsn: raise DomainError('restore requires operator connection')
    dbname=conninfo_to_dict(repo.db.admin_dsn).get('dbname','')
    if not dbname.startswith('cf_restore_'): raise DomainError('restore only into fresh cf_restore_ database')
    source=Path(snapshot); raw=(source/'snapshot.json').read_bytes()
    if sha(raw)!=(source/'snapshot.sha256').read_text(): raise DomainError('snapshot integrity failure')
    data=json.loads(raw)
    if data['schemaVersion']!='1.0.0' or set(data['tables'])!=set(TABLES): raise DomainError('unsupported backup schema')
    tenant=data['tenant']
    for rows in data['tables'].values():
        if any(r['tenant']!=tenant for r in rows): raise DomainError('mixed tenant backup')
    for row in data['tables']['revisions']:
        digest=row['digest']
        if len(digest)!=64 or any(x not in '0123456789abcdef' for x in digest): raise DomainError('invalid object digest')
        raw_object=(source/'objects'/digest).read_bytes()
        if sha(raw_object)!=digest: raise DomainError('backup object integrity failure')
    repo.db.initialize()
    with psycopg.connect(repo.db.admin_dsn) as c:
        for table in TABLES:
            if c.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier(table))).fetchone()[0]: raise DomainError('restore target not empty')
        for row in data['tables']['revisions']:
            repo.put_object(tenant,(source/'objects'/row['digest']).read_bytes())
        for table in TABLES:
            for row in data['tables'][table]:
                cols=list(row)
                values=[Jsonb(row[k]) if k in JSON_FIELDS else row[k] for k in cols]
                c.execute(sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(sql.Identifier(table),sql.SQL(',').join(map(sql.Identifier,cols)),sql.SQL(',').join(sql.Placeholder() for _ in cols)),values)
    return {'status':'restored','tenant':tenant,'credentialPolicy':'new credentials required'}
