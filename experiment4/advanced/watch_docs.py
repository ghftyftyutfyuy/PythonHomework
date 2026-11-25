# -*- coding: utf-8 -*-

# ============================================================
# 【答辩速读】进阶 3：watchdog 让文件夹「一有新文档就自动重跑」
# 一句话：盯着 docs/，只要 .txt/.md 被新增或修改，就自动重新执行
#         「读取 -> 分词 -> 统计 -> 报告 -> 词云」全流程，实现无人值守。
# 三个关键点：
#   1) Observer + FileSystemEventHandler：watchdog 库监听文件系统事件
#   2) 防抖 debounce：1 秒内连续变动只触发一次，避免保存一次文件重跑好几遍
#   3) --once：只跑一次就退出，答辩演示用这个最稳（不会卡住 300 秒）
# 和另外两个进阶脚本一样，用 from main import DocumentAnalyzer 复用主程序类。
# 老师常问：防抖是什么？为什么要 1 秒？和定时轮询有什么区别？
# ============================================================

"""
实验四 · 进阶探索 3：watchdog 自动化工作流

监控 docs/ 文件夹，一旦有新文档放入或已有 .txt / .md 被修改，
自动重新触发「读取 -> 分词 -> 词频 -> 报告 -> 词云」全流程，实现无人值守审查。

用法（PyCharm 中直接运行）：
    python watch_docs.py --once     只做一次分析并退出（用于快速验证）
    python watch_docs.py --seconds 60   监控 60 秒，期间改动文件会自动重跑
    python watch_docs.py            默认监控 300 秒，Ctrl+C 可提前停止
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# 复用主程序的分析类，不重复写一遍流程代码
from main import DocumentAnalyzer  # noqa: E402


# 一次完整分析：加载词典和停用词 -> analyze() -> 写报告 -> 画词云。
# 整个包在 try/except 里，某个文件出问题只会打印错误，监控不会中断。
def run_analysis(tag: str) -> None:
    print(f"\n>>> [{tag}] 检测到文档变化，开始重新分析 ...")
    try:
        analyzer = DocumentAnalyzer()
        analyzer.load_user_dict()
        analyzer.stopwords = analyzer.load_stopwords()
        result = analyzer.analyze()
        txt, csv_path, corpus = analyzer.write_report(result)
        # 后台自动运行不能弹窗，所以 show=False，只把词云保存成 PNG
        image = analyzer.render_wordcloud(result, show=False)
        print(f"    完成：{len(result['details'])} 个文档，"
              f"去重词 {len(result['global'])} 个")
        print(f"    Top5：{'、'.join(w for w, _ in result['top50'][:5])}")
        print(f"    已更新：{image.name} / {txt.name} / {csv_path.name} / {corpus.name}")
    except Exception as exc:  # noqa: BLE001
        print(f"    分析失败：{exc}")


# 入口：先跑一次「初始化」分析，再按参数决定是单次验证还是持续监控
def main() -> int:
    parser = argparse.ArgumentParser(description="实验四：文档变更自动审查")
    # --once 单次验证；--seconds 控制监控时长，默认 300 秒，Ctrl+C 可提前停
    parser.add_argument("--once", action="store_true", help="只做一次分析后退出")
    parser.add_argument("--seconds", type=int, default=300, help="监控时长（秒）")
    args = parser.parse_args()

    docs_dir = BASE_DIR / "docs"
    print("=" * 64)
    print("进阶 3：watchdog 文档变更自动审查")
    print("=" * 64)
    print(f"监控目录：{docs_dir}")

    run_analysis("初始化")

    if args.once:
        print("\n--once 模式：单次验证完成，退出。")
        return 0

    try:
        # 延迟导入：--once 模式根本用不到 watchdog，缺这个库也能跑，
        # 把可选依赖的影响降到最低。
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        print("未安装 watchdog，请先执行：pip install watchdog")
        return 1

    # 防抖用的定时器；文件事件可能连续到达，再用 lock 保护定时器的读写
    debounce_timer: threading.Timer | None = None
    lock = threading.Lock()

    # 自定义事件处理器：只关心 .txt/.md 的新建、修改、移入这三类事件，
    # 文件夹事件和其他类型一律忽略，避免无关文件触发重跑。
    class Handler(FileSystemEventHandler):
        def on_any_event(self, event) -> None:
            nonlocal debounce_timer
            if event.is_directory or not str(event.src_path).lower().endswith((".txt", ".md")):
                return
            if event.event_type not in ("created", "modified", "moved_to"):
                return
            with lock:
                if debounce_timer is not None:
                    debounce_timer.cancel()
                # 【重点·防抖】每次事件先把上一个定时器取消，再重新计时 1 秒；
                # 所以连续保存文件只会在「最后一次」触发一次分析，不会重复跑很多遍。
                debounce_timer = threading.Timer(1.0, run_analysis, args=(Path(event.src_path).name,))
                debounce_timer.daemon = True
                debounce_timer.start()

    # 创建观察者，把处理器绑定到 docs/ 目录；recursive=False 只监控当前一层
    observer = Observer()
    observer.schedule(Handler(), str(docs_dir), recursive=False)
    observer.start()
    print(f"监控已启动，将持续 {args.seconds} 秒。试着往 docs/ 里放入或修改一个 .txt/.md 文件。")

    try:
        # 主线程等待指定时长；Ctrl+C 提前结束时，finally 里会 stop+join 释放资源
        time.sleep(args.seconds)
    except KeyboardInterrupt:
        print("\n收到 Ctrl+C，停止监控。")
    finally:
        observer.stop()
        observer.join()
    print("监控结束。")
    return 0


# 直接运行才执行；被 import 时不自动跑
if __name__ == "__main__":
    raise SystemExit(main())
