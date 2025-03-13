from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Generator

from app.core.config import settings
from app.core.security import verify_password
from app.db.database import SessionLocal
from app.cruds.user_crud import get_user_by_id
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # название эндпоинта, где получаем токен

def get_db() -> Generator:
    """
    Каждое обращение к эндпоинту получает новую сессию.
    В конце запроса — сессия закрывается.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    Достаем пользователя из токена.
    Если токен неправильный, кидаем 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_id(db, int(user_id))
    if not user:
        raise credentials_exception
    return user
