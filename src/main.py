from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.config import static_dir
from .database import (
    async_session,
    drop_db_and_tables,
    create_db_and_tables,
    create_db_data,
)
from src.api.models import User
from src.api.router import router
from src.api.service import get_user_by_api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    await drop_db_and_tables()
    await create_db_and_tables()
    await create_db_data()
    yield
    await drop_db_and_tables()


app: FastAPI = FastAPI(title="Twitter API", lifespan=lifespan)
app.include_router(router)

# app.mount("/static", StaticFiles(directory=static_dir), name="static")
# templates: Jinja2Templates = Jinja2Templates(directory=f"{static_dir}/templates")
#
#
# @app.middleware("http")
# async def check_user_api_key_middleware(request: Request, call_next):
#     """
#     Middleware для проверки наличия api-key в заголовках запроса и базе данных
#     :param request: Запрос
#     :param call_next: Передача запроса следующему обработчику
#     :return: Ответ
#     """
#     api_key: str | None = request.headers.get("api-key")
#
#     if api_key is not None:
#         async with async_session() as session:
#             user: User | None = await get_user_by_api_key(session, api_key)
#             if user is None:
#                 raise HTTPException(status_code=401, detail="Invalid API Key")
#
#     response: Response = await call_next(request)
#     return response
#
#
# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     """
#     Эндпоинт для отдачи статики
#     :param request: Запрос
#     :return: Шаблон
#     """
#     return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
