"""Run from learning-engineering/: python3 -m engine.cli --help."""
import argparse
import json
from pathlib import Path
import sys
from engine.knowledge import load_records, validate_records, search, render_markdown, accumulate
from engine.exchange import build_package, receive_package
from engine.review import review_revision

def output(value):
    print(json.dumps(value,ensure_ascii=False,indent=2))

def write_new(path,value):
    # Control: an output cannot silently replace canonical records or earlier evidence.
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False); f.write('\n')

def main(argv=None):
    parser=argparse.ArgumentParser(description='Local bilingual Learning Engineering repository')
    subs=parser.add_subparsers(dest='command',required=True)
    for name in ('validate','search','render','accumulate','export','review'):
        sub=subs.add_parser(name); sub.add_argument('records')
        if name=='validate': sub.add_argument('--delivery',action='store_true')
        if name=='search': sub.add_argument('query')
        if name=='accumulate': sub.add_argument('new'); sub.add_argument('output')
        if name=='review':
            for field in ('record_id','version','new_version','output'): sub.add_argument(field)
            sub.add_argument('--reviewer',required=True); sub.add_argument('--reviewed-at',required=True)
        if name=='export':
            sub.add_argument('output'); sub.add_argument('--package-id',required=True); sub.add_argument('--revision',required=True)
    sub=subs.add_parser('import'); sub.add_argument('package'); sub.add_argument('store')
    sub.add_argument('--consumer',choices=['content-factory','learning-os'],required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='import':
            package=json.loads(Path(args.package).read_text(encoding='utf-8'))
            output(receive_package(package,args.store,{'producer':'learning-engineering','consumer':args.consumer,'scope':'local-fixture'})); return 0
        records=load_records(args.records)
        errors=validate_records(records,delivery=getattr(args,'delivery',False))
        if not records: errors.append('EMPTY_REPOSITORY')
        if errors:
            output({'status':'FAIL','errors':errors}); return 1
        if args.command=='validate': output({'status':'PASS_LOCAL_STRUCTURE','records':len(records)})
        elif args.command=='search': output(search(records,args.query))
        elif args.command=='render': print(render_markdown(records))
        elif args.command=='accumulate':
            combined=accumulate(records,load_records(args.new)); write_new(args.output,combined)
            output({'status':'ACCUMULATED','records':len(combined)})
        elif args.command=='review':
            write_new(args.output,review_revision(records,args.record_id,args.version,args.new_version,args.reviewer,args.reviewed_at))
            output({'status':'DECLARED_REVIEW_RECORDED','trustedHumanApproval':False})
        elif args.command=='export':
            write_new(args.output,build_package(records,args.package_id,args.revision))
            output({'status':'EXPORTED_DRAFT','records':len(records)})
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('ERROR: '+str(exc),file=sys.stderr); return 1

if __name__=='__main__': sys.exit(main())
