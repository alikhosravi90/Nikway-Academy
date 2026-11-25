# LE-04 — پروتکل پایلوت آموزشی / Educational pilot protocol
Version 0.1.0; status: PREPARED / NOT RUN. No learners contacted or enrolled.
User approved continuing preparation on 2026-11-25; no named expert or pilot lead was supplied.

## Research question / پرسش
Can participants demonstrate bounded PDCA reasoning on a new task after instruction,
and apply that reasoning to a permitted workplace problem? This pilot estimates feasibility
and descriptive change; it does not establish causal effectiveness.
آیا فراگیر پس از آموزش می‌تواند در مسئله‌ای تازه استدلال PDCA را نشان دهد و آن را
در مسئله‌ای مجاز به‌کار ببرد؟ تغییر نمره به‌تنهایی اثبات علیت نیست.

## Proposed design (requires human sign-off before recruitment)
- Adult volunteers with an improvement-related role; no employment performance decisions.
- Proposed feasibility cohort: 8–12; convenience sample, not a powered efficacy trial.
- Pre-test before seeing lesson/answer key, 20 minutes; instruction/practice 45 minutes;
  post-test within 24 hours, 20 minutes; practical transfer review 14 days later.
- Counterbalance original forms A/B: half A-pre/B-post, half B-pre/A-post. Assignment log
  remains private. No equivalence claim until expert review and pilot evidence.
- Same four-criterion 0..2 rubric, pinned version, at every phase. Two raters independently
  score blinded scripts; preserve both scores and reconcile disagreements before analysis.
- Proposed feasibility targets: >=80% complete pre/post; record all missingness reasons;
  report paired change and criterion distributions without invented success threshold.
  Existing 8/8 mastery suggestion remains unvalidated, not a certification cutoff.
- Freeze the signed protocol, task/rubric versions and analysis plan before first enrolment.

## Prerequisites and stop conditions
LE-01 clears exact intended content use; LE-02 human domain/language reviewers approve forms,
rubric anchors and lesson; LE-03 authorized delivery path is available if platform used.
Owner names pilot lead, data custodian and two raters, and approves recruitment/consent and
retention period. Stop recruitment on access/privacy incident, invalid content rights,
withdrawn authorization, or inability to preserve voluntary participation.

## Learner protection / حفاظت از فراگیر
Provide plain-language purpose, tasks, time commitment, voluntary participation, withdrawal
route, intended data use and contact person before consent. No benefit or risk-free promise.
Do not put names, emails, consent forms, raw scripts, employer details or person-code mapping
in GitHub. A designated custodian stores them in an approved restricted location.
Retention duration, withdrawal deadline and deletion process must be filled and approved,
not assumed. The analyzer cannot verify consent or deidentification.

## Analysis
Score totals 0..8 from complete four-criterion ratings. Analyze paired pre/post observations;
report pre-only/post-only and transfer counts. Never substitute missing with zero.
Report completion denominators, scores per criterion, individual paired changes (privately),
mean/median and range as appropriate. Public output must aggregate safely and undergo owner
privacy review; small-group reidentification is possible even without names.
Report practice effects, selection bias, form differences, rater disagreement, ceiling effects
and lack of control group. Negative/no change is a valid result. Do not fabricate observations.
Transfer requires a real permitted artifact plus human rubric review; its mere submission
or presence in a file does not demonstrate success.

## Current execution evidence
Only automated synthetic analyzer tests were run. `dataset-empty.json` is intentionally empty.
`synthetic-demo.json` is a software fixture, not a participant dataset.
Run: `python3 missions/LE-04/evaluate.py /approved/private/path/scores.json` from learning-engineering/.
The command prints descriptive results only; it cannot approve scientific, ethical or owner gates.

## Human sign-off (blank)
Owner: UNASSIGNED; pilot lead: UNASSIGNED; data custodian: UNASSIGNED.
Domain reviewer: UNASSIGNED; bilingual reviewer: UNASSIGNED; raters: UNASSIGNED.
Approved protocol hash: PENDING; authorized date/window: PENDING.
Recruitment authorized: NO; real data collection begun: NO; outcomes: NO DATA.
