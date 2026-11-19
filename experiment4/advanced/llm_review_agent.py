# -*- coding: utf-8 -*-
"""
实验四 · 进阶探索 2：对接大模型 API 生成文档审查意见 / 摘要

链路：Top50 关键词与词频 + 清洗后的核心文本片段 + 蒙特卡洛补充上下文
      -> 组装结构化 Prompt -> 调用大模型（OpenAI 兼容接口）-> 结构化审查报告。

无网络 / 未配置密钥时不会报错：脚本会打印并保存组装好的 Prompt，
明确说明「未发起外部请求」，保证在 PyCharm 中可直接运行、结果可见。

配置环境变量（可选）：
    LLM_API_KEY    API 密钥
    LLM_BASE_URL   接口地址，默认 https://api.openai.com/v1
    LLM_MODEL      模型名，默认 gpt-4o-mini
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = BASE_DIR / "output"


def read_or_default(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    return path.read_text(encoding="utf-8")


def build_prompt() -> str:
    keywords = read_or_default(
        OUTPUT / "keywords_report.txt",
        "[尚未生成，请先运行 main.py]",
    )
    corpus = read_or_default(
        OUTPUT / "cleaned_corpus.txt",
        "[尚未生成，请先运行 main.py]",
    )
    montecarlo = read_or_default(
        OUTPUT / "monte_carlo_context.txt",
        "[尚未生成，可先运行 advanced/monte_carlo_simulation.py]",
    )
    # 控制长度，避免把整篇语料塞进 Prompt
    corpus_excerpt = corpus[:1200]
    keyword_excerpt = keywords[:1600]

    return (
        "你是「本地文档智能审查与摘要 Agent」。请基于以下由本地脚本自动提取的材料，"
        "对这批文档做一次结构化审查，不要臆造材料之外的信息。\n\n"
        "【一、Top50 关键词与词频 / 各文件核心关键词】\n"
        f"{keyword_excerpt}\n\n"
        "【二、清洗后的核心文本片段】\n"
        f"{corpus_excerpt}\n\n"
        "【三、蒙特卡洛模拟补充上下文】\n"
        f"{montecarlo}\n\n"
        "【输出要求】请依次给出四部分，使用 Markdown 小标题：\n"
        "1. 主题综述：用 3~5 句话概括这批文档共同关注的方向；\n"
        "2. 核心要点：列出 5 条要点，每条注明主要依据的关键词；\n"
        "3. 审查意见：指出 3 个值得核查或补充的地方（如数据口径、论证缺口、"
        "风险提示、表述不一致），并说明判断依据；\n"
        "4. 一句话摘要：不超过 40 字。\n"
    )


def call_llm(prompt: str) -> str | None:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return None

    import requests

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        print(f"[提示] 大模型调用失败，已降级为仅输出 Prompt：{exc}")
        return None


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt()

    print("=" * 64)
    print("进阶 2：大模型文档审查 Agent（Prompt 组装）")
    print("=" * 64)
    print(prompt)
    print("=" * 64)

    prompt_path = OUTPUT / "review_prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    print(f"结构化 Prompt 已保存：{prompt_path}")

    review = call_llm(prompt)
    if review is None:
        print("未配置 LLM_API_KEY 或调用失败：本次未发起外部请求，仅生成并保存 Prompt。")
        print("配置密钥后重新运行即可自动获得结构化审查报告 output/llm_review.md。")
        return 0

    review_path = OUTPUT / "llm_review.md"
    review_path.write_text(review + "\n", encoding="utf-8")
    print("-" * 64)
    print("【大模型返回的审查报告】")
    print(review)
    print(f"\n审查报告已保存：{review_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
