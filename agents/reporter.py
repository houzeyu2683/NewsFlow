from pathlib import Path
from google.adk.agents import Agent
from config import MODEL

PROMPT = (Path(__file__).parent.parent / "prompts" / "reporter.md").read_text()


def create_reporter_agent() -> Agent:
    """整合所有文章摘要，產出最終報告存入 state["report_final"]"""
    return Agent(
        name="news_reporter",
        model=MODEL,
        description="將多篇文章摘要整合成一份結構化的每日新聞報告。",
        instruction=PROMPT,
        output_key="report_final",
    )
