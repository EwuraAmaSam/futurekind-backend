from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.models.schemas import AgentResponse, EvidenceChunk
from app.retrieval.retriever import evidence_to_citations, format_evidence_for_prompt, retrieve_evidence


def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key, temperature=temperature)


def build_context_query(user_input: str | None, recent_messages: list[dict], scenario_title: str) -> str:
    parts = [f"Scenario: {scenario_title}"]
    for msg in recent_messages[-6:]:
        parts.append(f"{msg['role']}: {msg['content'][:300]}")
    if user_input:
        parts.append(f"user: {user_input}")
    return "\n".join(parts)


def retrieve_for_context(
    user_input: str | None,
    recent_messages: list[dict],
    scenario_title: str,
    category: str | None = None,
) -> list[EvidenceChunk]:
    query = build_context_query(user_input, recent_messages, scenario_title)
    return retrieve_evidence(query, category=category)


def messages_from_history(recent_messages: list[dict]) -> list[BaseMessage]:
    result: list[BaseMessage] = []
    for msg in recent_messages:
        if msg["role"] == "user":
            result.append(HumanMessage(content=msg["content"]))
        else:
            result.append(AIMessage(content=f"[{msg['role']}] {msg['content']}"))
    return result


def invoke_with_evidence(
    system_prompt: str,
    user_prompt: str,
    evidence: list[EvidenceChunk],
    recent_messages: list[dict],
    temperature: float = 0.3,
) -> AgentResponse:
    llm = get_llm(temperature=temperature)
    structured = llm.with_structured_output(AgentResponse)

    evidence_text = format_evidence_for_prompt(evidence)
    messages: list[BaseMessage] = [
        SystemMessage(content=system_prompt),
        *messages_from_history(recent_messages),
        HumanMessage(
            content=(
                f"{user_prompt}\n\n"
                f"--- EVIDENCE FROM KNOWLEDGE BASE ---\n{evidence_text}\n\n"
                "You MUST ground your response in the provided evidence. "
                "Cite specific sources in your response and populate the sources field."
            )
        ),
    ]

    response: AgentResponse = structured.invoke(messages)

    if not response.sources and evidence:
        response.sources = evidence_to_citations(evidence)
    if not response.evidence_used and evidence:
        response.evidence_used = [c.chunk_id for c in evidence]

    return response
