import logging
from google.adk.tools import ToolContext

log = logging.getLogger(__name__)


def save_selected_urls(articles: list, tool_context: ToolContext) -> dict:
    """Saves the selected article URLs and sources into state so parallel readers can access them.

    Args:
        articles: A list of dicts with 'url' and 'source' keys (max 3).

    Returns:
        A dictionary confirming how many articles were saved.
    """
    articles = articles[:3]
    for i, article in enumerate(articles):
        log.info("儲存 url_%d = %s (source=%s)", i, article["url"], article["source"])
        tool_context.state[f"url_{i}"] = article["url"]
        tool_context.state[f"source_{i}"] = article["source"]
    tool_context.state["n_selected"] = len(articles)
    log.info("共儲存 %d 篇文章", len(articles))
    return {"status": "success", "saved": len(articles)}
