"""GitHub Trending 抓取器 - 直接解析 HTML 页面（不需要 API Key）"""
import httpx
from bs4 import BeautifulSoup


async def fetch_github_trending(top_n: int = 15) -> list[dict]:
    """抓取 GitHub 今日 Trending 仓库"""
    url = "https://github.com/trending"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, params={"since": "daily"}, headers=headers, timeout=15)
            r.raise_for_status()
        except Exception as e:
            print(f"⚠️ GitHub Trending 请求失败: {e}")
            return []

    soup = BeautifulSoup(r.text, "html.parser")
    repos = []

    for article in soup.select("article.Box-row")[:top_n]:
        # 仓库名
        name_tag = article.select_one("h2 a")
        if not name_tag:
            continue
        name = name_tag.get("href", "").strip("/")

        # 描述
        desc_tag = article.select_one("p")
        description = desc_tag.text.strip() if desc_tag else ""

        # 语言
        lang_tag = article.select_one("[itemprop='programmingLanguage']")
        language = lang_tag.text.strip() if lang_tag else ""

        # 今日星标数
        stars_text = ""
        for span in article.select("span.d-inline-block.float-sm-right"):
            stars_text = span.text.strip()
        today_stars = 0
        if stars_text:
            try:
                today_stars = int(stars_text.replace(",", "").split()[0])
            except (ValueError, IndexError):
                pass

        repos.append({
            "title": f"{name}" + (f" ({language})" if language else ""),
            "url": f"https://github.com/{name}",
            "score": today_stars,
            "source": "github",
            "content": description,
        })

    return repos
