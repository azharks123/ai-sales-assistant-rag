from pydantic import BaseModel, Field

class ChatPayload(BaseModel):
    user_id: str = Field(..., description="Unique user session identifier")
    message: str = Field(..., description="Message text sent by the user")

class ChatResponse(BaseModel):
    user_id: str
    message: str
