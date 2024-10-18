from pydantic import BaseModel



class IntensitySetting(BaseModel):
    intensity_value: float = 0.0