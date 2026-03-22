"""输出模块 - 生成 HTML 页面和 JSON 文件"""
import json
import os
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def _ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _source_emoji(source: str) -> str:
    return {
        "hackernews": "🟠",
        "producthunt": "🐱",
        "github": "🐙",
        "devto": "📝",
        "v2ex": "💬",
        "twitter": "🐦",
        "techcrunch": "📰",
        "theverge": "📰",
        "arstechnica": "📰",
        "36kr": "🇨🇳",
    }.get(source, "📌")


def _source_display(source: str) -> str:
    return {
        "hackernews": "Hacker News",
        "producthunt": "Product Hunt",
        "github": "GitHub Trending",
        "devto": "Dev.to",
        "v2ex": "V2EX",
        "twitter": "Twitter",
        "techcrunch": "TechCrunch",
        "theverge": "The Verge",
        "arstechnica": "Ars Technica",
        "36kr": "36氪",
    }.get(source, source)


def generate_html(articles: list[dict], date_str: str) -> str:
    """生成精美的 HTML 摘要页面"""
    _ensure_output_dir()

    cards_html = ""
    for i, a in enumerate(articles, 1):
        source = a.get("source", "")
        emoji = _source_emoji(source)
        display = _source_display(source)
        score = a.get("score", 0)
        category = a.get("category", "行业动态")
        summary = a.get("summary", "")
        url = a.get("url", "#")
        title = a.get("title", "")
        also_on = a.get("also_on", [])

        score_html = f'<span class="score">{score}分</span>' if score > 0 else ""
        also_html = ""
        if also_on:
            platforms = ", ".join([_source_display(s) for s in also_on])
            also_html = f'<span class="also-on">也出现在 {platforms}</span>'

        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <span class="rank">#{i}</span>
                <span class="source">{emoji} {display}</span>
                {score_html}
                <span class="category">{category}</span>
            </div>
            <h3 class="card-title">
                <a href="{url}" target="_blank" rel="noopener">{title}</a>
            </h3>
            <p class="card-summary">{summary}</p>
            {f'<div class="card-meta">{also_html}</div>' if also_html else ''}
        </div>"""

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
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 40px 0 30px;
            border-bottom: 1px solid #2a2a2a;
            margin-bottom: 30px;
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
        .card {{
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            transition: border-color 0.2s;
        }}
        .card:hover {{
            border-color: #444;
        }}
        .card-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        .rank {{
            color: #666;
            font-size: 13px;
            font-weight: 600;
        }}
        .source {{
            font-size: 13px;
            color: #999;
        }}
        .score {{
            font-size: 12px;
            color: #f59e0b;
            background: #f59e0b22;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .category {{
            font-size: 12px;
            color: #60a5fa;
            background: #60a5fa22;
            padding: 2px 8px;
            border-radius: 4px;
            margin-left: auto;
        }}
        .card-title {{
            font-size: 17px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .card-title a {{
            color: #fff;
            text-decoration: none;
        }}
        .card-title a:hover {{
            color: #60a5fa;
        }}
        .card-summary {{
            color: #aaa;
            font-size: 14px;
            line-height: 1.7;
        }}
        .card-meta {{
            margin-top: 10px;
            font-size: 12px;
        }}
        .also-on {{
            color: #666;
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
            .card {{ padding: 15px; }}
            .card-title {{ font-size: 15px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>每日科技热点</h1>
        <div class="date">{date_str}</div>
        <div class="stats">来自 HackerNews / ProductHunt / GitHub / Dev.to / V2EX / TechCrunch / 36氪 / Twitter 等 8 个源</div>
    </div>
    {cards_html}
    <div class="footer">
        由 AI 自动聚合生成 | Daily Tech Digest
    </div>
</body>
</html>"""

    filepath = os.path.join(OUTPUT_DIR, f"digest-{date_str}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filepath


def save_digest_json(articles: list[dict], date_str: str) -> str:
    """保存摘要为 JSON 文件"""
    _ensure_output_dir()

    data = {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "count": len(articles),
        "articles": articles,
    }

    filepath = os.path.join(OUTPUT_DIR, f"digest-{date_str}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath
