from core.mcp.utility import Collection


async def get_topic(source: str) -> str:
    """
    爬取指定來源的最新文章標題與連結。
    根據使用者問題的性質決定要抓哪個來源：
    - 'bbc'   國際時事新聞
    - 'cnyes' 台股財經新聞
    可以呼叫多次來同時取得多個來源的標題。
    """
    collection = Collection(source)
    await collection.openBrowser()
    await collection.openPage()
    await collection.accessSite()
    await collection.parseArticle()
    await collection.closePage()
    await collection.closeBrowser()
    result = []
    for _, value in collection.article.items():
        result.append(f"標題：{value['title']}\n連結：{value['link']}")
    return "\n\n".join(result)


async def get_article(source: str, link: str) -> str:
    """
    根據連結抓取單篇文章的完整內文。
    先呼叫 get_topic 取得標題列表，從中挑選相關的文章後再呼叫此 tool。
    - source: 'bbc' 或 'cnyes'，需與 get_topic 的來源一致
    - link:   文章連結，來自 get_topic 的回傳結果
    """
    collection = Collection(source)
    return await collection.getContent(link)
