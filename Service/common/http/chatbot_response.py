from pydantic import BaseModel

# Define a Pydantic model to structure and validate the response data from the chatbot
class ChatbotResponse(BaseModel):

    # The chatbot's response to the user's query
    response: str
