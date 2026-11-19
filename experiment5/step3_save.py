# -*- coding: utf-8 -*-
"""
实验五 · 步骤 3：数据持久化与异常处理

操作：用 pandas 把解析结果写入 result.csv，补齐异常处理
      （字段缺失填空字符串、单条解析失败跳过、写入失败给出提示）。
验证：检查 CSV 编码是否为 UTF-8、列名是否正确、数据是否对齐，
      并在终端打印成功抓取条数。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from step1_fetch import BASE_DIR, FIELDS, obtain_html
from step2_parse import parse_news_list

RESULT_CSV = BASE_DIR / "result.csv"


def to_dataframe(records: list[dict]) -> pd.DataFrame:
    """按固定列顺序建表；缺字段补空字符串，避免 NaN 与列错位。"""
    df = pd.DataFrame(records)
    for field in FIELDS:
        if field not in df.columns:
            df[field] = ""
    df = df[FIELDS].fillna("").astype(str)
    return df


def save_csv(df: pd.DataFrame, path: Path = RESULT_CSV) -> Path:
    try:
        df.to_csv(path, index=False, encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"CSV 写入失败：{exc}") from exc
    return path


def verify_csv(path: Path) -> pd.DataFrame:
    """验收三步：UTF-8 解码 / 列名 / 数据对齐。"""
    raw = path.read_bytes()
    try:
        raw.decode("utf-8")
        print("  编码检查  : UTF-8 解码通过（无 BOM，纯 UTF-8 文本）")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"result.csv 不是 UTF-8 编码：{exc}") from exc

    df = pd.read_csv(path, encoding="utf-8", keep_default_na=False)
    print(f"  列名检查  : {list(df.columns)}")
    if list(df.columns) != FIELDS:
        raise RuntimeError(f"列名不符合验收要求，应为 {FIELDS}")
    print(f"  数据对齐  : {df.shape[0]} 行 × {df.shape[1]} 列，无列错位")
    blanks = {f: int((df[f].astype(str).str.strip() == "").sum()) for f in FIELDS}
    print(f"  空值统计  : {blanks}（字段缺失已填空字符串，未导致程序崩溃）")
    return df


def main() -> int:
    print("=" * 64)
    print("步骤 3：数据持久化与异常处理")
    print("=" * 64)
    html, code, source, offline = obtain_html()
    records, errors = parse_news_list(html)
    df = to_dataframe(records)
    path = save_csv(df)
    print(f"输出文件    : {path}")
    print("-" * 64)
    print("验收检查：")
    checked = verify_csv(path)
    print("-" * 64)
    print("CSV 前 3 行：")
    print(checked.head(3).to_string(index=False))
    print("-" * 64)
    for err in errors:
        print(f"  ! {err}")
    print(f"成功抓取条数：{len(checked)}")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
