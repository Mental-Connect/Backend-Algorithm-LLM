from fastapi import APIRouter
from Service.common.http.chatbot_request import ChatbotRequest
from Service.common.http.chatbot_response import ChatbotResponse
from Service.services.chatbot_service import chatbot_service_logic

router = APIRouter()

@router.post("/chatbot", response_model=ChatbotResponse)
async def chat_model(request: ChatbotRequest):
    try:

        print("chatbot service was called!")
        answer = await chatbot_service_logic(request)
        return ChatbotResponse(response=answer)
    except:
        return ChatbotResponse(response="Error in chatbot api")
