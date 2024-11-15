import librosa
import logging
import numpy as np
from pydub import AudioSegment
import scipy.signal
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from Service.common.audio_intensity_calculator import filter_high_intensity_segments
from Service.common.offline_audio_file_splitting import audio_file_splitting, text_generator
from Service.config import *
from Service.logging.logging import *


def audio_to_text_model_offline(audio_file_path: str, model: AutoModel, segmentation_length = 1, intensity_threshold: float = 0.00,intensity_active = True):
    """Converts audio file to text using the provided model."""
    try:    
        logging.info("Trying Librosa")
        audio_array, sampling_rate = librosa.load(audio_file_path, sr=None)
        logging.info("Audio Loaded")
        audio_array = librosa.resample(audio_array, orig_sr=sampling_rate, target_sr=model_sampling_rate)
        # Filter high-intensity segments
        if intensity_active:
            high_intensity_segments = filter_high_intensity_segments(audio_array, segmentation_length, intensity_threshold)
            if high_intensity_segments:
                combined_audio = np.concatenate(high_intensity_segments)
            else:
                combined_audio = np.array([])
            
            if len(combined_audio) == 0:
                    logging.warning("Combined audio is empty; no transcription will be performed.")
                    return ""
            else:
                generated_text = text_generator(model, combined_audio)
                return rich_transcription_postprocess(generated_text[0]["text"]), generated_text
        else:
            logging.info('Audio length is acceptable; processing full audio.')
            generated_text = text_generator(model, audio_array)
            return rich_transcription_postprocess(generated_text[0]["text"]), generated_text
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return ""
