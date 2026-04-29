import uuid
import math
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_top_k
from app.models.models import Chunk

def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

async def insert_embeddings(
    db: AsyncSession,
    chunks: List[Dict[str, Any]],
) -> None:
    for chunk in chunks:
        new_chunk = Chunk(
            id=str(uuid.uuid4()),
            doc_id=chunk["doc_id"],
            content=chunk["content"],
            embedding=chunk["embedding"],
            chunk_index=chunk["chunk_index"],
        )
        db.add(new_chunk)
    await db.commit()

async def similarity_search(
    db: AsyncSession,
    query_embedding: List[float],
    doc_id: Optional[str] = None,
    top_k: int = None,
) -> List[Dict[str, Any]]:
    if top_k is None:
        top_k = get_top_k()

    stmt = select(Chunk)
    if doc_id:
        stmt = stmt.where(Chunk.doc_id == doc_id)

    result = await db.execute(stmt)
    all_chunks = result.scalars().all()

    scored = []
    for chunk in all_chunks:
        sim = cosine_similarity(query_embedding, chunk.embedding)
        scored.append({
            "id": chunk.id,
            "doc_id": chunk.doc_id,
            "content": chunk.content,
            "chunk_index": chunk.chunk_index,
            "similarity": sim,
        })

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]

async def delete_document_chunks(db: AsyncSession, doc_id: str) -> None:
    result = await db.execute(select(Chunk).where(Chunk.doc_id == doc_id))
    chunks = result.scalars().all()
    for chunk in chunks:
        await db.delete(chunk)
    await db.commit()
