import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph

from ... import CHECKPOINT_DATA_PATH, GRAPH_IMAGE_PATH
from .state import State
from .node import (
    node_fetch_vehicle_context,
    node_fetch_webcam_context,
    node_extract_image_context,
    node_run_chatbot,
)

graph_builder = StateGraph(State)
# Add Nodes
graph_builder.add_node("node_fetch_vehicle_context", node_fetch_vehicle_context)
graph_builder.add_node("node_fetch_webcam_context", node_fetch_webcam_context)
graph_builder.add_node("node_extract_image_context", node_extract_image_context)
graph_builder.add_node("node_run_chatbot", node_run_chatbot)
# Add Edges
graph_builder.add_edge(START, "node_fetch_webcam_context")
graph_builder.add_edge(START, "node_fetch_vehicle_context")
graph_builder.add_edge("node_fetch_webcam_context", "node_extract_image_context")
graph_builder.add_edge(["node_fetch_vehicle_context", "node_extract_image_context"], "node_run_chatbot")
graph_builder.add_edge("node_run_chatbot", END)

# Compile the graph
sqlite_conn = aiosqlite.connect(CHECKPOINT_DATA_PATH)
memory = AsyncSqliteSaver(sqlite_conn)
chat_graph = graph_builder.compile(checkpointer=memory)
chat_graph.get_graph().draw_png(output_file_path=GRAPH_IMAGE_PATH)
