import logging

import grpc

from agent.react_agent import ReActAgent
from rpc.gen import ai_service_pb2
from rpc.gen import ai_service_pb2_grpc
from schemas.chat import ChatMessage

""" gRPC 服务处理器 """


class AIServiceHandler(ai_service_pb2_grpc.AIServiceServicer):
    def __init__(self) -> None:
        self.agent = ReActAgent()

    def Chat(self, request, context: grpc.ServicerContext):
        """处理聊天请求。"""
        logging.info(
            "Chat request received: session_id=%s user_id=%s use_rag=%s query=%s",
            request.session_id,
            request.user_id,
            request.use_rag,
            request.query[:120],
        )

        history = [
            ChatMessage(role=item.role, content=item.content)
            for item in request.history
        ]

        result = self.agent.chat(
            query=request.query,
            history=history,
            use_rag=request.use_rag,
        )

        response = ai_service_pb2.ChatResponse(
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

        logging.info(
            "Chat request completed: session_id=%s answer_length=%s references=%s",
            request.session_id,
            len(response.answer),
            len(response.references),
        )
        return response

    def StreamChat(self, request, context: grpc.ServicerContext):
        """处理流式聊天请求。"""
        logging.info(
            "StreamChat request received: session_id=%s user_id=%s use_rag=%s query=%s",
            request.session_id,
            request.user_id,
            request.use_rag,
            request.query[:120],
        )

        history = [
            ChatMessage(role=item.role, content=item.content)
            for item in request.history
        ]

        chunk_count = 0
        for chunk in self.agent.stream_chat(
            query=request.query,
            history=history,
            use_rag=request.use_rag,
        ):
            chunk_count += 1
            yield ai_service_pb2.StreamChatResponse(
                delta=chunk,
                done=False,
            )

        logging.info(
            "StreamChat request completed: session_id=%s chunks=%s",
            request.session_id,
            chunk_count,
        )
        yield ai_service_pb2.StreamChatResponse(
            delta="",
            done=True,
        )
