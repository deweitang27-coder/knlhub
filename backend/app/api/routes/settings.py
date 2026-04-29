import os
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.models.models import User

router = APIRouter(prefix="/settings", tags=["设置"])

SETTINGS_FILE = "app_settings.json"

class SettingsData(BaseModel):
    embedding_api_key: str
    llm_api_key: str
    embedding_provider: str
    llm_provider: str
    embedding_model: str
    llm_model: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    max_file_size_mb: int

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_settings(data: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def apply_settings(data: dict) -> None:
    """Apply settings to environment variables for runtime effect"""
    if data.get("embedding_api_key"):
        os.environ["EMBEDDING_API_KEY"] = data["embedding_api_key"]
    if data.get("llm_api_key"):
        os.environ["LLM_API_KEY"] = data["llm_api_key"]
    if data.get("embedding_provider"):
        os.environ["EMBEDDING_PROVIDER"] = data["embedding_provider"]
    if data.get("llm_provider"):
        os.environ["LLM_PROVIDER"] = data["llm_provider"]
    if data.get("embedding_model"):
        os.environ["EMBEDDING_MODEL"] = data["embedding_model"]
    if data.get("llm_model"):
        os.environ["LLM_MODEL"] = data["llm_model"]
    if data.get("chunk_size"):
        os.environ["CHUNK_SIZE"] = str(data["chunk_size"])
    if data.get("chunk_overlap"):
        os.environ["CHUNK_OVERLAP"] = str(data["chunk_overlap"])
    if data.get("top_k"):
        os.environ["TOP_K"] = str(data["top_k"])
    if data.get("max_file_size_mb"):
        os.environ["MAX_FILE_SIZE"] = str(data["max_file_size_mb"] * 1024 * 1024)

@router.get("/")
async def get_settings(current_user: User = Depends(get_current_user)):
    settings = load_settings()
    return {
        "embedding_api_key": settings.get("embedding_api_key", ""),
        "llm_api_key": settings.get("llm_api_key", ""),
        "embedding_provider": settings.get("embedding_provider", "tongyi"),
        "llm_provider": settings.get("llm_provider", "deepseek"),
        "embedding_model": settings.get("embedding_model", "text-embedding-v3"),
        "llm_model": settings.get("llm_model", "deepseek-chat"),
        "chunk_size": int(settings.get("chunk_size", 512)),
        "chunk_overlap": int(settings.get("chunk_overlap", 64)),
        "top_k": int(settings.get("top_k", 5)),
        "max_file_size_mb": int(settings.get("max_file_size_mb", 50)),
    }

@router.post("/")
async def save_settings_route(
    data: SettingsData,
    current_user: User = Depends(get_current_user),
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
    save_settings(settings)
    apply_settings(settings)
    return {"message": "设置已保存", "settings": settings}
