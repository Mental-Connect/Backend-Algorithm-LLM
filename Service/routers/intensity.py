from fastapi import APIRouter
from Service.common.http.intensity_setting import IntensitySetting
from Service.common.data.intensity_settings import IntensitySettings

router = APIRouter()

@router.post("/intensity-settings")
async def set_frequency(settings: IntensitySetting):
     IntensitySettings.intensity_value = settings.intensity_value