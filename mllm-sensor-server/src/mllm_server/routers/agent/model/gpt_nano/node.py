from typing import Annotated, Dict, List, TypedDict, Optional
import logging

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from .state import State
from .....scaner_udp import ScanerFilterServer
from .....webcam import capture_webcam_image

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "답변은 한국어로 그리고 3문장 이내로 해주세요"

# 센서 서버를 모듈 레벨이 아닌 함수 내에서 초기화하도록 변경
_sensor_server: Optional[ScanerFilterServer] = None

def get_sensor_server() -> ScanerFilterServer:
    global _sensor_server
    if _sensor_server is None:
        _sensor_server = ScanerFilterServer()
        _sensor_server.activate()
        logger.info("Sensor server activated")
    return _sensor_server

gpt_nano = ChatOpenAI(model="gpt-5-nano")


def node_fetch_vehicle_context(state: State):
    sensor_server = get_sensor_server()
    sensor_data = sensor_server.get_sensor_data()
    sensor_context = {
        "Steering Angle": str(sensor_data.get("steering", [])),
        "Speed": str(sensor_data.get("speed", [])),
    }
    logger.info("Vehicle sensor context fetched successfully")
    return {"sensor_context": sensor_context}


def node_fetch_webcam_context(state: State):
    base64_jpg = capture_webcam_image().decode("utf-8")
    image_context = {
        "type": "image_url",
        "image_url": f"data:image/jpeg;base64,{base64_jpg}",  # Data URI 형식 사용
    }
    logger.info("Webcam image context fetched successfully")
    return {"image_context": image_context}
    


def node_run_chatbot(state: State):
    query: List[BaseMessage] = state["messages"]
    current_query: HumanMessage = state["messages"][-1]
    
    current_query_text: str = current_query.content + "\r\n"
    sensor_context = state.get("sensor_context")
    if sensor_context is not None:
        current_query_text += _convert_sensor_context(sensor_context)
    logger.info(f"Current query text:\r\n{current_query_text}")

    current_query_image = state.get("image_context", None)

    current_query_content = [
        {
            "type": "text",
            "text": current_query_text,
        }
    ]
    if current_query_image:
        current_query_content.append(current_query_image)

    current_query = HumanMessage(content=current_query_content)

    query[-1] = current_query
    # SystemMessage를 맨 앞에 추가
    query = [SystemMessage(content=SYSTEM_PROMPT)] + query
    
    result = gpt_nano.invoke(query)
    logger.info(f"Chatbot responsed")

    return {"messages": [result]}


def _convert_sensor_context(sensor_context: Dict[str, str]) -> str:
    current_query_text = "-" * 10 + "\r\n"
    current_query_text += "Current User's Vehicle State:\r\n"
    for key, value in sensor_context.items():
        current_query_text += f"{key}: {value}\r\n"
    return current_query_text
