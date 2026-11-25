"""Descriptive deidentified scores only; metadata is not consent or evidence certification."""
import json
import re
import sys
from pathlib import Path

def analyze(dataset):
    if not isinstance(dataset,dict) or set(dataset)!={'datasetKind','protocolVersion','rubricVersion','rows'}:
        raise ValueError('Invalid dataset shape; personal/free-text fields forbidden')
    if dataset['datasetKind'] not in ('synthetic','observed-deidentified'):
        raise ValueError('Explicit dataset kind required')
    if dataset['protocolVersion']!='0.1.0' or dataset['rubricVersion']!='0.1.0':
        raise ValueError('Unsupported protocol/rubric version')
    if not isinstance(dataset['rows'],list): raise ValueError('Rows must be a list')
    totals={}; phases={'pre':{},'post':{},'transfer':{}}
    for row in dataset['rows']:
        if not isinstance(row,dict) or set(row)!={'participantId','phase','scores'}: raise ValueError('Invalid row fields')
        pid=row['participantId'];phase=row['phase'];scores=row['scores']
        if not isinstance(pid,str) or not re.fullmatch(r'P-[0-9]{3,6}',pid): raise ValueError('Pseudonymous P-number required')
        if not isinstance(phase,str) or phase not in phases: raise ValueError('Unknown phase')
        if not isinstance(scores,dict) or set(scores)!={'plan','do','check','act'}: raise ValueError('All criteria required; missing is not zero')
        if any(type(v) is not int or v not in (0,1,2) for v in scores.values()): raise ValueError('Scores must be integer 0..2')
        if (pid,phase) in totals: raise ValueError('Duplicate participant/phase; adjudicate raters separately')
        totals[(pid,phase)]=sum(scores.values());phases[phase][pid]=sum(scores.values())
    paired=sorted(set(phases['pre'])&set(phases['post']))
    changes=[phases['post'][pid]-phases['pre'][pid] for pid in paired]
    return {'status':'DESCRIPTIVE_ONLY' if totals else 'NO_DATA','declaredDatasetKind':dataset['datasetKind'],
       'protocolVersion':dataset['protocolVersion'],'rubricVersion':dataset['rubricVersion'],
       'participantCount':len({pid for pid,_ in totals}),'pairedCount':len(paired),
       'preOnlyCount':len(set(phases['pre'])-set(phases['post'])),
       'postOnlyCount':len(set(phases['post'])-set(phases['pre'])),
       'transferCount':len(phases['transfer']),
       'meanPairedChange':sum(changes)/len(changes) if changes else None,
       'pairedChanges':changes,'phaseCounts':{k:len(v) for k,v in phases.items()},
       'phaseMeanScores':{k:sum(v.values())/len(v) if v else None for k,v in phases.items()},
       'consentVerified':False,'humanReviewVerified':False,'causalInference':False,
       'limitations':['Descriptive paired change only; no control group or equivalence proof.',
         'Declared dataset type does not authenticate observations or consent.',
         'No missing-score imputation. Transfer count is not transfer success.']}

if __name__=='__main__':
    try:
        if len(sys.argv)!=2: raise ValueError('Usage: evaluate.py /private/path/deidentified-scores.json')
        data=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
        print(json.dumps(analyze(data),ensure_ascii=False,indent=2,allow_nan=False))
    except (OSError,ValueError) as exc:
        print('ERROR: '+str(exc),file=sys.stderr);sys.exit(1)
