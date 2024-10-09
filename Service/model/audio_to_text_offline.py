import librosa
import numpy as np
import nltk
import logging
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from Service.config import model_sampling_rate
from Service.logging.logging import *

def audio_file_splitting(model: AutoModel, audio_array: np.ndarray, sampling_rate: int = model_sampling_rate) -> str:
    """Splits audio into chunks and generates transcriptions."""
    transcriptions = []
    sample_length = int(30 * sampling_rate)
    
    for start in range(0, len(audio_array), sample_length):
        end = min(start + sample_length, len(audio_array))
        chunk = audio_array[start:end]
        
        res = model.generate(
            input=chunk,
            cache={},
            language="auto",
            use_itn=True,
            batch_size_s=60,
            merge_vad=False
        )
        text = rich_transcription_postprocess(res[0]["text"])
        transcriptions.append(text)
    
    return " ".join(transcriptions)

def audio_to_text_model_offline(audio_file_path: str, model: AutoModel) -> str:
    """Converts audio file to text using the provided model."""
    try:
        audio_array, sampling_rate = librosa.load(audio_file_path, sr=None)
        audio_array = librosa.resample(audio_array, orig_sr=sampling_rate, target_sr=model_sampling_rate)

        if len(audio_array) > int(30 * sampling_rate):
            logging.info("Length exceeds model's maximum limit; splitting audio.")
            return audio_file_splitting(model, audio_array)
        
        logging.info('Audio length is acceptable; processing full audio.')
        res = model.generate(
            input=audio_array,
            cache={},
            language="auto",
            use_itn=True,
            batch_size_s=60,
            merge_vad=False
        )
        return rich_transcription_postprocess(res[0]["text"])

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return ""
