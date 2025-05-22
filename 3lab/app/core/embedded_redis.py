"""
Встроенный Redis на фиксированном порту (6380 по умолчанию).
Linux/macOS -> redislite,  Windows -> скачиваем tporadowski-порт.
"""

import os, platform, subprocess, tempfile, time, zipfile, urllib.request, atexit
from pathlib import Path
from urllib.error import HTTPError

PORT = int(os.getenv("REDIS_PORT", "6380"))

GITHUB = "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
SFNET  = "https://downloads.sourceforge.net/project/redis-for-windows.mirror/v5.0.14.1/Redis-x64-5.0.14.1.zip"

class _Shim:
    def __init__(self):
        if platform.system() != "Windows":
            from redislite import Redis               # type: ignore
            self.redis = Redis(port=PORT)
            self.port  = PORT
            return

        self.port  = PORT
        self._proc = self._start_win_redis()
        self.redis = self._wait_ready()
        atexit.register(self._cleanup)

    # ---------- helpers ----------
    def _download(self, dest: Path):
        for url in (GITHUB, SFNET):
            try:
                print("💾  Downloading", url.split("/")[-1])
                urllib.request.urlretrieve(url, dest)
                return
            except HTTPError as e:
                print("⚠️ ", e.status, "from", url, "-> retry")
        raise RuntimeError("Cannot fetch redis binary")

    def _start_win_redis(self) -> subprocess.Popen:
        cache = Path(tempfile.gettempdir()) / "embedded_redis_win"
        exe   = cache / "redis-server.exe"
        if not exe.exists():
            cache.mkdir(exist_ok=True)
            zip_path = cache / "redis.zip"
            self._download(zip_path)
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(cache)
            zip_path.unlink()
            exe = next(cache.rglob("redis-server.exe"))
            exe.rename(cache / "redis-server.exe")
            exe = cache / "redis-server.exe"

        return subprocess.Popen(
            [str(exe), "--port", str(self.port), "--save", "", "--appendonly", "no"],
            cwd=exe.parent,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

    def _wait_ready(self):
        import redis
        r = redis.Redis(host="127.0.0.1", port=self.port, decode_responses=True)
        for _ in range(20):          # ≤10 с
            try:
                r.ping(); return r
            except redis.ConnectionError:
                time.sleep(0.5)
        raise RuntimeError("Redis not responding")

    def _cleanup(self):
        if getattr(self, "_proc", None) and self._proc.poll() is None:
            self._proc.terminate()

shim = _Shim()      # экспорт для всех
