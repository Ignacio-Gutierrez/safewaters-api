from fastapi import FastAPI
from app.api.urls import router

app = FastAPI()

app.include_router(router)