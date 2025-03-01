from fastapi import FastAPI, status, Response
from fastapi.responses import ORJSONResponse
from icecream import ic

from routers import v1_router


# Само приложение fastApi. именно оно запускается сервером и служит точкой входа
# в нем можно указать разные параметры для сваггера и для ручек (эндпоинтов).
app = FastAPI(
    title="Book Library App",
    description="Учебное приложение для MTS Shad",
    version="0.0.1",
    default_response_class= ORJSONResponse,
    responses={404:{"description":"Not found!"}} # Подключаем быстрый сериализатор
    )

app.include_router(v1_router)


# Для запуска:
#  uvicorn main:app --reload