from app.models.schemas import TopicResponse

SCENARIOS: list[TopicResponse] = [
    TopicResponse(
        slug="subsidize-plf-welfare",
        title="Should governments subsidize precision livestock farming technologies that improve animal welfare?",
        description=(
            "Deliberate whether public subsidies for PLF technologies that demonstrably improve "
            "animal welfare are justified, given costs, adoption barriers, and distributional impacts."
        ),
    ),
    TopicResponse(
        slug="mandatory-ai-welfare-large-farms",
        title="Should AI-based welfare monitoring systems be mandatory on large commercial farms?",
        description=(
            "Explore whether regulators should require AI welfare monitoring on large commercial "
            "operations, weighing enforcement feasibility, farmer burden, and welfare gains."
        ),
    ),
    TopicResponse(
        slug="ai-replace-human-inspections",
        title="Should continuous AI monitoring replace periodic human welfare inspections?",
        description=(
            "Examine whether continuous AI monitoring can supplement or replace periodic human "
            "inspections, including accuracy, trust, accountability, and oversight concerns."
        ),
    ),
    TopicResponse(
        slug="mandatory-ai-pain-detection",
        title="Should farms be required to use AI systems for early detection of animal pain and disease?",
        description=(
            "Consider whether mandatory AI-based early detection of pain and disease is warranted, "
            "including technology readiness, false positives, and farmer implementation burdens."
        ),
    ),
    TopicResponse(
        slug="certification-require-ai-monitoring",
        title="Should welfare certification schemes require AI-based continuous monitoring?",
        description=(
            "Discuss whether private or industry welfare certification programs should require "
            "continuous AI monitoring as a condition of certification."
        ),
    ),
    TopicResponse(
        slug="mandatory-public-welfare-reporting",
        title="Should farms be required to publicly report AI-collected animal welfare metrics?",
        description=(
            "Evaluate mandatory public disclosure of AI-collected welfare metrics, including "
            "transparency benefits, competitive concerns, and data interpretation risks."
        ),
    ),
    TopicResponse(
        slug="plf-data-ownership",
        title="Who should own and control animal welfare data collected through precision livestock farming systems?",
        description=(
            "Deliberate data ownership and control for PLF-collected welfare data among farmers, "
            "technology vendors, regulators, and other stakeholders."
        ),
    ),
    TopicResponse(
        slug="regulator-real-time-access",
        title="Should independent regulators have access to real-time animal welfare monitoring data?",
        description=(
            "Explore regulator access to real-time PLF welfare data, balancing oversight capacity, "
            "privacy, commercial sensitivity, and enforcement effectiveness."
        ),
    ),
    TopicResponse(
        slug="independent-ai-audit",
        title="Should AI systems used to monitor animal welfare be independently audited before deployment?",
        description=(
            "Consider pre-deployment independent auditing of AI welfare monitoring systems for "
            "accuracy, bias, reliability, and alignment with welfare standards."
        ),
    ),
    TopicResponse(
        slug="disclose-ai-welfare-decisions",
        title="Should farms disclose when animal welfare decisions are being made or assisted by AI systems?",
        description=(
            "Discuss transparency requirements when AI assists or automates animal welfare "
            "decisions, including consumer trust and accountability."
        ),
    ),
    TopicResponse(
        slug="financial-incentives-ai-welfare",
        title="Should governments provide financial incentives for farmers to adopt AI welfare technologies?",
        description=(
            "Deliberate financial incentives (grants, tax credits, subsidies) to accelerate adoption "
            "of AI technologies aimed at improving farmed animal welfare."
        ),
    ),
    TopicResponse(
        slug="welfare-justify-higher-prices",
        title="Should animal welfare improvements justify increased food prices resulting from precision livestock farming adoption?",
        description=(
            "Examine whether welfare gains from PLF adoption justify potential food price increases "
            "and how costs should be distributed across producers and consumers."
        ),
    ),
    TopicResponse(
        slug="small-farm-plf-support",
        title="Should small-scale farms receive additional support to adopt precision livestock farming technologies?",
        description=(
            "Consider targeted support for small-scale farms adopting PLF, addressing affordability, "
            "technical capacity, and equity in welfare technology access."
        ),
    ),
    TopicResponse(
        slug="public-funding-welfare-over-productivity",
        title="Should public funding prioritize AI technologies that improve animal welfare over those that only improve productivity?",
        description=(
            "Deliberate whether public R&D and subsidy programs should prioritize welfare-enhancing "
            "AI over productivity-only PLF innovations."
        ),
    ),
    TopicResponse(
        slug="economic-feasibility-limit-adoption",
        title="Should economic feasibility limit the adoption of welfare-enhancing AI technologies?",
        description=(
            "Explore whether economic feasibility should constrain mandatory or encouraged adoption "
            "of welfare-enhancing AI, especially for marginal or small operations."
        ),
    ),
    TopicResponse(
        slug="plf-improve-welfare-intensive",
        title="Can precision livestock farming meaningfully improve animal welfare within intensive farming systems?",
        description=(
            "Examine whether PLF can deliver meaningful welfare improvements within intensive "
            "systems, or whether structural limits cap potential gains."
        ),
    ),
    TopicResponse(
        slug="ai-prioritize-welfare-over-productivity",
        title="Should AI systems prioritize animal welfare when animal welfare and productivity objectives conflict?",
        description=(
            "Discuss programming and governance of AI systems when welfare and productivity "
            "objectives conflict, including who sets priorities and how."
        ),
    ),
    TopicResponse(
        slug="human-oversight-ai-recommendations",
        title="Should AI-generated animal welfare recommendations always require human oversight before implementation?",
        description=(
            "Consider mandatory human-in-the-loop oversight before acting on AI welfare "
            "recommendations, including latency, training, and liability implications."
        ),
    ),
    TopicResponse(
        slug="national-ethical-guidelines-ai-farms",
        title="Should governments establish national ethical guidelines for AI used in farmed animal welfare?",
        description=(
            "Deliberate national ethical frameworks for AI in farmed animal welfare, including "
            "scope, enforcement, and relationship to existing welfare standards."
        ),
    ),
    TopicResponse(
        slug="ai-evidence-legal-proceedings",
        title="Should evidence from AI-based welfare monitoring systems be admissible in animal welfare enforcement and legal proceedings?",
        description=(
            "Examine admissibility and reliability of AI-collected welfare evidence in enforcement "
            "actions and legal proceedings, including standards of proof and challenge rights."
        ),
    ),
]


def get_scenario_by_slug(slug: str) -> TopicResponse | None:
    return next((s for s in SCENARIOS if s.slug == slug), None)


def list_scenarios() -> list[TopicResponse]:
    return SCENARIOS
