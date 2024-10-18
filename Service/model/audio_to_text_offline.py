import librosa
import numpy as np
import nltk
import logging
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from Service.config import *
from Service.logging.logging import *
from Service.common.session_manager import *
from Service.common.audio_intensity_calculation import *
from Service.common.offline_audio_file_splitting import *
from Service.common.intensity_settings import IntensitySettings

def audio_to_text_model_offline(audio_file_path: str, model: AutoModel, segmentation_length = 1, intensity_threshold: float = 0.00) -> str:
    """Converts audio file to text using the provided model."""
    try:
        audio_array, sampling_rate = librosa.load(audio_file_path, sr=None)
        audio_array = librosa.resample(audio_array, orig_sr=sampling_rate, target_sr=model_sampling_rate)
         # Filter high-intensity segments
        high_intensity_segments = filter_high_intensity_segments(audio_array, segmentation_length, intensity_threshold)
        if high_intensity_segments:
            combined_audio = np.concatenate(high_intensity_segments)
        else:
            combined_audio = np.array([])
        
        if len(combined_audio) == 0:
                logging.warning("Combined audio is empty; no transcription will be performed.")
                return ""
        
        if len(combined_audio) > int(30 * sampling_rate):
            logging.info("Length exceeds model's maximum limit; splitting audio.")
            return audio_file_splitting(model, combined_audio)
        
        logging.info('Audio length is acceptable; processing full audio.')
        generated_text = text_generator(model, combined_audio)
        return rich_transcription_postprocess(generated_text[0]["text"])

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return ""
