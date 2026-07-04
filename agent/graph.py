from functools import lru_cache
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, START, END
from .state import AgentState, SalesResearchResponse
from .tools import research_company, research_prospect, generate_precall_report


def build_graph():
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    research_tools = [research_company, research_prospect, generate_precall_report]
    llm_with_tools = llm.bind_tools(research_tools)
    responder_llm = llm.with_structured_output(SalesResearchResponse)

    def llm_node(state: AgentState):
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def research_company_node(state: AgentState):
        tool_call = state["messages"][-1].tool_calls[0]
        result = research_company.invoke(tool_call["args"])
        return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

    def research_prospect_node(state: AgentState):
        tool_call = state["messages"][-1].tool_calls[0]
        result = research_prospect.invoke(tool_call["args"])
        return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

    def generate_report_node(state: AgentState):
        tool_call = state["messages"][-1].tool_calls[0]
        result = generate_precall_report.invoke(tool_call["args"])
        return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

    def responder_node(state: AgentState):
        structured = responder_llm.invoke(state["messages"])
        return {"sales_research_response": structured}

    def route_after_llm(state: AgentState):
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            tool_name = last_message.tool_calls[0]["name"]
            if tool_name == "research_company":
                return "research_company"
            if tool_name == "research_prospect":
                return "research_prospect"
            if tool_name == "generate_precall_report":
                return "generate_report"
        return "responder"

    graph = StateGraph(AgentState)
    graph.add_node("llm", llm_node)
    graph.add_node("research_company", research_company_node)
    graph.add_node("research_prospect", research_prospect_node)
    graph.add_node("generate_report", generate_report_node)
    graph.add_node("responder", responder_node)

    graph.add_edge(START, "llm")
    graph.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "research_company": "research_company",
            "research_prospect": "research_prospect",
            "generate_report": "generate_report",
            "responder": "responder",
        },
    )
    graph.add_edge("research_company", "llm")
    graph.add_edge("research_prospect", "llm")
    graph.add_edge("generate_report", "llm")
    graph.add_edge("responder", END)

    return graph.compile()


@lru_cache(maxsize=1)
def get_graph():
    return build_graph()
