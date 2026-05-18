#!/usr/bin/env python3
"""
Скрипт для пересоздания базы данных и применения миграций Alembic.
Работает напрямую с PostgreSQL (без Docker).

Использование:
    python reset_db_local.py

Требования:
    - pip install psycopg2-binary alembic
    - PostgreSQL запущен и доступен
    - Пользователь БД имеет права CREATE DATABASE

Параметры подключения (можно переопределить через env):
    DB_HOST=localhost
    DB_PORT=5432
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_NAME=newlife
"""

import os
import sys
import time
import subprocess
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("Ошибка: psycopg2 не установлен.")
    print("Установите: pip install psycopg2-binary")
    sys.exit(1)

# Переходим в директорию backend
BACKEND_DIR = Path(__file__).parent.resolve()
os.chdir(BACKEND_DIR)

# Параметры подключения
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'newlife')


def print_separator():
    print("=" * 60)


def wait_for_postgres(max_attempts=30, delay=2):
    """Ждем доступности PostgreSQL."""
    print(f"Ожидание доступности PostgreSQL ({DB_HOST}:{DB_PORT})...")
    for attempt in range(1, max_attempts + 1):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname='postgres'
            )
            conn.close()
            print("✓ PostgreSQL доступен!")
            return True
        except psycopg2.OperationalError as e:
            if attempt < max_attempts:
                print(f"Попытка {attempt}/{max_attempts}: {e}. Ждем {delay}c...")
                time.sleep(delay)
            else:
                print(f"✗ Не удалось подключиться к PostgreSQL после {max_attempts} попыток.")
                print("\nУбедитесь, что PostgreSQL запущен.")
                return False
    return False


def drop_database(conn, db_name):
    """Удаляет базу данных если существует."""
    try:
        # Завершаем все активные подключения к базе
        with conn.cursor() as cur:
            cur.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
            """, (db_name,))
        conn.commit()
        
        # DROP DATABASE требует отдельной транзакции
        old_isolation_level = conn.isolation_level
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor() as cur:
                cur.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
            print(f"✓ База данных '{db_name}' удалена (если существовала).")
        finally:
            conn.set_isolation_level(old_isolation_level)
        
        return True
    except Exception as e:
        print(f"✗ Ошибка при удалении базы данных: {e}")
        conn.rollback()
        return False


def create_database(conn, db_name):
    """Создает новую базу данных."""
    try:
        # CREATE DATABASE также требует отдельной транзакции
        old_isolation_level = conn.isolation_level
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor() as cur:
                cur.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✓ База данных '{db_name}' создана.")
        finally:
            conn.set_isolation_level(old_isolation_level)
        
        return True
    except Exception as e:
        print(f"✗ Ошибка при создании базы данных: {e}")
        conn.rollback()
        return False


def run_alembic_upgrade():
    """Запускает alembic upgrade head."""
    print("Применение миграций Alembic...")
    try:
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            cwd=BACKEND_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Миграции успешно применены!")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print("✗ Ошибка при применении миграций:")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("✗ Ошибка: alembic не найден. Установите: pip install alembic")
        return False
    except Exception as e:
        print(f"✗ Ошибка при запуске alembic: {e}")
        return False


def run_alembic_current():
    """Показывает текущую версию миграций."""
    print("\nПроверка статуса миграций...")
    try:
        result = subprocess.run(
            ['alembic', 'current'],
            cwd=BACKEND_DIR,
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print(result.stdout)
        if result.stderr.strip():
            print(result.stderr)
    except Exception as e:
        print(f"✗ Ошибка: {e}")


def main():
    print_separator()
    print("Скрипт пересоздания базы данных и применения миграций")
    print_separator()
    print()
    print(f"Параметры подключения:")
    print(f"  Хост: {DB_HOST}:{DB_PORT}")
    print(f"  Пользователь: {DB_USER}")
    print(f"  База данных: {DB_NAME}")
    print()

    # Ждем доступности PostgreSQL
    if not wait_for_postgres():
        print("\n✗ Не удалось подключиться к PostgreSQL. Выход.")
        sys.exit(1)

    # Подключаемся к базе 'postgres' для операций с другими БД
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname='postgres'
        )
        conn.autocommit = False
        print("✓ Подключение к PostgreSQL установлено.")
    except Exception as e:
        print(f"✗ Ошибка подключения к PostgreSQL: {e}")
        sys.exit(1)

    try:
        # Удаляем старую базу данных
        if not drop_database(conn, DB_NAME):
            print("✗ Не удалось удалить базу данных. Выход.")
            sys.exit(1)
        
        # Создаем новую базу данных
        if not create_database(conn, DB_NAME):
            print("✗ Не удалось создать базу данных. Выход.")
            sys.exit(1)
        
    finally:
        conn.close()
        print("✓ Подключение закрыто.")

    # Применяем миграции
    if not run_alembic_upgrade():
        print("\n✗ Не удалось применить миграции. Выход.")
        sys.exit(1)
    
    # Показываем статус
    run_alembic_current()
    
    print()
    print_separator()
    print("✓ Готово! База данных пересоздана и миграции применены.")
    print_separator()
    print()
    print(f"База данных '{DB_NAME}' готова к использованию.")
    print()
    print("Для создания администратора выполните:")
    print("  cd backend && alembic upgrade head")
    print("  # Затем создайте пользователя через API или скрипт")


if __name__ == '__main__':
    main()
