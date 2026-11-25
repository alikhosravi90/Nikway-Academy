# Bilingual knowledge taxonomy (draft)

| Type | فارسی | English |
|---|---|---|
| Foundation | فلسفه یادگیری | Learning Philosophy |
| Semantic | هستی‌شناسی | Learning Ontology |
| Semantic | واژه‌نامه | Glossary |
| Semantic | طبقه‌بندی | Taxonomy |
| Science | علوم یادگیری | Learning Science |
| Design | معماری یادگیری | Learning Architecture |
| Design | معماری شایستگی | Competency Architecture |
| Design | برنامه درسی | Curriculum Architecture |
| Design | طراحی آموزشی | Instructional Design |
| Experience | طراحی تجربه یادگیری | Learning Experience Design |
| Production | مهندسی محتوا | Content Engineering |
| Measurement | مهندسی سنجش | Assessment Engineering |
| Measurement | تحلیل یادگیری | Learning Analytics |
| Assurance | تضمین کیفیت | Quality Assurance |
| Governance | حاکمیت آموزشی | Learning Governance |
| Improvement | بهبود مستمر | Continuous Improvement |

Entity candidates: Source, Evidence, Claim, Concept, Theory, Standard, Framework, Competency, LearningOutcome, Curriculum, Program, Course, Module, Lesson, LearningObject, Assessment, Rubric, Credential, LearnerEvent. Relationship candidates: cites, supports, contradicts, defines, prerequisiteOf, teaches, assesses, derivesFrom, versionOf, translatesTo, supersedes.
No ontology is yet formally approved; RDF/SKOS/OWL adoption requires schema and query tests.


## Semantic governance supplement / راهبری معنایی
Learning Engineering is labelled **مهندسی یادگیری** in the proposed glossary;
**مهندسی نظام آموزشی** is retained as the owner's supplied contextual label.
Their equivalence and scope are **pending verification** by a bilingual domain reviewer.
Existing labels above remain unchanged; no formal translation or ontology approval is claimed.

| Stable domain ID | فارسی | English |
|---|---|---|
| LE-PHI | فلسفه یادگیری | Learning Philosophy |
| LE-ONT | هستی‌شناسی یادگیری | Learning Ontology |
| LE-GLO | واژه‌نامه | Glossary |
| LE-TAX | طبقه‌بندی | Taxonomy |
| LE-SCI | علوم یادگیری | Learning Science |
| LE-ARC | معماری یادگیری | Learning Architecture |
| LE-COM | معماری شایستگی | Competency Architecture |
| LE-CUR | معماری برنامه درسی | Curriculum Architecture |
| LE-INS | طراحی آموزشی | Instructional Design |
| LE-LXD | طراحی تجربه یادگیری | Learning Experience Design |
| LE-CON | مهندسی محتوا | Content Engineering |
| LE-ASM | مهندسی سنجش | Assessment Engineering |
| LE-ANA | تحلیل یادگیری | Learning Analytics |
| LE-QUA | تضمین کیفیت | Quality Assurance |
| LE-GOV | حاکمیت آموزشی | Learning Governance |
| LE-IMP | بهبود مستمر | Continuous Improvement |

The original Type column is a grouping label, not a unique key.
Proposed records require id, preferredLabel.fa, preferredLabel.en, definition.fa,
definition.en, aliases, domainIds, sourceEvidenceIds, revision, reviewStatus and reviewer.
Definitions and translations remain draft until reviewed; missing translations are explicit,
never silently replaced by another language. IDs survive label changes and are never reassigned.
Synonyms are recorded as aliases; homonyms receive different IDs with scope notes.
Additional README domains (standards, frameworks, methodologies, models, patterns,
templates, protocols, evidence and cases) use these domain IDs plus an entity/content kind;
they are not silently dropped or assumed to be equivalent domains.

Relation direction must be explicit: Object teaches Outcome; Assessment assesses Outcome;
Claim cites Source; Evidence supports or contradicts Claim; Object derivesFrom Object;
older revision is superseded by newer revision. Translation links name source and target locale
and revision. Prerequisite cycles are invalid for a publishable learning path; other graph cycles
require relation-specific rules. Domain coverage and formal relation constraints remain proposed.
