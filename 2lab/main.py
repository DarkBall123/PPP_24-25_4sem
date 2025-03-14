import subprocess
import uvicorn
def run_migrations():
    print("alembic")
    subprocess.run(["alembic", "upgrade", "head"])

def run_server():
    print("uvicorn")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    run_migrations()
    run_server()
