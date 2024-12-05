import httpx
import asyncio
from pydantic import BaseModel

# Define a Pydantic model to validate and serialize input data for chatbot requests
class ChatbotRequest(BaseModel):
    # The context or background information to assist the chatbot in understanding the query
    context: str
    
    # A prompt or instruction that guides the chatbot's response
    prompt: str

    # The user's query to be processed by the chatbot
    query: str
    

# 定义输出数据结构 (ChatbotResponse)
class ChatbotResponse(BaseModel):
    response: str

# 构造请求数据
def create_chatbot_request():
    # 示例心理咨询对话
    query = "请给出具体的摘要"
    context = "学生：老师，我最近感觉特别焦虑，每天都很紧张，心情一直很低落，尤其是考试快到了，我总是担心自己做不好。心理咨询师：我理解你的感受，考试的压力确实会让人感觉焦虑。你能具体说说，是什么让你特别担心自己做不好呢？ 学生：我觉得自己做题速度很慢，考试的时候总是想着自己可能会答错，觉得压力特别大。心理咨询师：这种担心其实是很常见的，特别是在高压的环境下。你是否有过类似的情境，结果并没有像你想象的那么糟糕？学生：嗯，有时候我考试前也很担心，但最终成绩还好。不过我总是担心自己会在某次考试中失败。心理咨询师：你的焦虑其实是一种对未来的担忧，尝试去接受这些不确定性，给自己一些正面的肯定。你有没有尝试过深呼吸或冥想来放松自己？学生：我还没试过，但听起来不错，我会试试的。"
    prompt = "当前上下文描述了一个情境：\n<Context>\n{context}\n<Context>\n这是一个通用的聊天对话。请以第一人称的口吻直接回答以下问题。请确保回答直接、准确地针对问题本身，不要添加额外的背景信息或建议。如果问题与上下文无关，请直接说明我们没有讨论过这个话题，并提供一个简洁的通用回答，而不是额外的信息。\n问题：{input}\n"
    
    return ChatbotRequest(query=query, context=context, prompt=prompt)

def send_chatbot_request():
    chatbot_request = create_chatbot_request()
    url = "http://0.0.0.0:8000/chatbot"
    headers = {"Content-Type": "application/json"}  # 确保 Content-Type 正确

    # 自定义 timeout 配置
    timeout = httpx.Timeout(None)  # None 表示禁用超时限制

    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=chatbot_request.dict(), headers=headers)

        print("Response status code:", response.status_code)
        print("Response content:", response.text)

        if response.status_code == 200:
            try:
                chatbot_response = ChatbotResponse(**response.json())
                print("Chatbot Response:", chatbot_response.response)
            except Exception as e:
                print("Error parsing response JSON:", e)
        else:
            print(f"Request failed with status code {response.status_code}")


send_chatbot_request()