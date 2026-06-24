from app.agents.base import invoke_with_evidence, retrieve_for_context
from app.models.schemas import AgentResponse

ENVIRONMENTAL_SYSTEM = """You are the Environmental Agent in a PLF policy deliberation.

You represent:
- Environmental sustainability of livestock systems
- Resource efficiency (water, feed, energy)
- Emissions and climate impacts
- Ecological tradeoffs of PLF technologies
- Long-term environmental consequences

Provide environmental perspectives and identify sustainability considerations.
Ground ALL arguments in the provided evidence. Do not speculate beyond the evidence.
Be concise — you are a consultant called by the Policy Agent, not the main speaker."""


def generate_environmental_response(
    scenario_title: str,
    recent_messages: list[dict],
    user_input: str | None,
) -> AgentResponse:
    evidence = retrieve_for_context(
        user_input,
        recent_messages,
        scenario_title,
        category="Environmental & Sustainability",
    )
    if len(evidence) < 2:
        general = retrieve_for_context(user_input, recent_messages, scenario_title)
        seen = {e.chunk_id for e in evidence}
        evidence.extend(e for e in general if e.chunk_id not in seen)

    user_prompt = (
        f"The Policy Agent has asked for your environmental perspective on: {scenario_title}\n"
        "Provide key sustainability considerations, tradeoffs, and cite supporting evidence."
    )

    return invoke_with_evidence(
        ENVIRONMENTAL_SYSTEM, user_prompt, evidence, recent_messages, temperature=0.3
    )
