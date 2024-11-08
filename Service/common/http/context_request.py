from pydantic import BaseModel

class ContextRequest(BaseModel):
    audio: bytes