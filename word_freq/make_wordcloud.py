# -*- coding: utf-8 -*-
import csv
import logging
import re
from collections import Counter
from pathlib import Path

import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud

jieba.setLogLevel(logging.ERROR)


BASE_DIR = Path(__file__).resolve().parent
TXT_PATH = BASE_DIR / "report.txt"
CSV_PATH = BASE_DIR / "hot_words.csv"
WORDCLOUD_PATH = BASE_DIR / "wordcloud.png"
TOP_N = 30


USER_WORDS = [
    "十五五",
    "十四五",
    "新质生产力",
    "高质量发展",
    "中国式现代化",
    "科技自立自强",
    "国内国际双循环",
    "全过程人民民主",
    "碳达峰碳中和",
    "乡村振兴",
    "数字中国",
    "现代化产业体系",
    "共同富裕",
    "高水平对外开放",
    "区域协调发展",
    "教育强国",
    "科技强国",
    "人才强国",
]


STOPWORDS = {
    "的", "了", "和", "与", "及", "或", "在", "是", "为", "对",
    "从", "到", "以", "要", "等", "上", "中", "下", "把", "被",
    "向", "按", "按照", "通过", "以及", "围绕", "进一步", "全面",
    "各", "每", "个", "一些", "有关", "之间", "其中", "同时",
    "不仅", "而且", "但是", "因此", "如果", "我们", "他们",
}


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"请先把文章保存为：{path}")

    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise RuntimeError(
        f"无法识别文件编码：{path}\n"
        "请用记事本打开文章，另存为 report.txt，编码选择 UTF-8。"
    )


def is_valid_word(word: str) -> bool:
    return (
        len(word) >= 2
        and word not in STOPWORDS
        and re.search(r"[\u4e00-\u9fa5A-Za-z]", word) is not None
    )


def count_hot_words(text: str):
    for word in USER_WORDS:
        jieba.add_word(word)

    words = jieba.lcut(text)
    words = [word.strip() for word in words]
    words = [word for word in words if is_valid_word(word)]

    return Counter(words)


def save_csv(counter: Counter):
    with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["排名", "词语", "次数"])

        for rank, (word, count) in enumerate(counter.most_common(TOP_N), start=1):
            writer.writerow([rank, word, count])


def show_wordcloud(counter: Counter):
    font_path = None
    for font in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"):
        if Path(font).exists():
            font_path = font
            break

    wc = WordCloud(
        font_path=font_path,
        background_color="white",
        width=1200,
        height=800,
        max_words=100,
        prefer_horizontal=0.9,
        colormap="viridis",
    ).generate_from_frequencies(counter)

    plt.figure(figsize=(12, 8), dpi=120)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("十五五发展规划报告词云", fontsize=18)
    plt.tight_layout()

    wc.to_file(str(WORDCLOUD_PATH))
    plt.show()


if __name__ == "__main__":

    text = load_text(TXT_PATH)
    counter = count_hot_words(text)

    print(f"统计文件：{TXT_PATH}")
    print(f"输出文件：{CSV_PATH}")
    print(f"词云文件：{WORDCLOUD_PATH}")
    print(f"\n热词频率 Top {TOP_N}：\n")

    for rank, (word, count) in enumerate(counter.most_common(TOP_N), start=1):
        print(f"{rank:2d}. {word:<20} {count}")

    save_csv(counter)
    show_wordcloud(counter)
