import json
import os
from typing import Annotated, Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages.ai import AIMessageChunk
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict

from .types import ChatRequest

from pprint import pprint

load_dotenv()


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


fastapi_app = FastAPI()
os.makedirs("assets", exist_ok=True)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
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
graph = graph_builder.compile()

graph.get_graph().draw_mermaid_png(output_file_path="assets/graph.png")


# ----- APIs -----


@fastapi_app.get("/")
def read_root() -> Dict[str, str]:
    return {"Hello": "World"}


@fastapi_app.post("/chat")
async def chat_endpoint(chat_req: ChatRequest) -> Dict[str, Any]:
    if not chat_req.messages:
        return {"error": "No messages provided."}

    return StreamingResponse(stream_chat_llama(chat_req.messages))


async def stream_chat_llama(messages: list):
    user_input = messages[-1].content
    async for event in graph.astream_events(
        {"messages": [("user", user_input)]},
        version="v1",
    ):
        kind = event["event"]
        print(f"{kind}: {event['name']}")

        if event["event"] == "on_chat_model_stream":
            data_chunk: AIMessageChunk = event["data"]["chunk"]
            pprint(data_chunk.content)
            chunk = {
                "event": event["event"],
                "content": data_chunk.content,
            }
            yield json.dumps(chunk)
        else:
            pprint(event)
