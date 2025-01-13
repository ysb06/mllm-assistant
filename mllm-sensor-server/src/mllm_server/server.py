import json
import logging
import os
from typing import Annotated, Any, AsyncIterable, Dict, List, Union

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langchain_core.runnables.schema import StreamEvent

from .types import ChatRequest, UserMessage, AssistantMessage
from pydantic import BaseModel

load_dotenv()

logger = logging.getLogger(__name__)


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


fastapi_app = FastAPI()
os.makedirs("assets", exist_ok=True)

origins = [
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 혹은 특정 도메인만 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph_builder = StateGraph(State)

llm_llama = ChatOllama(model="llama3.1")
llm_gpt4omini = ChatOpenAI(model="gpt-4o-mini")


def node_llama_chatbot(state: State):
    return {"messages": [llm_llama.invoke(state["messages"])]}


graph_builder.add_node("chatbot", node_llama_chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
simple_chat_graph = graph_builder.compile()

simple_chat_graph.get_graph().draw_mermaid_png(output_file_path="assets/chat_graph.png")


# ----- APIs -----


@fastapi_app.get("/")
def read_root() -> Dict[str, str]:
    return {"Hello": "World"}

@fastapi_app.get("/chat/graph")
def get_chat_graph_image() -> FileResponse:
    return FileResponse("assets/chat_graph.png")

@fastapi_app.post("/chat")
async def chat_endpoint(chat_req: ChatRequest) -> StreamingResponse:
    if not chat_req.messages:
        return {"error": "No messages provided."}

    return StreamingResponse(stream_events(chat_req.messages))


async def stream_events(
    messages: List[Union[UserMessage, AssistantMessage]]
) -> AsyncIterable[str]:
    user_input = []
    for message in messages:
        if type(message.content) == str:
            # 현재는 Text Content만 지원
            user_input.append((message.role, message.content))
        else:
            content_type = type(message.content).__name__
            user_input.append(
                (
                    message.role,
                    f"(Failed to recognize the content. The type of this may be {content_type})",
                )
            )

    langgraph_input = {"messages": user_input}
    async for event in simple_chat_graph.astream_events(langgraph_input, version="v2"):
        response = generate_event_response(event)
        yield response + "\n"


def generate_serializable(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return {k: generate_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [generate_serializable(v) for v in obj]
    elif (
        isinstance(obj, str)
        or isinstance(obj, int)
        or isinstance(obj, float)
        or obj is None
    ):
        return obj
    else:
        logger.warning(f"Non-serialize: {obj}")
        return "(Unknown Object)"


def generate_event_response(event: StreamEvent) -> str:
    event["data"] = generate_serializable(event["data"])
    return json.dumps(event)
