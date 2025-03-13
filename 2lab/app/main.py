from fastapi import FastAPI
from app.api.router import api_router
from app.db.database import engine
from app.models import Base

def create_tables():
    """Создаёт таблицы в БД (если их нет)."""
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fuzzy Search Project")

# подключаем главный роутер
app.include_router(api_router)

@app.on_event("startup")
def on_startup():
    # на старте приложения создадим таблицы
    create_tables()
