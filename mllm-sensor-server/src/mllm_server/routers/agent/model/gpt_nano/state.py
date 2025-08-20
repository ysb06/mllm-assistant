from typing import Annotated, Dict, List, Optional

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

def merge_contexts(current: Dict[str, str], new: Dict[str, str]) -> Dict[str, str]:
    if current is None:
        return new
    merged = current.copy()
    merged.update(new)
    return merged


class State(TypedDict):
    messages: Annotated[List, add_messages]
    image_context: Optional[Dict[str, str]]
    sensor_context: Optional[Dict[str, str]]