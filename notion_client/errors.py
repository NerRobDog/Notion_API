
"""Пользовательские исключения.

Этот модуль определяет исключения, которые могут быть вызваны при возникновении ошибки.
"""
from enum import Enum
from typing import Optional

import httpx


class RequestTimeoutError(Exception):
    """Исключение для запросов, превысивших время ожидания.

    Запрос ожидает ответа в течение указанного периода времени или максимального количества
    повторных попыток. Если ответ не приходит в течение ограниченного времени или
    после всех попыток, выбрасывается это Исключение.
    """

    code = "notionhq_client_request_timeout"

    def __init__(self, message: str = "Запрос к API Notion превысил время ожидания") -> None:
        super().__init__(message)


class HTTPResponseError(Exception):
    """Исключение для ошибок HTTP.

    Ответы от API используют коды ответа HTTP, которые указывают на общие
    классы успеха и ошибок.
    """

    code: str = "notionhq_client_response_error"
    status: int
    headers: httpx.Headers
    body: str

    def __init__(self, response: httpx.Response, message: Optional[str] = None) -> None:
        if message is None:
            message = (
                f"Запрос к API Notion не удался со статусом: {response.status_code}"
            )
        super().__init__(message)
        self.status = response.status_code
        self.headers = response.headers
        self.body = response.text


class APIErrorCode(str, Enum):
    Unauthorized = "unauthorized"
    """Токен доступа недействителен."""

    RestrictedResource = "restricted_resource"
    """Учитывая используемый токен доступа, у клиента нет разрешения на
    выполнение этой операции."""

    ObjectNotFound = "object_not_found"
    """Учитывая используемый токен доступа, ресурс не существует.
    Эта ошибка также может указывать на то, что ресурс не был предоставлен владельцу
    токена доступа."""

    RateLimited = "rate_limited"
    """Этот запрос превышает допустимое количество запросов. Замедлитесь и попробуйте снова."""

    InvalidJSON = "invalid_json"
    """Тело запроса не может быть декодировано как JSON."""

    InvalidRequestURL = "invalid_request_url"
    """URL запроса недействителен."""

    InvalidRequest = "invalid_request"
    """Этот запрос не поддерживается."""

    ValidationError = "validation_error"
    """Тело запроса не соответствует схеме для ожидаемых параметров."""

    ConflictError = "conflict_error"
    """Транзакция не может быть завершена, возможно, из-за конфликта данных.
    Убедитесь, что параметры актуальны, и попробуйте снова."""

    InternalServerError = "internal_server_error"
    """Произошла непредвиденная ошибка. Обратитесь в службу поддержки Notion."""

    ServiceUnavailable = "service_unavailable"
    """Notion недоступен. Попробуйте позже.
    Это может произойти, когда время ответа на запрос превышает 60 секунд,
    максимальное время ожидания запроса."""


class APIResponseError(HTTPResponseError):
    """Ошибка, вызванная API Notion."""

    code: APIErrorCode

    def __init__(
        self, response: httpx.Response, message: str, code: APIErrorCode
    ) -> None:
        super().__init__(response, message)
        self.code = code


def is_api_error_code(code: str) -> bool:
    """Проверяет, принадлежит ли данный код к списку допустимых кодов ошибок API."""
    if isinstance(code, str):
        return code in (error_code.value for error_code in APIErrorCode)
    return False
