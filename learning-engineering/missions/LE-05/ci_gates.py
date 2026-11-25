"""CI must distinguish expected quarantine from a crashed command."""
import json
from pathlib import Path
import subprocess
import sys

def check_delivery_result(returncode, stdout):
    try: value=json.loads(stdout)
    except (ValueError,TypeError): return False
    if returncode!=1 or not isinstance(value,dict) or value.get('status')!='FAIL': return False
    errors=value.get('errors')
    return isinstance(errors,list) and bool(errors) and all(isinstance(e,str) for e in errors) and {e.split(':',1)[0] for e in errors}=={'RIGHTS_PENDING','REVIEW_PENDING'}

def check_empty_result(returncode, stdout):
    try: value=json.loads(stdout)
    except (ValueError,TypeError): return False
    return returncode==0 and isinstance(value,dict) and value.get('status')=='NO_DATA' and type(value.get('participantCount')) is int and value['participantCount']==0 and type(value.get('pairedCount')) is int and value['pairedCount']==0 and 'meanPairedChange' in value and value['meanPairedChange'] is None

def main():
    root=Path(__file__).resolve().parents[2]
    checks=[([sys.executable,'-m','engine.cli','validate','records','--delivery'],check_delivery_result),
            ([sys.executable,'missions/LE-04/evaluate.py','missions/LE-04/dataset-empty.json'],check_empty_result)]
    for command,check in checks:
        result=subprocess.run(command,cwd=root,capture_output=True,text=True)
        if result.stderr or not check(result.returncode,result.stdout):
            print('GATE FAILURE: '+ ' '.join(command));print(result.stdout);print(result.stderr);return 1
    print('PASS: expected delivery denial and absent learner data verified');return 0
if __name__=='__main__': sys.exit(main())
