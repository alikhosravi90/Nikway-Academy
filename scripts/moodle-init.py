#!/usr/bin/env python3
"""Generate local-only private bootstrap files. Never overwrite existing secrets."""
import json, os, pathlib, secrets
root=pathlib.Path(__file__).resolve().parents[1]
r=root/'infra/moodle/runtime'; r.mkdir(parents=True, exist_ok=True); r.chmod(0o700)
if (r/'config.php').exists():
    raise SystemExit('Private Moodle configuration already exists; preserved.')
os.umask(0o077)
pw=secrets.token_hex(32)
(r/'db_password').write_text(pw+'\n')
(r/'postgres_password').write_text(secrets.token_hex(32)+'\n')
(r/'credentials.json').write_text(json.dumps({'username':'localadmin','password':secrets.token_urlsafe(32)+'Aa1!','url':'http://localhost:18701'})+'\n')
(r/'backup_passphrase').write_text(secrets.token_urlsafe(48)+'\n')
(r/'config.php').write_text('''<?php
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
