import logging
import os
from typing import Annotated, Dict, List, TypedDict

from langgraph.graph.message import add_messages

logging.basicConfig(
    format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.INFO,
)

ROUTER_NAME = "agent"
ROUTER_ASSETS_DIR = f"assets/{ROUTER_NAME}"
os.makedirs(ROUTER_ASSETS_DIR, exist_ok=True)
CHECKPOINT_DATA_PATH = os.path.join(ROUTER_ASSETS_DIR, "checkpoint.sqlite")
GRAPH_IMAGE_PATH = os.path.join(ROUTER_ASSETS_DIR, "state_graph.png")

class PetriState(TypedDict):
    messages: Annotated[List, add_messages]
    contexts: Dict[str, str]