# app/models/__init__.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# импортируем все модели, чтобы Alembic видел их metadata
from app.models.user import User
from app.models.corpus import Corpus
