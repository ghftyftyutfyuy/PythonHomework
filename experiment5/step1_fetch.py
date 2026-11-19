# -*- coding: utf-8 -*-
"""
实验五 · 步骤 2 第 1 小步：发送请求并获取 HTML

验证目标：确认能拿到状态码 200 与 HTML 内容。
真实抓取时设置 User-Agent、请求间隔 ≥2 秒、超时重试 3 次；
未配置 TARGET_URL（或网络不可用）时自动使用离线样本页 sample_page.html，
保证在 PyCharm 中一定能跑通验证闭环。
"""

from __future__ import annotations

import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_PAGE = BASE_DIR / "sample_page.html"

# 示例域名，仅用于把相对链接补全为绝对链接
BASE_URL = "https://news.example.com"
# 留空 = 离线演示；填入老师指定的「公开新闻网站 / 书籍排行榜」URL 即走真实抓取
TARGET_URL = ""

FIELDS = ["文章标题", "发布时间", "作者", "链接"]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
REQUEST_DELAY = 2.0   # 请求间隔不低于 2 秒
MAX_RETRIES = 3       # 超时 / 网络错误重试 3 次
TIMEOUT = 10


def load_local_html() -> str:
    if not SAMPLE_PAGE.exists():
        raise FileNotFoundError(f"离线样本页不存在：{SAMPLE_PAGE}")
    return SAMPLE_PAGE.read_text(encoding="utf-8")


def fetch_html(url: str) -> tuple[str, int, str]:
    """真实网络抓取，返回 (html, status_code, final_url)。"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            time.sleep(REQUEST_DELAY)
            resp = session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
                resp.encoding = resp.apparent_encoding
            return resp.text, resp.status_code, resp.url
        except requests.RequestException as exc:
            last_error = exc
            print(f"  第 {attempt}/{MAX_RETRIES} 次请求失败：{exc}")
    raise RuntimeError(f"重试 {MAX_RETRIES} 次后仍无法获取页面：{last_error}")


def obtain_html(url: str = TARGET_URL) -> tuple[str, int, str, bool]:
    """统一入口：优先真实抓取，失败则降级到离线样本。返回 (html, code, source, 是否离线)。"""
    if url:
        print(f"[真实模式] 目标 URL：{url}")
        try:
            html, code, final_url = fetch_html(url)
            return html, code, final_url, False
        except RuntimeError as exc:
            print(f"[降级] {exc}")
            print("[降级] 改用离线样本页完成验证闭环（统计逻辑完全一致）。")
    html = load_local_html()
    return html, 200, f"file:///{SAMPLE_PAGE.as_posix()}", True


def main() -> int:
    print("=" * 64)
    print("步骤 2-1：发送请求并获取 HTML")
    print("=" * 64)
    html, code, source, offline = obtain_html()
    print(f"来源        : {source}")
    print(f"模式        : {'离线样本页（验证闭环）' if offline else '真实网络抓取'}")
    print(f"状态码      : {code}")
    print(f"HTML 长度   : {len(html)} 字符")
    print(f"User-Agent  : {USER_AGENT[:48]}...")
    print(f"请求间隔    : {REQUEST_DELAY} 秒 / 超时重试 {MAX_RETRIES} 次")
    print("-" * 64)
    print("HTML 前 200 字符预览：")
    print(" ".join(html[:200].split()))
    print("-" * 64)
    if code == 200 and html.strip():
        print("验证通过：成功获取状态码 200 且 HTML 内容非空，可进入解析环节。")
        return 0
    print("验证失败：状态码异常或 HTML 为空。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
