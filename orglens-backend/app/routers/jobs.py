from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from loguru import logger

from app.database import get_db
from app.models import AnalysisReport, AnalysisStatus
from app.services.auth import get_current_user
from app.models.auth import User

router = APIRouter()


def _get_celery_inspect():
    try:
        from app.workers.celery_app import celery_app
        i = celery_app.control.inspect(timeout=2.0)
        return i
    except Exception as e:
        return None


@router.get("/active")
async def list_active_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inspect = _get_celery_inspect()
    active_tasks = []
    if inspect:
        try:
            active = inspect.active() or {}
            for worker, tasks in active.items():
                for task in tasks:
                    active_tasks.append({
                        "task_id": task.get("id"),
                        "name": task.get("name"),
                        "args": task.get("args"),
                        "started_at": task.get("time_start"),
                        "worker": worker,
                    })
        except Exception as e:
            logger.warning(f"Failed to get active tasks: {e}")

    result = await db.execute(
        select(AnalysisReport)
        .where(AnalysisReport.status == AnalysisStatus.PROCESSING)
        .order_by(AnalysisReport.created_at.desc())
        .limit(20)
    )
    db_jobs = result.scalars().all()

    return {
        "active_celery_tasks": active_tasks,
        "processing_analyses": [
            {
                "analysis_id": str(a.id),
                "org_id": str(a.org_id),
                "progress": a.progress,
                "started_at": a.created_at.isoformat(),
            }
            for a in db_jobs
        ],
    }


@router.get("/failed")
async def list_failed_jobs(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AnalysisReport)
        .where(AnalysisReport.status == AnalysisStatus.FAILED)
        .order_by(AnalysisReport.created_at.desc())
        .limit(limit)
    )
    failed = result.scalars().all()

    return {
        "failed_analyses": [
            {
                "analysis_id": str(a.id),
                "org_id": str(a.org_id),
                "error": a.error_message,
                "failed_at": a.completed_at.isoformat() if a.completed_at else None,
                "created_at": a.created_at.isoformat(),
            }
            for a in failed
        ],
        "total": len(failed),
    }


@router.post("/retry/{analysis_id}")
async def retry_failed_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        analysis = await db.get(AnalysisReport, UUID(analysis_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if analysis.status not in (AnalysisStatus.FAILED, AnalysisStatus.PENDING):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry analysis in '{analysis.status.value}' state. Only FAILED or PENDING allowed.",
        )

    analysis.status = AnalysisStatus.PENDING
    analysis.progress = 0
    analysis.error_message = None
    analysis.completed_at = None
    await db.commit()

    try:
        from app.workers.analysis_tasks import analyze_organization
        task = analyze_organization.delay(str(analysis.org_id), str(analysis.id))
        return {
            "analysis_id": analysis_id,
            "task_id": task.id,
            "status": "queued",
            "message": "Analysis re-queued successfully.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to dispatch retry: {str(e)}")


@router.get("/stats")
async def job_stats(current_user: User = Depends(get_current_user)):
    """Celery broker and worker stats."""
    inspect = _get_celery_inspect()
    stats = {"broker_reachable": False, "workers": []}

    if inspect:
        try:
            worker_stats = inspect.stats() or {}
            stats["broker_reachable"] = True
            stats["workers"] = [
                {
                    "name": name,
                    "total_tasks": data.get("total", {}),
                    "pool": data.get("pool", {}).get("implementation"),
                    "concurrency": data.get("pool", {}).get("max-concurrency"),
                }
                for name, data in worker_stats.items()
            ]
        except Exception as e:
            logger.warning(f"Stats unavailable: {e}")

    return stats
