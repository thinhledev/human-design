#!/usr/bin/env python3
"""Check colour pairs for contrast: WCAG 2 ratio (the legal and audit standard)
and APCA Lc (a perceptual estimate, useful for dark mode and thin text).

Usage:
  python3 contrast_check.py "#5b6470" "#ffffff"
  python3 contrast_check.py "oklch(0.55 0.02 250)" "#fff" --size 14 --weight 400
  python3 contrast_check.py --pairs "text:bg" "muted:surface" --css tokens.css
  python3 contrast_check.py --css tokens.css            # every text-like token on every ground-like token
  python3 contrast_check.py "#777" "#fff" --fix         # nearest lightness that passes, hue and chroma kept

WCAG 2.2 AA: 4.5:1 for text, 3:1 for large text (24px, or 18.66px bold) and for
the boundaries of controls and meaningful graphics. AAA: 7:1 and 4.5:1.
APCA is not part of any adopted standard; treat Lc 75 as comfortable for body
text, 60 for larger text and 45 for large headings, as a second opinion only.

With --css, custom properties are read from :root and from dark-mode blocks,
and each mode is checked separately. Standard library only.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design_lib import apca, blend, fit_oklch, md_table, parse_color, srgb_to_oklch, to_hex, wcag_contrast  # noqa: E402

TEXT_LIKE = re.compile(r"(text|fg|foreground|ink|accent-text|muted|subtle|link|good|warn|bad|info|danger|success|error|second-text)(?!.*(tint|bg))", re.I)
GROUND_LIKE = re.compile(r"(^|-)(bg|background|surface|ground|paper|canvas|sunken|card|panel|tint)($|-)", re.I)


def read_vars(path):
    """Return {mode: {name: value}} for custom properties; mode is light or dark."""
    text = re.sub(r"/\*.*?\*/", "", open(path, encoding="utf-8").read(), flags=re.S)
    modes = {"light": {}, "dark": {}}
    depth, ctx, buf = 0, [], ""
    for ch in text:
        if ch == "{":
            ctx.append(buf.strip())
            buf = ""
            depth += 1
        elif ch == "}":
            block = " ".join(ctx)
            dark = "dark" in block and ("prefers-color-scheme" in block or "data-theme" in block or ".dark" in block)
            for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);?", buf):
                modes["dark" if dark else "light"][m.group(1)[2:]] = m.group(2).strip()
            buf = ""
            ctx.pop() if ctx else None
            depth -= 1
        else:
            buf += ch
    if not modes["dark"]:
        del modes["dark"]
    else:
        modes["dark"] = dict(modes["light"], **modes["dark"])
    return modes


def resolve(value, table, depth=0):
    m = re.fullmatch(r"var\(\s*--([\w-]+)\s*(?:,\s*([^)]+))?\)", value.strip())
    if m and depth < 6:
        return resolve(table.get(m.group(1), m.group(2) or ""), table, depth + 1)
    return value


def verdict(ratio, size, weight):
    large = size >= 24 or (size >= 18.66 and weight >= 700)
    need = 3.0 if large else 4.5
    if ratio >= (4.5 if large else 7.0):
        return "AAA", need
    if ratio >= need:
        return "AA", need
    if ratio >= 3.0:
        return "controls only", need
    return "FAIL", need


def fix(fg, bg, need):
    L, c, h = srgb_to_oklch(*fg[:3])
    bg_l = srgb_to_oklch(*bg[:3])[0]
    step = -0.005 if bg_l > 0.5 else 0.005
    for _ in range(200):
        rgb, _c, _clip = fit_oklch(L, c, h)
        if wcag_contrast(rgb, bg) >= need:
            return to_hex(rgb)
        L += step
        if not 0 <= L <= 1:
            break
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("colors", nargs="*", help="foreground and background")
    ap.add_argument("--css", help="CSS file with custom properties")
    ap.add_argument("--pairs", nargs="+", metavar="FG:BG", help="token names (without --) to check as pairs")
    ap.add_argument("--size", type=float, default=16.0, help="text size in px (default 16)")
    ap.add_argument("--weight", type=int, default=400)
    ap.add_argument("--fix", action="store_true", help="suggest the nearest passing foreground")
    a = ap.parse_args(argv)
    rows, failed = [], 0

    def add(label, fg_raw, bg_raw, non_text=False):
        nonlocal failed
        fg, bg = parse_color(fg_raw), parse_color(bg_raw)
        if not fg or not bg:
            rows.append([label, fg_raw, bg_raw, "-", "-", "not a plain colour", ""])
            return
        bg3 = blend(bg, (1, 1, 1))
        fg3 = blend(fg, bg3)
        ratio = wcag_contrast(fg3, bg3)
        v, need = verdict(ratio, a.size, a.weight)
        if non_text:  # placeholders, disabled text, borders and focus rings need 3:1
            v, need = ("ok for non-text (3:1)" if ratio >= 3 else "FAIL"), 3.0
        failed += v in ("FAIL", "controls only")
        hint = ""
        if a.fix and v in ("FAIL", "controls only"):
            hint = fix(fg3, bg3, need) or "no passing lightness"
        rows.append([label, to_hex(fg3), to_hex(bg3), f"{ratio:.2f}", f"{apca(fg3, bg3):.0f}", v, hint])

    if a.css:
        modes = read_vars(a.css)
        for mode, table in modes.items():
            if a.pairs:
                pairs = [p.split(":", 1) for p in a.pairs]
            else:
                texts = [k for k in table if TEXT_LIKE.search(k) and parse_color(resolve(table[k], table))]
                grounds = [k for k in table if GROUND_LIKE.search(k) and parse_color(resolve(table[k], table))
                           and not re.search(r"-\d{2,3}$", k)]
                pairs = [(t, g) for t in texts for g in grounds if not re.search(r"-\d{2,3}$", t)
                         and not (("tint" in g) and not g.startswith(t.split("-")[0]) and t.split("-")[0] in ("good", "warn", "bad", "info"))]
            for fg, bg in pairs:
                if fg not in table or bg not in table:
                    rows.append([f"{mode}: {fg} on {bg}", "?", "?", "-", "-", "token not found", ""])
                    continue
                add(f"{mode}: {fg} on {bg}", resolve(table[fg], table), resolve(table[bg], table),
                    non_text=bool(re.search(r"subtle|placeholder|disabled|border|focus|ring|line", fg)))
    elif len(a.colors) == 2:
        add("pair", a.colors[0], a.colors[1])
    else:
        ap.error("give two colours, or --css FILE")
    print(md_table(["pair", "foreground", "background", "WCAG", "APCA Lc", f"at {a.size:g}px/{a.weight}", "passing foreground" if a.fix else ""], rows))
    print(f"\n{failed} pair(s) below their minimum." if failed else "\nAll pairs pass (4.5:1 for text at this size; 3:1 for subtle, "
          "border and focus tokens, which are not body text).")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
