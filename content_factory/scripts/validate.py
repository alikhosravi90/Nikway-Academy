"""Evaluate every original gate against recorded tests and live demo/probe evidence."""
import json
from pathlib import Path
from datetime import datetime,timezone
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]; ev=root/'evidence'
xml=ET.parse(ev/'tests.xml'); cases=xml.findall('.//testcase')
passed={c.attrib['name'] for c in cases if not any(c.find(x) is not None for x in ('failure','error','skipped'))}
failed=[c.attrib['name'] for c in cases if c.attrib['name'] not in passed]
demo=json.loads((ev/'local-http-demo.json').read_text()); probe=json.loads((ev/'learning-os-probe.json').read_text())

def gate(id,status,tests,remaining):
    missing=sorted(set(tests)-passed)
    return {'id':id,'status':'FAIL' if missing else status,'testEvidence':tests,'missingOrFailed':missing,'remaining':remaining}

gates=[
 gate('CF-G0','PARTIAL',[], 'User approved architecture in current chat; full original assistant source remains unavailable. Source fidelity is not upgraded by approval.'),
 gate('CF-G1','PARTIAL',['test_contract_rejects_unknown_fields_and_invalid_answer','test_broken_lineage_and_missing_source_rejected','test_package_has_four_outputs_safe_html_and_scoring'],'External outcome/competency authority and human pedagogy review pending.'),
 gate('CF-G2','PARTIAL',['test_review_requires_independent_reviewer_and_rights','test_pipeline_unknown_rights_fails_check'],'Only synthetic internal-trial material; human rights/provenance review and real-corpus permissions pending.'),
 gate('CF-G3','PASS_LOCAL',['test_restore_rehydrates_matching_metadata_objects_and_search','test_backup_rejects_missing_object_and_reports_orphan','test_pipeline_failure_rolls_back_revision'],'Local snapshot restore only; no production RPO/RTO agreement, S3 or durability certification. Dedicated backup-tamper negative tests deferred.'),
 gate('CF-G4','PASS_LOCAL',['test_two_course_reuse_pins_revisions_and_withdrawal','test_concurrent_revision_writers_only_one_wins','test_transitive_dependency_withdrawal_blocks_candidate'],'Bounded local versioning/reuse demonstrated; broader localization and semantic review pending.'),
 gate('CF-G5','PASS_LOCAL',['test_tenant_rls_and_search','test_api_auth_roles_and_forbidden_tenant','test_api_token_revocation_and_payload_bound','test_revoked_and_expired_credentials'],'Local-token and database boundary only; production OIDC, enrollment integration and penetration assessment pending.'),
 gate('CF-G6','PARTIAL',['test_consumer_replay_and_withdrawal_at_delivery','test_consumer_rejects_schema_digest_foreign_tenant_and_outage','test_consumer_rejects_package_rehashed_by_attacker','test_delivery_rejects_wrong_candidate_from_routing_mixup'],'Custom local manifest/ZIP round trip only; QTI/CASE/CC/LTI adapters and event transport not implemented.'),
 gate('CF-G7','PARTIAL',['test_consumer_replay_and_withdrawal_at_delivery'],'Local consumer passes; live Academy is reachable but has no Content Factory ingestion contract. No live end-to-end learning integration.'),
 gate('CF-G8','PARTIAL',['test_package_has_four_outputs_safe_html_and_scoring'],'Agent browser inspection confirms Persian RTL/structure. Human editorial review, assistive-technology testing and accessibility certification pending.'),
 gate('CF-G9','PARTIAL',['test_pdca_enforces_order_and_requires_review','test_no_release_endpoint'],'Local synthetic acceptance only. Real learner pilot, accountable human approval and release decision pending.')]
local_ok=not failed and all(g['status']!='FAIL' for g in gates) and demo['sameRevisionInTwoCourses'] and demo['pinnedAfterUpdate']
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'tests':{'total':len(cases),'passed':len(passed),'failed':failed},'decision':'GO_LOCAL_SYNTHETIC' if local_ok else 'NO_GO','production':'NO_GO','merge':'NOT_PERFORMED','release':'NOT_PERFORMED','gates':gates,'liveLearningOS':probe['result'],'evidence':['tests.xml','full-suite.log','local-http-demo.json','learning-os-probe.json','review.md','visual-check.json']}
(ev/'gates.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'decision':report['decision'],'production':report['production'],'tests':report['tests'],'gates':{g['id']:g['status'] for g in gates}},indent=2))
if not local_ok: raise SystemExit(1)
