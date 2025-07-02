from typing import Annotated, Dict, List, TypedDict
import logging

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
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

llm_llama = ChatOllama(model="llama3.1")
llm_llama_code_structured = llm_llama.with_structured_output(
    CodeOutput, include_raw=True
)


def node_find_next_action(state: State):
    query: List[BaseMessage] = state["messages"]
    current_user_query: HumanMessage = query[-1]
    user_query_message: str = current_user_query.content
    result = llm_llama_code_structured.invoke(user_query_message)
    print(result)


def node_llama_chatbot(state: State):
    query: List[BaseMessage] = state["messages"]
    user_query: HumanMessage = state["messages"][-1]
    user_query_content = user_query.content
    
    # Handle sensor contexts - append to text content
    if "sensor_contexts" in state and state["sensor_contexts"]:
        if isinstance(user_query_content, str):
            user_query_content += "-" * 10 + "\r\n"
            for key, value in state["sensor_contexts"].items():
                user_query_content += f"{key}: {value}\r\n"
        else:
            # If content is already a list, find text content and append
            for content_item in user_query_content:
                if content_item.get("type") == "text":
                    content_item["text"] += "-" * 10 + "\r\n"
                    for key, value in state["sensor_contexts"].items():
                        content_item["text"] += f"{key}: {value}\r\n"
                    break
    
    # Handle visual contexts - convert to multimodal format if needed
    if "visual_contexts" in state and state["visual_contexts"]:
        if isinstance(user_query_content, str):
            # Convert string to multimodal format
            user_query_content = [
                {
                    "type": "text",
                    "text": user_query_content,
                },
                state["visual_contexts"]
            ]
        else:
            # Check if image already exists
            has_image = any(content.get("type") == "image" for content in user_query_content)
            if not has_image:
                user_query_content.append(state["visual_contexts"])
            else:
                logger.warning("Visual context already exists in the query.")
    
    # Update the query content
    logger.info(f"User query content:\r\n {user_query_content[0]}")
    query[-1].content = user_query_content
    
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
        "type": "image",
        "source_type": "base64",
        "data": base64_jpg,
        "mime_type": "image/jpeg",
    }
    return state


if __name__ == "__main__":
    sample_state = {"messages": [HumanMessage(content="What is 3653 + 111?")]}
    node_find_next_action(sample_state)
