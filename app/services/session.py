from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.db.supabase_client import get_supabase_client
from app.models.schemas import (
    AgentResponse,
    AgentRole,
    DeliberationStage,
    PolicyAction,
    Recommendation,
    SourceCitation,
    TranscriptMessage,
    TranscriptResponse,
)


def create_session_record(scenario_slug: str, scenario_title: str) -> dict[str, Any]:
    client = get_supabase_client()
    result = (
        client.table("sessions")
        .insert(
            {
                "scenario_slug": scenario_slug,
                "scenario_title": scenario_title,
                "stage": DeliberationStage.INTRO.value,
                "recommendation_status": "pending",
            }
        )
        .execute()
    )
    return result.data[0]


def get_session(session_id: str) -> dict[str, Any] | None:
    client = get_supabase_client()
    result = client.table("sessions").select("*").eq("id", session_id).execute()
    return result.data[0] if result.data else None


def update_session_stage(session_id: str, stage: DeliberationStage, recommendation_status: str | None = None) -> None:
    client = get_supabase_client()
    payload: dict[str, Any] = {
        "stage": stage.value,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if recommendation_status:
        payload["recommendation_status"] = recommendation_status
    client.table("sessions").update(payload).eq("id", session_id).execute()


def save_message(
    session_id: str,
    role: AgentRole,
    content: str,
    action: PolicyAction | None = None,
    evidence: list[SourceCitation] | None = None,
) -> dict[str, Any]:
    client = get_supabase_client()
    evidence_data = [e.model_dump() for e in (evidence or [])]
    result = (
        client.table("messages")
        .insert(
            {
                "session_id": session_id,
                "role": role.value,
                "content": content,
                "action": action.value if action else None,
                "evidence_used": evidence_data,
            }
        )
        .execute()
    )
    return result.data[0]


def save_session_evidence(session_id: str, sources: list[SourceCitation]) -> None:
    if not sources:
        return
    client = get_supabase_client()
    for source in sources:
        row = {
            "session_id": session_id,
            "document_id": source.document_id,
            "chunk_id": source.chunk_id,
            "title": source.title,
            "summary": source.summary,
            "excerpt": source.excerpt,
            "source_file": source.source_file,
            "category": source.category,
        }
        try:
            client.table("session_evidence").upsert(row, on_conflict="session_id,chunk_id").execute()
        except Exception:
            client.table("session_evidence").insert(row).execute()


def save_recommendation(session_id: str, recommendation: Recommendation) -> dict[str, Any]:
    client = get_supabase_client()
    result = (
        client.table("recommendations")
        .insert(
            {
                "session_id": session_id,
                "recommendation": recommendation.recommendation,
                "supporting_arguments": recommendation.supporting_arguments,
                "tradeoffs": recommendation.tradeoffs,
                "uncertainties": recommendation.uncertainties,
                "evidence_cited": [e.model_dump() for e in recommendation.evidence_cited],
            }
        )
        .execute()
    )
    update_session_stage(session_id, DeliberationStage.COMPLETE, "available")
    return result.data[0]


def get_recommendation(session_id: str) -> dict[str, Any] | None:
    client = get_supabase_client()
    result = client.table("recommendations").select("*").eq("session_id", session_id).execute()
    return result.data[0] if result.data else None


def get_messages(session_id: str) -> list[dict[str, Any]]:
    client = get_supabase_client()
    result = (
        client.table("messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


def get_session_evidence(session_id: str) -> list[dict[str, Any]]:
    client = get_supabase_client()
    result = client.table("session_evidence").select("*").eq("session_id", session_id).execute()
    return result.data or []


def get_turn_count(session_id: str) -> int:
    messages = get_messages(session_id)
    return sum(1 for m in messages if m["role"] == AgentRole.USER.value)


def build_transcript(session_id: str) -> TranscriptResponse:
    session = get_session(session_id)
    if not session:
        raise ValueError("Session not found")

    messages = get_messages(session_id)
    evidence_rows = get_session_evidence(session_id)

    transcript_messages = [
        TranscriptMessage(
            role=AgentRole(m["role"]),
            content=m["content"],
            action=PolicyAction(m["action"]) if m.get("action") else None,
            evidence=[SourceCitation(**e) for e in (m.get("evidence_used") or [])],
            created_at=m.get("created_at"),
        )
        for m in messages
    ]

    cited_sources = [
        SourceCitation(
            chunk_id=str(row.get("chunk_id")) if row.get("chunk_id") else None,
            document_id=str(row.get("document_id")) if row.get("document_id") else None,
            title=row["title"],
            summary=row.get("summary"),
            excerpt=row["excerpt"],
            source_file=row.get("source_file"),
            category=row.get("category"),
        )
        for row in evidence_rows
    ]

    return TranscriptResponse(
        session_id=UUID(session_id),
        scenario_slug=session["scenario_slug"],
        scenario_title=session["scenario_title"],
        messages=transcript_messages,
        cited_sources=cited_sources,
    )


def history_from_messages(messages: list[dict[str, Any]]) -> list[dict]:
    return [{"role": m["role"], "content": m["content"]} for m in messages]
