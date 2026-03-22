"""YouTube 科技频道抓取器 - 通过 RSS Feed（完全免费，无需 API Key）"""
import feedparser
import httpx
from bs4 import BeautifulSoup

# 科技 YouTube 频道 ID
# YouTube 每个频道都有免费 RSS：https://www.youtube.com/feeds/videos.xml?channel_id=XXX
YOUTUBE_CHANNELS = {
    # 英文科技
    "Fireship": "UCsBjURrPoezykLs9EqgamOA",
    "ThePrimeagen": "UCUyeluBRhGPCW4rPe_UvBZQ",
    "NetworkChuck": "UC9-y-6csu5WGm29I7JiwpnA",
    "TechLinked": "UCeeFfhMcJa1kjtfZAGskOCA",
    "MKBHD": "UCBJycsmduvYEL83R_U4JriQ",
    "TwoMinutePapers": "UCbfYPyITQ-7l4upoX8nvctg",
    "YannicKilcher": "UCZHmQk67mSJgfCCTn7xBfew",
    "ArvinAsh": "UCpMcsdZf2KkAnfmxiq2MfMQ",
    # 中文科技
    "林亦LYi": "UCHAuvFMEaof0F2beAnJGBXg",
}

YOUTUBE_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def fetch_youtube(per_channel: int = 3) -> list[dict]:
    """抓取科技 YouTube 频道最新视频"""
    articles = []

    for channel_name, channel_id in YOUTUBE_CHANNELS.items():
        url = YOUTUBE_RSS.format(channel_id=channel_id)
        try:
            xml_content = _download_feed(url)
            if not xml_content:
                continue

            feed = feedparser.parse(xml_content)
            for entry in feed.entries[:per_channel]:
                # 提取视频信息
                title = entry.get("title", "")
                link = entry.get("link", "")

                # 从 media:statistics 获取观看数
                views = 0
                media_stats = entry.get("media_statistics", {})
                if media_stats:
                    views = int(media_stats.get("views", 0))

                # 从 media:group > media:description 获取描述
                description = ""
                media_group = entry.get("media_group", [])
                if media_group:
                    for item in media_group:
                        if hasattr(item, "get"):
                            description = item.get("media:description", "")
                            break

                if not description:
                    description = entry.get("summary", "")
                    if description:
                        description = BeautifulSoup(description, "html.parser").get_text()

                articles.append({
                    "title": f"[{channel_name}] {title}",
                    "url": link,
                    "score": views,
                    "source": "youtube",
                    "source_label": channel_name,
                    "content": description[:2000] if description else title,
                })
        except Exception as e:
            print(f"  ⚠️ YouTube [{channel_name}] 抓取失败: {e}")
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
