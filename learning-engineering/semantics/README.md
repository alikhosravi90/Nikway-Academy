# Operational semantics — proposed v0.1.0

این بسته تعریف‌ها و ترجمه‌های پیشنهادی را عملیاتی می‌کند؛ تأیید متخصص یا اثربخشی آموزشی نیست.

The 16 domain identifiers preserve TAXONOMY.md. `ontology.json` defines a local,
versioned vocabulary of ten record kinds and directional relation domain/range rules.
`glossary.json` contains original operational definitions with proposed Persian labels.
These are authoring assets, not an OWL/SKOS implementation or a formally approved ontology.
Additional standards/frameworks/methodologies remain possible content topics classified
by existing domain IDs; this sample neither adopts nor evaluates those references.

## PDCA chain and alignment

LE-CARD-PDCA explains LE-CONCEPT-PDCA; LE-COMP-PDCA develops that concept;
LE-OBJ-PDCA targets that competency; LE-CUR-PDCA includes that objective;
LE-CONTENT-PDCA specifies content for it; LE-ASSESS-PDCA assesses it using
LE-RUBRIC-PDCA. Every reference binds version 0.1.0. Provenance resolves through
LE-EVD-PDCA and LE-SRC-ASQ-PDCA supplied separately by the source curator.

The original fictional handover exercise has 12/100 baseline errors and 5/100 trial
errors: 12%, 5%, and a decrease of 7 percentage points. These are invented exercise
inputs, not observations. The proposed target of at most 6% is met in the invented
numbers; that does not establish causality. Four rubric criteria cover plan, do,
check and act with 0/1/2 anchors and an explicitly unvalidated 8/8 pass threshold.
Partial fulfillment scores 1, missing/incorrect fulfillment scores 0, and complete
fulfillment scores 2. Assessor calibration and inter-rater reliability are pending.
No learner data, actual outcome, evaluation result or effectiveness claim is included.

## Meaning and graph constraints

Relation direction is subject to target. `derived-from` links a card to Evidence;
`derivesFrom` is a distinct same-kind record lineage link. `supersedes` points from
new to old revision. Same-kind lineage and prerequisite constraints must not be
mistaken for evidence support. No causal relation is defined. Duplicate identifiers
are not aliases; label changes retain identifiers. New meanings require new IDs;
new revisions preserve old immutable references. Prerequisite and supersession graphs are acyclic; other cycles require
relation-specific review. Supersession names the same stable ID at an older version.
The v0.1 validator pins its own supported vocabulary, so editing ontology JSON alone
does not change executable acceptance rules. Change both through reviewed revisions.

## PDCA / PDSA limits and G2

PDCA is summarized from the separately identified ASQ evidence. PDSA is only a
proposed glossary expansion; the research register includes the Deming Institute
source LE-SRC-029, but no canonical PDSA Source/Evidence record or approved equivalence
finding is supplied. Do not substitute the terms, infer attribution,
or transfer evidence between them without additional source and domain review.
The phrase مهندسی نظام آموزشی is retained as a contextual alias supplied in the
baseline; equivalence with مهندسی یادگیری remains pending expert review.

G2 remains **pending verification**: a bilingual domain expert must review meanings,
scope, translations, relation direction/ranges, alias collisions and the sample's
instruction/assessment alignment. Reviewers and review dates remain null. All
records remain proposed; rights remain pending verification with UNKNOWN license
and empty allowedUses. Source citations support provenance, not permissions or
learning effectiveness. No publishing or delivery authorization follows from local
structural validation. G4 still requires an approved evaluation design and actual
learner evidence. Extending to a second domain requires its own sources, evidence,
competencies, objectives and reviewed rubric; PDCA-specific values are not defaults.
