# NIKWAY Learning Engineering Knowledge Base
Status: DRAFT / architecture proposal (2026-11-25); NOT an accepted standard or deployed service.

## Purpose
Build an independently versioned, traceable, bilingual (fa/en) body of knowledge for engineering learning. This is independent of Learning OS (delivery platform) and Content Factory (production), linked via explicit contracts.

## Knowledge domains
Philosophy; Ontology; Glossary; Taxonomy; Learning Science and Theories; Standards; Frameworks; Methodologies; Reference Models; Competency Architecture; Curriculum Architecture; Instructional Design; Learning Experience Design; Content Engineering; Assessment Engineering; Learning Analytics; Quality Assurance; Governance; Patterns; Templates; Protocols; Evidence; Case Studies.

## Reference operating loop
Discover sources -> verify provenance and usage rights -> extract claims/concepts -> classify/relate -> peer review -> version/publish -> apply in curricula -> assess effectiveness -> update.

## Preservation & governance
Immutable source citations, source author/date/version/URL/access timestamp, permissions, evidence level, status (proposed/reviewed/approved/deprecated), owner, multilingual translations and semantic identifiers. Never treat LLM-generated content as verified evidence. Merge into main requires review.

## Interfaces
Learning Engineering defines learning objectives, competencies, curriculum maps, pedagogy, assessments and rubrics; Content Factory produces versioned content objects; Learning OS serves those objects and emits learning evidence. Identifiers and schema are versioned independently. No LMS-specific authoring lock-in.

See BENCHMARK.md, TAXONOMY.md, CONTRACT.md and ROADMAP.md.


## Audit supplement — 2026-11-25
This supplement preserves the original proposal above. Repository documents at
`d8d3347a708749f545eb3f2ac7e339db3f277b1f` are the source baseline designated by the owner.
New details below are proposed elaborations, not recovered quotations from the conversation.

### Proposed knowledge architecture / معماری پایگاه دانش
| Layer | Responsibility | Canonical records |
|---|---|---|
| Source registry / ثبت منابع | Provenance, exact edition and rights review | Source, permission record |
| Evidence / شواهد | Locate claims in sources; record limitations and contradictions | Evidence, Claim |
| Semantic / معنایی | Stable bilingual concepts and explicit relations | Concept, glossary, taxonomy |
| Learning design / طراحی یادگیری | Connect competencies, outcomes, activities and assessment | Curriculum, Outcome, Rubric |
| Reusable content / محتوای بازاستفاده‌پذیر | Versioned objects independent of presentation | LearningObject, derivative manifest |
| Evaluation / ارزیابی | Feed reviewed findings back into revisions | Aggregate evaluation, change record |

Markdown documents and a future structured registry are proposed canonical authoring assets.
Search indexes, graphs and LMS views are derived projections; none is implemented here.
A citation is not evidence of effectiveness, and a taxonomy relationship is not proof of causality.
Raw learner records and private source documents must not enter this repository.
The proposed storage layout is `sources/`, `evidence/`, `concepts/`, `designs/`,
`objects/`, and `evaluations/`; these directories are not claimed to exist.
A record links Source -> Evidence -> Claim/Concept -> Outcome -> Object/Assessment -> Evaluation.
Each link names stable ID and immutable revision; contradictory findings remain traceable.

### Reading map
- [Benchmark register](BENCHMARK.md)
- [Bilingual taxonomy](TAXONOMY.md)
- [Accumulation workflow](ACCUMULATION.md)
- [Roadmap and gates](ROADMAP.md)
- [Content exchange outline](CONTRACT.md)
- [Audit and six-part coverage](AUDIT.md)

پذیرش این بسته صرفاً پذیرش مستندات پیشنهادی است؛ تأیید علمی، مجوز بازنشر،
انطباق استانداردها، پیاده‌سازی و نتایج یادگیری را اثبات نمی‌کند.
