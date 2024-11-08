from Service.common.http.request import Request
from Service.common.data.transcription_context import transcription_context
from Service.model.chatbot import chatbot

async def chatbot_service_logic(request: Request) ->str:
    if transcription_context.transcription:
        response_text = chatbot(query=request.prompt, context=request.context)
        return response_text.response
    else:
        return "No transcription available. Please upload an audio file first."
