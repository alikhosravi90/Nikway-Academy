# Accumulation workflow / گردش انباشت دانش
Status: proposed operating procedure; not an implemented pipeline.

## Record lifecycle
1. **Discover / کشف** — Curator records a candidate source with stable source ID, title,
author/issuer, URL, edition, discovery date and intended use. Unknown fields are UNKNOWN.
Deduplicate by canonical URL/identifier and edition; preserve alternate citations.
2. **Verify / بررسی** — Source reviewer records source location, authority, exact claim locator,
limitations and contradictions. Rights reviewer records evidence and permitted uses separately.
Unverified references/licensing remain `pending verification`.
3. **Extract / استخراج** — Create an original claim/concept card; distinguish quotation,
paraphrase, inference and proposal. No protected full text is imported without permission.
4. **Classify / طبقه‌بندی** — Assign domain/entity IDs from TAXONOMY.md, bilingual labels,
relations and exact evidence revisions. Missing definitions or translation review stays visible.
5. **Review / بازبینی** — A reviewer other than the author checks evidence, semantic consistency,
rights, translations and links. Record reviewer, date, disposition and rationale.
6. **Version / نسخه‌بندی** — Approver assigns immutable revision and approval scope.
A repository commit can hold drafts; it does not authorize publishing learning content.
7. **Apply / کاربرد** — Bind approved revisions to outcomes, content objects and assessments
through CONTRACT.md. Record consumers so change impact can be traced.
8. **Evaluate / ارزیابی** — Record measured findings and limitations; open a revision proposal,
preserving previous evidence, contradictory claims and historical consumers.

## State rules
Workflow state: proposed -> reviewed -> approved -> deprecated.
"reviewed" records a completed review, not necessarily approval; adverse findings return the
candidate to proposed with reasons. Only an accountable approver may approve.
Verification state (per reference and license): pending verification / verified / rejected.
Approval requires appropriate verified evidence and rights, bilingual/semantic review and
resolved references. A changed approved item creates a new proposed revision; the old revision
remains immutable. Deprecation carries reason, replacement ID if any, and affected consumers.
Source withdrawal or license concerns suspend further export pending review; historical records
are retained subject to applicable retention rules, not silently overwritten.

## Minimum knowledge card template
```yaml
id: LE-CARD-EXAMPLE
revision: 0.1.0
kind: Concept
title: {fa: "نمونه پیشنهادی", en: "Proposed example"}
domainIds: [LE-IMP]
definition: {fa: UNKNOWN, en: UNKNOWN}
claimKind: proposal
sourceEvidenceIds: []
relations: []
referenceStatus: pending verification
licenseStatus: pending verification
licenseEvidenceRefs: []
allowedUses: []
workflowState: proposed
author: UNASSIGNED
reviewer: UNASSIGNED
reviewedAt: null
changeReason: Initial draft
supersedes: null
```
This is an incomplete synthetic template, not approved knowledge or a validated schema.
Each evidence record needs source ID/revision, page/section locator, claim, evidence type,
limitations, verification date and reviewer. Each source needs bibliographic and rights fields
listed in BENCHMARK.md.

## Batch review and accumulation controls
Curator proposes a bounded batch; reviewer checks duplicates, orphan references, translation gaps
and contradictory evidence; approver records acceptance or rejection. Frequency and batch size
are owner decisions (TBD). Maintain a change log with record IDs, reason, evidence and impact.
Report reviewed/approved counts separately from total collected count, plus unresolved rights,
missing citations and affected consumers. A larger collection alone is not progress in quality.
