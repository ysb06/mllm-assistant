from typing import Annotated, Dict, List, TypedDict
import logging

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from .state import State
from .....scaner_udp import ScanerFilterServer
from .....webcam import capture_webcam_image

logger = logging.getLogger(__name__)

sensor_server = ScanerFilterServer()
sensor_server.activate()
logger.info("Sensor server activated")

gpt_oss = ChatOllama(model="gpt-oss:20b")
# GPU를 사용할 경우 Gemma3를 사용
# vision_encoder = ChatOllama(model="gemma3:4b")
vision_encoder = ChatOllama(model="llava:7b")


def node_fetch_vehicle_context(state: State):
    sensor_data = sensor_server.get_sensor_data()
    sensor_context = {
        "Steering Angle": str(sensor_data.get("steering", [])),
        "Speed": str(sensor_data.get("speed", [])),
    }

    return {"sensor_context": sensor_context}


def node_fetch_webcam_context(state: State):
    base64_jpg = capture_webcam_image().decode("utf-8")
    raw_image_context = {
        "type": "image_url",
        "image_url": f"data:image/jpeg;base64,{base64_jpg}",  # Data URI 형식 사용
    }
    return {"raw_image_context": raw_image_context}


def node_extract_image_context(state: State):
    raw_image_context = state.get("raw_image_context", None)
    prompt_text = f"다음 이미지는 운전 시뮬레이터에서 운전 중 차량 전면을 촬영한 사진입니다. 실제 운전상황이라고 생각하고 분석해 주세요. 이미지에서 보이는 도로 상황, 장애물, 교통 상황 등 운전 상황들을 자세히 설명해주세요."

    # 멀티모달 메시지 구성
    if raw_image_context:
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                raw_image_context,  # 이미 올바른 형식으로 되어 있음
            ]
        )
    else:
        message = HumanMessage(content=prompt_text)

    logger.info("Extracting visual context from image...")
    response = vision_encoder.invoke([message])
    visual_context = response.content if hasattr(response, "content") else str(response)
    logger.info(f"Visual context extracted")

    return {"visual_context": visual_context}


def node_run_chatbot(state: State):
    query: List[BaseMessage] = state["messages"]
    current_query: HumanMessage = state["messages"][-1]
    current_query_text: str = current_query.content

    if "sensor_context" in state:
        current_query_text += _convert_sensor_context(state["sensor_context"])

    if "visual_context" in state:
        current_query_text += _convert_visual_context(state["visual_context"])

    current_query = HumanMessage(
        content=[{
            "type": "text",
            "text": current_query_text,
        }],
    )

    extra_prompt = "답변은 한국어로 그리고 3문장 이내로 해주세요"
    system_msg = SystemMessage(content=extra_prompt)
    
    query[-1] = current_query
    query = [system_msg] + query  # SystemMessage를 맨 앞에 추가
    logger.info(f"Current query text:\r\n{current_query_text}")
    result = gpt_oss.invoke(query)
    logger.info(f"Chatbot responsed")

    return {"messages": [result]}

def _convert_sensor_context(sensor_context: Dict[str, str]) -> str:
    current_query_text = "-" * 10 + "\r\n"
    current_query_text += "Current User's Vehicle State:\r\n"
    for key, value in sensor_context.items():
        current_query_text += f"{key}: {value}\r\n"
    return current_query_text

def _convert_visual_context(visual_context: str) -> str:
    current_query_text = "\r\n" + "-" * 10 + "\r\n"
    current_query_text += f"Visual Context:\r\n{visual_context}\r\n"
    return current_query_text