# 实验五：Vibe Coding 爬虫开发实验

> 对应实验指导书《爬虫开发实验指导书》（DOCX）。
> 命名延续本仓库规则：`experiment1` / `experiment2` / `experiment3` / `experiment4` / **`experiment5`**。
> 本 README 兼作实验报告，在 GitHub 上可直接阅读。

## 一、实验目的

1. 掌握 Vibe Coding 核心工作流（意图定义、任务拆解、验证闭环），改变传统逐行编写代码的习惯。
2. 学会用结构化 Prompt 驱动 AI 生成基于 `requests` 与 `BeautifulSoup` 的 Python 爬虫代码。
3. 掌握对 AI 生成代码的审查、调试与重构能力，建立反爬合规意识。

## 二、实验环境

| 项目 | 版本 / 说明 |
| --- | --- |
| Python | 3.11（要求 3.9 及以上） |
| 核心依赖 | `requests`、`beautifulsoup4`、`pandas` |
| 安装 | `pip install requests beautifulsoup4 pandas` |
| AI 编程助手 | WorkBuddy（Vibe Coding 对话过程见 `prompts.md`） |
| IDE | PyCharm，四个脚本各自可直接右键运行，结果打印在运行窗口 |

完整依赖见 [`requirements.txt`](./requirements.txt)。

## 三、实验任务与场景

抓取公开新闻网站（或书籍排行榜）的**列表页**，提取「文章标题」「发布时间」「作者」「链接」，保存为结构化 CSV。

**Vibe Coding 核心约束（指导书第三节）**：

1. 禁止直接让 AI 一次性生成所有代码；
2. 必须采用「需求澄清 → 分步生成 → 运行验证 → 报错反馈」的迭代流程。

本实验把这一约束落到四个可独立运行的脚本上，每步都有明确验收输出，完整对话与报错记录见 [`prompts.md`](./prompts.md)。

> **关于目标页面的说明**：为保证在无外网 / 不稳定网络环境下也能完成「运行验证」闭环，
> 仓库内置了 [`sample_page.html`](./sample_page.html)（12 条模拟新闻，含 2 条故意缺字段的测试条目）作为默认数据源。
> **真实网络抓取代码已完整实现**：把 `--url` 指向老师指定的公开站点即可切换，
> 代码会自动设置 User-Agent、间隔 ≥2 秒、超时重试 3 次；若请求失败会明确打印并降级回样本页，
> 同时在运行输出中标注「离线样本页（验证闭环）」而非冒充真实抓取。
> 切换真实站点时，需按目标页面的实际 HTML 结构调整 `NewsCrawler.LIST_SELECTOR` 及字段选择器。

## 四、实验步骤与交付物对照

| 指导书步骤 | 交付物 | 验收点 |
| --- | --- | --- |
| 步骤 1 需求澄清与结构化 Prompt | [`prompts.md`](./prompts.md) 第一节 | 角色 + 目标 + 约束 + 验收标准齐备 |
| 步骤 2-1 获取 HTML | [`step1_fetch.py`](./step1_fetch.py) | 状态码 200、HTML 非空 |
| 步骤 2-2 解析字段 | [`step2_parse.py`](./step2_parse.py) | 打印前 3 条、字段缺失填 `""` |
| 步骤 3 持久化与异常处理 | [`step3_save.py`](./step3_save.py)、[`result.csv`](./result.csv) | UTF-8、列名正确、数据对齐、打印条数 |
| 步骤 4 审查与工程化重构 | [`news_crawler.py`](./news_crawler.py) | 重构前后输出一致、`NewsCrawler` 类结构 |
| 步骤 5 进阶挑战 | [`dynamic_rendering.md`](./dynamic_rendering.md) | 动态渲染两种方案 + 复杂度/效率对比 |

## 五、目录结构

```text
experiment5/
├── README.md                  # 本实验报告 / 说明
├── prompts.md                 # 四轮结构化 Prompt、报错反馈、代码审查结论
├── requirements.txt
├── sample_page.html           # 离线演示用新闻列表页（12 条，含 2 条缺字段）
├── step1_fetch.py             # 步骤 2-1：获取 HTML
├── step2_parse.py             # 步骤 2-2：BeautifulSoup 解析四字段
├── step3_save.py              # 步骤 3：pandas 写 CSV + 验收
├── news_crawler.py            # 步骤 4：重构后的 NewsCrawler 类（最终版）
├── dynamic_rendering.md       # 进阶挑战：Vue/React 动态渲染爬取方案对比
├── result.csv                 # 运行产物：12 行 × 4 列
└── 运行结果.txt               # 四个脚本完整运行输出留档
```

## 六、运行方式（PyCharm 直接可跑）

