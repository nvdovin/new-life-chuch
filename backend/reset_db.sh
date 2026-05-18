#!/bin/bash
#
# Скрипт для пересоздания базы данных и применения миграций Alembic
#
# Использование:
#   ./reset_db.sh
#
# Требования:
#   - Установлен PostgreSQL клиент (psql)
#   - Установлен alembic и зависимости проекта
#   - База данных PostgreSQL доступна
#

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Параметры подключения (можно переопределить через переменные окружения)
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-newlife}"

# Переходим в директорию скрипта
cd "$(dirname "$0")"

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}Скрипт пересоздания базы данных и применения миграций${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${YELLOW}Параметры подключения:${NC}"
echo "  Хост: ${DB_HOST}:${DB_PORT}"
echo "  Пользователь: ${DB_USER}"
echo "  База данных: ${DB_NAME}"
echo ""

# Функция для выполнения команд с выводом статуса
run_cmd() {
    local description="$1"
    shift
    echo -e "${YELLOW}Выполнение: ${description}${NC}"
    if ! "$@"; then
        echo -e "${RED}Ошибка при выполнении: ${description}${NC}"
        return 1
    fi
    return 0
}

# Шаг 1: Удаление существующей базы данных
echo -e "${YELLOW}Удаление базы данных '${DB_NAME}' если существует...${NC}"
export PGPASSWORD="${DB_PASSWORD}"
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};" || {
    echo -e "${RED}Не удалось удалить базу данных. Проверьте подключение к PostgreSQL.${NC}"
    exit 1
}

# Шаг 2: Создание новой базы данных
echo -e "${YELLOW}Создание базы данных '${DB_NAME}'...${NC}"
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${DB_NAME};" || {
    echo -e "${RED}Не удалось создать базу данных. Проверьте подключение к PostgreSQL.${NC}"
    exit 1
}

# Шаг 3: Применение миграций Alembic
echo ""
echo -e "${YELLOW}Применение миграций Alembic...${NC}"
alembic upgrade head || {
    echo -e "${RED}Не удалось применить миграции. Проверьте настройки alembic.ini и зависимости.${NC}"
    exit 1
}

# Шаг 4: Проверка статуса миграций
echo ""
echo -e "${YELLOW}Проверка статуса миграций...${NC}"
alembic current || {
    echo -e "${RED}Не удалось получить статус миграций.${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}База данных успешно пересоздана и миграции применены!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}База данных '${DB_NAME}' готова к использованию.${NC}"
