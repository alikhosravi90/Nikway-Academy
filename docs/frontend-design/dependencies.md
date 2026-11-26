# Dependency decisions

Preserve React19 / TypeScript7 / Vite8 and the existing FastAPI/PostgreSQL/Keycloak/Moodle boundaries. Next.js migration was not introduced: this local authenticated SPA does not need a new server-rendering framework, and preserving operational authentication is more valuable than replacing the build tool.

- Existing Tailwind4 Vite integration is now enabled. Existing shadcn Button source is reused from `frontend/prototype/src/components/ui/button.tsx`, with Radix Slot/CVA/clsx utilities and explicit semantic color rules.
- Storybook10.6.9/react-vite10.6.9: MIT, registry peers include Vite5–8, React16–19 and TypeScript>=4.9. Node22.22.1 used. Build verified. Storybook is a development artifact only; its larger bundle is not shipped with Academy.
- @fontsource-variable/vazirmatn5.3.0: OFL-1.1, local WOFF2, Arabic/Latin subsets. License retained in frontend/VAZIRMATN-LICENSE.txt. No font CDN request.
- @axe-core/playwright4.14.1: MPL-2.0, development-only accessibility checks; compatible with installed Playwright1.65.1 and Node22.22.1.
- Lucide icons, React, Radix and other existing licenses remain documented in research.json. No new backend dependency.
- PWA uses a small explicit service worker and manifest. Only static offline notice/icons are cached; no token, API response, user content or authenticated document is cached. Offline learning/submission is deliberately unavailable.

`npm ci`, application build, unit tests and Storybook build are the compatibility evidence. The package lock is committed. Registry audit is a dependency check, not a complete application-security certification. Repository license remains unspecified; this work does not invent a license for the user's project.
