<?php
// Operator-only, dedicated read-only service; output contains secrets and MUST be captured privately.
define('CLI_SCRIPT', true);
require('/var/www/moodle/config.php');
require_once('/tmp/nikway-content-binding.php');
\core\session\manager::set_user(get_admin());
if ($CFG->wwwroot !== 'http://localhost:18701') throw new Exception('Local pilot only');
$subjects=['00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000003'];
$functions=['core_webservice_get_site_info','core_enrol_get_users_courses','core_course_get_contents'];
$users=[];
foreach ($subjects as $sub) {
 $u=$DB->get_record('user',['username'=>$sub], '*', MUST_EXIST);
 nikway_validate_content_binding($u,$sub,(int)$CFG->mnet_localhost_id); $users[$sub]=$u;
}
$tx=$DB->start_delegated_transaction();
$s=$DB->get_record('external_services',['shortname'=>'nikway_frontend_readonly']);
if (!$s) {
 $s=(object)['name'=>'NIKWAY frontend read only','shortname'=>'nikway_frontend_readonly','enabled'=>1,'restrictedusers'=>1,'downloadfiles'=>0,'uploadfiles'=>0,'timecreated'=>time(),'requiredcapability'=>''];
 $s->id=$DB->insert_record('external_services',$s);
 foreach ($functions as $f) $DB->insert_record('external_services_functions',(object)['externalserviceid'=>$s->id,'functionname'=>$f]);
}
$actual=array_values($DB->get_fieldset_select('external_services_functions','functionname','externalserviceid=?',[$s->id])); sort($actual); $expected=$functions; sort($expected);
if ($actual!==$expected || !$s->enabled || !$s->restrictedusers || $s->downloadfiles || $s->uploadfiles) throw new Exception('Service profile drift');
$role=$DB->get_record('role',['shortname'=>'nikway_ws_reader']);
if (!$role) {$rid=create_role('NIKWAY REST reader','nikway_ws_reader','Only REST transport access; no course or user administration'); $role=$DB->get_record('role',['id'=>$rid]);}
assign_capability('webservice/rest:use',CAP_ALLOW,$role->id,context_system::instance()->id);
$output=['tenant_id'=>'10000000-0000-4000-8000-000000000001','users'=>[]];
foreach ($users as $sub=>$u) {
 role_assign($role->id,$u->id,context_system::instance()->id);
 if (!$DB->record_exists('external_services_users',['externalserviceid'=>$s->id,'userid'=>$u->id])) $DB->insert_record('external_services_users',(object)['externalserviceid'=>$s->id,'userid'=>$u->id,'timecreated'=>time()]);
 $token=$DB->get_record('external_tokens',['externalserviceid'=>$s->id,'userid'=>$u->id,'tokentype'=>0]);
 if ($token && $token->validuntil <= time()) throw new Exception('Token expired: explicit operator rotation required');
 $value=$token ? $token->token : \core_external\util::generate_token(0,$s,$u->id,context_system::instance(),time()+7*86400,'','NIKWAY read only pilot');
 $output['users'][$sub]=['userid'=>(int)$u->id,'token'=>$value];
}
set_config('enablewebservices',1);
$protocols=array_filter(explode(',',get_config('core','webserviceprotocols') ?: '')); if (!in_array('rest',$protocols)) $protocols[]='rest'; set_config('webserviceprotocols',implode(',',$protocols));
$tx->allow_commit(); echo json_encode($output,JSON_THROW_ON_ERROR);
