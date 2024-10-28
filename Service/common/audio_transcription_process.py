import asyncio
from asyncio import Queue
from Service.model.audio_to_text_online import audio_to_text_model_online
from Service.model.audio_to_text_offline import audio_to_text_model_offline
from Service.common.temp_file_save_functions import *
from Service.config import *
from Service.common.data.audio_buffer import *
from Service.common.data.audio_models import AudioModels
from Service.common.audio_transcription_save import audio_transcription_save
from Service.common.audio_receive_queue import audio_receive_queue
from Service.common.data.pointers_position import PointerPosition
from Service.common.data.transcribed_text_store import TranscribedTextStore
from Service.common.audio_word_mapping import word_mapping
from Service.common.data.buffer_length import BufferLength
from Service.common.data.intensity_settings import IntensitySettings
from Service.common.data.offline_transcription import OfflineTranscription


buffer_processing_queue = Queue()
pointer_info = PointerPosition()
transcribedtextstore = TranscribedTextStore()
buffer_length = BufferLength()

async def reset_everything():
    pointer_info.indexed_pointer_position = 0
    pointer_info.total_pointer_position = 0
    transcribedtextstore.old_messsage  = []
    transcribedtextstore.new_message = []
    transcribedtextstore.total_message = []
    buffer_length.audio_chunk_start_index = 0
    buffer_length.audio_chunk_end_index = 4
    audio_buffer_instance.saved_audio_data = []
    audio_buffer_instance.audio_for_context_store = bytearray()
    audio_buffer_instance.audio_for_context_store = bytearray()


async def process_audio_queue():
    while True:
        data = await audio_receive_queue.audio_queue.get()
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
            await buffer_processing_queue.put(current_buffer)
            # Finally put in the buffer for process
            asyncio.create_task(process_current_buffer_queue())
                    
        # After 15 chunks below condition will be applicable
        if len(audio_buffer_instance.saved_audio_data) >= buffer_length.maximum_stored_buffer_length:
            audio_buffer_instance.transcription_correction_audio_store.clear()
            for chunk in audio_buffer_instance.saved_audio_data[buffer_length.audio_chunk_start_index:buffer_length.audio_chunk_end_index]:  # Set the Minimun and Naximum chunks length, start from o to 15 
                # Making a long stream of audio byte for transcription
                audio_buffer_instance.transcription_correction_audio_store.extend(chunk)  
                # Giving whole 15 Second of chunk as current Buffer and using it for transcription
            # asyncio.create_task(check_and_process_buffers(audio_buffer_instance.transcription_correction_audio_store))
            await buffer_processing_queue.put(audio_buffer_instance.transcription_correction_audio_store)
            asyncio.create_task(process_current_buffer_queue())
            # await check_and_process_buffers(audio_buffer_instance.transcription_correction_audio_store)
            buffer_length.audio_chunk_start_index += 1
            buffer_length.audio_chunk_end_index += 1

async def process_current_buffer_queue():
    while True:
        current_buffer = await buffer_processing_queue.get()
        await check_and_process_buffers(current_buffer)
        buffer_processing_queue.task_done()


async def check_and_process_buffers(current_buffer):
        combined_temp_path = save_temp_audio_file(current_buffer)
        if combined_temp_path:
            await corrected_transcription_online(combined_temp_path, AudioModels.non_streaming_model)


async def corrected_transcription_online(temp_file_path: str,model):
    try:
        message,_ = audio_to_text_model_offline(temp_file_path,model, intensity_threshold = IntensitySettings.intensity_value)
        print("Checking message", message)
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
            mapped_pointer= await word_mapping(transcribedtextstore.old_messsage, transcribedtextstore.new_message)
            old_chunk_unmapped_pointer, new_chunk_unmapped_pointer = mapped_pointer.old_chunk_unamapped_pointer, mapped_pointer.new_chunk_unmapped_pointer
            old_chunk_mapped_pointer = len(transcribedtextstore.old_messsage[old_chunk_unmapped_pointer:])
            transcribedtextstore.old_messsage = transcribedtextstore.new_message[new_chunk_unmapped_pointer:]
            pointer_info.indexed_pointer_position = pointer_info.indexed_pointer_position - old_chunk_mapped_pointer
            transcribedtextstore.total_message = transcribedtextstore.total_message[:pointer_info.indexed_pointer_position]  + transcribedtextstore.new_message[new_chunk_unmapped_pointer:]

            print("Total Message Final: ", transcribedtextstore.total_message)
            # await send_corrected_transcription_to_clients(transcribedtextstore.new_message[new_chunk_unmapped_pointer:],"New Transcription", pointer_info.indexed_pointer_position, pointer_info.total_pointer_position)
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
        await send_transcription_to_clients(message.streaming_response,"Instant Transcription")
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
    finally:
        await remove_temp_file(temp_file_path)

async def process_transcription_offline()-> OfflineTranscription:
    try:
        identified_subject = []
        temp_file_path = save_temp_audio_file(audio_buffer_instance.audio_for_context_store, save_to_path=audio_transcription_files)
        logging.info(f"Temporary Path Created: {temp_file_path}")
        message,generated_result = audio_to_text_model_offline(temp_file_path, AudioModels.full_transcription_model)
        
        for mess in generated_result:
            for info in mess['sentence_info']:
                identified_subject.append(f'Speaker {info['spk']}: {info['text']}')
                logging.info(f"Audio And Trascibed Info Saved!!! ")
        return OfflineTranscription(message = message, subject_conversation = identified_subject)
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
