from pydantic import BaseModel

class StreamingModelFrequency(BaseModel):
    low_freq: int = 350
    high_freq: int = 3500