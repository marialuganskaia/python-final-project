import aiohttp
import yarl
from aiohttp import web


async def request_handler(request: web.Request) -> web.Response:
    """
    Проверяет, что запрос содержит корректный http(s) URL в параметрах:
    /fetch?url=http%3A%2F%2Fexample.com%2F
    Затем выполняет асинхронную загрузку указанного ресурса и возвращает его содержимое с кодом HTTP-статуса.
    Если URL не содержит схему (http или https) или является некорректным, возвращается ответ с кодом 400 (Bad Request).
    При ошибках запроса возвращается 502 (Bad Gateway).
    :param request: Объект запроса aiohttp.web.Request
    :return: Объект ответа aiohttp.web.Response
    """
    curr_url = request.rel_url.query.get('url')
    if not curr_url:
        return web.Response(
            text="No url to fetch",
            status=400
        )
    try:
        parsed_url = yarl.URL(curr_url)
        if not parsed_url.scheme:
            return web.Response(
                text="Empty url scheme",
                status=400
            )
        if parsed_url.scheme not in ('http', 'https'):
            return web.Response(
                text=f"Bad url scheme: {parsed_url.scheme}",
                status=400
            )
    except Exception:
        return web.Response(
            text="Invalid url",
            status=400
        )
    session: aiohttp.ClientSession = request.app["session"]
    try:
        async with session.get(parsed_url) as response:
            body = await response.text()
            return web.Response(
                text=body,
                status=response.status
            )
    except Exception:
        return web.Response(
            text="Bad Gateway",
            status=502
        )


async def initialize_app(app: web.Application) -> None:
    """
    Настраивает handler'ы для приложения и инициализирует aiohttp-сессию для выполнения запросов.
    :param app: app to apply settings with
    """
    app["session"] = aiohttp.ClientSession()
    app.router.add_get("/fetch", request_handler)


async def close_app(app: web.Application) -> None:
    """
    Завершение приложения
    :param app: приложение которое должно завершиться!
    """
    session = app["session"]
    if not session.closed:
        await session.close()
