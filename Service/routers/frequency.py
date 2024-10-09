from fastapi import APIRouter
from Service.common.http.frequency_setting import FrequencySettings
from Service.common.streaming_model_frequency import StreamingModelFrequency
import logging

router = APIRouter()

@router.post("/frequency-settings")
async def set_frequency(settings: FrequencySettings):
    
    StreamingModelFrequency.low_freq = settings.low_frequency
    StreamingModelFrequency.high_freq = settings.high_frequency
    logging.info(f"Low Freq Range: {settings.low_frequency}, High Freq Range: {settings.high_frequency} ")

