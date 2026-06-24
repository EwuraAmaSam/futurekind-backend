from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.config import get_settings
from app.ingestion.loader import LoadedDocument
from app.models.schemas import DocumentSummaryResult


SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You summarize research documents for a precision livestock farming policy deliberation "
            "knowledge base. Be factual and concise.",
        ),
        (
            "human",
            "Summarize this research document.\n\n"
            "Filename: {title}\n"
            "Category: {category}\n\n"
            "Content (excerpt):\n{content}",
        ),
    ]
)


def summarize_document(doc: LoadedDocument, max_chars: int = 12000) -> DocumentSummaryResult:
    settings = get_settings()
    llm = ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key, temperature=0)
    structured = llm.with_structured_output(DocumentSummaryResult)

    excerpt = doc.text[:max_chars]
    chain = SUMMARY_PROMPT | structured
    result: DocumentSummaryResult = chain.invoke(
        {
            "title": doc.title,
            "category": doc.category,
            "content": excerpt,
        }
    )
    if not result.title:
        result.title = doc.title
    return result
