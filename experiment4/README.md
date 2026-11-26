# 实验四：本地文档智能审查与摘要 Agent

> 对应实验指导书《本地文档智能审查与摘要 Agent 实验指导书》（PDF，4 页）。
> 命名延续本仓库规则：`experiment1` / `experiment2` / `experiment3` / **`experiment4`** / `experiment5`。
> 本 README 兼作实验报告，在 GitHub 上可直接阅读。

## 一、实验目的

1. 掌握使用 Python 进行批量文件读取与文本预处理的方法。
2. 熟练运用 `jieba` 进行中文分词、停用词过滤及自定义词典加载。
3. 掌握 `wordcloud` 参数配置，生成具有业务指导意义的数据可视化词云。
4. 体验 Vibe Coding 工作流，学习用结构化 Prompt 引导 AI 完成代码架构设计与实现。

## 二、实验环境

| 项目 | 版本 / 说明 |
| --- | --- |
| Python | 3.11（要求 3.8 及以上） |
| 核心依赖 | `jieba`、`wordcloud`、`matplotlib`、`numpy`、`pillow` |
| 进阶依赖 | `watchdog`（自动监控）、`requests`（大模型 API） |
| 安装 | `pip install jieba wordcloud matplotlib numpy pillow watchdog requests` |
| IDE | PyCharm，脚本可直接右键运行，结果打印在运行窗口 |

完整依赖见 [`requirements.txt`](./requirements.txt)。

## 三、需求边界定义（步骤 1）

| 项目 | 内容 |
| --- | --- |
| **输入** | ① 含多个 `.txt` / `.md` 的本地文件夹路径；② 自定义停用词表；③ 自定义专业词典 |
| **处理** | 批量读取 → 文本清洗 → 加载自定义词典 → jieba 精确模式分词 → 过滤停用词与单字符 → 统计词频 |
| **输出** | ① Top50 高频词词云 PNG（1000×800，白底）；② 各文件核心关键词汇总报告（TXT + CSV） |
| **约束** | 完善错误处理（文件不存在、编码错误、无有效词）；中文字体正常显示；结果在 PyCharm 运行窗口直接可见 |

## 四、实验步骤与交付物对照

| 指导书步骤 | 本文件夹中的交付物 |
| --- | --- |
| 步骤 1 定义需求边界 | 本 README 第三节 |
| 步骤 2 结构化 Prompt | [`prompts.md`](./prompts.md) 第二节（初始 Prompt）+ 第三节（分模块迭代记录）+ 第四节（报错反馈闭环） |
| 步骤 3 核心代码实现与本地验证 | [`main.py`](./main.py)、[`docs/`](./docs/)、[`stopwords.txt`](./stopwords.txt)、[`user_dict.txt`](./user_dict.txt)、[`output/`](./output/)、[`运行结果.txt`](./运行结果.txt) |
| 步骤 4 进阶探索与 Agent 化改造 | [`advanced/`](./advanced/) 下三个脚本（见下表） |

## 五、目录结构

```text
experiment4/
├── README.md                          # 本实验报告 / 说明
├── prompts.md                         # 结构化 Prompt 与 Vibe Coding 迭代记录
├── requirements.txt
├── main.py                            # 主程序：批量读取 → 分词 → 词频 → 词云 → 汇总报告
├── docs/                              # 输入：待审查的本地文档（4 篇）
│   ├── 人工智能与教育.txt
│   ├── 十五五报告.txt                  # 约 183 KB 的长文本，全局词频主要由它贡献
│   ├── 新质生产力与产业发展.md
│   └── 数字中国建设.txt
├── stopwords.txt                      # 自定义停用词表（UTF-8，每行一词，100 个）
├── user_dict.txt                      # 自定义专业词典（UTF-8，jieba load_userdict 格式）
├── advanced/
│   ├── monte_carlo_simulation.py      # 进阶 1：蒙特卡洛随机抽样与概率分布预测
│   ├── llm_review_agent.py            # 进阶 2：组装结构化 Prompt 并对接大模型 API
│   └── watch_docs.py                 # 进阶 3：watchdog 文件夹自动监控
├── output/                            # 运行产物（已随仓库上传，作为结果证据）
│   ├── document_wordcloud.png        # Top50 词云图
│   ├── keywords_report.txt           # 关键词汇总报告（TXT）
│   ├── keywords_report.csv           # 关键词汇总报告（CSV）
│   ├── cleaned_corpus.txt            # 清洗后的核心文本片段
│   ├── monte_carlo_context.txt       # 蒙特卡洛补充上下文
│   └── review_prompt.txt             # 组装好的大模型审查 Prompt
└── 运行结果.txt                       # 四个脚本的完整运行输出留档
```

## 六、运行方式

在 PyCharm 中直接运行 `main.py`（右键 → Run），或在终端执行：

```bash
cd E:\PythonHomework\experiment4
python main.py
python main.py --no-show                 # 不弹词云窗口，适合无界面环境
python main.py --docs ./docs --output ./output --font C:/Windows/Fonts/msyh.ttc
python main.py --mask ./mask.png        # 可选：用 numpy + pillow 读入背景蒙版
```

进阶脚本：

```bash
python advanced/monte_carlo_simulation.py
python advanced/llm_review_agent.py
python advanced/watch_docs.py --once        # 单次验证
python advanced/watch_docs.py --seconds 60  # 监控 60 秒，往 docs/ 放文件会自动重跑
```

> 说明：指导书参考代码中 `analyze_documents(...)` 是被注释掉的调用，直接复制运行「什么也不会发生」。
> 本实现改为 `if __name__ == "__main__":` 直接可运行，并把结果同时打印到控制台。

