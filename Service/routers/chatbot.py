from fastapi import APIRouter
from Service.common.http.request import Request
from Service.common.http.response import Response

# from Algorithm.question_answering_llm.service.chat_bot import chatbot
from Service.model.chatbot import chatbot

from Service.common.session_manager import session_manager
import logging

router = APIRouter()

@router.post("/chatbot", response_model=Response)
async def chat_model(request: Request):
    full_transcription = session_manager.transcription_storage["transcription"]
    student_id = session_manager.student_id_info
    if not full_transcription:
        logging.warning("response: No transcription available. Please upload an audio file first.")
        return {"response": "No transcription available. Please upload an audio file first."}

    response_text = chatbot(query=request.prompt, context=full_transcription)

    if student_id:
        if 'question_answers' not in session_manager.database_data_saved[student_id]:
            session_manager.database_data_saved[student_id]['question_answers'] = []
        session_manager.database_data_saved[student_id]['question_answers'].append({
            "prompt": request.prompt,
            "answer": response_text.response
        })
    else:
        logging.warning("Student ID is not initialized")

    logging.info(f"Database after chat: {session_manager.database_data_saved}")
    return Response(response=response_text.response)
