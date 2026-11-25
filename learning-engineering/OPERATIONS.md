# Local operation / راهنمای استفاده محلی

This implementation adds an offline authoring/validation system to the preserved design documents.
No server, LMS, database, external API or production tenant is needed. Run from this folder.
Python 3.10+ on Linux/macOS (file locking uses fcntl); Windows is not tested.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m engine.cli validate records
.venv/bin/python -m engine.cli search records 'چرخه'
.venv/bin/python -m engine.cli search records 'PDCA'
.venv/bin/python -m engine.cli render records
.venv/bin/python -m engine.pilot
```

Tests also run with an existing Python environment containing the pinned jsonschema dependency.
Installation is local; no service is started. Tests use synthetic records and temporary directories.
`validate --delivery` deliberately exits 1 for the present repository: all rights are pending and
all canonical records remain proposed. Validation is not scientific approval.

## Accumulate and review / انباشت و بازبینی

1. Add a UTF-8 JSON source with title/summary in fa and en; identify its exact source locator,
   source-fact verification scope and rights separately. Add Evidence linked to exact source revision.
2. Author concepts, cards and learning designs using the record schema. Do not place benchmark
   register JSON or schemas inside records/: that directory contains only canonical records.
3. Run validation, semantic tests and search. IDs are never reused for another concept.
4. For a new revision, keep the old JSON and use a new filename. References stay pinned;
   changing a record does not automatically repoint its consumers. Review downstream impact.
5. Accumulate into a **new** output path; exact replay is harmless, conflicts are refused:

```sh
python3 -m engine.cli accumulate records /path/to/candidate.json /path/to/new-batch.json
python3 -m engine.cli review records LE-CONCEPT-PDCA 0.1.0 0.2.0 /path/to/reviewed-batch.json \
  --reviewer 'actual-reviewer-label' --reviewed-at '2026-11-25T12:00:00Z'
```

The review command only records a declared proposed→reviewed transition in a new immutable
revision. Use an actual review time, not the illustrative timestamp. It refuses same-author review,
version overwrite and skipped state. It does **not** authenticate a person, clear rights or approve
release. No canonical record has been advanced by these examples. An actual trusted approval
workflow and G5 acceptance remain external. Unknown and pending values are not silently filled.
Keep generated batches outside records/ until integrating only the new versions to avoid duplicates.

## Offline exchange / تبادل محلی

```sh
python3 -m engine.cli export records /path/to/pdca-package.json --package-id pdca-reference --revision 0.1.0
python3 -m engine.cli import /path/to/pdca-package.json /path/to/factory-store.json --consumer content-factory
python3 -m engine.cli import /path/to/pdca-package.json /path/to/os-store.json --consumer learning-os
```

Output paths are explicit; export/review/accumulate refuse overwrites. Import uses a lock and atomic
replacement for a local store. Exact replay retains the receipt; digest mismatch, revision conflict
within or across packages, malformed records and invalid scope are rejected before acceptance.
Both adapters are **local consumer fixtures**, not connections to existing applications.
Every receipt is quarantined, including caller-declared approved records: a trusted adapter and
owner acceptance are required for real delivery. This prevents accidental promotion of metadata
into authorization. Do not use fixture context as authentication or a tenant boundary.

## Extending beyond PDCA

Existing ten kinds are not PDCA-specific. Add another domain's records with new IDs and evidence,
keeping all required fa/en fields. New domain IDs must be added consistently to ontology and schema;
new kinds or relations need versioned schema changes, validators and negative tests.
The glossary is extensible; tests check consistency rather than a permanently fixed entry count.
Search normalizes Arabic/Persian yeh/kaf and spacing; it is local substring search, not semantic IR.
Markdown is a derived index, not canonical evidence or a rendered accessibility certification.
No NLP translation accuracy, scoring validity or learner effectiveness claim is made.

## Evidence map

- `records/`: ten canonical PDCA records; source/evidence through assessment plus rubric.
- `semantics/`: reference ontology and 13 original bilingual glossary definitions, all proposed.
- `research/references.json`: 29 candidate reference entries, source facts and rights separately.
- `schemas/`: record, package, ontology and glossary JSON Schema.
- `engine/`: one shared validator/search renderer, semantics checks, review, exchange, CLI, pilot.
- `tests/`: reproducible positive and adversarial checks.
- `evidence/`: generated local pilot receipt/package/index and test receipt.
- `QA-REVIEW.md` and `GO-NO-GO.md`: independent review and scoped gate decision.
