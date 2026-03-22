"""每日摘要生成器 - 主入口"""
import asyncio
import sys
from datetime import datetime

from scrapers import (
    fetch_hackernews,
    fetch_producthunt,
    fetch_github_trending,
    fetch_devto,
    fetch_v2ex,
    fetch_rss_feeds,
    fetch_36kr,
    fetch_twitter_kols,
)
from pipeline import deduplicate, rank_articles, summarize_articles, fetch_content_for_articles
from output import generate_html, save_digest_json


async def run():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"📰 每日科技热点 - {today}")
    print(f"{'='*60}\n")

    # ── 1. 并行抓取所有数据源 ──────────────────────
    print("📥 抓取数据源...")

    # 异步源
    async_results = await asyncio.gather(
        fetch_hackernews(30),
        fetch_producthunt(10),
        fetch_github_trending(15),
        fetch_devto(15),
        fetch_v2ex(15),
        return_exceptions=True,
    )

    # 同步源
    sync_results = []
    for fetch_fn in [fetch_rss_feeds, fetch_36kr, fetch_twitter_kols]:
        try:
            result = fetch_fn()
            sync_results.append(result)
        except Exception as e:
            print(f"⚠️ {fetch_fn.__name__} 失败: {e}")
            sync_results.append([])

    # 合并所有结果
    all_articles = []
    source_names = ["HackerNews", "ProductHunt", "GitHub", "Dev.to", "V2EX",
                     "RSS", "36氪", "Twitter"]

    for i, result in enumerate(list(async_results) + sync_results):
        name = source_names[i] if i < len(source_names) else f"Source-{i}"
        if isinstance(result, Exception):
            print(f"  ❌ {name}: 失败 ({result})")
        elif isinstance(result, list):
            print(f"  ✅ {name}: {len(result)} 条")
            all_articles.extend(result)
        else:
            print(f"  ❌ {name}: 未知结果")

    print(f"\n📊 共抓取: {len(all_articles)} 条\n")

    if not all_articles:
        print("❌ 没有抓到任何数据，退出")
        sys.exit(1)

    # ── 2. 去重 ─────────────────────────────────────
    print("🔄 去重中...")
    unique = deduplicate(all_articles)
    print(f"   去重后: {len(unique)} 条\n")

    # ── 3. 排序 ─────────────────────────────────────
    print("📈 排序中...")
    ranked = rank_articles(unique)

    # ── 4. 取 TOP 20，补充正文 ──────────────────────
    top_n = 20
    top_articles = ranked[:top_n]

    print(f"📄 为 TOP {top_n} 补充正文...")
    top_articles = await fetch_content_for_articles(top_articles)

    # ── 5. AI 摘要 ──────────────────────────────────
    print("🤖 生成 AI 摘要...\n")
    top_articles = await summarize_articles(top_articles)

    # ── 6. 输出 ─────────────────────────────────────
    # 生成 HTML
    html_path = generate_html(top_articles, today)
    print(f"📄 HTML 已生成: {html_path}")

    # 保存 JSON
    json_path = save_digest_json(top_articles, today)
    print(f"💾 JSON 已保存: {json_path}")

    # 控制台预览
    print(f"\n{'='*60}")
    print(f"🔥 今日 TOP {top_n}")
    print(f"{'='*60}\n")

    for i, article in enumerate(top_articles, 1):
        source = article.get("source", "")
        score = article.get("score", 0)
        also_on = article.get("also_on", [])
        category = article.get("category", "")
        summary = article.get("summary", "")

        source_info = f"[{source}"
        if score > 0:
            source_info += f"/{score}分"
        source_info += "]"
        if also_on:
            source_info += f" 也出现在: {', '.join(also_on)}"

        print(f"{i:2d}. {article.get('title', '')}")
        print(f"    {source_info} #{category}")
        if summary:
            print(f"    📝 {summary}")
        print(f"    🔗 {article.get('url', '')}")
        print()

    print(f"✅ 完成！用浏览器打开 {html_path} 查看完整报告\n")


if __name__ == "__main__":
    asyncio.run(run())
