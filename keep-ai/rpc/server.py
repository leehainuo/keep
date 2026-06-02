import logging
from concurrent import futures

import grpc

from config.settings import get_settings
from rpc.gen import ai_service_pb2_grpc
from rpc.handlers import AIServiceHandler


def serve() -> None:
    settings = get_settings()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ai_service_pb2_grpc.add_AIServiceServicer_to_server(AIServiceHandler(), server)

    address = f"{settings.grpc_host}:{settings.grpc_port}"
    server.add_insecure_port(address)
    server.start()

    logging.info("Keep-AI gRPC server started at %s", address)
    server.wait_for_termination()
