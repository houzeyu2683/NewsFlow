import uuid
import json
import logging
from pathlib import Path

import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

app = FastAPI(title="Daily News API")

REDIS_URL = "redis://redis:6379"
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)


class ReportRequest(BaseModel):
    query: str


@app.post("/reports")
async def create_report(req: ReportRequest):
    job_id = str(uuid.uuid4())
    await redis_client.hset(f"job:{job_id}", mapping={"status": "pending", "query": req.query})
    await redis_client.lpush("task_queue", json.dumps({"job_id": job_id, "query": req.query}))
    log.info("job %s 已推入 queue，query=%s", job_id, req.query)
    return {"job_id": job_id, "status": "pending"}


@app.get("/reports/{job_id}")
async def get_report(job_id: str):
    data = await redis_client.hgetall(f"job:{job_id}")
    if not data:
        raise HTTPException(status_code=404, detail="job not found")
    return data


@app.get("/reports")
async def list_reports():
    reports_dir = Path(__file__).parent / "reports"
    files = sorted(reports_dir.glob("*.md"), reverse=True)
    return [{"file": f.name, "size": f.stat().st_size} for f in files]
