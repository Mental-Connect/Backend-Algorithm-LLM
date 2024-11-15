from pydantic import BaseModel

class ContextRequest(BaseModel):
    audio_file: str