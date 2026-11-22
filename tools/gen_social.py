"""生成仓库的 Social Preview 封面（1280x640 PNG）。

GitHub 的仓库 Social Preview 没有上传 API，只能在
Settings → Social preview 手动传图，所以这里只负责出图。

用法：python tools/gen_social.py
输出：assets/social/<仓库名>.png
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen_banner import (  # noqa: E402  复用同一套字模与调色板
    BG,
    CAT,
    CYAN,
    DASH,
    DIM,
    GRID,
    INK,
    MAGENTA,
    ROOT,
    pixel_text,
    pixel_text_width,
    rects_to_png,
    runs,
)

W, H = 1280, 640
PAD = 72
MAXW = W - PAD * 2 - 40  # 名称可用宽度

REPOS = [
    dict(
        name="astrbot_plugin_lolmatch",
        tagline="LOL ESPORTS SCHEDULE AND PUSH",
        lang="PYTHON",
        kind="ASTRBOT PLUGIN",
    ),
    dict(
        name="astrbot_plugin_bili_card",
        tagline="BILIBILI LINK TO CARD",
        lang="PYTHON",
        kind="ASTRBOT PLUGIN",
    ),
    dict(
        name="astrbot_plugin_steamhub",
        tagline="STEAM FRIEND TRACKER",
        lang="PYTHON",
        kind="ASTRBOT PLUGIN",
    ),
    dict(
        name="nas-log-analyzer",
        tagline="SYNOLOGY AUDIT LOG SEARCH",
        lang="PYTHON",
        kind="TOOLING",
    ),
    dict(
        name="symlink-explorer",
        tagline="WINDOWS SYMLINK MANAGER",
        lang="PYTHON",
        kind="TOOLING",
    ),
    dict(
        name="ahk-scripts",
        tagline="AUTOHOTKEY V2 SCRIPTS",
        lang="AHK",
        kind="TOOLING",
    ),
]


def fit_px(text, maxw, hi=13, lo=5):
    """返回能塞进 maxw 的最大点阵单元尺寸。"""
    for px in range(hi, lo - 1, -1):
        if pixel_text_width(text, px) <= maxw:
            return px
    return lo


def split_name(up, maxlen=14):
    """按下划线切分长仓库名，保证每行不超过 maxlen 个字符。"""
    if len(up) <= maxlen:
        return [up]
    lines, cur = [], ""
    for part in up.split("_"):
        cand = part if not cur else f"{cur}_{part}"
        if len(cand) <= maxlen:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = part
    if cur:
        lines.append(cur)
    return lines


def layout_name(up):
    """单行放得下就用单行（字号不低于 8），否则拆成两行。"""
    px = fit_px(up, MAXW, hi=12, lo=8)
    if pixel_text_width(up, px) <= MAXW and px >= 8:
        return [up], px
    lines = split_name(up)
    px = min(fit_px(line, MAXW) for line in lines)
    return lines, px


def brackets(rects, m=32, ln=44, th=2, color=CYAN):
    """四角 HUD 直角标记。"""
    for x, y, dx, dy in (
        (m, m, 1, 1),
        (W - m, m, -1, 1),
        (m, H - m, 1, -1),
        (W - m, H - m, -1, -1),
    ):
        hx = x if dx > 0 else x - ln
        vy = y if dy > 0 else y - ln
        rects.append((hx, y - (th - 1), ln, th, color))
        rects.append((x - (th - 1), vy, th, ln, color))


def cover(repo):
    rects = []

    # 网格底
    for x in range(0, W, 40):
        rects.append((x, 0, 1, H, GRID))
    for y in range(0, H, 40):
        rects.append((0, y, W, 1, GRID))

    # 星点
    rnd = random.Random(repo["name"])
    for _ in range(26):
        rects.append(
            (
                rnd.randrange(0, W, 4),
                rnd.randrange(0, H, 4),
                rnd.choice([2, 2, 3]),
                rnd.choice([2, 2, 3]),
                rnd.choice([DASH, CYAN, GRID]),
            )
        )

    # 顶部标识
    rects += pixel_text("GITHUB.COM/SZJMHXD", 3, PAD, 46, DIM)

    # 右上角像素猫
    cat_px = 4
    cat_w = len(CAT[0]) * cat_px
    rects += runs(CAT, cat_px, W - PAD - cat_w, 38, MAGENTA)

    # 名称
    lines, px = layout_name(repo["name"].upper())
    gap = 3 * px
    block_h = len(lines) * 7 * px + (len(lines) - 1) * gap
    top = 300 - block_h // 2

    rects.append((PAD, top, 8, block_h, MAGENTA))
    nx = PAD + 8 + 30
    for i, line in enumerate(lines):
        y = top + i * (7 * px + gap)
        rects += pixel_text(line, px, nx, y, INK)

    # 副标题
    tag_y = top + block_h + 40
    rects += pixel_text(repo["tagline"], 3, PAD + 8, tag_y, CYAN)

    # 底部语言标签
    chip_y = H - 124
    chip_w = pixel_text_width(repo["lang"], 3) + 44
    rects.append((PAD, chip_y, chip_w, 46, DASH))
    rects.append((PAD, chip_y, chip_w, 3, CYAN))
    rects.append((PAD, chip_y + 43, chip_w, 3, CYAN))
    rects += pixel_text(repo["lang"], 3, PAD + 22, chip_y + 13, CYAN)

    # 底部右侧分类
    kw = pixel_text_width(repo["kind"], 3)
    rects += pixel_text(repo["kind"], 3, W - PAD - kw, chip_y + 13, DIM)

    # 底部横线
    for x in range(PAD, W - PAD, 16):
        rects.append((x, H - 156, 8, 2, DASH))

    brackets(rects)
    return rects


def main():
    out = ROOT / "assets" / "social"
    out.mkdir(parents=True, exist_ok=True)
    for repo in REPOS:
        path = rects_to_png(cover(repo), W, H, BG, out / f"{repo['name']}.png")
        print(f"{path.name:32} {path.stat().st_size / 1024:6.1f} KB")
    print("done ->", out)


if __name__ == "__main__":
    main()
