from fastapi import FastAPI
from app.api import api_router
from app.db.session import Base, engine

app = FastAPI(title="Lab 3 - fuzzy + WS + Celery")
Base.metadata.create_all(bind=engine)

app.include_router(api_router)
