# Moodle local SSO decision

Scope: isolated Moodle 5.3.1 at `http://localhost:18701`, dedicated client `nikway-moodle-local` in the existing synthetic Academy realm. The scripts are operator-invoked; their presence does not establish that SSO has passed a browser test. No existing Keycloak client, user, role or realm policy is changed.

## Selected supported extension

Core OAuth2 was inspected first. Exact Moodle 5.3.1 `public/lib/classes/oauth2/endpoint.php::validate_url` requires HTTPS for endpoints, while its OAuth client has no PKCE support. Core's account-creation restriction also does not disable its email-matching path. We do not patch core, bypass endpoint validation, install a local CA globally, or bypass browser certificate checks.

Use the standalone maintained `auth_oidc` 5.3.0 plugin, version `2026100500`, Git commit `5866154d55fa56ea5a112386fac9722c3a58ac7b`, tag `v5.3.0` from [Microsoft/moodle-auth_oidc](https://github.com/microsoft/moodle-auth_oidc/tree/5866154d55fa56ea5a112386fac9722c3a58ac7b). [Moodle Marketplace](https://marketplace.moodle.com/plugins/auth_oidc/versions?show=all) identifies this stable release for Moodle 5.3 and its addition of PKCE. License: GPL-3.0-or-later, as declared by the source headers. Install only this plugin, not the Microsoft 365 suite or account-matching integration. [Moodle documentation](https://docs.moodle.org/503/en/Microsoft_365) describes support for non-Microsoft OIDC providers.

## Configuration and identity boundary

1. `infra/moodle/auth-keycloak.py --academy-runtime <private Academy runtime directory> --output <private Moodle auth.json>` creates only the dedicated client or checks its exact existing profile. Existing mismatched/unowned clients are rejected. The client uses a secret, authorization code, required S256 PKCE, exact callback `http://localhost:18701/auth/oidc/`, no wildcard redirect, no direct grants, no service account, no implicit flow and no full-scope access. Credentials and generated secret are never printed. Output is created exclusively with mode 0600.
2. Mount that private JSON into the Moodle container and run `php /path/to/auth-configure.php /path/to/auth.json` as the local container operator after Moodle and the pinned plugin are installed. The script uses Moodle configuration/user/capability APIs and refuses an unrelated provider or profile drift.
3. Configure `idptype=OTHER`, `bindingusernameclaim=sub`, `usepkce=1` and an anchored subject allowlist containing only the existing synthetic tenant-A learner (`...0001`) and reviewer (`...0003`). Precreated Moodle usernames equal the full immutable subject UUID; `idnumber` records the fixed Academy realm binding. No email or display name is used to identify or merge accounts. Account auto-creation is disabled, and user connection-management capabilities are prohibited in this new Moodle instance. No identity claim grants teacher/admin privileges. Course enrolment roles are a separate explicit action.
4. Authorization goes to the existing loopback Keycloak URL; server token exchange goes to `http://keycloak:8080` through the explicitly attached candidate Docker network. Existing Academy browser configuration remains unchanged. Only the Moodle web container needs that external network; its database stays private.

The allowlist is checked before login/account handling, including returning token records. A tenant-B identity must be denied even if it already has a valid Keycloak SSO session. Preprovisioning or Moodle enrolment is **not** live synchronization of Academy memberships: later Academy membership revocation is not automatically reflected in an existing Moodle session. Moodle suspension/session revocation remains a separate local administrative action.

## Important validation limit

Inspection of this plugin's `process_idtoken` and `jwt` implementation found ID-token decoding, nonce checking and standard subject extraction, but no independent JWKS signature, issuer or audience verification in that path. It receives tokens from the fixed configured token endpoint after a confidential-client authorization-code exchange with S256 PKCE and single-use state. The source also prefers the Microsoft `oid` claim for its internal token key when present; the selected Keycloak client supplies standard `sub`, and the configured binding/allowlist is explicitly `sub`.

Accordingly this is a **trusted loopback/internal-network synthetic pilot**, not production OIDC validation certification. No browser-supplied ID token is accepted by our setup script. Production adoption needs HTTPS, a complete verification review (signature/issuer/audience/nonce/expiry), session and revocation behavior, and explicit maintenance ownership. No custom JWT validation claim is made here.

## Required operational evidence

- Real learner-A and reviewer-A browser login and logout via Keycloak; the authorization request includes S256 PKCE.
- Learner-B denied without account creation or course access.
- Learner has no teacher/site-admin permissions; reviewer gets only the explicitly selected course role.
- Repeated setup is idempotent; unexpected provider/client drift fails closed.
- Existing Academy client configuration remains unchanged; existing application login still works.
- Wrong code verifier, invalid/replayed state, and unauthorized callback are rejected by the actual flow where tested; unexecuted cases remain unverified.

No merge, release, public deployment, external email or real learner data is authorized by these scripts.

## Internal token endpoint and Moodle's outbound policy

Moodle's default outbound URL policy blocks RFC1918 addresses and allows only ports 80/443. The first live callback failed because `keycloak:8080` resolves inside the blocked 10/8 network. `auth-network.py` is a separate explicit local configuration step. It inspects the running candidate Keycloak network address, requires Moodle DNS to resolve to the same address, and subtracts only that IPv4 `/32` from the existing 10/8 block using exact CIDRs. All other original private/loopback/metadata-address blocks remain. Port 8080 is added to the allowed-port list; this port setting applies globally to Moodle outbound requests, while the private-address exception remains a single IP. No core/plugin security check is bypassed.

The script checks the original or previously owned policy, performs the change in a database transaction, verifies the Keycloak URL passes and representative other private addresses remain blocked. Unexpected configuration or IP drift fails closed. An existing persisted exception does not itself track Docker address reassignment: if that IP is later given to another container, it could remain reachable. The pilot therefore depends on the trusted isolated Docker network, preserving the candidate container identity, and revalidating before adopting a changed runtime. Do not treat this as a production egress policy or automatic revocation mechanism.

`auth-test.py` performs actual HTTP authorization/form_post/token-backed login through isolated cookie jars, observes S256, checks exact precreated profile IDs, logout, tenant-B rejection without account creation and unknown-state denial. It never prints credentials, cookies, authorization codes or tokens. Browser rendering remains an independent test.
