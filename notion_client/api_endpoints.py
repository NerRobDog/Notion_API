"""Эндпоинты API Notion."""  # noqa: E501

from typing import TYPE_CHECKING, Any

from notion_client.helpers import pick
from notion_client.typing import SyncAsync

if TYPE_CHECKING:  # pragma: no cover
    from notion_client.client import BaseClient


class Endpoint:
    def __init__(self, parent: "BaseClient") -> None:
        self.parent = parent


class BlocksChildrenEndpoint(Endpoint):
    def append(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Создает и добавляет новые дочерние блоки к блоку с указанным ID.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/patch-block-children)*
        """  # noqa: E501
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="PATCH",
            body=pick(kwargs, "children", "after"),
            auth=kwargs.get("auth"),
        )

    def list(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Возвращает постраничный массив дочерних [объектов блоков](https://developers.notion.com/reference/block), содержащихся в блоке.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/get-block-children)*
        """  # noqa: E501
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )


class BlocksEndpoint(Endpoint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.children = BlocksChildrenEndpoint(*args, **kwargs)

    def retrieve(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Получить [объект Block](https://developers.notion.com/reference/block) по указанному ID.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/retrieve-a-block)*
        """  # noqa: E501
        return self.parent.request(
            path=f"blocks/{block_id}", method="GET", auth=kwargs.get("auth")
        )

    def update(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Обновить содержимое для указанного `block_id` в зависимости от типа блока.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/update-a-block)*
        """  # noqa: E501
        return self.parent.request(
            path=f"blocks/{block_id}",
            method="PATCH",
            body=pick(
                kwargs,
                "embed",
                "type",
                "archived",
                "in_trash",
                "bookmark",
                "image",
                "video",
                "pdf",
                "file",
                "audio",
                "code",
                "equation",
                "divider",
                "breadcrumb",
                "table_of_contents",
                "link_to_page",
                "table_row",
                "heading_1",
                "heading_2",
                "heading_3",
                "paragraph",
                "bulleted_list_item",
                "numbered_list_item",
                "quote",
                "to_do",
                "toggle",
                "template",
                "callout",
                "synced_block",
                "table",
            ),
            auth=kwargs.get("auth"),
        )

    def delete(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Установить для [объекта Block](https://developers.notion.com/reference/block), включая блоки страниц, значение `archived: true`.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/delete-a-block)*
        """  # noqa: E501
        return self.parent.request(
            path=f"blocks/{block_id}",
            method="DELETE",
            auth=kwargs.get("auth"),
        )


class DatabasesEndpoint(Endpoint):
    def list(self, **kwargs: Any) -> SyncAsync[Any]:  # pragma: no cover
        """Получить список всех [баз данных](https://developers.notion.com/reference/database), доступных аутентифицированной интеграции.

        > ⚠️  **Устаревший эндпоинт**

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/get-databases)*
        """  # noqa: E501
        return self.parent.request(
            path="databases",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def query(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Получить список [страниц](https://developers.notion.com/reference/page), содержащихся в базе данных.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/post-database-query)*
        """  # noqa: E501
        return self.parent.request(
            path=f"databases/{database_id}/query",
            method="POST",
            query=pick(kwargs, "filter_properties"),
            body=pick(
                kwargs,
                "filter",
                "sorts",
                "start_cursor",
                "page_size",
                "archived",
                "in_trash",
            ),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Получить [объект базы данных](https://developers.notion.com/reference/database) по указанному ID.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/retrieve-a-database)*
        """  # noqa: E501
        return self.parent.request(
            path=f"databases/{database_id}", method="GET", auth=kwargs.get("auth")
        )

    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Создать базу данных как подстраницу в указанной родительской странице.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/create-a-database)*
        """  # noqa: E501
        return self.parent.request(
            path="databases",
            method="POST",
            body=pick(
                kwargs,
                "parent",
                "title",
                "description",
                "properties",
                "icon",
                "cover",
                "is_inline",
            ),
            auth=kwargs.get("auth"),
        )

    def update(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Обновить существующую базу данных согласно указанным параметрам.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/update-a-database)*
        """  # noqa: E501
        return self.parent.request(
            path=f"databases/{database_id}",
            method="PATCH",
            body=pick(
                kwargs,
                "properties",
                "title",
                "description",
                "icon",
                "cover",
                "is_inline",
                "archived",
                "in_trash",
            ),
            auth=kwargs.get("auth"),
        )


class PagesPropertiesEndpoint(Endpoint):
    def retrieve(self, page_id: str, property_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Получить объект `property_item` для указанных `page_id` и `property_id`.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/retrieve-a-page-property)*
        """  # noqa: E501
        return self.parent.request(
            path=f"pages/{page_id}/properties/{property_id}",
            method="GET",
            auth=kwargs.get("auth"),
            query=pick(kwargs, "start_cursor", "page_size"),
        )


class PagesEndpoint(Endpoint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.properties = PagesPropertiesEndpoint(*args, **kwargs)

    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Создать новую страницу в указанной базе данных или как дочернюю существующей страницы.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/post-page)*
        """  # noqa: E501
        return self.parent.request(
            path="pages",
            method="POST",
            body=pick(kwargs, "parent", "properties", "children", "icon", "cover"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, page_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Получить [объект Page](https://developers.notion.com/reference/page) по указанному ID.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/retrieve-a-page)*
        """  # noqa: E501
        return self.parent.request(
            path=f"pages/{page_id}",
            method="GET",
            query=pick(kwargs, "filter_properties"),
            auth=kwargs.get("auth"),
        )

    def update(self, page_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Обновить [значения свойств страницы](https://developers.notion.com/reference/page#property-value-object) для указанной страницы.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/patch-page)*
        """  # noqa: E501
        return self.parent.request(
            path=f"pages/{page_id}",
            method="PATCH",
            body=pick(kwargs, "in_trash", "archived", "properties", "icon", "cover"),
            auth=kwargs.get("auth"),
        )


class UsersEndpoint(Endpoint):
    def list(self, **kwargs: Any) -> SyncAsync[Any]:
        """Вернуть постраничный список [пользователей](https://developers.notion.com/reference/user) рабочего пространства.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/get-users)*
        """  # noqa: E501
        return self.parent.request(
            path="users",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, user_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Получить [пользователя](https://developers.notion.com/reference/user) по указанному ID.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/get-user)*
        """  # noqa: E501
        return self.parent.request(
            path=f"users/{user_id}", method="GET", auth=kwargs.get("auth")
        )

    def me(self, **kwargs: Any) -> SyncAsync[Any]:
        """Получить [пользователя-бота](https://developers.notion.com/reference/user), связанного с API токеном.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/get-self)*
        """  # noqa: E501
        return self.parent.request(
            path="users/me", method="GET", auth=kwargs.get("auth")
        )


class SearchEndpoint(Endpoint):
    def __call__(self, **kwargs: Any) -> SyncAsync[Any]:
        """Поиск по всем страницам и дочерним страницам, доступным интеграции.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/post-search)*
        """  # noqa: E501
        return self.parent.request(
            path="search",
            method="POST",
            body=pick(kwargs, "query", "sort", "filter", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )


class CommentsEndpoint(Endpoint):
    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Создать новый комментарий на указанной странице или в существующей цепочке обсуждения.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/create-a-comment)*
        """  # noqa: E501
        return self.parent.request(
            path="comments",
            method="POST",
            body=pick(kwargs, "parent", "discussion_id", "rich_text"),
            auth=kwargs.get("auth"),
        )

    def list(self, **kwargs: Any) -> SyncAsync[Any]:
        """Получить список нерешенных [объектов комментариев](https://developers.notion.com/reference/comment-object) из указанного блока.

        *[🔗 Документация эндпоинта](https://developers.notion.com/reference/retrieve-a-comment)*
        """  # noqa: E501
        return self.parent.request(
            path="comments",
            method="GET",
            query=pick(kwargs, "block_id", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )