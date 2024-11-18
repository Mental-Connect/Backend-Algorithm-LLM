from pydantic import BaseModel
from typing import List

class Request(BaseModel):
    prompt: str
    context:str
    session_keywords: List[str]
    session_specific_prompt: str
    generic_non_session_prompt: str
