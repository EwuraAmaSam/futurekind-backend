from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.ingestion.loader import LoadedDocument


def chunk_document(doc: LoadedDocument, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(doc.text)
    return [
        {
            "content": chunk,
            "chunk_index": idx,
            "metadata": {
                "title": doc.title,
                "category": doc.category,
                "source_file": doc.relative_path,
            },
        }
        for idx, chunk in enumerate(chunks)
        if chunk.strip()
    ]
