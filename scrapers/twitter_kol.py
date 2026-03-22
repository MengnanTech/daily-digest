"""Twitter KOL 抓取器 - 通过 Nitter RSS（完全免费）"""
import feedparser
from config import NITTER_INSTANCE, TWITTER_KOLS


def fetch_twitter_kols(per_kol: int = 5) -> list[dict]:
    """通过 Nitter RSS 抓取 Twitter KOL 的推文"""
    articles = []

    for username, label in TWITTER_KOLS.items():
        rss_url = f"{NITTER_INSTANCE}/{username}/rss"
        try:
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                continue

            for entry in feed.entries[:per_kol]:
                title = entry.get("title", "")
                if not title or len(title) < 10:
                    continue

                # Nitter 链接转回 Twitter 链接
                link = entry.get("link", "")
                link = link.replace(NITTER_INSTANCE, "https://twitter.com")

                articles.append({
                    "title": title[:280],
                    "url": link,
                    "score": 0,
                    "source": "twitter",
                    "source_label": f"@{username} ({label})",
                    "content": title,  # 推文内容就是正文
                })
        except Exception as e:
            print(f"⚠️ Twitter KOL @{username} 抓取失败: {e}")
            continue

    return articles
