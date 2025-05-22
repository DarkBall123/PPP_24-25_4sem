import os
from pydantic import BaseModel
from functools import lru_cache

class _Settings(BaseModel):
    secret_key: str = os.getenv("SECRET_KEY", "bad_key_don_t_use_in_prod")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

@lru_cache
def get_settings() -> _Settings:
    return _Settings()