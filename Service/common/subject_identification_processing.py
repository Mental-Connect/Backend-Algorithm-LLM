from Service.model.chatbot import chatbot
from Service.common.data.transcription_context import transcription_context

async def subject_identification_processing() ->str:
    context = transcription_context.transcription
    response_text = chatbot(context, conversation_identifier = True)
    return response_text.response