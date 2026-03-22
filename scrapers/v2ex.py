"""V2EX 抓取器 - 使用官方 API"""
import httpx
from config import V2EX_TOKEN

V2EX_API = "https://www.v2ex.com/api/v2"


async def fetch_v2ex(top_n: int = 15) -> list[dict]:
    """抓取 V2EX 热门话题"""
    # 优先使用 V2 API（需要 Token）
    if V2EX_TOKEN:
        return await _fetch_v2_api(top_n)
    # 降级到免费的 V1 API
    return await _fetch_v1_api(top_n)


async def _fetch_v2_api(top_n: int) -> list[dict]:
    headers = {"Authorization": f"Bearer {V2EX_TOKEN}"}
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{V2EX_API}/nodes/hot/topics",
                headers=headers,
                timeout=15,
            )
            r.raise_for_status()
            topics = r.json().get("result", [])[:top_n]
            return [{
                "title": t.get("title", ""),
                "url": f"https://www.v2ex.com/t/{t['id']}",
                "score": t.get("replies", 0),
                "source": "v2ex",
                "content": t.get("content", "")[:2000],
            } for t in topics]
        except Exception as e:
            print(f"⚠️ V2EX V2 API 失败: {e}，使用 V1 降级")
            return await _fetch_v1_api(top_n)


async def _fetch_v1_api(top_n: int) -> list[dict]:
    """V1 API 降级方案（不需要 Token）"""
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                "https://www.v2ex.com/api/topics/hot.json",
                timeout=15,
            )
            r.raise_for_status()
            topics = r.json()[:top_n]
            return [{
                "title": t.get("title", ""),
                "url": t.get("url", ""),
                "score": t.get("replies", 0),
                "source": "v2ex",
                "content": t.get("content", "")[:2000],
            } for t in topics]
        except Exception as e:
            print(f"⚠️ V2EX V1 API 也失败了: {e}")
            return []
