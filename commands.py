# commands.py
import sys
from typing import Callable, Dict, List, Any

# Конфигурация доступных команд
COMMAND_CONFIG = {
    "list": {
        "usage": "list",
        "desc": "Получить список всех записей",
        "example": "python main.py list",
        "min_args": 1,
        "args": []
    },
    "add": {
        "usage": "add <название> [приоритет] [свойства] [типы_свойств]",
        "desc": "Добавить новую запись",
        "example": 'python main.py add "Новая задача" "Высокий" \\\n'
                   '    \'{"Сервис": ["API", "Бэкенд"]}\' \\\n'
                   '    \'{"Сервис": "multi_select"}\'',
        "min_args": 3,
        "args": ["name", "priority", "properties", "property_types"]
    },
    "update": {
        "usage": "update <id> <новое_название> [свойства] [типы_свойств]",
        "desc": "Обновить существующую запись",
        "example": 'python main.py update abc123 "Обновленная задача" \\\n'
                   '    \'{"Сервис": ["DevOps"]}\' \\\n'
                   '    \'{"Сервис": "multi_select"}\'',
        "min_args": 4,
        "args": ["page_id", "name", "properties", "property_types"]
    },
    "delete": {
        "usage": "delete <id>",
        "desc": "Удалить запись",
        "example": "python main.py delete abc123",
        "min_args": 3,
        "args": ["page_id"]
    }
}

COMMANDS: Dict[str, Dict[str, Any]] = {}


def print_help() -> None:
    """Вывод справочной информации по командам."""
    print("\n📋 Доступные команды:")
    for cmd, info in COMMAND_CONFIG.items():
        print(f"\n🔸 {cmd}")
        print(f"   Использование: {info['usage']}")
        print(f"   Описание: {info['desc']}")
        print(f"   Пример: {info['example']}")


def register_command(name: str, handler: Callable) -> None:
    """Регистрация команды в системе."""
    if name not in COMMAND_CONFIG:
        raise ValueError(f"Неизвестная команда: {name}")

    COMMANDS[name] = {
        "handler": handler,
        "min_args": COMMAND_CONFIG[name]["min_args"],
        "args": COMMAND_CONFIG[name]["args"]
    }


def execute_command() -> None:
    """Выполнение команды из аргументов командной строки."""
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help", "help"]:
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    if command not in COMMANDS:
        print(f"❌ Неизвестная команда: {command}")
        print_help()
        sys.exit(1)

    cmd_info = COMMANDS[command]
    if len(sys.argv) < cmd_info["min_args"]:
        print(f"❌ Недостаточно аргументов для команды {command}")
        print_help()
        sys.exit(1)

    args = sys.argv[2:]
    while len(args) < len(cmd_info["args"]):
        if cmd_info["args"][len(args)] in ["properties", "property_types"]:
            args.append("{}")
        else:
            args.append(None)

    try:
        cmd_info["handler"](*args)
    except Exception as e:
        print(f"❌ Ошибка при выполнении команды {command}: {e}")
        sys.exit(1)