<?php
// Pure fixture tests; no Moodle bootstrap or database writes.
require(__DIR__ . '/nikway-content-binding.php');
$sub = '00000000-0000-4000-8000-000000000001';
$valid = (object)['username' => $sub, 'auth' => 'oidc', 'mnethostid' => 1,
    'idnumber' => 'keycloak:academy:' . $sub, 'suspended' => 0, 'deleted' => 0];
nikway_validate_content_binding($valid, $sub, 1);
$rejected = 0;
foreach (['username' => 'other', 'auth' => 'manual', 'mnethostid' => 2,
          'idnumber' => 'unbound', 'suspended' => 1, 'deleted' => 1] as $field => $value) {
    $invalid = clone $valid;
    $invalid->$field = $value;
    try { nikway_validate_content_binding($invalid, $sub, 1); }
    catch (RuntimeException $e) { $rejected++; continue; }
    throw new RuntimeException('Failed to reject invalid ' . $field);
}
echo json_encode(['valid_binding_passed' => true, 'invalid_bindings_rejected' => $rejected]) . "\n";
