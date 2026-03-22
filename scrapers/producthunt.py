"""Product Hunt 抓取器 - 使用官方 GraphQL API"""
import httpx
from config import PH_TOKEN

PH_API = "https://api.producthunt.com/v2/api/graphql"

QUERY = """
{
  posts(order: VOTES, first: %d) {
    edges {
      node {
        name
        tagline
        url
        website
        votesCount
        createdAt
      }
    }
  }
}
"""


async def fetch_producthunt(top_n: int = 10) -> list[dict]:
    """抓取 Product Hunt 今日热门产品"""
    if not PH_TOKEN:
        # 没有 Token 时使用 RSS 降级
        return await _fetch_via_rss(top_n)

    headers = {
        "Authorization": f"Bearer {PH_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                PH_API,
                json={"query": QUERY % top_n},
                headers=headers,
                timeout=15,
            )
            r.raise_for_status()
            data = r.json()
            edges = data.get("data", {}).get("posts", {}).get("edges", [])

            return [{
                "title": f"{p['node']['name']} - {p['node']['tagline']}",
                "url": p["node"].get("website") or p["node"]["url"],
                "score": p["node"].get("votesCount", 0),
                "source": "producthunt",
                "content": p["node"].get("tagline", ""),
            } for p in edges]
        except Exception as e:
            print(f"⚠️ Product Hunt API 失败: {e}，使用 RSS 降级")
            return await _fetch_via_rss(top_n)


async def _fetch_via_rss(top_n: int = 10) -> list[dict]:
    """Product Hunt RSS 降级方案（不需要 Token）"""
    import feedparser
    try:
        feed = feedparser.parse("https://www.producthunt.com/feed")
        return [{
            "title": e.title,
            "url": e.link,
            "score": 0,
            "source": "producthunt",
            "content": e.get("summary", ""),
        } for e in feed.entries[:top_n]]
    except Exception:
        return []
