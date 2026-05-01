from typing import List, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import (
    get_llm_provider,
    get_llm_model,
    get_llm_api_key,
    get_llm_base_url,
    get_top_k,
)
from app.core.embeddings import get_embedding_with_user
from app.core.vector_store import similarity_search
from app.core.cache import get_cached_query, set_cached_query
from app.models.models import User, UsageRecord
from sqlalchemy.ext.asyncio import AsyncSession
import json

router = APIRouter(prefix="/query", tags=["问答"])

PROVIDER_BASE_URLS = {
    "deepseek": "https://api.deepseek.com/v1",
    "tongyi": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "kimi": "https://api.moonshot.cn/v1",
    "moonshot": "https://api.moonshot.cn/v1",
    "openai": "https://api.openai.com/v1",
}

class QueryRequest(BaseModel):
    message: str
    doc_id: str = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

def get_llm_client(user_id: str) -> AsyncOpenAI:
    base_url = get_llm_base_url(user_id) or PROVIDER_BASE_URLS.get(get_llm_provider(user_id).lower(), "https://api.deepseek.com/v1")
    return AsyncOpenAI(api_key=get_llm_api_key(user_id), base_url=base_url)

def build_prompt(question: str, contexts: List[dict]) -> str:
    context_text = "\n\n".join(
        [f"【文档片段 {i+1}】\n{ctx['content']}" for i, ctx in enumerate(contexts)]
    )
    return f"""你是一个专业的AI知识库助手。请根据以下文档内容回答用户的问题。

相关文档内容：
{context_text}

---

用户问题：{question}

请基于以上文档内容给出准确、简洁的回答。如果文档中没有相关信息，请明确告知用户。"""

@router.post("/", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cached = get_cached_query(request.message)
    if cached:
        import json
        return QueryResponse(**json.loads(cached))

    query_embedding = await get_embedding_with_user(request.message, current_user.id)
    if not query_embedding:
        raise HTTPException(status_code=500, detail="生成向量失败")

    top_k = get_top_k(current_user.id)
    contexts = await similarity_search(db, query_embedding, request.doc_id, top_k)
    if not contexts:
        return QueryResponse(
            answer="抱歉，我在知识库中没有找到相关信息。请上传更多文档后重试。",
            sources=[],
        )

    sources = [
        {"content": ctx["content"][:200] + "...", "similarity": ctx["similarity"]}
        for ctx in contexts
    ]

    api_key = get_llm_api_key(current_user.id)
    prompt_tokens = 0
    completion_tokens = 0
    model_used = ""

    if not api_key:
        context_text = "\n\n".join([f"【文档片段 {i+1}】\n{ctx['content'][:500]}" for i, ctx in enumerate(contexts[:3])])
        answer = f"根据知识库检索，找到以下相关内容：\n\n{context_text}\n\n注意：请在「系统设置」中配置 LLM API 密钥，我可以生成更准确的回答。"
    else:
        prompt = build_prompt(request.message, contexts)
        client = get_llm_client(current_user.id)

        try:
            response = await client.chat.completions.create(
                model=get_llm_model(current_user.id),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2048,
            )
            answer = response.choices[0].message.content.strip()
            usage = response.usage
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            model_used = get_llm_model(current_user.id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM 调用失败: {str(e)}")

    import json
    set_cached_query(request.message, json.dumps({"answer": answer, "sources": sources}))

    total_tokens = prompt_tokens + completion_tokens
    db.add(UsageRecord(
        user_id=current_user.id,
        query_text=request.message[:500],
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        model_used=model_used,
    ))
    await db.commit()

    return QueryResponse(answer=answer, sources=sources)

async def stream_generator(
    request: QueryRequest,
    current_user: User,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
    """流式生成 AI 回答"""
    cached = get_cached_query(request.message)
    if cached:
        data = json.loads(cached)
        yield f"data: {json.dumps({'answer': data['answer'], 'sources': data['sources'], 'done': True}, ensure_ascii=False)}\n\n"
        return

    query_embedding = await get_embedding_with_user(request.message, current_user.id)
    if not query_embedding:
        yield f"data: {json.dumps({'error': '生成向量失败', 'done': True}, ensure_ascii=False)}\n\n"
        return

    top_k = get_top_k(current_user.id)
    contexts = await similarity_search(db, query_embedding, request.doc_id, top_k)
    if not contexts:
        answer = "抱歉，我在知识库中没有找到相关信息。请上传更多文档后重试。"
        yield f"data: {json.dumps({'answer': answer, 'sources': [], 'done': True}, ensure_ascii=False)}\n\n"
        return

    sources = [
        {"content": ctx["content"][:200] + "...", "similarity": ctx["similarity"]}
        for ctx in contexts
    ]

    # 发送来源信息
    yield f"data: {json.dumps({'sources': sources}, ensure_ascii=False)}\n\n"

    api_key = get_llm_api_key(current_user.id)
    prompt_tokens = 0
    completion_tokens = 0
    model_used = ""
    full_answer = ""

    if not api_key:
        context_text = "\n\n".join([f"【文档片段 {i+1}】\n{ctx['content'][:500]}" for i, ctx in enumerate(contexts[:3])])
        full_answer = f"根据知识库检索，找到以下相关内容：\n\n{context_text}\n\n注意：请在「系统设置」中配置 LLM API 密钥，我可以生成更准确的回答。"
        yield f"data: {json.dumps({'answer': full_answer, 'done': True}, ensure_ascii=False)}\n\n"
        return

    prompt = build_prompt(request.message, contexts)
    client = get_llm_client(current_user.id)

    try:
        stream = await client.chat.completions.create(
            model=get_llm_model(current_user.id),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2048,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_answer += content
                yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

        # 发送完成信号
        usage = chunk.usage if hasattr(chunk, 'usage') and chunk.usage else None
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        model_used = get_llm_model(current_user.id)

        yield f"data: {json.dumps({'done': True, 'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'model': model_used}, ensure_ascii=False)}\n\n"

        # 保存缓存和使用记录
        set_cached_query(request.message, json.dumps({"answer": full_answer, "sources": sources}))
        total_tokens = prompt_tokens + completion_tokens
        db.add(UsageRecord(
            user_id=current_user.id,
            query_text=request.message[:500],
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model_used=model_used,
        ))
        await db.commit()

    except Exception as e:
        yield f"data: {json.dumps({'error': f'LLM 调用失败: {str(e)}', 'done': True}, ensure_ascii=False)}\n\n"

@router.post("/stream")
async def query_stream(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """流式问答接口"""
    return StreamingResponse(
        stream_generator(request, current_user, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
