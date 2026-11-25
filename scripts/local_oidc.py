"""Local synthetic operator login with PKCE; tokens are never logged."""
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import html
import http.cookiejar
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(os.environ.get('ACADEMY_RUNTIME_ROOT', Path(__file__).resolve().parents[1]))
settings=dict(line.split('=',1) for line in (ROOT/'infra/runtime/.env').read_text().splitlines() if '=' in line)
API = 'http://localhost:'+settings.get('ACADEMY_API_PORT','18400')
IDP = 'http://localhost:'+settings.get('ACADEMY_IDP_PORT','18480')+'/realms/academy/protocol/openid-connect'

class LocalCookiePolicy(http.cookiejar.DefaultCookiePolicy):
    def return_ok_secure(self, cookie, request):
        # Match browser secure-context exception for loopback development only.
        if urllib.parse.urlsplit(request.full_url).hostname == 'localhost':
            return True
        return super().return_ok_secure(cookie,request)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def login(name):
    creds = json.loads((ROOT/'infra/runtime/credentials.json').read_text())[name]
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    state = secrets.token_urlsafe(16)
    redirect = 'http://localhost:'+settings.get('ACADEMY_UI_PORT','18401')+'/'
    query = urllib.parse.urlencode(dict(client_id='academy-web',redirect_uri=redirect,response_type='code',scope='openid',code_challenge=challenge,code_challenge_method='S256',state=state))
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar(policy=LocalCookiePolicy())),NoRedirect())
    response = opener.open(IDP+'/auth?'+query,timeout=15)
    page = response.read().decode()
    match = re.search(r'<form[^>]+action="([^"]+)"',page)
    if not match:
        raise RuntimeError('OIDC login form missing')
    action = html.unescape(match.group(1))
    data = urllib.parse.urlencode({'username':creds['username'],'password':creds['password'],'credentialId':''}).encode()
    try:
        response = opener.open(action,data,timeout=15)
    except urllib.error.HTTPError as error:
        if error.code not in (302,303):
            raise RuntimeError('OIDC local login failed') from None
        response = error
    location = response.headers.get('Location','')
    values = urllib.parse.parse_qs(urllib.parse.urlsplit(location).query)
    if values.get('state') != [state] or 'code' not in values:
        raise RuntimeError('OIDC authorization code/state missing')
    payload = urllib.parse.urlencode(dict(grant_type='authorization_code',client_id='academy-web',code=values['code'][0],redirect_uri=redirect,code_verifier=verifier)).encode()
    return json.load(opener.open(IDP+'/token',payload,timeout=15))

