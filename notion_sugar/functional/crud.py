from datetime import datetime
from typing import Any, Dict, List, Optional
from notion_client import Client

class DatabaseQuery:
    """Класс для работы с базами данных Notion."""
    DEFAULT_PLACEHOLDER = ""
    def __init__(self, database_id: str, client: Client):
        """
        Инициализация класса DatabaseQuery.

        :param database_id: Идентификатор базы данных Notion.
        :param client: Клиент для взаимодействия с API Notion.
        """
        self.database_id = database_id
        self.client = client
        self.schema = self._fetch_schema()  # Получаем схему базы

    def _fetch_schema(self) -> Dict[str, Any]:
        """Получает структуру базы данных (доступные поля и их типы)."""
        try:
            database_info = self.client.databases.retrieve(database_id=self.database_id)
            return database_info.get("properties", {})
        except Exception as e:
            print(f"❌ Ошибка при получении структуры базы данных: {e}")
            return {}

    def generate_valid_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Формирует корректные данные перед отправкой в Notion."""
        valid_data = {}

        for field_name, field_value in data.items():
            if field_name not in self.schema:
                print(f"⚠️ Поле '{field_name}' отсутствует в базе данных, пропускаем.")
                continue

            field_type = self.schema[field_name]["type"]

            if field_type == "title":
                valid_data[field_name] = {"title": [{"text": {"content": str(field_value)}}]}
            elif field_type == "rich_text":
                valid_data[field_name] = {"rich_text": [{"text": {"content": str(field_value)}}]}
            elif field_type == "select":
                options = self.schema[field_name].get("select", {}).get("options", [])
                if any(opt["name"] == field_value for opt in options):
                    valid_data[field_name] = {"select": {"name": field_value}}
                else:
                    print(f"⚠️ Значение '{field_value}' не найдено среди допустимых вариантов для '{field_name}', пропускаем.")
            elif field_type == "multi_select":
                options = self.schema[field_name].get("multi_select", {}).get("options", [])
                selected_options = [opt for opt in options if opt["name"] in field_value]
                if selected_options:
                    valid_data[field_name] = {"multi_select": [{"name": opt["name"]} for opt in selected_options]}
                else:
                    print(f"⚠️ Значения '{field_value}' не соответствуют допустимым вариантам для '{field_name}', пропускаем.")
            elif field_type == "date":
                valid_data[field_name] = {"date": {"start": field_value.isoformat() if isinstance(field_value, datetime) else str(field_value)}}
            elif field_type == "checkbox":
                valid_data[field_name] = {"checkbox": bool(field_value)}
            elif field_type == "number":
                valid_data[field_name] = {"number": float(field_value)}
            elif field_type == "url":
                valid_data[field_name] = {"url": str(field_value)}
            elif field_type == "email":
                valid_data[field_name] = {"email": str(field_value)}
            elif field_type == "phone_number":
                valid_data[field_name] = {"phone_number": str(field_value)}
            else:
                print(f"⚠️ Тип '{field_type}' для '{field_name}' пока не поддерживается.")

        return valid_data

    def add_row(self, property_types: Dict[str, str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Добавление новой записи в базу данных с учетом типов полей."""
        properties = {}
        new_fields = {}

        for key, value in kwargs.items():
            if key in self.schema:
                properties[key] = self._format_property(self.schema[key]["type"], value)
            else:
                field_type = property_types.get(key, "rich_text") if property_types else "rich_text"
                print(f"⚠️ Добавляем новое свойство '{key}' с типом '{field_type}' в базу данных.")
                new_fields[key] = field_type
                properties[key] = self._format_property(field_type, value)

        if new_fields:
            self._update_schema(new_fields)

        try:
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            print(f"✅ Новая запись успешно создана: {response['id']}")
            return response
        except Exception as e:
            print(f"❌ Ошибка при добавлении записи: {e}")
            return {}
    def _update_schema(self, new_properties: Dict[str, str]):
        """Добавляет новые свойства в базу данных."""
        formatted_properties = {}
        for name, prop_type in new_properties.items():
            formatted_properties[name] = {"type": prop_type}

        try:
            self.client.databases.update(
                database_id=self.database_id,
                properties=formatted_properties
            )
            self.schema.update(formatted_properties)
            print(f"✅ Обновлена схема базы данных с новыми полями: {list(new_properties.keys())}")
        except Exception as e:
            print(f"❌ Ошибка при обновлении схемы базы данных: {e}")

    def _format_property(self, field_type: str, value: Any) -> Dict[str, Any]:
        """Форматирует значение в нужный формат перед отправкой в Notion."""
        if field_type == "title":
            return {"title": [{"text": {"content": str(value)}}]}
        elif field_type == "rich_text":
            return {"rich_text": [{"text": {"content": str(value)}}]}
        elif field_type == "select":
            return {"select": {"name": str(value)}}
        elif field_type == "multi_select":
            return {"multi_select": [{"name": v} for v in value] if isinstance(value, list) else []}
        elif field_type == "date":
            return {"date": {"start": value}}
        elif field_type == "checkbox":
            return {"checkbox": bool(value)}
        elif field_type == "number":
            return {"number": float(value)}
        elif field_type == "url":
            return {"url": str(value)}
        elif field_type == "email":
            return {"email": str(value)}
        elif field_type == "phone_number":
            return {"phone_number": str(value)}
        else:
            return {"rich_text": [{"text": {"content": str(value)}}]}

    def query(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.databases.query(database_id=self.database_id)
            results = response.get("results", [])

            formatted_results = []
            for entry in results:
                page_id = entry.get("id", self.DEFAULT_PLACEHOLDER)

                properties = entry.get("properties", {})
                if not properties:
                    print(f"⚠️ Пропущена запись {page_id}, так как у неё нет `properties`.")
                    continue

                title_value = "Без названия"
                if "Name" in properties and "title" in properties["Name"]:
                    title_parts = properties["Name"]["title"]
                    if title_parts:
                        title_value = title_parts[0].get("text", {}).get("content", "Без названия")

                record_data = {"id": page_id, "title": title_value}
                for field_name, field_info in self.schema.items():
                    field_type = field_info["type"]
                    value = properties.get(field_name, {})

                    if field_type == "title":
                        record_data[field_name] = title_value
                    elif field_type == "rich_text":
                        rich_text_list = value.get("rich_text", [])
                        content = rich_text_list[0].get("text", {}).get("content") if rich_text_list else None
                        record_data[field_name] = content if content is not None else self.DEFAULT_PLACEHOLDER
                    elif field_type == "select":
                        select_data = value.get("select")
                        name = select_data.get("name") if select_data else None
                        record_data[field_name] = name if name is not None else self.DEFAULT_PLACEHOLDER
                    elif field_type == "multi_select":
                        multi_select = value.get("multi_select", [])
                        names = [opt.get("name") for opt in multi_select if opt.get("name")]
                        record_data[field_name] = names if names else [self.DEFAULT_PLACEHOLDER]
                    elif field_type == "date":
                        date_value = value.get("date", {})
                        start_date = date_value.get("start") if date_value else None
                        record_data[field_name] = start_date if start_date is not None else self.DEFAULT_PLACEHOLDER
                    elif field_type == "checkbox":
                        checkbox = value.get("checkbox")
                        record_data[field_name] = "✅" if checkbox else "❌"
                    elif field_type == "number":
                        number = value.get("number")
                        record_data[field_name] = number if number is not None else self.DEFAULT_PLACEHOLDER
                    elif field_type == "url":
                        url = value.get("url")
                        record_data[field_name] = url if url is not None else self.DEFAULT_PLACEHOLDER
                    elif field_type == "email":
                        email = value.get("email")
                        record_data[field_name] = email if email is not None else self.DEFAULT_PLACEHOLDER
                    elif field_type == "phone_number":
                        phone = value.get("phone_number")
                        record_data[field_name] = phone if phone is not None else self.DEFAULT_PLACEHOLDER
                    elif field_type == "people":
                        people = value.get("people", [])
                        names = [user.get("name") for user in people if user.get("name")]
                        record_data[field_name] = names if names else [self.DEFAULT_PLACEHOLDER]

                formatted_results.append(record_data)

            print(f"\n📄 Найдено {len(formatted_results)} записей (исключены записи без `properties`):\n")
            for record in formatted_results:
                print(f"🆔 {record['id']} | 📌 {record['title']}")
                for key, val in record.items():
                    if key not in ["id", "title"]:
                        print(f"   🔹 {key}: {val}")
                print("-" * 40)

            return formatted_results

        except Exception as e:
            print(f"❌CRUD: Ошибка при получении списка записей: {e}")
            return []

        except Exception as e:
            print(f"❌CRUD: Ошибка при получении списка записей: {e}")
            return []

    def update_row(self, page_id: str, property_types: Dict[str, str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Обновление записи в базе данных с возможностью добавления новых свойств."""
        properties = {}
        new_fields = {}

        for key, value in kwargs.items():
            if key in self.schema:
                properties[key] = self._format_property(self.schema[key]["type"], value)
            else:
                field_type = property_types.get(key, "rich_text") if property_types else "rich_text"
                print(f"⚠️ Добавляем новое свойство '{key}' с типом '{field_type}' в базу данных.")
                new_fields[key] = field_type
                properties[key] = self._format_property(field_type, value)

        if new_fields:
            self._update_schema(new_fields)

        try:
            response = self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            print(f"✅ Запись {page_id} успешно обновлена!")
            return response
        except Exception as e:
            print(f"❌ Ошибка при обновлении записи: {e}")
            return {}