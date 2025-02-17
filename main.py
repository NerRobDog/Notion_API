# main.py
import os
import sys
from dotenv import load_dotenv
from notion_sugar.core.client import NotionSugar
from commands import register_command, execute_command

# Загружаем переменные из .env
load_dotenv()

# Подключаемся к Notion API
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    print("❌ Ошибка: NOTION_TOKEN или DATABASE_ID не указаны в .env")
    sys.exit(1)

client = NotionSugar(NOTION_TOKEN)
db = client.db(DATABASE_ID)

def list_entries():
    """Получить список записей в базе данных."""
    try:
        db.query()
    except Exception as e:
        print(f"❌MAIN Ошибка при получении списка записей: {e}")

def add_entry(name: str, priority: str = None, properties: str = "{}", property_types: str = "{}"):
    """Добавить новую запись в базу данных."""
    data = {"Name": name}
    if priority:
        data["Priority"] = priority
    try:
        new_page = db.add_row(**data)
        print(f"✅ Запись добавлена: {new_page['id']}")
    except Exception as e:
        print(f"❌ Ошибка при добавлении записи: {e}")

def update_entry(page_id: str, name: str, properties: str = "{}", property_types: str = "{}"):
    """Обновить существующую запись."""
    try:
        db.update_row(page_id, Name=name)
        print(f"✅ Запись {page_id} обновлена")
    except Exception as e:
        print(f"❌ Ошибка при обновлении записи: {e}")

def delete_entry(page_id: str):
    """Удалить запись."""
    try:
        db.delete(page_id)
        print(f"🗑️ Запись {page_id} удалена")
    except Exception as e:
        print(f"❌ Ошибка при удалении записи: {e}")

if __name__ == "__main__":
    register_command("list", list_entries)
    register_command("add", add_entry)
    register_command("update", update_entry)
    register_command("delete", delete_entry)
    execute_command()