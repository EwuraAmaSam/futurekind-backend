from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    Recommendation,
    RecommendationResponse,
    SourceCitation,
    TranscriptResponse,
    TurnRequest,
    TurnResponse,
)
from app.services import deliberation as deliberation_service
from app.services import session as session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=CreateSessionResponse)
def create_session(body: CreateSessionRequest):
    try:
        return deliberation_service.create_session(body.scenario_slug)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{session_id}/turn", response_model=TurnResponse)
def submit_turn(session_id: UUID, body: TurnRequest):
    try:
        return deliberation_service.process_turn(str(session_id), body.message)
    except ValueError as exc:
        msg = str(exc)
        if "complete" in msg.lower():
            raise HTTPException(status_code=409, detail=msg) from exc
        raise HTTPException(status_code=404, detail=msg) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{session_id}/recommendation", response_model=RecommendationResponse)
def get_recommendation(session_id: UUID):
    session = session_service.get_session(str(session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["stage"] != "complete":
        raise HTTPException(status_code=404, detail="Recommendation not yet available")

    rec = session_service.get_recommendation(str(session_id))
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    evidence = [SourceCitation(**e) for e in (rec.get("evidence_cited") or [])]
    return RecommendationResponse(
        session_id=session_id,
        recommendation=Recommendation(
            recommendation=rec["recommendation"],
            supporting_arguments=rec.get("supporting_arguments") or [],
            tradeoffs=rec.get("tradeoffs") or [],
            uncertainties=rec.get("uncertainties") or [],
            evidence_cited=evidence,
        ),
    )


@router.get("/{session_id}/transcript", response_model=TranscriptResponse)
def get_transcript(session_id: UUID):
    try:
        return session_service.build_transcript(str(session_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
