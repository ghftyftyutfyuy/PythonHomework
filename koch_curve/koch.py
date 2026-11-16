import turtle
import math


def koch_curve(t, order, length):
    if order == 0:
        t.forward(length)
        return

    length /= 3

    koch_curve(t, order - 1, length)
    t.left(60)
    koch_curve(t, order - 1, length)
    t.right(120)
    koch_curve(t, order - 1, length)
    t.left(60)
    koch_curve(t, order - 1, length)


def draw_snowflake(order, size=300):
    screen = turtle.Screen()
    screen.title("科赫雪花")
    screen.bgcolor("white")
    screen.setup(width=800, height=800)
    screen.tracer(0)

    pen = turtle.Turtle()
    pen.color("#378ADD")
    pen.pensize(2)
    pen.penup()
    pen.goto(-size / 4, size * math.sqrt(3) / 4)
    pen.pendown()

    for _ in range(3):
        koch_curve(pen, order, size)
        pen.right(120)

    pen.hideturtle()
    screen.update()
    turtle.done()


if __name__ == '__main__':
    n = int(input("请输入科赫雪花阶数(0~4)："))

    if 0 <= n <= 4:
        draw_snowflake(n)
    else:
        print("阶数必须是 0~4")
