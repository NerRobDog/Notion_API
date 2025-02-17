# notion_sugar/core/fields.py
from dataclasses import dataclass
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')


@dataclass
class Field(Generic[T]):
    """
    Базовый класс для представления поля в Notion.

    Attributes:
        type (str): Тип поля в Notion (например, 'title', 'rich_text', 'select' и т.д.)
        options (Optional[List[str]]): Список возможных значений для полей с выбором
        required (bool): Флаг, указывающий является ли поле обязательным
        default (T): Значение по умолчанию для поля
    """
    type: str
    options: Optional[List[str]] = None
    required: bool = False
    default: T = None


class FieldFactory:
    """
    Фабрика для создания различных типов полей Notion.

    Предоставляет статические методы для создания предварительно настроенных
    экземпляров Field с соответствующими типами Notion.
    """

    @staticmethod
    def title() -> Field:
        """
        Создает поле заголовка.

        Returns:
            Field: Поле типа 'title'
        """
        return Field(type="title")

    @staticmethod
    def text() -> Field:
        """
        Создает текстовое поле с форматированием.

        Returns:
            Field: Поле типа 'rich_text'
        """
        return Field(type="rich_text")

    @staticmethod
    def select(options: List[str]) -> Field:
        """
        Создает поле с выбором из списка опций.

        Args:
            options (List[str]): Список доступных вариантов выбора

        Returns:
            Field: Поле типа 'select' с указанными опциями
        """
        return Field(type="select", options=options)

    @staticmethod
    def date() -> Field:
        """
        Создает поле даты.

        Returns:
            Field: Поле типа 'date'
        """
        return Field(type="date")

    @staticmethod
    def person() -> Field:
        """
        Создает поле для указания пользователя.

        Returns:
            Field: Поле типа 'people'
        """
        return Field(type="people")


field = FieldFactory()