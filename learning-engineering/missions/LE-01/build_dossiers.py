import json,pathlib,collections,hashlib
p=pathlib.Path(__file__).parent
src=p.parents[1]/'research/references.json'
refs=json.loads(src.read_text())['references']
E={}
def ev(k,url,loc,note,kind='official page via web search/open'):
 E[k]={'id':k,'url':url,'locator':loc,'observedAt':'2026-11-25','method':kind,'observation':note}
ev('iso','https://www.iso.org/copyright.html','Copyright; All Rights Reserved','ISO asserts ownership of its publications and requires written permission for reproduction; the page also reserves AI uses.')
ev('ims','https://www.1edtech.org/policy/how-to-use-1edtech-documents','sections 7, 8, 10, 12','As-is document redistribution is permitted. Distributed/commercial derivatives require agreement; translation requires a signed agreement, with nonmember distribution through 1EdTech. Implementation is distinct from document reuse.')
ev('imslic','https://www.1edtech.org/standards/specification-license','sections 2–5','Copyright attributed to 1EdTech except noted exceptions; implementation license is conditional; document derivatives are not granted by this license alone. It applies to specifications linking to it.')
ev('unesco','https://www.unesco.org/en/terms-use','sections 5 and 7; last update 15 September 2026','Occasional individual noncommercial educational/research consultation, citation, translation and reproduction permitted subject to attribution and material-specific conditions; commercial and broader reuse require an applicable license or authorization.')
ev('routledge','https://www.routledge.com/contacts/rights-and-permissions/','opening; Books Permissions; Rights Licensing','Written reproduction consent required; translation rights are separately administered; anthology extracts and figures may have other owners.')
ev('atd','https://www.td.org/terms-and-privacy','Terms and Conditions 1–2','Personal downloading/printing with notices is permitted. Modification, translation, distribution and derivative use are restricted; rights can belong to ATD or licensors.')
ev('asq','https://asq.org/terms-of-use','sections 3 and 9(a–b)','Site access does not grant IP rights. Copying, translating, adapting and distributing require written consent; site use is personal and noncommercial.')
ev('asqpermission','https://asq.org/copyright/reprint-permission','Reprint Permission','Requests are reviewed for the specified use; written permission and possibly fees are required. No request was submitted.')
ev('deming','https://deming.org/about-us/f-a-qs/','Copyrights and Permissions','PDSA reprinting specifically requires a request and approval. Institute publications cannot be publicly disseminated without permission; logo separately reserved.')
ev('solar','https://www.solaresearch.org/about/what-is-learning-analytics/','footer lines 205–206; video lines 162–164','Footer licenses site content CC BY 4.0 except noted items. Embedded video is expressly Standard YouTube License; exclude it from the CC scope.')
ev('ccby','https://creativecommons.org/licenses/by/4.0/','You are free to; Under the following terms','Sharing and adaptation including commercial purposes are permitted with attribution, license link and change indication; no endorsement or additional restrictions. Deed is a summary, legal-code review remains necessary.')
ev('xapi','https://github.com/adlnet/xAPI-Spec/blob/master/LICENSE','LICENSE sections 2 and 4','Apache-2.0 copyright grant includes derivatives and redistribution with license, retained notices and change notices. Commit not pinned; does not cover IEEE xAPI 2.0 by implication.')
ev('cmi','https://github.com/AICC/CMI-5_Spec_Current/blob/quartz/LICENSE','Apache License 2.0; sections 2 and 4; repository README release','License text inspected on quartz branch; repository identifies Quartz first edition June 2016. Exact commit and third-party notices remain to be reviewed.')
ev('lebok','https://lebok.wiki/','open result: zero readable lines','Direct official page returned no readable text. No rights conclusion possible.','official open unsuccessful for content')
ev('cast','https://udlguidelines.cast.org/more/downloads/','Version 3.0 (2024); translations','CAST identifies version 3.0 and published translations. No affirmative reuse license verified; available downloads do not grant reuse rights.')
ev('aect','https://www.aect.org/aect/about/aect-definition','definition and 2023 task-force credit','Official definition page inspected; no affirmative license verified in returned content.')
ev('ieee','https://www.ieee.org/about/help/site-terms-conditions.html','direct open failed','Authoritative terms URL identified but direct fetch restricted; no operative permission inferred from mirrored terms.','official open failed')
ev('addie','https://link.springer.com/book/10.1007/978-0-387-09506-6','book title and publisher','Candidate work Instructional Design: The ADDIE Approach located. Selection not authorized; it is not a license for ADDIE generally.')
ev('backward','https://www.ascd.org/books/the-understanding-by-design-guide-to-creating-high-quality-units?variant=109107','title and trademark notice','Candidate book located; Understanding by Design and UbD trademarks identified. No content license verified.')
ev('bloom','https://www.loc.gov/item/00063423/','About this Item','Catalog identifies Anderson/Krathwohl 2001 revised taxonomy. This is one candidate, distinct from original Bloom; catalog is not a license for the book.')
ev('merrill','https://doi.org/10.1007/bf02505024','article title','Candidate First principles of instruction article located; article versus book selection remains open.')
ev('4cid','https://4cid.org/','direct open failure','Official candidate site inaccessible in this attempt; no license established.','official open failed')
uses=['quotation','summary','translation','adaptation','redistribution','commercial_use']
D=[]
for r in refs:
 n=int(r['referenceId'][-3:]); d={'referenceId':r['referenceId'],'suppliedName':r['suppliedName'],'exactWork':r['exactTitle'],'version':r['edition'],'canonicalURL':r['canonicalURL'],'owner':{'name':'UNKNOWN','status':'pending verification'},'identitySource':'baseline research/references.json; unchanged','dossierState':'documented_with_open_items','rightsClearedForIntendedUse':False,'evidenceRefs':[],'uses':{},'ownerDecision':'Specify exact excerpt/assets, language, audience, delivery channel, commercial context and reviewer; approve only the evidenced use.','limitations':[]}
 status={u:'pending verification' for u in uses}; reason='No work-specific affirmative permission verified; no statutory exception assessed.'
 if n in range(16,20):
  d['evidenceRefs']=['iso']; d['owner']={'name':'ISO','status':'issuer policy observed'}; status={u:'permission-required' for u in uses};status['summary']='pending verification'; reason='ISO reproduction policy; original factual summary versus protected expression requires use-specific review.'
 elif n in range(23,28):
  d['evidenceRefs']=['ims','imslic'];d['owner']={'name':'1EdTech, except item-specific third-party notices','status':'issuer policy observed'};status.update(quotation='restricted',summary='pending verification',translation='permission-required',adaptation='restricted',redistribution='restricted',commercial_use='restricted');reason='Issuer policy offers bounded uses; normative document/version and its license link must first be selected. Translation agreement is required; commercial implementation is not commercial document adaptation.'
 elif n in [2,4,28,29]:
  k={2:'routledge',4:'atd',28:'asq',29:'deming'}[n];d['evidenceRefs']=[k]+(['asqpermission'] if n==28 else []);status={u:'permission-required' for u in uses};status['summary']='pending verification';reason='Recorded issuer policy restricts protected-content reuse; independent summary and any legal exception remain unreviewed.';d['owner']={'name':{2:'UNKNOWN per chapter/figure; Routledge/Taylor & Francis administers permissions',4:'ATD and/or licensors',28:'ASQ and/or third-party authors',29:'The W. Edwards Deming Institute'}[n],'status':'policy observed; item-level exceptions must be checked'}
 elif n==6:
  d['evidenceRefs']=['unesco'];d['owner']={'name':'UNESCO; third-party exceptions unverified','status':'issuer terms observed'};status.update(quotation='restricted',summary='restricted',translation='restricted',adaptation='pending verification',redistribution='restricted',commercial_use='permission-required');reason='Only occasional individual noncommercial educational/research uses under section 5; do not infer CC license for this legal-affairs page.'
 elif n==7:
  d['evidenceRefs']=['solar','ccby'];d['owner']={'name':'Society for Learning Analytics Research; excludes separately noted material','status':'page footer observed'};status={u:'allowed' for u in uses};reason='Conditional CC BY 4.0 for unexcepted webpage text: attribute, link license, mark changes; exclude embedded video, logos and third-party exceptions. Exact reusable text and legal code still require reviewer signoff.'
 elif n in [21,22]:
  d['evidenceRefs']=['xapi' if n==21 else 'cmi'];d['owner']={'name':'Repository contributors; complete ownership chain UNKNOWN','status':'repository license observed'};status={u:'restricted' for u in uses};reason='Apache-2.0 repository license observed; pin commit and material scope, retain license/notices, mark modifications. No transfer to later IEEE standards.'
 else:
  k={1:'ieee',3:'lebok',5:'aect',8:'addie',10:'backward',11:'4cid',12:'bloom',14:'merrill',15:'cast'}.get(n)
  if k:d['evidenceRefs']=[k]
  d['limitations'].append({9:'SAM name alone does not identify a work; unrelated Cengage SAM license rejected as nonmatching.',13:'Gagne may refer to different books/editions or nine-events representations; no work selected.',20:'FY24 DoDI reference is not selected SCORM specification; government provenance alone does not clear third-party text.'}.get(n,'No transferable rights inference from institution, framework name, public access or download availability.'))
 if 8<=n<=14:d['ownerDecision']='Select exact primary work, author, edition/ISBN/DOI and asset first; then inspect that work’s copyright and permission scope. Candidate discovery is not adoption.'
 d['issuerFromBaseline']=r['issuer']
 d['authoritativeTermsURLs']=[E[k]['url'] for k in d['evidenceRefs']]
 d['observedAt']='2026-11-25'
 d['evidence']=[E[k] for k in d['evidenceRefs']]
 d['uses']={u:{'status':status[u],'basis':reason,'evidenceRefs':d['evidenceRefs']} for u in uses}
 d['limitations'].append('No purchase, contact, permission request, license selection, publication or operational release performed. Dossier completion is not G1 clearance.')
 D.append(d)
 forfile=p/(d['referenceId']+'.json');forfile.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
