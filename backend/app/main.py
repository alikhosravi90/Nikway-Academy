import os, json
from typing import Literal
from uuid import UUID, uuid4
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from .auth import authenticated, Context
from .db import engine, rows, one
from .rules import next_completion, review_transition

app = FastAPI(title='NIKWAY Academy Local API',version='0.3.0', docs_url='/api/docs',openapi_url='/api/openapi.json')

@app.middleware('http')
async def boundary(request: Request, call_next):
    request.state.correlation_id = str(uuid4())
    limit = 131072 if request.url.path == '/api/content-packages' else (65536 if request.url.path.endswith('/submissions') else 20000)
    length = request.headers.get('content-length','0')
    try:
        if int(length) < 0: raise ValueError('negative length')
        if int(length) > limit:
            return JSONResponse({'code':'payload_too_large','message':'Request too large'},status_code=413)
    except ValueError:
        return JSONResponse({'code':'invalid_length','message':'Invalid request'},status_code=400)
    # Bound the actual stream as well as the declared length, including chunked bodies.
    payload = bytearray()
    async for chunk in request.stream():
        payload.extend(chunk)
        if len(payload) > limit:
            return JSONResponse({'code':'payload_too_large','message':'Request too large'},status_code=413)
    request._body = bytes(payload)
    response = await call_next(request)
    response.headers['X-Correlation-ID'] = request.state.correlation_id
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.exception_handler(HTTPException)
async def api_error(request, exc):
    return JSONResponse({'code':str(exc.status_code),'message':exc.detail,'detail':exc.detail,'correlation_id':request.state.correlation_id},status_code=exc.status_code,headers=exc.headers)

@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse({'code':'invalid_input','message':'Input does not satisfy the API contract','correlation_id':request.state.correlation_id},status_code=422)

