import json
import pytest
from fastapi import HTTPException
from app import moodle
A='10000000-0000-4000-8000-000000000001'
S='00000000-0000-4000-8000-000000000001'
@pytest.fixture
def configured(tmp_path,monkeypatch):
    p=tmp_path/'tokens.json'; p.write_text(json.dumps({'tenant_id':A,'users':{S:{'userid':4,'token':'private-test-token'}}})); p.chmod(0o600)
    for k,v in {'MOODLE_URL':'http://localhost:18701','MOODLE_TENANT_ID':A,'MOODLE_TOKENS_FILE':str(p)}.items(): monkeypatch.setenv(k,v)
    return p

def test_other_tenant_never_reads_secret(configured,monkeypatch):
    configured.unlink()
    assert moodle.overview('10000000-0000-4000-8000-000000000002',S)=={'enabled':False}

def test_unknown_subject_denied(configured):
    with pytest.raises(HTTPException) as exc: moodle.overview(A,'untrusted')
    assert exc.value.status_code==403

def test_insecure_secret_permissions_fail_closed(configured):
    configured.chmod(0o644)
    with pytest.raises(HTTPException) as exc: moodle.overview(A,S)
    assert exc.value.status_code==503

def test_mismatched_remote_identity_fails_before_course_read(configured,monkeypatch):
    calls=[]
    def fake(token,function,**kw): calls.append(function); return {'userid':4,'username':'different'}
    monkeypatch.setattr(moodle,'rest',fake)
    with pytest.raises(HTTPException): moodle.overview(A,S)
    assert calls==['core_webservice_get_site_info']

def test_output_is_minimal_and_course_parameters_server_derived(configured,monkeypatch):
    calls=[]
    def fake(token,function,**kw):
        kw.pop('_timeout',None)
        calls.append((function,kw))
        if function=='core_webservice_get_site_info': return {'userid':4,'username':S,'secret':'omitted'}
        if function=='core_enrol_get_users_courses': return [{'id':6,'fullname':'Course','progress':100,'private':'omitted'}]
        return [{'modules':[{'id':22,'name':'Lesson','modname':'page','url':'https://evil.example','contents':[{'secret':'omit'}],'completiondata':{'state':1}}]}]
    monkeypatch.setattr(moodle,'rest',fake)
    result=moodle.overview(A,S)
    assert calls[1][1]=={'userid':4}; assert calls[2][1]=={'courseid':6}
    assert result['courses'][0]['modules'][0]['url']=='http://localhost:18701/mod/page/view.php?id=22'
    assert 'private-test-token' not in json.dumps(result) and 'omitted' not in json.dumps(result)

def test_untrusted_endpoint_rejected(monkeypatch):
    monkeypatch.setenv('MOODLE_REST_URL','https://evil.example/webservice/rest/server.php')
    with pytest.raises(ValueError): moodle.rest('secret','core_webservice_get_site_info')


def test_total_deadline_stops_further_calls(configured,monkeypatch):
    clock=[0]; calls=[]
    monkeypatch.setattr(moodle.time,'monotonic',lambda:clock[0])
    def fake(token,function,**kw):
        calls.append(function); clock[0]+=11
        return {'userid':4,'username':S}
    monkeypatch.setattr(moodle,'rest',fake)
    with pytest.raises(HTTPException) as exc: moodle.overview(A,S)
    assert exc.value.status_code==503 and len(calls)==1

def test_course_bound_stops_contents(configured,monkeypatch):
    calls=[]
    def fake(token,function,**kw):
        calls.append(function)
        return {'userid':4,'username':S} if len(calls)==1 else [{}]*11
    monkeypatch.setattr(moodle,'rest',fake)
    with pytest.raises(HTTPException): moodle.overview(A,S)
    assert len(calls)==2

def test_module_bound(configured,monkeypatch):
    def fake(token,function,**kw):
        if function=='core_webservice_get_site_info': return {'userid':4,'username':S}
        if function=='core_enrol_get_users_courses': return [{'id':6,'fullname':'Course'}]
        return [{'modules':[{'id':22,'name':'Lesson','modname':'page'}]*1001}]
    monkeypatch.setattr(moodle,'rest',fake)
    with pytest.raises(HTTPException) as exc: moodle.overview(A,S)
    assert exc.value.status_code==503
