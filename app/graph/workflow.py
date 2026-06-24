from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    ask_user_node,
    economic_node,
    environmental_node,
    policy_router_node,
    recommend_node,
    request_evidence_node,
    summarize_node,
)
from app.graph.router import route_from_policy
from app.graph.state import DeliberationState

_checkpointer = MemorySaver()
_compiled_graph = None


def build_workflow():
    graph = StateGraph(DeliberationState)

    graph.add_node("policy_router", policy_router_node)
    graph.add_node("ask_user", ask_user_node)
    graph.add_node("economic", economic_node)
    graph.add_node("environmental", environmental_node)
    graph.add_node("request_evidence", request_evidence_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("recommend", recommend_node)

    graph.set_entry_point("policy_router")

    graph.add_conditional_edges(
        "policy_router",
        route_from_policy,
        {
            "ask_user": "ask_user",
            "economic": "economic",
            "environmental": "environmental",
            "request_evidence": "request_evidence",
            "summarize": "summarize",
            "recommend": "recommend",
        },
    )

    graph.add_edge("ask_user", END)
    graph.add_edge("economic", "policy_router")
    graph.add_edge("environmental", "policy_router")
    graph.add_edge("request_evidence", "policy_router")
    graph.add_edge("summarize", "policy_router")
    graph.add_edge("recommend", END)

    return graph.compile(checkpointer=_checkpointer)


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_workflow()
    return _compiled_graph
