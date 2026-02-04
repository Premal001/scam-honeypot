from pydantic import BaseModel, Field
from typing import List, Optional

# --- Section 6: API Request Format ---

class MessageData(BaseModel):
    sender: str
    text: str
    timestamp: int

class MetaData(BaseModel):
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"

class IncomingRequest(BaseModel):
    sessionId: str
    message: MessageData
    conversationHistory: List[MessageData] = []
    metadata: Optional[MetaData] = None

# --- Section 8: API Response Format ---

class APIResponse(BaseModel):
    status: str
    reply: str