# -*- coding: utf-8 -*-
"""
实验3 任务5：综合设计题（必做，分值最高）

需求：class1 = [101,103,105,107,109,103,101]
      class2 = [102,104,106,108,109,107,102]
  ① 分别获取两个班不重复的选课学生编号（保序）；
  ② 求出同时选两门课的学生编号；
  ③ 求出只选其中一门课的学生编号（对称差）；
  ④ 求出选了 1 班但是没有选 2 班的学生编号；
  ⑤ 将最终的交集结果转为元组（说明为什么可以转元组、还能存入集合）。
  输出所有结果，并配上文字说明。
  拓展：对嵌套列表 nest = [[1,2],[3,4],[1,2],[5,6]] 去重。

运行：python task5_course.py
"""

SEP = "=" * 64


def banner(title):
    print("\n" + SEP)
    print(title)
    print(SEP)


def order_unique(seq):
    """保序去重：用集合记录已出现元素，按首次出现顺序输出。"""
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def main():
    banner("任务5  综合设计：两个班选课编号统计（必做）")
    class1 = [101, 103, 105, 107, 109, 103, 101]
    class2 = [102, 104, 106, 108, 109, 107, 102]
    print("  1班原始：", class1)
    print("  2班原始：", class2, "\n")

    u1 = order_unique(class1)
    u2 = order_unique(class2)
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


if __name__ == "__main__":
    main()
