from pydantic import BaseModel

""" 聊天消息模型 """
class ChatMessage(BaseModel):
    role: str
    content: str

""" 聊天结果模型 """
class ChatResult(BaseModel):
    answer: str
    references: list[dict]