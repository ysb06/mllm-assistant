import logging
from contextlib import asynccontextmanager
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.agent import agent_router
from .routers.agent.node import sensor_server
from .webcam import cap

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    cap.release()
    sensor_server.deactivate()
    logger.info("Webcam and sensor server resources released")


load_dotenv()

fastapi_app = FastAPI(lifespan=lifespan)
fastapi_app.include_router(agent_router)

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


@fastapi_app.get("/")
def read_root() -> Dict[str, str]:
    return {"State": "OK"}
