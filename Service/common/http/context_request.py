from pydantic import BaseModel

class ContextRequest(BaseModel):
    command: bool