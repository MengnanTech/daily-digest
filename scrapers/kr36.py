"""36氪抓取器 - 通过 RSSHub（完全免费，多实例备选）"""
import feedparser
import httpx
from config import RSSHUB_FEEDS


def fetch_36kr(top_n: int = 15) -> list[dict]:
    """抓取 36氪热榜，自动尝试多个 RSSHub 实例"""
    articles = []

    for source_name, urls in RSSHUB_FEEDS.items():
        # urls 是一个列表，按优先级尝试
        if isinstance(urls, str):
            urls = [urls]

        xml_content = ""
        for url in urls:
            xml_content = _download_feed(url)
            if xml_content:
                break

        if not xml_content:
            print(f"  ⚠️ {source_name} 所有 RSSHub 实例都失败了")
            continue

        try:
            feed = feedparser.parse(xml_content)
            for entry in feed.entries[:top_n]:
                summary = entry.get("summary", "")
                from bs4 import BeautifulSoup
                clean = BeautifulSoup(summary, "html.parser").get_text() if summary else ""

                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "score": 0,
                    "source": source_name,
                    "content": clean[:2000],
                })
        except Exception as e:
            print(f"  ⚠️ {source_name} 解析失败: {e}")
            continue

    return articles


def _download_feed(url: str) -> str:
    """用 httpx 同步下载 RSS 内容"""
    try:
        with httpx.Client(verify=False, timeout=10, follow_redirects=True) as client:
            r = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
            })
            r.raise_for_status()
            return r.text
    except Exception as e:
        print(f"  ⚠️ 下载 {url} 失败: {e}")
        return ""
