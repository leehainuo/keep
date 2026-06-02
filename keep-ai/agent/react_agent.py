from typing import Any, TypedDict

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from config.settings import Settings, get_settings
from models.chat_model import ChatModelFactory
from prompts.system_prompt import SYSTEM_PROMPT
from retriever.knowledge_retriever import KnowledgeRetriever
from schemas.chat import ChatMessage, ChatResult
from schemas.knowledge import RetrievedDocument
from tools.observability_tools import build_tools

""" 格式化内容 """
def _normalize_content(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "".join(parts)

    return str(content)

""" Agent 状态 """
class AgentState(TypedDict, total=False):
    query: str
    history: list[ChatMessage]
    use_rag: bool
    rag_query: str
    refs: list[RetrievedDocument]
    messages: list[BaseMessage]
    prepared_query: str
    answer: str
    references: list[dict]

""" ReAct 智能体 """
class ReActAgent:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.model_factory = ChatModelFactory(self.settings)
        self.retriever = KnowledgeRetriever(self.settings)
        self.tools = build_tools(self.retriever, self.settings)

        self.react_agent = create_agent(
            model=self.model_factory.main_model(streaming=False),
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
        )
        self.streaming_react_agent = create_agent(
            model=self.model_factory.main_model(streaming=True),
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
        )
        self.graph = self._build_graph()

    """ 构建图编排 """
    def _build_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("InputToRag", self._input_to_rag)
        graph.add_node("KnowledgeRetriever", self._retrieve_refs_node)
        graph.add_node("InputToChat", self._input_to_chat)
        graph.add_node("ChatTemplate", self._chat_template)
        graph.add_node("ReactAgent", self._run_react_agent)

        graph.add_edge(START, "InputToRag")
        graph.add_edge("InputToRag", "KnowledgeRetriever")
        graph.add_edge("KnowledgeRetriever", "InputToChat")
        graph.add_edge("InputToChat", "ChatTemplate")
        graph.add_edge("ChatTemplate", "ReactAgent")
        graph.add_edge("ReactAgent", END)

        return graph.compile()

    """ 截断历史记录 """
    def _trim_history(self, history: list[ChatMessage]) -> list[ChatMessage]:
        return history[-self.settings.prompt_max_history :]

    """ 转换历史记录 """
    def _convert_history(self, history: list[ChatMessage]) -> list[BaseMessage]:
        messages: list[BaseMessage] = []
        for item in self._trim_history(history):
            role = item.role.lower()
            if role == "assistant":
                messages.append(AIMessage(content=item.content))
            else:
                messages.append(HumanMessage(content=item.content))
        return messages

    """ 检索知识库 """
    def _retrieve_refs(self, query: str, use_rag: bool) -> list[RetrievedDocument]:
        if not use_rag or not self.settings.enable_rag:
            return []
        return self.retriever.search(query, top_k=self.settings.search_top_k)

    """ 格式化参考资料 """
    def _format_refs_for_prompt(self, docs: list[RetrievedDocument]) -> str:
        if not docs:
            return ""

        lines: list[str] = []
        for idx, doc in enumerate(docs, start=1):
            lines.append(
                f"参考资料{idx}\n"
                f"标题: {doc.title}\n"
                f"分类: {doc.category}\n"
                f"相关度: {doc.score:.4f}\n"
                f"内容: {doc.content[:1200]}"
            )
        return "\n\n".join(lines)

    """ 准备最终问题 """
    def _prepare_query(self, query: str, docs: list[RetrievedDocument]) -> str:
        normalized = query.strip()
        if normalized in {"继续", "请继续", "继续分析", "继续查询"}:
            normalized = "请基于已有上下文直接继续输出阶段性结论，不要重复过程性描述。"

        refs_text = self._format_refs_for_prompt(docs)
        if not refs_text:
            return normalized

        return f"{normalized}\n\n以下是参考资料:\n{refs_text}"

    """ 转换引用信息 """
    def _build_references(self, refs: list[RetrievedDocument]) -> list[dict]:
        return [
            {
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "snippet": item.content[:200],
                "score": item.score,
            }
            for item in refs
        ]

    """ 提取 RAG 查询 """
    def _input_to_rag(self, state: AgentState) -> AgentState:
        return {"rag_query": state.get("query", "").strip()}

    """ 检索参考资料节点 """
    def _retrieve_refs_node(self, state: AgentState) -> AgentState:
        refs = self._retrieve_refs(
            query=state.get("rag_query", ""),
            use_rag=state.get("use_rag", True),
        )
        return {"refs": refs}

    """ 准备对话消息节点 """
    def _input_to_chat(self, state: AgentState) -> AgentState:
        history = state.get("history", [])
        return {"messages": self._convert_history(history)}

    """ 组装 Prompt 节点 """
    def _chat_template(self, state: AgentState) -> AgentState:
        refs = state.get("refs", [])
        prepared_query = self._prepare_query(state.get("query", ""), refs)
        messages = list(state.get("messages", []))
        messages.append(HumanMessage(content=prepared_query))
        return {
            "prepared_query": prepared_query,
            "messages": messages,
            "references": self._build_references(refs),
        }

    """ 执行 ReAct Agent 节点 """
    def _run_react_agent(self, state: AgentState) -> AgentState:
        result = self.react_agent.invoke({"messages": state.get("messages", [])})
        final_messages = result.get("messages", [])
        answer = ""
        if final_messages:
            answer = _normalize_content(final_messages[-1].content)
        return {"answer": answer}

    """ 聊天 """
    def chat(self, query: str, history: list[ChatMessage], use_rag: bool = True) -> ChatResult:
        result = self.graph.invoke(
            {
                "query": query,
                "history": history,
                "use_rag": use_rag,
            }
        )
        return ChatResult(
            answer=result.get("answer", ""),
            references=result.get("references", []),
        )

    """ 流式聊天 """
    def stream_chat(self, query: str, history: list[ChatMessage], use_rag: bool = True):
        refs = self._retrieve_refs(query, use_rag)
        prepared_query = self._prepare_query(query, refs)
        messages = self._convert_history(history)
        messages.append(HumanMessage(content=prepared_query))

        for chunk, _metadata in self.streaming_react_agent.stream(
            {"messages": messages},
            stream_mode="messages",
        ):
            raw_content = getattr(chunk, "content", None)
            if raw_content is None:
                continue
            content = _normalize_content(raw_content)
            if content:
                yield content
