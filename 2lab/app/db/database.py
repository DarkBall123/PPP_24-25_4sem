from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# формируем URL к базе данных SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{settings.DB_NAME}"
# избегаем ошибок многопоточности
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# создаём фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
