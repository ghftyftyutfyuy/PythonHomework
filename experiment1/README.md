# 实验1：Python Vibe Coding 实操

本文件夹对应实验1指导书《Python Vibe Coding 实操》，包含两道考题：

| 考题 | 目录 | 内容 |
| --- | --- | --- |
| 考题一（必做，40 分） | [`excel/`](./excel/) | Excel 报表生成脚本：读取 `sales_raw.xlsx`，清洗脏数据，按销售员 / 地区汇总销售额，输出含「明细清洗后、按销售员、按地区、总览」四个工作表的 `report.xlsx` |
| 考题二 | [`fastapi/`](./fastapi/) | FastAPI 记账接口：`POST /records`、`GET /records`、`GET /summary`，含非法参数校验与 pytest 测试用例 |

## 目录结构

```text
experiment1/
├── excel/                  # 考题一：Excel 报表生成脚本
│   ├── README.md
│   ├── src/                # 源代码（create_sample.py / generate_report.py）
│   ├── data/               # 原始数据 sales_raw.xlsx
│   ├── output/             # 生成的报表 report.xlsx
│   └── docs/               # 运行截图、AI 对话记录
└── fastapi/                # 考题二：FastAPI 记账接口
    ├── README.md
    ├── main.py             # 接口主程序
    ├── test_main.py        # pytest 测试用例
    ├── requirements.txt    # 依赖清单
    └── docs/               # 运行截图、AI 对话记录
```

## 运行方式

各考题的具体运行命令、接口说明与验收标准见对应子目录的 `README.md`。

## 交付物对照（指导书第一节）

1. 需求澄清清单 —— 见各子目录 `README.md` 中的需求与验收标准；
2. 可运行的源代码工程 —— `excel/src/`、`fastapi/main.py`，均含 README；
3. 测试用例与运行结果 —— `fastapi/test_main.py`、`docs/` 下的截图；
4. AI 协作过程记录 —— `excel/docs/` 下的 ai-chat 与截图、`fastapi/docs/ai-chat/` 下的对话截图；
5. 文字复盘 —— 见各子目录 `README.md` 的说明部分。
