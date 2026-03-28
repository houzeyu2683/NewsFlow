from pathlib import Path
from google.adk.agents import Agent
from config import MODEL
from tools.url_saver import save_selected_urls

PROMPT = (Path(__file__).parent.parent / "prompts" / "filter.md").read_text()


def create_filter_agent() -> Agent:
    """從標題清單中篩選最值得閱讀的 3 篇，URL 存入 state["url_0~2"]"""
    return Agent(
        name="news_filter",
        model=MODEL,
        description="從新聞清單中篩選最相關、最值得深讀的文章。",
        instruction=PROMPT,
        tools=[save_selected_urls],
    )
