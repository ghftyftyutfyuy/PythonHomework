# -*- coding: utf-8 -*-
"""
实验3 任务2：嵌套容器与可哈希深度辨析（探究题）

要求：依次测试 (1,2,3)、(1,[2,3])、[1,2]、frozenset({1,2})、{1,2}
      能否加入集合，逐条记录成功或报错并写出理由；说明 frozenset 的作用。

运行：python task2_hashable.py
"""

SEP = "=" * 64


def banner(title):
    print("\n" + SEP)
    print(title)
    print(SEP)


def main():
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


if __name__ == "__main__":
    main()
