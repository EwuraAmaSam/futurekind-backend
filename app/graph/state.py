from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

from app.models.schemas import (
    AgentResponse,
    AgentRole,
    DeliberationStage,
    PolicyAction,
    Recommendation,
    SourceCitation,
)


class DeliberationState(TypedDict):
    session_id: str
    scenario_slug: str
    scenario_title: str
    scenario_description: str
    messages: Annotated[list, add_messages]
    history: list[dict]
    cited_evidence: list[SourceCitation]
    stage: str
    last_action: str | None
    user_input: str | None
    next_action: str | None
    current_agent: str
    agent_response: AgentResponse | None
    recommendation: Recommendation | None
    turn_count: int
    awaiting_user: bool
    consecutive_stakeholder_calls: int
