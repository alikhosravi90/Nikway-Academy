"""Bounded read-only Moodle adapter. Identity comes exclusively from authenticated Context."""
import json
import os
import stat
import time
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from fastapi import HTTPException
from .integrations import moodle_link

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('Redirect refused')

def rest(token, function, _timeout=5, **params):
    endpoint = os.environ.get('MOODLE_REST_URL', '')
    parsed = urlsplit(endpoint)
    if parsed.scheme != 'http' or parsed.hostname not in ('localhost', 'moodle') or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path != '/webservice/rest/server.php':
        raise ValueError('Untrusted endpoint')
    request = Request(endpoint, data=urlencode({'wstoken':token,'wsfunction':function,'moodlewsrestformat':'json',**params}).encode(), headers={'Host':'localhost:18701','Content-Type':'application/x-www-form-urlencoded'})
    with build_opener(NoRedirect).open(request, timeout=min(5, _timeout)) as response:
        raw=response.read(2_000_001)
    if len(raw)>2_000_000: raise ValueError('Response too large')
    data=json.loads(raw)
    if isinstance(data,dict) and ('exception' in data or 'errorcode' in data): raise ValueError('Moodle rejected request')
    return data

def overview(tenant_id, subject):
    link=moodle_link(tenant_id)
    if not link['enabled']: return {'enabled':False}
    try:
        path=Path(os.environ['MOODLE_TOKENS_FILE'])
        if stat.S_IMODE(path.stat().st_mode) != 0o600: raise ValueError('Unsafe secret permissions')
        config=json.loads(path.read_text())
        if config['tenant_id'] != tenant_id: raise ValueError('Tenant configuration mismatch')
        binding=config['users'].get(subject)
        if not binding: raise HTTPException(403,'Moodle identity not provisioned')
        token=binding['token']
        deadline=time.monotonic()+10
        def call(function, **params):
            remaining=deadline-time.monotonic()
            if remaining <= 0: raise ValueError('Moodle deadline exceeded')
            value=rest(token,function,_timeout=remaining,**params)
            if time.monotonic() >= deadline: raise ValueError('Moodle deadline exceeded')
            return value
        identity=call('core_webservice_get_site_info')
        if identity['userid'] != binding['userid'] or identity['username'] != subject: raise ValueError('Identity drift')
        courses=call('core_enrol_get_users_courses',userid=identity['userid'])
        if not isinstance(courses,list) or len(courses)>10: raise ValueError('Course bound exceeded')
        output=[]
        module_count=0
        for course in courses:
            cid=int(course['id'])
            sections=call('core_course_get_contents',courseid=cid)
            modules=[]
            for section in sections:
                for item in section.get('modules',[]):
                    module_count+=1
                    if module_count>1000: raise ValueError('Module bound exceeded')
                    mid=int(item['id']); kind=item['modname']
                    if kind not in ('page','assign','quiz','resource','url','forum','book','lesson','h5pactivity'): continue
                    modules.append({'id':mid,'title':item['name'],'type':kind,'url':f"{link['url']}mod/{kind}/view.php?id={mid}",'completion':item.get('completiondata',{}).get('state')})
            output.append({'id':cid,'title':course['fullname'],'url':f"{link['url']}course/view.php?id={cid}",'progress':course.get('progress'),'modules':modules})
        return {'enabled':True,'source':'moodle','url':link['url'],'progress_sync':False,'courses':output}
    except HTTPException: raise
    except Exception:
        raise HTTPException(503,'Moodle read-only integration unavailable') from None
