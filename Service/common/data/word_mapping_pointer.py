from pydantic import BaseModel

class WordMappingPointer(BaseModel):
    old_chunk_unamapped_pointer: int
    new_chunk_unmapped_pointer: int