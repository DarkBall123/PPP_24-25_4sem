from fastapi import APIRouter
from .routes_corpus import router as corpus_router
from .routes_search import router as search_router
from .routes_ws import router as ws_router

api_router = APIRouter()
api_router.include_router(corpus_router)
api_router.include_router(search_router)
api_router.include_router(ws_router)
