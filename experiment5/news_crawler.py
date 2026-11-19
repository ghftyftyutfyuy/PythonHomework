# -*- coding: utf-8 -*-
"""
实验五 · 步骤 4：代码审查与工程化重构（最终版）

把步骤 1~3 的过程式脚本重构为面向对象的 NewsCrawler 类，功能保持一致：
    获取 HTML -> 解析「文章标题 / 发布时间 / 作者 / 链接」-> 写入 result.csv
    -> 验收检查 -> 打印成功抓取条数。

重构要点（相对步骤 3 的改进）：
    1. 请求会话、重试策略、解析选择器、字段定义全部收进类属性，便于替换目标站点；
    2. fetch / parse / to_frame / save / verify 拆为单一职责方法，可分别单测；
    3. 统一异常处理：字段缺失填空字符串、单条解析失败跳过、网络失败降级离线样本；
    4. 反爬合规：User-Agent 伪装、请求间隔 ≥2 秒、超时重试 3 次、只抓公开列表页。

在 PyCharm 中直接运行本文件即可（默认离线样本页，结果打印在运行窗口）。
真实抓取示例：
    python news_crawler.py --url "https://<公开新闻站点>/list.html"
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_PAGE = BASE_DIR / "sample_page.html"
DEFAULT_OUTPUT = BASE_DIR / "result.csv"
FALLBACK_BASE_URL = "https://news.example.com"

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


class NewsCrawler:
    """静态新闻列表页爬虫（Vibe Coding 重构版）。"""

    FIELDS = ["文章标题", "发布时间", "作者", "链接"]
    LIST_SELECTOR = "li.news-item"
    ALT_SELECTORS = (".news-item", "article", ".list-item")

    def __init__(
        self,
        url: str = "",
        output: Path = DEFAULT_OUTPUT,
        base_url: str | None = None,
        delay: float = 2.0,
        retries: int = 3,
        timeout: int = 10,
        user_agent: str = DEFAULT_UA,
        min_delay: float = 2.0,
    ) -> None:
        self.url = url.strip()
        self.output = Path(output)
        self.base_url = base_url or self.url or FALLBACK_BASE_URL
        self.delay = max(float(delay), min_delay)  # 强制不低于 2 秒
        self.retries = max(int(retries), 1)
        self.timeout = int(timeout)
        self.user_agent = user_agent
        self.sample_page = SAMPLE_PAGE
        self.errors: list[str] = []
        self.offline = False
        self.source = ""
        self.status_code = 0

    # ---------- 1. 获取页面 ----------
    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        })
        return session

    def _fetch_remote(self) -> tuple[str, int, str]:
        session = self._build_session()
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                time.sleep(self.delay)
                resp = session.get(self.url, timeout=self.timeout)
                resp.raise_for_status()
                if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
                    resp.encoding = resp.apparent_encoding
                return resp.text, resp.status_code, resp.url
            except requests.RequestException as exc:
                last_error = exc
                self.errors.append(f"第 {attempt}/{self.retries} 次请求失败：{exc}")
        raise RuntimeError(f"重试 {self.retries} 次后仍无法获取页面：{last_error}")

    def fetch(self) -> str:
        """返回 HTML；真实抓取失败时降级到离线样本页，保证验证闭环。"""
        if self.url:
            try:
                html, code, source = self._fetch_remote()
                self.status_code, self.source, self.offline = code, source, False
                return html
            except RuntimeError as exc:
                self.errors.append(f"真实抓取失败，已降级：{exc}")
        if not self.sample_page.exists():
            raise FileNotFoundError(f"离线样本页不存在：{self.sample_page}")
        html = self.sample_page.read_text(encoding="utf-8")
        self.status_code = 200
        self.source = f"file:///{self.sample_page.as_posix()}"
        self.offline = True
        return html

    # ---------- 2. 解析字段 ----------
    def _items(self, soup: BeautifulSoup) -> list:
        items = soup.select(self.LIST_SELECTOR)
        if items:
            return items
        for selector in self.ALT_SELECTORS:
            items = soup.select(selector)
            if items:
                return items
        return []

    def parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        records: list[dict] = []
        for index, item in enumerate(self._items(soup), 1):
            try:
                a_tag = item.select_one("h2 a") or item.select_one("a")
                time_tag = item.select_one("time")
                author_tag = item.select_one(".author")

                title = a_tag.get_text(strip=True) if a_tag else ""
                href = a_tag.get("href", "") if a_tag else ""
                link = urljoin(self.base_url, href) if href else ""
                pub_time = ""
                if time_tag:
                    pub_time = time_tag.get("datetime") or time_tag.get_text(strip=True)
                author = ""
                if author_tag:
                    author = author_tag.get_text(strip=True).removeprefix("作者：").strip()

                records.append(dict(zip(self.FIELDS, (title, pub_time, author, link))))
            except Exception as exc:  # noqa: BLE001
                self.errors.append(f"第 {index} 条解析失败，已跳过：{exc}")
        return records

    # ---------- 3. 持久化 ----------
    def to_frame(self, records: list[dict]) -> pd.DataFrame:
        df = pd.DataFrame(records)
        for field in self.FIELDS:
            if field not in df.columns:
                df[field] = ""
        return df[self.FIELDS].fillna("").astype(str)

    def save(self, df: pd.DataFrame) -> Path:
        self.output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output, index=False, encoding="utf-8")
        return self.output

    # ---------- 4. 验收 ----------
    def verify(self, path: Path) -> pd.DataFrame:
        raw = path.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise RuntimeError(f"result.csv 不是 UTF-8 编码：{exc}") from exc
        df = pd.read_csv(path, encoding="utf-8", keep_default_na=False)
        if list(df.columns) != self.FIELDS:
            raise RuntimeError(f"列名不符合验收要求，应为 {self.FIELDS}")
        return df

    # ---------- 5. 完整流程 ----------
    def run(self) -> int:
        print("=" * 64)
        print("实验五 · NewsCrawler（重构版）")
        print("=" * 64)
        print(f"目标        : {self.url or '（未配置，使用离线样本页）'}")
        print(f"User-Agent  : 已设置（{self.user_agent[:40]}...）")
        print(f"请求间隔    : {self.delay} 秒（≥2 秒） | 超时重试：{self.retries} 次")
        print("-" * 64)

        html = self.fetch()
        print(f"页面来源    : {self.source}")
        print(f"运行模式    : {'离线样本页（验证闭环）' if self.offline else '真实网络抓取'}")
        print(f"状态码      : {self.status_code} | HTML 长度：{len(html)} 字符")

        records = self.parse(html)
        df = self.to_frame(records)
        path = self.save(df)
        checked = self.verify(path)

        print("-" * 64)
        print(f"输出文件    : {path}")
        print(f"列名        : {list(checked.columns)}")
        print(f"数据规模    : {checked.shape[0]} 行 × {checked.shape[1]} 列")
        blanks = {f: int((checked[f].astype(str).str.strip() == "").sum()) for f in self.FIELDS}
        print(f"字段缺失    : {blanks}（已填空字符串，未崩溃）")
        print("-" * 64)
        print("前 3 条数据：")
        for i, row in checked.head(3).iterrows():
            print(f"  [{i + 1}] {row['文章标题']}")
            print(f"       {row['发布时间']} | {row['作者'] or '（缺失）'}")
            print(f"       {row['链接']}")
        for err in self.errors:
            print(f"  ! {err}")
        print("-" * 64)
        print(f"成功抓取条数：{len(checked)}")
        print("=" * 64)
        return len(checked)


def main() -> int:
    parser = argparse.ArgumentParser(description="实验五：NewsCrawler 静态新闻列表页爬虫")
    parser.add_argument("--url", default="", help="公开新闻/榜单列表页 URL，留空则用离线样本页")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="CSV 输出路径")
    parser.add_argument("--base-url", default=None, help="相对链接补全用的基准 URL")
    parser.add_argument("--delay", type=float, default=2.0, help="请求间隔秒数，最低 2 秒")
    parser.add_argument("--retries", type=int, default=3, help="超时重试次数")
    parser.add_argument("--timeout", type=int, default=10, help="单次请求超时秒数")
    args = parser.parse_args()

    crawler = NewsCrawler(
        url=args.url,
        output=args.output,
        base_url=args.base_url,
        delay=args.delay,
        retries=args.retries,
        timeout=args.timeout,
    )
    try:
        count = crawler.run()
        return 0 if count > 0 else 1
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"[运行中止] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
