from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from config.settings import Settings, get_settings
from models.chat_model import ChatModelFactory
from prompts.system_prompt import SYSTEM_PROMPT
from schemas.chat import ChatMessage

""" 简单智能体 """
class SimpleAgent:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.model_factory = ChatModelFactory(self.settings)

    """ 构建消息列表 """
    def _build_messages(self, query: str, history: list[ChatMessage]) -> list:
        messages: list = [
            SystemMessage(content=SYSTEM_PROMPT),
        ]

        for item in history[-self.settings.prompt_max_history :]:
            role = item.role.lower()
            if role == "assistant":
                messages.append(AIMessage(content=item.content))
            else:
                messages.append(HumanMessage(content=item.content))

        messages.append(HumanMessage(content=query))
        return messages

    """ 聊天 """
    def chat(self, query: str, history: list[ChatMessage]) -> str:
        llm = self.model_factory.main_model(streaming=False)
        message = self._build_messages(query, history)
        result = llm.invoke(message)
        return str(result.content)

    """ 流式聊天 """
    def stream_chat(self, query: str, history: list[ChatMessage]):
        llm = self.model_factory.main_model(streaming=True)
        message = self._build_messages(query, history)
        for chunk in llm.stream(message):
            content = getattr(chunk, "content", "")
            if content:
                yield content
