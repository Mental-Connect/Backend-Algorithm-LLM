from pydantic import BaseModel

class TranscriptionContext(BaseModel):
    transcription: str = ''

transcription_context = TranscriptionContext()