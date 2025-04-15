import json
import logging
import os
from typing import Annotated, AsyncIterable, Dict, List, Optional, Union

import aiosqlite
from fastapi import APIRouter
from fastapi.responses import FileResponse, StreamingResponse
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables.schema import StreamEvent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from ...scaner_udp import ScanerFilterServer
from ...types import AssistantMessage, ChatRequest, UserMessage
from ...utils import convert_serializable

logger = logging.getLogger(__name__)

os.makedirs("assets/chatbot", exist_ok=True)

llm_llama = ChatOllama(model="llama3.1")

sensor_server = ScanerFilterServer()
sensor_server.activate()


chatbot_router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class State(TypedDict):
    messages: Annotated[List, add_messages]
    contexts: Dict[str, str]


def node_vehicle_context_fetch(state: State):
    sensor_data = sensor_server.get_sensor_data()
    sensor_context = {
        "Steering Angle": str(sensor_data.get("steering", [])),
        "Speed": str(sensor_data.get("speed", [])),
    }
    state["contexts"] = sensor_context
    return state


def node_llama_chatbot(state: State):
    # 프롬프트를 통해 차량의 상태는 사용자가 질문하기 전까지는 언급하지 않도록 하는 것이 필요할 수 있음
    # 차량의 상태를 사용자의 질의를 생성
    user_query: HumanMessage = state["messages"][-1]
    user_query_message: str = user_query.content
    user_query_message += "-" * 16 + "\n" + "Current User's Vehicle State:\n"
    for key, value in state["contexts"].items():
        user_query_message += f"{key}: {value}\n"

    # 차량의 상태를 포함한 질의를 LLM에 주입
    query: List[BaseMessage] = state["messages"]
    query[-1].content = user_query_message

    result = llm_llama.invoke(query)
    return {"messages": [result]}


graph_builder = StateGraph(State)
# Add Nodes
graph_builder.add_node("chatbot", node_llama_chatbot)
graph_builder.add_node("vehicle_context", node_vehicle_context_fetch)
# Add Edges
graph_builder.add_edge(START, "vehicle_context")
graph_builder.add_edge("vehicle_context", "chatbot")
graph_builder.add_edge("chatbot", END)
# Compile the graph
sqlite_conn = aiosqlite.connect("assets/chatbot/checkpoint.sqlite")
memory = AsyncSqliteSaver(sqlite_conn)
simple_chat_graph = graph_builder.compile(
    checkpointer=memory,
)
simple_chat_graph.get_graph().draw_png(
    output_file_path="assets/chatbot/state_graph.png",
)


@chatbot_router.get("/state-graph")
def get_chat_graph_image() -> FileResponse:
    return FileResponse("assets/chatbot/state_graph.png")


@chatbot_router.post("/")
async def chat_endpoint(chat_req: ChatRequest) -> StreamingResponse:
    if not chat_req.messages:
        return {"error": "No messages provided."}

    return StreamingResponse(stream_events(chat_req.messages, session=chat_req.session))


@chatbot_router.get("/sessions")
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
