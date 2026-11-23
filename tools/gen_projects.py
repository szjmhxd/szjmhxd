"""生成「精选项目」用的像素名签（nameplate）。

为什么不用原生 Markdown 表格样式：
  GitHub 会丢掉所有 `style` 属性，表格只能吃默认灰色描边，
  与页面其它自绘素材完全不搭。这里把「项目名」这一列换成自绘名签，
  表格结构保留 —— 链接、说明文字仍然是可选中、可索引的真文本。

宽度按最长仓库名反推：单行 300px 会把「说明」挤到只剩 200px，
所以超过 18 字符的名字在最近的 `_` 处折成两行，卡片统一 300×56。

用法：python tools/gen_projects.py
输出：assets/proj/<slug>{,-dark}.svg
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_banner import (  # noqa: E402
    _PALETTES,
    FONT5x7,
    pixel_text,
    pixel_text_width,
    rects_to_png,
    runs,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "proj"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 300, 56
PX = 2          # 单格 2px → 字高 14px
TRACK = 2       # 字距（格）
LH = 7 * PX     # 行高
LINE_GAP = 10

# slug, 仓库名, 分类色键（决定左侧色条）
PROJECTS = [
    ("lolmatch", "astrbot_plugin_lolmatch", "MAGENTA"),
    ("bili-card", "astrbot_plugin_bili_card", "MAGENTA"),
    ("steamhub", "astrbot_plugin_steamhub", "MAGENTA"),
    ("nas-log", "nas-log-analyzer", "CYAN"),
    ("symlink", "symlink-explorer", "CYAN"),
    ("ahk", "ahk-scripts", "YELLOW"),
]


def split_name(name, limit=18):
    """超过 limit 就在离中点最近的 `_` 处断开，保证两行都不越界。"""
    if len(name) <= limit:
        return [name]
    cand = [i for i, c in enumerate(name) if c == "_"] or [len(name) // 2]
    cut = min(cand, key=lambda i: abs(i - len(name) / 2))
    return [name[:cut], name[cut + 1:]]


def plate(theme, name, accent_key):
    t = _PALETTES[theme]
    ACCENT = t[accent_key]
    CARD, CARD_GRID = t["CARD"], t["CARD_GRID"]
    INK = t["INK"]

    r = []
    # 底板 + 细描边（全用 rect，避免 stroke 在不同渲染器上的 1px 偏移）
    r.append((0, 0, W, H, CARD))
    r.append((0, 0, W, 1, CARD_GRID))
    r.append((0, H - 1, W, 1, CARD_GRID))
    r.append((W - 1, 0, 1, H, CARD_GRID))
    # 左侧分类色条
    r.append((0, 0, 4, H, ACCENT))
    # 顶部点缀
    for x in range(8, W - 12, 7):
        r.append((x, 3, 4, 1, CARD_GRID))

    lines = split_name(name)
    block = len(lines) * LH + (len(lines) - 1) * LINE_GAP
    y = (H - block) // 2

    # 终端提示符跟着第一行
    r += runs(FONT5x7[">"], PX, 14, y, ACCENT)
    nx = 14 + (5 + TRACK) * PX + 6

    for i, ln in enumerate(lines):
        r += pixel_text(ln, PX, nx, y + i * (LH + LINE_GAP), INK)

    # 右端三条刻度
    for i in range(3):
        r.append((W - 24 + i * 6, H // 2 - 6, 3, 12, ACCENT if i == 2 else CARD_GRID))

    return r


def svg_for(rects, name):
    body = "\n".join(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{c}"/>'
        for x, y, w, h, c in rects
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
<title>{name}</title>
{body}
</svg>
'''


def main():
    for slug, name, key in PROJECTS:
        lines = split_name(name)
        widest = max(pixel_text_width(x, PX) for x in lines)
        assert 14 + (5 + TRACK) * PX + 6 + widest <= W - 30, f"{name} 超宽"
        for theme in ("light", "dark"):
            rects = plate(theme, name, key)
            suffix = "" if theme == "light" else "-dark"
            (OUT / f"{slug}{suffix}.svg").write_text(svg_for(rects, name), encoding="utf-8")
            if theme == "light":
                rects_to_png(rects, W, H, _PALETTES["light"]["BG"], ROOT / f"_plate_{slug}.png")
        print("ok", slug, lines, widest)


if __name__ == "__main__":
    main()
