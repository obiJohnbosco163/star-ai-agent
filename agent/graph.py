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
        max_tokens=700,
        max_retries=0,
    )

    system_prompt = (
        "You are S.T.A.R., the Sales Targeting & Readiness assistant. You turn a company URL and a prospect LinkedIn URL into a long, human-readable pre-call research briefing. "
        "Write a detailed business-ready report with clear section headings: Prospect, Company Context, Why Now, Suggested Opening, Key Talking Points, and Watch Out For. "
        "Use the company and prospect page summaries in the user message to include specific evidence, product or role signals, and recent activity from the URLs. "
        "Make each section at least three sentences long and explain why this call is worth the user's time. "
        "Do not return JSON or code formatting. Return a readable plain-text briefing only."
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
