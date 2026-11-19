# -*- coding: utf-8 -*-
"""
实验3 任务1：切片删除深度探究（验证 + 分析，重点考点）

要求：先手写预判结果，再运行代码核对，分析为什么和直觉不一样；
      并解释「边遍历边删除」列表元素的 bug，给出安全修改方案。

运行：python task1_slice_delete.py
"""

SEP = "=" * 64


def banner(title):
    print("\n" + SEP)
    print(title)
    print(SEP)


def compare(expected, actual):
    """打印预判值、实测值与一致性结论。"""
    tag = "一致" if expected == actual else "不一致 → 见实验报告分析"
    print("  预判：", expected)
    print("  实测：", actual)
    print("  结论：", tag)


def main():
    banner("任务1  切片删除深度探究")
    print("原理：del 列表[切片] 先按「删除前」的原列表一次性算出全部目标索引，")
    print("      然后统一删除；不是删一个就重新编号，因此不存在动态索引。\n")

    src = list(range(10))
    cases = [
        ("del ls[::3]",  slice(None, None, 3), [1, 2, 4, 5, 7, 8]),
        ("del ls[1::3]", slice(1, None, 3),    [0, 2, 3, 5, 6, 8, 9]),
    ]
    for desc, sl, expected in cases:
        idx = list(range(*sl.indices(len(src))))
        ls = src.copy()
        del ls[sl]
        print(desc)
        print("  原列表：", src)
        print("  命中索引：", idx, "→ 命中值：", [src[i] for i in idx])
        compare(expected, ls)

    src3 = list(range(6))
    sl3 = slice(None, None, -2)
    idx3 = list(range(*sl3.indices(len(src3))))
    ls3 = src3.copy()
    del ls3[sl3]
    print("\ndel ls[::-2]（负步长，从末尾往前取）")
    print("  原列表：", src3, " 命中索引：", idx3, "→ 命中值：", [src3[i] for i in idx3])
    compare([0, 2, 4], ls3)

    print("\n【拓展坑】for 遍历的同时 remove 元素")
    ls4 = [1, 2, 3, 4, 5, 6]
    for i in ls4:
        if i % 2 == 0:
            ls4.remove(i)
    print("  for i in ls4: remove(i)  →", ls4, "（本例恰好没漏删，但不代表写法正确）")

    risky = [1, 2, 2, 4, 6, 3]
    r = risky.copy()
    for i in r:
        if i % 2 == 0:
            r.remove(i)
    print("  换成含连续偶数的数据", risky, "→", r, "  ← 有偶数被漏删！")
    print("  原因：for 用递增的内部下标；删除后后面的元素整体前移，")
    print("        下一个元素被「跳过」；且 remove(x) 按值只删第一个匹配项。")

    print("\n  安全的修改方案（三选一）：")
    print("   ① 列表推导式（推荐，生成新列表）：", [x for x in risky if x % 2 != 0])
    r2 = risky.copy()
    for i in range(len(r2) - 1, -1, -1):
        if r2[i] % 2 == 0:
            del r2[i]
    print("   ② 倒序按下标删除（原地，避免前移影响）：", r2)
    r3 = risky.copy()
    for x in r3[:]:                     # 遍历快照，操作原列表
        if x % 2 == 0:
            r3.remove(x)
    print("   ③ 遍历副本 / 快照：", r3)


if __name__ == "__main__":
    main()
