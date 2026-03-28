import asyncio
import argparse
import logging
from datetime import datetime
from pathlib import Path
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


async def run(query: str):

    log.info("建立 pipeline")
    pipeline = build_pipeline()
    session_service = InMemorySessionService()

    log.info("建立 session，query=%s", query)
    session = await session_service.create_session(
        app_name=pipeline.name,
        user_id="news_user",
        state={"query": query},
    )

    log.info("建立 runner")
    runner = Runner(
        agent=pipeline,
        app_name=pipeline.name,
        session_service=session_service,
    )

    log.info("開始執行 pipeline")
    report = None
    async for event in runner.run_async(
        user_id="news_user",
        session_id=session.id,
        new_message=Content(
            parts=[Part(text=query)], role="user"
        ),
    ):
        if event.is_final_response():
            log.info("agent [%s] 完成", event.author)
            report = event.content.parts[0].text
        else:
            log.info("agent [%s] 執行中", event.author)

    if report:
        log.info("pipeline 完成，寫入報告")
        print("\n" + "="*50)
        print(report)

        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(__file__).parent / "reports" / f"{date_str}_{query}.md"
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        log.info("報告已儲存：%s", output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="內容生成")
    parser.add_argument("--query", type=str, help="")
    args = parser.parse_args()
    asyncio.run(run(args.query))
