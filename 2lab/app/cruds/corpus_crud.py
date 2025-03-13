from sqlalchemy.orm import Session
from app.models.corpus import Corpus
from app.schemas.corpus import CorpusCreate

def create_corpus(db: Session, corpus_data: CorpusCreate) -> Corpus:
    """
    Создаём новый корпус в БД.
    """
    db_corpus = Corpus(
        name=corpus_data.name,
        text=corpus_data.text
    )
    db.add(db_corpus)
    db.commit()
    db.refresh(db_corpus)
    return db_corpus

def get_corpus_by_id(db: Session, corpus_id: int) -> Corpus | None:
    """
    Находим корпус по ID (или None, если не найден).
    """
    return db.query(Corpus).filter(Corpus.id == corpus_id).first()

def get_all_corpuses(db: Session) -> list[Corpus]:
    """
    Возвращает список всех корпусов (объекты SQLAlchemy).
    """
    return db.query(Corpus).all()
