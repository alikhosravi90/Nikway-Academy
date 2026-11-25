#!/usr/bin/env python3
"""Explicit local operator step: permit ONLY current candidate Keycloak IP through Moodle SSRF policy."""
import ipaddress,json,subprocess

def run(args,input=None):return subprocess.run(args,input=input,text=True,capture_output=True,check=True).stdout
info=json.loads(run(['docker','inspect','nikway-academy-content-keycloak-1']))[0]
ip=info['NetworkSettings']['Networks']['nikway-academy-content_default']['IPAddress']
address=ipaddress.IPv4Address(ip)
if address not in ipaddress.IPv4Network('10.0.0.0/8'):raise SystemExit('Unexpected candidate address range; review required')
excluded=[str(x) for x in ipaddress.IPv4Network('10.0.0.0/8').address_exclude(ipaddress.IPv4Network(ip+'/32'))]
policy='\n'.join(['127.0.0.0/8','192.168.0.0/16',*excluded,'172.16.0.0/12','0.0.0.0','localhost','169.254.169.254','0000::1'])
# Values are generated numeric CIDRs, never untrusted source text or credentials.
code="""<?php define('CLI_SCRIPT',true);require('/var/www/moodle/config.php');require_once($CFG->libdir.'/filelib.php');
$ip=IPVALUE;$policy=POLICYVALUE;
if ($CFG->wwwroot!=='http://localhost:18701' || gethostbyname('keycloak')!==$ip) {throw new Exception('Runtime/DNS mismatch');}
$old=get_config('auth_oidc','nikway_backchannel_ip');
$default="127.0.0.0/8\\n192.168.0.0/16\\n10.0.0.0/8\\n172.16.0.0/12\\n0.0.0.0\\nlocalhost\\n169.254.169.254\\n0000::1";
$current=get_config('core','curlsecurityblockedhosts');
if (($old && ($old!==$ip || $current!==$policy)) || (!$old && $current!==$default)) {throw new Exception('Policy drift; review before change');}
set_config('curlsecurityblockedhosts',$policy);set_config('curlsecurityallowedport',"80\\n443\\n8080");
set_config('nikway_backchannel_ip',$ip,'auth_oidc');
$helper=new \\core\\files\\curl_security_helper();
if ($helper->url_is_blocked('http://keycloak:8080/realms/academy/protocol/openid-connect/token')) {throw new Exception('Keycloak remains blocked');}
foreach (['http://127.0.0.1','http://169.254.169.254','http://10.253.244.2:8080','http://192.168.1.1','http://172.16.0.1'] as $url) {
 if (!(new \\core\\files\\curl_security_helper())->url_is_blocked($url)) {throw new Exception('Private boundary unexpectedly open');}
}
echo json_encode(['configured'=>true,'allowed_private_ip'=>$ip,'port'=>8080,'other_private_ranges_blocked'=>true,'core_or_plugin_patch'=>false])."\\n";
""".replace('IPVALUE',json.dumps(ip)).replace('POLICYVALUE',json.dumps(policy))
print(run(['docker','exec','-i','nikway-academy-moodle-moodle-1','php'],code),end='')
