"""生成 GitHub Profile README 的像素科幻风资源。

设计语言：
  像素   —— 所有文字用手绘点阵 / 二值化点阵，边缘零抗锯齿
  科幻   —— 深空底 + 透视网格 + HUD 角标 + 扫描线 + 霓虹色发光
  二次元 —— 赛博粉点缀 + 像素猫 + 颜文字式小图标

用法：python tools/gen_banner.py
输出：assets/banner.svg、assets/divider.svg、assets/skills.svg
"""
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/msyhbd.ttc"

# ---------------------------------------------------------------- 调色板
THEME = os.environ.get("THEME", "light")
SUFFIX = "" if THEME == "light" else "-dark"

_PALETTES = {
    # 浅色：白底蓝图感，靠细网格和硬边描边撑住科幻调性
    "light": dict(
        BG="#FAFBFF", GRID="#E7EDF8", CYAN="#0E9F94", CYAN_D="#08736B",
        MAGENTA="#FB4D8D", YELLOW="#F5A524", INK="#1A1D2E", DIM="#7C8AA0",
        ZH_SH="#BFE3DF", DASH="#DDE6F4", CARD="#F1F6FD", CARD_GRID="#DDE7F5",
        SPARK=["#D8E2F0", "#A9D9D4", "#FFC7DC", "#C9D4E6"],
        GLOW=0.10, SCAN=0.045,
    ),
    # 深色：深空霓虹，扫描线压在点阵上
    "dark": dict(
        BG="#0A0B14", GRID="#161A2C", CYAN="#2EE6D0", CYAN_D="#7FF0E4",
        MAGENTA="#FF5FA2", YELLOW="#FFD166", INK="#E8ECFF", DIM="#5F6685",
        ZH_SH="#134A46", DASH="#20243A", CARD="#12152A", CARD_GRID="#1D2136",
        SPARK=["#3A4062", "#2EE6D0", "#FF5FA2", "#8892B8"],
        GLOW=0.16, SCAN=0.10,
    ),
}
_T = _PALETTES[THEME]
BG, GRID, CYAN, CYAN_D = _T["BG"], _T["GRID"], _T["CYAN"], _T["CYAN_D"]
MAGENTA, YELLOW, INK, DIM = _T["MAGENTA"], _T["YELLOW"], _T["INK"], _T["DIM"]
ZH_SH, DASH = _T["ZH_SH"], _T["DASH"]
CARD, CARD_GRID = _T["CARD"], _T["CARD_GRID"]

