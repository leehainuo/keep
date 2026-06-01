from datetime import datetime
from pydantic import BaseModel, Field

""" 知识库文档模型 """
class KnowledgeDocument(BaseModel):
    id: str | None = None
    title: str
    content: str
    category: str = "general"
    tags: list[str] = Field(default_factory=list)
    vector: list[float] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

""" 检索到的文档模型 """
class RetrievedDocument(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: list[str] = Field(default_factory=list)
    score: float = 0.0