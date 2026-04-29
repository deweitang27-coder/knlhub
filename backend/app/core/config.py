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

SETTINGS_FILE = os.path.join(project_root, "backend", "app_settings.json")

def _get_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

_settings_cache = None

def get_runtime_settings():
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = _get_settings()
    return _settings_cache

def reload_settings():
    global _settings_cache
    _settings_cache = _get_settings()
    return _settings_cache

def get_embedding_api_key():
    s = get_runtime_settings()
    return s.get("embedding_api_key", "") or os.getenv("EMBEDDING_API_KEY", "")

def get_llm_api_key():
    s = get_runtime_settings()
    return s.get("llm_api_key", "") or os.getenv("LLM_API_KEY", "")

def get_embedding_provider():
    s = get_runtime_settings()
    return s.get("embedding_provider", "") or os.getenv("EMBEDDING_PROVIDER", "tongyi")

def get_llm_provider():
    s = get_runtime_settings()
    return s.get("llm_provider", "") or os.getenv("LLM_PROVIDER", "deepseek")

def get_embedding_model():
    s = get_runtime_settings()
    return s.get("embedding_model", "") or os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

def get_llm_model():
    s = get_runtime_settings()
    return s.get("llm_model", "") or os.getenv("LLM_MODEL", "deepseek-chat")

def get_embedding_base_url():
    s = get_runtime_settings()
    return os.getenv("EMBEDDING_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

def get_llm_base_url():
    s = get_runtime_settings()
    return os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")

def get_chunk_size():
    s = get_runtime_settings()
    return int(s.get("chunk_size", os.getenv("CHUNK_SIZE", "512")))

def get_chunk_overlap():
    s = get_runtime_settings()
    return int(s.get("chunk_overlap", os.getenv("CHUNK_OVERLAP", "64")))

def get_top_k():
    s = get_runtime_settings()
    return int(s.get("top_k", os.getenv("TOP_K", "5")))

def get_max_file_size():
    s = get_runtime_settings()
    mb = int(s.get("max_file_size_mb", os.getenv("MAX_FILE_SIZE", "52428800")))
    if mb > 1000:
        return mb
    return mb * 1024 * 1024

ALLOWED_FILE_TYPES = [".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".xlsx", ".pptx"]
