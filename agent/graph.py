from functools import lru_cache
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, START, END
from .state import AgentState, WeatherResponse
from .tools import get_weather


def build_graph():
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    llm_with_tools = llm.bind_tools([get_weather])
    responder_llm = llm.with_structured_output(WeatherResponse)

    def llm_node(state: AgentState):
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def weather_node(state: AgentState):
        tool_call = state["messages"][-1].tool_calls[0]
        result = get_weather.invoke(tool_call["args"])
        return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

    def responder_node(state: AgentState):
        structured = responder_llm.invoke(state["messages"])
        return {"weather_response": structured}

    def has_tool_call(state: AgentState):
        last = state["messages"][-1]
        return "weather" if getattr(last, "tool_calls", None) else "respond"

    graph = StateGraph(AgentState)
    graph.add_node("llm", llm_node)
    graph.add_node("weather", weather_node)
    graph.add_node("responder", responder_node)

    graph.add_edge(START, "llm")
    graph.add_conditional_edges(
        "llm", has_tool_call, {"weather": "weather", "respond": "responder"}
    )
    graph.add_edge("weather", "responder")
    graph.add_edge("responder", END)

    return graph.compile()


@lru_cache(maxsize=1)
def get_graph():
    return build_graph()
