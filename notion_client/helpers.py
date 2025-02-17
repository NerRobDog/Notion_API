"""Utility functions"""
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, Generator, List
from urllib.parse import urlparse
from uuid import UUID


"""
    Список функций:
    1. pick — возвращает словарь, составленный из пар ключ-значение для ключей, переданных в качестве аргументов.
    2. get_url — возвращает URL для объекта с заданным id.
    3. get_id — возвращает id объекта по заданному URL.
    4. iterate_paginated_api — возвращает итератор по результатам любой пагинированной (разбитой на страницы) API Notion.
    5. collect_paginated_api — собирает все результаты пагинации API в список.
    6. async_iterate_paginated_api — возвращает асинхронный итератор по результатам любой пагинированной API Notion.
    7. async_collect_paginated_api — асинхронно собирает все результаты пагинации API в список.
    8. is_full_block — возвращает `True`, если ответ является полным блоком.
    9. is_full_page — возвращает `True`, если ответ является полной страницей.
    10. is_full_database — возвращает `True`, если ответ является полной базой данных.
    11. is_full_page_or_database — возвращает `True`, если `response` является полной базой данных или полной страницей.
    12. is_full_user — возвращает `True`, если ответ является полным пользователем.
    13. is_full_comment — возвращает `True`, если ответ является полным комментарием.
    14. is_text_rich_text_item_response — возвращает `True`, если `rich_text` является текстом.
    15. is_equation_rich_text_item_response — возвращает `True`, если `rich_text` является уравнением.
    16. is_mention_rich_text_item_response — возвращает `True`, если `rich_text` является упоминанием.
    17. validate_notion_id — проверяет и нормализует ID Notion.
    18. validate_auth_token — проверяет формат токена авторизации.
"""

def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    """Возвращает словарь, составленный из пар ключ-значение для ключей, переданных в качестве аргументов."""
    result = {}
    for key in keys:
        if key not in base:
            continue
        value = base.get(key)
        if value is None and key == "start_cursor":
            continue
        result[key] = value
    return result


def get_url(object_id: str) -> str:
    """Возвращает URL для объекта с заданным id."""
    return f"https://notion.so/{UUID(object_id).hex}"


def get_id(url: str) -> str:
    """Возвращает id объекта по заданному URL."""
    parsed = urlparse(url)
    if parsed.netloc not in ("notion.so", "www.notion.so"):
        raise ValueError("Not a valid Notion URL.")
    path = parsed.path
    if len(path) < 32:
        raise ValueError("The path in the URL seems to be incorrect.")
    raw_id = path[-32:]
    return str(UUID(raw_id))


def iterate_paginated_api(
    function: Callable[..., Any], **kwargs: Any
) -> Generator[Any, None, None]:
    """Возвращает итератор по результатам любой пагинированной API Notion."""
    next_cursor = kwargs.pop("start_cursor", None)

    while True:
        response = function(**kwargs, start_cursor=next_cursor)
        for result in response.get("results"):
            yield result

        next_cursor = response.get("next_cursor")
        if not response.get("has_more") or not next_cursor:
            return


def collect_paginated_api(function: Callable[..., Any], **kwargs: Any) -> List[Any]:
    """Собирает все результаты пагинации API в список."""
    return [result for result in iterate_paginated_api(function, **kwargs)]


async def async_iterate_paginated_api(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> AsyncGenerator[Any, None]:
    """Возвращает асинхронный итератор по результатам любой пагинированной API Notion."""
    next_cursor = kwargs.pop("start_cursor", None)

    while True:
        response = await function(**kwargs, start_cursor=next_cursor)
        for result in response.get("results"):
            yield result

        next_cursor = response.get("next_cursor")
        if (not response["has_more"]) | (next_cursor is None):
            return


async def async_collect_paginated_api(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> List[Any]:
    """Асинхронно собирает все результаты пагинации API в список."""
    return [result async for result in async_iterate_paginated_api(function, **kwargs)]


def is_full_block(response: Dict[Any, Any]) -> bool:
    """Возвращает `True`, если ответ является полным блоком."""
    return response.get("object") == "block" and "type" in response


def is_full_page(response: Dict[Any, Any]) -> bool:
    """Возвращает `True`, если ответ является полной страницей."""
    return response.get("object") == "page" and "url" in response


def is_full_database(response: Dict[Any, Any]) -> bool:
    """Возвращает `True`, если ответ является полной базой данных."""
    return response.get("object") == "database" and "title" in response


def is_full_page_or_database(response: Dict[Any, Any]) -> bool:
    """Возвращает `True`, если `response` является полной базой данных или полной страницей."""
    if response.get("object") == "database":
        return is_full_database(response)
    return is_full_page(response)


def is_full_user(response: Dict[Any, Any]) -> bool:
    """Возвращает `True`, если ответ является полным пользователем."""
    return "type" in response


def is_full_comment(response: Dict[Any, Any]) -> bool:
    """Возвращает `True`, если ответ является полным комментарием."""
    return "type" in response



def is_text_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Возвращает `True`, если `rich_text` является текстом."""
    return rich_text.get("type") == "text"


def is_equation_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Возвращает `True`, если `rich_text` является уравнением."""
    return rich_text.get("type") == "equation"


def is_mention_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Возвращает `True`, если `rich_text` является упоминанием."""
    return rich_text.get("type") == "mention"


def validate_notion_id(value: str) -> str:
    """
    Проверяет и нормализует ID Notion или извлекает ID из URL.

    Args:
        value (str): ID Notion или URL страницы/базы данных

    Returns:
        str: Нормализованный ID Notion

    Raises:
        ValueError: Если формат ID или URL неверный
    """
    try:
        # Пробуем получить ID из URL если передана ссылка
        if value.startswith(("https://", "http://")):
            parsed_url = urlparse(value)
            base_id = parsed_url.path.split("/")[-1]  # Извлекаем последний фрагмент пути
            clean_id = base_id.split("?")[0]  # Убираем `?v=...`
            return str(clean_id)
        # Иначе валидируем как UUID
        return str(UUID(value.replace("-", "")))
    except ValueError as e:
        raise ValueError(f"Неверный формат ID или URL Notion: {value}") from e

def validate_auth_token(token: str) -> str:
    """Проверяет формат токена авторизации"""
    if not token.startswith(("secret_", "v2_", "ntn_")):
        raise ValueError("Токен должен начинаться с 'secret_' или 'v2_' или 'ntn_'")
    return token