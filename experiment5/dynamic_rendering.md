# 实验五 · 进阶挑战：动态渲染页面如何爬取

> 对应指导书「五、进阶挑战」：如果目标网站是动态渲染的（Vue / React），如何爬取？
> 重写爬虫并对比两种方案在**代码复杂度**和**运行效率**上的差异。

## 一、问题本质

`requests + BeautifulSoup` 只能拿到服务端返回的**原始 HTML**。Vue / React 应用的初始 HTML 往往只有一个空壳：

```html
<div id="app"></div>
<script src="/assets/index-a1b2c3.js"></script>
```

列表数据是在浏览器里执行 JS 后，通过 XHR / Fetch 请求接口拿到 JSON，再由前端渲染进 DOM。
所以 `soup.select("li.news-item")` 在动态页面上会返回空列表——**不是选择器写错，而是数据根本不在 HTML 里**。

## 二、两种方案

### 方案 A：直接请求数据接口（推荐优先）

用浏览器开发者工具 → Network → Fetch/XHR，找到返回列表 JSON 的接口，然后用 `requests` 直接请求它，
跳过渲染环节，把 JSON 映射成本实验的四个字段。

```python
import requests
import pandas as pd

API = "https://example.com/api/news/list"

def crawl_by_api(page: int = 1) -> list[dict]:
    resp = requests.get(
        API,
        params={"page": page, "size": 20},
        headers={
            "User-Agent": "Mozilla/5.0 ...",
            "Referer": "https://example.com/news",
        },
        timeout=10,
    )
    resp.raise_for_status()
    rows = resp.json()["data"]["list"]       # 按实际响应结构取值
    return [
        {
            "文章标题": row.get("title", ""),
            "发布时间": row.get("publishTime", ""),
            "作者": row.get("author", ""),
            "链接": row.get("url", ""),
        }
        for row in rows
    ]

records = crawl_by_api(1)
pd.DataFrame(records).to_csv("result.csv", index=False, encoding="utf-8")
print(f"成功抓取条数：{len(records)}")
```

**注意**：部分接口带签名（`sign` / `nonce` / 时间戳）或需要登录态 Cookie；这类接口若做了鉴权，
应遵守站点规则改用官方 API 或方案 B，**不要逆向绕过鉴权**。

### 方案 B：浏览器自动化（Selenium / Playwright）

让真实浏览器执行 JS，等列表渲染完成后再取 DOM 或拦截响应。

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0 ...")
    page.goto("https://example.com/news", wait_until="networkidle")
    page.wait_for_selector("li.news-item")        # 等关键元素出现

    items = page.locator("li.news-item")
    records = [
        {
            "文章标题": items.nth(i).locator("h2 a").inner_text(),
            "发布时间": items.nth(i).locator("time").get_attribute("datetime"),
            "作者": items.nth(i).locator(".author").inner_text(),
            "链接": items.nth(i).locator("h2 a").get_attribute("href"),
        }
        for i in range(items.count())
    ]
    browser.close()
```

Playwright 还可以直接监听响应，把「页面渲染」和「接口数据」两步合一：

```python
page.on("response", lambda r: capture(r) if "/api/news/list" in r.url else None)
```

## 三、方案对比

| 维度 | 方案 A：直连数据接口 | 方案 B：浏览器自动化 |
| --- | --- | --- |
| 代码复杂度 | **低**：一次 `requests` + JSON 字段映射，约 20 行 | **高**：需管理浏览器生命周期、等待策略、选择器、并发与资源释放 |
| 运行效率 | **高**：单页一次 HTTP 请求，几十毫秒级，内存占用极小 | **低**：需启动 Chromium、加载 JS/CSS/图片，单页数秒级，内存数百 MB |
| 稳定性 | 中：依赖接口结构，接口改版即失效（但改动点集中、易修） | 中高：贴近真实用户，对前端改版容忍度更好，但易受加载超时影响 |
| 反爬风险 | 较高：接口常有签名/频控，需严格遵守 `robots.txt` 与调用频率 | 较低：浏览器指纹接近真人，但仍应控制频率、不绕过验证码 |
| 依赖体积 | 仅 `requests` / `pandas` | 需额外安装 `playwright` 并下载浏览器内核（数百 MB） |
| 分页与翻页 | 直接改 `page` 参数，成本极低 | 需模拟点击或滚动，逻辑复杂 |
| 适用场景 | 有清晰 JSON 接口、批量抓取、对速度敏感 | 接口加密/签名复杂、需要登录态、需要交互（滚动、点击、展开） |

## 四、结论与选型建议

1. **先找接口，再考虑浏览器**。用 Network 面板花 5 分钟确认是否有公开 JSON 接口，能省下大量工程复杂度。
2. 本实验的 `NewsCrawler` 已经把职责拆成 `fetch / parse / to_frame / save / verify`，
   切换方案 A 时**只需替换 `fetch()` 与 `parse()` 两个方法**，其余流程与验收标准完全复用：
   - `fetch()` 改为请求 API 并把 `resp.json()` 传给解析层；
   - `parse()` 改为遍历 JSON 列表做字段映射。
   这正体现了「面向对象重构」的价值：**变化被隔离在局部**。
3. 方案 B 作为兜底：当接口存在签名/鉴权且无法合规获取时，用 Playwright 以真实用户视角抓取，
   并保留 `REQUEST_DELAY ≥ 2s`、重试、字段缺失填空等本实验已实现的约束。
4. 无论哪种方案，都要遵守合规底线：只抓公开数据、先读 `robots.txt`、设置合理 User-Agent 与请求间隔、
   不绕过登录与验证码、不用于商业转售或高频压测。
