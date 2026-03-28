import mcp.server.fastmcp
import utility

server = mcp.server.fastmcp.FastMCP("新聞爬蟲")


@server.tool()
async def getTopic(source: str) -> str:
    """
    爬取指定來源的最新文章標題與連結。
    根據使用者問題的性質決定要抓哪個來源：
    - 'bbc'   國際時事新聞
    - 'cnyes' 台股財經新聞
    可以呼叫多次來同時取得多個來源的標題。
    """
    collection = utility.Collection(source)
    await collection.openBrowser()
    await collection.openPage()
    await collection.accessSite()
    await collection.parseArticle()
    await collection.closePage()
    await collection.closeBrowser()
    result = []
    iteration = collection.article.items()
    for _, value in iteration:
        block = f"標題：{value['title']}\n連結：{value['link']}"
        result += [block]
        continue
    _ = iteration
    return("\n\n".join(result))


@server.tool()
async def getArticle(source: str, link: str) -> str:
    """
    根據連結抓取單篇文章的完整內文。
    先呼叫 getTopic 取得標題列表，從中挑選相關的文章後再呼叫此 tool。
    - source: 'bbc' 或 'cnyes'，需與 getTopic 的來源一致
    - link:   文章連結，來自 getTopic 的回傳結果
    """
    collection = utility.Collection(source)
    content = await collection.getContent(link)
    return(content)


if __name__ == "__main__":
    server.run()
