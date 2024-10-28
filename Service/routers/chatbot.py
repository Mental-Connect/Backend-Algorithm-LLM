import logging
from fastapi import APIRouter
from Service.common.http.request import Request
from Service.common.http.response import Response
from Service.common.data.transcription_context import transcription_context
from Service.model.chatbot import chatbot


router = APIRouter()

@router.post("/chatbot", response_model=Response)
async def chat_model(request: Request):
    full_transcription = transcription_context.transcription
    if not full_transcription:
        logging.warning("response: No transcription available. Please upload an audio file first.")
        return {"response": "No transcription available. Please upload an audio file first."}

    response_text = chatbot(query=request.prompt, context=full_transcription)
    return Response(response=response_text.response)
