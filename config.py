import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
PH_TOKEN = os.getenv("PH_TOKEN", "")
V2EX_TOKEN = os.getenv("V2EX_TOKEN", "")
NITTER_INSTANCE = os.getenv("NITTER_INSTANCE", "https://nitter.privacydev.net")

# RSS 源配置
RSS_FEEDS = {
    "techcrunch": "https://techcrunch.com/feed/",
    "theverge": "https://www.theverge.com/rss/index.xml",
    "arstechnica": "https://feeds.arstechnica.com/arstechnica/index",
    "mit_tech": "https://www.technologyreview.com/feed/",
    "wired": "https://www.wired.com/feed/rss",
}

# 36氪通过 RSSHub（多个实例备选）
RSSHUB_FEEDS = {
    "36kr": [
        "https://rsshub.rssforever.com/36kr/hot-list",
        "https://rsshub.pseudoyu.com/36kr/hot-list",
        "https://rsshub.app/36kr/hot-list",
    ],
}

# Twitter KOL 列表
TWITTER_KOLS = {
    "levelsio": "独立开发",
    "sama": "AI",
    "karpathy": "AI/ML",
    "marclouvion": "独立开发",
    "techcrunch": "科技新闻",
    "ProductHunt": "产品发布",
}

# 热度排序权重
SOURCE_WEIGHTS = {
    "hackernews": {"score_base": 100, "weight": 1.0},
    "producthunt": {"score_base": 200, "weight": 0.8},
    "github": {"score_base": 500, "weight": 0.7},
    "devto": {"score_base": 50, "weight": 0.6},
    "v2ex": {"score_base": 30, "weight": 0.5},
    "twitter": {"score_base": 1, "weight": 0.7},
    "techcrunch": {"score_base": 1, "weight": 0.9},
    "theverge": {"score_base": 1, "weight": 0.8},
    "arstechnica": {"score_base": 1, "weight": 0.7},
    "36kr": {"score_base": 1, "weight": 0.7},
}
