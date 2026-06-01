from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

""" 配置类 """
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    """ 服务端配置 """
    server_name: str = Field(
        default="keep-ai",
        validation_alias=AliasChoices("SERVER_NAME")
    )
    server_env: str = Field(
        default="dev",
        validation_alias=AliasChoices("SERVER_ENV")
    )
    grpc_host: str = Field(
        default="0.0.0.0",
        validation_alias=AliasChoices("GRPC_HOST")
    )
    grpc_port: int = Field(
        default=50051,
        validation_alias=AliasChoices("GRPC_PORT")
    )

    """ LLM 配置 """
    llm_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        validation_alias=AliasChoices("LLM_BASE_URL"),
    )
    llm_main_model: str = Field(
        default="qwen-plus",
        validation_alias=AliasChoices("LLM_MAIN_MODEL"),
    )
    llm_quick_model: str = Field(
        default="qwen-flash",
        validation_alias=AliasChoices("LLM_QUICK_MODEL"),
    )
    llm_temperature: float = Field(
        default=0.5,
        validation_alias=AliasChoices("LLM_TEMPERATURE"),
    )
    llm_max_tokens: int = Field(
        default=4096,
        validation_alias=AliasChoices("LLM_MAX_TOKENS"),
    )

    """ Embedding 模型配置 """
    embedding_model: str = Field(
        default="text-embedding-v4",
        validation_alias=AliasChoices("EMBEDDING_MODEL"),
    )
    embedding_dimension: int = Field(
        default=1024,
        validation_alias=AliasChoices("EMBEDDING_DIMENSION"),
    )

    """ Prompt 配置"""
    prompt_max_history: int = Field(
        default=10,
        validation_alias=AliasChoices("PROMPT_MAX_HISTORY"),
    )

    """ 搜索配置 """
    search_top_k: int = Field(
        default=5,
        validation_alias=AliasChoices("SEARCH_TOP_K"),
    )

    """ RAG 配置 """
    enable_rag: bool = Field(
        default=True,
        validation_alias=AliasChoices("ENABLE_RAG"),
    )

    """ Elasticsearch 配置 """
    es_url: str = Field(
        default="http://localhost:9200",
        validation_alias=AliasChoices("ES_URL"),
    )
    es_username: str = Field(
        default="",
        validation_alias=AliasChoices("ES_USERNAME"),
    )
    es_password: str = Field(
        default="",
        validation_alias=AliasChoices("ES_PASSWORD"),
    )
    es_verify_certs: bool = Field(
        default=False,
        validation_alias=AliasChoices("ES_VERIFY_CERTS"),
    )
    es_knowledge_index: str = Field(
        default="pilot_knowledge",
        validation_alias=AliasChoices("ES_KNOWLEDGE_INDEX"),
    )
    es_log_index: str = Field(
        default="pilot_logs",
        validation_alias=AliasChoices("ES_LOG_INDEX"),
    )

    """ Prometheus 配置 """
    prometheus_url: str = Field(
        default="http://localhost:9090",
        validation_alias=AliasChoices("PROMETHEUS_URL"),
    )

    """ Jaeger 配置 """
    jaeger_url: str = Field(
        default="http://localhost:16686",
        validation_alias=AliasChoices("JAEGER_URL"),
    )

    """ OTLP 配置 """
    otlp_http_endpoint: str = Field(
        default="http://localhost:4318",
        validation_alias=AliasChoices("OTLP_HTTP_ENDPOINT"),
    )

    """ Redis 配置 """
    redis_addr: str = Field(
        default="localhost:6379",
        validation_alias=AliasChoices("REDIS_ADDR"),
    )
    redis_password: str = Field(
        default="",
        validation_alias=AliasChoices("REDIS_PASSWORD"),
    )
    redis_db: int = Field(
        default=0,
        validation_alias=AliasChoices("REDIS_DB"),
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()