import json, time
from celery.utils.log import get_task_logger
from app.celery_app import celery_app, redis_server
from app.services import fuzzy
from app.websocket.events import Status

log = get_task_logger(__name__)

@celery_app.task(bind=True, name="app.tasks.fuzzy_search_task")
def fuzzy_search_task(self, user_id: int, word: str, algorithm: str, corpus: list[str]):
    t0 = time.perf_counter()
    total = len(corpus)
    results = []

    for idx, candidate in enumerate(corpus, 1):
        dist = (fuzzy.levenshtein if algorithm == "levenshtein" else fuzzy.ngram)(word, candidate)
        results.append({"word": candidate, "distance": dist})

        if idx % max(1, total // 10) == 0:   # каждые ~10 %
            redis_server.publish(
                "ws_notifications",
                json.dumps({
                    "user_id": user_id,
                    "status":  Status.progress,
                    "task_id": self.request.id,
                    "progress": int(idx / total * 100),
                    "current_word": f"{idx}/{total}"
                })
            )

    exec_time = round(time.perf_counter() - t0, 4)
    payload = {
        "user_id":       user_id,
        "status":        Status.completed,
        "task_id":       self.request.id,
        "execution_time": exec_time,
        "results":       sorted(results, key=lambda x: x["distance"])[:10],
    }
    redis_server.publish("ws_notifications", json.dumps(payload))
    return payload
