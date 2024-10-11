import logging
from Service.common.session_manager import *


def handle_disconnection(websocket: WebSocket):
    session_manager.active_websockets.remove(websocket)
    full_transcription = " ".join(session_manager.transcriptions)
    session_manager.transcription_storage["transcription"] = full_transcription
    student_id = session_manager.student_id_info
    session_manager.database_data_saved[student_id]['Transcribed_Data'] = full_transcription
    logging.info(f"Client disconnected, full transcription: {full_transcription}")