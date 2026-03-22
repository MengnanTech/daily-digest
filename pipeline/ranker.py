"""热度排序模块 - 跨平台归一化评分"""
from config import SOURCE_WEIGHTS


def rank_articles(articles: list[dict]) -> list[dict]:
    """
    跨平台热度排序：
    1. 将不同平台的分数归一化到 0-100
    2. 乘以平台权重
    3. 跨平台出现加分（同一条在 HN 和 Reddit 都出现 → 更重要）
    """
    for article in articles:
        source = article.get("source", "")
        config = SOURCE_WEIGHTS.get(source, {"score_base": 1, "weight": 0.5})

        raw_score = article.get("score", 0)
        score_base = config["score_base"]
        weight = config["weight"]

        # 归一化到 0-100
        if score_base > 0 and raw_score > 0:
            normalized = min(100, (raw_score / score_base) * 100)
        else:
            # RSS / Twitter 等没有分数的源，给基础分
            normalized = 30  # 权威媒体基础保底分

        # 加权
        weighted = normalized * weight

        # 跨平台加分：每多出现一个平台 +15 分
        also_on = article.get("also_on", [])
        cross_platform_bonus = len(also_on) * 15

        article["final_score"] = weighted + cross_platform_bonus

    # 按最终分数降序排列
    return sorted(articles, key=lambda x: x.get("final_score", 0), reverse=True)
