import librosa
import warnings

from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from Service.config import *

def audio_to_text_model(audio_file_path, model_name='paraformer-zh'):
    # Suppress specific warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="librosa")
    warnings.filterwarnings("ignore", category=FutureWarning, module="torch")
    warnings.filterwarnings("ignore", category=FutureWarning, module="funasr")

    try:
        # Initialize the model with disable_update set to True
        model = AutoModel(
            model=audio_text_model,
            kwargs=kwargs
        )

        # Load and process the audio file
        audio_array, sampling_rate = librosa.load(audio_file_path, sr=None)
        audio_array = librosa.resample(audio_array, orig_sr=sampling_rate, target_sr=model_sampling_rate)

        # Generate the transcription
        res = model.generate(
            input=audio_array,
            cache={},
            language="auto",
            use_itn=True,
            batch_size_s=60,
            merge_vad=False
        )

        # Post-process the transcription
        text = rich_transcription_postprocess(res[0]["text"])

        # Return the transcription
        return text

    except Exception as e:
        print(f"An error occurred: {e}")
        return " "