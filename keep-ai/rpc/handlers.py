import grpc

from agent.react_agent import ReActAgent
from rpc.gen import ai_service_pb2
from rpc.gen import ai_service_pb2_grpc
from schemas.chat import ChatMessage

""" gRPC 服务处理器 """


class AIServiceHandler(ai_service_pb2_grpc.AIServiceServicer):
    def __init__(self) -> None:
        self.agent = ReActAgent()


    """ 处理聊天请求 """
    def Chat(self, request, context: grpc.ServicerContext):
        history = [
            ChatMessage(role=item.role, content=item.content)
            for item in request.history
        ]

        result = self.agent.chat(
            query=request.query,
            history=history,
            use_rag=request.use_rag,
        )

        return ai_service_pb2.ChatResponse(
            answer=result.answer,
            references=[
                ai_service_pb2.Reference(
                    id=ref["id"],
                    title=ref["title"],
                    category=ref["category"],
                    snippet=ref["snippet"],
                    score=float(ref["score"]),
                )
                for ref in result.references
            ]
        )

    """ 处理流式聊天请求 """
    def StreamChat(self, request, context: grpc.ServicerContext):
        history = [
            ChatMessage(role=item.role, content=item.content)
            for item in request.history
        ]

        for chunk in self.agent.stream_chat(
            query=request.query,
            history=history,
            use_rag=request.use_rag,
        ):
            yield ai_service_pb2.StreamChatResponse(
                delta=chunk,
                done=False,
            )

        yield ai_service_pb2.StreamChatResponse(
            delta="",
            done=True,
        )
