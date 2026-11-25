#!/usr/bin/env python3
"""Install only into empty Moodle DB, keeping password out of process arguments."""
import json, pathlib, subprocess
root=pathlib.Path(__file__).resolve().parents[1]
c=json.loads((root/'infra/moodle/runtime/credentials.json').read_text())
wrapper='''$c=json_decode(stream_get_contents(STDIN),true); $argv=['install_database.php','--agree-license','--adminuser='.$c['username'],'--adminpass='.$c['password'],'--adminemail=admin@example.invalid','--fullname=NIKWAY Academy Moodle Local','--shortname=NIKWAY Moodle']; $argc=count($argv); $_SERVER['argv']=$argv; $_SERVER['argc']=$argc; require '/var/www/moodle/admin/cli/install_database.php';'''
subprocess.run([str(root/'scripts/moodle-compose.sh'),'exec','-T','-u','www-data','moodle','php','-r',wrapper],input=json.dumps(c).encode(),check=True)
