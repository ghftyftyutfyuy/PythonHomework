# -*- coding: utf-8 -*-
"""
实验3 任务3：集合全部运算 + 集合推导式

要求：给定 A = {2,4,6,8,10,12}、B = {3,6,9,12,15}，
      实现交集、并集、A-B、B-A、对称差集；
      并用集合推导式生成 1~30 中所有能被 4 整除的数字集合。

运行：python task3_set_ops.py
"""

SEP = "=" * 64


def banner(title):
    print("\n" + SEP)
    print(title)
    print(SEP)


def main():
    banner("任务3  集合运算 + 集合推导式")
    A = {2, 4, 6, 8, 10, 12}
    B = {3, 6, 9, 12, 15}
    print("  A =", A)
    print("  B =", B, "\n")

    # 运算符写法与等价的方法写法对照
    rows = [
        ("交集   A & B", A & B, A.intersection(B)),
        ("并集   A | B", A | B, A.union(B)),
        ("差集   A - B", A - B, A.difference(B)),
        ("差集   B - A", B - A, B.difference(A)),
        ("对称差 A ^ B", A ^ B, A.symmetric_difference(B)),
    ]
    for label, op, method in rows:
        print("  %-16s 运算符→ %-30s 方法→ %s"
              % (label, str(sorted(op)), sorted(method)))
    print("\n  说明：对称差 = 只属于其中一个集合的元素 = (A|B) - (A&B)。")

    div4 = {x for x in range(1, 31) if x % 4 == 0}
    print("  集合推导式：1~30 中能被 4 整除 =", sorted(div4))


if __name__ == "__main__":
    main()
