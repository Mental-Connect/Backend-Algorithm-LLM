# import asyncio
# from fastapi import WebSocket
# import logging
# from asyncio import Queue
# from Service.model.audio_to_text_online import audio_to_text_model_online
# from Service.model.audio_to_text_offline import audio_to_text_model_offline
# from Service.common.temp_file_save_functions import *
# from Service.config import *
# from Service.common.data.audio_buffer import *
# from Service.common.data.audio_models import AudioModels
# from Service.common.audio_transcription_saver import audio_transcription_save
# from Service.common.data.websockets_managment import websocket_manager
# from Service.common.data.audio_receive_queue import audio_receive_queue
# from Service.common.data.pointers_position import PointerPosition
# from Service.common.data.transcribed_text_store import TranscribedTextStore
# from Service.common.audio_word_mapping import word_mapping
# from Service.common.data.buffer_length import BufferLength
# from Service.common.data.intensity_settings import IntensitySettings
# from Service.common.data.offline_transcription import OfflineTranscription


# # buffer_processing_queue = Queue()
# pointer_info = PointerPosition()
# transcribedtextstore = TranscribedTextStore()
# buffer_length = BufferLength()

# async def reset_everything():
#     """
#     Reset all relevant states and data structures to their initial values.

#     This function resets various components of the application, including:
#     - Pointer positions
#     - Transcribed text storage
#     - Buffer length indices
#     - Audio buffer instances

#     This is typically used to clear previous states and prepare for a new session or fresh input.
#     """
#     pointer_info.indexed_pointer_position = 0
#     pointer_info.total_pointer_position = 0
#     transcribedtextstore.old_message  = []
#     transcribedtextstore.new_message = []
#     transcribedtextstore.total_message = []
#     buffer_length.audio_chunk_start_index = 0
#     buffer_length.audio_chunk_end_index = 4
#     audio_buffer_instance.saved_audio_data = []
#     audio_buffer_instance.audio_for_context_store = bytearray()
#     audio_buffer_instance.audio_for_context_store = bytearray()


# async def process_audio_queue(websocket: WebSocket):
#     """
#     Continuously processes incoming audio data from the audio queue.

#     This function retrieves audio data from the audio queue, manages audio buffering,
#     and triggers transcription processes based on the length of the buffered audio data.
#     It filters audio segments based on predefined thresholds for segment length and processes them accordingly.

#     The function performs the following steps:
#     1. Extends the audio buffer with incoming audio data.
#     2. Saves incoming audio data to a temporary file for transcription.
#     3. If the audio buffer reaches specific thresholds, it prepares and processes segments for transcription.
#     4. Triggers processing of current audio buffers asynchronously.
#     """
#     user_queue = websocket_manager.get_user_queue(websocket)  # Get the queue for this WebSocket
#     audio_buffer_instance = websocket_manager.get_user_audio_buffer(websocket)  # Get the audio buffer for this WebSocket
#     while True:
#         data = await user_queue.get()
#         audio_buffer_instance.audio_for_context_store.extend(data)  # Add incoming data to the buffer

#         # audio_buffer_instance.transcription_correction_audio_store.extend(data)
#         audio_buffer_instance.saved_audio_data.append((data))
#         temp_file_path = save_temp_audio_file(data, online_streaming_path = online_streaming_files)


#         if temp_file_path:
#             asyncio.create_task(process_streaming_transcription(temp_file_path,AudioModels.streaming_model, websocket))
        
#         #when length of audio is greater than 8 second and less than 30 second
#         if buffer_length.minimum_stored_buffer_length<= len(audio_buffer_instance.saved_audio_data)< buffer_length.maximum_stored_buffer_length:
#             # Clear the audio stream so new one will come
#             audio_buffer_instance.transcription_correction_audio_store.clear()
#             # Start the index from 0 to end_correction_length
#             for chunk in audio_buffer_instance.saved_audio_data[buffer_length.audio_chunk_start_index:buffer_length.audio_chunk_end_index]:
#                 # Put the data in Byte array so it become one data stream
#                 audio_buffer_instance.transcription_correction_audio_store.extend(chunk)  
#             # Increase the end data length so new time data will come 
#             buffer_length.audio_chunk_end_index += 1 
#             current_buffer = audio_buffer_instance.transcription_correction_audio_store
#             print("Done Her Check 1:")
#             await audio_buffer_instance.buffer_processing_queue.put(current_buffer)
#             # Finally put in the buffer for process
#             await process_current_buffer_queue(current_buffer, websocket)
                    
