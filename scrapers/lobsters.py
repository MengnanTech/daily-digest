"""Lobsters 抓取器 - 高质量技术社区（完全免费，无需 API Key）"""
import httpx


async def fetch_lobsters(top_n: int = 15) -> list[dict]:
    """抓取 Lobsters 热门文章"""
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                "https://lobste.rs/hottest.json",
                timeout=15,
                headers={"User-Agent": "DailyDigest/1.0"},
            )
            r.raise_for_status()
            items = r.json()[:top_n]

            return [{
                "title": item.get("title", ""),
                "url": item.get("url") or item.get("comments_url", ""),
                "score": item.get("score", 0),
                "source": "lobsters",
                "content": item.get("description", ""),
                "tags": item.get("tags", []),
            } for item in items]
        except Exception as e:
            print(f"⚠️ Lobsters 抓取失败: {e}")
            return []
