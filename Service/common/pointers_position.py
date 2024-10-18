from pydantic import BaseModel


class PointerPosition(BaseModel):
    total_pointer_position: int = 0
    indexed_pointer_position: int = 0

class BufferLength(BaseModel):
    minimum_stored_buffer_length: int = 4
    maximum_stored_buffer_length: int = 15
    audio_chunk_start_index: int = 0
    audio_chunk_end_index: int = 4