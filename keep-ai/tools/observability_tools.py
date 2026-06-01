from datetime import datetime

import httpx
from langchain_core.tools import tool

from clients.elasticsearch_client import get_elasticsearch_client
from config.settings import Settings, get_settings
from retriever.knowledge_retriever import KnowledgeRetriever

"""
构建可观测性工具集
    - 核心工具: 
        1. get_current_time - 获取当前服务器时间
        2. search_knowledge - 在知识库中检索和当前问题相关的内容
        3. query_metrics    - 查询 Prometheus 指标，参数为 PromQL 表达式
        4. query_logs       - 查询 Elasticsearch 日志，参数为日志关键词
        5. query_traces     - 查询 Jaeger 链路，参数为链路关键词
    :param retriever: 知识库检索器
    :param settings: 配置参数
    :return: 工具列表
"""
def build_tools(retriever: KnowledgeRetriever, settings: Settings | None = None) -> list:
    settings = settings or get_settings()
    es = get_elasticsearch_client()

    """获取当前服务器时间。"""
    @tool
    def get_current_time() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    """在知识库中检索和当前问题相关的内容。"""
    @tool
    def search_knowledge(query: str) -> str:
        docs = retriever.search(query, top_k=settings.search_top_k)
        if not docs:
            return "知识库中没有检索到相关内容。"

        lines: list[str] = []
        for idx, doc in enumerate(docs, start=1):
            lines.append(
                f"文档{idx}\n标题: {doc.title}\n分类: {doc.category}\n得分: {doc.score:.4f}\n内容: {doc.content[:800]}"
            )
        return "\n\n".join(lines)

    """查询 Prometheus 指标，参数为 PromQL 表达式。""""""查询 Prometheus 指标，参数为 PromQL 表达式。"""
    @tool
    def query_metrics(expr: str) -> str:
        url = f"{settings.prometheus_url.rstrip('/')}/api/v1/query"
        resp = httpx.get(url, params={"query": expr}, timeout=20.0)
        resp.raise_for_status()
        payload = resp.json()

        if payload.get("status") != "success":
            return f"Prometheus 查询失败: {payload}"

        result = payload.get("data", {}).get("result", [])
        if not result:
            return "没有查询到指标数据。"

        lines: list[str] = []
        for item in result[:10]:
            metric = item.get("metric", {})
            value = item.get("value", [])
            lines.append(f"metric={metric}, value={value}")
        return "\n".join(lines)

    """查询 Elasticsearch 日志，参数为关键词。"""
    @tool
    def query_logs(keyword: str) -> str:
        body = {
            "size": 10,
            "sort": [{"@timestamp": {"order": "desc"}}],
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["message^3", "service", "level", "trace_id"],
                    "operator": "or",
                }
            },
            "_source": ["@timestamp", "service", "level", "message", "trace_id"],
        }

        resp = es.search(index=settings.es_log_index, body=body)
        hits = resp.get("hits", {}).get("hits", [])
        if not hits:
            return "没有查询到日志。"

        lines: list[str] = []
        for hit in hits:
            src = hit.get("_source", {})
            lines.append(
                f"[{src.get('@timestamp', '')}] "
                f"[{src.get('service', '')}] "
                f"[{src.get('level', '')}] "
                f"{src.get('message', '')}"
            )
        return "\n".join(lines)

    """查询 Jaeger 链路，参数为服务名。"""
    @tool
    def query_traces(service_name: str) -> str:
        url = f"{settings.jaeger_url.rstrip('/')}/api/traces"
        resp = httpx.get(url, params={"service": service_name, "limit": 5}, timeout=20.0)
        resp.raise_for_status()
        payload = resp.json()
        data = payload.get("data", [])
        if not data:
            return "没有查询到链路数据。"

        lines: list[str] = []
        for trace in data[:5]:
            trace_id = trace.get("traceID", "")
            span_count = len(trace.get("spans", []))
            processes = trace.get("processes", {})
            service_names = [
                item.get("serviceName", "")
                for item in processes.values()
                if isinstance(item, dict)
            ]
            lines.append(
                f"trace_id={trace_id}, spans={span_count}, services={service_names}"
            )
        return "\n".join(lines)

    return [
        get_current_time,
        search_knowledge,
        query_metrics,
        query_logs,
        query_traces,
    ]