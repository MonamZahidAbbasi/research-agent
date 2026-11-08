import operator
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

class ResearchAgentState(TypedDict):
    user_query:str
    plan:list[str]
    search_results:Annotated[list[dict], operator.add]
    claims:list[dict]
    human_feedback:str
    final_report:str
    step_count:int
    messages:Annotated[list[str], add_messages]
    