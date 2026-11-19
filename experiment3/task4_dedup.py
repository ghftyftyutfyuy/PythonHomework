# -*- coding: utf-8 -*-
"""
实验3 任务4：去重算法对比（保序 vs 无序去重）

要求：对 data = [5,2,7,2,5,9,7,3,9,1]：
      方案1 list(set(data))，观察输出顺序；
      方案2 手写保留第一次出现顺序的去重（不使用第三方库）；
      拓展：dict.fromkeys(data) 一行实现保序去重；
      并对比各方案优缺点。

运行：python task4_dedup.py
"""

SEP = "=" * 64


def banner(title):
    print("\n" + SEP)
    print(title)
    print(SEP)


def order_unique_by_list(seq):
    """指导书提示的做法：新列表 + not in 判断，时间复杂度 O(n^2)。"""
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def order_unique_by_set(seq):
    """改进做法：用集合记录已出现元素，保序且 O(n)（要求元素可哈希）。"""
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def main():
    banner("任务4  去重算法对比（保序 vs 无序）")
    data = [5, 2, 7, 2, 5, 9, 7, 3, 9, 1]
    print("  原始数据：", data, "\n")

    r1 = list(set(data))
    r2 = order_unique_by_list(data)
    r3 = order_unique_by_set(data)
    r4 = list(dict.fromkeys(data))
    print("  方案1 list(set(data))          →", r1, " 无序去重")
    print("  方案2 手写保序(新列表+not in)  →", r2)
    print("  方案3 手写保序(哈希辅助)       →", r3)
    print("  方案4 dict.fromkeys(data)      →", r4)

    print("\n  注意：方案1 这串小整数看起来是升序，只是巧合")
    print("        （CPython 中小整数 hash 等于自身，哈希桶恰好升序）。")
    words = ["banana", "apple", "cherry", "apple", "banana"]
    print("  换成字符串立刻乱序：", words, "→", list(set(words)))
    print("        （set 无序，且每次运行的顺序不保证一致）")

    print("\n  方案对比：")
    print("   方案1 最简洁、O(n)，但丢失原始顺序，不能用于需要保序的场景；")
    print("   方案2 完全按提示手写，逻辑直观，但 'not in 列表' 是线性查找，O(n^2)；")
    print("   方案3 用 set 记已见元素，保持 O(n) 且保序，元素必须可哈希；")
    print("   方案4 利用字典键唯一且自 Python 3.7 起保持插入顺序，一行搞定，最推荐。")


if __name__ == "__main__":
    main()
