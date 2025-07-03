from typing import Annotated, Dict, List, TypedDict
import logging

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from . import State
from ...scaner_udp import ScanerFilterServer
from ...webcam import capture_webcam_image

logger = logging.getLogger(__name__)


class CodeOutput(BaseModel):
    answer: str = Field(description="Answer to the query")
    python_function: str = Field(
        description="Python code used to derive the answer. The LLM should write the solution code as a Python function that returns the correct answer."
    )
    python_function_args: Dict[str, str] = Field(
        description="Arguments passed as **kwargs to the python_function to obtain the answer to the query. These arguments must ensure the python_function returns the correct answer when called."
    )


sensor_server = ScanerFilterServer()
sensor_server.activate()

# llm_llama = ChatOllama(model="llama3.1")
llm_llama = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
llm_llama_code_structured = llm_llama.with_structured_output(
    CodeOutput, include_raw=True
)


def node_find_next_action(state: State):
    query: List[BaseMessage] = state["messages"]
    current_user_query: HumanMessage = query[-1]
    user_query_message: str = current_user_query.content
    result = llm_llama_code_structured.invoke(user_query_message)


def node_llama_chatbot(state: State):
    query: List[BaseMessage] = state["messages"]
    current_query: HumanMessage = state["messages"][-1]
    current_query_text: str = current_query.content

    if "sensor_contexts" in state:
        current_query_text += "-" * 10 + "\r\n"
        for key, value in state["sensor_contexts"].items():
            current_query_text += f"{key}: {value}\r\n"

    current_query = HumanMessage(
        content=[{
            "type": "text",
            "text": current_query_text,
        }],
    )
    if "visual_contexts" in state:
        current_query.content.append(state["visual_contexts"])

    query[-1] = current_query
    result = llm_llama.invoke(query)
    return {"messages": [result]}


def node_vehicle_context_fetch(state: State):
    sensor_data = sensor_server.get_sensor_data()
    sensor_context = {
        "Current User's Vehicle State": "",
        "Steering Angle": str(sensor_data.get("steering", [])),
        "Speed": str(sensor_data.get("speed", [])),
    }
    state["sensor_contexts"] = sensor_context
    return state


def node_webcam_context_fetch(state: State):
    base64_jpg = capture_webcam_image().decode("utf-8")
    state["visual_contexts"] = {
        "type": "image_url",
        "image_url": f"data:image/jpeg;base64,{base64_jpg}",  # Data URI 형식 사용
    }
    return state


if __name__ == "__main__":
    sample_state = {"messages": [HumanMessage(content="What is 3653 + 111?")]}
    node_find_next_action(sample_state)
