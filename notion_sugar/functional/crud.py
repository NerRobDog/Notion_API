# notion_sugar/functional/crud.py
from datetime import datetime
from typing import Any, Dict, List, Optional, Generator

from notion_client import Client


class DatabaseQuery:
    """Класс для работы с базами данных Notion.

    Предоставляет fluent interface для выполнения CRUD операций с базами данных Notion.
    Поддерживает фильтрацию, сортировку, пагинацию и преобразование типов данных.

    Attributes:
        database_id (str): ID базы данных в Notion
        client (Client): Экземпляр клиента Notion API
        _filters (list): Внутренний список фильтров запроса
        _sorts (list): Внутренний список параметров сортировки
    """

    def __init__(self, database_id: str, client: Client):
        """
        Args:
            database_id (str): ID базы данных в Notion
            client (Client): Экземпляр клиента Notion API
        """
        self.database_id = database_id
        self.client = client
        self._filters = []
        self._sorts = []

    def first(self) -> Optional[Dict[str, Any]]:
        """Получить первую запись из результатов запроса.

        Returns:
            Optional[Dict[str, Any]]: Первая запись или None, если результаты пусты
        """
        results = self.get_rows()
        return results[0] if results else None

    def count(self) -> int:
        """Получить количество записей, соответствующих текущему запросу.

        Returns:
            int: Количество записей
        """
        return len(self.get_rows())

    def paginate(self, page_size: int = 100) -> Generator[Dict[str, Any], None, None]:
        """Постраничная итерация по результатам запроса.

        Args:
            page_size (int, optional): Размер страницы. По умолчанию 100.

        Yields:
            Dict[str, Any]: Записи из базы данных
        """
        has_more = True
        next_cursor = None

        while has_more:
            response = self.client.databases.query(
                database_id=self.database_id,
                start_cursor=next_cursor,
                page_size=page_size,
                filter={"and": self._filters} if self._filters else None,
                sorts=self._sorts or None
            )
            yield from response["results"]
            has_more = response["has_more"]
            next_cursor = response["next_cursor"]

    def where(self, **kwargs: Any) -> "DatabaseQuery":
        """Фильтрация записей по условиям.

        Args:
            **kwargs: Пары ключ-значение для фильтрации

        Returns:
            DatabaseQuery: Текущий объект для цепочки вызовов
        """
        for key, value in kwargs.items():
            filter_type = self._get_filter_type(value)
            self._filters.append({
                "property": key,
                filter_type: self._get_filter_value(value, filter_type)
            })
        return self

    def order_by(self, field: str, descending: bool = False) -> "DatabaseQuery":
        """Установка сортировки результатов.

        Args:
            field (str): Поле для сортировки
            descending (bool, optional): Направление сортировки. По умолчанию False.

        Returns:
            DatabaseQuery: Текущий объект для цепочки вызовов
        """
        self._sorts.append({
            "property": field,
            "direction": "descending" if descending else "ascending"
        })
        return self

    def add_row(self, **kwargs: Any) -> Dict[str, Any]:
        """Добавление новой записи в базу данных.

        Args:
            **kwargs: Пары ключ-значение для создания записи

        Returns:
            Dict[str, Any]: Созданная запись
        """
        properties = self._prepare_properties(kwargs)
        return self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties
        )

    def update(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Обновление записей, соответствующих текущему запросу.

        Args:
            **kwargs: Пары ключ-значение для обновления

        Returns:
            List[Dict[str, Any]]: Список обновленных записей
        """
        pages = self.get_rows()
        results = []
        for page in pages:
            properties = self._prepare_properties(kwargs)
            result = self.client.pages.update(
                page_id=page["id"],
                properties=properties
            )
            results.append(result)
        return results

    def get_rows(self) -> List[Dict[str, Any]]:
        """Получение всех записей, соответствующих текущему запросу.

        Returns:
            List[Dict[str, Any]]: Список записей
        """
        filter_obj = {"and": self._filters} if self._filters else None
        return self.client.databases.query(
            database_id=self.database_id,
            filter=filter_obj,
            sorts=self._sorts or None
        ).get("results", [])

    def _prepare_properties(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Подготовка свойств для API Notion.

        Args:
            data (Dict[str, Any]): Исходные данные

        Returns:
            Dict[str, Any]: Подготовленные свойства
        """
        properties = {}
        for key, value in data.items():
            properties[key] = self._get_property_value(value)
        return properties

    def _get_property_value(self, value: Any) -> Dict[str, Any]:
        """Преобразование значения в формат свойства Notion.

        Args:
            value (Any): Исходное значение

        Returns:
            Dict[str, Any]: Структура свойства для API Notion
        """
        if isinstance(value, str):
            return {
                "title" if value == "Name" else "rich_text": [
                    {"text": {"content": value}}
                ]
            }
        elif isinstance(value, datetime):
            return {
                "date": {
                    "start": value.isoformat()
                }
            }
        elif isinstance(value, bool):
            return {"checkbox": value}
        elif isinstance(value, (int, float)):
            return {"number": value}
        elif isinstance(value, list):
            return {"multi_select": [{"name": v} for v in value]}
        return {"rich_text": [{"text": {"content": str(value)}}]}

    def _get_filter_type(self, value: Any) -> str:
        """Определение типа фильтра на основе значения.

        Args:
            value (Any): Значение для фильтрации

        Returns:
            str: Тип фильтра Notion
        """
        if isinstance(value, str):
            return "rich_text"
        elif isinstance(value, bool):
            return "checkbox"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, datetime):
            return "date"
        elif isinstance(value, list):
            return "multi_select"
        return "rich_text"

    def _get_filter_value(self, value: Any, filter_type: str) -> Dict[str, Any]:
        """Преобразование значения в формат фильтра Notion.

        Args:
            value (Any): Значение для фильтрации
            filter_type (str): Тип фильтра

        Returns:
            Dict[str, Any]: Структура фильтра для API Notion
        """
        if filter_type == "rich_text":
            return {"equals": str(value)}
        elif filter_type == "checkbox":
            return {"equals": bool(value)}
        elif filter_type == "number":
            return {"equals": float(value)}
        elif filter_type == "date":
            return {"equals": value.isoformat()}
        elif filter_type == "multi_select":
            return {"contains": value[0] if value else ""}
        return {"equals": str(value)}