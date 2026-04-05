import asyncio
from google.adk.agents import Agent
from core.config import MODEL, PROMPTS_DIR
from core.tools.scraper import get_article

PROMPT = (PROMPTS_DIR / "reader.md").read_text()


async def _sleep_before_run(callback_context):
    await asyncio.sleep(10)


def create_reader_agent(index: int) -> Agent:
    """閱讀單篇文章，摘要存入 state[f"article_{index}"]"""
    return Agent(
        name=f"article_reader_{index}",
        model=MODEL,
        description=f"閱讀並摘要第 {index} 篇文章。",
        instruction=PROMPT + f"\n\n- source: {{source_{index}}}\n- link: {{url_{index}}}",
        tools=[get_article],
        output_key=f"article_{index}",
        before_agent_callback=_sleep_before_run,
    )
