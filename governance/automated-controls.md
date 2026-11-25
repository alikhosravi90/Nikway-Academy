# Automated Engineering Controls

Status: proposed control catalog; no tools installed or checks executed by this document.

| ID | Category | Control | Candidate tool | Activation |
|---|---|---|---|---|
| CTL-01 | Docs | Markdown syntax/style | markdownlint | Now |
| CTL-02 | Docs | Broken links | Lychee | Now |
| CTL-03 | Docs | Technical prose | Vale | Now |
| CTL-04 | Docs | Metadata/template | Python validator | Now |
| CTL-05 | Docs | Unique IDs | Python validator | Now |
| CTL-06 | Architecture | Dependency boundaries | Dependency Cruiser | Source available |
| CTL-07 | Architecture | Cyclic imports | Madge | Source available |
| CTL-08 | Architecture | Fitness rules | ArchUnitTS / Import Linter | Source available |
| CTL-09 | Architecture | Diagram syntax | Mermaid CLI | Now |
| CTL-10 | Architecture | ADR traceability | Python validator | Now |
| CTL-11 | Contracts | JSON Schema | AJV | Schema available |
| CTL-12 | Contracts | YAML syntax | yamllint | YAML available |
| CTL-13 | Contracts | OpenAPI | Spectral | Contract available |
| CTL-14 | Contracts | AsyncAPI | AsyncAPI CLI | Contract available |
| CTL-15 | Contracts | Semantic constraints | pySHACL | RDF/shapes available |
| CTL-16 | Contracts | Compatibility | Pact / oasdiff | Contracts and baseline available |
| CTL-17 | Security | Secrets | Gitleaks | Now |
| CTL-18 | Security | Dependency vulnerabilities | Trivy | Manifests/images available |
| CTL-19 | Security | License inventory | ScanCode | Now |
| CTL-20 | Security | Policy checks | OPA / Conftest | Policies available |
| CTL-21 | Security | Static code security | CodeQL | Supported source available |
| CTL-22 | Governance | Issue/PR linkage | GitHub Actions | Now; bootstrap exceptions documented |
| CTL-23 | Governance | Commit convention | Commitlint | Convention approved |
| CTL-24 | Governance | Evidence completeness | Python validator | Now |
| CTL-25 | Governance | Merge gate | GitHub Rulesets | Checks configured and owner approved |

## Methods
Static, semantic, contract, policy-as-code, architecture fitness functions, traceability and AI-assisted review with human oversight.

## Rollout
Start with documentation, IDs, links, diagrams, secrets and traceability. Pin tool versions, review licenses, use least-privilege CI and test each control against positive and negative fixtures. Record PASS/FAIL/NOT_APPLICABLE/NOT_RUN separately; missing artifacts never count as PASS. Existing historical evidence must not be rewritten to satisfy lint rules. External link failures may require manual review. Activate source and contract checks when artifacts exist. Enforce merge gates only after checks are proven and approved. No merge or installation authorized.
