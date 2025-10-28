from typing import List, Dict, Set
import threading
import time


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
        self.is_alive_flag = True
        self.processed: Set[str] = set()
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(1)

    def process_request(self, request: Request) -> None:
        """
        Processes a request. Save the request client_id and request_id.
        """
        time.sleep(request.processing_time)
        with self.lock:
            self.processed.add(request.request_id)

    def is_alive(self) -> bool:
        """
        Checks if the server is alive.
        """
        return self.is_alive_flag

    def crash(self) -> None:
        """
        Crashes the server.
        """
        self.is_alive_flag = False

    def recover(self) -> None:
        """
        Recovers the server.
        """
        self.is_alive_flag = True

    def is_processed(self, request_id: str) -> bool:
        """
        Checks if the request is processed. Emulates caching.
        """
        with self.lock:
            return request_id in self.processed


class Router:
    """
    Represents a router that can route requests to servers.
    """
    def __init__(self, servers: List[Server], max_load: int):
        self.servers = servers
        self.max_load = max_load
        self.semaphore = threading.Semaphore(max_load)
        self.lock = threading.Lock()
        self.wrr_lock = threading.Lock()
        self.client_to_server: Dict[str, Server] = {}
        self.current_weights: Dict[Server, int] = {server: 0 for server in self.servers}

    def get_alive_servers(self) -> List[Server]:
        return [server for server in self.servers if server.is_alive()]

    def wrr_find_server(self) -> Server:
        with self.wrr_lock:
            alive_servers = self.get_alive_servers()
            total = sum(server.performance_score for server in alive_servers)
            for server in alive_servers:
                self.current_weights[server] += server.performance_score
            max_server = max(alive_servers, key=lambda s: self.current_weights[s])
            self.current_weights[max_server] -= total
            return max_server

    def route(self, request: Request) -> None:
        client = request.client_id
        with self.lock:
            if client in self.client_to_server:
                server = self.client_to_server[client]
                if not server.is_alive() or server not in self.servers:
                    server = self.wrr_find_server()
                    self.client_to_server[client] = server
            else:
                server = self.wrr_find_server()
                self.client_to_server[client] = server
        self.semaphore.acquire()
        server.semaphore.acquire()
        try:
            server.process_request(request)
        finally:
            server.semaphore.release()
            self.semaphore.release()

    def add_server(self, server: Server) -> None:
        with self.lock:
            if server not in self.servers:
                self.servers.append(server)
            with self.wrr_lock:
                self.current_weights[server] = 0

    def remove_server(self, server: Server) -> None:
        with self.lock:
            if server in self.servers:
                self.servers.remove(server)
                self.client_to_server = {
                    c: s for c, s in self.client_to_server.items()
                    if s != server}
                with self.wrr_lock:
                    self.current_weights.pop(server, None)
