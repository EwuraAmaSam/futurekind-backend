from app.agents.economic import generate_economic_response
from app.agents.environmental import generate_environmental_response
from app.agents.policy import generate_policy_response, generate_recommendation, route_next_action
from app.graph.state import DeliberationState
from app.models.schemas import AgentRole, DeliberationStage, PolicyAction


def _count_user_turns(history: list[dict]) -> int:
    return sum(1 for m in history if m.get("role") == AgentRole.USER.value)


def policy_router_node(state: DeliberationState) -> DeliberationState:
    stage = DeliberationStage(state["stage"])
    turn_count = _count_user_turns(state["history"])

    if state.get("next_action"):
        action = PolicyAction(state["next_action"])
        state["next_action"] = None
    else:
        decision = route_next_action(
            stage=stage,
            turn_count=turn_count,
            last_action=state.get("last_action"),
            recent_messages=state["history"],
            scenario_title=state["scenario_title"],
            user_input=state.get("user_input"),
        )
        action = decision.action

        if (
            action in (PolicyAction.CALL_ECONOMIC_AGENT, PolicyAction.CALL_ENVIRONMENTAL_AGENT)
            and state.get("consecutive_stakeholder_calls", 0) >= 1
        ):
            action = PolicyAction.ASK_USER_QUESTION

    state["last_action"] = action.value
    state["next_action"] = action.value
    return state


def ask_user_node(state: DeliberationState) -> DeliberationState:
    response = generate_policy_response(
        action=PolicyAction.ASK_USER_QUESTION,
        scenario_title=state["scenario_title"],
        scenario_description=state["scenario_description"],
        recent_messages=state["history"],
        user_input=state.get("user_input"),
    )
    state["agent_response"] = response
    state["current_agent"] = AgentRole.POLICY.value
    state["stage"] = DeliberationStage.DELIBERATION.value if state["history"] else DeliberationStage.INTRO.value
    state["awaiting_user"] = True
    state["consecutive_stakeholder_calls"] = 0
    return state


def economic_node(state: DeliberationState) -> DeliberationState:
    response = generate_economic_response(
        scenario_title=state["scenario_title"],
        recent_messages=state["history"],
        user_input=state.get("user_input"),
    )
    state["agent_response"] = response
    state["current_agent"] = AgentRole.ECONOMIC.value
    state["stage"] = DeliberationStage.DELIBERATION.value
    state["consecutive_stakeholder_calls"] = state.get("consecutive_stakeholder_calls", 0) + 1
    state["next_action"] = None
    return state


def environmental_node(state: DeliberationState) -> DeliberationState:
    response = generate_environmental_response(
        scenario_title=state["scenario_title"],
        recent_messages=state["history"],
        user_input=state.get("user_input"),
    )
    state["agent_response"] = response
    state["current_agent"] = AgentRole.ENVIRONMENTAL.value
    state["stage"] = DeliberationStage.DELIBERATION.value
    state["consecutive_stakeholder_calls"] = state.get("consecutive_stakeholder_calls", 0) + 1
    state["next_action"] = None
    return state


def request_evidence_node(state: DeliberationState) -> DeliberationState:
    response = generate_policy_response(
        action=PolicyAction.REQUEST_EVIDENCE,
        scenario_title=state["scenario_title"],
        scenario_description=state["scenario_description"],
        recent_messages=state["history"],
        user_input=state.get("user_input"),
    )
    state["agent_response"] = response
    state["current_agent"] = AgentRole.POLICY.value
    state["stage"] = DeliberationStage.DELIBERATION.value
    state["consecutive_stakeholder_calls"] = 0
    state["next_action"] = None
    return state


def summarize_node(state: DeliberationState) -> DeliberationState:
    response = generate_policy_response(
        action=PolicyAction.SUMMARIZE_DISCUSSION,
        scenario_title=state["scenario_title"],
        scenario_description=state["scenario_description"],
        recent_messages=state["history"],
        user_input=state.get("user_input"),
    )
    state["agent_response"] = response
    state["current_agent"] = AgentRole.POLICY.value
    state["stage"] = DeliberationStage.SUMMARIZING.value
    state["consecutive_stakeholder_calls"] = 0
    state["next_action"] = None
    return state


def recommend_node(state: DeliberationState) -> DeliberationState:
    recommendation = generate_recommendation(
        scenario_title=state["scenario_title"],
        recent_messages=state["history"],
    )
    state["recommendation"] = recommendation
    state["agent_response"] = None
    state["current_agent"] = AgentRole.POLICY.value
    state["stage"] = DeliberationStage.COMPLETE.value
    state["last_action"] = PolicyAction.ISSUE_RECOMMENDATION.value
    state["awaiting_user"] = False
    return state
