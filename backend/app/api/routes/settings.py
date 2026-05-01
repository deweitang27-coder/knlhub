from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import set_user_settings
from app.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/settings", tags=["设置"])

DEFAULT_SETTINGS = {
    "embedding_api_key": "",
    "llm_api_key": "",
    "embedding_provider": "tongyi",
    "llm_provider": "deepseek",
    "embedding_model": "text-embedding-v3",
    "llm_model": "deepseek-chat",
    "chunk_size": 512,
    "chunk_overlap": 64,
    "top_k": 5,
    "max_file_size_mb": 50,
}

class SettingsData(BaseModel):
    embedding_api_key: str = ""
    llm_api_key: str = ""
    embedding_provider: str = "tongyi"
    llm_provider: str = "deepseek"
    embedding_model: str = "text-embedding-v3"
    llm_model: str = "deepseek-chat"
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 5
    max_file_size_mb: int = 50

@router.get("/")
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one()
    settings = user.settings or {}
    return {**DEFAULT_SETTINGS, **settings}

@router.post("/")
async def save_settings_route(
    data: SettingsData,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settings = {
        "embedding_api_key": data.embedding_api_key,
        "llm_api_key": data.llm_api_key,
        "embedding_provider": data.embedding_provider,
        "llm_provider": data.llm_provider,
        "embedding_model": data.embedding_model,
        "llm_model": data.llm_model,
        "chunk_size": data.chunk_size,
        "chunk_overlap": data.chunk_overlap,
        "top_k": data.top_k,
        "max_file_size_mb": data.max_file_size_mb,
    }

    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one()
    user.settings = settings
    await db.commit()

    set_user_settings(current_user.id, settings)

    return {"message": "设置已保存", "settings": settings}
