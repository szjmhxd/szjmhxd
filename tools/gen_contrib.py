"""生成贡献热力图（替代原生那张绿色方格）。

原生 contribution graph 是 GitHub 页面自带的，样式不可改（没有 API、没有 CSS 钩子）。
所以这里用 GraphQL 的 contributionsCollection 拉日历，自己画一张同数据的像素热力图：
  · 5 档强度用青→品红的色阶，和整页配色统一
  · 额外给出活跃天数 / 最长连续 / 峰值，这三点原生图没有
  · 数据随 GitHub Actions 每日重算，不会手写过期数字

用法：
    python tools/gen_contrib.py            # 用 gh auth token
    GITHUB_TOKEN=xxx python tools/gen_contrib.py
输出：assets/contrib.svg、assets/contrib-dark.svg
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_banner import (  # noqa: E402
    _PALETTES,
    pixel_text,
    pixel_text_width,
    rects_to_png,
)

USER = "szjmhxd"
ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1200, 286
CELL, GAP = 16, 3
PITCH = CELL + GAP
X0, Y0 = 98, 96

QUERY = """
query($login:String!) {
  user(login:$login) {
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

# 强度色阶：0 空 → 4 最热
LEVELS = {
    "light": ["#E7EDF8", "#C6E8E3", "#78CEC6", "#1FA79B", "#FB4D8D"],
    "dark": ["#171B2E", "#14433F", "#1B7C74", "#25B6A8", "#FF5FA2"],
}


def level_of(n):
    if n <= 0:
        return 0
    if n <= 2:
        return 1
    if n <= 5:
        return 2
    if n <= 9:
        return 3
    return 4


def token():
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok
    gh = shutil.which("gh")
    if gh:
        try:
            return subprocess.check_output([gh, "auth", "token"], text=True).strip()
        except Exception:
            pass
    return None


def fetch():
    tok = token()
    if not tok:
        raise RuntimeError("没有可用的 GitHub token")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={
            "Authorization": f"bearer {tok}",
            "Content-Type": "application/json",
            "User-Agent": "profile-contrib-generator",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]["contributionsCollection"]


def stats(days):
    total = sum(d["contributionCount"] for d in days)
    active = sum(1 for d in days if d["contributionCount"] > 0)
    peak = max(days, key=lambda d: d["contributionCount"])
    best = cur = 0
    for d in days:  # days 已按时间升序
        cur = cur + 1 if d["contributionCount"] > 0 else 0
        best = max(best, cur)
    return total, active, best, peak


def seg_width(segs, px, gap=0):
    return sum(pixel_text_width(t, px) for t, _ in segs) + gap * (len(segs) - 1)


def seg(segs, px, x, y, gap=0):
    out, cx = [], x
    for txt, color in segs:
        out += pixel_text(txt, px, cx, y, color)
        cx += pixel_text_width(txt, px) + gap
    return out


def build(theme, cal):
    t = _PALETTES[theme]
    BG, CYAN, MAGENTA = t["BG"], t["CYAN"], t["MAGENTA"]
    DIM, CARD, CARD_GRID = t["DIM"], t["CARD"], t["CARD_GRID"]
    pal = LEVELS[theme]

    weeks = cal["weeks"]
    days = [d for wk in weeks for d in wk["contributionDays"]]
    total, active, best, peak = stats(days)

    r = []
    # 底板：与 stats 卡片同一套边框语言
    r.append((0, 0, W, H, CARD))
    r.append((0, 0, W, 2, CYAN))
    r.append((0, H - 2, W, 2, MAGENTA))
    for x in range(4, W - 4, 7):
        r.append((x, 4, 3, 1, CARD_GRID))

    # 标题 + 总数
    r += pixel_text("YEAR IN PIXELS", 3, 40, 28, CYAN)
    r += seg(
        [("TOTAL ", DIM), (str(total), MAGENTA)],
        3,
        W - 40 - seg_width([("TOTAL ", DIM), (str(total), MAGENTA)], 3),
        28,
    )

    # 月份标签：某周的第一天进入新月份时打一个；两条之间至少隔 3 周，避免贴字
    prev, last = None, -9
    for i, wk in enumerate(weeks):
        d0 = wk["contributionDays"][0]["date"]
        m = int(d0[5:7])
        if m != prev:
            prev = m
            if i - last >= 3 and i <= len(weeks) - 3:
                r += pixel_text(MONTHS[m - 1], 2, X0 + i * PITCH, 72, DIM)
                last = i

    # 星期标签
    for row, label in ((1, "MON"), (3, "WED"), (5, "FRI")):
        w = pixel_text_width(label, 2)
        r += pixel_text(label, 2, X0 - 10 - w, Y0 + row * PITCH + 1, DIM)

    # 方格
    for i, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            lv = level_of(d["contributionCount"])
            r.append(
                (X0 + i * PITCH, Y0 + d["weekday"] * PITCH, CELL, CELL, pal[lv])
            )

    # 底部：数据摘要（原生图没有这组信息）
    y = 246
    r += seg(
        [
            ("ACTIVE ", DIM), (f"{active}D", CYAN),
            ("  STREAK ", DIM), (f"{best}D", MAGENTA),
            ("  PEAK ", DIM), (f"{peak['contributionCount']}/D", CYAN),
        ],
        2,
        40,
        y,
    )

    # 图例
    right = X0 + len(weeks) * PITCH - GAP
    lw_less = pixel_text_width("LESS", 2)
    lw_more = pixel_text_width("MORE", 2)
    total_lg = lw_less + 12 + 5 * PITCH - GAP + 12 + lw_more
    lx = right - total_lg
    r += pixel_text("LESS", 2, lx, y, DIM)
    bx = lx + lw_less + 12
    for k in range(5):
        r.append((bx + k * PITCH, y - 1, CELL, CELL, pal[k]))
    r += pixel_text("MORE", 2, bx + 5 * PITCH - GAP + 12, y, DIM)

    body = "\n".join(
        f'<rect x="{x}" y="{y:.1f}" width="{w}" height="{h}" fill="{c}"/>'
        for x, y, w, h, c in r
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
<title>{USER} 近一年的提交热力图</title>
<desc>过去 12 个月每日提交次数：共 {total} 次，活跃 {active} 天，最长连续 {best} 天，单日峰值 {peak['contributionCount']} 次。</desc>
<rect width="{W}" height="{H}" fill="{BG}"/>
{body}
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="{CYAN}" stroke-width="1" opacity="0.30"/>
</svg>
'''
    suffix = "" if theme == "light" else "-dark"
    (ASSETS / f"contrib{suffix}.svg").write_text(svg, encoding="utf-8")
    if theme == "light":
        rects_to_png([(0, 0, W, H, BG)] + r, W, H, BG, ROOT / "_contrib.png")
    print(f"contrib{suffix}.svg  total={total} active={active} streak={best} peak={peak['contributionCount']}")


def main():
    try:
        cal = fetch()["contributionCalendar"]
    except (urllib.error.URLError, RuntimeError, KeyError) as e:
        print(f"拉取失败，保留旧图：{e}", file=sys.stderr)
        return
    for theme in ("light", "dark"):
        build(theme, cal)


if __name__ == "__main__":
    main()
