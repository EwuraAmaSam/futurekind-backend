from app.graph.state import DeliberationState
from app.models.schemas import PolicyAction


def route_from_policy(state: DeliberationState) -> str:
    action = state.get("next_action") or state.get("last_action")
    mapping = {
        PolicyAction.ASK_USER_QUESTION.value: "ask_user",
        PolicyAction.CALL_ECONOMIC_AGENT.value: "economic",
        PolicyAction.CALL_ENVIRONMENTAL_AGENT.value: "environmental",
        PolicyAction.REQUEST_EVIDENCE.value: "request_evidence",
        PolicyAction.SUMMARIZE_DISCUSSION.value: "summarize",
        PolicyAction.ISSUE_RECOMMENDATION.value: "recommend",
    }
    return mapping.get(action, "ask_user")
