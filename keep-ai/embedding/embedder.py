from langchain_openai import OpenAIEmbeddings

from config.settings import Settings, get_settings

"""
嵌入器
 - 专门负责把文本转换成向量（Embedding）
 - 支持查询和文档的嵌入
"""
class Embedder:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = OpenAIEmbeddings(
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_base_url,
            model=self.settings.embedding_model,
        )
    
    """ 嵌入查询文本 """
    def embed_query(self, text: str) -> list[float]:
        return self.client.embed_query(text)

    """ 嵌入文档文本 """
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.client.embed_documents(texts)