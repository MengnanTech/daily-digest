# Daily Digest 架构概述

_最后更新：2026-03-31_

## 应用简介

Daily Digest 是一个 **多源科技新闻聚合与每日摘要生成器**。它每天自动从 11 个中英文科技信息平台抓取内容，经过去重、热度排序、正文补充等处理，生成 HTML 和 JSON 格式的每日科技热点报告，并通过 GitHub Pages 发布。同时将文章 upsert 写入 MongoDB（`manage_man_prod.digest_articles`），供 manage-man 平台使用。

通过 GitHub Actions 自动化调度，每日北京时间 07:00 执行，无需人工干预。

## 核心功能

- **多源并行抓取**：HackerNews、ProductHunt、GitHub Trending、Dev.to、V2EX、Lobsters、Reddit（异步并发），英文 RSS、RSSHub 中文源、中文 RSS、YouTube（同步顺序）
- **跨平台去重**：URL 精确去重 + 标题相似度去重（SequenceMatcher，阈值 0.6），保留最高分条目并记录 `also_on`
- **跨平台热度排序**：归一化评分（0-100）+ 平台权重 + 跨平台加分（每个额外平台 +15 分）
- **正文补充**：用 readability-lxml 自动提取文章正文（限 3000 字符，并发数 ≤5）
- **MongoDB 存储**：pymongo bulk upsert，写入 `manage_man_prod.digest_articles`
- **按平台分组 HTML 输出**：深色主题，含粘性导航栏、卡片式展示、跨平台标记
- **GitHub Actions 定时调度 + GitHub Pages 部署**：全自动，保留历史报告

## 技术栈

| 层次 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| 包管理 | uv（astral-sh，替代 pip/poetry）|
| 异步框架 | asyncio + httpx（HTTP/2、SOCKS 支持）|
| RSS 解析 | feedparser |
| 正文提取 | readability-lxml + BeautifulSoup4 |
| AI SDK | anthropic（预留，summarizer 当前透传）|
| 数据库 | MongoDB（pymongo，upsert）|
| CI/CD | GitHub Actions |
| 发布 | GitHub Pages（peaceiris/actions-gh-pages）|
| 配置 | python-dotenv（`.env` 文件）|

## 执行流程

```
daily_run.py::run()
│
├── 1. 并行抓取（asyncio.gather）
│   ├── fetch_hackernews(30)        [async]
│   ├── fetch_producthunt(10)       [async]
│   ├── fetch_github_trending(15)   [async]
│   ├── fetch_devto(15)             [async]
│   ├── fetch_v2ex(15)              [async]
│   ├── fetch_lobsters(15)          [async]
│   ├── fetch_reddit(5)             [async]
│   ├── fetch_rss_feeds()           [sync]
│   ├── fetch_rsshub()              [sync, 多实例备选]
│   ├── fetch_cn_rss()              [sync]
│   └── fetch_youtube()             [sync]
│
├── 2. 去重 deduplicate()
│   ├── URL 精确匹配（标准化后）
│   └── 标题相似度 > 0.6（SequenceMatcher）
│
├── 3. 排序 rank_articles()
│   ├── 归一化分数（raw / score_base * 100，max 100）
│   ├── 乘以平台权重
│   └── 跨平台加分（+15/个 also_on）
│
├── 4. 每平台 TOP 10 筛选（by source 分组）
│
├── 5. 正文补充 fetch_content_for_articles()
│   └── 异步并发，信号量限制 ≤5
│
├── 6. MongoDB upsert save_articles()
│   └── manage_man_prod.digest_articles
│
└── 7. 输出
    ├── generate_html() → output/digest-YYYY-MM-DD.html
    └── save_digest_json() → output/digest-YYYY-MM-DD.json
```

## 项目目录结构

```
daily-digest/
├── daily_run.py          # 主入口（pipeline 编排）
├── main.py               # 占位入口（uv script entry）
├── config.py             # 数据源配置、权重配置、环境变量
├── output.py             # HTML/JSON 输出生成（按平台分组）
├── pyproject.toml        # 项目依赖（uv 管理，Python 3.11）
├── uv.lock               # 依赖锁定文件
├── scrapers/             # 各平台抓取器（11 个）
├── pipeline/             # 数据处理管线（去重、排序、正文、摘要）
├── storage/              # MongoDB 存储层
├── output/               # 生成的 HTML/JSON 文件（.gitignore）
├── scripts/              # 辅助脚本
└── .github/workflows/
    └── daily-digest.yml  # GitHub Actions 定时任务
```
