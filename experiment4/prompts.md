# 实验四 · Vibe Coding 结构化 Prompt 与迭代记录

> 对应指导书「步骤 1：定义可执行的需求边界」「步骤 2：编写结构化 Prompt」「步骤 4：进阶探索」。
> 本文件是实验过程记录，不作为程序运行依赖。

## 一、需求边界澄清（对应步骤 1）

| 项目 | 内容 |
| --- | --- |
| 输入 | ① 含多个 `.txt` / `.md` 的本地文件夹路径；② 自定义停用词表路径；③ 自定义专业词典路径 |
| 处理 | 批量读取 → 文本清洗 → 加载自定义词典 → jieba 精确模式分词 → 过滤停用词与单字符 → 统计词频 |
| 输出 | ① Top50 高频词词云图片（PNG，1000×800，白底）；② 含各文件核心关键词的汇总报告（TXT / CSV） |
| 约束 | 完善错误处理（文件不存在、编码错误、无有效词）；支持中文字体正常显示；结果在 PyCharm 运行窗口直接可见 |

## 二、初始结构化 Prompt（对应步骤 2 模板）

```text
需求背景：我需要开发一个本地文档分析工具，用于批量处理文件夹中的文本文件，
提取高频词并生成词云。

明确约束：
1. 使用 os 或 pathlib 遍历指定目录下的所有 .txt 与 .md 文件。
2. 使用 jieba 进行精确模式分词，要求支持加载自定义词典 user_dict.txt
   和停用词表 stopwords.txt；两个文件均为 UTF-8 编码，每行一个词语。
3. 使用 wordcloud 生成词云，指定中文字体路径 font_path='C:/Windows/Fonts/msyh.ttc'，
   背景色为白色，尺寸为 1000x800，max_words=50，collocations=False。
4. 代码需包含详细的中文注释，并处理文件不存在、编码错误、无有效词等异常。
5. 除了词云之外，还要输出一份汇总报告，列出每个文件各自的 Top10 关键词。

输出要求：请提供完整的 Python 代码，并简要说明如何配置停用词表和自定义词典；
所有统计结果请同时 print 到终端，不要只写文件。
```

## 三、分模块迭代对话记录（按指导书建议顺序）

| 轮次 | 对 AI 的指令（摘要） | AI 产出 | 本地微调 / 审查 | 验证结果 |
| --- | --- | --- | --- | --- |
| 1 | 「先只写批量读取 + 多编码回退 + 清洗函数」 | `os.listdir` + `open(..., encoding='utf-8')` | 改为 `pathlib`；增加 `utf-8-sig / utf-8 / gb18030` 三级回退；增加目录不存在、非目录、空目录判断 | 3 篇文档全部读取成功，编码均识别为 `utf-8-sig` |
| 2 | 「在上一版基础上加 jieba 分词、自定义词典、停用词过滤、Counter 统计」 | `jieba.lcut` + 单字符过滤 | 关闭 jieba 加载日志（`setLogLevel`）；增加「必须含中文或字母数字」的正则；把类抽成 `DocumentAnalyzer` 方便复用 | 全局有效词 770 个、去重 493 个 |
| 3 | 「加词云生成与保存」 | `WordCloud.generate_from_frequencies` | 自动探测 `msyh.ttc / simhei.ttf / simsun.ttc`；加 `--mask` 用 `numpy + pillow` 处理蒙版；matplotlib 标题设置中文字体；加 `--no-show` 便于无界面验证 | 生成 `document_wordcloud.png`，中文无方框 |
| 4 | 「补齐异常处理，并输出每文件关键词报告」 | 单文件 try/except | 异常统一收集到 `errors` 并写入报告；TXT + CSV 双份输出；额外产出 `cleaned_corpus.txt` 供后续 Agent 使用 | 报告含全局 Top50 与 3 个文件各 Top10 |
| 5 | 「按进阶探索做 Agent 化改造」 | 三段独立脚本 | 蒙特卡洛结果写入 `monte_carlo_context.txt` 作为 LLM 补充上下文；大模型调用支持环境变量且无密钥时安全降级；watchdog 加 1 秒防抖 | 三个进阶脚本均 `exit 0` |

## 四、报错反馈闭环（Vibe Coding「报错反馈」环节留痕）

1. **现象**：首版词云中文显示为方框。
   **反馈给 AI**：`WordCloud` 未指定 `font_path`，且 Windows 字体路径需写绝对路径。
   **修复**：增加 `find_chinese_font()` 自动探测 + `--font` 手动指定，未找到字体直接抛出可读错误。

2. **现象**：部分 `.txt` 读取时抛 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xa1`。
   **反馈给 AI**：本地记事本另存的文件可能带 BOM 或为 GBK。
   **修复**：改为 `ENCODINGS = ("utf-8-sig", "utf-8", "gb18030")` 依次回退，并把实际使用的编码写进报告。

3. **现象**：`jieba` 首次运行在运行窗口刷出红色加载日志，干扰查看统计结果。
   **反馈给 AI**：需要静默词典加载日志。
   **修复**：`jieba.setLogLevel(logging.ERROR)`。

4. **现象**：本地文件名 `user_dict.txt` 与 `stopwords.txt` 若被误命名为库名会遮住第三方库。
   **约定**：所有本地脚本不得命名为 `jieba.py` / `wordcloud.py` / `requests.py`。

## 五、进阶探索对应文件

| 指导书进阶项 | 实现文件 | 说明 |
| --- | --- | --- |
| 引入蒙特卡洛方法 | `advanced/monte_carlo_simulation.py` | 按词频概率抽样 20000 次，输出命中核心词数量分布与主题词概率置信区间 |
| 对接大模型 API | `advanced/llm_review_agent.py` | 关键词 + 词频 + 清洗语料 + 蒙特卡洛上下文 → 结构化审查 Prompt；配置 `LLM_API_KEY` 后自动调用 |
| 构建自动化工作流 | `advanced/watch_docs.py` | watchdog 监控 `docs/`，新增/修改文档自动重跑全流程 |
