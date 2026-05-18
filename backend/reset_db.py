#!/usr/bin/env python3
"""
Скрипт для пересоздания базы данных и применения миграций Alembic.

Использование:
    python reset_db.py

Требования:
    - Установлены зависимости проекта (alembic, sqlalchemy, asyncpg)
    - База данных PostgreSQL доступна по адресу из alembic.ini
    - Пользователь БД имеет права на создание/удаление баз данных
"""

import os
import sys
import subprocess
from pathlib import Path

# Переходим в директорию backend
BACKEND_DIR = Path(__file__).parent.resolve()
os.chdir(BACKEND_DIR)

# Цвета для вывода
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'


def print_status(message: str, color: str = GREEN):
    """Вывод сообщения с цветом."""
    print(f"{color}{message}{RESET}")


def print_error(message: str):
    """Вывод ошибки."""
    print(f"{RED}Ошибка: {message}{RESET}")


def run_command(command: list, description: str) -> bool:
    """Выполнение команды и проверка результата."""
    print_status(f"Выполнение: {description}", YELLOW)
    try:
        result = subprocess.run(
            command,
            cwd=BACKEND_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_error(f"Команда не выполнена:\n{result.stderr}")
            return False
        if result.stdout:
            print(result.stdout)
        return True
    except Exception as e:
        print_error(f"Исключение при выполнении: {e}")
        return False


def drop_database(db_name: str, user: str, host: str, port: str) -> bool:
    """Удаление существующей базы данных."""
    print_status(f"Удаление базы данных '{db_name}' если существует...", YELLOW)
    
    # Команда для удаления БД (подключаемся к postgres)
    cmd = [
        'psql',
        '-h', host,
        '-p', port,
        '-U', user,
        '-d', 'postgres',
        '-c', f'DROP DATABASE IF EXISTS {db_name};'
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = 'postgres'  # Пароль по умолчанию из alembic.ini
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env
        )
        if result.returncode != 0:
            print_error(f"Не удалось удалить БД:\n{result.stderr}")
            return False
        print(result.stdout)
        return True
    except FileNotFoundError:
        print_error("psql не найден. Убедитесь, что PostgreSQL клиент установлен.")
        return False
    except Exception as e:
        print_error(f"Исключение: {e}")
        return False


def create_database(db_name: str, user: str, host: str, port: str) -> bool:
    """Создание новой базы данных."""
    print_status(f"Создание базы данных '{db_name}'...", YELLOW)
    
    cmd = [
        'psql',
        '-h', host,
        '-p', port,
        '-U', user,
        '-d', 'postgres',
        '-c', f'CREATE DATABASE {db_name};'
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = 'postgres'
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env
        )
        if result.returncode != 0:
            print_error(f"Не удалось создать БД:\n{result.stderr}")
            return False
        print(result.stdout)
        return True
    except Exception as e:
        print_error(f"Исключение: {e}")
        return False


def main():
    """Основная функция."""
    print_status("=" * 60, GREEN)
    print_status("Скрипт пересоздания базы данных и применения миграций", GREEN)
    print_status("=" * 60, GREEN)
    
    # Параметры подключения из alembic.ini
    # postgresql+asyncpg://postgres:postgres@postgres:5432/newlife
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'postgres')
    db_host = os.environ.get('DB_HOST', 'postgres')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'newlife')
    
    print_status(f"\nПараметры подключения:", YELLOW)
    print(f"  Хост: {db_host}:{db_port}")
    print(f"  Пользователь: {db_user}")
    print(f"  База данных: {db_name}")
    print()
    
    # Шаг 1: Удаление существующей БД
    if not drop_database(db_name, db_user, db_host, db_port):
        print_error("Не удалось удалить базу данных. Продолжение невозможно.")
        sys.exit(1)
    
    # Шаг 2: Создание новой БД
    if not create_database(db_name, db_user, db_host, db_port):
        print_error("Не удалось создать базу данных. Продолжение невозможно.")
        sys.exit(1)
    
    # Шаг 3: Применение миграций Alembic
    print_status("\nПрименение миграций Alembic...", YELLOW)
    
    # Устанавливаем переменную окружения для пароля
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    if not run_command(
        ['alembic', 'upgrade', 'head'],
        'alembic upgrade head'
    ):
        print_error("Не удалось применить миграции.")
        sys.exit(1)
    
    # Шаг 4: Проверка статуса миграций
    print_status("\nПроверка статуса миграций...", YELLOW)
    run_command(['alembic', 'current'], 'alembic current')
    
    print_status("\n" + "=" * 60, GREEN)
    print_status("База данных успешно пересоздана и миграции применены!", GREEN)
    print_status("=" * 60, GREEN)
    print_status(f"\nБаза данных '{db_name}' готова к использованию.", GREEN)


if __name__ == '__main__':
    main()
