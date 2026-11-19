# -*- coding: utf-8 -*-
"""
实验五 · 步骤 2 第 2 小步：解析 HTML 提取字段

验证目标：打印前 3 条数据，确认「文章标题 / 发布时间 / 作者 / 链接」解析逻辑正确。
字段缺失时填空字符串（不抛异常、不丢整条记录），为步骤 3 的持久化做准备。
"""

from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from step1_fetch import BASE_URL, FIELDS, obtain_html


def parse_news_list(html: str, base_url: str = BASE_URL) -> tuple[list[dict], list[str]]:
    """解析列表页，返回 (记录列表, 异常说明列表)。"""
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict] = []
    errors: list[str] = []

    items = soup.select("li.news-item")
    if not items:
        # 兼容其它站点常见的 class 命名
        items = soup.select(".news-item, article, .list-item")

    for index, item in enumerate(items, 1):
        try:
            a_tag = item.select_one("h2 a") or item.select_one("a")
            time_tag = item.select_one("time")
            author_tag = item.select_one(".author")

            title = a_tag.get_text(strip=True) if a_tag else ""
            href = a_tag.get("href", "") if a_tag else ""
            link = urljoin(base_url, href) if href else ""
            pub_time = ""
            if time_tag:
                pub_time = time_tag.get("datetime") or time_tag.get_text(strip=True)
            author = ""
            if author_tag:
                author = author_tag.get_text(strip=True).removeprefix("作者：").strip()

            records.append({
                FIELDS[0]: title,
                FIELDS[1]: pub_time,
                FIELDS[2]: author,
                FIELDS[3]: link,
            })
        except Exception as exc:  # noqa: BLE001
            errors.append(f"第 {index} 条解析失败，已跳过：{exc}")

    return records, errors


def main() -> int:
    print("=" * 64)
    print("步骤 2-2：解析 HTML 提取字段")
    print("=" * 64)
    html, code, source, offline = obtain_html()
    records, errors = parse_news_list(html)
    print(f"页面来源    : {source}")
    print(f"解析到条目  : {len(records)} 条")
    print("-" * 64)
    print("前 3 条数据预览：")
    for i, row in enumerate(records[:3], 1):
        print(f"  [{i}] 标题：{row[FIELDS[0]]}")
        print(f"      时间：{row[FIELDS[1]]} | 作者：{row[FIELDS[2]]}")
        print(f"      链接：{row[FIELDS[3]]}")
    print("-" * 64)
    missing = {f: sum(1 for r in records if not r[f]) for f in FIELDS}
    print(f"字段缺失统计（填 '' 处理）：{missing}")
    for err in errors:
        print(f"  ! {err}")
    print("-" * 64)
    if records and all(row[FIELDS[0]] for row in records):
        print("验证通过：标题全部解析成功，字段缺失已填空字符串，可进入持久化环节。")
        return 0
    print("验证失败：未解析到有效记录。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
