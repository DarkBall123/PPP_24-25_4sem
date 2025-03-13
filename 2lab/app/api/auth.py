from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.cruds.user_crud import get_user_by_email, create_user
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/sign-up/", response_model=UserRead)
def sign_up(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.
    1) Проверяем, нет ли уже такого email.
    2) Создаём пользователя.
    3) Возвращаем данные пользователя (id, email).
    """
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    user = create_user(db, user_data)
    return user  # Pydantic сам превратит в UserRead

@router.post("/login/", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Авторизация пользователя.
    Принимает form-data: username, password. (username = email)
    Возвращает токен.
    """
    # Пытаемся найти пользователя по email (form_data.username)
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token)

@router.get("/users/me/", response_model=UserRead)
def get_me(current_user: UserRead = Depends(get_current_user)):
    """
    Возвращает данные текущего авторизованного пользователя.
    """
    return current_user
