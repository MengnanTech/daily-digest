# Daily Digest 更新日志

_最后更新：2026-03-31_

## 最新提交

### GitHub Actions 日程 + GitHub Pages 部署（Commit: `352ba4d`）
- 添加 GitHub Actions 定时调度（每日自动执行）
- 添加 GitHub Pages 自动部署

### 新增 6 个数据源 + 平台分组展示 + 批量 AI 摘要（Commit: `814cdc1`）
- 新增 6 个数据源（具体来源待确认，可能包括更多 RSS 源）
- 输出格式改为按平台分组展示
- 添加批量 AI 摘要功能（pipeline/summarizer.py）
- 优化结果展示结构

### 切换 uv 包管理器（Commit: `c08a0ca`）
- 从 pip/requirements.txt 迁移到 uv 包管理器
- 删除 requirements.txt，改用 pyproject.toml + uv.lock

### 初始提交（Commit: `7bbac3a`）
- 项目初始化：Daily Tech Digest — 多源科技新闻聚合器
- 实现基础 pipeline：抓取 → 去重 → 排序 → 输出
- 支持 HackerNews、ProductHunt、GitHub Trending 等核心数据源

## 功能路线图（待实现）

- [ ] Twitter KOL 完整集成（当前 twitter_kol.py 需要单独运行）
- [ ] AI 摘要接入（summarizer.py 当前直接透传，预留接口）
- [ ] 更多数据源（Hacker News 分类、IndieHackers 等）
- [ ] 个性化权重配置
- [ ] 邮件推送
- [ ] Telegram/Feishu 推送
