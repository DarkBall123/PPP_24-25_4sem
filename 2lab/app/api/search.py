from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time

from app.api.deps import get_db
from app.cruds.corpus_crud import create_corpus, get_all_corpuses, get_corpus_by_id
from app.schemas.corpus import CorpusCreate, CorpusRead
from app.services.fuzzy_search import perform_fuzzy_search

router = APIRouter()

@router.post("/upload_corpus", response_model=dict)
def upload_corpus(corpus_data: CorpusCreate, db: Session = Depends(get_db)):
    """
    Создаёт запись о корпусе в БД.
    Возвращает {"corpus_id": <id>, "message": "Corpus uploaded successfully"}
    """
    # name=unique
    db_corpus = create_corpus(db, corpus_data)
    return {
        "corpus_id": db_corpus.id,
        "message": "Corpus uploaded successfully"
    }

@router.get("/corpuses", response_model=dict)
def get_corpuses(db: Session = Depends(get_db)):
    """
    Возвращаем список корпусов c идентификаторами.
    Пример ответа:
    {
      "corpuses": [
        {"id": 1, "name": "example_corpus"},
        {"id": 2, "name": "another_corpus"}
      ]
    }
    """
    corpuses_db = get_all_corpuses(db)

    result = [{"id": c.id, "name": c.name} for c in corpuses_db]
    return {"corpuses": result}

@router.post("/search_algorithm", response_model=dict)
def search_algorithm(
    word: str,
    algorithm: str,
    corpus_id: int,
    db: Session = Depends(get_db)
):
    """
    Запускает нечеткий поиск 'word' в корпусе 'corpus_id' с помощью 'algorithm' ("levenshtein" или "damerau").
    Возвращает execution_time + results (список слов и distance).
    """
    db_corpus = get_corpus_by_id(db, corpus_id)
    if not db_corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    start_time = time.time()
    results = perform_fuzzy_search(word, db_corpus.text, algorithm)
    end_time = time.time()

    execution_time = end_time - start_time

    # возвращ. все результаты
    results_to_return = [
        {"word": r[0], "distance": r[1]} for r in results
    ]

    return {
        "execution_time": round(execution_time, 4),
        "results": results_to_return
    }
