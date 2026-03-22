import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
PH_TOKEN = os.getenv("PH_TOKEN", "")
V2EX_TOKEN = os.getenv("V2EX_TOKEN", "")
NITTER_INSTANCE = os.getenv("NITTER_INSTANCE", "https://nitter.privacydev.net")

# ── 英文 RSS 源 ──────────────────────────────────
RSS_FEEDS = {
    # 科技媒体
    "techcrunch": "https://techcrunch.com/feed/",
    "theverge": "https://www.theverge.com/rss/index.xml",
    "arstechnica": "https://feeds.arstechnica.com/arstechnica/index",
    "mit_tech": "https://www.technologyreview.com/feed/",
    "wired": "https://www.wired.com/feed/rss",
    # 开发者
    "changelog": "https://changelog.com/feed",
    "infoq": "https://feed.infoq.com/",
    "echojs": "https://www.echojs.com/rss",
    "slashdot": "https://rss.slashdot.org/Slashdot/slashdotMain",
    # AI 专项
    "aiweekly": "https://aiweekly.co/feed",
    "thenewstack": "https://thenewstack.io/feed/",
}

# ── 中文 RSS 源（直接订阅）──────────────────────
CN_RSS_FEEDS = {
    "ruanyifeng": "https://www.ruanyifeng.com/blog/atom.xml",
    "geekpark": "https://www.geekpark.net/rss",
}

# ── RSSHub 源（多实例备选）─────────────────────
RSSHUB_INSTANCES = [
    "https://rsshub.rssforever.com",
    "https://rsshub.pseudoyu.com",
    "https://rsshub.app",
]

RSSHUB_ROUTES = {
    # 中文科技
    "36kr": "/36kr/hot-list",
    "sspai": "/sspai/matrix",
    "juejin": "/juejin/trending/all/1",
    "zhihu": "/zhihu/hot",
    "oschina": "/oschina/news",
    "ifanr": "/ifanr/app",
    "cls": "/cls/telegraph",  # 财联社电报（快讯）
}

# ── Reddit 子版块 ─────────────────────────────
REDDIT_SUBREDDITS = [
    "programming",
    "technology",
    "MachineLearning",
    "artificial",
    "startups",
    "SideProject",
]

# ── Twitter KOL 列表 ──────────────────────────
TWITTER_KOLS = {
    # AI
    "sama": "AI",
    "karpathy": "AI/ML",
    "ylecun": "AI/ML",
    "AndrewYNg": "AI",
    "EMostaque": "AI",
    # 独立开发
    "levelsio": "独立开发",
    "marclouvion": "独立开发",
    "taborein": "独立开发",
    "dannypostmaa": "独立开发",
    # 科技新闻
    "techcrunch": "科技新闻",
    "ProductHunt": "产品发布",
    # 中文科技
    "dotey": "AI/中文",
    "op7418": "AI/中文",
    "starzqeth": "Web3/中文",
}

# ── 热度排序权重 ──────────────────────────────
SOURCE_WEIGHTS = {
    # 英文社区
    "hackernews": {"score_base": 100, "weight": 1.0},
    "producthunt": {"score_base": 200, "weight": 0.8},
    "github": {"score_base": 500, "weight": 0.7},
    "devto": {"score_base": 50, "weight": 0.6},
    "lobsters": {"score_base": 30, "weight": 0.9},
    "reddit": {"score_base": 200, "weight": 0.7},
    # 英文媒体
    "techcrunch": {"score_base": 1, "weight": 0.9},
    "theverge": {"score_base": 1, "weight": 0.8},
    "arstechnica": {"score_base": 1, "weight": 0.7},
    "mit_tech": {"score_base": 1, "weight": 0.8},
    "wired": {"score_base": 1, "weight": 0.7},
    "changelog": {"score_base": 1, "weight": 0.6},
    "infoq": {"score_base": 1, "weight": 0.7},
    "echojs": {"score_base": 1, "weight": 0.5},
    "slashdot": {"score_base": 1, "weight": 0.6},
    "aiweekly": {"score_base": 1, "weight": 0.7},
    "thenewstack": {"score_base": 1, "weight": 0.6},
    # 中文
    "v2ex": {"score_base": 30, "weight": 0.5},
    "36kr": {"score_base": 1, "weight": 0.7},
    "sspai": {"score_base": 1, "weight": 0.6},
    "juejin": {"score_base": 1, "weight": 0.5},
    "zhihu": {"score_base": 1, "weight": 0.6},
    "oschina": {"score_base": 1, "weight": 0.5},
    "ifanr": {"score_base": 1, "weight": 0.6},
    "cls": {"score_base": 1, "weight": 0.5},
    "ruanyifeng": {"score_base": 1, "weight": 0.7},
    "geekpark": {"score_base": 1, "weight": 0.6},
    # 社交/视频
    "twitter": {"score_base": 1, "weight": 0.7},
    "youtube": {"score_base": 50000, "weight": 0.6},  # 5万播放 = 满分
}
