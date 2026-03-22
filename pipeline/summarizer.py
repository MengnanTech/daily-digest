"""AI 摘要生成模块 - 使用 DeepSeek API"""
import json
import httpx
from config import DEEPSEEK_API_KEY

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"

SYSTEM_PROMPT = """你是一个科技新闻编辑。你的任务是为每篇文章生成简洁的中文摘要。

要求：
1. 每条摘要不超过80字
2. 说清楚"谁做了什么，有什么影响"
3. 使用中文输出
4. 从以下类别中选一个标签：AI、前端、后端、开源、创业、行业动态、开发工具、移动端
5. 输出严格的 JSON 数组格式"""

USER_PROMPT_TEMPLATE = """请为以下 {count} 篇文章生成摘要和分类标签：

{articles}

输出格式（JSON 数组）：
[
  {{"index": 0, "summary": "中文摘要", "category": "分类标签"}},
  ...
]

只输出 JSON，不要其他文字。"""


async def summarize_articles(articles: list[dict]) -> list[dict]:
    """为文章列表生成 AI 摘要"""
    if not DEEPSEEK_API_KEY:
        print("⚠️ 未设置 DEEPSEEK_API_KEY，跳过 AI 摘要")
        for a in articles:
            a["summary"] = a.get("content", a.get("title", ""))[:80]
            a["category"] = "行业动态"
        return articles

    # 构建文章列表文本
    articles_text = "\n\n".join([
        f"[{i}] 标题: {a.get('title', '')}\n来源: {a.get('source', '')}\n内容: {a.get('content', '')[:500]}"
        for i, a in enumerate(articles)
    ])

    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                DEEPSEEK_API,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                            count=len(articles),
                            articles=articles_text,
                        )},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 4000,
                },
                timeout=60,
            )
            r.raise_for_status()

            content = r.json()["choices"][0]["message"]["content"]
            # 提取 JSON（可能被包裹在 ```json ``` 中）
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]

            summaries = json.loads(content)

            # 合并摘要到文章数据中
            for item in summaries:
                idx = item.get("index", -1)
                if 0 <= idx < len(articles):
                    articles[idx]["summary"] = item.get("summary", "")
                    articles[idx]["category"] = item.get("category", "行业动态")

        except Exception as e:
            print(f"⚠️ AI 摘要生成失败: {e}")
            # 降级：使用内容前 80 字作为摘要
            for a in articles:
                if not a.get("summary"):
                    a["summary"] = a.get("content", a.get("title", ""))[:80]
                    a["category"] = "行业动态"

    return articles
