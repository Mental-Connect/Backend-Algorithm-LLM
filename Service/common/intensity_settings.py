from pydantic import BaseModel

class IntensitySettings(BaseModel):
    intensity_value:float = 0