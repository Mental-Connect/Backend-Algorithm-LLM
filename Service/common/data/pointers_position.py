from pydantic import BaseModel

class PointerPosition(BaseModel):
    total_pointer_position: int = 0
    indexed_pointer_position: int = 0
