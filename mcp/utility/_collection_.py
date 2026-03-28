# from playwright.async_api import async_playwright, Browser as PlaywrightBrowser
import playwright.async_api
import asyncio
import datetime
import time
import json
import pathlib
import httpx
import bs4
# CHROMIUM_PATH = "/usr/bin/chromium"


class Collection:

    def __init__(self, target: str) -> None:
        self.target = target
        return

    async def openBrowser(self) -> bool:
        self.engine = await playwright.async_api.async_playwright().start()
        self.browser = await self.engine.chromium.launch(
            headless=True,
        )
        return(True)

    async def openPage(self) -> bool:
        browser = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
        self.page = await browser.new_page()
        return(True)

    async def closePage(self) -> bool:
        if(self.page): await self.page.close()
        return(True)
    
    async def closeBrowser(self) -> bool:
        if(self.browser): await self.browser.close()
        if(self.engine): await self.engine.stop()
        return(True)

    async def saveScreen(self, path: str) -> bool:
        await self.page.screenshot(path=path)
        return(True)
    
    async def accessSite(self) -> bool:
        link = self.supplement.get(self.target)
        await self.page.goto(link, wait_until="domcontentloaded")
        return(True)

    async def parseArticle(self) -> bool:
        article = {}
        if(self.target=='cnyes'):
            await self.page.wait_for_selector(
                'div[class="infinite-scroll-component "] li'
                # 'div[class="carousel__body__item"]'
            )
            tree = self.page.locator(
                'div[class="infinite-scroll-component "] li'
                # 'div[class="carousel__body__item"]'
            )
            length = await tree.count()
            iteration = range(5)
            for index in iteration:
                # node = tree.nth(index).locator('div p time').nth(0)
                # date = await node.inner_text()
                node = tree.nth(index).locator('div a').nth(0)
                title = await node.inner_text()
                pattern = await node.get_attribute('href')
                number = pattern.split('/').pop()
                link = f"https://news.cnyes.com{pattern}"
                # content = await self.getContent(link)
                item = {
                    'title': title,
                    'link': link,
                    # 'content': content
                }
                article.update({number: item})
                continue
            _ = iteration
            self.article = article
            return(True)
        assert self.target=='bbc'
        await self.page.wait_for_selector(
            'div[data-testid="hierarchical-grid"] ul[role="list"]'
        )
        tree = self.page.locator(
            'div[data-testid="hierarchical-grid"] ul[role="list"]'
        ).nth(0).locator('li')
        length = await tree.count()
        iteration = range(length)
        for index in iteration:
            node = tree.nth(index)
            text = await node.inner_text()
            link = await node.locator("h3 a").get_attribute("href")
            number = str(link).split('/')[-2]
            title, _ = str(text).rsplit("\n", 1)
            # content = await self.getContent(link)
            item = {
                'title': title,
                # 'date': date,
                'link': link,
                # 'content': content
            }
            article.update({number: item})
            continue
        _ = iteration
        self.article = article
        return(True)

    async def getContent(self, link: str) -> str:
        if(self.target=='cnyes'):
            content = []
            async with httpx.AsyncClient() as client:
                response = await client.get(link)
                pass
            context = bs4.BeautifulSoup(response.text, 'html.parser')
            iteration = context.select('main[id="article-container"] section')
            for node in iteration:
                text = node.get_text()
                content += [text]
                continue
            _ = iteration
            content = "\n".join(content)
            time.sleep(1)
            return(content)
        assert self.target=='bbc'
        content = []
        async with httpx.AsyncClient() as client:
            response = await client.get(link)
            pass
        context = bs4.BeautifulSoup(response.text, 'html.parser')
        iteration = context.select('main[role="main"] > div[dir="ltr"]')
        for node in iteration:
            text = node.get_text()
            content += [text]
            continue
        _ = iteration
        content = "\n".join(content)
        time.sleep(1)
        return(content)

    async def saveArticle(self) -> bool:
        folder = pathlib.Path(".data/") / self.target
        folder.mkdir(parents=True, exist_ok=True)
        iteration = self.article.items()
        for key, value in iteration:
            path = folder / f"{key}.json"
            path.write_text(
                json.dumps(value, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            continue
        _ = iteration
        return(True)

    supplement = {
        "cnyes": 'https://news.cnyes.com/news/cat/headline',
        "bbc": "https://www.bbc.com/zhongwen/trad"
    }
    pass

