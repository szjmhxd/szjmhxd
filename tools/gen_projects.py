"""生成「精选项目」用的像素名签（nameplate）。

为什么不用原生 Markdown 表格样式：
  GitHub 会丢掉所有 `style` 属性，表格只能吃默认灰色描边，
  与页面其它自绘素材完全不搭。这里把「项目名」这一列换成自绘名签，
  表格结构保留 —— 链接、说明文字仍然是可选中、可索引的真文本。

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

W, H = 400, 46
NAME_PX = 2

# slug, 仓库名, 分类色键（决定左侧色条）
PROJECTS = [
    ("lolmatch", "astrbot_plugin_lolmatch", "MAGENTA"),
    ("bili-card", "astrbot_plugin_bili_card", "MAGENTA"),
    ("steamhub", "astrbot_plugin_steamhub", "MAGENTA"),
    ("nas-log", "nas-log-analyzer", "CYAN"),
    ("symlink", "symlink-explorer", "CYAN"),
    ("ahk", "ahk-scripts", "YELLOW"),
]


def plate(theme, name, accent_key):
    t = _PALETTES[theme]
    ACCENT = t[accent_key]
    CARD, CARD_GRID = t["CARD"], t["CARD_GRID"]
    INK, DIM = t["INK"], t["DIM"]
    CYAN = t["CYAN"]

    r = []
    # 底板 + 细描边（全用 rect，避免 stroke 在不同渲染器上的 1px 偏移）
    r.append((0, 0, W, H, CARD))
    r.append((0, 0, W, 1, CARD_GRID))
    r.append((0, H - 1, W, 1, CARD_GRID))
    r.append((W - 1, 0, 1, H, CARD_GRID))
    # 左侧分类色条
    r.append((0, 0, 4, H, ACCENT))
    # 顶部 12 格提示条
    for x in range(4, W - 12, 7):
        r.append((x, 3, 4, 1, CARD_GRID))

    # 终端提示符
    r += runs(FONT5x7[">"], NAME_PX, 16, (H - 7 * NAME_PX) // 2, ACCENT)

    # 仓库名
    nx = 16 + (5 + 2) * NAME_PX + 6
    r += pixel_text(name, NAME_PX, nx, (H - 7 * NAME_PX) // 2, INK)

    # 右端三条刻度
    for i in range(3):
        r.append((W - 22 + i * 6, H // 2 - 6, 3, 12, ACCENT if i == 2 else CARD_GRID))

    return r


def svg_for(theme, rects, name):
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
        for theme in ("light", "dark"):
            rects = plate(theme, name, key)
            suffix = "" if theme == "light" else "-dark"
            (OUT / f"{slug}{suffix}.svg").write_text(
                svg_for(theme, rects, name), encoding="utf-8"
            )
            if theme == "light":
                rects_to_png(rects, W, H, _PALETTES["light"]["BG"], ROOT / f"_plate_{slug}.png")
        print("ok", slug, name, pixel_text_width(name, NAME_PX))


if __name__ == "__main__":
    main()
