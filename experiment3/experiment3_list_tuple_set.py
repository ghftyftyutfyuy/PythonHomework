# -*- coding: utf-8 -*-
"""
实验3  Python 列表、元组、集合
课程：Python 程序设计        实验类型：验证 + 综合设计 + 分析探究

【改写说明】（对应指导书第六节「禁止直接复制上交，需要自己改写」）
1. 把平铺的参考代码重构为 5 个独立任务函数 + 统一入口；
2. 任务1 增加「预判值 / 实测值 / 是否一致」自动对比，并补充能真正触发 bug 的反例；
3. 任务2 用 try/except 逐条捕获 TypeError，自动记录成功或报错原因；
4. 任务4 提供三种保序去重实现，并补充字符串样例证明 list(set(...)) 会乱序；
5. 任务5 复用保序去重函数，每一步输出都带文字解释，并完成嵌套列表去重拓展；
6. 运行时用 Tee 把控制台输出同步保存为「运行结果.txt」，便于截图与撰写报告。

运行环境：Python 3.x，标准库，无第三方库依赖。
"""
import sys
from pathlib import Path


SEP = "=" * 64


class Tee:
    """把一份输出同时写到控制台和日志文件。"""

    def __init__(self, *streams):
        self._streams = streams

    def write(self, text):
        for s in self._streams:
            s.write(text)

    def flush(self):
        for s in self._streams:
            s.flush()


def banner(title):
    print("\n" + SEP)
    print(title)
    print(SEP)


def compare(expected, actual):
    """任务1 专用：打印预判值、实测值与一致性结论。"""
    tag = "一致" if expected == actual else "不一致 → 见实验报告分析"
    print("  预判：", expected)
    print("  实测：", actual)
    print("  结论：", tag)


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


# ------------------------------ 任务1 ------------------------------
def task1_slice_delete():
    banner("任务1  切片删除深度探究（验证 + 分析）")
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
    print("  for i in ls4: remove(i)  →", ls4,
          "（本例恰好没漏删，但不代表写法正确）")

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


# ------------------------------ 任务2 ------------------------------
def task2_hashable():
    banner("任务2  嵌套容器与可哈希深度辨析")
    print("规则：能放进 set 的对象必须可哈希（生命周期内 hash 值不变）；")
    print("      容器「只要含有一个不可哈希元素」就整体不可哈希。\n")

    candidates = [
        ("(1, 2, 3)",         lambda: (1, 2, 3)),
        ("(1, [2, 3])",       lambda: (1, [2, 3])),
        ("[1, 2]",            lambda: [1, 2]),
        ("frozenset({1, 2})", lambda: frozenset({1, 2})),
        ("{1, 2}",            lambda: {1, 2}),
    ]
    s = set()
    for name, make in candidates:
        try:
            s.add(make())
            print("  s.add(%-18s) → 成功：可哈希" % name)
        except TypeError as exc:
            print("  s.add(%-18s) → TypeError: %s" % (name, exc))
    print("\n  集合最终内容：", s)

    t = (1, [2, 3])
    t[1].append(4)
    print("\n  t = (1, [2, 3]) 后执行 t[1].append(4) →", t)
    print("  合法：元组只保证「引用地址」不变，不限制引用指向的列表内容被修改。")
    print("  但 t 含列表，整体不可哈希，所以仍不能 s.add(t)。")
    print("\n  结论：需要「集合里放集合」时，内层必须用 frozenset（不可变、可哈希）。")


# ------------------------------ 任务3 ------------------------------
def task3_set_ops():
    banner("任务3  集合运算 + 集合推导式")
    A = {2, 4, 6, 8, 10, 12}
    B = {3, 6, 9, 12, 15}
    print("  A =", A)
    print("  B =", B, "\n")

    rows = [
        ("交集   A & B", A & B, A.intersection(B)),
        ("并集   A | B", A | B, A.union(B)),
        ("差集   A - B", A - B, A.difference(B)),
        ("差集   B - A", B - A, B.difference(A)),
        ("对称差 A ^ B", A ^ B, A.symmetric_difference(B)),
    ]
    for label, op, method in rows:
        print("  %-16s 运算符→ %-30s 方法→ %s" % (label, str(sorted(op)), sorted(method)))
    print("\n  说明：对称差 = 只属于其中一个集合的元素 = (A|B) - (A&B)。")

    div4 = {x for x in range(1, 31) if x % 4 == 0}
    print("  集合推导式：1~30 中能被 4 整除 =", sorted(div4))


# ------------------------------ 任务4 ------------------------------
def task4_dedup():
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


# ------------------------------ 任务5 ------------------------------
def task5_course():
    banner("任务5  综合设计：两个班选课编号统计（必做）")
    class1 = [101, 103, 105, 107, 109, 103, 101]
    class2 = [102, 104, 106, 108, 109, 107, 102]
    print("  1班原始：", class1)
    print("  2班原始：", class2, "\n")

    u1 = order_unique_by_set(class1)
    u2 = order_unique_by_set(class2)
    print("  ① 1班不重复编号（按首次出现保序）：", u1)
    print("     2班不重复编号（按首次出现保序）：", u2)
    print("     说明：先去重再统计，重复的 103/101、107/102 只算一次。\n")

    s1, s2 = set(u1), set(u2)
    both = s1 & s2
    only_one = s1 ^ s2
    only_c1 = s1 - s2
    print("  ② 同时选两门（交集 s1 & s2）：", sorted(both))
    print("     说明：既出现在 1 班又出现在 2 班的编号。")
    print("  ③ 只选其中一门（对称差 s1 ^ s2）：", sorted(only_one))
    print("     说明：去掉交集后剩下的所有编号，等价于 (s1|s2) - (s1&s2)。")
    print("  ④ 选了 1 班但没选 2 班（差集 s1 - s2）：", sorted(only_c1))
    print("     说明：以 1 班为基准做差，只保留不在 2 班中的编号。")

    t_both = tuple(sorted(both))
    print("\n  ⑤ 交集转元组：", t_both)
    print("     说明：交集元素是 int（不可变、可哈希），元组能装可哈希对象，")
    print("           所以 tuple(...) 合法；同理这些元素也能直接放进 set。")
    print("           （若元素是 list 这类不可哈希对象，则既不能转 set 也不能作字典键。）")

    print("\n  【拓展】嵌套列表去重")
    nest = [[1, 2], [3, 4], [1, 2], [5, 6]]
    seen, uniq = set(), []
    for inner in nest:
        key = tuple(inner)              # 内层 list 不可哈希 → 先转 tuple
        if key not in seen:
            seen.add(key)
            uniq.append(inner)          # 需要列表形态则保留原对象
    print("  原始：", nest)
    print("  去重：", uniq, "（内层 list → tuple 作键去重，再保留/转回 list）")


# ------------------------------ 入口 ------------------------------
def run_all():
    print("实验3  Python 列表、元组、集合 —— 运行结果")
    print("环境：Python 3.x，标准库，无第三方依赖")
    task1_slice_delete()
    task2_hashable()
    task3_set_ops()
    task4_dedup()
    task5_course()
    banner("全部 5 个任务执行完毕")


def main():
    log_path = Path(__file__).resolve().with_name("运行结果.txt")
    origin = sys.stdout
    with log_path.open("w", encoding="utf-8") as f:
        sys.stdout = Tee(origin, f)
        try:
            run_all()
        finally:
            sys.stdout = origin
    print("运行结果已同步保存到：", log_path)


if __name__ == "__main__":
    main()
