from pydantic import BaseModel, Field, model_validator, field_validator
from typing import List, Dict, Any, Optional, Self
import uuid
from nutrition.model import NutritionMacro, NutritionMicro, NutritionMineral, DietaryData, DietarySummary


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
    content: List[Content]

class ChatRequest(BaseModel):
    model: str
    user_id: str
    session_id: uuid.UUID
    app_id: Optional[str] = 'default'
    is_thought: bool = False
    user_meta: Dict[str, Any]
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
    
    
class UploadFileRequest(BaseModel):
    title: str
    filename: str
    app_id: Optional[str] = 'default'
    filetype: str
    type: str
    auth: List[str] = Field(default_factory=list)
    meta: Optional[Dict[str, Any]] = None


class ChatSessionRequest(BaseModel):
    user_id: str
    user_meta: Optional[dict] = None
    is_dynamic: Optional[bool] = False 


class ChatSessionResponse(BaseModel):
    user_id: str
    session_id: str
    
    
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
    
    @model_validator(mode='after')
    def check_dietary_length(self) -> Self:
        assert len(self.dietary) == self.days
        return self