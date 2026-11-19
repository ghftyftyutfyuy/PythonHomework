# -*- coding: utf-8 -*-
"""
实验四：本地文档智能审查与摘要 Agent

需求边界（对应指导书「步骤 1」）：
    输入  : 含多个 .txt / .md 的本地文件夹、自定义停用词表、自定义专业词典
    处理  : 批量读取 -> 文本清洗 -> 加载自定义词典 -> jieba 精确模式分词
            -> 过滤停用词与单字符 -> 统计词频
    输出  : Top50 高频词词云 PNG + 各文件核心关键词汇总报告（TXT / CSV）
    约束  : 完善的错误处理（文件不存在、编码错误）、中文字体正常显示

在 PyCharm 中直接运行本文件即可：结果会打印到运行窗口，同时落盘到 output/。
可选参数：
    --no-show   不弹出词云窗口（无界面环境 / 自动化验证时使用）
    --mask      可选的背景蒙版图片路径（会使用 numpy + pillow 处理）
"""

from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
from collections import Counter
from pathlib import Path

import jieba
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from wordcloud import WordCloud

jieba.setLogLevel(logging.ERROR)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DOCS = BASE_DIR / "docs"
DEFAULT_STOPWORDS = BASE_DIR / "stopwords.txt"
DEFAULT_USER_DICT = BASE_DIR / "user_dict.txt"
DEFAULT_OUTPUT = BASE_DIR / "output"

ENCODINGS = ("utf-8-sig", "utf-8", "gb18030")
TOP_N = 50
KEYWORDS_PER_FILE = 10
CORPUS_CHARS_PER_FILE = 300

# 未提供停用词表时的兜底集合
FALLBACK_STOPWORDS = {
    "的", "了", "和", "在", "是", "我", "你", "他", "我们", "他们",
    "为", "以", "等", "并", "对", "与", "及", "或", "也", "就",
    "都", "而", "其", "这", "那", "之", "于", "把", "被", "从",
    "到", "上", "中", "下", "个", "一些", "一个", "通过", "以及",
    "同时", "进一步", "不断", "可以", "需要", "能够", "具有", "进行",
}

TAG_RE = re.compile(r"<[^>]+>")
MD_RE = re.compile(r"[#>*`|_\-=~\[\]()]+")
WORD_RE = re.compile(r"[\u4e00-\u9fa5A-Za-z0-9]")


def find_chinese_font() -> str | None:
    """自动探测本机中文字体，避免词云出现方框。"""
    candidates = (
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("/System/Library/Fonts/Arial Unicode.ttf"),
    )
    for font in candidates:
        if font.exists():
            return str(font)
    return None


def read_text(path: Path) -> tuple[str, str]:
    """多编码回退读取，返回 (正文, 实际编码)。"""
    last_error: Exception | None = None
    for encoding in ENCODINGS:
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError as exc:
            last_error = exc
        except OSError as exc:
            raise RuntimeError(f"文件读取失败：{exc}") from exc
    raise RuntimeError(
        f"无法识别编码（已尝试 {', '.join(ENCODINGS)}）：{path.name}，最后一次错误：{last_error}"
    )


def clean_text(raw: str) -> str:
    """轻量文本清洗：去 HTML 标签、Markdown 装饰符、压缩空白。"""
    text = TAG_RE.sub(" ", raw)
    text = MD_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str, stopwords: set[str]) -> list[str]:
    """jieba 精确模式分词 + 过滤停用词与单字符。"""
    result = []
    for word in jieba.lcut(text, cut_all=False):
        word = word.strip()
        if len(word) > 1 and word not in stopwords and WORD_RE.search(word):
            result.append(word)
    return result


