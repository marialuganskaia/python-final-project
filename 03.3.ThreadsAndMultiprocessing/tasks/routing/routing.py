from typing import List

class Request:
    def __init__(self, client_id: str, request_id: str, processing_time: float):
        self.client_id = client_id
        self.request_id = request_id
        self.processing_time = processing_time

class Server:
    """
    Represents a server that can process requests.
    """
    def __init__(self, server_id: str, performance_score: int):
        self.server_id = server_id
        self.performance_score = performance_score

    def process_request(self, request: Request) -> None:
        """
        Processes a request. Save the request client_id and request_id.
        """
        pass

    def is_alive(self) -> bool:
        """
        Checks if the server is alive.
        """
        pass
    
    def crash(self) -> None:
        """
        Crashes the server.
        """
        pass

    def recover(self) -> None:
        """
        Recovers the server.
        """
        pass

    def is_processed(self, request_id: str) -> bool:
        """
        Checks if the request is processed. Emulates caching.
        """
        pass


class Router:
    """
    Represents a router that can route requests to servers.
    """
    def __init__(self, servers: List[Server], max_load: int):
        pass

    def route(self, request: Request) -> None:
        pass

    def add_server(self, server: Server) -> None:
        pass

    def remove_server(self, server: Server) -> None:
        pass