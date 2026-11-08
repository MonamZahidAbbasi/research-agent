from app.graph.state import ResearchAgentState


def route_after_verification(state: ResearchAgentState) -> str:
    claims = state["claims"]

    if claims and all(c["verification_status"] == "verified" for c in claims):
        return "synthesizer"

    return "human_review"