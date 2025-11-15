import time
from unittest.mock import patch
from typing import Any, Optional, Type

import aiohttp
import pytest
import pytest_asyncio
from aioresponses import aioresponses
from aiohttp.test_utils import TestServer

import request_app
import server


@pytest.fixture
def reset_server_state() -> None:
    """автообновлятор"""
    server.request_count = 0
    server.first_request_time = None
    server.test_complete = False


@pytest_asyncio.fixture
async def mock_server(reset_server_state: Any) -> Any:
    app = server.create_app()
    test_server = TestServer(app)
    await test_server.start_server()
    try:
        yield test_server
    finally:
        await test_server.close()


@pytest.mark.asyncio
async def test_request_app_basic(mock_server: Any) -> None:
    """Базовый минимум: тестируем отправку 100 запросов"""
    total_requests = 100
    concurrent_requests = 10
    url = f"http://{mock_server.host}:{mock_server.port}/"

    await request_app.main(url, total_requests, concurrent_requests)
    assert server.request_count == total_requests


class MockResponse:
    def __init__(self, status: int) -> None:
        self.status = status

    async def text(self) -> str:
        return "Mocked response"

    async def __aenter__(self) -> "MockResponse":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        return None


class MockClientSession:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def get(self, url: str, *args: Any, **kwargs: Any) -> MockResponse:
        return MockResponse(status=200)

    async def __aenter__(self) -> "MockClientSession":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        return None


@pytest.mark.asyncio
async def test_send_10000_requests_under_one_second() -> None:
    """Проверяем, что 10 000 запросов выполняются менее чем за одну секунду."""
    url = "http://example.com/test"
    total_requests = 10_000
    concurrent_requests = 10_000

    with patch("builtins.print"), patch(
        "aiohttp.ClientSession", new=MockClientSession
    ):
        start_time = time.time()
        await request_app.main(url, total_requests, concurrent_requests)
        end_time = time.time()

    total_time = end_time - start_time

    assert total_time <= 1.0, (
        f"Время выполнения {total_time:.2f} сек превышает 1 секунду"
    )
    print(f"Total time taken: {total_time:.4f} seconds")


@pytest.mark.asyncio
async def test_send_request_exception() -> None:
    """Проверяем что ошибки обрабатываются"""
    with aioresponses() as mocked:
        url = "http://testserver/"
        mocked.get(url, exception=Exception("Network error"))
        async with aiohttp.ClientSession() as session:
            await request_app.send_request(session, url)
