"""Синхронный и асинхронный клиенты для API Notion."""
import json
import logging
from abc import abstractclassmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union

import httpx
from httpx import Request, Response

from notion_client.api_endpoints import (
    BlocksEndpoint,
    CommentsEndpoint,
    DatabasesEndpoint,
    PagesEndpoint,
    SearchEndpoint,
    UsersEndpoint,
)
from notion_client.errors import (
    APIResponseError,
    HTTPResponseError,
    RequestTimeoutError,
    is_api_error_code,
)
from notion_client.logging import make_console_logger
from notion_client.typing import SyncAsync


@dataclass
class ClientOptions:
    """Параметры для настройки клиента.

    Атрибуты:
        auth: Bearer токен для аутентификации. Если не определен, параметр `auth` 
            должен быть установлен для каждого запроса.
        timeout_ms: Количество миллисекунд ожидания до вызова 
            `RequestTimeoutError`.
        base_url: Корневой URL для отправки API запросов. Может быть изменен для 
            тестирования с мок-сервером.
        log_level: Уровень детализации логов. По умолчанию логи записываются 
            в `stdout`.
        logger: Пользовательский логгер.
        notion_version: Используемая версия Notion API.
    """

    auth: Optional[str] = None
    timeout_ms: int = 60_000
    base_url: str = "https://api.notion.com"
    log_level: int = logging.WARNING
    logger: Optional[logging.Logger] = None
    notion_version: str = "2022-06-28"


class BaseClient:
    def __init__(
            self,
            client: Union[httpx.Client, httpx.AsyncClient],
            options: Optional[Union[Dict[str, Any], ClientOptions]] = None,
            **kwargs: Any,
    ) -> None:
        if options is None:
            options = ClientOptions(**kwargs)
        elif isinstance(options, dict):
            options = ClientOptions(**options)

        self.logger = options.logger or make_console_logger()
        self.logger.setLevel(options.log_level)
        self.options = options

        self._clients: List[Union[httpx.Client, httpx.AsyncClient]] = []
        self.client = client

        self.blocks = BlocksEndpoint(self)
        self.databases = DatabasesEndpoint(self)
        self.users = UsersEndpoint(self)
        self.pages = PagesEndpoint(self)
        self.search = SearchEndpoint(self)
        self.comments = CommentsEndpoint(self)

    @property
    def client(self) -> Union[httpx.Client, httpx.AsyncClient]:
        return self._clients[-1]

    @client.setter
    def client(self, client: Union[httpx.Client, httpx.AsyncClient]) -> None:
        client.base_url = httpx.URL(f"{self.options.base_url}/v1/")
        client.timeout = httpx.Timeout(timeout=self.options.timeout_ms / 1_000)
        client.headers = httpx.Headers(
            {
                "Notion-Version": self.options.notion_version,
                "User-Agent": "ramnes/notion-sdk-py@2.3.0",
            }
        )
        if self.options.auth:
            client.headers["Authorization"] = f"Bearer {self.options.auth}"
        self._clients.append(client)

    def _build_request(
            self,
            method: str,
            path: str,
            query: Optional[Dict[Any, Any]] = None,
            body: Optional[Dict[Any, Any]] = None,
            auth: Optional[str] = None,
    ) -> Request:
        headers = httpx.Headers()
        if auth:
            headers["Authorization"] = f"Bearer {auth}"
        self.logger.info(f"{method} {self.client.base_url}{path}")
        self.logger.debug(f"=> {query} -- {body}")
        return self.client.build_request(
            method, path, params=query, json=body, headers=headers
        )

    def _parse_response(self, response: Response) -> Any:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            try:
                body = error.response.json()
                code = body.get("code")
            except json.JSONDecodeError:
                code = None
            if code and is_api_error_code(code):
                raise APIResponseError(response, body["message"], code)
            raise HTTPResponseError(error.response)

        body = response.json()
        self.logger.debug(f"=> {body}")

        return body

    @abstractclassmethod
    def request(
            self,
            path: str,
            method: str,
            query: Optional[Dict[Any, Any]] = None,
            body: Optional[Dict[Any, Any]] = None,
            auth: Optional[str] = None,
    ) -> SyncAsync[Any]:
        # noqa
        pass


class Client(BaseClient):
    """Синхронный клиент для API Notion."""

    client: httpx.Client

    def __init__(
            self,
            options: Optional[Union[Dict[Any, Any], ClientOptions]] = None,
            client: Optional[httpx.Client] = None,
            **kwargs: Any,
    ) -> None:
        if client is None:
            client = httpx.Client()
        super().__init__(client, options, **kwargs)

    def __enter__(self) -> "Client":
        self.client = httpx.Client()
        self.client.__enter__()
        return self

    def __exit__(
            self,
            exc_type: Type[BaseException],
            exc_value: BaseException,
            traceback: TracebackType,
    ) -> None:
        self.client.__exit__(exc_type, exc_value, traceback)
        del self._clients[-1]

    def close(self) -> None:
        """Закрыть пул соединений текущего внутреннего клиента."""
        self.client.close()

    def request(
            self,
            path: str,
            method: str,
            query: Optional[Dict[Any, Any]] = None,
            body: Optional[Dict[Any, Any]] = None,
            auth: Optional[str] = None,
    ) -> Any:
        """Отправить HTTP запрос."""
        request = self._build_request(method, path, query, body, auth)
        try:
            response = self.client.send(request)
        except httpx.TimeoutException:
            raise RequestTimeoutError()
        return self._parse_response(response)


class AsyncClient(BaseClient):
    """Асинхронный клиент для API Notion."""

    client: httpx.AsyncClient

    def __init__(
            self,
            options: Optional[Union[Dict[str, Any], ClientOptions]] = None,
            client: Optional[httpx.AsyncClient] = None,
            **kwargs: Any,
    ) -> None:
        if client is None:
            client = httpx.AsyncClient()
        super().__init__(client, options, **kwargs)

    async def __aenter__(self) -> "AsyncClient":
        self.client = httpx.AsyncClient()
        await self.client.__aenter__()
        return self

    async def __aexit__(
            self,
            exc_type: Type[BaseException],
            exc_value: BaseException,
            traceback: TracebackType,
    ) -> None:
        await self.client.__aexit__(exc_type, exc_value, traceback)
        del self._clients[-1]

    async def aclose(self) -> None:
        """Закрыть пул соединений текущего внутреннего клиента."""
        await self.client.aclose()

    async def request(
            self,
            path: str,
            method: str,
            query: Optional[Dict[Any, Any]] = None,
            body: Optional[Dict[Any, Any]] = None,
            auth: Optional[str] = None,
    ) -> Any:
        """Отправить HTTP запрос асинхронно."""
        request = self._build_request(method, path, query, body, auth)
        try:
            response = await self.client.send(request)
        except httpx.TimeoutException:
            raise RequestTimeoutError()
        return self._parse_response(response)
