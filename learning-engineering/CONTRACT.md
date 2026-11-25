# Learning Engineering <-> Content Factory <-> Learning OS
Status: proposed, NOT implemented.

## Minimal object contract
Each learning object has stable id, semanticVersion, locale, type, title, learningOutcomeIds[], competencyIds[], prerequisiteIds[], sourceEvidenceIds[], license, accessibility, reviewStatus, checksum, mediaRefs[], publishedAt and deprecatedAt (optional).
Each assessment links outcomeIds, rubricId, scoring specification and evidence requirements.
A curriculum defines ordered program/course/module/lesson references; references bind explicit immutable versions or declared compatible ranges.

## Ownership
Learning Engineering owns competency/outcome definitions, curricula and assessment intent; Content Factory owns authored artifacts, media derivatives, quality control and licenses; Learning OS owns delivery, access control, enrollment and learning event capture.

## Acceptance
Validate JSON schema, referential integrity, localization, content provenance, licensing, accessibility, export/import, and no cross-tenant leaks. Content may be authored independently of the LMS. Version changes must not silently rewrite historical student results.
