<?php
// Pure guard: provider identity binding must survive bootstrap-to-import drift.
function nikway_validate_content_binding(object $user, string $subject, int $localhostid): void {
    if (($user->username ?? null) !== $subject || ($user->auth ?? null) !== 'oidc' ||
            (int)($user->mnethostid ?? -1) !== $localhostid ||
            ($user->idnumber ?? null) !== 'keycloak:academy:' . $subject ||
            (int)($user->suspended ?? 1) !== 0 || (int)($user->deleted ?? 1) !== 0) {
        throw new RuntimeException('Refuse enrolment of an unbound or inactive OIDC subject');
    }
}
