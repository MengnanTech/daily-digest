"""输出模块 - 生成 HTML 页面和 JSON 文件（按平台分区展示）"""
import json
import os
from collections import defaultdict
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def _ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── 平台分组定义 ──────────────────────────────
# 把多个 source 归入同一个展示分组
PLATFORM_GROUPS = [
    {
        "id": "hackernews",
        "name": "Hacker News",
        "emoji": "🟠",
        "sources": ["hackernews"],
    },
    {
        "id": "lobsters",
        "name": "Lobsters",
        "emoji": "🦞",
        "sources": ["lobsters"],
    },
    {
        "id": "producthunt",
        "name": "Product Hunt",
        "emoji": "🐱",
        "sources": ["producthunt"],
    },
    {
        "id": "github",
        "name": "GitHub Trending",
        "emoji": "🐙",
        "sources": ["github"],
    },
    {
        "id": "reddit",
        "name": "Reddit",
        "emoji": "🔴",
        "sources": ["reddit"],
    },
    {
        "id": "youtube",
        "name": "YouTube",
        "emoji": "▶️",
        "sources": ["youtube"],
    },
    {
        "id": "devto",
        "name": "Dev.to",
        "emoji": "📝",
        "sources": ["devto"],
    },
    {
        "id": "tech_media",
        "name": "科技媒体",
        "emoji": "📰",
        "sources": ["techcrunch", "theverge", "arstechnica", "mit_tech", "wired",
                     "changelog", "infoq", "echojs", "slashdot", "aiweekly", "thenewstack"],
    },
    {
        "id": "cn_community",
        "name": "中文社区",
        "emoji": "🇨🇳",
        "sources": ["v2ex", "36kr", "sspai", "juejin", "zhihu", "oschina",
                     "ifanr", "cls", "ruanyifeng", "geekpark"],
    },
    {
        "id": "twitter",
        "name": "Twitter",
        "emoji": "🐦",
        "sources": ["twitter"],
    },
]

# source → 显示名映射
SOURCE_DISPLAY = {
    "hackernews": "Hacker News", "producthunt": "Product Hunt",
    "github": "GitHub Trending", "devto": "Dev.to", "v2ex": "V2EX",
    "twitter": "Twitter", "lobsters": "Lobsters", "reddit": "Reddit",
    "techcrunch": "TechCrunch", "theverge": "The Verge",
    "arstechnica": "Ars Technica", "mit_tech": "MIT Tech Review",
    "wired": "Wired", "changelog": "Changelog", "infoq": "InfoQ",
    "echojs": "Echo JS", "slashdot": "Slashdot", "aiweekly": "AI Weekly",
    "thenewstack": "The New Stack", "36kr": "36氪", "sspai": "少数派",
    "juejin": "掘金", "zhihu": "知乎", "oschina": "开源中国",
    "ifanr": "爱范儿", "cls": "财联社", "ruanyifeng": "阮一峰",
    "geekpark": "极客公园", "youtube": "YouTube",
}


def _source_display(source: str) -> str:
    return SOURCE_DISPLAY.get(source, source)


def _group_articles(articles: list[dict]) -> list[dict]:
    """按平台分组，返回 [{group_info, articles}, ...]"""
    # 建立 source → group 映射
    source_to_group = {}
    for group in PLATFORM_GROUPS:
        for src in group["sources"]:
            source_to_group[src] = group["id"]

    # 按 group 分桶
    buckets = defaultdict(list)
    for a in articles:
        source = a.get("source", "")
        group_id = source_to_group.get(source, "other")
        buckets[group_id].append(a)

    # 按 PLATFORM_GROUPS 定义的顺序输出，跳过空桶
    result = []
    for group in PLATFORM_GROUPS:
        items = buckets.get(group["id"], [])
        if items:
            # 组内按分数排序
            items.sort(key=lambda x: x.get("final_score", x.get("score", 0)), reverse=True)
            result.append({**group, "articles": items})

    # 未匹配的放到最后
    other = buckets.get("other", [])
    if other:
        result.append({"id": "other", "name": "其他", "emoji": "📌", "articles": other})

    return result


