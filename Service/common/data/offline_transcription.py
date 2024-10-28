from pydantic import BaseModel
from typing import List

class OfflineTranscription(BaseModel):
    message: str
    subject_conversation: List[str]