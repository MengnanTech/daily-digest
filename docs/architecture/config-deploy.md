# Daily Digest 配置与部署

_最后更新：2026-03-31_

## 本地运行

### 环境准备

```bash
# 安装 uv（如未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 进入项目目录
cd /Users/levi/project/Python/daily-digest

# 安装依赖
uv sync
```

### 配置 .env 文件

在项目根目录创建 `.env` 文件：

```env
PH_TOKEN=your_producthunt_api_token
V2EX_TOKEN=your_v2ex_api_token
NITTER_INSTANCE=https://nitter.privacydev.net
MONGODB_URI=mongodb://localhost:27017/daily_digest
```

### 运行

```bash
uv run python daily_run.py
```

输出文件在 `output/YYYY-MM-DD.html` 和 `output/YYYY-MM-DD.json`。

## GitHub Actions 自动化部署

### 触发方式
- **定时调度**：每日定时执行（cron 配置在 `.github/workflows/` 中）
- **手动触发**：workflow_dispatch

### GitHub Actions Workflow 详情（`.github/workflows/daily-digest.yml`）

触发条件：
- cron `0 23 * * *`（北京时间每日 07:00）
- `workflow_dispatch`（手动触发）

权限：`contents: write`、`pages: write`

执行步骤：
1. `actions/checkout@v4` 检出代码
2. `astral-sh/setup-uv@v4` 安装 uv
3. `uv python install 3.11` 安装 Python
4. `uv sync` 安装依赖
5. 注入 Secrets：`PH_TOKEN`、`V2EX_TOKEN`（注意：MONGODB_URI 需要在 Secrets 中配置）
6. `uv run python daily_run.py` 执行主程序
7. 将最新 HTML 复制为 `site/index.html`，保留历史文件
8. `peaceiris/actions-gh-pages@v4` 部署到 GitHub Pages（`keep_files: true`）

### GitHub Pages
- 生成的 HTML 报告自动发布到 GitHub Pages
- 访问地址：`https://<username>.github.io/<repo>/`

## 依赖管理

使用 `uv` 包管理器（替代 pip/poetry）：
- `pyproject.toml`：项目依赖声明
- `uv.lock`：锁定文件（确保可复现）

主要依赖：
- `httpx` 或 `aiohttp`：异步 HTTP 客户端
- `feedparser`：RSS 解析
- `pymongo`：MongoDB 客户端
- `python-dotenv`：环境变量加载
- `difflib`（标准库）：标题相似度计算

## 数据存储

### MongoDB
- 数据库：`manage_man_prod`（与 manage-man 后端共用）
- 集合：`digest_articles`
- 主键：`url`（upsert，避免重复插入）
- 字段：`title`、`url`、`source`、`score`、`final_score`、`also_on`、`content`、`summary`、`category`、`category_label`、`source_label`、`date`、`created_at`、`updated_at`

### 本地文件
```
output/
├── 2026-03-31.html     # HTML 摘要报告
└── 2026-03-31.json     # JSON 结构化数据
```

## 数据源配置参考

| 数据源 | 类型 | 需要 Token | 评分基准 |
|--------|------|-----------|---------|
| HackerNews | 异步 | 否 | 100 分 |
| ProductHunt | 异步 | PH_TOKEN | 200 票 |
| GitHub Trending | 异步 | 否 | 500 star |
| Dev.to | 异步 | 否 | 50 心 |
| V2EX | 异步 | V2EX_TOKEN | 30 点击 |
| Lobsters | 异步 | 否 | 30 分 |
| Reddit | 异步 | 否 | 200 赞 |
| RSS Feeds (英文) | 同步 | 否 | 30 基础分 |
| RSSHub (中文) | 同步 | 否 | 30 基础分 |
| 中文 RSS | 同步 | 否 | 30 基础分 |
| YouTube | 同步 | 否 | 5 万播放 |
| Twitter KOL | 独立 | NITTER | 30 基础分 |
