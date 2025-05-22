from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.corpus import Corpus
from app.tasks import fuzzy_search_task

router = APIRouter(prefix="/search", tags=["search"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def start_search(user_id: int, corpus_id: int, word: str, algorithm: str = "levenshtein", db: Session = Depends(get_db)):
    corpus = db.query(Corpus).filter_by(id=corpus_id).first()
    if not corpus:
        raise HTTPException(404, "Corpus not found")
    task = fuzzy_search_task.delay(user_id, word, algorithm, corpus.text.split())
    return {"task_id": task.id}
