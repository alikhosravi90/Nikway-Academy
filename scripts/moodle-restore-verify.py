#!/usr/bin/env python3
"""Restore encrypted DB to disposable database; validate data archive without overwrite."""
import pathlib,subprocess,sys,secrets,json,hashlib
root=pathlib.Path(__file__).resolve().parents[1]; folder=pathlib.Path(sys.argv[1]).resolve()
c=[str(root/'scripts/moodle-compose.sh'),'exec','-T','db']
passfile=root/'infra/moodle/runtime/backup_passphrase'
def run(a,data=None): return subprocess.run(a,input=data,check=True,capture_output=True).stdout
def decrypt(name): return run(['gpg','--batch','--pinentry-mode','loopback','--passphrase-file',str(passfile),'--decrypt',str(folder/name)])
def sql(db,q):return run(c+['psql','-U','postgres','-d',db,'-At','-c',q])
def rows(data):
    result={}; table=None; lines=[]
    for line in data.splitlines():
        if line.startswith(b'COPY '): table=line.split(b' FROM stdin;')[0].decode();lines=[]
        elif table and line==b'\\.': result[table]={'rows':len(lines),'sha256':hashlib.sha256(b'\n'.join(sorted(lines))).hexdigest()};table=None
        elif table:lines.append(line)
    return result
name='verify_'+secrets.token_hex(6)
dump=decrypt('moodle.dump.gpg')
# pg_restore can emit plain COPY streams without a local server.
original=run(c+['pg_restore','--data-only','--file=-'],dump)
try:
    sql('postgres','CREATE DATABASE '+name+' OWNER moodle')
    run(c+['pg_restore','-U','postgres','-d',name,'--exit-on-error'],dump)
    restored=run(c+['pg_dump','-U','postgres','-d',name,'--data-only'])
    assert rows(original)==rows(restored), 'Restored table data differs'
    import tarfile,io,tempfile
    payload=decrypt('moodledata.tgz.gpg')
    with tarfile.open(fileobj=io.BytesIO(payload),mode='r:gz') as archive:
        members=archive.getmembers(); assert all(not pathlib.PurePosixPath(m.name).is_absolute() and '..' not in pathlib.PurePosixPath(m.name).parts for m in members)
        expected={m.name:hashlib.sha256(archive.extractfile(m).read()).hexdigest() for m in members if m.isfile()}
        with tempfile.TemporaryDirectory(prefix='moodle-data-restore-',dir=root/'infra/moodle/runtime') as target:
            archive.extractall(target,filter='data')
            actual={name:hashlib.sha256((pathlib.Path(target)/name).read_bytes()).hexdigest() for name in expected}
            assert actual==expected, 'Restored data file digest differs'
    print(json.dumps({'status':'PASS','tables':len(rows(original)),'rows':sum(x['rows'] for x in rows(original).values()),'data_archive_members':len(members),'data_files_restored_verified':len(expected),'data_scope':'temporary directory restoration and per-file SHA256; no live volume overwrite','config_decryptable':decrypt('config.php.gpg').startswith(b'<?php')}))
finally:
    sql('postgres','DROP DATABASE IF EXISTS '+name)