## 七、运行结果（本地实跑，Python 3.11，2026-11-26 更新）

> `docs/` 新增《十五五报告.txt》（约 183 KB）后重新实跑，以下为 4 篇文档的最新结果。

```text
[1/4] 自定义词典加载完成：54 个词条
[2/4] 停用词表加载完成：100 个词
[3/4] 批量读取 + 清洗 + 分词 + 词频统计 ...
[4/4] 生成汇总报告与词云 ...

文档数量  : 4
  ✓ 人工智能与教育.txt        724 字符 /   227 有效词 | Top3: 人工智能(9)、数据(8)、教师(7)
  ✓ 十五五报告.txt          59786 字符 / 21077 有效词 | Top3: 发展(415)、建设(290)、体系(202)
  ✓ 数字中国建设.txt          898 字符 /   264 有效词 | Top3: 建设(7)、数据(6)、数字中国(5)
  ✓ 新质生产力与产业发展.md    957 字符 /   279 有效词 | Top3: 产业(10)、新质生产力(9)、技术(5)

全局有效词 21847 个，去重后 4577 个
全局 Top10：发展(424)、建设(302)、体系(208)、健全(187)、机制(159)、
            实施(149)、国家(139)、制度(136)、服务(131)、加快(124)
```

四个脚本（主程序 + 三个进阶）全部 `exit 0`，完整输出见 [`运行结果.txt`](./运行结果.txt)。

**结果解读**：四篇材料共享「发展 / 建设 / 体系 / 机制 / 制度」等高频词，说明共同主线是**以制度建设与规划部署支撑发展**；其中《十五五报告》篇幅远大（59786 字符 / 21077 有效词），所以全局 Top50 主要由它贡献。各文件 Top3 又能清晰区分各自侧重（教师 / 发展 / 数字中国 / 产业），自定义词典成功把「新质生产力」「数字中国」「数据要素」等专有名词整体切出，词云具备业务指导意义。

> 说明：答辩现场以 `python main.py --no-show` 的实时输出为准；`docs/` 内容变化时数字会随之变化。

## 八、实验注意事项（指导书第四节）

1. **字体问题**：`wordcloud` 默认不支持中文。本实现通过 `find_chinese_font()` 自动探测 `msyh.ttc` / `simhei.ttf` / `simsun.ttc`，也可用 `--font` 手动指定；找不到字体时直接给出可读报错，避免生成一图方框。matplotlib 标题同样设置了中文字体并关闭负号乱码。
2. **停用词与自定义词典**：两个文件均为纯文本、每行一个词、UTF-8 保存。自定义词典采用 `词语 词频 词性` 三列格式，`jieba.load_userdict()` 加载。加载专业词典后，「新质生产力」「数字中国」「数据要素」等不再被切碎，分词准确率明显提升。
3. **编码容错**：`utf-8-sig → utf-8 → gb18030` 三级回退，报告中记录了每个文件实际采用的编码，避免 Windows 记事本另存文件带 BOM 或 GBK 导致崩溃。
4. **Vibe Coding 实践**：按「文件读取 → 分词统计 → 词云生成 → 异常处理」分模块迭代，每轮运行验证，报错后把完整信息反馈给 AI 修复，过程见 [`prompts.md`](./prompts.md)。

## 九、进阶探索与 Agent 化改造（步骤 4）

| 进阶项 | 文件 | 实现要点 |
| --- | --- | --- |
| 蒙特卡洛方法 | `advanced/monte_carlo_simulation.py` | 按词频构造概率分布，随机抽 20 个词、模拟 20000 次，给出命中核心词数量的均值 / 标准差 / 95% 区间；对最高频主题词做 2000 次 bootstrap 得到概率置信区间。结果写入 `monte_carlo_context.txt` 作为补充上下文。 |
| 对接大模型 API | `advanced/llm_review_agent.py` | 把 Top50 关键词与词频、清洗后的核心文本片段、蒙特卡洛上下文组装成结构化 Prompt，要求输出「主题综述 / 核心要点 / 审查意见 / 一句话摘要」四部分。配置 `LLM_API_KEY`（可选 `LLM_BASE_URL`、`LLM_MODEL`）后调用 OpenAI 兼容接口；未配置密钥或调用失败时安全降级，只打印并保存 Prompt，不发起外部请求。 |
| 自动化工作流 | `advanced/watch_docs.py` | `watchdog` 监控 `docs/`，`.txt` / `.md` 新增或修改后（1 秒防抖）自动重跑全流程并刷新词云与报告，实现无人值守审查。`--once` 可单次验证，`--seconds` 控制监控时长。 |

## 十、实验小结

本实验把一个「文本处理脚本」逐步扩展成一个具备输入边界、容错能力、可视化输出与可扩展 Agent 接口的文档审查原型。三点体会：

1. **结构化 Prompt 的价值在于约束而非描述**。把输入 / 处理 / 输出 / 约束写清楚，AI 产出的代码才可直接落地；按模块分轮迭代比一次性生成全部代码更容易定位与修复问题。
2. **中文文本处理的两个关键点是「词典」和「字体」**。专业词典决定词频是否有业务含义，中文字体决定词云是否可读；两者都不是算法问题，却最容易让实验结果失真。
3. **错误处理属于功能而非补丁**。文件不存在、编码不一致、无有效词、缺字体都给出明确提示，程序才可能在无人值守的 Agent 工作流中长期运行。

从 Agent 视角看，本原型已经具备「感知（文件遍历）→ 处理（分词统计）→ 输出（词云 / 报告）→ 扩展（蒙特卡洛量化、LLM 审查、watchdog 触发）」的完整链路，后续只需接入真实大模型即可自动产出审查意见。
