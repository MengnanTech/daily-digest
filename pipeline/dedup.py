"""去重模块 - URL 精确去重 + 标题相似度去重"""
from difflib import SequenceMatcher
from urllib.parse import urlparse


def _normalize_url(url: str) -> str:
    """标准化 URL 用于去重"""
    parsed = urlparse(url)
    # 去掉 www 前缀、尾部斜杠、查询参数中的 utm 跟踪
    host = parsed.netloc.replace("www.", "")
    path = parsed.path.rstrip("/")
    return f"{host}{path}".lower()


def _title_similarity(a: str, b: str) -> float:
    """计算两个标题的相似度（0-1）"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def deduplicate(articles: list[dict]) -> list[dict]:
    """
    去重逻辑：
    1. URL 精确匹配去重
    2. 标题相似度 > 0.6 去重（同一事件不同平台报道）
    3. 同一事件多平台出现时，保留分数最高的那条，并记录其他平台
    """
    seen_urls: set[str] = set()
    result: list[dict] = []

    for article in articles:
        # URL 去重
        norm_url = _normalize_url(article.get("url", ""))
        if norm_url in seen_urls:
            # 找到已存在的文章，记录跨平台出现
            for existing in result:
                if _normalize_url(existing.get("url", "")) == norm_url:
                    existing.setdefault("also_on", []).append(article["source"])
                    # 取更高的分数
                    if article.get("score", 0) > existing.get("score", 0):
                        existing["score"] = article["score"]
                    break
            continue
        seen_urls.add(norm_url)

        # 标题相似度去重
        is_duplicate = False
        for existing in result:
            if _title_similarity(article.get("title", ""), existing.get("title", "")) > 0.6:
                existing.setdefault("also_on", []).append(article["source"])
                if article.get("score", 0) > existing.get("score", 0):
                    existing["score"] = article["score"]
                is_duplicate = True
                break

        if not is_duplicate:
            article["also_on"] = []
            result.append(article)

    return result
