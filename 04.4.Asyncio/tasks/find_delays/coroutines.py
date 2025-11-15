import asyncio


# Текущая реализация не проходит тесты! Вам нужно настроить задачи, так чтобы оно проходило тесты!
async def coroutine_1(delay: float = 0.1) -> None:
    print("First message from coroutine 1")
    await asyncio.sleep(delay * 3)
    print("Second message from coroutine 1")
    await asyncio.sleep(delay * 3)
    print("Third message from coroutine 1")
    await asyncio.sleep(delay * 1)
    print("Forth message from coroutine 1")
    await asyncio.sleep(delay * 4)
    print("Fifth message from coroutine 1")


async def coroutine_2(delay: float = 0.1) -> None:
    print("First message from coroutine 2")
    await asyncio.sleep(delay * 2)
    print("Second message from coroutine 2")
    await asyncio.sleep(delay * 2)
    print("Third message from coroutine 2")
    await asyncio.sleep(delay * 5)
    print("Forth message from coroutine 2")
    await asyncio.sleep(delay * 1)
    print("Fifth message from coroutine 2")


async def coroutine_3(delay: float = 0.1) -> None:
    print("First message from coroutine 3")
    await asyncio.sleep(delay * 1)
    print("Second message from coroutine 3")
    await asyncio.sleep(delay * 4)
    print("Third message from coroutine 3")
    await asyncio.sleep(delay * 3)
    print("Forth message from coroutine 3")
    await asyncio.sleep(delay * 4)
    print("Fifth message from coroutine 3")


async def main() -> None:
    """Главная функция: запускает три корутины параллельно."""
    await asyncio.gather(
        coroutine_1(),
        coroutine_2(),
        coroutine_3(),
    )


if __name__ == "__main__":
    asyncio.run(main())
