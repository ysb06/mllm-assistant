import os
from typing_extensions import TypedDict
from typing import Annotated, Dict, List
from langgraph.graph.message import add_messages

ROUTER_NAME = "agent"
ROUTER_ASSETS_DIR = f"assets/{ROUTER_NAME}"
os.makedirs(ROUTER_ASSETS_DIR, exist_ok=True)
CHECKPOINT_DATA_PATH = os.path.join(ROUTER_ASSETS_DIR, "checkpoint.sqlite")
GRAPH_IMAGE_PATH = os.path.join(ROUTER_ASSETS_DIR, "state_graph.png")

def merge_contexts(current: Dict[str, str], new: Dict[str, str]) -> Dict[str, str]:
    if current is None:
        return new
    merged = current.copy()
    merged.update(new)
    return merged

class State(TypedDict):
    messages: Annotated[List, add_messages]
    sensor_contexts: Annotated[Dict[str, str], merge_contexts]
    visual_contexts: Annotated[Dict[str, str], merge_contexts]

from .graph import chat_graph, memory
from .router import agent_router
