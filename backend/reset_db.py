#!/usr/bin/env python3
"""
Скрипт для пересоздания базы данных и применения миграций Alembic через Docker Compose.

Использование:
    python reset_db.py

Требования:
    - Docker и Docker Compose установлены
    - Контейнеры запущены (docker compose up -d)
"""

import os
import sys
import subprocess
from pathlib import Path

# Переходим в директорию проекта (родительскую для backend)
PROJECT_DIR = Path(__file__).parent.parent.resolve()
os.chdir(PROJECT_DIR)

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


def run_docker_command(command: list, description: str, check_output: bool = True) -> bool:
    """Выполнение команды docker compose."""
    print_status(f"Выполнение: {description}", YELLOW)
    try:
        result = subprocess.run(
            ['docker', 'compose'] + command,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_error(f"Команда не выполнена:\n{result.stderr}")
            return False
        if check_output and result.stdout:
            print(result.stdout)
        return True
    except FileNotFoundError:
        print_error("Docker не найден. Убедитесь, что Docker установлен.")
        return False
    except Exception as e:
        print_error(f"Исключение при выполнении: {e}")
        return False


def check_containers_running() -> bool:
    """Проверка, запущены ли контейнеры."""
    print_status("Проверка состояния контейнеров...", YELLOW)
    try:
        result = subprocess.run(
            ['docker', 'compose', 'ps', 'postgres'],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        if "Up" in result.stdout:
            return True
        else:
            print_status("Контейнер postgres не запущен. Запускаем сервисы...", YELLOW)
            run_docker_command(['up', '-d', 'postgres', 'redis'], 'Запуск postgres и redis')
            print_status("Ожидание готовности PostgreSQL (30 секунд)...", YELLOW)
            import time
            time.sleep(30)
            return True
    except Exception as e:
        print_error(f"Ошибка проверки контейнеров: {e}")
        return False


def drop_and_create_database(db_name: str, db_user: str) -> bool:
    """Удаление и создание базы данных через docker exec."""
    # Проверяем существование БД
    print_status(f"Проверка существования базы данных '{db_name}'...", YELLOW)
    check_cmd = ['exec', '-T', 'postgres', 'psql', '-U', db_user, '-d', 'postgres', 
                 '-tc', f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"]
    
    try:
        result = subprocess.run(
            ['docker', 'compose'] + check_cmd,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        db_exists = '1' in result.stdout
        
        if db_exists:
            print_status(f"Удаление базы данных '{db_name}'...", YELLOW)
            drop_cmd = ['exec', '-T', 'postgres', 'psql', '-U', db_user, '-d', 'postgres',
                       '-c', f'DROP DATABASE IF EXISTS {db_name};']
            result = subprocess.run(
                ['docker', 'compose'] + drop_cmd,
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print_error(f"Не удалось удалить БД:\n{result.stderr}")
                return False
            print(result.stdout)
        else:
            print_status(f"База данных '{db_name}' не существовала, пропускаем удаление.", YELLOW)
    except Exception as e:
        print_error(f"Ошибка при удалении БД: {e}")
        return False
    
    # Создание БД
    print_status(f"Создание базы данных '{db_name}'...", YELLOW)
    create_cmd = ['exec', '-T', 'postgres', 'psql', '-U', db_user, '-d', 'postgres',
                 '-c', f'CREATE DATABASE {db_name};']
    
    try:
        result = subprocess.run(
            ['docker', 'compose'] + create_cmd,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_error(f"Не удалось создать БД:\n{result.stderr}")
            return False
        print(result.stdout)
        return True
    except Exception as e:
        print_error(f"Ошибка при создании БД: {e}")
        return False


def apply_migrations() -> bool:
    """Применение миграций Alembic."""
    print_status("Применение миграций Alembic...", YELLOW)
    return run_docker_command(['exec', '-T', 'backend', 'alembic', 'upgrade', 'head'],
                             'alembic upgrade head')


def check_migrations() -> bool:
    """Проверка статуса миграций."""
    print_status("Проверка статуса миграций...", YELLOW)
    return run_docker_command(['exec', '-T', 'backend', 'alembic', 'current'],
                             'alembic current', check_output=False)


def main():
    """Основная функция."""
    print_status("=" * 60, GREEN)
    print_status("Скрипт пересоздания базы данных и применения миграций (Docker)", GREEN)
    print_status("=" * 60, GREEN)
    
    # Параметры
    db_user = os.environ.get('DB_USER', 'postgres')
    db_name = os.environ.get('DB_NAME', 'newlife')
    
    print_status(f"\nПараметры:", YELLOW)
    print(f"  База данных: {db_name}")
    print(f"  Пользователь: {db_user}")
    print(f"  Проект: {PROJECT_DIR}")
    print()
    
    # Проверка Docker
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Docker не найден. Установите Docker.")
        sys.exit(1)
    
    # Проверка контейнеров
    if not check_containers_running():
        print_error("Не удалось подготовить контейнеры.")
        sys.exit(1)
    
    # Удаление и создание БД
    if not drop_and_create_database(db_name, db_user):
        print_error("Не удалось пересоздать базу данных.")
        sys.exit(1)
    
    # Применение миграций
    if not apply_migrations():
        print_error("Не удалось применить миграции.")
        sys.exit(1)
    
    # Проверка статуса
    check_migrations()
    
    print_status("\n" + "=" * 60, GREEN)
    print_status("База данных успешно пересоздана и миграции применены!", GREEN)
    print_status("=" * 60, GREEN)
    print_status(f"\nБаза данных '{db_name}' готова к использованию.", GREEN)
    print()
    print_status("Примечание: Для создания администратора выполните:", YELLOW)
    print("  docker compose exec backend python -m app.scripts.create_admin")


if __name__ == '__main__':
    main()
