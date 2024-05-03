from fastapi import FastAPI

from src.api.router import router

app = FastAPI(
    title="Twitter API",
)

app.include_router(router)
