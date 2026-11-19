# -*- coding: utf-8 -*-
"""
实验四 · 进阶探索 1：蒙特卡洛模拟

针对「文档中不确定性指标」做随机抽样与概率分布预测：
  指标 A：按词频概率随机抽取 20 个词，命中核心关键词（Top10）的数量分布；
  指标 B：对最高频主题词的出现概率做 bootstrap，给出 95% 置信区间。

统计结果会写入 output/monte_carlo_context.txt，作为后续大模型审查的补充上下文。
在 PyCharm 中直接运行即可，结果打印在运行窗口。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from main import DocumentAnalyzer  # noqa: E402

OUTPUT = BASE_DIR / "output"
N_SIM = 20000
DRAW_K = 20
N_BOOTSTRAP = 2000
SEED = 2026


def build_distribution() -> tuple[list[str], np.ndarray]:
    analyzer = DocumentAnalyzer()
    analyzer.load_user_dict()
    analyzer.stopwords = analyzer.load_stopwords()
    result = analyzer.analyze()
    words = [w for w, _ in result["top50"]]
    counts = np.array([c for _, c in result["top50"]], dtype=float)
    return words, counts / counts.sum()


def main() -> int:
    rng = np.random.default_rng(SEED)
    words, probs = build_distribution()
    core = set(words[:10])
    core_mask = np.array([w in core for w in words])

    # 指标 A：一次抽 20 个词，命中核心词的数量分布
    samples = rng.choice(len(words), size=(N_SIM, DRAW_K), p=probs)
    hits = core_mask[samples].sum(axis=1)

    # 指标 B：最高频主题词出现概率的 bootstrap 区间
    boot_p = []
    for _ in range(N_BOOTSTRAP):
        boot = rng.multinomial(1000, probs)
        boot_p.append(boot[0] / 1000)
    boot_p = np.array(boot_p)
    lo, hi = np.percentile(boot_p, [2.5, 97.5])

    print("=" * 64)
    print("进阶 1：蒙特卡洛模拟（文档关键词不确定性分析）")
    print("=" * 64)
    print(f"候选词数        : {len(words)}")
    print(f"核心关键词集合  : {'、'.join(words[:10])}")
    print(f"模拟次数        : {N_SIM}，每次抽取 {DRAW_K} 个词")
    print("-" * 64)
    print(f"指标 A  命中核心词数量  均值 = {hits.mean():.3f}，标准差 = {hits.std():.3f}")
    print(f"        95% 区间 = [{np.percentile(hits, 2.5):.0f}, {np.percentile(hits, 97.5):.0f}]")
    print(f"        至少命中 1 个核心词的概率 = {(hits >= 1).mean():.4f}")
    print("        命中数分布：")
    for h in range(int(hits.max()) + 1):
        p = (hits == h).mean()
        print(f"          {h:2d} 个 | {'█' * int(p * 60):<60} | {p:.4f}")
    print("-" * 64)
    print(f"指标 B  最高频主题词「{words[0]}」")
    print(f"        点估计 = {probs[0]:.4f}，bootstrap 95% 区间 = [{lo:.4f}, {hi:.4f}]")
    print("=" * 64)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    context = (
        "【蒙特卡洛模拟补充上下文】\n"
        f"按词频概率随机抽取 {DRAW_K} 个词、共模拟 {N_SIM} 次：命中核心关键词数量的均值为 "
        f"{hits.mean():.2f}，标准差 {hits.std():.2f}，95% 区间 "
        f"[{np.percentile(hits, 2.5):.0f}, {np.percentile(hits, 97.5):.0f}]；"
        f"至少命中 1 个核心词的概率为 {(hits >= 1).mean():.2%}。\n"
        f"对最高频主题词「{words[0]}」做 {N_BOOTSTRAP} 次 bootstrap，出现概率点估计 "
        f"{probs[0]:.2%}，95% 置信区间 [{lo:.2%}, {hi:.2%}]。\n"
        "解读：核心词在随机抽样中稳定出现，说明文档主题集中度较高；置信区间可用于判断"
        "「某主题是否被过度强调」，为审查意见提供量化依据。\n"
    )
    path = OUTPUT / "monte_carlo_context.txt"
    path.write_text(context, encoding="utf-8")
    print(f"补充上下文已保存：{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
