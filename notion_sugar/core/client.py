# notion_sugar/core/client.py
"""
Основной модуль для работы с Notion API через NotionSugar клиент.

Предоставляет упрощенный интерфейс для взаимодействия с Notion базами данных.
"""

from notion_client import Client
from notion_client.helpers import validate_notion_id, validate_auth_token
from .errors import NotionSugarError
from ..functional.crud import DatabaseQuery


class NotionSugar:
    """
    Основной класс для взаимодействия с Notion API.

    Предоставляет высокоуровневый интерфейс для работы с Notion,
    упрощая взаимодействие с базами данных.

    Attributes:
        auth_token (str): Валидированный токен аутентификации Notion API.
        client (Client): Экземпляр клиента Notion API.

    Raises:
        NotionSugarError: Если инициализация клиента не удалась.
    """

    def __init__(self, auth_token: str):
        """
        Инициализирует новый экземпляр NotionSugar.

        Args:
            auth_token (str): Токен аутентификации Notion API.

        Raises:
            NotionSugarError: Если валидация токена или создание клиента не удались.
        """
        try:
            self.auth_token = validate_auth_token(auth_token)
            self.client = Client(auth=self.auth_token)
        except Exception as e:
            raise NotionSugarError(f"Failed to initialize client: {str(e)}")

    def db(self, database_id: str) -> "DatabaseQuery":
        """
        Создает объект для работы с конкретной базой данных Notion.

        Args:
            database_id (str): ID базы данных в Notion.

        Returns:
            DatabaseQuery: Объект для выполнения запросов к базе данных.

        Raises:
            NotionSugarError: Если ID базы данных невалиден.
        """
        try:
            database_id = validate_notion_id(database_id)
            return DatabaseQuery(database_id, self.client)
        except ValueError as e:
            raise NotionSugarError(str(e))
