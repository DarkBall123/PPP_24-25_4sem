import asyncio, json, uuid, httpx, websockets

API = "http://127.0.0.1:8000"
WS  = "ws://127.0.0.1:8000/ws"
UID = 42

async def listen_and_trigger():
    async with websockets.connect(f"{WS}/{UID}") as ws:
        print("WS connected, waiting…")
        # параллельно создаём корпус + задачу
        asyncio.get_event_loop().create_task(trigger())
        while True:
            data = json.loads(await ws.recv())
            print("WS-EVENT:", data)
            if data.get("status") == "COMPLETED":
                break

async def trigger():
    async with httpx.AsyncClient() as c:
        corpus = {
            "name": f"demo_{uuid.uuid4().hex[:6]}",
            "text": "example sample temple ample apple maple"
        }
        corpus_id = (await c.post(f"{API}/corpuses/", json=corpus)).json()["corpus_id"]
        await c.post(f"{API}/search/", params={
            "user_id": UID, "corpus_id": corpus_id, "word": "example", "algorithm": "levenshtein"
        })

asyncio.run(listen_and_trigger())
