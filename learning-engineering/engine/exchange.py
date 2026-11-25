"""Offline fixture exchange. Not an authentication or production delivery service."""
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
from jsonschema import Draft202012Validator, FormatChecker
from engine.knowledge import validate_records, SCHEMA as RECORD_SCHEMA
from referencing import Registry, Resource

SCHEMA_PATH = Path(__file__).resolve().parents[1]/'schemas/package.schema.json'

def package_validator():
    schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    registry=Registry().with_resource('urn:nikway:learning-engineering:record:0.1.0',Resource.from_contents(RECORD_SCHEMA))
    return Draft202012Validator(schema,registry=registry,format_checker=FormatChecker())

def canonical(value):
    """Local wire profile: UTF-8, sorted keys, compact separators, no NaN. Not RFC 8785."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')

def digest(body):
    return hashlib.sha256(canonical(body)).hexdigest()

def build_package(records, package_id, revision):
    errors=validate_records(records)
    if not records or errors:
        raise ValueError('INVALID_RECORDS: '+ '; '.join(errors))
    records=sorted(copy.deepcopy(records), key=lambda r:(r['id'],r['version']))
    body={'contractVersion':'0.1.0','packageId':package_id,'packageRevision':revision,
          'producer':'learning-engineering','objects':records,
          'dependencyManifest':[{'id':r['id'],'version':r['version']} for r in records]}
    package=dict(body,payloadDigest=digest(body))
    _validate(package)
    return package

def _validate(package):
    if not isinstance(package,dict): raise ValueError('INVALID_PACKAGE')
    if package.get('contractVersion') != '0.1.0': raise ValueError('UNSUPPORTED_VERSION')
    errors=list(package_validator().iter_errors(package))
    if errors: raise ValueError('INVALID_PACKAGE: '+errors[0].message)
    body={k:v for k,v in package.items() if k!='payloadDigest'}
    if digest(body)!=package['payloadDigest']: raise ValueError('DIGEST_MISMATCH')
    errors=validate_records(package['objects'])
    if errors: raise ValueError('INVALID_RECORDS: '+'; '.join(errors))
    expected=sorted([{'id':r['id'],'version':r['version']} for r in package['objects']],key=lambda r:(r['id'],r['version']))
    if package['dependencyManifest']!=expected: raise ValueError('MANIFEST_MISMATCH')

def _receipt(package):
    return {'packageId':package['packageId'],'packageRevision':package['packageRevision'],
            'payloadDigest':package['payloadDigest'],'status':'quarantined',
            'scope':'local-fixture','reasons':validate_records(package['objects'],delivery=True)+
            ['OWNER_ACCEPTANCE_AND_TRUSTED_ADAPTER_REQUIRED']}

def receive_package(package, store, context):
    # Control: never infer a trusted principal or tenant from caller-supplied metadata.
    if context not in ({'producer':'learning-engineering','consumer':c,'scope':'local-fixture'} for c in ('content-factory','learning-os')):
        raise ValueError('ACCESS_DENIED: local fixture context only')
    _validate(package)
    store=Path(store)
    store.parent.mkdir(parents=True,exist_ok=True)
    with open(str(store)+'.lock','a',encoding='utf-8') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        state=json.loads(store.read_text(encoding='utf-8')) if store.exists() else {'packages':[]}
        if not isinstance(state,dict) or set(state)!={'packages'} or not isinstance(state['packages'],list):
            raise ValueError('CORRUPT_STORE')
        replay=None
        prior_records={}
        for entry in state['packages']:
            if not isinstance(entry,dict) or set(entry)!={'package','receipt'}:
                raise ValueError('CORRUPT_STORE')
            old=entry['package']
            _validate(old)
            if entry['receipt'] != _receipt(old): raise ValueError('CORRUPT_STORE: receipt mismatch')
            if (old['packageId'],old['packageRevision'])==(package['packageId'],package['packageRevision']):
                if old['payloadDigest']!=package['payloadDigest']: raise ValueError('REVISION_CONFLICT')
                replay=entry['receipt']
            for record in old['objects']:
                key=(record['id'],record['version'])
                if key in prior_records and prior_records[key]!=record:
                    raise ValueError('CORRUPT_STORE: record conflict')
                prior_records[key]=record
        for record in package['objects']:
            key=(record['id'],record['version'])
            if key in prior_records and prior_records[key]!=record:
                raise ValueError('RECORD_REVISION_CONFLICT')
        if replay is not None: return replay
        receipt=_receipt(package)
        # Control: this local adapter never promotes metadata to real delivery authorization.
        state['packages'].append({'package':copy.deepcopy(package),'receipt':receipt})
        fd,name=tempfile.mkstemp(prefix=store.name+'.',dir=store.parent)
        try:
            with os.fdopen(fd,'wb') as stream:
                stream.write(canonical(state)); stream.flush(); os.fsync(stream.fileno())
            os.replace(name,store)
        finally:
            if os.path.exists(name): os.unlink(name)
        return receipt