class DocumentAnalyzer:
    """本地文档智能审查 Agent 原型（面向对象，便于 watchdog / LLM 模块复用）。"""

    def __init__(
        self,
        docs_dir: Path = DEFAULT_DOCS,
        stopwords_file: Path = DEFAULT_STOPWORDS,
        user_dict_file: Path = DEFAULT_USER_DICT,
        output_dir: Path = DEFAULT_OUTPUT,
        font_path: str | None = None,
    ) -> None:
        self.docs_dir = Path(docs_dir)
        self.stopwords_file = Path(stopwords_file)
        self.user_dict_file = Path(user_dict_file)
        self.output_dir = Path(output_dir)
        self.font_path = font_path or find_chinese_font()
        self.stopwords: set[str] = set(FALLBACK_STOPWORDS)
        self.errors: list[str] = []

    # ---------- 配置加载 ----------
    def load_user_dict(self) -> int:
        if not self.user_dict_file.exists():
            self.errors.append(f"自定义词典不存在，已跳过：{self.user_dict_file}")
            return 0
        try:
            jieba.load_userdict(str(self.user_dict_file))
            with self.user_dict_file.open("r", encoding="utf-8-sig") as f:
                count = sum(1 for line in f if line.strip())
            return count
        except Exception as exc:  # noqa: BLE001
            self.errors.append(f"自定义词典加载失败：{exc}")
            return 0

    def load_stopwords(self) -> set[str]:
        if not self.stopwords_file.exists():
            self.errors.append(f"停用词表不存在，使用内置默认停用词：{self.stopwords_file}")
            return set(FALLBACK_STOPWORDS)
        try:
            raw, _ = read_text(self.stopwords_file)
            words = {line.strip() for line in raw.splitlines() if line.strip()}
            return words or set(FALLBACK_STOPWORDS)
        except RuntimeError as exc:
            self.errors.append(f"停用词表读取失败，使用内置默认停用词：{exc}")
            return set(FALLBACK_STOPWORDS)

    # ---------- 核心分析 ----------
    def collect_files(self) -> list[Path]:
        if not self.docs_dir.exists():
            raise FileNotFoundError(f"文档目录不存在：{self.docs_dir}")
        if not self.docs_dir.is_dir():
            raise NotADirectoryError(f"不是文件夹：{self.docs_dir}")
        files = sorted(
            p for p in self.docs_dir.iterdir()
            if p.is_file() and p.suffix.lower() in {".txt", ".md"}
        )
        return files

    def analyze(self) -> dict:
        files = self.collect_files()
        if not files:
            raise RuntimeError(
                f"目录下没有找到 .txt / .md 文档：{self.docs_dir}\n"
                "请把待审查文档放进 docs/ 文件夹后重新运行。"
            )

        details: list[dict] = []
        global_counter: Counter = Counter()
        corpus_parts: list[str] = []

        for path in files:
            try:
                raw, encoding = read_text(path)
                text = clean_text(raw)
                words = tokenize(text, self.stopwords)
                counter = Counter(words)
                global_counter.update(words)
                details.append({
                    "name": path.name,
                    "encoding": encoding,
                    "chars": len(text),
                    "tokens": len(words),
                    "top": counter.most_common(KEYWORDS_PER_FILE),
                })
                corpus_parts.append(f"【{path.name}】\n{text[:CORPUS_CHARS_PER_FILE]}")
            except Exception as exc:  # noqa: BLE001
                self.errors.append(f"处理文件 {path.name} 时发生错误：{exc}")

        if not global_counter:
            raise RuntimeError("未提取到有效词汇，请检查文档内容或停用词表是否把所有词都过滤掉了。")

        return {
            "files": files,
            "details": details,
            "global": global_counter,
            "top50": global_counter.most_common(TOP_N),
            "corpus": "\n\n".join(corpus_parts),
            "stopwords": self.stopwords,
        }

    # ---------- 输出 ----------
    def write_report(self, result: dict) -> tuple[Path, Path, Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        txt_path = self.output_dir / "keywords_report.txt"
        csv_path = self.output_dir / "keywords_report.csv"
        corpus_path = self.output_dir / "cleaned_corpus.txt"

        lines = [
            "=" * 60,
            "本地文档智能审查与摘要 —— 关键词汇总报告",
            "=" * 60,
            f"文档目录：{self.docs_dir}",
            f"文档数量：{len(result['details'])}",
            f"有效词总数：{sum(result['global'].values())}",
            f"去重词数：{len(result['global'])}",
            "",
            "一、全局 Top50 高频词",
            "-" * 60,
        ]
        for rank, (word, count) in enumerate(result["top50"], 1):
            lines.append(f"{rank:3d}. {word:<16} {count}")
        lines += ["", "二、各文件核心关键词", "-" * 60]
        for item in result["details"]:
            lines.append(
                f"\n[{item['name']}] 编码={item['encoding']} "
                f"字符={item['chars']} 有效词={item['tokens']}"
            )
            for rank, (word, count) in enumerate(item["top"], 1):
                lines.append(f"   {rank:2d}. {word:<16} {count}")
        if self.errors:
            lines += ["", "三、异常记录", "-" * 60] + [f"  ! {e}" for e in self.errors]
        txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["范围", "排名", "关键词", "词频", "文件"])
            for rank, (word, count) in enumerate(result["top50"], 1):
                writer.writerow(["全局", rank, word, count, "全部文档"])
            for item in result["details"]:
                for rank, (word, count) in enumerate(item["top"], 1):
                    writer.writerow(["单文件", rank, word, count, item["name"]])
        corpus_path.write_text(result["corpus"] + "\n", encoding="utf-8")
        return txt_path, csv_path, corpus_path

    def render_wordcloud(self, result: dict, mask_path: Path | None = None, show: bool = True) -> Path:
        if self.font_path is None:
            raise RuntimeError(
                "未找到中文字体，请用 --font 指定 msyh.ttc / simhei.ttf 的路径，否则词云会显示为方框。"
            )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        mask = None
        if mask_path is not None:
            if not mask_path.exists():
                raise FileNotFoundError(f"背景蒙版图片不存在：{mask_path}")
            mask = np.array(Image.open(str(mask_path)).convert("L"))

        wc = WordCloud(
            font_path=self.font_path,
            width=1000,
            height=800,
            background_color="white",
            max_words=TOP_N,
            collocations=False,
            mask=mask,
        ).generate_from_frequencies(dict(result["top50"]))

        image_path = self.output_dir / "document_wordcloud.png"
        wc.to_file(str(image_path))

        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
        plt.figure(figsize=(10, 8))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title("本地文档高频词云分析（Top50）", fontsize=16)
        plt.tight_layout()
        if show:
            plt.show()
        else:
            plt.close("all")
        return image_path


