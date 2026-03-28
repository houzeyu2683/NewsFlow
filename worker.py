import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

import redis.asyncio as aioredis
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from pipelines.daily_news import build_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

REDIS_URL = "redis://redis:6379"
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)


async def run_pipeline(job_id: str, query: str):
    try:
        await redis_client.hset(f"job:{job_id}", mapping={"status": "running"})

        pipeline = build_pipeline()
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name=pipeline.name,
            user_id="news_user",
            state={"query": query},
        )
        runner = Runner(agent=pipeline, app_name=pipeline.name, session_service=session_service)

        report = None
        async for event in runner.run_async(
            user_id="news_user",
            session_id=session.id,
            new_message=Content(parts=[Part(text=query)], role="user"),
        ):
            if event.is_final_response():
                report = event.content.parts[0].text

        if report:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(__file__).parent / "reports" / f"{date_str}_{query}.md"
            output_path.parent.mkdir(exist_ok=True)
            output_path.write_text(report, encoding="utf-8")
            await redis_client.hset(f"job:{job_id}", mapping={
                "status": "done",
                "report": report,
                "file": str(output_path),
            })
        else:
            await redis_client.hset(f"job:{job_id}", mapping={"status": "failed", "error": "no report generated"})

    except Exception as e:
        log.exception("pipeline failed for job %s", job_id)
        await redis_client.hset(f"job:{job_id}", mapping={"status": "failed", "error": str(e)})


async def main():
    log.info("worker 啟動，監聽 task_queue")
    while True:
        _, raw = await redis_client.brpop("task_queue")
        task = json.loads(raw)
        log.info("收到任務 job_id=%s query=%s", task["job_id"], task["query"])
        await run_pipeline(task["job_id"], task["query"])


if __name__ == "__main__":
    asyncio.run(main())
