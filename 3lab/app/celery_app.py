from celery import Celery
from app.core.embedded_redis import shim
import platform

REDIS_URL = f"redis://localhost:{shim.port}/0"

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"],
)

if platform.system() == "Windows":
    celery_app.conf.worker_pool = "solo"

celery_app.conf.update(task_track_started=True)

celery_app.redis_server = shim.redis
redis_server            = shim.redis
