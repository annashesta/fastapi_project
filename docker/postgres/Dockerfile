# Используем официальный образ PostgreSQL из Docker Hub.
# Образ содержит предустановленную СУБД PostgreSQL.
FROM postgres:latest

# Копируем SQL-скрипт для создания баз данных и настройки прав доступа
# в специальную директорию `/docker-entrypoint-initdb.d/`.
# Файлы, помещённые в эту директорию, автоматически выполняются
# при инициализации контейнера PostgreSQL.
COPY ./docker/postgres/create_databases.sql /docker-entrypoint-initdb.d/create_databases.sql