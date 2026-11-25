# Custom image maintenance and license evidence

Checked2026-11-25. This is a locally maintained build, not a vendor-supported Keycloak release. The application remains Keycloak26.8.2, with an explicit dependency-management change to Guava33.7.2 and a Temurin21 Alpine runtime. Our maintainers own dependency monitoring, compatibility regression, rebuilds, scanner freshness, notices, and the eventual return to a suitable upstream release. No production support entitlement was purchased or implied.

| Component | Upstream license evidence | Scope |
|---|---|---|
| Keycloak26.8.2 | [Apache2.0 license at release tag](https://github.com/keycloak/keycloak/blob/26.8.2/LICENSE.txt) | Source archive includes LICENSE.txt; distribution assembly retains upstream license material. |
| Guava33.7.2 | [Apache2.0 license at release tag](https://raw.githubusercontent.com/google/guava/v33.7.2/LICENSE) | Dependency version change is documented in build recipe and evidence. |
| Temurin21 | [Adoptium FAQ](https://adoptium.net/docs/faq/) | No-cost binaries under GPLv2 with Classpath Exception; included component notices remain relevant. |
| Alpine runtime packages | Installed package metadata and each package's upstream license | The base is not one uniformly Apache-licensed work. Bash and other packages retain their own terms. |

This records primary license provenance for changed major components, not an exhaustive redistribution/legal clearance of every transitive package. Existing image/package notices must be retained. No binary image was published externally by this task. Maven is a build-stage tool and is absent from the final runtime image.

A zero High/Critical Trivy result means no findings at those severities in the selected OS/JAR scan with the recorded database snapshot. It does not establish absence of unknown vulnerabilities, application-logic defects, insecure deployment settings, or future advisories. Upstream integration tests were skipped for the bounded rebuild; the local Academy tests and their exact image identities are separate evidence. Both development-mode HTTP and loopback-only deployment remain local-MVP boundaries.
