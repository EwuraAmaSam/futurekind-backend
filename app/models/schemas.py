from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PolicyAction(StrEnum):
    ASK_USER_QUESTION = "ASK_USER_QUESTION"
    CALL_ECONOMIC_AGENT = "CALL_ECONOMIC_AGENT"
    CALL_ENVIRONMENTAL_AGENT = "CALL_ENVIRONMENTAL_AGENT"
    REQUEST_EVIDENCE = "REQUEST_EVIDENCE"
    SUMMARIZE_DISCUSSION = "SUMMARIZE_DISCUSSION"
    ISSUE_RECOMMENDATION = "ISSUE_RECOMMENDATION"


class DeliberationStage(StrEnum):
    INTRO = "intro"
    DELIBERATION = "deliberation"
    SUMMARIZING = "summarizing"
    COMPLETE = "complete"


class AgentRole(StrEnum):
    USER = "user"
    POLICY = "policy"
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"


class TopicResponse(BaseModel):
    slug: str
    title: str
    description: str


class SourceCitation(BaseModel):
    chunk_id: str | None = None
    document_id: str | None = None
    title: str
    summary: str | None = None
    excerpt: str
    source_file: str | None = None
    category: str | None = None


class AgentResponse(BaseModel):
    response: str
    evidence_used: list[str] = Field(default_factory=list)
    sources: list[SourceCitation] = Field(default_factory=list)
    reasoning_summary: str = ""


class Recommendation(BaseModel):
    recommendation: str
    supporting_arguments: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    evidence_cited: list[SourceCitation] = Field(default_factory=list)


class SessionState(BaseModel):
    stage: DeliberationStage
    turn_count: int
    recommendation_available: bool


class CreateSessionRequest(BaseModel):
    scenario_slug: str


class TurnRequest(BaseModel):
    message: str = Field(min_length=1)


class TurnResponse(BaseModel):
    session_id: UUID
    agent: AgentRole
    action: PolicyAction | None = None
    response: str
    evidence: list[SourceCitation] = Field(default_factory=list)
    state: SessionState


class CreateSessionResponse(BaseModel):
    session_id: UUID
    agent: AgentRole
    action: PolicyAction | None = None
    response: str
    evidence: list[SourceCitation] = Field(default_factory=list)
    state: SessionState


class TranscriptMessage(BaseModel):
    role: AgentRole
    content: str
    action: PolicyAction | None = None
    evidence: list[SourceCitation] = Field(default_factory=list)
    created_at: str | None = None


class TranscriptResponse(BaseModel):
    session_id: UUID
    scenario_slug: str
    scenario_title: str
    messages: list[TranscriptMessage]
    cited_sources: list[SourceCitation]


class RecommendationResponse(BaseModel):
    session_id: UUID
    recommendation: Recommendation


class EvidenceChunk(BaseModel):
    chunk_id: str
    document_id: str
    excerpt: str
    title: str
    summary: str | None = None
    source_file: str | None = None
    category: str | None = None
    similarity: float | None = None


class PolicyRouterDecision(BaseModel):
    action: PolicyAction
    reasoning: str
    evidence_query: str | None = None
    evidence_category: str | None = None


class DocumentSummaryResult(BaseModel):
    title: str
    summary: str
    key_findings: list[str]
    topic: str
