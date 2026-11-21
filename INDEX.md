# 根目录索引 / Repository Index

本文件逐个列出仓库内容目录中的文件及用途。仓库介绍、环境准备与运行方式见 [README.md](README.md)。

整理时间：2026-11-21。截图类文件按目录汇总，不逐张列出文件名。

## 一、顶层条目总览

| 条目 | 类别 | 内容摘要 | 主要交付物 |
| --- | --- | --- | --- |
| [experiment1/](experiment1/) | 实验1 | Excel 报表 + 记账接口 | `实验报告.docx`、`README.md`、两个子工程 |
| [experiment2/](experiment2/) | 实验2 | 城市交通数据看板 | `app.py`、`实验报告.docx`、6 张截图 |
| [experiment3/](experiment3/) | 实验3 | 列表、元组、集合 | 5 个 `task*.py`、`思考题.md`、`README.md` |
| [experiment4/](experiment4/) | 实验4 | 本地文档审查与摘要 Agent | `main.py`、词云 PNG、`README.md` |
| [experiment5/](experiment5/) | 实验5 | Vibe Coding 爬虫 | 四步脚本、`NewsCrawler` 类、`result.csv` |
| [Monte_Carlo_Methon/](Monte_Carlo_Methon/) | 平时作业 | 蒙特卡罗绘图与 π 估算 | `Monte.py`、1 张截图 |
| [draw_tian_grid/](draw_tian_grid/) | 平时作业 | 字符田字格 | `draw_tian_grid.py`、1 张截图 |
| [koch_curve/](koch_curve/) | 平时作业 | 递归科赫雪花 | `koch.py`、5 张截图 |
| [word_freq/](word_freq/) | 平时作业 | 热词统计与词云 | 2 个 `.py`、`report.txt`、`hot_words.csv`、`wordcloud.png` |
| [if __name__ == '__main__'/](if%20__name__%20%3D%3D%20%27__main__%27/) | 平时作业 | 博客文章 | `if_name_main.md` |
| `README.md` | 根目录文件 | 仓库首页与顶层导航 | 本仓库入口 |
| `INDEX.md` | 根目录文件 | 完整文件索引 | 本文件 |
| `.gitignore` | 根目录文件 | 版本管理忽略规则 | — |

## 二、实验目录

### experiment1/ — 实验1 Python Vibe Coding 实操（2026-09-30）

| 路径 | 用途 |
| --- | --- |
| `README.md` | 实验一索引，说明 `excel/` 与 `fastapi/` 两个考题 |
| `实验报告.docx` | 按课程模板填写的 Word 实验报告 |
| `excel/README.md` | 考题一说明：销售数据清洗与报表生成 |
| `excel/src/create_sample.py` | 生成原始销售数据 `sales_raw.xlsx` |
| `excel/src/generate_report.py` | 清洗并按人员、地区汇总，输出 `report.xlsx` |
| `excel/data/sales_raw.xlsx` | 原始脏数据 |
| `excel/output/report.xlsx` | 生成的汇总报表 |
| `excel/docs/ai-chat` | 过程记录占位文件 |
| `excel/docs/屏幕截图 *.png`（4 张） | 运行与结果截图 |
| `fastapi/README.md` | 考题二说明：接口设计与测试 |
| `fastapi/main.py` | FastAPI 记账接口（增删改查 + 收支统计） |
| `fastapi/test_main.py` | pytest 单元测试 |
| `fastapi/requirements.txt` | 依赖清单 |
| `fastapi/docs/ai-chat/`（5 张） | Vibe Coding 对话过程截图 |

### experiment2/ — 实验2 城市交通数据看板的设计与实现（2026-10-09）

| 路径 | 用途 |
| --- | --- |
| `app.py` | Streamlit 看板主程序：亮暗主题、日期/区域筛选、图表、拥堵预警 |
| `generate_data.py` | 生成 7 天模拟交通数据 |
| `city_traffic.csv` | 模拟数据 |
| `实验报告.docx` | 按课程模板填写的 Word 实验报告 |
| `屏幕截图 *.png`（6 张） | 看板运行截图 |

注：本目录没有 `README.md`，实验说明见 `实验报告.docx` 与 `app.py` 注释。

### experiment3/ — 实验3 Python 列表、元组、集合（2026-10-21）

| 路径 | 用途 |
| --- | --- |
| `README.md` | Markdown 版实验报告，含预判与结果对比分析 |
| `task1_slice_delete.py` | 任务1：切片删除探究、循环删除 bug 与安全方案 |
| `task2_hashable.py` | 任务2：可哈希性逐条辨析与 `frozenset` |
| `task3_set_ops.py` | 任务3：集合五种运算与集合推导式 |
| `task4_dedup.py` | 任务4：三种保序去重方案对比 |
| `task5_course.py` | 任务5：综合选课统计与嵌套列表去重 |
| `思考题.md` | 5 道必答思考题的完整解答 |
| `运行结果.txt` | 五个任务实跑输出留档 |
| `实验报告.docx` | 按课程模板填写的 Word 实验报告 |

### experiment4/ — 实验4 本地文档智能审查与摘要 Agent（2026-10-27）

