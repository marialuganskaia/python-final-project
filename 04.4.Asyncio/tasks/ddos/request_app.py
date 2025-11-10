import asyncio
import time

import aiohttp


async def send_request(session: aiohttp.ClientSession, url: str) -> None:
    """Отправка одного запроса (заглушка)."""
    pass


async def main(url: str, total_requests: int, concurrent_requests: int) -> None:
    """Основная функция: создаёт и выполняет множество запросов."""
    connector = aiohttp.TCPConnector(limit=concurrent_requests)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [send_request(session, url) for _ in range(total_requests)]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    TOTAL_REQUESTS: int = 100_000
    CONCURRENT_REQUESTS: int = 3_000
    URL: str = "http://localhost:8888/"

    start = time.time()
    asyncio.run(main(URL, TOTAL_REQUESTS, CONCURRENT_REQUESTS))
    duration = time.time() - start
    print(f"Выполнено {TOTAL_REQUESTS} запросов за {duration:.2f} сек.")
