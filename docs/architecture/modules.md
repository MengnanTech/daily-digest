# Daily Digest 模块详解

_最后更新：2026-03-31_

## 目录结构

```
daily-digest/
├── main.py                   # 应用入口（基础 hello world，实际逻辑在 daily_run.py）
├── daily_run.py              # 主执行逻辑（pipeline 编排）
├── config.py                 # 全局配置（数据源、权重、API Keys）
├── output.py                 # HTML/JSON 输出生成
├── pipeline/
│   ├── __init__.py           # 导出 deduplicate, rank_articles, fetch_content_for_articles
│   ├── content_fetcher.py    # 文章正文抓取
│   ├── dedup.py              # 去重逻辑
│   ├── ranker.py             # 热度排序
│   └── summarizer.py        # 摘要（当前透传，不做额外处理）
├── scrapers/
│   ├── __init__.py           # 导出所有 scraper 函数
│   ├── hackernews.py         # HN 抓取（async）
│   ├── producthunt.py        # PH 抓取（async，需 PH_TOKEN）
│   ├── github_trending.py    # GitHub Trending 抓取（async）
│   ├── devto.py              # Dev.to 抓取（async）
│   ├── v2ex.py               # V2EX 抓取（async，需 V2EX_TOKEN）
│   ├── lobsters.py           # Lobsters 抓取（async）
│   ├── reddit.py             # Reddit 抓取（async）
│   ├── rss_feeds.py          # 英文 RSS 抓取（sync）
│   ├── rsshub.py             # RSSHub 中文源（sync，多实例备选）
│   ├── cn_rss.py             # 中文 RSS 直接订阅（sync）
│   ├── youtube.py            # YouTube 热门视频（sync）
│   └── twitter_kol.py        # Twitter KOL（单独运行，不含在 daily_run 中）
├── storage/
│   └── __init__.py           # MongoDB 存储（save_articles）
├── output/                   # 生成的 HTML/JSON 文件（.gitignore 排除）
├── scripts/                  # 辅助脚本（GitHub Actions workflow 等）
├── config.py                 # 数据源配置和权重
└── pyproject.toml            # 项目依赖（uv 管理）
```

## 核心模块

### daily_run.py（Pipeline 编排）

整个摘要生成的主入口：

1. **并行抓取**：使用 `asyncio.gather` 并行执行 7 个异步 scraper，同步 scraper 顺序执行
2. **结果合并**：合并所有来源，处理异常（Exception）
3. **去重**：调用 `deduplicate()`
4. **排序**：调用 `rank_articles()`
5. **每平台 TOP 10**：按 `source` 分组，各取前 10
6. **正文补充**：`fetch_content_for_articles()`（异步）
7. **MongoDB 写入**：`save_articles()`
8. **HTML/JSON 输出**：`generate_html()` + `save_digest_json()`

### config.py（配置中枢）

- `RSS_FEEDS`：英文 RSS 源列表（TechCrunch、TheVerge、ArsTechnica、MIT Tech Review、Wired、Changelog、InfoQ、EchoJS、Slashdot、AIWeekly、TheNewStack）
- `CN_RSS_FEEDS`：中文 RSS 源（阮一峰、极客公园）
- `RSSHUB_INSTANCES`：RSSHub 多实例备选列表（rssforever、pseudoyu、rsshub.app）
- `RSSHUB_ROUTES`：RSSHub 路由（36kr、少数派、掘金、知乎、OSChina、爱范儿、财联社）
- `REDDIT_SUBREDDITS`：关注子版块（programming、technology、MachineLearning、artificial、startups、SideProject）
- `TWITTER_KOLS`：KOL 列表（Altman、Karpathy、LeCun、等 AI/独立开发/科技领域 KOL）
- `SOURCE_WEIGHTS`：各数据源评分权重

**环境变量：**
| 变量 | 用途 |
|------|------|
| `PH_TOKEN` | ProductHunt API Token |
| `V2EX_TOKEN` | V2EX API Token |
| `NITTER_INSTANCE` | Nitter 实例地址（Twitter 代理）|
| `MONGODB_URI` | MongoDB 连接字符串 |

### pipeline/dedup.py（去重）

两阶段去重：
1. **URL 去重**：标准化 URL（去 www、去尾部斜杠、忽略 UTM 参数），集合精确匹配
2. **标题去重**：`SequenceMatcher` 相似度 > 0.6 判定为重复
3. **合并策略**：重复时保留更高分数的条目，记录 `also_on` 列表

### pipeline/ranker.py（排序）

跨平台归一化评分：
```
normalized = min(100, (raw_score / score_base) * 100)
weighted   = normalized * weight
bonus      = len(also_on) * 15  # 跨平台加分
final_score = weighted + bonus
```

RSS/Twitter 等无评分源给基础 30 分。
HackerNews score_base = 100，ProductHunt = 200，GitHub = 500，YouTube = 50000。

### pipeline/content_fetcher.py

批量抓取文章完整正文，为 HTML 报告提供摘要展示。

### pipeline/summarizer.py

当前版本直接透传原始文章数据，未接入 AI 摘要（预留扩展点）。

### output.py

- `generate_html(articles, date)` → 生成 HTML 报告（含来源标签、评分展示、跨平台标记）
- `save_digest_json(articles, date)` → 保存 JSON 格式摘要

### storage/mongo.py（存储层）

- 数据库：`manage_man_prod`，集合：`digest_articles`
- `get_mongo_collection()`：懒连接，读取 `MONGODB_URI` 环境变量
- `ensure_indexes(col)`：创建 `(date, category)` 复合索引 + `url` 唯一稀疏索引
- `save_articles(articles, default_category)`：批量 `UpdateOne` upsert，返回写入数量
  - 写入字段：title, url, source, category, content, summary, score, final_score, also_on, date, updated_at, created_at（仅首次）

### scrapers/ 说明

| 文件 | 类型 | 说明 |
|------|------|------|
| hackernews.py | async | 抓取 HN Top 30，含评分 |
| producthunt.py | async | 需 PH_TOKEN，抓取 Top 10 |
| github_trending.py | async | 爬取 GitHub Trending，含 star 数 |
| devto.py | async | 抓取 Dev.to 热门，含点赞数 |
| v2ex.py | async | 需 V2EX_TOKEN，抓取热帖 |
| lobsters.py | async | 抓取 Lobsters Top |
| reddit.py | async | 多 subreddit 并发抓取 |
| rss_feeds.py | sync | 批量解析英文 RSS（11 个源）|
| rsshub.py | sync | 解析 RSSHub 路由（多实例自动切换）|
| cn_rss.py | sync | 直接解析中文 RSS（阮一峰、极客公园）|
| youtube.py | sync | YouTube 热门视频 |
| twitter_kol.py | 独立 | KOL 推文，单独运行，不纳入 daily_run |
| kr36.py | - | 36氪辅助抓取 |
