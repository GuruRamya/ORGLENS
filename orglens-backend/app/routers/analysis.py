from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4, UUID
from datetime import datetime
from loguru import logger
from app.config import settings
from app.database import get_db
from app.models import Organization, AnalysisReport, AnalysisStatus, Message, Employee
from app.schemas.analysis import AnalysisTriggerResponse, AnalysisStatusResponse
from app.services.auth import get_current_user, require_org_access
from app.models.auth import User

router = APIRouter()


@router.post("/trigger/{org_id}")
async def trigger_analysis(
    org_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AnalysisTriggerResponse:
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    msg_result = await db.execute(
        select(Message).where(Message.org_id == org_id).limit(1)
    )
    if not msg_result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="No communication data found. Please upload data first."
        )

    try:
        analysis = AnalysisReport(
            id=uuid4(),
            org_id=org_id,
            status=AnalysisStatus.PENDING,
        )
        db.add(analysis)
        await db.commit()
        from app.workers.analysis_tasks import _async_analysis_pipeline
        background_tasks.add_task(
            _async_analysis_pipeline,
            str(org_id),
            str(analysis.id)
        )

        logger.info(f"✅ Analysis triggered for org {org.name}: {analysis.id}")

        return AnalysisTriggerResponse(
            analysis_id=analysis.id,
            org_id=org_id,
            status="queued",
            message="Analysis queued. Processing will begin shortly.",
            estimated_minutes=5
        )

    except Exception as e:
        logger.error(f"Analysis trigger error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{analysis_id}")
async def get_analysis_status(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await db.execute(
            select(AnalysisReport).where(AnalysisReport.id == UUID(analysis_id))
        )
        analysis = result.scalar_one_or_none()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return {
            "id": str(analysis.id),
            "status": analysis.status.value if analysis.status else "pending",
            "progress": analysis.progress or 0,  
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#async def get_redis():
    #global _redis_client

    #print("GET REDIS CALLED")
    #if _redis_client is None and REDIS_AVAILABLE:
        #import os
        #import ssl
        #url = os.getenv("redis_url")
        #print("REDIS URL:", url)
        #try:
            #_redis_client = aioredis.from_url(
                #url,
                #decode_responses=True,
                #ssl_cert_reqs=ssl.CERT_NONE
            #)
            #await _redis_client.ping()
            #print("REDIS CONNECTED")
        #except Exception as e:
            #print("REDIS FAILED:", e)
            #_redis_client = None
    #return _redis_client

@router.get("/latest/{org_id}")
async def get_latest_analysis(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(AnalysisReport)
        .where(
            (AnalysisReport.org_id == org_id) &
            (AnalysisReport.status == AnalysisStatus.COMPLETED)
        )
        .order_by(AnalysisReport.created_at.desc())
        .limit(1)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="No completed analysis found")
    return {
        "analysis_id": str(analysis.id),
        "org_id": str(analysis.org_id),
        "status": analysis.status.value,
        "created_at": analysis.created_at,
        "completed_at": analysis.completed_at,
        "messages_analyzed": analysis.messages_analyzed,
        "decisions_extracted": analysis.decisions_extracted,
    }


@router.get("/list/{org_id}")
async def list_analyses(
    org_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(AnalysisReport)
        .where(AnalysisReport.org_id == org_id)
        .order_by(AnalysisReport.created_at.desc())
        .limit(limit)
    )
    analyses = result.scalars().all()
    return [
        {
            "analysis_id": str(a.id),
            "status": a.status.value,
            "created_at": a.created_at,
            "completed_at": a.completed_at,
            "messages_analyzed": a.messages_analyzed,
        }
        for a in analyses
    ]
#from app.services.security.rate_limiter import rate_limit

#@router.get("/test-rate-limit")
#async def test(
    #_: None = Depends(
        #rate_limit(
            #"analysis",
            #max_calls=3,
            #window_seconds=60
        #)
    #)
#):
    #return {"message": "working"}
