from typing import List

from langgraph.graph import MessagesState
from pydantic import BaseModel


class SalesResearchResponse(BaseModel):
    prospect_name: str
    company_name: str
    who_you_are_talking_to: str
    company_context: str
    why_now: str
    suggested_opening: str
    key_talking_points: List[str]
    watch_out_for: List[str]


class AgentState(MessagesState):
    sales_research_response: SalesResearchResponse | None = None
