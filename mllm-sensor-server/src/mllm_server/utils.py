import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)

def convert_serializable(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return {k: convert_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [convert_serializable(v) for v in obj]
    elif (
        isinstance(obj, str)
        or isinstance(obj, int)
        or isinstance(obj, float)
        or obj is None
    ):
        return obj
    else:
        logger.warning(f"Serialization Failed: {obj}")
        return "(Object)"