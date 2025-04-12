from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, UTC


# now we define our pydantic models
class Metadata(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    
                            
class Message(BaseModel):
    user_id : str
    text: str
    metadata: Metadata | None = None
    tags: list[str] | None = None
    
class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata    