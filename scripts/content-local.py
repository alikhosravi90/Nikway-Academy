#!/usr/bin/env python3
"""Local operator content admission/export. Credentials stay in private runtime files."""
import argparse, json, sys, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from content.validate_package import load_package
from local_oidc import login, API

parser=argparse.ArgumentParser(description=__doc__)
sub=parser.add_subparsers(dest='command',required=True)
imp=sub.add_parser('import'); imp.add_argument('file'); imp.add_argument('--publish',action='store_true',help='Explicit reviewer approval for this local publication')
exp=sub.add_parser('export'); exp.add_argument('course_id'); exp.add_argument('output')
args=parser.parse_args()
# Validation occurs before login or any network mutation.
package=load_package(Path(args.file).read_bytes()) if args.command=='import' else None
token=login('reviewer-a')['access_token']
def call(path,body=None):
    data=json.dumps(body,ensure_ascii=False).encode() if body is not None else None
    request=urllib.request.Request(API+path,data,{'Content-Type':'application/json','Authorization':'Bearer '+token})
    try:
        return json.load(urllib.request.urlopen(request,timeout=30))
    except urllib.error.HTTPError as error:
        raise SystemExit(f'Content operation rejected HTTP {error.code}; no credentials logged') from None
if package:
    result=call('/api/content-packages',package)
    if args.publish:
        result=call('/api/content-packages/'+result['id']+'/publish',{'expected_digest':result['digest'],'expected_revision':result['revision']})
    print(json.dumps(result,ensure_ascii=False))
else:
    result=call('/api/courses/'+args.course_id+'/package')
    data=json.dumps(result,ensure_ascii=False,indent=2).encode()
    load_package(data)
    # Never overwrite a pre-existing operator artifact.
    with open(args.output,'xb') as stream: stream.write(data+b'\n')
    print('Exported validated portable package; no tenant credentials or runtime IDs added.')
