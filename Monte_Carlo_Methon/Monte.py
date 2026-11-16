import numpy as np
import matplotlib.pyplot as plt


def mc_rejection(mask, xlim, ylim, n=50000, batch=20000, seed=0):
    rng = np.random.default_rng(seed)
    kept = []
    hit = total = 0

    while hit < n:
        x = rng.uniform(xlim[0], xlim[1], batch)
        y = rng.uniform(ylim[0], ylim[1], batch)
        m = mask(x, y)
        kept.append(np.column_stack([x[m], y[m]]))
        hit += int(m.sum())
        total += batch

    return np.vstack(kept)[:n], hit / total


def circle_mask(x, y):
    return x * x + y * y <= 1


def heart_mask(x, y):
    return (x * x + y * y - 1) ** 3 - x * x * y ** 3 <= 0


def star_polygon(points=5, outer=1.0, inner=0.42):
    angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, points * 2, endpoint=False)
    radius = np.where(np.arange(points * 2) % 2 == 0, outer, inner)
    return np.column_stack([radius * np.cos(angles), radius * np.sin(angles)])


STAR = star_polygon()


def star_mask(x, y):
    inside = np.zeros_like(x, dtype=bool)
    x1, y1 = STAR[-1]

    for x2, y2 in STAR:
        cond = ((y1 > y) != (y2 > y)) & (
            x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-15) + x1
        )
        inside ^= cond
        x1, y1 = x2, y2

    return inside


def sierpinski(n=80000, seed=3):
    rng = np.random.default_rng(seed)
    v = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, np.sqrt(3) / 2]])
    p = np.empty((n, 2))
    cur = np.array([0.5, 0.2])

    for i in range(n):
        cur = (cur + v[rng.integers(0, 3)]) / 2
        p[i] = cur

    return p


def draw(ax, pts, title, color):
    ax.scatter(pts[:, 0], pts[:, 1], s=0.8, c=color, alpha=0.45, linewidths=0)
    ax.set_title(title)
    ax.set_aspect("equal")
    ax.axis("off")


circle, rate = mc_rejection(circle_mask, (-1, 1), (-1, 1), seed=1)
heart, _ = mc_rejection(heart_mask, (-1.4, 1.4), (-1.3, 1.3), seed=2)
star, _ = mc_rejection(star_mask, (-1.2, 1.2), (-1.2, 1.2), seed=3)
tri = sierpinski()

fig, axs = plt.subplots(2, 2, figsize=(10, 10))

draw(axs[0, 0], circle, f"Circle  pi ≈ {4 * rate:.4f}", "#e74c3c")
draw(axs[0, 1], heart, "Heart", "#e91e63")
draw(axs[1, 0], star, "Star", "#f39c12")
draw(axs[1, 1], tri, "Sierpinski Triangle", "#2c3e50")

plt.tight_layout()
plt.show()
