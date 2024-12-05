from pydantic import BaseModel

# Define a Pydantic model to validate and serialize input data for chatbot requests
class ChatbotRequest(BaseModel):    
    # The context or background information to assist the chatbot in understanding the query
    context: str
    
    # A prompt or instruction that guides the chatbot's response
    prompt: str

    # The user's query to be processed by the chatbot
    query: str
