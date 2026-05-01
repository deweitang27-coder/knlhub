from datetime import datetime
from typing import List, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from openai import AsyncOpenAI
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import (
    get_llm_provider,
    get_llm_model,
    get_llm_api_key,
    get_llm_base_url,
)
from app.models.models import User, Skill, AgentConversation
from sqlalchemy.ext.asyncio import AsyncSession
import json

router = APIRouter(prefix="/skills", tags=["AI技能"])

PROVIDER_BASE_URLS = {
    "deepseek": "https://api.deepseek.com/v1",
    "tongyi": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "kimi": "https://api.moonshot.cn/v1",
    "moonshot": "https://api.moonshot.cn/v1",
    "openai": "https://api.openai.com/v1",
}

def get_llm_client(user_id: str) -> AsyncOpenAI:
    base_url = get_llm_base_url(user_id) or PROVIDER_BASE_URLS.get(get_llm_provider(user_id).lower(), "https://api.deepseek.com/v1")
    return AsyncOpenAI(api_key=get_llm_api_key(user_id), base_url=base_url)

# ========== Skills ==========

class SkillCreate(BaseModel):
    name: str
    description: str
    icon: str = "zap"
    color: str = "#10b981"
    system_prompt: str

class SkillUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    system_prompt: str | None = None
    is_active: bool | None = None

class SkillItem(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    color: str
    system_prompt: str
    is_active: bool
    created_at: str
    updated_at: str

@router.get("/", response_model=list[SkillItem])
async def list_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Skill)
        .where(Skill.user_id == current_user.id)
        .order_by(Skill.created_at.desc())
    )
    skills = result.scalars().all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "icon": s.icon,
            "color": s.color,
            "system_prompt": s.system_prompt,
            "is_active": s.is_active,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in skills
    ]

@router.post("/", response_model=SkillItem)
async def create_skill(
    data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skill = Skill(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        icon=data.icon,
        color=data.color,
        system_prompt=data.system_prompt,
        is_active=True,
    )
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "icon": skill.icon,
        "color": skill.color,
        "system_prompt": skill.system_prompt,
        "is_active": skill.is_active,
        "created_at": skill.created_at.isoformat(),
        "updated_at": skill.updated_at.isoformat(),
    }

@router.get("/{skill_id}", response_model=SkillItem)
async def get_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Skill).where(
            Skill.id == skill_id,
            Skill.user_id == current_user.id,
        )
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "icon": skill.icon,
        "color": skill.color,
        "system_prompt": skill.system_prompt,
        "is_active": skill.is_active,
        "created_at": skill.created_at.isoformat(),
        "updated_at": skill.updated_at.isoformat(),
    }

@router.put("/{skill_id}", response_model=SkillItem)
async def update_skill(
    skill_id: str,
    data: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Skill).where(
            Skill.id == skill_id,
            Skill.user_id == current_user.id,
        )
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")

    if data.name is not None:
        skill.name = data.name
    if data.description is not None:
        skill.description = data.description
    if data.icon is not None:
        skill.icon = data.icon
    if data.color is not None:
        skill.color = data.color
    if data.system_prompt is not None:
        skill.system_prompt = data.system_prompt
    if data.is_active is not None:
        skill.is_active = data.is_active

    await db.commit()
    await db.refresh(skill)
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "icon": skill.icon,
        "color": skill.color,
        "system_prompt": skill.system_prompt,
        "is_active": skill.is_active,
        "created_at": skill.created_at.isoformat(),
        "updated_at": skill.updated_at.isoformat(),
    }

@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Skill).where(
            Skill.id == skill_id,
            Skill.user_id == current_user.id,
        )
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")

    await db.delete(skill)
    await db.commit()
    return {"message": "技能已删除"}


# ========== Agent Conversations ==========

class AgentConversationItem(BaseModel):
    id: str
    title: str
    active_skills: list
    created_at: str
    updated_at: str

class AgentConversationDetail(BaseModel):
    id: str
    title: str
    messages: list
    active_skills: list
    created_at: str
    updated_at: str

@router.get("/agent/conversations", response_model=list[AgentConversationItem])
async def list_agent_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AgentConversation)
        .where(AgentConversation.user_id == current_user.id)
        .order_by(AgentConversation.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "active_skills": s.active_skills or [],
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in sessions
    ]