#         # After 15 chunks below condition will be applicable
#         if len(audio_buffer_instance.saved_audio_data) >= buffer_length.maximum_stored_buffer_length:
#             audio_buffer_instance.transcription_correction_audio_store.clear()
#             for chunk in audio_buffer_instance.saved_audio_data[buffer_length.audio_chunk_start_index:buffer_length.audio_chunk_end_index]:  # Set the Minimun and Naximum chunks length, start from o to 15 
#                 # Making a long stream of audio byte for transcription
#                 audio_buffer_instance.transcription_correction_audio_store.extend(chunk)
#                 print("Done Her Check 2:")
#                 # Giving whole 15 Second of chunk as current Buffer and using it for transcription
#             print("Length of Audio Buffer: ",len(audio_buffer_instance.transcription_correction_audio_store)) 
#             # await audio_buffer_instance.buffer_processing_queue.put()
#             await process_current_buffer_queue(audio_buffer_instance.transcription_correction_audio_store, websocket)
#             print("Done Her Check 3:")
#             buffer_length.audio_chunk_start_index += 1
#             buffer_length.audio_chunk_end_index += 1

# async def process_current_buffer_queue(current_buffer, websocket):
#     """
#     Continuously processes the current audio buffer from the buffer processing queue.

#     This function retrieves the current audio buffer from the queue and processes it to check
#     for transcription readiness. It calls the function to check and process the buffers.

#     Returns:
#         None
#     """
#     while True: 
#         # current_buffer = await audio_buffer_instance.buffer_processing_queue.get()
#         print("Small Check Here: ", len(current_buffer))
#         print("Done Her Check 4:")
#         await check_and_process_buffers(current_buffer,websocket)
#         audio_buffer_instance.buffer_processing_queue.task_done()


# async def check_and_process_buffers(current_buffer, websocket):
#     """
#     Check and process the provided audio buffer for transcription.

#     This function saves the current buffer to a temporary file and triggers the transcription process.
    
#     Parameters:
#         current_buffer (bytes): The audio buffer to be processed.

#     Returns:
#         None
#     """
#     combined_temp_path = save_temp_audio_file(current_buffer, online_correction_path = online_correction_files)
#     print("Done Her Check 5:", combined_temp_path)
#     if combined_temp_path:
#         await corrected_transcription_online(combined_temp_path, AudioModels.non_streaming_model, websocket)


# async def corrected_transcription_online(temp_file_path: str,model, websocket):
#     """
#     Process the audio file for online transcription and manage the transcribed output.

#     This function handles the transcription of audio files, updates the stored messages,
#     and sends the transcribed results to clients.

#     Parameters:
#         temp_file_path (str): The path to the temporary audio file for transcription.
#         model: The model used for transcription.

#     Returns:
#         None
#     """
#     try:
#         message,_ = audio_to_text_model_offline(temp_file_path,model, intensity_threshold = IntensitySettings.intensity_value)
#         # This will check if the message is first message or not,
#         if len(audio_buffer_instance.saved_audio_data) <= buffer_length.maximum_stored_buffer_length:
#             # Put the first message in old_message and total message list for furture processing
#             transcribedtextstore.old_message = message.split()
#             transcribedtextstore.total_message = message.split()
#             print("Done Her Check 6:", message)

#             pointer_info.total_pointer_position = len(transcribedtextstore.old_message)
#             pointer_info.indexed_pointer_position = len(transcribedtextstore.old_message)
#             print("pointer_info.total_pointer_position", pointer_info.total_pointer_position)
#             await send_corrected_transcription_to_clients(transcribedtextstore.total_message,"final_Transcription",websocket ,pointer_info.indexed_pointer_position, pointer_info.total_pointer_position)
#             await send_corrected_transcription_to_clients(transcribedtextstore.total_message,"corrected_transcription",websocket,pointer_info.indexed_pointer_position, pointer_info.total_pointer_position)

