from typing import Annotated, Dict, List

import aiosqlite
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from typing_extensions import TypedDict

from petrillm import GRAPH_IMAGE_PATH, PetriState
from petrillm.node import node_find_next_action


class GraphGenGraph:
    def __init__(self):
        self.graph_builder = StateGraph(PetriState)
        # Add Nodes
        self.graph_builder.add_node("chatbot", node_find_next_action)
        # Add Edges
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)
        self.chat_graph = self.graph_builder.compile()
        self.chat_graph.get_graph().draw_png(output_file_path=GRAPH_IMAGE_PATH)
    
    def invoke(self, user_query: str):
        init_state = PetriState(messages=[HumanMessage(content=user_query)])
        for event in self.chat_graph.stream(init_state):
            print(event)