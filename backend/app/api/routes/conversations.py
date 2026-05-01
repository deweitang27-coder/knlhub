import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User, ConversationSession
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/conversations", tags=["对话历史"])

class ConversationItem(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str

class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: list
    created_at: str
    updated_at: str

@router.get("/", response_model=list[ConversationItem])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConversationSession)
        .where(ConversationSession.user_id == current_user.id)
        .order_by(ConversationSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in sessions
    ]

@router.get("/{conv_id}", response_model=ConversationDetail)
async def get_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == conv_id,
            ConversationSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")

    return {
        "id": session.id,
        "title": session.title,
        "messages": session.messages,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }

@router.post("/")
async def create_conversation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = ConversationSession(
        user_id=current_user.id,
        title="新对话",
        messages=[],
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "id": session.id,
        "title": session.title,
        "messages": session.messages,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }

@router.post("/{conv_id}/message")
async def add_message(
    conv_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == conv_id,
            ConversationSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")

    messages = (session.messages or []) + [data]

    if session.title == "新对话" and data.get("role") == "user":
        session.title = data["content"][:30] + ("..." if len(data["content"]) > 30 else "")

    session.messages = messages
    await db.commit()
    await db.refresh(session)

    return {
        "id": session.id,
        "title": session.title,
        "messages": session.messages,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }

@router.delete("/{conv_id}")
async def delete_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == conv_id,
            ConversationSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")

    await db.delete(session)
    await db.commit()

    return {"message": "对话已删除"}
