def draw_tian_grid(width, cell_width=4):
    border = ("+" + "-" * cell_width) * width + "+"
    body = ("|" + " " * cell_width) * width + "|"

    for _ in range(width):
        print(border)
        print(body)
        print(body)
    print(border)


if __name__ == '__main__':
    n = int(input("请输入田字格宽度："))
    draw_tian_grid(n)
