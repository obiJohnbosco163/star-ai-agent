import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from .state import AgentState


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

    if hasattr(tool, "run"):
        return tool.run(tool_args)

    if isinstance(tool_args, dict):
        return tool(**tool_args)
    return tool(tool_args)


def build_graph():
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file before running the agent.")

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=groq_api_key,
        temperature=0.0,
        max_tokens=400,
        max_retries=0,
    )

    system_prompt = (
        "You are S.T.A.R., the Sales Targeting & Readiness assistant. You turn a company URL and a prospect LinkedIn URL into a concise pre-call research brief. "
        "Given the user message, return only valid JSON with these exact fields: prospect_name, company_name, who_you_are_talking_to, company_context, why_now, suggested_opening, key_talking_points, and watch_out_for. "
        "Use the company and prospect page summaries in the user message to generate factual, sales-ready insights. "
        "Do not ask follow-up questions or ask for approval. Do not add any text outside the JSON object. "
        "If a field has no clear information, return a short explicit note rather than leaving it empty or blank. "
        "Provide enough detail to fill a single-page pre-call brief, but keep the JSON concise and easy to read."
    )

    def llm_node(state: AgentState):
        messages = [("system", system_prompt)] + state["messages"]
        response = llm.invoke(messages)
        content = getattr(response, "content", response)
        return {"sales_research_response": content}

    graph = StateGraph(AgentState)
    graph.add_node("llm", llm_node)
    graph.add_edge(START, "llm")
    graph.add_edge("llm", END)

    return graph.compile()


@lru_cache(maxsize=1)
def get_graph():
    return build_graph()
