"""Dev.to 抓取器 - 使用官方 REST API（完全免费）"""
import httpx

DEVTO_API = "https://dev.to/api"


async def fetch_devto(top_n: int = 15) -> list[dict]:
    """抓取 Dev.to 过去一天最热门文章"""
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{DEVTO_API}/articles",
                params={"top": 1, "per_page": top_n},
                timeout=15,
            )
            r.raise_for_status()
            articles = r.json()
        except Exception as e:
            print(f"⚠️ Dev.to API 失败: {e}")
            return []

    results = []
    for a in articles:
        results.append({
            "title": a.get("title", ""),
            "url": a.get("url", ""),
            "score": a.get("positive_reactions_count", 0),
            "source": "devto",
            "content": a.get("description", ""),
            "tags": [t for t in a.get("tag_list", [])],
        })

    return results