def generate_html(articles: list[dict], date_str: str) -> str:
    """生成按平台分区展示的 HTML 摘要页面"""
    _ensure_output_dir()

    grouped = _group_articles(articles)

    # 生成导航栏
    nav_html = ""
    for g in grouped:
        count = len(g["articles"])
        nav_html += f'<a href="#{g["id"]}" class="nav-item">{g["emoji"]} {g["name"]} <span class="nav-count">{count}</span></a>\n'

    # 生成各平台内容区
    sections_html = ""
    for g in grouped:
        cards = ""
        for i, a in enumerate(g["articles"], 1):
            source = a.get("source", "")
            score = a.get("score", 0)
            category = a.get("category", "")
            summary = a.get("summary", "")
            url = a.get("url", "#")
            title = a.get("title", "")
            also_on = a.get("also_on", [])
            source_label = a.get("source_label", "")

            score_html = f'<span class="score">{score:,}</span>' if score > 0 else ""
            cat_html = f'<span class="category">{category}</span>' if category else ""

            # 在合并分组（科技媒体/中文社区）中显示具体来源
            sub_source = ""
            if len(g["sources"]) > 1:
                sub_source = f'<span class="sub-source">{_source_display(source)}</span>'
            elif source_label:
                sub_source = f'<span class="sub-source">{source_label}</span>'

            also_html = ""
            if also_on:
                platforms = ", ".join([_source_display(s) for s in also_on])
                also_html = f'<div class="card-meta"><span class="also-on">也出现在 {platforms}</span></div>'

            cards += f"""
            <div class="card">
                <div class="card-header">
                    <span class="rank">#{i}</span>
                    {sub_source}
                    {score_html}
                    {cat_html}
                </div>
                <h3 class="card-title">
                    <a href="{url}" target="_blank" rel="noopener">{title}</a>
                </h3>
                {"<p class='card-summary'>" + summary + "</p>" if summary else ""}
                {also_html}
            </div>"""

        sections_html += f"""
        <section class="platform-section" id="{g['id']}">
            <div class="section-header">
                <h2>{g['emoji']} {g['name']}</h2>
                <span class="section-count">{len(g['articles'])} 条</span>
            </div>
            {cards}
        </section>"""

    total = sum(len(g["articles"]) for g in grouped)
    platform_count = len(grouped)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日科技热点 - {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f0f0f;
            color: #e0e0e0;
            line-height: 1.6;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 40px 0 20px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 8px;
        }}
        .header .date {{
            color: #888;
            font-size: 16px;
        }}
        .header .stats {{
            color: #666;
            font-size: 13px;
            margin-top: 8px;
        }}
        /* 导航栏 */
        .nav {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 16px 0;
            border-top: 1px solid #2a2a2a;
            border-bottom: 1px solid #2a2a2a;
            margin-bottom: 30px;
            position: sticky;
            top: 0;
            background: #0f0f0f;
            z-index: 10;
        }}
        .nav-item {{
            color: #999;
            text-decoration: none;
            font-size: 13px;
            padding: 6px 12px;
            border-radius: 6px;
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .nav-item:hover {{
            color: #fff;
            border-color: #444;
            background: #252525;
        }}
        .nav-count {{
            color: #666;
            font-size: 11px;
            margin-left: 4px;
        }}
        /* 平台分区 */
        .platform-section {{
            margin-bottom: 40px;
        }}
        .section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 2px solid #2a2a2a;
            margin-bottom: 16px;
        }}
        .section-header h2 {{
            font-size: 20px;
            font-weight: 600;
            color: #fff;
        }}
        .section-count {{
            color: #666;
            font-size: 13px;
        }}
        /* 卡片 */
        .card {{
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            transition: border-color 0.2s;
        }}
        .card:hover {{
            border-color: #444;
        }}
        .card-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
            flex-wrap: wrap;
        }}
        .rank {{
            color: #555;
            font-size: 12px;
            font-weight: 600;
            min-width: 24px;
        }}
        .sub-source {{
            font-size: 12px;
            color: #888;
            background: #ffffff0a;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .score {{
            font-size: 12px;
            color: #f59e0b;
            background: #f59e0b15;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .category {{
            font-size: 12px;
            color: #60a5fa;
            background: #60a5fa15;
            padding: 2px 8px;
            border-radius: 4px;
            margin-left: auto;
        }}
        .card-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 6px;
        }}
        .card-title a {{
            color: #e8e8e8;
            text-decoration: none;
        }}
        .card-title a:hover {{
            color: #60a5fa;
        }}
        .card-summary {{
            color: #999;
            font-size: 14px;
            line-height: 1.7;
        }}
        .card-meta {{
            margin-top: 8px;
            font-size: 12px;
        }}
        .also-on {{
            color: #555;
        }}
        .footer {{
            text-align: center;
            padding: 30px 0;
            color: #555;
            font-size: 13px;
            border-top: 1px solid #2a2a2a;
            margin-top: 20px;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 10px; }}
            .header h1 {{ font-size: 22px; }}
            .card {{ padding: 12px 14px; }}
            .card-title {{ font-size: 14px; }}
            .nav {{ gap: 6px; }}
            .nav-item {{ font-size: 12px; padding: 4px 8px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>每日科技热点</h1>
        <div class="date">{date_str}</div>
        <div class="stats">共 {total} 条 · 来自 {platform_count} 个平台</div>
    </div>
    <nav class="nav">
        {nav_html}
    </nav>
    {sections_html}
    <div class="footer">
        由 AI 自动聚合生成 · Daily Tech Digest
    </div>
</body>
</html>"""

    filepath = os.path.join(OUTPUT_DIR, f"digest-{date_str}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filepath


def save_digest_json(articles: list[dict], date_str: str) -> str:
    """保存摘要为 JSON 文件（也按平台分组）"""
    _ensure_output_dir()

    grouped = _group_articles(articles)
    data = {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "total_count": len(articles),
        "platforms": [
            {
                "name": g["name"],
                "emoji": g["emoji"],
                "count": len(g["articles"]),
                "articles": g["articles"],
            }
            for g in grouped
        ],
    }

    filepath = os.path.join(OUTPUT_DIR, f"digest-{date_str}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath
