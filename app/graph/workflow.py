from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import ResearchAgentState
from app.graph.nodes import (
    planner_node,
    researcher_node,
    claim_extractor_node,
    verifier_node,
    human_review_node,
    synthesizer_node,
)
from app.graph.edges import route_after_verification


def build_graph(checkpointer=None):
    builder = StateGraph(ResearchAgentState)

    builder.add_node("planner", planner_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("claim_extractor", claim_extractor_node)
    builder.add_node("verifier", verifier_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("synthesizer", synthesizer_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "claim_extractor")
    builder.add_edge("claim_extractor", "verifier")

    builder.add_conditional_edges(
        "verifier",
        route_after_verification,
        {"synthesizer": "synthesizer", "human_review": "human_review"},
    )

    builder.add_edge("human_review", "synthesizer")
    builder.add_edge("synthesizer", END)

    return builder.compile(
        checkpointer=checkpointer or MemorySaver(),
        interrupt_before=["human_review"],
    )


research_graph = build_graph()


def make_initial_state(user_query: str) -> dict:
    return {
        "user_query": user_query,
        "plan": [],
        "search_results": [],
        "claims": [],
        "human_feedback": "",
        "final_report": "",
        "step_count": 0,
        "messages": [],
    }