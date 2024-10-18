import numpy as np

from funasr import AutoModel
from Service.config import model_sampling_rate
from funasr.utils.postprocess_utils import rich_transcription_postprocess


def text_generator(model: AutoModel, audio_sample):
    text = model.generate(
            input=audio_sample,
            cache={},
            language="auto",
            use_itn=True,
            batch_size_s=60,
            merge_vad=False
        )
    return text

def audio_file_splitting(model: AutoModel, audio_array: np.ndarray, sampling_rate: int = model_sampling_rate) -> str:
    """Splits audio into chunks and generates transcriptions."""
    transcriptions = []
    sample_length = int(30 * sampling_rate)
    
    for start in range(0, len(audio_array), sample_length):
        end = min(start + sample_length, len(audio_array))
        chunk = audio_array[start:end]
        generated_text = text_generator(model, chunk)
        text = rich_transcription_postprocess(generated_text[0]["text"])
        transcriptions.append(text)
    
    return " ".join(transcriptions)