"""Production-ready FastAPI agent for the Day 14 final project."""
import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from .auth import verify_api_key
from .cost_guard import check_budget, record_cost
from .rate_limiter import check_rate_limit
from .redis_client import redis_healthy
from utils.mock_llm import ask as llm_ask

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({"ts": datetime.now(timezone.utc).isoformat(),
                           "lvl": record.levelname,
                           "event": record.getMessage()}, ensure_ascii=False)

logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("startup")
    yield
    logger.info("shutdown")

app = FastAPI(title="Production AI Agent", lifespan=lifespan)

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    user_id: str | None = Field(default=None, max_length=200)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    if not redis_healthy():
        raise HTTPException(status_code=503, detail="Redis is not ready")
    return {"status": "ready"}

@app.post("/ask")
def ask(body: AskRequest, api_key: str = Depends(verify_api_key)):
    started = time.perf_counter()
    check_rate_limit(api_key)
    check_budget()
    answer = llm_ask(body.question)
    cost = record_cost(len(body.question.split()), len(answer.split()))
    logger.info(json.dumps({"event": "request", "path": "/ask", "status": 200,
                            "ms": round((time.perf_counter() - started) * 1000, 2),
                            "cost_usd": cost}))
    return {"question": body.question, "answer": answer}

