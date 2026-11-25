#!/usr/bin/env python3
"""Real local HTTP OIDC checks. Never prints credentials, cookies, codes or tokens."""
import argparse,http.cookiejar,html,json,re,secrets,subprocess,urllib.request,urllib.parse,urllib.error
from pathlib import Path
from html.parser import HTMLParser
class PostForm(HTMLParser):
 def __init__(self): super().__init__();self.action=None;self.fields={}
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='form' and a.get('method','').lower()=='post': self.action=a.get('action')
  if tag=='input' and a.get('name') and a.get('type','').lower()=='hidden': self.fields[a['name']]=a.get('value','')
p=argparse.ArgumentParser();p.add_argument('--academy-runtime',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
base='http://localhost:18701';checks=[]
credentials=json.loads((args.academy_runtime/'credentials.json').read_text())
class LocalCookies(http.cookiejar.DefaultCookiePolicy):
 def return_ok_secure(self,cookie,request):
  return urllib.parse.urlsplit(request.full_url).hostname=='localhost' or super().return_ok_secure(cookie,request)
class Redirects(urllib.request.HTTPRedirectHandler):
 def __init__(self):self.urls=[]
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  self.urls.append(newurl);return super().redirect_request(req,fp,code,msg,headers,newurl)
def opener():
 trace=Redirects();return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar(policy=LocalCookies())),trace),trace
def page(o,url,data=None):
 try:r=o.open(url,data,timeout=30)
 except urllib.error.HTTPError as e:r=e
 return r.status,r.geturl(),r.read().decode()
def check(label,value):
 if not value:raise AssertionError(label)
 checks.append(label)
def snapshot():
 code='''<?php define('CLI_SCRIPT',true); require('/var/www/moodle/config.php'); $out=[];
 foreach (['00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000003','00000000-0000-4000-8000-000000000002'] as $sub) {
 $u=$DB->get_record('user',['username'=>$sub,'deleted'=>0]); $out[$sub]=$u ? ['id'=>(int)$u->id,'admin'=>is_siteadmin($u->id),'auth'=>$u->auth] : null; }
 $out['user_count']=$DB->count_records('user',['deleted'=>0]); echo json_encode($out);'''
 r=subprocess.run(['docker','exec','-i','nikway-academy-moodle-moodle-1','php'],input=code,text=True,capture_output=True,check=True)
 return json.loads(r.stdout)
def login(name):
 o,trace=opener();status,url,body=page(o,base+'/auth/oidc/')
 queries=[urllib.parse.parse_qs(urllib.parse.urlsplit(u).query) for u in trace.urls]
 check(name+' authorization S256',any(q.get('code_challenge_method')==['S256'] and q.get('code_challenge') for q in queries))
 form=re.search(r'<form[^>]+action="([^"]+)"',body)
 check(name+' real identity form',form is not None)
 c=credentials[name];payload=urllib.parse.urlencode({'username':c['username'],'password':c['password'],'credentialId':''}).encode()
 status,url,body=page(o,html.unescape(form.group(1)),payload)
 f=PostForm();f.feed(body)
 if f.action and 'code' in f.fields and 'state' in f.fields:
  check(name+' form_post callback exact',f.action==base+'/auth/oidc/')
  status,url,body=page(o,f.action,urllib.parse.urlencode(f.fields).encode())
 return o,status,url,body
before=snapshot();check('tenant B absent before',before['00000000-0000-4000-8000-000000000002'] is None)
for name,sub in [('learner-a','00000000-0000-4000-8000-000000000001'),('reviewer-a','00000000-0000-4000-8000-000000000003')]:
 o,status,url,body=login(name)
 status,url,body=page(o,base+'/my/')
 check(name+' authenticated dashboard',status==200 and '/my/' in url and 'login/logout.php' in body)
 check(name+' own profile identity',bool(re.search(r'/user/profile\.php\?id='+str(before[sub]['id'])+r'(?:["&])',html.unescape(body))))
 check(name+' not site administrator',before[sub]['admin'] is False)
 logout=re.search(r'(?:href|action)="([^"]*login/logout\.php[^\"]*)"',body)
 check(name+' logout available',logout is not None)
 page(o,html.unescape(logout.group(1)))
 _,afterurl,afterbody=page(o,base+'/my/')
 check(name+' logout invalidates Moodle session','login/logout.php' not in afterbody)
o,status,url,body=login('learner-b')
check('tenant B explicitly denied','restrictions currently prevent' in body)
_,url,body=page(o,base+'/my/')
check('tenant B has no Moodle session','login/logout.php' not in body)
after=snapshot();check('tenant B absent after',after['00000000-0000-4000-8000-000000000002'] is None)
check('no account auto-creation',before['user_count']==after['user_count'])
o,_=opener();_,url,body=page(o,base+'/auth/oidc/?code=synthetic-invalid&state='+secrets.token_hex(24))
check('unknown callback state rejected','Unknown state' in body or 'login state' in body.lower())
_,url,body=page(o,base+'/my/');check('invalid callback no session','login/logout.php' not in body)
result={'result':'PASS','scope':'real local HTTP OIDC; no browser rendering or JWT verification certification','checks':checks,'count':len(checks),'subject_account_snapshot_unchanged':before==after,'secrets_logged':False}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'result':'PASS','checks':len(checks)}))