| 路径 | 用途 |
| --- | --- |
| `README.md` | Markdown 版实验报告 |
| `main.py` | 主程序 `DocumentAnalyzer`：批量读取 → 分词 → Top50 词云 → 关键词报告 |
| `stopwords.txt` | 中文停用词表 |
| `user_dict.txt` | jieba 自定义词典（十五五、新质生产力等专有词） |
| `docs/人工智能与教育.txt` | 自写中文语料 1 |
| `docs/新质生产力与产业发展.md` | 自写中文语料 2 |
| `docs/数字中国建设.txt` | 自写中文语料 3 |
| `advanced/monte_carlo_simulation.py` | 进阶：蒙特卡洛模拟审查 |
| `advanced/llm_review_agent.py` | 进阶：大模型审查 Prompt 组装（未配密钥，安全降级） |
| `advanced/watch_docs.py` | 进阶：watchdog 目录自动监控 |
| `output/document_wordcloud.png` | Top50 高频词词云图 |
| `output/keywords_report.txt` | 各文档关键词汇总（文本版） |
| `output/keywords_report.csv` | 各文档关键词汇总（表格版） |
| `output/cleaned_corpus.txt` | 清洗后的语料 |
| `output/review_prompt.txt` | 进阶脚本生成的审查 Prompt |
| `output/monte_carlo_context.txt` | 进阶脚本生成的模拟上下文 |
| `prompts.md` | 需求边界定义与结构化 Prompt 记录 |
| `requirements.txt` | 依赖清单 |
| `运行结果.txt` | 实跑输出留档 |
| `实验报告.docx` | 按课程模板填写的 Word 实验报告 |

### experiment5/ — 实验5 Vibe Coding 爬虫开发实验（2026-11-18）

| 路径 | 用途 |
| --- | --- |
| `README.md` | Markdown 版实验报告 |
| `sample_page.html` | 内置离线样本页，用于验证闭环 |
| `step1_fetch.py` | 第 1 步：请求网页并检查状态码 |
| `step2_parse.py` | 第 2 步：解析标题、时间、作者、链接四字段 |
| `step3_save.py` | 第 3 步：用 pandas 存为 UTF-8 CSV |
| `news_crawler.py` | 第 4 步：重构为 `NewsCrawler` 类，支持 `--url` 切真实站点 |
| `result.csv` | 输出：文章标题 / 发布时间 / 作者 / 链接，12 行 |
| `dynamic_rendering.md` | 进阶题：Vue/React 动态渲染两方案对比与七维度表 |
| `prompts.md` | 四步迭代（需求澄清 → 分步生成 → 验证 → 报错反馈）过程记录 |
| `requirements.txt` | 依赖清单 |
| `运行结果.txt` | 实跑输出留档 |
| `实验报告.docx` | 按课程模板填写的 Word 实验报告 |

## 三、平时作业目录

### Monte_Carlo_Methon/ — 蒙特卡罗方法绘图

| 路径 | 用途 |
| --- | --- |
| `Monte.py` | 拒绝采样绘圆形、心形、五角星，混沌游戏绘谢尔宾斯基三角，并估算 π |
| `屏幕截图 *.png`（1 张） | 运行结果截图 |

### draw_tian_grid/ — 字符田字格

| 路径 | 用途 |
| --- | --- |
| `draw_tian_grid.py` | 输入宽度 n，用加号、短横与竖线循环打印 n×n 田字格 |
| `屏幕截图 *.png`（1 张） | 运行结果截图 |

### koch_curve/ — 科赫雪花

| 路径 | 用途 |
| --- | --- |
| `koch.py` | turtle 递归绘制科赫曲线，三条拼成雪花，阶数 0~4 |
| `屏幕截图 *.png`（5 张） | 不同阶数的绘制结果 |

### word_freq/ — 热词统计与词云

| 路径 | 用途 |
| --- | --- |
| `report.txt` | 「十五五」发展规划报告正文（纯文本 UTF-8） |
| `word_freq.py` | jieba 分词 + 停用词过滤，输出 Top30 热词 |
| `make_wordcloud.py` | 在统计基础上生成词云图 |
| `hot_words.csv` | 热词排名表 |
| `wordcloud.png` | 词云图 |
| `屏幕截图 *.png`（3 张） | 运行结果截图 |

### if __name__ == '__main__'/ — 博客文章

| 路径 | 用途 |
| --- | --- |
| `if_name_main.md` | 解释 `if __name__ == '__main__':` 的含义、直接运行与 import 的区别、为何要用、常见误区 |

## 四、根目录文件

| 路径 | 用途 |
| --- | --- |
| `README.md` | 仓库首页：实验总览、仓库结构、环境准备、运行方式、目录约定 |
| `INDEX.md` | 本文件：完整文件级索引 |
| `.gitignore` | 忽略 Office 临时锁文件、PyCharm 配置、Python 缓存、虚拟环境与根目录旧 xlsx |
| `report.xlsx`、`sales_raw.xlsx` | 实验一早期遗留在根目录的旧文件，已被 `.gitignore` 忽略，不上传；正式版本在 `experiment1/excel/` |

## 五、不纳入版本管理的内容

`.idea/`、`.venv/`、`__pycache__/`、`*.pyc`、`*.pyo`、`*.pyd`、`.pytest_cache/`、`~$*.docx`、`~$*.xlsx`、`~$*.doc`，以及上表中的两个根目录 xlsx。

## 六、按用途速查

| 想找什么 | 去哪里 |
| --- | --- |
| 交作业用的实验报告 | 各 `experimentN/实验报告.docx`，或同目录 `README.md` |
| 把程序跑起来 | `README.md` 的「如何运行」一节 |
| 可视化成果（图 / 网页） | `experiment2/`（网页看板）、`experiment4/output/document_wordcloud.png`（词云） |
| 运行结果证据 | 各目录的 `屏幕截图 *.png`、`运行结果.txt`、`output/` |
| 可运行的源码 | 各 `experimentN/` 下的 `.py` 文件 |
| Vibe Coding 过程记录 | `experiment4/prompts.md`、`experiment5/prompts.md` |
| 思考题答案 | `experiment3/思考题.md` |
| 中文分词与词云入门 | `word_freq/`（单文件版）→ `experiment4/`（工程版） |
