import logging
from google.adk.agents import SequentialAgent, ParallelAgent
from config import N_ARTICLES
from agents.fetcher import create_bbc_fetcher_agent, create_cnyes_fetcher_agent
from agents.filter import create_filter_agent
from agents.reader import create_reader_agent
from agents.reporter import create_reporter_agent

log = logging.getLogger(__name__)


def build_pipeline() -> SequentialAgent:
    """
    組裝每日新聞 pipeline：
      1. Parallel Fetchers — 同時抓 BBC + 鉅亨網頭條
      2. Filter            — 根據 query 篩選 3 篇，寫入 state["url_0~2"]
      3. Parallel Readers  — 同時閱讀 3 篇文章，寫入 state["article_0~2"]
      4. Reporter          — 整合報告
    """
    log.info("建立 bbc / cnyes fetcher agent")
    parallel_fetchers = ParallelAgent(
        name="parallel_fetchers",
        sub_agents=[create_bbc_fetcher_agent(), create_cnyes_fetcher_agent()],
    )

    log.info("建立 filter agent")
    filter_agent = create_filter_agent()

    log.info("建立 %d 個 reader agent", N_ARTICLES)
    parallel_readers = SequentialAgent(
        name="sequential_article_readers",
        sub_agents=[create_reader_agent(i) for i in range(N_ARTICLES)],
    )

    log.info("建立 reporter agent")
    reporter = create_reporter_agent()

    log.info("組裝 SequentialAgent pipeline")
    return SequentialAgent(
        name="daily_news_pipeline",
        sub_agents=[parallel_fetchers, filter_agent, parallel_readers, reporter],
    )
