from Service.common.http.request import Request
from Service.model.chatbot import chatbot

async def chatbot_service_logic(request: Request) ->str:
    try:
        response_text = chatbot(query=request.prompt, context=request.context, session_keywords = request.session_keywords, 
                                session_specific_prompt = request.session_specific_prompt,
                                  generic_non_session_prompt= request.generic_non_session_prompt )
        return response_text
    except:
        return "Error Uploading the transcription."
