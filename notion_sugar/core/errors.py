from notion_client.errors import APIResponseError


class NotionSugarError(Exception):
    pass


class ValidationError(NotionSugarError):
    pass


class PropertyError(NotionSugarError):
    pass
