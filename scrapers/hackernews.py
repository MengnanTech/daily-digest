"""Hacker News 抓取器 - 使用官方 Firebase API（完全免费）"""
import asyncio
import httpx

HN_API = "https://hacker-news.firebaseio.com/v0"


async def _fetch_item(client: httpx.AsyncClient, item_id: int) -> dict | None:
    try:
        r = await client.get(f"{HN_API}/item/{item_id}.json", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


async def fetch_hackernews(top_n: int = 30) -> list[dict]:
    """抓取 Hacker News Top Stories"""
    async with httpx.AsyncClient() as client:
        # 获取 top stories IDs
        r = await client.get(f"{HN_API}/topstories.json", timeout=10)
        r.raise_for_status()
        ids = r.json()[:top_n]

        # 并行获取每条 story 的详情
        tasks = [_fetch_item(client, id) for id in ids]
        items = await asyncio.gather(*tasks)

        stories = []
        for item in items:
            if not item or item.get("type") != "story" or not item.get("title"):
                continue
            stories.append({
                "title": item["title"],
                "url": item.get("url", f"https://news.ycombinator.com/item?id={item['id']}"),
                "score": item.get("score", 0),
                "comments": item.get("descendants", 0),
                "source": "hackernews",
                "source_id": str(item["id"]),
                "content": "",  # HN API 不提供正文，后续用 fetch_content 补充
            })

        return stories


async def fetch_hn_top_comment(item_id: str) -> str:
    """获取 HN 帖子的最高分评论（用作正文降级方案）"""
    async with httpx.AsyncClient() as client:
        item = await _fetch_item(client, int(item_id))
        if not item or not item.get("kids"):
            return ""

        # 获取第一条评论（通常是最相关的）
        comment = await _fetch_item(client, item["kids"][0])
        if comment and comment.get("text"):
            return comment["text"][:2000]
        return ""