@router.post("/agent/conversations", response_model=AgentConversationDetail)
async def create_agent_conversation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = AgentConversation(
        user_id=current_user.id,
        title="新对话",
        messages=[],
        active_skills=[],
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {
        "id": session.id,
        "title": session.title,
        "messages": session.messages,
        "active_skills": session.active_skills or [],
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }

@router.get("/agent/conversations/{conv_id}", response_model=AgentConversationDetail)
async def get_agent_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AgentConversation).where(
            AgentConversation.id == conv_id,
            AgentConversation.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {
        "id": session.id,
        "title": session.title,
        "messages": session.messages,
        "active_skills": session.active_skills or [],
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }

@router.post("/agent/conversations/{conv_id}/message", response_model=AgentConversationDetail)
async def add_agent_message(
    conv_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AgentConversation).where(
            AgentConversation.id == conv_id,
            AgentConversation.user_id == current_user.id,
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
        "active_skills": session.active_skills or [],
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }

@router.put("/agent/conversations/{conv_id}/skills")
async def update_agent_skills(
    conv_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AgentConversation).where(
            AgentConversation.id == conv_id,
            AgentConversation.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")

    session.active_skills = data.get("active_skills", [])
    await db.commit()
    await db.refresh(session)
    return {"message": "技能已更新", "active_skills": session.active_skills}

@router.delete("/agent/conversations/{conv_id}")
async def delete_agent_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AgentConversation).where(
            AgentConversation.id == conv_id,
            AgentConversation.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")

    await db.delete(session)
    await db.commit()
    return {"message": "对话已删除"}


# ========== Agent Stream Chat ==========

class AgentStreamRequest(BaseModel):
    message: str
    active_skills: list[str] = []
    conversation_id: str | None = None

async def agent_stream_generator(
    request: AgentStreamRequest,
    current_user: User,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
    """流式生成 AI 智能体回答，支持 skills"""

    # 获取激活的技能
    skill_prompts = []
    if request.active_skills:
        result = await db.execute(
            select(Skill).where(
                Skill.id.in_(request.active_skills),
                Skill.user_id == current_user.id,
                Skill.is_active == True,
            )
        )
        skills = result.scalars().all()
        skill_prompts = [s.system_prompt for s in skills]

    # 构建消息
    messages = []

    # 添加系统提示
    base_system = "你是一位智能 AI 助手，能够根据用户的需求提供专业、准确的回答。"
    if skill_prompts:
        combined_skills = "\n\n".join(
            [f"【技能 {i+1}】\n{prompt}" for i, prompt in enumerate(skill_prompts)]
        )
        base_system += f"\n\n当前激活的技能要求：\n\n{combined_skills}\n\n请综合以上技能要求，以专业的态度回答用户问题。"

    messages.append({"role": "system", "content": base_system})

    # 获取历史消息
    if request.conversation_id:
        result = await db.execute(
            select(AgentConversation).where(
                AgentConversation.id == request.conversation_id,
                AgentConversation.user_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()
        if session and session.messages:
            # 只取最近 10 条作为上下文
            for msg in session.messages[-10:]:
                if msg.get("role") in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"],
                    })

    # 添加当前消息
    messages.append({"role": "user", "content": request.message})

    api_key = get_llm_api_key(current_user.id)
    if not api_key:
        # 缓存可能为空，直接查数据库兜底
        result_db = await db.execute(select(User).where(User.id == current_user.id))
        user_db = result_db.scalar_one()
        user_settings = user_db.settings or {}
        api_key = user_settings.get("llm_api_key", "") or get_llm_api_key()

    if not api_key:
        yield f"data: {json.dumps({'error': '请在设置中配置 LLM API 密钥', 'done': True}, ensure_ascii=False)}\n\n"
        return

    # 从数据库获取模型配置（同样兜底）
    result_db2 = await db.execute(select(User).where(User.id == current_user.id))
    user_db2 = result_db2.scalar_one()
    user_settings2 = user_db2.settings or {}
    llm_model = user_settings2.get("llm_model", "") or get_llm_model(current_user.id)

    client = get_llm_client(current_user.id)

    try:
        stream = await client.chat.completions.create(
            model=get_llm_model(current_user.id),
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': f'LLM 调用失败: {str(e)}', 'done': True}, ensure_ascii=False)}\n\n"

@router.post("/agent/stream")
async def agent_stream(
    request: AgentStreamRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI 智能体流式对话接口，支持 skills"""
    return StreamingResponse(
        agent_stream_generator(request, current_user, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
