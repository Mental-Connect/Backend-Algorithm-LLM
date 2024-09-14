import os
import sys

from Algorithm.common.response import Response
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatZhipuAI
from Service.config import *

# Set your ZHIPUAI API key

def chatbot(context, query) -> Response:
    # Initialize the ChatZhipuAI model
    chat = ChatZhipuAI(
        model=chatbot_model,
        temperature=temprature,
    )
    # Choose the appropriate template based on the context
    if context_related_to_session(context):
        prompt = ChatPromptTemplate.from_template(template=session_specific_prompt)
    else:
        prompt = ChatPromptTemplate.from_template(template=generic_non_session_prompt)

    # Format the prompt with context and query
    formatted_prompt = prompt.format(context=context, input=query)
    
    # Get the response from the chatbot
    response = chat.invoke(formatted_prompt)
    
    return Response(response = response.content)

def context_related_to_session(context):  
    # Check if any of the keywords are present in the context
    if any(keyword in context for keyword in session_keywords):
        return True
    else:
        return False
