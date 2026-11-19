# -*- coding: utf-8 -*-
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

from main import DocumentAnalyzer  # noqa: E402


def run_analysis(tag: str) -> None:
    print(f"\n>>> [{tag}] 检测到文档变化，开始重新分析 ...")
    try:
        analyzer = DocumentAnalyzer()
        analyzer.load_user_dict()
        analyzer.stopwords = analyzer.load_stopwords()
        result = analyzer.analyze()
        txt, csv_path, corpus = analyzer.write_report(result)
        image = analyzer.render_wordcloud(result, show=False)
        print(f"    完成：{len(result['details'])} 个文档，"
              f"去重词 {len(result['global'])} 个")
        print(f"    Top5：{'、'.join(w for w, _ in result['top50'][:5])}")
        print(f"    已更新：{image.name} / {txt.name} / {csv_path.name} / {corpus.name}")
    except Exception as exc:  # noqa: BLE001
        print(f"    分析失败：{exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="实验四：文档变更自动审查")
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
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        print("未安装 watchdog，请先执行：pip install watchdog")
        return 1

    debounce_timer: threading.Timer | None = None
    lock = threading.Lock()

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
                debounce_timer = threading.Timer(1.0, run_analysis, args=(Path(event.src_path).name,))
                debounce_timer.daemon = True
                debounce_timer.start()

    observer = Observer()
    observer.schedule(Handler(), str(docs_dir), recursive=False)
    observer.start()
    print(f"监控已启动，将持续 {args.seconds} 秒。试着往 docs/ 里放入或修改一个 .txt/.md 文件。")

    try:
        time.sleep(args.seconds)
    except KeyboardInterrupt:
        print("\n收到 Ctrl+C，停止监控。")
    finally:
        observer.stop()
        observer.join()
    print("监控结束。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
