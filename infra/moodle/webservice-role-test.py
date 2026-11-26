#!/usr/bin/env python3
"""Execute the exact provisioning role guard against synthetic capability fixtures, no DB writes."""
from pathlib import Path
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
subprocess.run(['docker','exec','-i','nikway-academy-moodle-moodle-1','php'],input=program.encode(),check=True)
