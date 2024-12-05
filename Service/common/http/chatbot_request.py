from pydantic import BaseModel

# Define a Pydantic model to validate and serialize input data for chatbot requests
class ChatbotRequest(BaseModel):
    # The user's query to be processed by the chatbot
    query: str
    
    # The context or background information to assist the chatbot in understanding the query
    context: str
    
    # A prompt or instruction that guides the chatbot's response
    prompt: str


    # "query": "xxxx?",
    # "context": "xxxx",
    # "prompt": "当前上下文描述了一个情境：\n<Context>\n{context}\n<Context>\n这是一个通用的聊天对话。请以第一人称的口吻直接回答以下问题。请确保回答直接、准确地针对问题本身，不要添加额外的背景信息或建议。如果问题与上下文无关，请直接说明我们没有讨论过这个话题，并提供一个简洁的通用回答，而不是额外的信息。\n问题：{input}\n",