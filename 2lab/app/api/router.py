from fastapi import APIRouter
from app.api import auth
from app.api import search

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(search.router, tags=["search"])
