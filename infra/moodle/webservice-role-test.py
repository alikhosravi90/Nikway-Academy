#!/usr/bin/env python3
"""Execute the exact provisioning role guard against synthetic capability fixtures, no DB writes."""
from pathlib import Path
import os
import shutil
import subprocess
source=(Path(__file__).parent/'webservice-provision.php').read_text()
guard=source[source.index('foreach ($caps as $cap) {'):source.index("assign_capability('webservice/rest:use'")]
program='''<?php
const CAP_ALLOW=1;
class context_system { static function instance() { return (object)['id'=>1]; } }
function check($caps) {
'''+guard+'''
}
check([]); check([(object)['capability'=>'webservice/rest:use','permission'=>1,'contextid'=>1]]);
$bad=[['capability'=>'moodle/site:config','permission'=>1,'contextid'=>1],['capability'=>'webservice/rest:use','permission'=>-1,'contextid'=>1],['capability'=>'webservice/rest:use','permission'=>1,'contextid'=>99]];
foreach ($bad as $fixture) { try { check([(object)$fixture]); } catch (Exception $e) { continue; } throw new Exception('Unsafe role accepted'); }
echo "PASS: five role capability fixtures; no database writes\\n";
'''
# Hosted runners use native PHP. Local operators may explicitly select an
# existing PHP container; never silently skip or assume a Moodle installation.
container=os.environ.get('NIKWAY_PHP_TEST_CONTAINER')
if container:
    command=['docker','exec','-i',container,'php']
elif shutil.which('php'):
    command=['php']
else:
    raise SystemExit('PHP required: install PHP CLI or set NIKWAY_PHP_TEST_CONTAINER to an existing local PHP container')
subprocess.run(command,input=program.encode(),check=True,timeout=30)
