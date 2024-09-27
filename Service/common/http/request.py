from pydantic import BaseModel

class Request(BaseModel):
    prompt: str
