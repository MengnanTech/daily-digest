"""正文抓取模块 - 用于补充 HN 等只有链接的数据源"""
import asyncio
import httpx


async def _fetch_one(client: httpx.AsyncClient, url: str) -> str:
    """抓取单个 URL 的正文内容"""
    try:
        r = await client.get(
            url,
            timeout=10,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
        )
        r.raise_for_status()

        # 使用 readability 提取正文
        from readability import Document
        doc = Document(r.text)
        clean_html = doc.summary()

        # HTML 转纯文本
        from bs4 import BeautifulSoup
        text = BeautifulSoup(clean_html, "html.parser").get_text(separator=" ")
        # 清理多余空白
        text = " ".join(text.split())
        return text[:3000]
    except Exception:
        return ""


async def fetch_content_for_articles(articles: list[dict], max_concurrent: int = 5) -> list[dict]:
    """
    为没有 content 的文章补充正文（主要是 HN 文章）
    使用信号量限制并发数，避免过多请求
    """
    sem = asyncio.Semaphore(max_concurrent)

    async def _fetch_with_sem(client: httpx.AsyncClient, article: dict):
        if article.get("content") and len(article["content"]) > 50:
            return  # 已有内容，跳过

        async with sem:
            content = await _fetch_one(client, article["url"])
            if content:
                article["content"] = content

    async with httpx.AsyncClient() as client:
        tasks = [_fetch_with_sem(client, a) for a in articles]
        await asyncio.gather(*tasks)

    return articles