def print_console(result: dict, analyzer: DocumentAnalyzer, paths: dict) -> None:
    print("=" * 64)
    print("实验四：本地文档智能审查与摘要 Agent")
    print("=" * 64)
    print(f"文档目录  : {analyzer.docs_dir}")
    print(f"停用词    : {len(result['stopwords'])} 个")
    print(f"中文字体  : {analyzer.font_path or '未找到（将报错）'}")
    print(f"文档数量  : {len(result['details'])}")
    print("-" * 64)
    print("【逐文件处理结果】")
    for item in result["details"]:
        top3 = "、".join(f"{w}({c})" for w, c in item["top"][:3])
        print(
            f"  ✓ {item['name']:<28} {item['encoding']:<10} "
            f"{item['chars']:>5} 字符 / {item['tokens']:>4} 有效词 | Top3: {top3}"
        )
    for err in analyzer.errors:
        print(f"  ! {err}")
    print("-" * 64)
    print(f"全局有效词 {sum(result['global'].values())} 个，去重后 {len(result['global'])} 个")
    print(f"\n【全局 Top{TOP_N} 高频词】")
    for rank, (word, count) in enumerate(result["top50"], 1):
        print(f"  {rank:2d}. {word:<18} {count}")
    print("-" * 64)
    print("【输出文件】")
    for label, path in paths.items():
        print(f"  {label:<12} {path}")
    print("=" * 64)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="实验四：本地文档智能审查与摘要 Agent")
    parser.add_argument("--docs", type=Path, default=DEFAULT_DOCS, help="待审查文档目录")
    parser.add_argument("--stopwords", type=Path, default=DEFAULT_STOPWORDS, help="停用词表")
    parser.add_argument("--user-dict", type=Path, default=DEFAULT_USER_DICT, help="自定义词典")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="输出目录")
    parser.add_argument("--font", type=str, default=None, help="中文字体文件路径")
    parser.add_argument("--mask", type=Path, default=None, help="可选词云蒙版图片")
    parser.add_argument("--no-show", action="store_true", help="不弹出词云窗口")
    args = parser.parse_args(argv)

    analyzer = DocumentAnalyzer(
        docs_dir=args.docs,
        stopwords_file=args.stopwords,
        user_dict_file=args.user_dict,
        output_dir=args.output,
        font_path=args.font,
    )

    try:
        n_dict = analyzer.load_user_dict()
        analyzer.stopwords = analyzer.load_stopwords()
        print(f"[1/4] 自定义词典加载完成：{n_dict} 个词条")
        print(f"[2/4] 停用词表加载完成：{len(analyzer.stopwords)} 个词")
        print("[3/4] 批量读取 + 清洗 + 分词 + 词频统计 ...")

        result = analyzer.analyze()
        txt_path, csv_path, corpus_path = analyzer.write_report(result)
        print("[4/4] 生成汇总报告与词云 ...")

        image_path = analyzer.render_wordcloud(result, mask_path=args.mask, show=not args.no_show)
        print_console(result, analyzer, {
            "词云图片": image_path,
            "汇总报告TXT": txt_path,
            "汇总报告CSV": csv_path,
            "清洗语料TXT": corpus_path,
        })
        return 0
    except (FileNotFoundError, NotADirectoryError, RuntimeError) as exc:
        print(f"\n[运行中止] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
