from app.agents.base import invoke_with_evidence, retrieve_for_context
from app.models.schemas import AgentResponse

ECONOMIC_SYSTEM = """You are the Economic Agent in a PLF policy deliberation.

You represent:
- Farmer livelihoods and economic viability
- Implementation and adoption costs
- Affordability for small and medium farms
- Market impacts and competitiveness
- Adoption barriers and incentives

Provide economic perspectives and tradeoffs. Ground ALL arguments in the provided
evidence from the knowledge base. Do not speculate beyond the evidence.
Be concise — you are a consultant called by the Policy Agent, not the main speaker."""


def generate_economic_response(
    scenario_title: str,
    recent_messages: list[dict],
    user_input: str | None,
) -> AgentResponse:
    evidence = retrieve_for_context(
        user_input,
        recent_messages,
        scenario_title,
        category="Economics & Adoption",
    )
    if len(evidence) < 2:
        general = retrieve_for_context(user_input, recent_messages, scenario_title)
        seen = {e.chunk_id for e in evidence}
        evidence.extend(e for e in general if e.chunk_id not in seen)

    user_prompt = (
        f"The Policy Agent has asked for your economic perspective on: {scenario_title}\n"
        "Provide the key economic considerations, tradeoffs, and cite supporting evidence."
    )

    return invoke_with_evidence(
        ECONOMIC_SYSTEM, user_prompt, evidence, recent_messages, temperature=0.3
    )