# ---------------------------------------------------------------- 5x7 点阵字模
FONT5x7 = {
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "M": ["10001", "11011", "10101", "10001", "10001", "10001", "10001"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    "/": ["00001", "00010", "00010", "00100", "00100", "01000", "10000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ">": ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
}

# ---------------------------------------------------------------- 像素猫头
def _cat_bitmap():
    """用几何图形拼猫脸，比手写点阵更可靠：三角耳 + 圆脸 + 方眼 + 小鼻。"""
    w, h = 17, 15
    img = Image.new("1", (w, h), 0)
    d = ImageDraw.Draw(img)
    d.polygon([(2, 7), (4, 1), (6, 7)], fill=1)
    d.polygon([(10, 7), (12, 1), (14, 7)], fill=1)
    d.ellipse([2, 5, 14, 13], fill=1)
    d.rectangle([5, 8, 6, 9], fill=0)
    d.rectangle([10, 8, 11, 9], fill=0)
    d.rectangle([8, 11, 8, 11], fill=0)
    bb = img.getbbox()
    img = img.crop(bb)
    return [["#" if img.getpixel((x, y)) else "." for x in range(img.width)]
            for y in range(img.height)]


CAT = _cat_bitmap()

# 颜文字式小图标
HEART = [
    ".##.##.",
    "#######",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
]
STAR = [
    "...#...",
    "...#...",
    ".#####.",
    "..###..",
    ".##.##.",
]


# ---------------------------------------------------------------- 工具函数
def _on(v):
    """点阵单元格是否点亮。字模用 '#'/'1'，PIL 提取用 0/1 整数。"""
    return v == 1 or v == "1" or v == "#"


def runs(bm, px, x0, y0, color):
    """把点阵合并成水平长条，减少 rect 数量。"""
    out = []
    for r, row in enumerate(bm):
        c, n = 0, len(row)
        while c < n:
            if _on(row[c]):
                s = c
                while c < n and _on(row[c]):
                    c += 1
                out.append((x0 + s * px, y0 + r * px, (c - s) * px, px, color))
            else:
                c += 1
    return out


def text_bitmap(text, target_h=24, render=72, th=100):
    """把一行中文渲染成点阵（整句渲染，保证笔画粗细一致）。"""
    f = ImageFont.truetype(FONT_PATH, render)
    img = Image.new("L", (render * len(text) + render, render * 2), 0)
    ImageDraw.Draw(img).text((render // 3, render // 3), text, font=f, fill=255)
    bb = img.getbbox()
    img = img.crop(bb)
    w, h = img.size
    nw = max(1, int(round(w * target_h / h)))
    img = img.resize((nw, target_h), Image.LANCZOS)
    return [[1 if img.getpixel((x, y)) > th else 0 for x in range(nw)] for y in range(target_h)]


def pixel_text(txt, px, x0, y0, color, tracking=2):
    """用 5x7 字模排一行英文，返回绝对坐标的 rects。不依赖任何字体。"""
    out, cx = [], x0
    for ch in txt.upper():
        bm = FONT5x7.get(ch)
        if bm is None:
            cx += 3 * px
            continue
        out += runs(bm, px, cx, y0, color)
        cx += (5 + tracking) * px
    return out


def pixel_text_width(txt, px, tracking=2):
    w, cx = 0, 0
    for ch in txt.upper():
        w = cx + (5 * px if ch in FONT5x7 else 3 * px)
        cx += (5 + tracking) * px if ch in FONT5x7 else 3 * px
    return w


def rects_to_svg(rects, extra=""):
    parts = []
    for x, y, w, h, color in rects:
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{color}"/>'
        )
    return "\n".join(parts) + extra


def rects_to_png(rects, w, h, bg, path):
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    for x, y, rw, rh, color in rects:
        try:
            d.rectangle([x, y, x + rw - 1, y + rh - 1], fill=color)
        except Exception:
            pass
    img.save(path)
    return path


# ================================================================ banner
def build_banner():
    W, H = 1200, 440
    rects = []

    # 背景与网格都交给底部单独绘制，base 只放星点


    # 星点
    rnd = random.Random(20261122)
    sp = _T["SPARK"]
    palette = [sp[0]] * 5 + [sp[1]] * 3 + [sp[2]] * 2 + [sp[3]]
    for _ in range(58):
        sx = rnd.randrange(0, W, 3)
        sy = rnd.randrange(0, H, 3)
        s = rnd.choice([2, 2, 2, 3])
        rects.append((sx, sy, s, s, rnd.choice(palette)))

    # 主标题 SZJMHXD
    title = "SZJMHXD"
    PX = 15
    cell_gap = 3 * PX
    tw = len(title) * 5 * PX + (len(title) - 1) * cell_gap
    tx = (W - tw) // 2
    ty = 92

    shadow, main = [], []
    cx = tx
    for ch in title:
        bm = FONT5x7[ch]
        shadow += runs(bm, PX, cx + 8, ty + 8, MAGENTA)
        main += runs(bm, PX, cx, ty, CYAN)
        cx += 5 * PX + cell_gap

    # 中文名
    zh = text_bitmap("十早九木", target_h=20, th=100)
    ZH_PX = 5
    zh_w = len(zh[0]) * ZH_PX
    zh_h = len(zh) * ZH_PX
    zx = (W - zh_w) // 2
    zy = 238
    zh_shadow = runs(zh, ZH_PX, zx + 5, zy + 5, ZH_SH)
    zh_main = runs(zh, ZH_PX, zx, zy, INK)

    # 中文名两侧的可爱元素
    ICON_PX = 6
    heart = runs(HEART, ICON_PX, zx - 7 * ICON_PX - 40, zy + 26, MAGENTA)
    star = runs(STAR, ICON_PX, zx + zh_w + 40, zy + 28, YELLOW)

    # 像素猫
    CAT_PX = 5
    cat_w = len(CAT[0]) * CAT_PX
    cat_h = len(CAT) * CAT_PX
    cat_x, cat_y = W - cat_w - 48, H - cat_h - 80
    cat = runs(CAT, CAT_PX, cat_x, cat_y, MAGENTA)

    return W, H, rects, shadow, main, zh_shadow, zh_main, cat + heart + star


def banner_svg():
    W, H, base, shadow, main, zh_shadow, zh_main, cat = build_banner()

    # 装饰文字全部用 5x7 点阵，不依赖访问者字体
    tag_l = pixel_text("SYS.ONLINE", 3, 72, 30, CYAN)
    tag_r = pixel_text("V2026.11", 3, W - 72 - pixel_text_width("V2026.11", 3), 30, DIM)
    foot_l = pixel_text("PYTHON // JAVA // PHP", 3, 48, 380, DIM)
    foot_r = pixel_text(
        "ASTRBOT.PLUGIN", 3, W - 72 - pixel_text_width("ASTRBOT.PLUGIN", 3), 380, CYAN_D
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
<title>十早九木 / SZJMHXD</title>
<desc>像素科幻风格的 GitHub 个人主页横幅：霓虹点阵文字、深空网格、HUD 装饰与像素猫。</desc>
<defs>
  <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">
    <path d="M48 0 V48 M0 48 H48" stroke="{GRID}" stroke-width="1" fill="none"/>
  </pattern>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="{CYAN}"/>
  </pattern>
  <radialGradient id="halo" cx="50%" cy="42%" r="55%">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="{_T['GLOW']}"/>
    <stop offset="55%" stop-color="{CYAN}" stop-opacity="0.03"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{BG}" stop-opacity="0.70"/>
    <stop offset="35%" stop-color="{BG}" stop-opacity="0"/>
    <stop offset="100%" stop-color="{BG}" stop-opacity="0.85"/>
  </linearGradient>
</defs>

<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
{rects_to_svg(base)}

<rect width="{W}" height="{H}" fill="url(#halo)"/>
<rect width="{W}" height="{H}" fill="url(#fade)"/>

{rects_to_svg(shadow)}
{rects_to_svg(main)}
{rects_to_svg(zh_shadow)}
{rects_to_svg(zh_main)}

<g>{rects_to_svg(cat)}</g>
{rects_to_svg(tag_l)}
{rects_to_svg(tag_r)}
{rects_to_svg(foot_l)}
{rects_to_svg(foot_r)}

<g stroke="{CYAN}" stroke-width="2" fill="none" opacity="0.85">
  <path d="M28 28 h34 M28 28 v34"/>
  <path d="M{W-28} 28 h-34 M{W-28} 28 v34"/>
  <path d="M28 {H-28} h34 M28 {H-28} v-34"/>
  <path d="M{W-28} {H-28} h-34 M{W-28} {H-28} v-34"/>
</g>

<rect width="{W}" height="{H}" fill="url(#scan)" opacity="{_T['SCAN']}"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="{CYAN}" stroke-width="1" opacity="0.35"/>
</svg>
'''
    (ASSETS / f"banner{SUFFIX}.svg").write_text(svg, encoding="utf-8")

    # 预览图（不含渐变与 HUD，用于核对点位、可读性、有无重叠）
    preview = base + shadow + main + zh_shadow + zh_main + cat + tag_l + tag_r + foot_l + foot_r
    rects_to_png(preview, W, H, BG, ASSETS / f"_preview_{THEME}.png")
    print(f"banner.svg  -> {len(preview)} rects")


# ================================================================ divider
def divider_svg(label):
    W, H = 1200, 44
    mid = H // 2
    lw = pixel_text_width(label, 2)
    label_px = rects_to_svg(pixel_text(label, 2, 600 - lw // 2, mid - 7, MAGENTA))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
<title>{label}</title>
<line x1="40" y1="{mid}" x2="470" y2="{mid}" stroke="{DASH}" stroke-width="2" stroke-dasharray="6 4"/>
<line x1="730" y1="{mid}" x2="1160" y2="{mid}" stroke="{DASH}" stroke-width="2" stroke-dasharray="6 4"/>
<rect x="500" y="{mid-9}" width="200" height="18" fill="none" stroke="{MAGENTA}" stroke-width="1" opacity="0.55"/>
<rect x="503" y="{mid-6}" width="194" height="12" fill="{MAGENTA}" opacity="0.10"/>
{label_px}
<rect x="478" y="{mid-3}" width="14" height="6" fill="{CYAN}"/>
<rect x="708" y="{mid-3}" width="14" height="6" fill="{CYAN}"/>
</svg>
'''
    return svg


# ================================================================ skills
def skills_svg(items):
    W, H = 1200, 132
    rects = []
    n = len(items)
    gap = 16
    bw = (W - 80 - gap * (n - 1)) // n
    bh = 58
    by = 30

    for i, name in enumerate(items):
        x = 40 + i * (bw + gap)
        rects.append((x, by, bw, bh, CARD))
        rects.append((x, by, bw, 2, CYAN))
        rects.append((x, by + bh - 2, bw, 2, MAGENTA))
        for cx_ in range(x + 4, x + bw - 4, 6):
            rects.append((cx_, by + 4, 3, 1, CARD_GRID))

    cells = []
    for i, name in enumerate(items):
        x = 40 + i * (bw + gap)
        bm_str = name.upper()
        PX = 3
        total = len(bm_str) * 5 * PX + (len(bm_str) - 1) * 2 * PX
        cx = x + (bw - total) // 2
        cy = by + (bh - 7 * PX) // 2
        for ch in bm_str:
            if ch in FONT5x7:
                cells += runs(FONT5x7[ch], PX, cx, cy, CYAN)
                cx += 5 * PX + 2 * PX

    fw = pixel_text_width("MAIN STACK", 2)
    foot_px = rects_to_svg(pixel_text("MAIN STACK", 2, 600 - fw // 2, H - 26, DIM))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
<title>技术栈</title>
{rects_to_svg(rects)}
{rects_to_svg(cells)}
{foot_px}
</svg>
'''
    return svg


if __name__ == "__main__":
    banner_svg()

    for name, label in [
        ("divider-stack.svg", "STACK"),
        ("divider-stats.svg", "DATA"),
        ("divider-work.svg", "WORK"),
    ]:
        (ASSETS / name.replace(".svg", f"{SUFFIX}.svg")).write_text(
            divider_svg(label), encoding="utf-8"
        )

    (ASSETS / f"skills{SUFFIX}.svg").write_text(
        skills_svg(["Python", "Java", "PHP", "AstrBot", "AHK", "SQLite"]), encoding="utf-8"
    )
    print("done ->", ASSETS)