counts=collections.Counter(v['status'] for d in D for v in d['uses'].values())
reg={'mission':'LE-01','observedAt':'2026-11-25','baseline':'3ff3f5d','sourceSHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'status':'PARTIAL','coverage':{'dossiers':len(D),'expected':29,'rightsClearedForIntendedUse':0,'statusCells':dict(counts)},'meaning':'All 29 names documented, not all rights questions resolved. Status describes observed policy scope, not legal advice or owner approval.','evidence':list(E.values()),'dossiers':D}
(p/'rights-register.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
lines=['# LE-01 — Source rights dossiers','Date: 2026-11-25. **29/29 dossiers documented; 0/29 cleared for intended operational use. G1 remains PARTIAL.**','', 'This is a source-grounded permissions review, not a legal opinion. Each use is assessed separately. “Allowed” means an observed conditional license grant, not owner acceptance. “Restricted” identifies bounded policy grants; “permission-required” reports an issuer requirement; “pending verification” preserves unknowns. No statutory exceptions have been adjudicated.','', 'The seven framework-only references remain unselected. Publisher/issuer identity does not automatically establish ownership of every asset. No purchase, contact, license selection, publication, or original-register change occurred.','', '## Matrix','Q=quotation; S=summary; T=translation; A=adaptation; R=redistribution; C=commercial use.','', '| ID / name | Q | S | T | A | R | C |','|---|---|---|---|---|---|---|']
for d in D:lines.append('| '+d['referenceId']+' '+d['suppliedName']+' | '+' | '.join(d['uses'][u]['status'] for u in uses)+' |')
lines+=['','## Evidence and decisions','1. Rights reviewer must pin exact work/assets and use context, review third-party exclusions and record attribution/permission receipts.','2. Domain owner must select ADDIE, SAM, Backward Design, 4C-ID, Bloom, Gagne and Merrill works; candidate links below are discovery only.','3. Technical owner must select normative SCORM/1EdTech versions and immutable repository commits. Repository Apache licenses do not license later IEEE standards.','4. SoLAR webpage text offers a conditional CC BY route, but its embedded video has a different license. UNESCO OER policy does not itself license all OER or every UNESCO page.','5. ASQ PDCA and Deming PDSA diagrams/text require distinct rights review; the synthetic pilot is not licensed by this dossier.','']
for d in D:
 lines+=['### '+d['referenceId']+' — '+d['suppliedName'],'- Work: '+d['exactWork']+'; version: '+d['version'],'- Owner: '+d['owner']['name']+' ('+d['owner']['status']+').','- Assessment: '+d['uses']['quotation']['basis'],'- Decision: '+d['ownerDecision']]
 for k in d['evidenceRefs']:
  e=E[k];lines.append('- Evidence ['+k+']('+e['url']+'), '+e['locator']+'; observed '+e['observedAt']+': '+e['observation'])
 lines+=['- Limits: '+' '.join(d['limitations']),'']
(p/'REPORT.md').write_text('\n'.join(lines)+'\n')
assert len(D)==29 and len({d['referenceId'] for d in D})==29
assert all(set(d['uses'])==set(uses) for d in D)
(p/'validation.json').write_text(json.dumps({'dossierCoverage':'29/29','individualJSONFiles':29,'usageCells':174,'statusCounts':dict(counts),'clearedUsageCount':0,'sourceUnchangedSHA256':reg['sourceSHA256'],'checks':['unique IDs','six usage statuses per dossier','JSON parsed/generated','baseline register read only'],'result':'PASS_STRUCTURAL_ONLY'},indent=2)+'\n')
print(json.dumps(reg['coverage']))
