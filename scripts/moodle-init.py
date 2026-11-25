#!/usr/bin/env python3
"""Generate local-only private bootstrap files. Never overwrite existing secrets."""
import json, os, pathlib, secrets
root=pathlib.Path(__file__).resolve().parents[1]
r=root/'infra/moodle/runtime'; r.mkdir(parents=True, exist_ok=True); r.chmod(0o700)
generated=('config.php','db_password','postgres_password','credentials.json','backup_passphrase')
if any((r/name).exists() or (r/name).is_symlink() for name in generated):
    raise SystemExit('Existing or partial private Moodle configuration preserved; no files overwritten.')
def write(name,text):
    with (r/name).open('x') as f: f.write(text)
os.umask(0o077)
pw=secrets.token_hex(32)
write('db_password',pw+'\n')
write('postgres_password',secrets.token_hex(32)+'\n')
write('credentials.json',json.dumps({'username':'localadmin','password':secrets.token_urlsafe(32)+'Aa1!','url':'http://localhost:18701'})+'\n')
write('backup_passphrase',secrets.token_urlsafe(48)+'\n')
write('config.php','''<?php
unset($CFG); global $CFG; $CFG = new stdClass();
$CFG->dbtype='pgsql'; $CFG->dblibrary='native'; $CFG->dbhost='db';
$CFG->dbname='moodle'; $CFG->dbuser='moodle'; $CFG->dbpass='%s';
$CFG->prefix='mdl_'; $CFG->dboptions=['dbpersist'=>false, 'dbport'=>5432];
$CFG->wwwroot='http://localhost:18701'; $CFG->dataroot='/var/moodledata';
$CFG->directorypermissions=02770;
$CFG->noreplyaddress='noreply@example.invalid';
$CFG->noemailever=true;
require_once(__DIR__ . '/lib/setup.php');
''' % pw)
print('Private Moodle configuration generated (0600); credentials not displayed.')
