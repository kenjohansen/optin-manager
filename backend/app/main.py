from fastapi import FastAPI
from .core.config import settings

app = FastAPI(title="OptIn Manager API")

@app.get("/health")
def health_check():
    return {"status": "ok"}
