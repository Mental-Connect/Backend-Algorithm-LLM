from Service.model.audio_to_text_online import audio_to_text_model_online
from Service.model.audio_to_text_offline import audio_to_text_model_offline
from Service.common.temp_file_save_functions import *
from Service.config import *
from Service.common.session_manager import *
from Service.common.audio_buffer import*
from Service.common.audio_models import AudioModels
from Service.common.audio_transcription_save import audio_transcription_save

async def process_audio_queue():
    while True:
        data = await session_manager.audio_queue.get()
        audio_buffer_instance.audio_buffer_store.extend(data)  # Add incoming data to the buffer
        temp_file_path = save_temp_audio_file(data)
        if temp_file_path:
            await process_transcription_online(temp_file_path,AudioModels.streaming_model)


async def process_transcription_online(temp_file_path: str,model):
    try:
        message = audio_to_text_model_online(temp_file_path,model)
        await send_transcription_to_clients(message)
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
    finally:
        await remove_temp_file(temp_file_path)

async def process_transcription_offline(model):
    try:
        temp_file_path = save_temp_audio_file(audio_buffer_instance.audio_buffer_store, save_to_path=audio_transcription_files)
        logging.info(f"Temporary Path Created: {temp_file_path}")

        message = audio_to_text_model_offline(temp_file_path, model)
        session_manager.transcriptions.append(message)
        full_transcription = " ".join(session_manager.transcriptions)
        session_manager.transcription_storage["transcription"] = full_transcription
        logging.info(f"Final Offline Transcription: {full_transcription}")

        audio_transcription_save(temp_file_path,full_transcription,audio_transcription_files)
        logging.info(f"Audio And Trascibed Info Saved!!! ")

    except Exception as e:
        logging.error(f"Error processing audio: {e}")