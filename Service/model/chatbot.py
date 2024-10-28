from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatZhipuAI

from Service.config import *
from Service.api_key import *
from Service.common.http.response import Response

def chatbot(context, query: str = '', conversation_identifier: bool = False) -> Response:
    # Initialize the ChatZhipuAI model
    chat = ChatZhipuAI(
        model=chatbot_model,
        temperature=temprature,
    )
    if conversation_identifier == False:
        # Choose the appropriate template based on the context
        if context_related_to_session(context):
            prompt = ChatPromptTemplate.from_template(template=session_specific_prompt)
            formatted_prompt = prompt.format(context=context, input=query)
        else:
            prompt = ChatPromptTemplate.from_template(template=generic_non_session_prompt)
            formatted_prompt = prompt.format(context=context, input=query)
    else:
        prompt = ChatPromptTemplate.from_template(template=text_speaker_identification)
        formatted_prompt = prompt.format(context=context)
  


  
    # Get the response from the chatbot
    response = chat.invoke(formatted_prompt)
    
    return Response(response = response.content)

def context_related_to_session(context):  
    # Check if any of the keywords are present in the context
    if any(keyword in context for keyword in session_keywords):
        return True
    else:
        return False
