import logging
import signal
import threading
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
    bound_port = server.add_insecure_port(address)
    if bound_port == 0:
        raise RuntimeError(f"Failed to bind to address {address}")

    server.start()

    logging.info("Keep-AI gRPC server started at %s", address)

    shutdown_event = threading.Event()

    def cleanup() -> None:
        logging.info("Cleaning up resources...")

    def handle_shutdown(signum, frame) -> None:
        del frame
        if shutdown_event.is_set():
            return

        shutdown_event.set()
        logging.info("Received signal %s, shutting down gRPC server...", signum)

        stop_event = server.stop(grace=5)
        stop_event.wait(timeout=5)

        cleanup()
        logging.info("Keep-AI gRPC server stopped")

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        handle_shutdown(signal.SIGINT, None)
