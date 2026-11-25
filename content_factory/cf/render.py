"""Deterministic portable local renditions; no third-party publisher involved."""
import html
import io
import json
import zipfile
from .store import canonical,sha
from .errors import DomainError

def score(component,answers):
    qs={q['id']:q for q in component['body']['questions']}
    if set(answers)-set(qs): raise DomainError('unknown question')
    if any(type(v) is not int or v<0 or v>=len(qs[k]['options']) for k,v in answers.items()):
        raise DomainError('invalid answer')
    return {'correct':sum(answers.get(k)==q['answer'] for k,q in qs.items()),'total':len(qs)}

def build_package(manifest,components,instructor=False):
    text=['# Local publication candidate — NOT RELEASED\n']; sections=[]; quiz=[]
    for r in components:
        body=r['body']; text.extend(['# '+r['title'],body['summary']])
        sections.append('<article><h1>'+html.escape(r['title'])+'</h1><p>'+html.escape(body['summary'])+'</p>')
        for s in body['sections']:
            text.extend(['## '+s['title'],s['text']])
            sections.append('<section><h2>'+html.escape(s['title'])+'</h2><p>'+html.escape(s['text'])+'</p></section>')
        text.extend(['## تمرین',body['exercise']])
        sections.append('<h2>تمرین</h2><p>'+html.escape(body['exercise'])+'</p><h2>خودآزمایی</h2>')
        questions=[]
        for q in body['questions']:
            public={k:v for k,v in q.items() if instructor or k not in ('answer','explanation')}
            questions.append(public)
            sections.append('<fieldset><legend>'+html.escape(q['prompt'])+'</legend><ol>'+''.join('<li>'+html.escape(o)+'</li>' for o in q['options'])+'</ol></fieldset>')
        sections.append('<p>منبع: محتوای آموزشی آزمایشی تألیف‌شده؛ تأیید انسانی و انتشار عمومی انجام نشده است.</p></article>')
        quiz.append({'componentId':r['id'],'revisionId':r['revisionId'],'questions':questions})
    lang=components[0]['locale'] if components else 'fa-IR'
    direction='rtl' if lang.split('-')[0] in ('fa','ar','he','ur') else 'ltr'
    page='<!doctype html><html lang="'+html.escape(lang,quote=True)+'" dir="'+direction+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>کارخانه محتوا — PDCA</title><style>body{font:18px/1.9 sans-serif;max-width:850px;margin:2em auto;padding:1em;color:#18332f;background:#f8faf9}h1,h2{color:#126b58}fieldset{margin:1em 0;border:1px solid #819b95;border-radius:8px}aside{background:#fff2cc;padding:1em}article{margin-top:2em}</style></head><body><aside>نسخه آزمایشی محلی — نامزد انتشار؛ انتشار یا تأیید انسانی نشده است.</aside><main>'+''.join(sections)+'</main></body></html>'
    parts={'text.md':'\n\n'.join(text).encode(),'lesson.html':page.encode(),'quiz.json':canonical(quiz)}
    export_manifest={**manifest,'audience':'instructor' if instructor else 'learner','files':{k:sha(v) for k,v in parts.items()}}
    parts['manifest.json']=canonical(export_manifest)
    return parts

def zip_package(parts):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in sorted(parts):
            info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,parts[name])
    return buf.getvalue()
