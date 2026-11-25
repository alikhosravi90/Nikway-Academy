import os
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import Field
from .contracts import Strict,ComponentInput
from .db import Database
from .errors import DomainError
from .pipeline import Pipeline
from .store import Repository

class Create(Strict):
    component: ComponentInput
    expectedRevision: int = Field(ge=0)
class Note(Strict):
    note: str = Field(min_length=1,max_length=2000)
class Prepare(Strict):
    courseId: str = Field(min_length=1,max_length=100)
    revisionIds: list[str] = Field(min_length=1,max_length=30)
    idempotencyKey: str = Field(min_length=1,max_length=120)
class Plan(Strict):
    component: ComponentInput
    objective: str = Field(min_length=1,max_length=2000)
class Act(Strict):
    courseId: str = Field(min_length=1,max_length=100)
    idempotencyKey: str = Field(min_length=1,max_length=120)

class SizeLimit:
    """Bound the actual request stream, including chunked bodies."""
    def __init__(self,app): self.app=app
    async def __call__(self,scope,receive,send):
        if scope['type']!='http': return await self.app(scope,receive,send)
        chunks=[]; size=0
        while True:
            message=await receive()
            if message['type']=='http.disconnect': return
            size+=len(message.get('body',b''))
            if size>300000:
                await JSONResponse({'detail':'payload too large'},status_code=413)(scope,receive,send); return
            chunks.append(message)
            if not message.get('more_body'): break
        index=0
        async def buffered():
            nonlocal index
            if index<len(chunks):
                m=chunks[index]; index+=1; return m
            return await receive()
        await self.app(scope,buffered,send)

def create_app(repo):
    app=FastAPI(title='NIKWAY Content Factory — Local MVP',version='0.1.0')
    app.add_middleware(SizeLimit)
    security=HTTPBearer(auto_error=False)
    pipeline=Pipeline(repo)
    def context(credentials:HTTPAuthorizationCredentials|None=Depends(security)):
        if credentials is None: raise DomainError('authentication required',401)
        return repo.db.authenticate(credentials.credentials)

    @app.middleware('http')
    async def headers(request:Request,call_next):
        response=await call_next(request)
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        return response

    @app.exception_handler(DomainError)
    async def domain_error(request,exc):
        return JSONResponse({'detail':str(exc)},status_code=exc.status)

    @app.get('/health')
    def health():
        return {'status':'ok','scope':'local-synthetic','publication':'disabled'}

    @app.get('/v1/components')
    def search(q:str='',ctx=Depends(context)): return repo.search(ctx,q[:200])

    @app.post('/v1/components',status_code=201)
    def create(body:Create,ctx=Depends(context)): return repo.create_revision(ctx,body.component,body.expectedRevision)

    @app.get('/v1/revisions/{rid}')
    def revision(rid:str,ctx=Depends(context)): return repo.get_revision(ctx,rid)

    @app.post('/v1/revisions/{rid}/review')
    def review(rid:str,body:Note,ctx=Depends(context)): return repo.review(ctx,rid,body.note)

    @app.post('/v1/revisions/{rid}/withdraw')
    def withdraw(rid:str,body:Note,ctx=Depends(context)): return repo.withdraw(ctx,rid,body.note)

    @app.post('/v1/candidates')
    def prepare(body:Prepare,ctx=Depends(context)): return repo.prepare(ctx,body.courseId,body.revisionIds,body.idempotencyKey)

    @app.get('/v1/candidates/{cid}')
    def candidate(cid:str,ctx=Depends(context)): return repo.candidate(ctx,cid)

    @app.get('/v1/candidates/{cid}/package')
    def package(cid:str,ctx=Depends(context)):
        return Response(repo.package(ctx,cid),media_type='application/zip',headers={'Content-Disposition':'attachment; filename="pdca-candidate.zip"'})

    @app.get('/v1/events')
    def events(ctx=Depends(context)): return repo.events(ctx)

    @app.post('/v1/pipelines',status_code=201)
    def plan(body:Plan,ctx=Depends(context)): return pipeline.plan(ctx,body.component,body.objective)

    @app.post('/v1/pipelines/{rid}/do')
    def do(rid:str,ctx=Depends(context)): return pipeline.do(ctx,rid)

    @app.post('/v1/pipelines/{rid}/check')
    def check(rid:str,ctx=Depends(context)): return pipeline.check(ctx,rid)

    @app.post('/v1/pipelines/{rid}/act')
    def act(rid:str,body:Act,ctx=Depends(context)): return pipeline.act(ctx,rid,body.courseId,body.idempotencyKey)
    return app

# Import without configuration remains safe for test factories.
if os.environ.get('CF_DATABASE_URL'):
    app=create_app(Repository(Database(os.environ['CF_DATABASE_URL']),os.environ['CF_OBJECT_ROOT']))
