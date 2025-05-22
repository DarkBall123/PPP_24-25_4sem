from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.corpus import Corpus

router = APIRouter(prefix="/corpuses", tags=["Corpus"])

class CorpusIn(BaseModel):
    name: str
    text: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def upload_corpus(payload: CorpusIn, db: Session = Depends(get_db)):
    corp = Corpus(name=payload.name, text=payload.text)
    db.add(corp)
    db.commit()
    db.refresh(corp)
    return {"corpus_id": corp.id, "message": "ok"}

@router.get("/")
def list_corpuses(db: Session = Depends(get_db)):
    rows = db.query(Corpus).all()
    return {"corpuses": [{"id": c.id, "name": c.name} for c in rows]}
