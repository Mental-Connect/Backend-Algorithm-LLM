from Service.common.http.chatbot_request import ChatbotRequest
from Service.model.chatbot import chatbot

async def chatbot_service_logic(request: ChatbotRequest) ->str:
    try:
        response_text = chatbot(context=request.context, prompt = request.prompt, query=request.query)
        return response_text
    except:
        return "Error Uploading the transcription."
