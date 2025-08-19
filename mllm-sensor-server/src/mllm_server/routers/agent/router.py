import json
import logging
from typing import AsyncIterable, List, Optional, Union

from fastapi import APIRouter
from fastapi.responses import FileResponse, StreamingResponse

from ...types import AssistantMessage, ChatRequest, UserMessage
from ...utils import convert_serializable
from . import GRAPH_IMAGE_PATH, ROUTER_NAME
from .model.oss_gpt.graph import chat_graph, memory

logger = logging.getLogger(__name__)
agent_router = APIRouter(prefix=f"/{ROUTER_NAME}", tags=[f"{ROUTER_NAME}"])


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
    async for event in chat_graph.astream_events(
        langgraph_input,
        config=config,
        version="v2",
    ):
        event["data"] = convert_serializable(event["data"])
        yield json.dumps(event) + "\n"  # ndjson 형식으로 반환


@agent_router.post("/")
async def chat_endpoint(chat_req: ChatRequest) -> StreamingResponse:
    if not chat_req.messages:
        return {"error": "No messages provided."}

    return StreamingResponse(stream_events(chat_req.messages, session=chat_req.session))


@agent_router.get("/state-graph")
def get_chat_graph_image() -> FileResponse:
    return FileResponse(GRAPH_IMAGE_PATH)


@agent_router.get("/sessions")
def list_sessions():
    sessions = set()
    for session in memory.list(None):
        sessions.add(session.config["configurable"]["thread_id"])
    return {"sessions": list(sessions)}
