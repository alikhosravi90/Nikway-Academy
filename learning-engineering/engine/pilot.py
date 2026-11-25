"""Reproducible local synthetic golden scenario; never delivers learner content."""
import json
from pathlib import Path
import tempfile
from engine.knowledge import load_records, validate_records, search
from engine.semantics import validate_semantics
from engine.exchange import build_package, receive_package
ROOT=Path(__file__).resolve().parents[1]

def run_pilot():
    records=load_records(ROOT/'records')
    errors=validate_records(records)
    ontology=json.loads((ROOT/'semantics/ontology.json').read_text())
    glossary=json.loads((ROOT/'semantics/glossary.json').read_text())
    errors+=validate_semantics(ontology,glossary,records)
    if errors: raise ValueError('\n'.join(errors))
    byid={r['id']:r for r in records}
    chain=['LE-SRC-ASQ-PDCA','LE-EVD-PDCA','LE-CARD-PDCA','LE-CONCEPT-PDCA','LE-COMP-PDCA','LE-OBJ-PDCA','LE-CUR-PDCA','LE-CONTENT-PDCA','LE-ASSESS-PDCA']
    for identity in chain:
        if identity not in byid: raise ValueError('MISSING_PILOT_STAGE: '+identity)
    def linked(a,b):
        # Exact refs in data, provenance or relations, including inverse semantic direction.
        def refs(value):
            if isinstance(value,dict):
                if set(value)=={'id','version'}: yield (value['id'],value['version'])
                else:
                    for child in value.values(): yield from refs(child)
            elif isinstance(value,list):
                for child in value: yield from refs(child)
        return (b['id'],b['version']) in set(refs(a)) or (a['id'],a['version']) in set(refs(b))
    for a,b in zip(chain[:-1],chain[1:-1]):
        if not linked(byid[a],byid[b]): raise ValueError('DISCONNECTED_PILOT: '+a+' -> '+b)
    if byid['LE-CONTENT-PDCA']['data']['objectiveRefs'] != byid['LE-ASSESS-PDCA']['data']['objectiveRefs']:
        raise ValueError('CONTENT_ASSESSMENT_ALIGNMENT')
    # Content and assessment are connected via the same objective and curriculum, not a fabricated direct edge.
    package=build_package(records,'pdca-reference','0.1.0')
    with tempfile.TemporaryDirectory() as tmp:
        states=[]
        for consumer in ('content-factory','learning-os'):
            path=Path(tmp)/(consumer+'.json')
            context={'producer':'learning-engineering','consumer':consumer,'scope':'local-fixture'}
            receipt=receive_package(package,path,context); before=path.read_bytes()
            again=receive_package(package,path,context)
            states.append((receipt,before==path.read_bytes() and receipt==again))
    if not search(records,'چرخه') or not search(records,'PDCA'): raise ValueError('SEARCH_FAILED')
    return {'status':'PASS_LOCAL_SYNTHETIC','recordCount':len(records),'chain':chain,
            'contentFactory':states[0][0]['status'],'learningOS':states[1][0]['status'],
            'replayUnchanged':all(x[1] for x in states),'packageDigest':package['payloadDigest'],
            'learnerEffectivenessMeasured':False,'productionIntegrationTested':False,
            'ownerAccepted':False,'deliveryErrors':validate_records(records,delivery=True)}

if __name__=='__main__': print(json.dumps(run_pilot(),ensure_ascii=False,indent=2))
