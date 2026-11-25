"""Isolated local bootstrap. Never touches existing Academy containers."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
RUNTIME=ROOT/'.runtime'
NAME='nikway-content-factory-mvp-db'

def setup():
    RUNTIME.mkdir(exist_ok=True,mode=0o700)
    config=RUNTIME/'config.json'
    if config.exists():
        print('Existing configuration retained. Use serve/demo/test commands.'); return
    # Refuse to take ownership of a pre-existing container.
    if subprocess.run(['docker','inspect',NAME],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:
        raise SystemExit('Container name occupied; inspect existing state, do not overwrite.')
    admin=secrets.token_hex(24); app=secrets.token_hex(24)
    env=RUNTIME/'postgres.env'; env.write_text('POSTGRES_PASSWORD='+admin+'\nPOSTGRES_DB=content_factory\n'); env.chmod(0o600)
    subprocess.run(['docker','run','-d','--name',NAME,'--label','nikway.scope=content-factory-mvp','--memory','256m','--cpus','1','-p','127.0.0.1:18532:5432','--env-file',str(env),'-v',str(RUNTIME/'pgdata')+':/var/lib/postgresql/data','postgres:16-alpine'],check=True,stdout=subprocess.DEVNULL)
    import psycopg
    admin_dsn=f'postgresql://postgres:{admin}@127.0.0.1:18532/content_factory'
    for _ in range(40):
        try:
            with psycopg.connect(admin_dsn) as c:
                from psycopg import sql
                c.execute(sql.SQL('CREATE ROLE cf_app LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS').format(sql.Literal(app)))
            break
        except psycopg.OperationalError: time.sleep(.25)
    else: raise SystemExit('Database did not become ready')
    cfg={'database':f'postgresql://cf_app:{app}@127.0.0.1:18532/content_factory','admin':admin_dsn,'objects':str(RUNTIME/'objects')}
    from cf.db import Database
    db=Database(cfg['database'],cfg['admin']); db.initialize()
    cfg['tokens']={r:db.provision('synthetic-academy',r,seconds=7*86400) for r in ['author','reviewer','consumer']}
    config.write_text(json.dumps(cfg,indent=2)); config.chmod(0o600)
    print('Isolated database and expiring local credentials initialized; secrets retained in .runtime/config.json only.')

def load():
    cfg=json.loads((RUNTIME/'config.json').read_text())
    os.environ['CF_DATABASE_URL']=cfg['database']; os.environ['CF_OBJECT_ROOT']=cfg['objects']
    return cfg

if __name__=='__main__':
    command=sys.argv[1] if len(sys.argv)>1 else 'help'
    if command=='setup': setup()
    elif command=='test':
        cfg=load(); os.environ['CF_ADMIN_URL']=cfg['admin']
        raise SystemExit(subprocess.call([sys.executable,'-m','pytest',*sys.argv[2:]],cwd=ROOT))
    elif command=='serve':
        load()
        import uvicorn
        uvicorn.run('cf.api:app',host='127.0.0.1',port=18500)
    else: print('Usage: python scripts/local.py setup|test|serve')
