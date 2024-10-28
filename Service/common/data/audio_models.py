from pydantic import BaseModel
from typing import Optional

class AudioModels(BaseModel):
    non_streaming_model: Optional[None] = None
    streaming_model: Optional[None] = None
    full_transcription_model: Optional[None] = None
