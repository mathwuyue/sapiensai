import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Self, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from nutrition.model import (
    DietaryData,
    DietarySummary,
    NutritionMacro,
    NutritionMicro,
    NutritionMineral,
)


class StandardResponse(BaseModel):
    status: int
    resp: Dict[str, Any]


class UploadFileResponse(BaseModel):
    status: int
    doc_id: str


class FileStatusResponse(BaseModel):
    status: int
    resp: Dict[str, Any]


class ImageUrl(BaseModel):
    url: str


class Content(BaseModel):
    type: str
    text: str = None
    image_url: ImageUrl = None


class Message(BaseModel):
    role: str
    content: Union[str, List[Content]]


class ChatRequest(BaseModel):
    model: str
    user_id: str
    session_id: uuid.UUID
    app_key: str = Field(..., description="App jwt key")
    is_thought: bool = False
    user_meta: Optional[Dict[str, Any]] = None
    messages: List[Message]
    temperature: float = 0.1
    stream: bool = True
    max_tokens: int = 300


class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    system_fingerprint: str
    choices: List[Dict[str, Any]]


class ChatMissionRequest(BaseModel):
    user_id: str
    mission_jwt: str
    created_at: datetime = Field(default_factory=datetime.now)


class UploadFileRequest(BaseModel):
    title: str
    filename: str
    app_id: Optional[str] = "default"
    filetype: str
    type: str
    auth: List[str] = Field(default_factory=list)
    meta: Optional[Dict[str, Any]] = None


class ChatSessionRequest(BaseModel):
    user_id: str
    user_meta: Optional[dict] = None
    is_dynamic: Optional[bool] = True

    @field_validator("user_id", mode="before")
    @classmethod
    def convert_user_id_to_str(cls, v):
        return str(v)


class ChatSessionResponse(BaseModel):
    user_id: str
    session_id: str


class ChatHistoryRequest(BaseModel):
    user_id: str
    session_id: str
    app_key: str
    date: Optional[str] = None
    offset: Optional[int] = None
    keyword: Optional[str] = None
    page: Optional[int] = 0
    limit: Optional[int] = 0


class ProductRequest(BaseModel):
    pid: int
    name: str
    brief: str
    description: str
    price: float
    meta: Dict[str, Any]


class RefResponseChunk(BaseModel):
    index: int
    title: str
    filepath: str
    text: str
    page: int
    start: int
    end: int


class NutritionResponse(BaseModel):
    macro: NutritionMacro
    micro: NutritionMicro
    mineral: NutritionMineral


class DietaryResponse(BaseModel):
    emma: DietarySummary
    days: int
    dietary: List[DietaryData] = Field(...)
    refs: List[Dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_dietary_length(self) -> Self:
        assert len(self.dietary) == self.days
        return self


class ExerciseDataRequest(BaseModel):
    user_id: str
    exercise: str
    duration: float
    weight: Optional[float] = 55
    intensity: Optional[str] = "normal"
    bpm: Optional[float] = 0.0
    remark: Optional[str] = None
    start_time: Optional[datetime] = None
