# -*- coding: utf-8 -*-

# ============================================================
# 【答辩速读】进阶 2：把分析结果组装成给大模型看的结构化 Prompt
# 一句话：读三个上游产物（关键词报告 / 清洗语料 / 蒙特卡洛结论），拼成一份
#         带角色设定、材料清单、输出格式要求的 Prompt，让大模型出审查意见。
# 【重要·如实回答】本实验没有真的调用大模型：没配 LLM_API_KEY，脚本做的是
#   「组装 + 保存 Prompt + 安全降级」。老师问「调用了吗」要如实说没有，
#   配了密钥才会走 requests.post 去请求 OpenAI 兼容接口。
# Prompt 结构：三段材料 + 四段输出要求（主题综述/核心要点/审查意见/一句话摘要）。
# 老师常问：为什么不把整篇文档塞进去？接口怎么调？密钥放哪里？
# ============================================================

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


# 上游产物可能还没生成，缺文件时返回占位文字而不是报错，
# 保证这个脚本单独运行也能看到结果（容错设计）。
def read_or_default(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    return path.read_text(encoding="utf-8")


# 组装 Prompt：把「关键词+词频」「清洗语料」「蒙特卡洛结论」三段材料拼进去，
# 并明确规定输出要分四部分。要求「不要臆造材料之外的信息」是关键约束，
# 用来抑制大模型编内容（幻觉）。
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
    # 截断长度：控制 Prompt 的 token 数和费用，也避免超出模型上下文；
    # 只取开头是最简单的策略，改进时可以按关键词密度挑片段。
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


# 可选分支：没配置密钥就直接返回 None，不发起任何外部请求；
# 有密钥才真正调用接口并返回审查文本。
def call_llm(prompt: str) -> str | None:
    # 密钥只从环境变量读取，不写死在代码里，这是基本的安全常识
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return None

    import requests

    # 接口地址和模型名也做成可配置，换国产大模型只需改环境变量
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    try:
        # OpenAI 兼容接口：POST /chat/completions，请求头带 Bearer 密钥，
        # messages 里放一条 user 消息，timeout=30 防止网络卡死。
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
            # temperature=0.3 调低「随机性」，审查类任务要稳定保守，不要自由发挥
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    # 网络/密钥/超时出错统统降级为「只输出 Prompt」，不崩也不假装调用成功
    except Exception as exc:  # noqa: BLE001
        print(f"[提示] 大模型调用失败，已降级为仅输出 Prompt：{exc}")
        return None


# 主流程：组 Prompt -> 打印并保存 -> 尝试调用 -> 有结果就写 llm_review.md
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

    # 没密钥时 review 是 None，走下面的降级提示分支
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


# 直接运行才执行；被 import 时不自动跑
if __name__ == "__main__":
    raise SystemExit(main())
