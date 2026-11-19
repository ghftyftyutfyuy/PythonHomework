# 实验五 · Vibe Coding 结构化 Prompt 与迭代记录

> 对应指导书「步骤 1 需求澄清与结构化 Prompt」「步骤 2 分步生成与最小化验证」
> 「步骤 4 代码审查与工程化重构」。本文件是实验过程记录，不作为程序运行依赖。

## 一、初始结构化 Prompt（角色 + 目标 + 约束 + 验收标准）

```text
你是 Python 后端工程师。我需要编写一个静态网页爬虫。

目标：抓取【目标网站 URL】的列表页，提取「文章标题」「发布时间」「作者」「链接」，
     并保存为结构化的 CSV 文件。

约束：
1. 使用 requests 和 BeautifulSoup，不使用 Scrapy 框架；
2. 必须设置 User-Agent 伪装；
3. 请求间隔不低于 2 秒；
4. 遇到网络超时 / 5xx 需重试 3 次，每次超时 10 秒；
5. 解析时字段缺失填空字符串，单条解析异常只跳过该条，不许整段崩溃；
6. 相对链接要用 urljoin 补全为绝对链接；
7. 只抓公开列表页，遵守 robots.txt，不绕过登录、验证码与反爬机制。

验收：输出 result.csv 文件，编码为 UTF-8、列名严格为
     「文章标题,发布时间,作者,链接」、数据无列错位，
     并在终端打印成功抓取条数。
```

> 说明：指导书明确要求「禁止直接让 AI 一次性生成所有代码」，因此下面按四轮分步推进，
> 每轮都必须先运行验证，再把完整 Traceback / 实际输出反馈给 AI 才进入下一轮。

## 二、分步生成与验证记录

| 轮次 | 对 AI 的指令 | 生成内容 | 运行验证 | 反馈/修复 |
| --- | --- | --- | --- | --- |
| 1（步骤 2-1） | 「先**只**写发送请求并获取 HTML 的代码，不要写解析」 | `requests.get` 打印状态码与 HTML 前 200 字符 | 状态码 200、HTML 长度 3204 字符 | 首版没设 User-Agent 被站点拒绝风险高 → 要求补 UA、Accept-Language、`time.sleep(2)` 间隔、3 次重试、`resp.raise_for_status()` |
| 2（步骤 2-2） | 「在上一版基础上，只加解析 HTML 提取四个字段，打印前 3 条」 | `soup.select("li.news-item")` + `time` / `.author` | 解析到 12 条，前 3 条打印正确 | 发现 2 条样本缺作者/时间导致 `AttributeError` → 要求全部 `get_text` 前判空、缺失填 `""`；相对链接用 `urljoin` 补全 |
| 3（步骤 3） | 「把解析结果写入 CSV，并补充异常处理与验收检查」 | `pandas.DataFrame.to_csv` | UTF-8 解码通过、列名正确、12 行 × 4 列 | `pd.read_csv` 默认把空串读成 NaN → 验证时改用 `keep_default_na=False`；补「编码 / 列名 / 数据对齐」三项检查 |
| 4（步骤 4） | 见第三节「代码审查 Prompt」 | `NewsCrawler` 类 | 重构后仍输出 12 条、CSV 验收全通过 | 对比前后输出一致，确认核心逻辑未被破坏 |

## 三、代码审查与重构 Prompt（步骤 4）

```text
请审查下面这段由前面四轮生成并已跑通的爬虫代码，指出潜在的性能瓶颈或安全隐患，
并将其重构为面向对象的类结构（如 NewsCrawler 类），保持功能不变：

审查要点：
- 请求策略：会话是否复用、间隔与重试是否可配置、是否会无限等待；
- 解析健壮性：选择器写死在流程里是否难维护、字段缺失是否可能污染整表；
- 可维护性：过程式脚本无法单独测试某一环节、配置散落在各处；
- 安全与合规：是否可能被误用为高频抓取、是否遗漏 robots.txt 约束。

重构要求：
1. 类名 NewsCrawler，把字段定义、选择器、UA、间隔、重试次数收为类属性；
2. 拆出 fetch / parse / to_frame / save / verify / run 单一职责方法；
3. 保持 CLI 可用，参数化 --url / --output / --delay / --retries；
4. 输出与验收标准必须与重构前完全一致。
```

**AI 审查指出的问题（摘要）**

1. 每次请求都新建连接 → 改为 `requests.Session()` 复用会话；
2. `delay` 可被调用方传入 0 → 构造时用 `max(delay, 2.0)` 强制 ≥2 秒；
3. 选择器硬编码在多处 → 收为 `LIST_SELECTOR` / `ALT_SELECTORS` 类属性；
4. 过程式脚本三个文件互相 `import`，任一环节改动会牵动全局 → 改为类方法隔离变化；
5. 异常处理散落 → 统一收集到 `self.errors`，运行结束集中打印；
6. 缺合规提示 → 在类文档字符串与 README 明确 `robots.txt`、频率、不绕过鉴权。

**重构前后对比**

| 维度 | 重构前（step1~3 过程式） | 重构后（`NewsCrawler`） |
| --- | --- | --- |
| 配置管理 | 常量散落在 `step1_fetch.py` 模块顶层 | 收为实例属性，CLI 可参数化 |
| 职责划分 | 获取/解析/存储分在三个文件，靠 import 串联 | 六个单一职责方法，可单独调用与单测 |
| 扩展目标站点 | 需改动多个文件 | 只改 `LIST_SELECTOR` 或重写 `fetch()` / `parse()` |
| 异常可见性 | 打印后就丢失 | `self.errors` 汇总，验收时集中输出 |
| 功能等价性 | 12 条、UTF-8、四列、无列错位 | **完全一致**（见 `运行结果.txt` 两组输出） |

## 四、报错反馈闭环留痕

| 现象 | 完整信息（反馈给 AI 的内容） | 修复 |
| --- | --- | --- |
| `AttributeError: 'NoneType' object has no attribute 'get_text'` | 样本中 2 条新闻故意缺少 `.author` / `time` 节点 | 所有节点先判空再取值，字段缺失填 `""` |
| CSV 中时间列被读成 `NaN` | `pd.read_csv` 默认把空字符串当缺失值 | 验证阶段加 `keep_default_na=False` |
| 链接是 `/news/...` 相对路径 | 直接写入 CSV 无法直接打开 | `urljoin(base_url, href)` 补全为绝对链接 |
| 网页中文乱码 | `resp.encoding` 被识别成 `ISO-8859-1` | 用 `resp.apparent_encoding` 修正编码 |
| 无外网时 `requests` 抛 `ConnectionError` | 实验机网络不可达 | 增加「真实抓取失败自动降级到离线样本页」分支，保证验证闭环不中断；并在输出中明确标注运行模式 |

## 五、反爬合规清单（实验约束落实位置）

| 约束 | 实现位置 |
| --- | --- |
| User-Agent 伪装 | `step1_fetch.py` 的 `fetch_html()`、`news_crawler.py` 的 `_build_session()` |
| 请求间隔 ≥2 秒 | `REQUEST_DELAY = 2.0`；`NewsCrawler.__init__` 中 `max(delay, 2.0)` |
| 超时重试 3 次 | `MAX_RETRIES = 3`、`TIMEOUT = 10`，逐次打印失败原因 |
| 字段缺失容错 | `parse_news_list()` / `NewsCrawler.parse()` 判空 + 填空字符串 |
| 只抓公开数据 | README 第六节合规说明；不提供登录、验证码绕过逻辑 |
| 遵守 robots.txt | README 明确要求抓取前先查阅目标站点 `robots.txt` |
