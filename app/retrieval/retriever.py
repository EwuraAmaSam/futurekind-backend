from langchain_openai import OpenAIEmbeddings

from app.config import get_settings
from app.db.supabase_client import get_supabase_client
from app.models.schemas import EvidenceChunk, SourceCitation


def _embed_query(query: str) -> list[float]:
    settings = get_settings()
    embeddings = OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
    return embeddings.embed_query(query)


def retrieve_evidence(
    query: str,
    top_k: int | None = None,
    category: str | None = None,
) -> list[EvidenceChunk]:
    settings = get_settings()
    k = top_k or settings.retrieval_top_k
    vector = _embed_query(query)

    client = get_supabase_client()
    params: dict = {
        "query_embedding": vector,
        "match_count": k,
    }
    if category:
        params["filter_category"] = category

    result = client.rpc("match_document_chunks", params).execute()
    rows = result.data or []

    if not rows and category:
        result = client.rpc(
            "match_document_chunks",
            {"query_embedding": vector, "match_count": k},
        ).execute()
        rows = result.data or []

    return [
        EvidenceChunk(
            chunk_id=str(row["chunk_id"]),
            document_id=str(row["document_id"]),
            excerpt=row["content"],
            title=row["title"],
            summary=row.get("summary"),
            source_file=row.get("source_file"),
            category=row.get("category"),
            similarity=row.get("similarity"),
        )
        for row in rows
    ]


def evidence_to_citations(chunks: list[EvidenceChunk]) -> list[SourceCitation]:
    return [
        SourceCitation(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            title=chunk.title,
            summary=chunk.summary,
            excerpt=chunk.excerpt[:500] if len(chunk.excerpt) > 500 else chunk.excerpt,
            source_file=chunk.source_file,
            category=chunk.category,
        )
        for chunk in chunks
    ]


def format_evidence_for_prompt(chunks: list[EvidenceChunk]) -> str:
    if not chunks:
        return "No evidence retrieved from the knowledge base."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}] Title: {chunk.title}\n"
            f"Category: {chunk.category}\n"
            f"Summary: {chunk.summary or 'N/A'}\n"
            f"Excerpt: {chunk.excerpt[:800]}\n"
            f"Chunk ID: {chunk.chunk_id}"
        )
    return "\n\n".join(parts)
