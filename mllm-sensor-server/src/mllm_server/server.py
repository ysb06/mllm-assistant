import logging
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.chatbot import chatbot_router


load_dotenv()

logger = logging.getLogger(__name__)
fastapi_app = FastAPI()
fastapi_app.include_router(chatbot_router)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 혹은 특정 도메인만 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# llm_gpt4omini = ChatOpenAI(model="gpt-4o-mini")


@fastapi_app.get("/")
def read_root() -> Dict[str, str]:
    return {"State": "OK"}
