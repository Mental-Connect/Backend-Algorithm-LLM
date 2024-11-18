from Service.common.http.request import Request
from Service.model.chatbot import chatbot

async def chatbot_service_logic(request: Request) ->str:
    try:
        response_text = chatbot(query=request.prompt, context=request.context)
        return response_text
    except:
        return "Error Uploading the transcription."
