#!/bin/bash
#
# Скрипт для пересоздания базы данных и применения миграций Alembic
# Работает через Docker Compose
#
# Использование:
#   ./reset_db.sh
#   # или из корня проекта:
#   cd /workspace && ./backend/reset_db.sh
#
# Требования:
#   - Установлен Docker и Docker Compose
#   - Контейнеры должны быть запущены (docker compose up -d)
#

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Параметры (можно переопределить через переменные окружения)
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
DB_NAME="${DB_NAME:-newlife}"
COMPOSE_PROJECT_DIR="${COMPOSE_PROJECT_DIR:-/workspace}"

# Переходим в директорию проекта
cd "${COMPOSE_PROJECT_DIR}"

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}Скрипт пересоздания базы данных и применения миграций${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${YELLOW}Параметры:${NC}"
echo "  База данных: ${DB_NAME}"
echo "  Пользователь: ${DB_USER}"
echo "  Проект: ${COMPOSE_PROJECT_DIR}"
echo ""

# Проверка наличия docker compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Ошибка: Docker не найден. Установите Docker.${NC}"
    exit 1
fi

# Проверка запущенности контейнеров
echo -e "${YELLOW}Проверка состояния контейнеров...${NC}"
if ! docker compose ps postgres | grep -q "Up"; then
    echo -e "${YELLOW}Контейнер postgres не запущен. Запускаем сервисы...${NC}"
    docker compose up -d postgres redis
    echo -e "${YELLOW}Ожидание готовности PostgreSQL (30 секунд)...${NC}"
    sleep 30
fi

# Шаг 1: Удаление и создание базы данных через exec в контейнере
echo ""
echo -e "${YELLOW}Удаление базы данных '${DB_NAME}' если существует...${NC}"
docker compose exec -T postgres psql -U "${DB_USER}" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1 && \
    docker compose exec -T postgres psql -U "${DB_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};" || \
    echo -e "${YELLOW}База данных '${DB_NAME}' не существовала, пропускаем удаление.${NC}"

echo -e "${YELLOW}Создание базы данных '${DB_NAME}'...${NC}"
docker compose exec -T postgres psql -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${DB_NAME};" || {
    echo -e "${RED}Не удалось создать базу данных.${NC}"
    exit 1
}

# Шаг 2: Применение миграций Alembic в контейнере backend
echo ""
echo -e "${YELLOW}Применение миграций Alembic...${NC}"
docker compose exec -T backend alembic upgrade head || {
    echo -e "${RED}Не удалось применить миграции. Проверьте логи backend.${NC}"
    exit 1
}

# Шаг 3: Проверка статуса миграций
echo ""
echo -e "${YELLOW}Проверка статуса миграций...${NC}"
docker compose exec -T backend alembic current || {
    echo -e "${RED}Не удалось получить статус миграций.${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}База данных успешно пересоздана и миграции применены!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}База данных '${DB_NAME}' готова к использованию.${NC}"
echo ""
echo -e "${YELLOW}Примечание: Для создания администратора выполните:${NC}"
echo -e "  docker compose exec backend python -m app.scripts.create_admin"
