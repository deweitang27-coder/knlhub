from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User, Document, UsageRecord
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/statistics", tags=["统计"])

@router.get("/")
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    doc_result = await db.execute(
        select(func.count(Document.id)).where(Document.user_id == current_user.id)
    )
    total_docs = doc_result.scalar()

    chunk_result = await db.execute(
        select(func.sum(Document.chunk_count)).where(
            Document.user_id == current_user.id,
            Document.status == "completed",
        )
    )
    total_chunks = chunk_result.scalar() or 0

    query_today = await db.execute(
        select(func.count(UsageRecord.id)).where(
            UsageRecord.user_id == current_user.id,
            UsageRecord.created_at >= today.replace(hour=0, minute=0, second=0, microsecond=0),
        )
    )
    queries_today = query_today.scalar()

    query_week = await db.execute(
        select(func.count(UsageRecord.id)).where(
            UsageRecord.user_id == current_user.id,
            UsageRecord.created_at >= week_ago,
        )
    )
    queries_week = query_week.scalar()

    query_month = await db.execute(
        select(func.count(UsageRecord.id)).where(
            UsageRecord.user_id == current_user.id,
            UsageRecord.created_at >= month_ago,
        )
    )
    queries_month = query_month.scalar()

    query_total = await db.execute(
        select(func.count(UsageRecord.id)).where(UsageRecord.user_id == current_user.id)
    )
    queries_total = query_total.scalar()

    tokens_week = await db.execute(
        select(func.sum(UsageRecord.total_tokens)).where(
            UsageRecord.user_id == current_user.id,
            UsageRecord.created_at >= week_ago,
        )
    )
    tokens_week = tokens_week.scalar() or 0

    tokens_month = await db.execute(
        select(func.sum(UsageRecord.total_tokens)).where(
            UsageRecord.user_id == current_user.id,
            UsageRecord.created_at >= month_ago,
        )
    )
    tokens_month = tokens_month.scalar() or 0

    tokens_total = await db.execute(
        select(func.sum(UsageRecord.total_tokens)).where(UsageRecord.user_id == current_user.id)
    )
    tokens_total = tokens_total.scalar() or 0

    recent_docs = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .limit(5)
    )
    recent_docs_list = [
        {
            "id": d.id,
            "filename": d.filename,
            "status": d.status,
            "created_at": d.created_at.isoformat(),
        }
        for d in recent_docs.scalars().all()
    ]

    return {
        "documents": {
            "total": total_docs,
            "completed_chunks": total_chunks,
            "recent": recent_docs_list,
        },
        "queries": {
            "today": queries_today,
            "week": queries_week,
            "month": queries_month,
            "total": queries_total,
        },
        "tokens": {
            "week": tokens_week,
            "month": tokens_month,
            "total": tokens_total,
        },
    }
