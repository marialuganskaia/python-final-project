import asyncio
import time

import aiohttp
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase
from yarl import URL

from proxy import close_app, initialize_app


class ProxyFetchTests(AioHTTPTestCase):
    async def get_application(self) -> web.Application:
        """Создаёт тестовое приложение с тремя endpoint'ами."""
        app_instance = web.Application()

        async def success_endpoint(_: web.Request) -> web.Response:
            return web.Response(text="Success")

        async def error_endpoint(_: web.Request) -> web.Response:
            raise web.HTTPInternalServerError(text="Internal server error")

        async def delay_endpoint(_: web.Request) -> web.Response:
            await asyncio.sleep(1)
            return web.Response(text="Delayed response")

        app_instance.router.add_get("/success", success_endpoint)
        app_instance.router.add_get("/error", error_endpoint)
        app_instance.router.add_get("/delay", delay_endpoint)

        await initialize_app(app_instance)
        return app_instance

    def generate_server_url(self, path: str) -> str:
        return str(
            URL.build(
                scheme="http",
                host=self.server.host,
                port=self.server.port,
                path=path,
            )
        )

    def prepare_fetch_url(self, destination_url: str) -> str:
        return str(
            URL.build(
                path="/fetch",
                query={"url": destination_url},
            )
        )

    async def test_fetch_success(self) -> None:
        url = self.prepare_fetch_url(self.generate_server_url("/success"))
        resp = await self.client.get(url)
        assert resp.status == 200
        assert await resp.text() == "Success"

    async def test_fetch_error(self) -> None:
        url = self.prepare_fetch_url(self.generate_server_url("/error"))
        resp = await self.client.get(url)
        assert resp.status == 500
        assert await resp.text() == "Internal server error"

    async def test_invalid_url(self) -> None:
        url = self.prepare_fetch_url("invalid_url")
        resp = await self.client.get(url)
        assert resp.status == 400
        assert await resp.text() == "Empty url scheme"

    async def test_missing_url(self) -> None:
        resp = await self.client.get("/fetch")
        assert resp.status == 400
        assert await resp.text() == "No url to fetch"

    async def test_unsupported_scheme(self) -> None:
        url = self.prepare_fetch_url("ftp://example.com/")
        resp = await self.client.get(url)
        assert resp.status == 400
        assert await resp.text() == "Bad url scheme: ftp"

    async def test_concurrent_fetches(self) -> None:
        start = time.time()
        urls = [
            self.prepare_fetch_url(self.generate_server_url("/delay"))
            for _ in range(3)
        ]
        tasks = [self.client.get(u) for u in urls]
        responses = await asyncio.gather(*tasks)
        end = time.time()

        assert end - start < 1.5
        for resp in responses:
            assert resp.status == 200
            assert await resp.text() == "Delayed response"


class AppLifecycleTests(AioHTTPTestCase):
    async def get_application(self) -> web.Application:
        app_instance = web.Application()
        await initialize_app(app_instance)

        async def test_endpoint(_: web.Request) -> web.Response:
            return web.Response(text="pong")

        app_instance.router.add_get("/ping", test_endpoint)
        return app_instance

    async def tearDownAsync(self) -> None:
        await close_app(self.server.app)

    async def test_app_fetching(self) -> None:
        async with aiohttp.ClientSession() as session:
            url = str(
                URL(
                    f"http://{self.server.host}:{self.server.port}/fetch?url="
                    f"http://{self.server.host}:{self.server.port}/ping"
                )
            )
            response = await session.get(url)
            assert response.status == 200
            assert await response.text() == "pong"
