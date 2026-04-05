from google.adk.agents import Agent
from core.config import MODEL, PROMPTS_DIR
from core.tools.scraper import get_topic

PROMPT_BBC = (PROMPTS_DIR / "fetcher_bbc.md").read_text()
PROMPT_CNYES = (PROMPTS_DIR / "fetcher_cnyes.md").read_text()


def create_bbc_fetcher_agent() -> Agent:
    """抓取 BBC 頭條，輸出 JSON 清單存入 state["bbc_headlines"]"""
    return Agent(
        name="bbc_fetcher",
        model=MODEL,
        description="抓取 BBC 中文最新頭條。",
        instruction=PROMPT_BBC,
        tools=[get_topic],
        output_key="bbc_headlines",
    )


def create_cnyes_fetcher_agent() -> Agent:
    """抓取鉅亨網頭條，輸出 JSON 清單存入 state["cnyes_headlines"]"""
    return Agent(
        name="cnyes_fetcher",
        model=MODEL,
        description="抓取鉅亨網最新台股財經頭條。",
        instruction=PROMPT_CNYES,
        tools=[get_topic],
        output_key="cnyes_headlines",
    )
