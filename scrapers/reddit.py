"""Reddit 抓取器 - 使用公开 JSON API（无需 API Key）"""
import httpx
from config import REDDIT_SUBREDDITS

HEADERS = {
    "User-Agent": "DailyDigest/1.0 (tech news aggregator)",
}


async def fetch_reddit(per_sub: int = 5) -> list[dict]:
    """抓取 Reddit 多个子版块的热门帖子"""
    articles = []

    async with httpx.AsyncClient() as client:
        for subreddit in REDDIT_SUBREDDITS:
            try:
                r = await client.get(
                    f"https://www.reddit.com/r/{subreddit}/hot.json",
                    params={"limit": per_sub, "t": "day"},
                    headers=HEADERS,
                    timeout=15,
                )
                r.raise_for_status()
                data = r.json()

                for post in data.get("data", {}).get("children", []):
                    d = post.get("data", {})
                    # 跳过置顶帖和自引用帖
                    if d.get("stickied"):
                        continue

                    articles.append({
                        "title": d.get("title", ""),
                        "url": d.get("url", ""),
                        "score": d.get("score", 0),
                        "comments": d.get("num_comments", 0),
                        "source": "reddit",
                        "source_label": f"r/{subreddit}",
                        "content": d.get("selftext", "")[:2000],
                    })
            except Exception as e:
                print(f"⚠️ Reddit r/{subreddit} 抓取失败: {e}")
                continue

    return articles
