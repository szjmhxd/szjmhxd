"""生成像素风 GitHub 统计卡片。

数据来源：GitHub REST API（公开数据，无需 token）
输出：assets/stats.svg、assets/stats-dark.svg

为什么不直接用 github-readme-stats：
  1. 它的 SVG 用 `opacity:0` + CSS 动画做淡入，作为 <img> 加载时动画若未执行，
     整块内容永久透明 —— 表现为卡片只剩一个背景方块。
  2. 语言统计按代码字节算，被博客类仓库的 HTML 冲垮，会显示成 HTML 76%、
     与实际的 Python 主力严重不符。本脚本按「仓库主语言出现的次数」统计，更贴近实际。

用法：
    python tools/gen_stats.py
"""
import json
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_banner import (  # noqa: E402
    _PALETTES,
    FONT5x7,
    pixel_text,
    pixel_text_width,
    runs,  # noqa: F401
)

USER = "szjmhxd"
ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"

W, H = 1200, 300


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "profile-stats-generator",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def collect():
    user = fetch(f"https://api.github.com/users/{USER}")
    repos = fetch(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated")

    langs = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        name = repo.get("language")
        if name:
            langs[name] = langs.get(name, 0) + 1

    return {
        "repos": user["public_repos"],
        "stars": sum(r.get("stargazers_count", 0) for r in repos),
        "followers": user["followers"],
        "following": user["following"],
        "langs": sorted(langs.items(), key=lambda kv: -kv[1])[:3],
    }


def big_number(txt, cx, top, color, px=7):
    """居中放大数字。"""
    return pixel_text(txt, px, cx - pixel_text_width(txt, px) // 2, top, color)


def centered_label(txt, cx, top, color, px=2):
    return pixel_text(txt, px, cx - pixel_text_width(txt, px) // 2, top, color)


def build(theme):
    t = _PALETTES[theme]
    BG, CYAN, MAGENTA, YELLOW = t["BG"], t["CYAN"], t["MAGENTA"], t["YELLOW"]
    INK, DIM, DASH = t["INK"], t["DIM"], t["DASH"]
    CARD, CARD_GRID = t["CARD"], t["CARD_GRID"]

    d = collect()
    rects = []

    # 底板
    rects.append((0, 0, W, H, CARD))
    rects.append((0, 0, W, 2, CYAN))
    rects.append((0, H - 2, W, 2, MAGENTA))
    for x in range(4, W - 4, 7):
        rects.append((x, 4, 3, 1, CARD_GRID))

    # 上排四个指标
    metrics = [
        ("REPOS", str(d["repos"]), CYAN),
        ("STARS", str(d["stars"]), MAGENTA),
        ("FOLLOWERS", str(d["followers"]), YELLOW),
        ("FOLLOWING", str(d["following"]), CYAN),
    ]
    for i, (label, val, color) in enumerate(metrics):
        cx = 150 + i * 300
        rects += big_number(val, cx, 46, color)
        rects += centered_label(label, cx, 108, DIM)

    # 分隔
    for x in range(40, 1160, 12):
        rects.append((x, 148, 7, 2, DASH))

    # 语言条
    total = sum(v for _, v in d["langs"]) or 1
    bar_x, bar_w = 300, 620
    palette = [CYAN, MAGENTA, YELLOW]
    for i, (name, cnt) in enumerate(d["langs"]):
        y = 178 + i * 36
        rects += pixel_text(name, 2, 56, y + 3, INK)
        # 轨道
        rects.append((bar_x, y, bar_w, 14, CARD_GRID))
        # 像素块填充
        cells = max(1, int(bar_w * cnt / total / 10))
        for c in range(cells):
            rects.append((bar_x + c * 10, y, 8, 14, palette[i % 3]))
        # 数量
        num = str(cnt)
        rects += pixel_text(num, 2, 1010 - pixel_text_width(num, 2), y + 3, DIM)

    body = "\n".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>'
        for x, y, w, h, c in rects
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
<title>{USER} 的 GitHub 统计</title>
<desc>仓库数、Star 数、关注者数，以及按仓库主语言统计的分布。</desc>
{body}
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="{CYAN}" stroke-width="1" opacity="0.30"/>
</svg>
'''
    out = ASSETS / ("stats.svg" if theme == "light" else "stats-dark.svg")
    out.write_text(svg, encoding="utf-8")
    print(f"{out.name}  repos={d['repos']} stars={d['stars']} langs={d['langs']}")


if __name__ == "__main__":
    build("light")
    build("dark")
