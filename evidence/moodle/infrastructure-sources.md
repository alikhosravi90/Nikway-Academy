# Moodle isolated installation provenance

Observed 2026-11-25. Official Moodle5.3.1 release, published12November2026, selected over mutable weekly build.

- Requirements: https://moodledev.io/general/releases/5.3 — PHP>=8.3,8.4supported; PostgreSQL>=17. ExistingAcademyPG16cannotbe reused.
- Release: https://download.moodle.org/releases/latest/
- Archive: https://download.moodle.org/download.php/direct/stable503/moodle-5.3.1.tgz
- Published checksum: https://download.moodle.org/download.php/direct/stable503/moodle-5.3.1.tgz.sha256
- Download independently SHA256verified820ee2bcd89acc6b91df255b2010bbbab108f29952ab78895a79c4feabf541e7.
- Source COPYING.txt is GPLv3; sourceheader permits GPLv3or later. Bundledcomponents retain theirlicenses. See https://github.com/moodle/moodle/blob/v5.3.1/COPYING.txt.
- PHP8.4FPMAlpine official image pinnedc0e41e0c856bf97b2e749f40a804031ce938d0d496c4c7d91ad416d993172826; PHPlicense3.01 and nginxBSD2clause componentlicenses. https://www.php.net/license/ and https://nginx.org/LICENSE
- PostgreSQL17Alpine official image pinnedf9cf3e1f0066f0eb0c48707d864f0ac5941e9ff454a072077d97a4d278d07d73; PostgreSQLlicense https://www.postgresql.org/about/licence/. OScomponents have individuallicenses.
- Port18701loopback wasfree. Subnet10.253.243.0/28 absent from Docker networkinventory beforecreation.
- New project nikway-academy-moodle; fresh moodle-db/moodle-data volumes. ExistingAcademybaseline/content volumes nevermounted.

DependencyAPKpackages resolve from upstreamAlpinerepositories atbuildtime; base+Moodlesource pinned, but build is notbit-for-bit reproducible. License inventory is not a full transitive legal review. Local HTTP endpoint and generated bootstrapadmin are development-only; no release authorization implied.

Initial officialPG17 had27High/Critical package findings (libxml2 plus bundledgosuGo runtime); derived image replaces gosu with actual distro su-exec0.3-r0 and upgrades libxml2to2.13.9-r3. Initial PHP8.4ApacheDebian candidate had103High/Critical findings, so AlpineFPM/nginx candidate selected instead. No scanner suppression or vulnerability metadata removal. First PGderivedbuild expected a historicalsu-execsymlink whichPG17doesnotinclude; removed that obsoleteunlink after inspectingimage. First CLIinstall wrapper omitted$_SERVERargv and licenseoptionwasnotreceived; fixedargv forwarding, thenfullinstallcompleted.

## Operational corrections verified

The initial nginx/FPM configuration forwarded internal port80, causing Moodle's canonical URL check to redirect the login page to itself. A validated numeric host-port map now forwards the external port, preserving both primary18701 and restore-probe18702. The first capture name conflicted with a new nginx built-in variable and failed startup; renamed it to `moodle_host_port`. Final login returns HTTP200 and nonexistent PHP scripts return404. The healthcheck follows redirects with a five-redirect limit. Moodle data ownership was migrated only inside its new volume from Debian www-data33 to Alpine www-data82.

Final package scans: see `security.json`. These do not cover every PHP application advisory because Trivy found no Composer lock target in the release archive. Local scans do not authorize production release.
