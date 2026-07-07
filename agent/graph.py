import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from .state import AgentState, SalesResearchResponse
from .tools import research_company, research_prospect, generate_precall_report


def load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()


def _invoke_tool(tool_name: str, tool_args: Any) -> str:
    tool_map = {
        "research_company": research_company,
        "research_prospect": research_prospect,
        "generate_precall_report": generate_precall_report,
    }
    tool = tool_map[tool_name]
    if isinstance(tool_args, dict):
        return tool(**tool_args)
    return tool(tool_args)


def build_graph():
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file before running the agent.")

    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_api_key, temperature=0.2)
    research_tools = [research_company, research_prospect, generate_precall_report]
    llm_with_tools = llm.bind_tools(research_tools)

    structured_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a sales research assistant. Use the conversation and any tool results to produce a structured sales research summary.
            Return the output as a JSON object matching the requested schema.
            Focus on the prospect, company context, why now, a suggested opening, key talking points, and watch-outs.""",
        ),
        ("placeholder", "{messages}"),
    ])
    responder_chain = structured_prompt | llm.with_structured_output(SalesResearchResponse)

    def llm_node(state: AgentState):
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def research_company_node(state: AgentState):
        tool_call = state["messages"][-1].tool_calls[0]
        result = _invoke_tool("research_company", tool_call.get("args", {}))
        return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

    def research_prospect_node(state: AgentState):
        tool_call = state["messages"][-1].tool_calls[0]
        result = _invoke_tool("research_prospect", tool_call.get("args", {}))
        return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

    def generate_report_node(state: AgentState):
        tool_call = state["messages"][-1].tool_calls[0]
        result = _invoke_tool("generate_precall_report", tool_call.get("args", {}))
        return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

    def responder_node(state: AgentState):
        structured = responder_chain.invoke({"messages": state["messages"]})
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
