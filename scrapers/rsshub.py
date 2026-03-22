"""RSSHub 统一抓取器 - 支持多实例自动切换"""
import feedparser
import httpx
from bs4 import BeautifulSoup
from config import RSSHUB_INSTANCES, RSSHUB_ROUTES


def fetch_rsshub(per_source: int = 10) -> list[dict]:
    """抓取所有 RSSHub 配置的源"""
    articles = []

    for source_name, route in RSSHUB_ROUTES.items():
        xml_content = _try_instances(route)
        if not xml_content:
            continue

        try:
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
            print(f"  ⚠️ {source_name} 解析失败: {e}")
            continue

    return articles


def _try_instances(route: str) -> str:
    """依次尝试多个 RSSHub 实例"""
    for instance in RSSHUB_INSTANCES:
        url = f"{instance}{route}"
        try:
            with httpx.Client(verify=False, timeout=10, follow_redirects=True) as client:
                r = client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                })
                r.raise_for_status()
                return r.text
        except Exception:
            continue

    return ""
