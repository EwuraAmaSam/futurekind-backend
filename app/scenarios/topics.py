from app.models.schemas import TopicResponse

SCENARIOS: list[TopicResponse] = [
    TopicResponse(
        slug="subsidize-plf",
        title="Should governments subsidize precision livestock farming technologies?",
        description=(
            "Deliberate whether public subsidies for PLF technologies (AI monitoring, "
            "automated welfare sensors, precision feeding) are justified given costs, "
            "adoption barriers, and animal welfare outcomes."
        ),
    ),
    TopicResponse(
        slug="mandatory-ai-welfare",
        title="Should AI welfare monitoring be mandatory?",
        description=(
            "Explore whether regulators should require AI-based animal welfare monitoring "
            "in livestock operations, weighing enforcement feasibility, farmer burden, "
            "and welfare improvements."
        ),
    ),
    TopicResponse(
        slug="ai-vs-human-inspection",
        title="Can AI monitoring replace human inspections?",
        description=(
            "Examine whether AI monitoring systems can supplement or replace traditional "
            "human welfare inspections, including accuracy, trust, and accountability concerns."
        ),
    ),
]


def get_scenario_by_slug(slug: str) -> TopicResponse | None:
    return next((s for s in SCENARIOS if s.slug == slug), None)


def list_scenarios() -> list[TopicResponse]:
    return SCENARIOS
