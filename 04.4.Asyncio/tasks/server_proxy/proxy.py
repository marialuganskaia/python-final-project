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
    pass


async def initialize_app(app: web.Application) -> None:
    """
    Настраивает handler'ы для приложения и инициализирует aiohttp-сессию для выполнения запросов.
    :param app: app to apply settings with
    """
    pass


async def close_app(app: web.Application) -> None:
    """
    Завершение приложения
    :param app: приложение которое должно завершиться!
    """
    pass
