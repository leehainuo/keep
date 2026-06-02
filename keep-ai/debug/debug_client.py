import grpc

from rpc.gen import ai_service_pb2
from rpc.gen import ai_service_pb2_grpc


def main() -> None:
    channel = grpc.insecure_channel("127.0.0.1:50051")
    client = ai_service_pb2_grpc.AIServiceStub(channel)

    request = ai_service_pb2.ChatRequest(
        session_id="debug-session",
        user_id="debug-user",
        query="请介绍一下 keep-ai 当前具备哪些能力",
        history=[],
        use_rag=False,
    )

    resp = client.Chat(
        request,
        timeout=60,
    )

    print("request:")
    print(request)
    print()
    print("answer:")
    print(resp.answer)
    print()
    print("references:")
    print(resp.references)


if __name__ == "__main__":
    main()
