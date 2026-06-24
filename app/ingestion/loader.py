import logging
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)


@dataclass
class LoadedDocument:
    title: str
    category: str
    source_file: str
    text: str
    relative_path: str


def _title_from_filename(path: Path) -> str:
    name = path.stem.replace("_", " ").replace("-", " ")
    return " ".join(name.split())


def load_documents(docs_root: Path) -> list[LoadedDocument]:
    if not docs_root.exists():
        raise FileNotFoundError(f"Documents path not found: {docs_root}")

    documents: list[LoadedDocument] = []
    pdf_files = sorted(docs_root.rglob("*.pdf"))

    if not pdf_files:
        logger.warning("No PDF files found under %s", docs_root)

    for pdf_path in pdf_files:
        category = pdf_path.parent.name if pdf_path.parent != docs_root else "Uncategorized"
        relative_path = str(pdf_path.relative_to(docs_root))

        try:
            reader = PdfReader(str(pdf_path))
            pages_text = []
            for page in reader.pages:
                text = page.extract_text() or ""
                pages_text.append(text)
            full_text = "\n\n".join(pages_text).strip()

            if len(full_text.split()) < 50:
                logger.warning("Low text extracted from %s (%d words)", pdf_path, len(full_text.split()))

            documents.append(
                LoadedDocument(
                    title=_title_from_filename(pdf_path),
                    category=category,
                    source_file=str(pdf_path),
                    text=full_text,
                    relative_path=relative_path,
                )
            )
        except Exception:
            logger.exception("Failed to load PDF: %s", pdf_path)

    return documents
