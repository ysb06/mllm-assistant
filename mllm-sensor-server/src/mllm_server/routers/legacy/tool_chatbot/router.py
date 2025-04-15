import json
import logging
import os
from typing import Annotated, AsyncIterable, List, Optional, Union

from fastapi import APIRouter
from fastapi.responses import FileResponse, StreamingResponse
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables.schema import StreamEvent
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite

from ....types import AssistantMessage, ChatRequest, UserMessage
from ....utils import convert_serializable

logger = logging.getLogger(__name__)
tool_chatbot_router = APIRouter(prefix="/service/tool-chatbot", tags=["chatbot"])


class State(TypedDict):
    messages: Annotated[list, add_messages]


os.makedirs("assets/tool-chatbot", exist_ok=True)


tavily_tool = TavilySearchResults(max_results=2)
tools = [tavily_tool]

llm_llama = ChatOllama(model="llama3.1")
tools_llm = llm_llama.bind_tools(tools)
# llm_gpt = ChatOpenAI(model="gpt-4o-mini")
# tools_llm = llm_gpt.bind_tools(tools)


def node_llama_chatbot(state: State):
    return {"messages": [tools_llm.invoke(state["messages"])]}
    # return {"messages": [tools_llm_gpt.invoke(state["messages"])]}


sqlite_conn = aiosqlite.connect("assets/tool-chatbot/checkpoint.sqlite")
memory = AsyncSqliteSaver(sqlite_conn)

graph_builder = StateGraph(State)
# Add Nodes
graph_builder.add_node("chatbot", node_llama_chatbot)
graph_builder.add_node("tools", ToolNode(tools=[tavily_tool]))
# Add Edges
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")

simple_chat_graph = graph_builder.compile(
    checkpointer=memory,
    # interrupt_before=["tools"],
)
simple_chat_graph.get_graph().draw_mermaid_png(
    output_file_path="assets/tool-chatbot/state_graph.png"
)


@tool_chatbot_router.get("/state-graph")
def get_chat_graph_image() -> FileResponse:
    return FileResponse("assets/tool-chatbot/state_graph.png")


@tool_chatbot_router.post("/")
async def chat_endpoint(chat_req: ChatRequest) -> StreamingResponse:
    if not chat_req.messages:
        return {"error": "No messages provided."}

    return StreamingResponse(stream_events(chat_req.messages, session=chat_req.session))


@tool_chatbot_router.get("/sessions")
def list_sessions():
    sessions = set()
    for session in memory.list(None):
        sessions.add(session.config["configurable"]["thread_id"])
    return {"sessions": list(sessions)}


async def stream_events(
    messages: List[Union[UserMessage, AssistantMessage]],
    session: Optional[str] = None,
) -> AsyncIterable[str]:
    user_input = []
    for message in reversed(messages):
        # 현재는 Text Content만 지원
        if message.role == "user":
            if type(message.content) == str:
                user_input.append((message.role, message.content))
                break
            else:
                content_type = type(message.content).__name__
                user_input.append((message.role, f"(Unknown Content: {content_type})"))

    langgraph_input = {"messages": user_input}
    config = {
        "configurable": {"thread_id": session if session is not None else "default"}
    }
    async for event in simple_chat_graph.astream_events(
        langgraph_input,
        config=config,
        version="v2",
    ):
        response = generate_event_response(event)
        yield response + "\n"  # ndjson 형식으로 반환


def generate_event_response(event: StreamEvent) -> str:
    event["data"] = convert_serializable(event["data"])
    return json.dumps(event)


# Code Reference: https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-1-build-a-basic-chatbot
