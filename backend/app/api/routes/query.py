from typing import List
from fastapi import APIRouter, Depends, HTTPException
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
from app.core.embeddings import get_embedding
from app.core.vector_store import similarity_search
from app.core.cache import get_cached_query, set_cached_query
from app.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession

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

def get_llm_client() -> AsyncOpenAI:
    base_url = get_llm_base_url() or PROVIDER_BASE_URLS.get(get_llm_provider().lower(), "https://api.deepseek.com/v1")
    return AsyncOpenAI(api_key=get_llm_api_key(), base_url=base_url)

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

    query_embedding = await get_embedding(request.message)
    if not query_embedding:
        raise HTTPException(status_code=500, detail="生成向量失败")

    top_k = get_top_k()
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

    api_key = get_llm_api_key()
    if not api_key:
        context_text = "\n\n".join([f"【文档片段 {i+1}】\n{ctx['content'][:500]}" for i, ctx in enumerate(contexts[:3])])
        answer = f"根据知识库检索，找到以下相关内容：\n\n{context_text}\n\n注意：请在「系统设置」中配置 LLM API 密钥，我可以生成更准确的回答。"
    else:
        prompt = build_prompt(request.message, contexts)
        client = get_llm_client()

        try:
            response = await client.chat.completions.create(
                model=get_llm_model(),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2048,
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM 调用失败: {str(e)}")

    import json
    set_cached_query(request.message, json.dumps({"answer": answer, "sources": sources}))

    return QueryResponse(answer=answer, sources=sources)
