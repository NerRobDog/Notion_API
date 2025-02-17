# notion_sugar/core/decorators.py
"""
Модуль декораторов для валидации и инициализации классов Notion страниц и баз данных.

Предоставляет декораторы для работы с классами, представляющими страницы и базы данных Notion.
"""

from .errors import ValidationError
from .fields import Field
from functools import wraps
from typing import Type, TypeVar, Any

T = TypeVar('T')

def Page(cls: Type[T]) -> Type[T]:
    """
    Декоратор для классов, представляющих страницы Notion.

    Выполняет валидацию полей класса:
    - Проверяет обязательные поля
    - Проверяет значения полей типа 'select' на соответствие допустимым опциям

    Args:
        cls (Type[T]): Класс, который необходимо декорировать

    Returns:
        Type[T]: Декорированный класс

    Raises:
        ValidationError: Если обязательное поле не установлено или значение select-поля недопустимо
    """
    original_init = cls.__init__ if hasattr(cls, '__init__') else lambda self: None

    @wraps(original_init)
    def new_init(self, **kwargs):
        # Инициализация полей значением None
        for field_name, field_value in cls.__dict__.items():
            if isinstance(field_value, Field):
                setattr(self, field_name, None)

        # Вызов оригинального __init__
        original_init(self)

        # Установка значений из kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Валидация полей
        for field_name, field_value in cls.__dict__.items():
            if isinstance(field_value, Field):
                value = getattr(self, field_name, None)
                if field_value.required and value is None:
                    raise ValidationError(f"Required field {field_name} is not set")
                if value is not None and field_value.type == "select" and field_value.options:
                    if value not in field_value.options:
                        raise ValidationError(
                            f"Invalid value for {field_name}. Must be one of: {field_value.options}"
                        )

    cls.__init__ = new_init
    return cls

def Database(cls: Type[T]) -> Type[T]:
    """
    Декоратор для классов, представляющих базы данных Notion.

    Инициализирует все аннотированные поля класса значением None,
    если они не были установлены при создании экземпляра.

    Args:
        cls (Type[T]): Класс, который необходимо декорировать

    Returns:
        Type[T]: Декорированный класс
    """
    original_init = cls.__init__ if hasattr(cls, '__init__') else lambda self: None

    @wraps(cls)
    @wraps(original_init)
    def new_init(self, **kwargs):
        original_init(self)
        for field_name in cls.__annotations__:
            if not hasattr(self, field_name):
                setattr(self, field_name, None)
        for key, value in kwargs.items():
            if key in cls.__annotations__:
                setattr(self, key, value)

    cls.__init__ = new_init
    return cls