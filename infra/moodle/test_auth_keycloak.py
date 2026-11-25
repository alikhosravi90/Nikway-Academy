"""Offline regression checks: reject existing-client drift without admin writes."""
import copy
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(os.environ.get('AUTH_KEYCLOAK_SCRIPT', Path(__file__).with_name('auth-keycloak.py')))

PROFILE = {
    'id': 'synthetic-client-id',
    'clientId': 'nikway-moodle-local', 'enabled': True,
    'protocol': 'openid-connect', 'publicClient': False,
    'clientAuthenticatorType': 'client-secret',
    'standardFlowEnabled': True, 'implicitFlowEnabled': False,
    'directAccessGrantsEnabled': False, 'serviceAccountsEnabled': False,
    'fullScopeAllowed': False,
    'redirectUris': ['http://localhost:18701/auth/oidc/'], 'webOrigins': [],
    'attributes': {'nikway.owner': 'moodle-local-pilot-v1',
                   'pkce.code.challenge.method': 'S256'},
    'defaultClientScopes': ['email', 'profile'], 'optionalClientScopes': [],
}


class ExistingClientDriftTests(unittest.TestCase):
    def assert_rejected_without_writes(self, field, value):
        profile = copy.deepcopy(PROFILE)
        profile[field] = value
        calls = []

        def urlopen(request, data=None, timeout=None):
            url = request if isinstance(request, str) else request.full_url
            method = ('POST' if data is not None else 'GET') if isinstance(request, str) else request.get_method()
            calls.append((method, url))
            if url.endswith('/realms/master/protocol/openid-connect/token'):
                self.assertEqual(method, 'POST')  # Authentication only; no admin mutation.
                payload = {'access_token': 'synthetic-test-token'}
            else:
                self.assertEqual(method, 'GET', 'Existing client must never be mutated')
                if url.endswith('/clients?clientId=nikway-moodle-local'):
                    payload = [{'id': PROFILE['id']}]
                elif url.endswith('/clients/' + PROFILE['id']):
                    payload = profile
                else:
                    self.fail('Unexpected request after profile drift: ' + url)
            return io.BytesIO(json.dumps(payload).encode())

        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            (runtime / '.env').write_text('KEYCLOAK_ADMIN_PASSWORD=synthetic-test-password\nACADEMY_IDP_PORT=18580\n')
            output = runtime / 'private' / 'auth.json'
            argv = [str(SCRIPT), '--academy-runtime', str(runtime), '--output', str(output)]
            with patch.object(sys, 'argv', argv), patch('urllib.request.urlopen', side_effect=urlopen):
                with self.assertRaisesRegex(SystemExit, field):
                    runpy.run_path(str(SCRIPT), run_name='__main__')
            self.assertFalse(output.exists(), 'Rejected drift must not emit credentials')
        self.assertEqual(len(calls), 3, 'Only authentication and two read-only profile requests expected')
        self.assertTrue(all(method == 'GET' for method, url in calls if '/admin/' in url))

    def test_changed_client_authenticator_rejected(self):
        self.assert_rejected_without_writes('clientAuthenticatorType', 'client-jwt')

    def test_changed_default_scopes_rejected(self):
        self.assert_rejected_without_writes('defaultClientScopes', ['email', 'profile', 'roles'])

    def test_changed_optional_scopes_rejected(self):
        self.assert_rejected_without_writes('optionalClientScopes', ['offline_access'])


if __name__ == '__main__':
    unittest.main()
