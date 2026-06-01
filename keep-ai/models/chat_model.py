from langchain_openai import ChatOpenAI

from config.settings import Settings, get_settings

""" 聊天模型工厂 """
class ChatModelFactory:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
    
    """ 创建主模型 """
    def main_model(self, streaming: bool = False) -> ChatOpenAI:
        return ChatOpenAI(
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_base_url,
            model=self.settings.llm_main_model,
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_tokens,
            streaming=streaming,
            timeout=60,
        )
    
    """ 创建快速模型 """
    def quick_model(self, streaming: bool = False) -> ChatOpenAI:
        return ChatOpenAI(
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_base_url,
            model=self.settings.llm_quick_model,
            temperature=0.3,
            max_tokens=2048,
            streaming=streaming,
            timeout=30,
        )