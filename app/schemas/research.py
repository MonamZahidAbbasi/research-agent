from pydantic import BaseModel, Field

class ResearchPlan(BaseModel):
    objective: str=Field(description="one sentence describing what the research must find out")
    sub_questions: list[str]=Field(description="3 to 5 specific, searchable questions that together answer the obective")