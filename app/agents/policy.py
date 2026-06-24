from app.agents.base import get_llm, invoke_with_evidence, retrieve_for_context
from app.models.schemas import (
    AgentResponse,
    DeliberationStage,
    PolicyAction,
    PolicyRouterDecision,
    Recommendation,
)
from langchain_core.messages import HumanMessage, SystemMessage


POLICY_SYSTEM = """You are the Policy Agent facilitating an evidence-based deliberation on
precision livestock farming (PLF) and animal welfare policy.

Your role is STRICTLY facilitation — you do NOT advocate for any position.
You introduce topics, ask clarifying questions, identify unresolved issues,
request evidence when needed, decide which stakeholder to consult, summarize
discussion progress, and produce final recommendations when appropriate.

The user is always the Animal Welfare Advocate — they are the primary participant.
Keep stakeholder consultations brief and always return focus to the user.

Be transparent, neutral, and evidence-oriented."""


ROUTER_SYSTEM = """You are the Policy Agent router deciding the next deliberation action.

Available actions:
- ASK_USER_QUESTION: Ask the user (Animal Welfare Advocate) a question or follow-up
- CALL_ECONOMIC_AGENT: Consult the Economic Agent on costs, adoption, livelihoods
- CALL_ENVIRONMENTAL_AGENT: Consult the Environmental Agent on sustainability impacts
- REQUEST_EVIDENCE: Retrieve and present relevant evidence to the discussion
- SUMMARIZE_DISCUSSION: Summarize progress and unresolved issues so far
- ISSUE_RECOMMENDATION: Generate final evidence-based recommendation (use only after sufficient discussion)

Rules:
- After a stakeholder responds, prefer ASK_USER_QUESTION to keep the user centered
- Do not call stakeholders consecutively without user interaction
- Use REQUEST_EVIDENCE when claims need grounding
- Use ISSUE_RECOMMENDATION only after at least 4 user turns and a summary
- Never advocate for a policy position yourself"""


def route_next_action(
    stage: DeliberationStage,
    turn_count: int,
    last_action: str | None,
    recent_messages: list[dict],
    scenario_title: str,
    user_input: str | None,
) -> PolicyRouterDecision:
    llm = get_llm(temperature=0)
    structured = llm.with_structured_output(PolicyRouterDecision)

    history = "\n".join(
        f"{m['role']}: {m['content'][:200]}" for m in recent_messages[-8:]
    )

    prompt = (
        f"Scenario: {scenario_title}\n"
        f"Stage: {stage.value}\n"
        f"Turn count: {turn_count}\n"
        f"Last action: {last_action or 'none'}\n"
        f"Latest user input: {user_input or 'none (session start)'}\n\n"
        f"Recent history:\n{history}\n\n"
        "Decide the next action."
    )

    if stage == DeliberationStage.INTRO:
        return PolicyRouterDecision(
            action=PolicyAction.ASK_USER_QUESTION,
            reasoning="Introduce the scenario and invite the user's opening perspective.",
        )

    return structured.invoke(
        [SystemMessage(content=ROUTER_SYSTEM), HumanMessage(content=prompt)]
    )


def generate_policy_response(
    action: PolicyAction,
    scenario_title: str,
    scenario_description: str,
    recent_messages: list[dict],
    user_input: str | None,
    evidence_category: str | None = None,
) -> AgentResponse:
    evidence = retrieve_for_context(
        user_input, recent_messages, scenario_title, category=evidence_category
    )

    if action == PolicyAction.ASK_USER_QUESTION and not recent_messages:
        user_prompt = (
            f"Introduce the deliberation scenario: '{scenario_title}'.\n"
            f"Context: {scenario_description}\n"
            "Welcome the Animal Welfare Advocate, explain your facilitator role, "
            "and ask for their opening perspective on this policy question."
        )
    elif action == PolicyAction.ASK_USER_QUESTION:
        user_prompt = (
            "Based on the discussion so far, ask the Animal Welfare Advocate a thoughtful "
            "follow-up question to advance the deliberation."
        )
    elif action == PolicyAction.REQUEST_EVIDENCE:
        user_prompt = (
            "Present the most relevant evidence from the knowledge base to the discussion. "
            "Explain why this evidence matters for the current question."
        )
    elif action == PolicyAction.SUMMARIZE_DISCUSSION:
        user_prompt = (
            "Summarize the deliberation progress so far: key points raised, areas of "
            "agreement/disagreement, unresolved issues, and what evidence has been cited."
        )
    else:
        user_prompt = "Respond as the Policy Agent facilitator."

    return invoke_with_evidence(
        POLICY_SYSTEM, user_prompt, evidence, recent_messages, temperature=0.4
    )


def generate_recommendation(
    scenario_title: str,
    recent_messages: list[dict],
) -> Recommendation:
    llm = get_llm(temperature=0.3)
    structured = llm.with_structured_output(Recommendation)

    evidence = retrieve_for_context(None, recent_messages, scenario_title)
    from app.retrieval.retriever import format_evidence_for_prompt

    history = "\n".join(f"{m['role']}: {m['content']}" for m in recent_messages)
    evidence_text = format_evidence_for_prompt(evidence)

    prompt = (
        f"Scenario: {scenario_title}\n\n"
        f"Discussion transcript:\n{history}\n\n"
        f"Available evidence:\n{evidence_text}\n\n"
        "As the neutral Policy Agent, produce a final evidence-based recommendation. "
        "Include supporting arguments, key tradeoffs, areas of uncertainty, and cite evidence."
    )

    result: Recommendation = structured.invoke(
        [SystemMessage(content=POLICY_SYSTEM), HumanMessage(content=prompt)]
    )

    if not result.evidence_cited and evidence:
        from app.retrieval.retriever import evidence_to_citations

        result.evidence_cited = evidence_to_citations(evidence)

    return result
