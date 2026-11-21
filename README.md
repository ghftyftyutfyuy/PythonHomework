# PythonHomework

2026 秋季学期《Python 语言程序设计》课程作业与实验汇总仓库。

- 仓库地址：https://github.com/ghftyftyutfyuy/PythonHomework
- 默认分支：`main`
- 组织方式：5 个课程实验统一按 `experimentN/` 命名；平时作业保留原有文件夹名
- 五个实验均附 Word 实验报告，并各有一份可在 GitHub 上直接阅读的 Markdown 版实验报告

## 实验总览

| 目录 | 实验名称 | 报告日期 | 主要技术 | 做了什么 |
| --- | --- | --- | --- | --- |
| [experiment1/](experiment1/) | 实验1 Python Vibe Coding 实操 | 2026-09-30 | pandas、openpyxl、FastAPI、pytest | 清洗销售 Excel 生成汇总报表；实现记账接口并写测试 |
| [experiment2/](experiment2/) | 实验2 城市交通数据看板的设计与实现 | 2026-10-09 | Streamlit、Plotly、pandas、numpy | 交互式网页看板：亮暗主题、日期/区域筛选、图表与拥堵预警 |
| [experiment3/](experiment3/) | 实验3 Python 列表、元组、集合 | 2026-10-21 | 纯标准库 | 切片删除、可哈希性、集合运算、保序去重、选课统计 |
| [experiment4/](experiment4/) | 实验4 本地文档智能审查与摘要 Agent | 2026-10-27 | jieba、wordcloud、matplotlib、watchdog | 批量读文档、中文分词、Top50 词云与关键词报告 |
| [experiment5/](experiment5/) | 实验5 Vibe Coding 爬虫开发实验 | 2026-11-18 | requests、BeautifulSoup、pandas | 四步迭代爬虫，重构为 `NewsCrawler` 类，输出 CSV |

## 平时作业

| 目录 | 内容 | 主要技术 |
| --- | --- | --- |
| [Monte_Carlo_Methon/](Monte_Carlo_Methon/) | 蒙特卡罗方法绘制圆形、心形、五角星、谢尔宾斯基三角形，并估算圆周率 | numpy、matplotlib |
| [draw_tian_grid/](draw_tian_grid/) | 用字符循环打印 n×n 田字格 | 纯标准库 |
| [koch_curve/](koch_curve/) | 递归绘制科赫雪花 | turtle |
| [word_freq/](word_freq/) | 「十五五」报告中文分词热词统计 Top30 与词云 | jieba、wordcloud、matplotlib |
| [if __name__ == '__main__'/](if%20__name__%20%3D%3D%20%27__main__%27/) | 博客文章：解释 `if __name__ == '__main__':` 的作用 | Markdown |

## 仓库结构

```text
PythonHomework/
├── README.md                      # 本文件：仓库首页与顶层导航
├── INDEX.md                       # 完整目录索引（逐个文件说明用途）
├── .gitignore
├── experiment1/                   # 实验1：Excel 报表 + 记账接口
│   ├── excel/                     #   考题一：销售数据清洗与报表
│   ├── fastapi/                   #   考题二：记账接口与 pytest
│   ├── README.md
│   └── 实验报告.docx
├── experiment2/                   # 实验2：城市交通数据看板（Streamlit，含 README.md 报告）
├── experiment3/                   # 实验3：列表、元组、集合（5 个任务源码）
├── experiment4/                   # 实验4：本地文档审查 Agent（词云）
│   ├── docs/  advanced/  output/
│   └── main.py ...
├── experiment5/                   # 实验5：Vibe Coding 爬虫
├── Monte_Carlo_Methon/            # 平时作业：蒙特卡罗绘图
├── draw_tian_grid/                # 平时作业：字符田字格
├── koch_curve/                    # 平时作业：科赫雪花
├── word_freq/                     # 平时作业：热词统计与词云
└── if __name__ == '__main__'/     # 平时作业：博客文章
```

## 环境准备

统一使用 Python 3.11：

```text
C:\Users\33787\AppData\Local\Programs\Python\Python311\python.exe
```

各实验自带依赖清单，在仓库根目录执行：

```bash
python -m pip install -r experiment1/fastapi/requirements.txt
python -m pip install -r experiment4/requirements.txt
python -m pip install -r experiment5/requirements.txt
```

全部涉及：numpy、pandas、matplotlib、openpyxl、jieba、wordcloud、pillow、requests、beautifulsoup4、watchdog、python-docx、pypdf、FastAPI、pytest、Streamlit、Plotly，以及标准库 turtle、csv、collections、argparse、pathlib。

## 如何运行

先进入对应目录再执行（多数脚本用 `Path(__file__).parent` 定位资源，从任意位置运行也可以）：

| 目标 | 命令 | 结果 |
| --- | --- | --- |
| 实验1 生成 Excel 报表 | `cd experiment1/excel && python src/generate_report.py` | `output/report.xlsx`，运行窗口同时打印汇总 |
| 实验1 启动记账接口 | `cd experiment1/fastapi && uvicorn main:app --reload` | 本地 HTTP 接口；`pytest test_main.py` 跑测试 |
| 实验2 启动看板 | `cd experiment2 && streamlit run app.py` | 浏览器打开交互式看板 |
| 实验3 五个任务 | `cd experiment3 && python task1_slice_delete.py` 等 5 个文件 | 运行窗口直接输出预判、实测与分析 |
| 实验4 文档审查 | `cd experiment4 && python main.py --no-show` | `output/` 下词云 PNG、关键词报告 TXT/CSV |
| 实验5 四步爬虫 | `cd experiment5 && python step1_fetch.py` → `step2_parse.py` → `step3_save.py` → `news_crawler.py` | `result.csv`，四步输出可直接对照 |
| 平时作业 | 进入对应目录，直接运行 `.py` 文件 | 田字格/热词在控制台，雪花与蒙特卡罗在图形窗口 |

## 目录约定

每个 `experimentN/` 尽量统一包含：

- `README.md`：Markdown 版实验报告，GitHub 上直接可读
- `实验报告.docx`：按课程《实验报告空白模板》填写的 Word 报告
- `prompts.md`：Vibe Coding 过程记录（实验4、5）
- `requirements.txt`：依赖清单（实验4、5 及 `experiment1/fastapi/`）
- `运行结果.txt`：脚本实跑输出留档
- `output/`：生成的图、CSV、报告等产物
- 运行截图：与各实验放在一起，作为结果证据

## 说明

- 根目录的 `report.xlsx`、`sales_raw.xlsx` 是实验一早期遗留文件，已在 `.gitignore` 中忽略；正式版本见 `experiment1/excel/`。
- `.idea/`、`.venv/`、`__pycache__/`、`*.pyc` 以及 `~$*` Office 临时锁文件均不纳入版本管理。
- 实验五默认使用内置 `sample_page.html` 完成离线验证闭环，未对公开站点发起真实抓取；切换真实站点的命令见 `experiment5/README.md`。
- 五份实验报告日期依次为 2026-09-30、10-09、10-21、10-27、11-18。

## 完整索引

逐个文件的用途与位置见 [INDEX.md](INDEX.md)。
