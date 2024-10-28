from pydantic import BaseModel
from typing import List

class TranscribedTextStore(BaseModel):
    old_messsage: List[str] = []
    new_message: List[str] = []
    total_message: List[str] = []
