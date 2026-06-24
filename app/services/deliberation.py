from typing import Any

from app.graph.workflow import get_graph
from app.models.schemas import (
    AgentResponse,
    AgentRole,
    CreateSessionResponse,
    DeliberationStage,
    PolicyAction,
    Recommendation,
    SessionState,
    SourceCitation,
    TurnResponse,
)
from app.scenarios.topics import get_scenario_by_slug
from app.services import session as session_service


def _build_session_state(session_id: str, stage: str) -> SessionState:
    return SessionState(
        stage=DeliberationStage(stage),
        turn_count=session_service.get_turn_count(session_id),
        recommendation_available=stage == DeliberationStage.COMPLETE.value,
    )


def _persist_agent_turn(
    session_id: str,
    agent: AgentRole,
    response: AgentResponse,
    action: PolicyAction | None,
    stage: DeliberationStage,
) -> None:
    session_service.save_message(
        session_id=session_id,
        role=agent,
        content=response.response,
        action=action,
        evidence=response.sources,
    )
    session_service.save_session_evidence(session_id, response.sources)
    session_service.update_session_stage(session_id, stage)


def _initial_state(session_id: str, scenario) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "scenario_slug": scenario.slug,
        "scenario_title": scenario.title,
        "scenario_description": scenario.description,
        "messages": [],
        "history": [],
        "cited_evidence": [],
        "stage": DeliberationStage.INTRO.value,
        "last_action": None,
        "user_input": None,
        "next_action": PolicyAction.ASK_USER_QUESTION.value,
        "current_agent": AgentRole.POLICY.value,
        "agent_response": None,
        "recommendation": None,
        "turn_count": 0,
        "awaiting_user": False,
        "consecutive_stakeholder_calls": 0,
    }


def _run_until_user_pause(session_id: str, state: dict[str, Any]) -> dict[str, Any]:
    graph = get_graph()
    config = {"configurable": {"thread_id": session_id}}
    current = state

    while True:
        result = graph.invoke(current, config=config)
        current = result

        if result.get("recommendation"):
            rec: Recommendation = result["recommendation"]
            session_service.save_recommendation(session_id, rec)
            session_service.save_message(
                session_id=session_id,
                role=AgentRole.POLICY,
                content=rec.recommendation,
                action=PolicyAction.ISSUE_RECOMMENDATION,
                evidence=rec.evidence_cited,
            )
            session_service.save_session_evidence(session_id, rec.evidence_cited)
            break

        agent_response: AgentResponse | None = result.get("agent_response")
        if not agent_response:
            break

        agent = AgentRole(result.get("current_agent", AgentRole.POLICY.value))
        action = PolicyAction(result["last_action"]) if result.get("last_action") else None
        stage = DeliberationStage(result["stage"])

        history = result.get("history", [])
        history.append({"role": agent.value, "content": agent_response.response})
        result["history"] = history

        _persist_agent_turn(session_id, agent, agent_response, action, stage)

        if result.get("awaiting_user") or result.get("last_action") == PolicyAction.ASK_USER_QUESTION.value:
            if result.get("last_action") == PolicyAction.ASK_USER_QUESTION.value:
                break
        if result.get("stage") == DeliberationStage.COMPLETE.value:
            break

        if result.get("last_action") in (
            PolicyAction.CALL_ECONOMIC_AGENT.value,
            PolicyAction.CALL_ENVIRONMENTAL_AGENT.value,
            PolicyAction.REQUEST_EVIDENCE.value,
            PolicyAction.SUMMARIZE_DISCUSSION.value,
        ):
            result["next_action"] = PolicyAction.ASK_USER_QUESTION.value
            current = result
            continue

        break

    return current


def create_session(scenario_slug: str) -> CreateSessionResponse:
    scenario = get_scenario_by_slug(scenario_slug)
    if not scenario:
        raise ValueError(f"Unknown scenario: {scenario_slug}")

    record = session_service.create_session_record(scenario.slug, scenario.title)
    session_id = record["id"]

    state = _initial_state(session_id, scenario)
    final = _run_until_user_pause(session_id, state)

    agent_response: AgentResponse = final["agent_response"]
    action = PolicyAction(final["last_action"]) if final.get("last_action") else None

    return CreateSessionResponse(
        session_id=session_id,
        agent=AgentRole(final.get("current_agent", AgentRole.POLICY.value)),
        action=action,
        response=agent_response.response,
        evidence=agent_response.sources,
        state=_build_session_state(session_id, final["stage"]),
    )


def process_turn(session_id: str, message: str) -> TurnResponse:
    session = session_service.get_session(session_id)
    if not session:
        raise ValueError("Session not found")
    if session["stage"] == DeliberationStage.COMPLETE.value:
        raise ValueError("Session is complete")

    session_service.save_message(
        session_id=session_id,
        role=AgentRole.USER,
        content=message,
    )

    messages = session_service.get_messages(session_id)
    history = session_service.history_from_messages(messages)

    scenario = get_scenario_by_slug(session["scenario_slug"])
    if not scenario:
        raise ValueError("Scenario not found")

    state = {
        "session_id": session_id,
        "scenario_slug": scenario.slug,
        "scenario_title": scenario.title,
        "scenario_description": scenario.description,
        "messages": [],
        "history": history,
        "cited_evidence": [],
        "stage": session["stage"],
        "last_action": None,
        "user_input": message,
        "next_action": None,
        "current_agent": AgentRole.POLICY.value,
        "agent_response": None,
        "recommendation": None,
        "turn_count": session_service.get_turn_count(session_id),
        "awaiting_user": False,
        "consecutive_stakeholder_calls": 0,
    }

    final = _run_until_user_pause(session_id, state)

    if final.get("recommendation"):
        rec: Recommendation = final["recommendation"]
        return TurnResponse(
            session_id=session_id,
            agent=AgentRole.POLICY,
            action=PolicyAction.ISSUE_RECOMMENDATION,
            response=rec.recommendation,
            evidence=rec.evidence_cited,
            state=_build_session_state(session_id, DeliberationStage.COMPLETE.value),
        )

    agent_response: AgentResponse = final["agent_response"]
    action = PolicyAction(final["last_action"]) if final.get("last_action") else None

    return TurnResponse(
        session_id=session_id,
        agent=AgentRole(final.get("current_agent", AgentRole.POLICY.value)),
        action=action,
        response=agent_response.response,
        evidence=agent_response.sources,
        state=_build_session_state(session_id, final["stage"]),
    )
