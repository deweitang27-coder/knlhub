import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.api.routes import auth, documents, query, settings, statistics, conversations, skills
from app.core.database import engine, async_session
from app.core.config import DB_TYPE
from app.models.models import Base

def _apply_sqlite_migrations():
    """Apply migrations for SQLite databases"""
    if DB_TYPE != "sqlite":
        return
    
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.db")
    if not os.path.exists(db_path):
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if settings column exists in users table
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "settings" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN settings JSON DEFAULT '{}'")
        conn.commit()
        print("Migration applied: added 'settings' column to users table")
    
    # Check if usage_records table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usage_records'")
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE usage_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                query_text TEXT NOT NULL,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                model_used TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Migration applied: created 'usage_records' table")

    # Check if conversation_sessions table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_sessions'")
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE conversation_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                title TEXT DEFAULT '新对话',
                messages JSON DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Migration applied: created 'conversation_sessions' table")
    
    # Check if skills table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skills'")
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE skills (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT DEFAULT 'zap',
                color TEXT DEFAULT '#10b981',
                system_prompt TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Migration applied: created 'skills' table")

    # Check if agent_conversations table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_conversations'")
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE agent_conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                title TEXT DEFAULT '新对话',
                messages JSON DEFAULT '[]',
                active_skills JSON DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Migration applied: created 'agent_conversations' table")
    
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("uploads", exist_ok=True)
    _apply_sqlite_migrations()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if DB_TYPE == "postgres":
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    yield

app = FastAPI(
    title="KnlHub API",
    description="KnlHub - 智能问答系统后端服务",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(query.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(skills.router, prefix="/api")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "ai-knowledge-base-api"}
