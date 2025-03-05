-- Этот скрипт выполняется при инициализации Docker-контейнера с PostgreSQL, 
-- чтобы автоматически настроить базы данных и права доступа.

-- Создание основной БД
CREATE DATABASE fastapi_project_db;

-- Создание тестовой БД. (для запуска тестов)
CREATE DATABASE fastapi_project_test_db;

-- Предоставление всех привилегий пользователю "postgres_user" на основную БД.
GRANT ALL PRIVILEGES ON DATABASE fastapi_project_db TO "postgres_user";

-- Предоставление всех привилегий пользователю "postgres_user" на тестовую БД.
GRANT ALL PRIVILEGES ON DATABASE fastapi_project_test_db TO "postgres_user";