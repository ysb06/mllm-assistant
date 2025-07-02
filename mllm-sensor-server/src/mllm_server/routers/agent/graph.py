import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph

from . import CHECKPOINT_DATA_PATH, GRAPH_IMAGE_PATH, State
from .node import (
    node_llama_chatbot,
    node_vehicle_context_fetch,
    node_webcam_context_fetch,
)

graph_builder = StateGraph(State)
# Add Nodes
graph_builder.add_node("chatbot", node_llama_chatbot)
graph_builder.add_node("vehicle_context", node_vehicle_context_fetch)
graph_builder.add_node("webcam_context", node_webcam_context_fetch)
# Add Edges
graph_builder.add_edge(START, "vehicle_context")
graph_builder.add_edge(START, "webcam_context")
graph_builder.add_edge(["vehicle_context", "webcam_context"], "chatbot")
graph_builder.add_edge("chatbot", END)

# Compile the graph
sqlite_conn = aiosqlite.connect(CHECKPOINT_DATA_PATH)
memory = AsyncSqliteSaver(sqlite_conn)
chat_graph = graph_builder.compile(checkpointer=memory)
chat_graph.get_graph().draw_png(output_file_path=GRAPH_IMAGE_PATH)
