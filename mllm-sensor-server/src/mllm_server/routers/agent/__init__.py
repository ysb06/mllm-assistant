import os

ROUTER_NAME = "agent"
ROUTER_ASSETS_DIR = f"assets/{ROUTER_NAME}"
os.makedirs(ROUTER_ASSETS_DIR, exist_ok=True)
CHECKPOINT_DATA_PATH = os.path.join(ROUTER_ASSETS_DIR, "checkpoint.sqlite")
GRAPH_IMAGE_PATH = os.path.join(ROUTER_ASSETS_DIR, "state_graph.png")