class StrictModel(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
class Submission(StrictModel):
    content: str = Field(min_length=20,max_length=10000)
class Review(StrictModel):
    decision: Literal['accepted','revision_requested']
    feedback: str = Field(min_length=3,max_length=2000)
    expected_revision: int = Field(default=1,ge=1)
class ToolRequest(StrictModel):
    name: str = Field(max_length=80)
    arguments: dict = Field(default_factory=dict)

def audit(ctx, request, action, resource=None):
    ctx.conn.execute(text('INSERT INTO audit_events(id,tenant_id,subject,action,resource_id,correlation_id) VALUES(:id,:t,:s,:a,:r,:c)'),
      {'id':uuid4(),'t':ctx.tenant_id,'s':ctx.sub,'a':action,'r':resource,'c':request.state.correlation_id})

def course(ctx, course_id):
    item=one(ctx.conn,'SELECT * FROM courses WHERE id=:id',id=course_id)
    if not item: raise HTTPException(404,'Course not found')
    return item

def enrollment(ctx, course_id, lock=False):
    item=one(ctx.conn,'SELECT * FROM enrollments WHERE course_id=:c AND subject=:s'+(' FOR UPDATE' if lock else ''),c=course_id,s=ctx.sub)
    if not item: raise HTTPException(409,'Enroll before continuing')
    return item

def course_list(ctx):
    result=rows(ctx.conn,'SELECT id,title,description,metadata FROM courses ORDER BY title')
    for c in result:
        c['lessons']=rows(ctx.conn,'SELECT id,title,content,position,metadata FROM lessons WHERE course_id=:id ORDER BY position',id=c['id'])
        e=one(ctx.conn,'SELECT id FROM enrollments WHERE course_id=:id AND subject=:s',id=c['id'],s=ctx.sub)
        c['enrolled']=bool(e)
        c['completed_lessons']=[str(r['lesson_id']) for r in rows(ctx.conn,'SELECT lesson_id FROM completions WHERE enrollment_id=:e',e=e['id'])] if e else []
    return result

@app.get('/api/health')
def health():
    with engine.connect() as c: c.execute(text('SELECT 1'))
    return {'status':'ok','version':'0.3.0'}

@app.get('/api/me')
def me(ctx:Context=Depends(authenticated, scope='function')):
    return {'sub':ctx.sub,'tenant_id':ctx.tenant_id,'role':ctx.role}

@app.get('/api/courses')
def courses(ctx:Context=Depends(authenticated, scope='function')): return course_list(ctx)

@app.post('/api/courses/{course_id}/enroll')
def enroll(course_id:UUID, request:Request, ctx:Context=Depends(authenticated, scope='function')):
    course(ctx,course_id)
    ctx.conn.execute(text('INSERT INTO enrollments(id,tenant_id,course_id,subject) VALUES(:id,:t,:c,:s) ON CONFLICT(tenant_id,course_id,subject) DO NOTHING'),{'id':uuid4(),'t':ctx.tenant_id,'c':course_id,'s':ctx.sub})
    audit(ctx,request,'enroll',course_id)
    return enrollment(ctx,course_id)

@app.post('/api/courses/{course_id}/lessons/{lesson_id}/complete')
def complete(course_id:UUID, lesson_id:UUID, request:Request, ctx:Context=Depends(authenticated, scope='function')):
    course(ctx,course_id); e=enrollment(ctx,course_id,True)
    lessons=rows(ctx.conn,'SELECT id FROM lessons WHERE course_id=:c ORDER BY position',c=course_id)
    done=rows(ctx.conn,'SELECT lesson_id FROM completions WHERE enrollment_id=:id',id=e['id'])
    try: needed=next_completion([str(x['id']) for x in lessons],[str(x['lesson_id']) for x in done],str(lesson_id))
    except ValueError as error: raise HTTPException(409,str(error))
    if needed:
        ctx.conn.execute(text('INSERT INTO completions(tenant_id,enrollment_id,lesson_id) VALUES(:t,:e,:l)'),{'t':ctx.tenant_id,'e':e['id'],'l':lesson_id})
        audit(ctx,request,'lesson_complete',lesson_id)
    return {'completed':True,'replayed':not needed}

@app.post('/api/courses/{course_id}/submissions')
def submit(course_id:UUID, body:Submission, request:Request, ctx:Context=Depends(authenticated, scope='function')):
    current=course(ctx,course_id); e=enrollment(ctx,course_id,True)
    assessment=current.get('metadata',{}).get('assessment',{})
    if not assessment.get('minCharacters',20) <= len(body.content) <= assessment.get('maxCharacters',10000):
        raise HTTPException(422,'Evidence length does not satisfy this course assessment')
    total=one(ctx.conn,'SELECT count(*) AS n FROM lessons WHERE course_id=:c',c=course_id)['n']
    done=one(ctx.conn,'SELECT count(*) AS n FROM completions WHERE enrollment_id=:e',e=e['id'])['n']
    if done != total: raise HTTPException(409,'Complete all lessons before submitting evidence')
    # Repeated identical submissions return the existing immutable evidence record.
    existing=one(ctx.conn,'SELECT * FROM submissions WHERE course_id=:c AND subject=:s AND content=:content ORDER BY created_at DESC LIMIT 1',c=course_id,s=ctx.sub,content=body.content)
    if existing: return existing
    result=one(ctx.conn,'INSERT INTO submissions(id,tenant_id,course_id,subject,content) VALUES(:id,:t,:c,:s,:content) RETURNING *',id=uuid4(),t=ctx.tenant_id,c=course_id,s=ctx.sub,content=body.content)
    audit(ctx,request,'submit',result['id']); return result

@app.get('/api/submissions')
def submissions(ctx:Context=Depends(authenticated, scope='function')):
    return rows(ctx.conn,'SELECT * FROM submissions'+('' if ctx.role=='reviewer' else ' WHERE subject=:s')+' ORDER BY created_at DESC',s=ctx.sub)

@app.post('/api/submissions/{submission_id}/review')
def review(submission_id:UUID, body:Review, request:Request, ctx:Context=Depends(authenticated, scope='function')):
    if ctx.role!='reviewer': raise HTTPException(403,'Reviewer role required')
    item=one(ctx.conn,'SELECT * FROM submissions WHERE id=:id FOR UPDATE',id=submission_id)
    if not item: raise HTTPException(404,'Submission not found')
    if item['revision']!=body.expected_revision: raise HTTPException(409,'Stale submission revision')
    try: state=review_transition(item['status'],str(item['subject']),ctx.sub,body.decision)
    except ValueError as error: raise HTTPException(409,str(error))
    result=one(ctx.conn,'UPDATE submissions SET status=:state,feedback=:f,reviewer=:s,revision=revision+1 WHERE id=:id RETURNING *',state=state,f=body.feedback,s=ctx.sub,id=submission_id)
    audit(ctx,request,'review',submission_id); return result

@app.get('/api/progress')
def progress(ctx:Context=Depends(authenticated, scope='function')):
    return {'enrollments':rows(ctx.conn,'SELECT * FROM enrollments WHERE subject=:s',s=ctx.sub),'submissions':rows(ctx.conn,'SELECT * FROM submissions WHERE subject=:s ORDER BY created_at DESC',s=ctx.sub),'courses':course_list(ctx)}

@app.get('/api/workshops')
def workshops(ctx:Context=Depends(authenticated, scope='function')):
    result=rows(ctx.conn,'SELECT * FROM workshops ORDER BY starts_at')
    for w in result:
        w['registered']=bool(one(ctx.conn,'SELECT subject FROM registrations WHERE workshop_id=:w AND subject=:s',w=w['id'],s=ctx.sub))
        w['registrations']=one(ctx.conn,'SELECT count(*) AS n FROM registrations WHERE workshop_id=:w',w=w['id'])['n']
        w['integration_status']='videoconferencing_not_integrated'
    return result

@app.post('/api/workshops/{workshop_id}/register')
def register(workshop_id:UUID,request:Request,ctx:Context=Depends(authenticated, scope='function')):
    w=one(ctx.conn,'SELECT * FROM workshops WHERE id=:id FOR UPDATE',id=workshop_id)
    if not w: raise HTTPException(404,'Workshop not found')
    existing=one(ctx.conn,'SELECT * FROM registrations WHERE workshop_id=:w AND subject=:s',w=workshop_id,s=ctx.sub)
    if existing:return {'registered':True,'replayed':True}
    count=one(ctx.conn,'SELECT count(*) AS n FROM registrations WHERE workshop_id=:w',w=workshop_id)['n']
    if count>=w['capacity']:raise HTTPException(409,'Workshop capacity reached')
    ctx.conn.execute(text('INSERT INTO registrations(tenant_id,workshop_id,subject) VALUES(:t,:w,:s)'),{'t':ctx.tenant_id,'w':workshop_id,'s':ctx.sub})
    audit(ctx,request,'workshop_register',workshop_id)
    return {'registered':True,'replayed':False}

@app.get('/api/capabilities')
def capabilities(ctx:Context=Depends(authenticated, scope='function')):
    return {'authentication':'operational','learning':'operational','workshops':'registration_only','videoconferencing':'not_integrated','ai_provider':'disabled','mcp':'not_integrated','tools':'read_only_progress','credentials':'not_issued'}

@app.post('/api/tools/invoke')
def invoke(body:ToolRequest,request:Request,ctx:Context=Depends(authenticated, scope='function')):
    # Control: no model-selected context, writes, network access or unlimited executions.
    reason = None
    if os.environ.get('TOOLS_ENABLED','false').lower() != 'true':
        reason = 'Tool execution disabled'
    elif body.name!='learning.progress' or body.arguments:
        reason = 'Tool or arguments not permitted'
    ctx.conn.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:sub,0))'), {'sub':ctx.sub})
    count = one(ctx.conn,"SELECT count(*) AS n FROM audit_events WHERE subject=:s AND action LIKE 'tool_%' AND created_at > now()-interval '1 minute'",s=ctx.sub)['n']
    if count >= 20:
        reason = 'Tool budget exhausted'
    if reason:
        audit(ctx,request,'tool_denied')
        return JSONResponse({'code':'tool_denied','message':reason},status_code=403)
    # Tool context needs bounded progress facts, not entire authored lessons or learner evidence.
    summary = {
        'enrolled_courses': one(ctx.conn,'SELECT count(*) AS n FROM enrollments WHERE subject=:s',s=ctx.sub)['n'],
        'completed_lessons': one(ctx.conn,'SELECT count(*) AS n FROM completions c JOIN enrollments e ON c.enrollment_id=e.id WHERE e.subject=:s',s=ctx.sub)['n'],
        'submission_records_by_status': {r['status']:r['n'] for r in rows(ctx.conn,'SELECT status,count(*) AS n FROM submissions WHERE subject=:s GROUP BY status',s=ctx.sub)},
        'scope': 'own tenant-bound participation records; not competency certification',
    }
    result = jsonable_encoder({'tool':'learning.progress','version':'2','result':summary})
    if len(json.dumps(result,ensure_ascii=False).encode()) > 32768:
        audit(ctx,request,'tool_result_limit')
        return JSONResponse({'code':'result_limit','message':'Tool result limit exceeded'},status_code=413)
    audit(ctx,request,'tool_learning_progress')
    return result

from .content_api import router as content_router
app.include_router(content_router)
