"""中文 RSS 源直接抓取器"""
import feedparser
import httpx
from bs4 import BeautifulSoup
from config import CN_RSS_FEEDS


def fetch_cn_rss(per_source: int = 10) -> list[dict]:
    """抓取中文 RSS 源"""
    articles = []

    for source_name, url in CN_RSS_FEEDS.items():
        try:
            xml_content = _download_feed(url)
            if not xml_content:
                continue

            feed = feedparser.parse(xml_content)
            for entry in feed.entries[:per_source]:
                summary = entry.get("summary", "")
                clean = BeautifulSoup(summary, "html.parser").get_text() if summary else ""

                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "score": 0,
                    "source": source_name,
                    "content": clean[:2000],
                })
        except Exception as e:
            print(f"  ⚠️ 中文RSS [{source_name}] 抓取失败: {e}")
            continue

    return articles


def _download_feed(url: str) -> str:
    try:
        with httpx.Client(verify=False, timeout=15, follow_redirects=True) as client:
            r = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            })
            r.raise_for_status()
            return r.text
    except Exception as e:
        print(f"  ⚠️ 下载 {url} 失败: {e}")
        return ""
