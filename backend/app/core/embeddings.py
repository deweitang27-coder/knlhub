from typing import List
import httpx
from app.core.config import (
    get_embedding_provider,
    get_embedding_model,
    get_embedding_api_key,
    get_embedding_base_url,
)

PROVIDER_CONFIG = {
    "tongyi": {
        "model": "text-embedding-v3",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings",
        "headers_key": "Authorization",
        "headers_value_prefix": "Bearer ",
        "input_key": "input",
    },
    "zhipu": {
        "model": "embedding-3",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/embeddings",
        "headers_key": "Authorization",
        "headers_value_prefix": "Bearer ",
        "input_key": "input",
    },
}

DEFAULT_DIM = 1536

async def get_embedding(text: str, user_id: str = None) -> List[float]:
    api_key = get_embedding_api_key(user_id)
    if not api_key:
        return [0.0] * DEFAULT_DIM

    provider = get_embedding_provider(user_id).lower()
    config = PROVIDER_CONFIG.get(provider, PROVIDER_CONFIG["tongyi"])

    payload = {
        "model": get_embedding_model(user_id) if provider != "zhipu" else config["model"],
        config["input_key"]: text,
    }

    headers = {
        "Content-Type": "application/json",
        config["headers_key"]: f"{config['headers_value_prefix']}{api_key}",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(config["base_url"], json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    embeddings = data.get("data", [])
    if embeddings and len(embeddings) > 0:
        return embeddings[0].get("embedding", [])
    return []

async def get_embedding_with_user(text: str, user_id: str) -> List[float]:
    return await get_embedding(text, user_id)

async def get_embeddings(texts: List[str], user_id: str = None) -> List[List[float]]:
    return [await get_embedding(text, user_id) for text in texts]
