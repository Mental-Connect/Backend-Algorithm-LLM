from Service.model.audio_to_text_online import audio_to_text_model_online
from Service.model.audio_to_text_offline import audio_to_text_model_offline
from Service.common.temp_file_save_functions import *
from Service.config import *
from Service.common.audio_buffer import*
from Service.common.audio_models import AudioModels
from Service.common.audio_transcription_save import audio_transcription_save
from Service.common.session_manager import *
from Service.common.pointers_position import PointerPosition
from Service.common.transcribed_text_store import TranscribedTextStore
from Service.common.audio_word_mapping import word_mapping
from Service.common.buffer_length import BufferLength
from Service.common.intensity_settings import IntensitySettings


# Initializing instances
pointer_info = PointerPosition()
transcribedtextstore = TranscribedTextStore()
buffer_length = BufferLength()

async def process_audio_queue():
    while True:
        data = await session_manager.audio_queue.get()
        audio_buffer_instance.audio_for_context_store.extend(data)  # Add incoming data to the buffer

        # audio_buffer_instance.transcription_correction_audio_store.extend(data)
        audio_buffer_instance.saved_audio_data.append((data))
        temp_file_path = save_temp_audio_file(data)

        if temp_file_path:
            asyncio.create_task(process_streaming_transcription(temp_file_path,AudioModels.streaming_model))
        
        #when length of audio is greater than 8 second and less than 30 second
        if buffer_length.minimum_stored_buffer_length<= len(audio_buffer_instance.saved_audio_data)< buffer_length.maximum_stored_buffer_length:
            # Clear the audio stream so new one will come
            audio_buffer_instance.transcription_correction_audio_store.clear()
            # Start the index from 0 to end_correction_length
            for chunk in audio_buffer_instance.saved_audio_data[buffer_length.audio_chunk_start_index:buffer_length.audio_chunk_end_index]:
                # Put the data in Byte array so it become one data stream
                audio_buffer_instance.transcription_correction_audio_store.extend(chunk)  
            # Increase the end data length so new time data will come 
            buffer_length.audio_chunk_end_index += 1 
            current_buffer = audio_buffer_instance.transcription_correction_audio_store
            # Finally put in the buffer for process
            asyncio.create_task(check_and_process_buffers(current_buffer))
                    
        # After 15 chunks below condition will be applicable
        if len(audio_buffer_instance.saved_audio_data) >= buffer_length.maximum_stored_buffer_length:
            audio_buffer_instance.transcription_correction_audio_store.clear()
            for chunk in audio_buffer_instance.saved_audio_data[buffer_length.audio_chunk_start_index:buffer_length.audio_chunk_end_index]:  # Set the Minimun and Naximum chunks length, start from o to 15 
                # Making a long stream of audio byte for transcription
                audio_buffer_instance.transcription_correction_audio_store.extend(chunk)  
                # Giving whole 15 Second of chunk as current Buffer and using it for transcription
            asyncio.create_task(check_and_process_buffers(audio_buffer_instance.transcription_correction_audio_store))
            buffer_length.audio_chunk_start_index += 1
            buffer_length.audio_chunk_end_index += 1

async def check_and_process_buffers(current_buffer):
        combined_temp_path = save_temp_audio_file(current_buffer)
        if combined_temp_path:
            await corrected_transcription_online(combined_temp_path, AudioModels.non_streaming_model)


async def corrected_transcription_online(temp_file_path: str,model):
    try:
        message = audio_to_text_model_offline(temp_file_path,model, intensity_threshold = IntensitySettings.intensity_value)
        # This will check if the message is first message or not,
        if len(audio_buffer_instance.saved_audio_data) <= buffer_length.maximum_stored_buffer_length:
            # Put the first message in old_message and total message list for furture processing
            transcribedtextstore.old_messsage = message.split()
            transcribedtextstore.total_message = message.split()
            print("Old Total Sentence: ", transcribedtextstore.total_message)

            pointer_info.total_pointer_position = len(transcribedtextstore.old_messsage)
            print("pointer_info.total_pointer_position", pointer_info.total_pointer_position)
            await send_corrected_transcription_to_clients(transcribedtextstore.total_message,"Final Transcription", final_sentence_pointer_position = pointer_info.total_pointer_position)
        else:
            # Receive and make list of new message
            transcribedtextstore.new_message = message.split()
            pointer_info.indexed_pointer_position = pointer_info.total_pointer_position
            old_chunk_unmapped_pointer, new_chunk_unmapped_pointer = await word_mapping(transcribedtextstore.old_messsage, transcribedtextstore.new_message)
            old_chunk_mapped_pointer = len(transcribedtextstore.old_messsage[old_chunk_unmapped_pointer:])
            transcribedtextstore.old_messsage = transcribedtextstore.new_message[new_chunk_unmapped_pointer:]
            pointer_info.indexed_pointer_position = pointer_info.indexed_pointer_position - old_chunk_mapped_pointer
            transcribedtextstore.total_message = transcribedtextstore.total_message[:pointer_info.indexed_pointer_position]  + transcribedtextstore.new_message[new_chunk_unmapped_pointer:]

            print("Total Message Final: ", transcribedtextstore.total_message)
            await send_corrected_transcription_to_clients(transcribedtextstore.total_message,"Final Transcription", pointer_info.indexed_pointer_position, pointer_info.total_pointer_position)
            pointer_info.total_pointer_position = len(transcribedtextstore.total_message)
            print("pointer_info.total_pointer_position: ", pointer_info.total_pointer_position)
            
            
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        
    finally:
        await remove_temp_file(temp_file_path)



async def process_streaming_transcription(temp_file_path: str,model):
    try:
        message = audio_to_text_model_online(temp_file_path,model)
        await send_transcription_to_clients(message,"Instant Transcription")
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
    finally:
        await remove_temp_file(temp_file_path)

async def process_transcription_offline(model):
    try:
        temp_file_path = save_temp_audio_file(audio_buffer_instance.audio_for_context_store, save_to_path=audio_transcription_files)
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
