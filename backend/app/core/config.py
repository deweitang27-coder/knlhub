import os
import json
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "sqlite")

if DB_TYPE == "sqlite":
    DATABASE_URL = "sqlite+aiosqlite:///./app.db"
else:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME = os.getenv("DB_NAME", "ai_knowledge_base")
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production-abc123xyz789")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7

ALLOWED_FILE_TYPES = [".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".xlsx", ".pptx"]

# ============ User-level settings cache ============

# 内存缓存：user_id -> settings dict
_user_settings_cache: dict = {}

def _set_cache(user_id: str, settings: dict):
    _user_settings_cache[user_id] = settings

def set_user_settings(user_id: str, settings: dict):
    """更新用户设置缓存（调用方负责持久化到数据库）"""
    _set_cache(user_id, settings)

def _get_settings(user_id: str) -> dict:
    return _user_settings_cache.get(user_id, {})

def _get_setting(user_id: str, key: str, default):
    """从缓存或环境变量获取用户级设置"""
    user_settings = _get_settings(user_id) if user_id else {}
    val = user_settings.get(key)
    if val is not None and val != "":
        return val
    return default

# ============ Config accessors ============

def get_embedding_api_key(user_id: str = None) -> str:
    return _get_setting(user_id, "embedding_api_key", os.getenv("EMBEDDING_API_KEY", ""))

def get_llm_api_key(user_id: str = None) -> str:
    return _get_setting(user_id, "llm_api_key", os.getenv("LLM_API_KEY", ""))

def get_embedding_provider(user_id: str = None) -> str:
    return _get_setting(user_id, "embedding_provider", os.getenv("EMBEDDING_PROVIDER", "tongyi"))

def get_llm_provider(user_id: str = None) -> str:
    return _get_setting(user_id, "llm_provider", os.getenv("LLM_PROVIDER", "deepseek"))

def get_embedding_model(user_id: str = None) -> str:
    return _get_setting(user_id, "embedding_model", os.getenv("EMBEDDING_MODEL", "text-embedding-v3"))

def get_llm_model(user_id: str = None) -> str:
    return _get_setting(user_id, "llm_model", os.getenv("LLM_MODEL", "deepseek-chat"))

def get_embedding_base_url(user_id: str = None) -> str:
    return _get_setting(user_id, "embedding_base_url", os.getenv("EMBEDDING_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"))

def get_llm_base_url(user_id: str = None) -> str:
    return _get_setting(user_id, "llm_base_url", os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"))

def get_chunk_size(user_id: str = None) -> int:
    raw = _get_setting(user_id, "chunk_size", os.getenv("CHUNK_SIZE", "512"))
    return int(raw)

def get_chunk_overlap(user_id: str = None) -> int:
    raw = _get_setting(user_id, "chunk_overlap", os.getenv("CHUNK_OVERLAP", "64"))
    return int(raw)

def get_top_k(user_id: str = None) -> int:
    raw = _get_setting(user_id, "top_k", os.getenv("TOP_K", "5"))
    return int(raw)

def get_max_file_size(user_id: str = None) -> int:
    mb = int(_get_setting(user_id, "max_file_size_mb", os.getenv("MAX_FILE_SIZE", "52428800")))
    if mb > 1000:
        return mb
    return mb * 1024 * 1024
