"""Portable package admission: tenant and publication authority never come from content."""
import json
from uuid import UUID, uuid4, uuid5, NAMESPACE_URL
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
from .auth import Context, authenticated
from .db import one, rows
from content.validate_package import load_package, validate_package

router = APIRouter()
MAX_PACKAGE_BYTES = 131072

class PublishRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_digest: str = Field(pattern=r'^[0-9a-f]{64}$')
    expected_revision: int = Field(ge=1)

def reviewer(ctx):
    if ctx.role != 'reviewer':
        raise HTTPException(403, 'Reviewer role required for local content admission')

def emit(ctx,request,action,resource):
    ctx.conn.execute(text('INSERT INTO audit_events(id,tenant_id,subject,action,resource_id,correlation_id) VALUES(:id,:t,:s,:a,:r,:c)'),
       dict(id=uuid4(),t=ctx.tenant_id,s=ctx.sub,a=action,r=resource,c=request.state.correlation_id))

def summary(row,replayed=False):
    return {k:row[k] for k in ('id','package_id','version','digest','status','revision','course_id')} | {'replayed':replayed}

def mapped_id(tenant, package, version, source):
    return uuid5(NAMESPACE_URL,f'nikway-content:{tenant}:{package}:{version}:{source}')

@router.post('/api/content-packages')
async def import_package(request:Request,ctx:Context=Depends(authenticated,scope='function')):
    reviewer(ctx)
    raw=bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw)>MAX_PACKAGE_BYTES:
            raise HTTPException(413,'Content package exceeds 128 KiB')
    # PostgreSQL locks must not block the event loop that completes earlier transactions.
    return await run_in_threadpool(admit,bytes(raw),request,ctx)

def admit(raw,request,ctx):
    try:
        package=load_package(raw)
        errors=validate_package(package)
    except (ValueError,TypeError,UnicodeError):
        raise HTTPException(422,'Invalid portable content package')
    if errors:
        raise HTTPException(422,{'code':'package_validation_failed','errors':errors[:20]})
    key=f'{ctx.tenant_id}:{package["packageId"]}:{package["version"]}'
    ctx.conn.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,0))'),{'key':key})
    existing=one(ctx.conn,'SELECT * FROM content_packages WHERE package_id=:p AND version=:v',p=package['packageId'],v=package['version'])
    if existing:
        if existing['digest'] != package['integrity']['digest']:
            raise HTTPException(409,'Version already exists with different content; create a new version')
        return summary(existing,True)
    row=one(ctx.conn,'INSERT INTO content_packages(id,tenant_id,package_id,version,digest,document,imported_by) VALUES(:id,:t,:p,:v,:d,CAST(:doc AS jsonb),:s) RETURNING *',
       id=uuid4(),t=ctx.tenant_id,p=package['packageId'],v=package['version'],d=package['integrity']['digest'],doc=json.dumps(package,ensure_ascii=False),s=ctx.sub)
    emit(ctx,request,'content_import',row['id'])
    return summary(row)

@router.get('/api/content-packages')
def list_packages(ctx:Context=Depends(authenticated,scope='function')):
    reviewer(ctx)
    return [summary(r) for r in rows(ctx.conn,'SELECT * FROM content_packages ORDER BY imported_at DESC')]

@router.post('/api/content-packages/{package_id}/publish')
def publish(package_id:UUID,body:PublishRequest,request:Request,ctx:Context=Depends(authenticated,scope='function')):
    reviewer(ctx)
    ctx.conn.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:id,0))'),{'id':str(package_id)})
    item=one(ctx.conn,'SELECT * FROM content_packages WHERE id=:id',id=package_id)
    if not item: raise HTTPException(404,'Package not found')
    if item['digest'] != body.expected_digest: raise HTTPException(409,'Package digest mismatch')
    if item['status']=='published':
        # Retry of the original publication intent is safe; no duplicated course.
        if body.expected_revision not in (item['revision']-1,item['revision']):
            raise HTTPException(409,'Stale package revision')
        return summary(item,True)
    if item['revision'] != body.expected_revision: raise HTTPException(409,'Stale package revision')
    package=item['document']
    if validate_package(package): raise HTTPException(409,'Stored package fails current admission validation')
    source=package['course']
    course_id=mapped_id(ctx.tenant_id,package['packageId'],package['version'],source['id'])
    metadata={k:v for k,v in source.items() if k not in ('id','title','description','lessons')}
    metadata.update(packageId=package['packageId'],version=package['version'],rights=package['rights'],provenance=package['provenance'])
    ctx.conn.execute(text('INSERT INTO courses(id,tenant_id,title,description,metadata) VALUES(:id,:t,:title,:description,CAST(:metadata AS jsonb))'),dict(id=course_id,t=ctx.tenant_id,title=source['title'],description=source['description'],metadata=json.dumps(metadata,ensure_ascii=False)))
    for lesson in source['lessons']:
        lid=mapped_id(ctx.tenant_id,package['packageId'],package['version'],lesson['id'])
        ctx.conn.execute(text('INSERT INTO lessons(id,tenant_id,course_id,position,title,content,metadata) VALUES(:id,:t,:c,:position,:title,:content,CAST(:metadata AS jsonb))'),dict(id=lid,t=ctx.tenant_id,c=course_id,position=lesson['position'],title=lesson['title'],content=lesson['content'],metadata=json.dumps({k:v for k,v in lesson.items() if k not in ('id','position','title','content')},ensure_ascii=False)))
    result=one(ctx.conn,"UPDATE content_packages SET status='published',revision=revision+1,published_at=now(),course_id=:c WHERE id=:id RETURNING *",c=course_id,id=package_id)
    emit(ctx,request,'content_publish',package_id)
    return summary(result)

@router.get('/api/courses/{course_id}/package')
def export_package(course_id:UUID,ctx:Context=Depends(authenticated,scope='function')):
    row=one(ctx.conn,"SELECT document FROM content_packages WHERE course_id=:c AND status='published'",c=course_id)
    if not row: raise HTTPException(404,'Published portable package not found')
    return row['document']
