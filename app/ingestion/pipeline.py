import logging
from typing import Any

from langchain_openai import OpenAIEmbeddings

from app.config import get_settings
from app.db.supabase_client import get_supabase_client
from app.ingestion.chunker import chunk_document
from app.ingestion.loader import LoadedDocument, load_documents
from app.ingestion.summarizer import summarize_document

logger = logging.getLogger(__name__)


def _document_exists(source_file: str) -> bool:
    client = get_supabase_client()
    result = client.table("documents").select("id").eq("source_file", source_file).execute()
    return bool(result.data)


def _delete_document(source_file: str) -> None:
    client = get_supabase_client()
    client.table("documents").delete().eq("source_file", source_file).execute()


def ingest_document(doc: LoadedDocument, force: bool = False) -> dict[str, Any]:
    if _document_exists(doc.source_file):
        if not force:
            logger.info("Skipping already ingested: %s", doc.relative_path)
            return {"skipped": True, "source_file": doc.source_file}
        _delete_document(doc.source_file)

    logger.info("Summarizing: %s", doc.relative_path)
    summary_result = summarize_document(doc)

    logger.info("Chunking: %s", doc.relative_path)
    chunks = chunk_document(doc)
    if not chunks:
        logger.warning("No chunks produced for %s", doc.relative_path)
        return {"skipped": True, "source_file": doc.source_file, "reason": "no_chunks"}

    settings = get_settings()
    embeddings = OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)

    logger.info("Embedding %d chunks for %s", len(chunks), doc.relative_path)
    vectors = embeddings.embed_documents([c["content"] for c in chunks])

    client = get_supabase_client()
    doc_row = (
        client.table("documents")
        .insert(
            {
                "title": summary_result.title,
                "category": doc.category,
                "source_file": doc.source_file,
                "topic": summary_result.topic,
                "summary": summary_result.summary,
                "key_findings": summary_result.key_findings,
            }
        )
        .execute()
    )
    document_id = doc_row.data[0]["id"]

    chunk_rows = [
        {
            "document_id": document_id,
            "content": chunk["content"],
            "chunk_index": chunk["chunk_index"],
            "embedding": vector,
            "metadata": chunk["metadata"],
        }
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]

    client.table("document_chunks").insert(chunk_rows).execute()

    return {
        "skipped": False,
        "source_file": doc.source_file,
        "document_id": document_id,
        "chunks": len(chunk_rows),
    }


def run_ingestion(docs_path: str | None = None, force: bool = False) -> dict[str, Any]:
    settings = get_settings()
    from pathlib import Path

    root = Path(docs_path) if docs_path else settings.docs_path
    if not root.is_absolute():
        root = Path.cwd() / root
    documents = load_documents(root)

    results = {"processed": 0, "skipped": 0, "errors": 0, "details": []}
    for doc in documents:
        try:
            outcome = ingest_document(doc, force=force)
            if outcome.get("skipped"):
                results["skipped"] += 1
            else:
                results["processed"] += 1
            results["details"].append(outcome)
        except Exception as exc:
            logger.exception("Ingestion failed for %s", doc.relative_path)
            results["errors"] += 1
            results["details"].append({"source_file": doc.source_file, "error": str(exc)})

    return results
