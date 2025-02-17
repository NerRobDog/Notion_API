"""
Синхронный + асинхронный Python-клиент для официального API Notion.
Подключайте страницы и базы данных Notion к инструментам, которыми вы
пользуетесь каждый день, создавая мощные рабочие процессы.
"""

from .client import AsyncClient, Client
from .errors import APIErrorCode, APIResponseError

__all__ = ["AsyncClient", "Client", "APIErrorCode", "APIResponseError"]