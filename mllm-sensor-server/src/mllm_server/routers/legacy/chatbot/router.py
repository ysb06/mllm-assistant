import json
import logging
import os
from typing import Annotated, AsyncIterable, List, Union

from fastapi import APIRouter
from fastapi.responses import FileResponse, StreamingResponse
from langchain_core.runnables.schema import StreamEvent
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from ....types import AssistantMessage, ChatRequest, UserMessage
from ....utils import convert_serializable

logger = logging.getLogger(__name__)
chatbot_router = APIRouter(prefix="/service/chatbot", tags=["chatbot"])


class State(TypedDict):
    messages: Annotated[list, add_messages]


os.makedirs("assets/chatbot", exist_ok=True)
graph_builder = StateGraph(State)
llm_llama = ChatOllama(model="llama3.1")


def node_llama_chatbot(state: State):
    return {"messages": [llm_llama.invoke(state["messages"])]}


graph_builder.add_node("chatbot", node_llama_chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
simple_chat_graph = graph_builder.compile()
simple_chat_graph.get_graph().draw_mermaid_png(
    output_file_path="assets/chatbot/state_graph.png"
)


@chatbot_router.get("/state-graph")
def get_chat_graph_image() -> FileResponse:
    return FileResponse("assets/chatbot/state_graph.png")


@chatbot_router.post("/")
async def chat_endpoint(chat_req: ChatRequest) -> StreamingResponse:
    if not chat_req.messages:
        return {"error": "No messages provided."}

    return StreamingResponse(stream_events(chat_req.messages))


async def stream_events(
    messages: List[Union[UserMessage, AssistantMessage]]
) -> AsyncIterable[str]:
    user_input = []
    for message in messages:
        # 현재는 Text Content만 지원
        if type(message.content) == str:
            user_input.append((message.role, message.content))
        else:
            content_type = type(message.content).__name__
            user_input.append((message.role, f"(Unknown Content: {content_type})"))

    langgraph_input = {"messages": user_input}
    async for event in simple_chat_graph.astream_events(langgraph_input, version="v2"):
        response = generate_event_response(event)
        yield response + "\n"  # ndjson 형식으로 반환


def generate_event_response(event: StreamEvent) -> str:
    event["data"] = convert_serializable(event["data"])
    return json.dumps(event)


# Code Reference: https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-1-build-a-basic-chatbot
