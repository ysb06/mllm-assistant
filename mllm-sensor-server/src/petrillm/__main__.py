import os
from typing import Annotated, Dict, List

import aiosqlite
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from typing_extensions import TypedDict

from petrillm import GRAPH_IMAGE_PATH
from petrillm.graph import PetriState
from petrillm.graph import GraphGenGraph
from petrillm.node import node_find_next_action

graph = GraphGenGraph()
graph.invoke("Please make a Python crtypto currency.")