import grpc
import time

from rpc.gen import ai_service_pb2
from rpc.gen import ai_service_pb2_grpc


def main() -> None:
    channel = grpc.insecure_channel("127.0.0.1:50051")
    client = ai_service_pb2_grpc.AIServiceStub(channel)

    request = ai_service_pb2.ChatRequest(
        session_id="debug-stream-session",
        user_id="debug-user",
        query="请用流式方式介绍一下 keep-ai 的核心能力",
        history=[],
        use_rag=False,
    )

    print("request:")
    print(request)
    print()
    print("stream:")

    start = time.time()
    stream = client.StreamChat(request, timeout=60)

    idx = 0
    for item in stream:
        idx += 1
        now = time.time() - start
        if item.delta:
            print(f"\n[chunk {idx} at {now:.2f}s]")
            print(repr(item.delta))
        if item.done:
            print("\n[stream done]")


if __name__ == "__main__":
    main()