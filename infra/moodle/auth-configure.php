<?php
// CLI-only configuration of the pinned maintained auth_oidc plugin; no core patch.
define('CLI_SCRIPT', true);
require('/var/www/moodle/config.php');
require_once($CFG->dirroot.'/auth/oidc/lib.php');
\core\session\manager::set_user(get_admin());
$input=json_decode(file_get_contents($argv[1] ?? '/run/moodle-auth.json'),true,512,JSON_THROW_ON_ERROR);
if ($CFG->wwwroot !== 'http://localhost:18701' || $input['client_id'] !== 'nikway-moodle-local') {
    throw new Exception('Refuse configuration outside isolated local Moodle');
}
if ((int)get_config('auth_oidc','version')!==2026100500 || auth_oidc_is_local_365_installed()) {
    throw new Exception('Require exact standalone auth_oidc 5.3.0 without account-matching suite');
}
$allowed=['00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000003'];
if (array_column($input['users'],'sub') !== $allowed || array_column($input['users'],'username') !== $allowed) {
    throw new Exception('Subject allowlist mismatch');
}
$tx=$DB->start_delegated_transaction();
$settings=['clientid'=>$input['client_id'],'clientsecret'=>$input['client_secret'],
    'idptype'=>AUTH_OIDC_IDP_TYPE_OTHER,'clientauthmethod'=>AUTH_OIDC_AUTH_METHOD_SECRET,
    'authendpoint'=>$input['authorization_endpoint'],'tokenendpoint'=>$input['token_endpoint'],
    'oidcscope'=>'openid profile email','oidcresource'=>'','usepkce'=>1,
    'bindingusernameclaim'=>'sub','userrestrictions'=>'^(00000000-0000-4000-8000-000000000001|00000000-0000-4000-8000-000000000003)$',
    'userrestrictionscasesensitive'=>1,'forceredirect'=>0,'debugmode'=>0,
    'opname'=>'NIKWAY SSO','field_map_firstname'=>'givenName','field_map_lastname'=>'surname','field_map_email'=>'mail'];
$previous=get_config('auth_oidc','nikway_profile');
if ($previous && $previous!=='subject-allowlist-v1') { throw new Exception('Unowned OIDC profile'); }
if (!$previous && get_config('auth_oidc','clientid')) { throw new Exception('Refuse replacing existing provider'); }
foreach ($settings as $key=>$value) {
    if ($previous && (string)get_config('auth_oidc',$key)!==(string)$value) { throw new Exception('OIDC config drift: '.$key); }
    set_config($key,$value,'auth_oidc');
}
set_config('nikway_profile','subject-allowlist-v1','auth_oidc');
set_config('authpreventaccountcreation',1);
set_config('auth','oidc');
set_config('registerauth','');
foreach (['auth/oidc:manageconnection','auth/oidc:manageconnectionconnect','auth/oidc:manageconnectiondisconnect'] as $cap) {
    assign_capability($cap,CAP_PROHIBIT,$CFG->defaultuserroleid,context_system::instance()->id,true);
}
foreach ($input['users'] as $u) {
    $user=$DB->get_record('user',['username'=>$u['sub'],'mnethostid'=>$CFG->mnet_localhost_id]);
    if ($user && ($user->auth!=='oidc' || $user->idnumber!=='keycloak:academy:'.$u['sub'] || $user->deleted)) {
        throw new Exception('Refuse rebinding an existing account by username or email');
    }
    if (!$user) {
        $record=(object)['username'=>$u['sub'],'auth'=>'oidc','confirmed'=>1,'mnethostid'=>$CFG->mnet_localhost_id,
          'password'=>'','email'=>$u['email'],'firstname'=>$u['firstname'],'lastname'=>$u['lastname'],
          'idnumber'=>'keycloak:academy:'.$u['sub']];
        \core\user::create_user($record,false,false);
    }
}
$tx->allow_commit();
echo json_encode(['configured'=>true,'provider'=>$input['issuer_base'],'allowlisted_subjects'=>count($allowed),
    'subject_binding'=>'sub','account_autocreation'=>false,'roles_from_identity'=>false,'pkce'=>'S256'])."\n";
