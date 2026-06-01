import hashlib
from datetime import datetime

from clients.elasticsearch_client import get_elasticsearch_client
from config.settings import Settings, get_settings
from embedding.embedder import Embedder
from schemas.knowledge import KnowledgeDocument, RetrievedDocument

"""
知识库检索器
 - 1. 把文档存入 ElasticSearch（带向量）
 - 2. 检索时，根据查询向量和文档向量计算相似度，返回 top_k 个文档
"""
class KnowledgeRetriever:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.es = get_elasticsearch_client()
        self.embedder = Embedder(self.settings)
        self.index_name = self.settings.es_knowledge_index
        self.ensure_index()

    """ 确保索引存在 """
    def ensure_index(self) -> None:
        # 确保索引存在
        if self.es.indices.exists(index=self.index_name):
            return

        # 创建索引，定义映射
        mappings = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "category": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "vector": {
                        "type": "dense_vector",
                        "dims": self.settings.embedding_dimension,
                        "index": True,
                        "similarity": "cosine",
                    },
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                }
            }
        }
        self.es.indices.create(index=self.index_name, body=mappings)

    """
    生成文档 ID
    :param title: 文档标题
    :param content: 文档内容
    :return: 文档 ID - 基于标题和内容的MD5
    """
    def _make_doc_id(self, title: str, content: str) -> str:
        raw = f"{title}\n{content}".encode("utf-8")
        return hashlib.md5(raw).hexdigest()

    """
    索引文档
     - 1. 文档内容用 Embedder 生成向量
     - 2. 补全文档 ID、时间
     - 3. 文档 + 向量 存入 ElasticSearch
    :param doc: 文档对象
    :return: 文档 ID
    """
    def index_document(self, doc: KnowledgeDocument) -> str:
        vector = self.embedder.embed_query(doc.content)
        now = datetime.utcnow()

        if not doc.id:
            doc.id = self._make_doc_id(doc.title, doc.content)

        if not doc.created_at:
            doc.created_at = now

        doc.updated_at = now
        doc.vector = vector

        self.es.index(
            index=self.index_name,
            id=doc.id,
            document=doc.model_dump(mode="json"),
            refresh=True,
        )
        return doc.id

    """
    检索文档
     - 核心: 混合检索 -> 向量检索（语义）+ 关键词检索（BM25 ）
    :param query: 查询字符串
    :param top_k: 返回的文档数量
    :return: 检索到的文档列表
    """
    def search(self, query: str, top_k: int | None = None) -> list[RetrievedDocument]:
        size = top_k or self.settings.search_top_k
        query_vector = self.embedder.embed_query(query)

        body = {
            "size": size,
            "query": {
                "bool": {
                    "should": [
                        # 1. 向量相似度检索（语义匹配）
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                                    "params": {"query_vector": query_vector},
                                },
                            }
                        },
                        # 2. 关键词匹配（title、content、category、tags）
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^3", "content^2", "category", "tags"],
                                "operator": "or",
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                }
            },
            "_source": ["title", "content", "category", "tags"],
        }

        resp = self.es.search(index=self.index_name, body=body)
        hits = resp.get("hits", {}).get("hits", [])

        results: list[RetrievedDocument] = []
        for hit in hits:
            source = hit.get("_source", {})
            results.append(
                RetrievedDocument(
                    id=hit.get("_id", ""),
                    title=source.get("title", ""),
                    content=source.get("content", ""),
                    category=source.get("category", "general"),
                    tags=source.get("tags", []),
                    score=float(hit.get("_score", 0.0)),
                )
            )
        return results