```bash
cd E:\PythonHomework\experiment5

python step1_fetch.py        # 步骤 2-1：状态码 200 / HTML 长度
python step2_parse.py        # 步骤 2-2：打印前 3 条
python step3_save.py         # 步骤 3：生成 result.csv 并验收
python news_crawler.py       # 步骤 4：重构版，一键跑完整流程
```

切换到真实公开站点：

```bash
python news_crawler.py --url "https://<公开新闻站点>/list.html"
python news_crawler.py --url "https://<站点>/list.html" --output ./result_real.csv --delay 2 --retries 3
```

> 抓取前请先查阅目标站点 `robots.txt`；只抓公开列表页，控制频率，
> 不绕过登录、验证码、签名鉴权，不用于商业转售或高频压测。

## 七、运行结果（本地实跑，Python 3.11）

```text
步骤 2-1：状态码 200，HTML 长度 3204 字符，验证通过
步骤 2-2：解析到 12 条
  [1] 人工智能赋能教育数字化转型迈入新阶段 | 2026-11-19 | 李文博
  [2] 新质生产力成为产业升级主攻方向       | 2026-11-19 | 周敏
  [3] 数字中国建设提速 公共数据授权运营试点扩围 | 2026-11-18 | 陈思远
  字段缺失统计：{'文章标题': 0, '发布时间': 1, '作者': 1, '链接': 0}
步骤 3 ：编码检查 UTF-8 通过 | 列名 ['文章标题','发布时间','作者','链接']
         | 12 行 × 4 列，无列错位 | 成功抓取条数：12
步骤 4 ：NewsCrawler 重构版输出与重构前完全一致 | 成功抓取条数：12
```

四个脚本全部 `exit 0`，完整输出见 [`运行结果.txt`](./运行结果.txt)。
两条故意缺字段的样本数据被填满 `""` 而不是崩溃，验证了步骤 3 的异常处理要求。

## 八、重构前后对比（步骤 4 验证结论）

| 维度 | 重构前（三个过程式脚本） | 重构后（`NewsCrawler`） |
| --- | --- | --- |
| 配置管理 | 常量散落在模块顶层 | 收为实例属性，CLI 可参数化 |
| 职责划分 | 靠 `import` 串联，难单独测试 | `fetch / parse / to_frame / save / verify / run` 单一职责 |
| 扩展目标站点 | 需改多个文件 | 只改类属性 `LIST_SELECTOR` 或重写两个方法 |
| 异常可见性 | 打印后即丢失 | `self.errors` 汇总、结束时集中输出 |
| 功能等价 | 12 条 / UTF-8 / 四列 | **完全一致** |

审查中发现的瓶颈与隐患（会话未复用、间隔可被传 0、选择器硬编码、空值被读成 NaN 等）及修复方式，见 [`prompts.md`](./prompts.md) 第三、四节。

## 九、进阶挑战

[`dynamic_rendering.md`](./dynamic_rendering.md) 回答了「Vue / React 动态渲染页面如何爬取」：

- **方案 A**：用 Network 面板找到 XHR/Fetch 的 JSON 接口，直接请求并做字段映射（代码约 20 行，几十毫秒级，**推荐优先**）；
- **方案 B**：用 Playwright / Selenium 启动真实浏览器，等列表渲染后取 DOM（代码复杂、单页数秒级、内存数百 MB，作为兜底）；
- 文内给出两种方案的示例代码、七维度对比表，并说明本实验的类结构如何做到「只换 `fetch()` 与 `parse()` 即可切换方案」。

## 十、反爬合规与实验小结

**合规落实**：User-Agent 伪装（`_build_session`）、请求间隔强制 ≥2 秒（`max(delay, 2.0)`）、超时 10 秒重试 3 次、只抓公开列表页、字段缺失容错不反复重试打爆站点；README 与 `prompts.md` 均明确要求先读 `robots.txt`、不绕过鉴权。

**三点体会**：

1. **Vibe Coding 的关键不是「让 AI 写」，而是「拆到能验证为止」**。每轮只加一个能力、先跑再迭代，报错时把完整 Traceback 反馈回去，定位成本远低于一次性生成几百行再调试。
2. **验收标准要写进 Prompt**。本实验把「UTF-8 / 四列名 / 数据对齐 / 打印条数」写进初始约束，AI 生成的代码才会自带检查逻辑，而不是只顾把数据写出去。
3. **重构的价值在隔离变化**。面向过程版本能跑，但换成动态渲染站点就要动三个文件；`NewsCrawler` 把变化收敛到 `fetch()` 与 `parse()`，其余验收流程原样复用——这正是「可维护」与「能跑」的区别。
