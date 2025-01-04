from typing import Iterable, List, Literal, Optional, Union
from pydantic import BaseModel

# ---- Elements ----


class ImageData(BaseModel):
    url: str
    """Either a URL of the image or the base64 encoded image data."""
    detail: Optional[Literal["auto", "low", "high"]] = None


class AudioData(BaseModel):
    data: str
    """Base64 encoded audio data."""
    format: Literal["wav", "mp3"]


class AssistantAudio(BaseModel):
    id: str
    """Unique identifier for a previous audio response from the model."""


class Function(BaseModel):
    name: str
    arguments: str


# ---- Contents ----


class TextContent(BaseModel):
    text: str
    type: Literal["text"]


class ImageContent(BaseModel):
    image_url: ImageData
    type: Literal["image_url"]


class AudioContent(BaseModel):
    input_audio: AudioData
    type: Literal["input_audio"]


class RefusalContent(BaseModel):
    refusal: str
    type: Literal["refusal"]


UserContent = Union[TextContent, ImageContent, AudioContent]
AssistantContent = Union[TextContent, RefusalContent]

# ---- Messages ----


class ToolCallMessage(BaseModel):
    id: str
    function: Function
    type: Literal["function"]


class SystemMessage(BaseModel):
    content: Union[str, Iterable[TextContent]]
    role: Literal["system"]
    name: Optional[str] = None


class AssistantMessage(BaseModel):
    role: Literal["assistant"]
    audio: Optional[AssistantAudio] = None
    content: Optional[Union[str, Iterable[AssistantContent]]] = None
    function_call: Optional[Function] = None
    """Deprecated and replaced by `tool_calls`"""
    name: Optional[str] = None
    refusal: Optional[str] = None
    tool_calls: Optional[Iterable[ToolCallMessage]] = None


class UserMessage(BaseModel):
    role: Literal["user"]
    content: Union[str, Iterable[UserContent]]
    name: Optional[str] = None


class ChatRequest(BaseModel):
    messages: List[Union[UserMessage, AssistantMessage, SystemMessage, ToolCallMessage]]