#         else:
#             # Receive and make list of new message
#             transcribedtextstore.new_message = message.split()
#             pointer_info.indexed_pointer_position = pointer_info.total_pointer_position
#             mapped_pointer= await word_mapping(transcribedtextstore.old_message, transcribedtextstore.new_message)
#             old_chunk_unmapped_pointer, new_chunk_unmapped_pointer = mapped_pointer.old_chunk_unmapped_pointer, mapped_pointer.new_chunk_unmapped_pointer
#             old_chunk_mapped_pointer = len(transcribedtextstore.old_message[old_chunk_unmapped_pointer:])
#             transcribedtextstore.old_message = transcribedtextstore.new_message[new_chunk_unmapped_pointer:]
#             pointer_info.indexed_pointer_position = pointer_info.indexed_pointer_position - old_chunk_mapped_pointer
#             transcribedtextstore.total_message = transcribedtextstore.total_message[:pointer_info.indexed_pointer_position]  + transcribedtextstore.new_message[new_chunk_unmapped_pointer:]
#             print("indexng positrion", pointer_info.indexed_pointer_position + len(transcribedtextstore.new_message[new_chunk_unmapped_pointer:]))
#             print("Total Pointer Position",len(transcribedtextstore.total_message) )
#             print("Done Her Check 7:", message)
#             await send_corrected_transcription_to_clients(transcribedtextstore.new_message,"corrected_transcription",websocket ,pointer_info.indexed_pointer_position, pointer_info.total_pointer_position, new_chunk_unmapped_pointer, websocket)
#             await send_corrected_transcription_to_clients(transcribedtextstore.total_message,"final_Transcription",websocket ,pointer_info.indexed_pointer_position, pointer_info.total_pointer_position, websocket)
#             pointer_info.total_pointer_position = len(transcribedtextstore.total_message)
            
            
#     except Exception as e:
#         logging.error(f"Error processing audio: {e}")
        
#     finally:
#         await remove_temp_file(temp_file_path)



# async def process_streaming_transcription(temp_file_path: str,model, websocket: WebSocket):
#     """
#     Process audio for streaming transcription and send results to clients.

#     This function handles audio data for online transcription and sends
#     the resulting transcription to clients.

#     Parameters:
#         temp_file_path (str): The path to the temporary audio file for transcription.
#         model: The model used for transcription.

#     Returns:
#         None
#     """
#     try:
#         message = audio_to_text_model_online(temp_file_path,model)
#         message_list = message.streaming_response
#         message_list = message_list.split()
#         print('message_list', message_list)
#         await send_transcription_to_clients(message_list,"instant_transcription", websocket)
#     except Exception as e:
#         logging.error(f"Error processing audio: {e}")
#     finally:
#         await remove_temp_file(temp_file_path)

# async def process_transcription_offline()-> OfflineTranscription:
#     """
#     Process audio for offline transcription and return the result.

#     This function saves the buffered audio to a temporary file,
#     performs offline transcription, and organizes the transcribed results.

#     Returns:
#         OfflineTranscription: An object containing the transcribed message and identified subjects.

#     Raises:
#         Exception: If there is an error during audio processing or transcription.
#     """
#     try:
#         identified_subject = []
#         temp_file_path = save_temp_audio_file(audio_buffer_instance.audio_for_context_store, save_to_path=audio_transcription_files)
#         logging.info(f"Temporary Path Created: {temp_file_path}")
#         message,generated_result = audio_to_text_model_offline(temp_file_path, AudioModels.full_transcription_model)
        
#         for mess in generated_result:
#             for info in mess['sentence_info']:
#                 identified_subject.append(f'Speaker {info['spk']}: {info['text']}')
#                 logging.info(f"Audio And Trascibed Info Saved!!! ")
#         return OfflineTranscription(message = message, subject_conversation = identified_subject)
#     except Exception as e:
#         logging.error(f"Error processing audio: {e}")

