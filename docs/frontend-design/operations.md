# Local frontend design preview

The preview is independent: **http://localhost:18901/**, API localhost18900. Existing Academy18501, Moodle18701 and baseline18401 remain in place. Preview reuses candidate authentication, database and learning data: authorized course submissions are real writes to the existing synthetic candidate, not fake previews. No production/public deployment or merge is performed.

## Start, stop and reproduce

Requires the existing candidate `.env`, Docker Compose, installed Moodle, port18900/18901 and free subnet10.253.245.0/28. Check subnet availability before installation on another host. From this checkout:

```sh
# Existing installation:
scripts/frontend-design-compose.sh ps
scripts/frontend-design-compose.sh stop
scripts/frontend-design-compose.sh start
scripts/frontend-design-compose.sh restart
# Rebuild/provision when needed (does not create a second Academy database):
ACADEMY_ENV_FILE=/absolute/path/to/candidate/infra/runtime/.env scripts/frontend-design-install.sh
# Component library:
cd frontend
npm ci
npm run storybook
```

Storybook: localhost18906, loopback only. `npm run build-storybook` produces an independently inspectable static UI kit. It contains example design-system data, never production/student data. Three palettes can also be selected in Profile → UI kit in the functional app. Light/dark and Persian/English shell controls are available in the header. Source course text is preserved, not automatically translated.

Installation adds only exact localhost18901 redirect/logout/origin entries to the existing S256 public Academy client; implicit flow, password grants and service accounts must already be off. Existing client entries are preserved. The read-only Moodle service is described in [Moodle API contract](../moodle-frontend-api.md). Secrets stay in ignored mode0600 files and a private named Docker volume readable by API UID10001; never put them in VITE variables. Preserve the secret volume when stopping. The original Moodle data/DB volumes are unchanged.

## Offline and authorization boundaries

Only offline notice/icons are cached. Authenticated HTML and API/coursework are network-only. Offline navigation shows a bilingual reconnect message, not stale learning data. This PWA does not support offline learning or submission. Device preferences contain only locale/theme/palette/reduced effects. The browser holds Keycloak tokens in memory; Moodle tokens never reach it.

Moodle remains a single explicitly mapped organization; tenantB receives disabled and no course metadata. Its progress is read through the API and not synchronized into Academy. A dashboard completion percentage does not establish assessment mastery. AI Tutor shows a truthful unavailable state and reflection prompts; no fabricated AI responses. Projects are existing course practices; Library is real lesson content. Administration grants no new capabilities and reviewer actions still use backend permissions.

Seven-day Moodle tokens require explicit rotation when expired. Provider auth/idnumber validation is provisioning-time; runtime verifies token userid/username. Existing local-only OIDC security limitations remain. Full WCAG2.2AA conformance, screen-reader testing across assistive technologies and production security approval are not implied by automated checks.
