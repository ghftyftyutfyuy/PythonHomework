# Python 作业仓库

## 作业列表
- [Lab1: Excel报表生成脚本](./lab1_excel/README.md)

## 说明
- 每个作业放在独立的 `labN_xxx` 目录下。
- 源代码在 `src/`，测试在 `tests/`，文档在 `docs/`。


(一) 考题一：Excel 报表生成脚本（必做，40 分）
背景：某团队每月有一份 sales_raw.xlsx，字段为 日期、销售员、产品、数量、单价、地区，存在空值、重复行与负数量等脏数据。
需求：编写 Python 脚本，读取原始表，完成清洗与统计，输出 report.xlsx。要求：
1. 数据清洗：删除关键字段缺失的行，剔除数量<=0 的异常行，按全字段去重；
2. 统计维度：按销售员汇总销售额（数量×单价），按地区汇总销售额，并给出月度总额；
3. 输出 report.xlsx：含"明细清洗后""按销售员""按地区""总览"四个工作表；
4. 约束：不得修改原始文件；对缺失字段、空文件、无有效数据等情况需给出明确报错或提示。
验收标准：给定样例数据能一键运行生成正确报表；统计数值与人工核对一致；异常输入不崩溃且有可读提示。


与ai聊天记录

image.png
17:27
思考过程
I see you've uploaded an image. What would you like me to do with it?

For example:

Recreate it as an editable design/page?
Use it as style reference for a new design?
Extract colors/typography/layout from it?
Simply describe what's in it?
学习Python语言过程中的一个作业，给出代码
17:31
已完成作业代码并验证通过。

核心脚本：generate_report.py

配套文件：

create_sample.py — 生成含脏数据的示例 sales_raw.xlsx
sales_raw.xlsx — 示例原始表
report.xlsx — 运行后生成的报表
实现要点：

读取 sales_raw.xlsx，校验必要字段（日期、销售员、产品、数量、单价、地区）。
数据清洗：删除关键字段缺失行、剔除数量 <=0 的行、按全字段去重。
统计销售额（数量 × 单价）：按销售员汇总、按地区汇总、按月度汇总。
输出 report.xlsx，包含四个工作表：明细清洗后、按销售员、按地区、总览。
异常处理：文件不存在、空文件、缺少字段、无有效数据时均有可读提示，不修改原始文件。
运行方式：


Bash

python generate_report.py
确保同目录下有 sales_raw.xlsx，运行后会生成 report.xlsx。

2 个文件已更改
