"""RSS Feed 抓取器 - 支持多个科技媒体源（完全免费）"""
import ssl
import feedparser
import httpx
from config import RSS_FEEDS


def fetch_rss_feeds(per_source: int = 10) -> list[dict]:
    """抓取所有 RSS 源的最新文章"""
    articles = []

    for source_name, url in RSS_FEEDS.items():
        try:
            # 用 httpx 下载 RSS 内容（解决 SSL 证书和代理问题）
            xml_content = _download_feed(url)
            if not xml_content:
                print(f"  ⚠️ RSS [{source_name}] 下载失败")
                continue

            feed = feedparser.parse(xml_content)
            for entry in feed.entries[:per_source]:
                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "score": 0,
                    "source": source_name,
                    "content": _clean_summary(entry.get("summary", "")),
                })
        except Exception as e:
            print(f"  ⚠️ RSS [{source_name}] 抓取失败: {e}")
            continue

    return articles


def _download_feed(url: str) -> str:
    """用 httpx 同步下载 RSS 内容"""
    try:
        with httpx.Client(verify=False, timeout=15, follow_redirects=True) as client:
            r = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
            })
            r.raise_for_status()
            return r.text
    except Exception as e:
        print(f"  ⚠️ 下载 {url} 失败: {e}")
        return ""


def _clean_summary(html_summary: str) -> str:
    """清理 RSS 摘要中的 HTML 标签"""
    from bs4 import BeautifulSoup
    if not html_summary:
        return ""
    text = BeautifulSoup(html_summary, "html.parser").get_text()
    return " ".join(text.split())[:2000]
