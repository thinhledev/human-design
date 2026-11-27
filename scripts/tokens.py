#!/usr/bin/env python3
"""Turn a project's design identity (design.json) into tokens: colour ramps in
OKLCH fitted to sRGB, role colours for light and dark with contrast checked, a
type scale with line heights and tracking, spacing, radii, shadows and motion.

Usage:
  python3 tokens.py design.json                         # report: ramps, roles, contrast
  python3 tokens.py design.json --css tokens.css        # CSS custom properties
  python3 tokens.py design.json --tailwind theme.css    # Tailwind v4 @theme block
  python3 tokens.py design.json --json tokens.json      # design-tokens JSON
  python3 tokens.py design.json --swift Tokens.swift --kotlin Tokens.kt
  python3 tokens.py --init design.json                  # write a commented starter file

Colour comes from color.palette, a set of roles (ground, surface, ink, primary,
secondary, highlight) usually adapted from a combination that palette.py
ranked for the brief. The report names the palette's harmony and exits with
status 2 when a text pair fails contrast, when only one colour carries any hue
(a timid palette) or when two strong colours compete, unless design.json lists
the last two under "deliberate" with a reason. The older neutral and accent
keys still work.

The identity file states decisions; this script only does the arithmetic. It
never chooses a typeface, a hue or a ratio for you: those come from the brief
(references/identity.md). Missing keys fail with a message instead of falling
back to a default look.

Standard library only. No network access.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design_lib import (apca, chroma_profile, classify_harmony, competing_pairs, fit_oklch, hue_diff, is_chromatic,  # noqa: E402
                        md_table, oklab_distance, parse_color, simulate_cvd, srgb_to_oklch, to_hex, wcag_contrast)

ROOT_PX = 16  # rem is relative to the root font size; the tokens never change it, so every rem value divides by 16

STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
LIGHT = [0.975, 0.945, 0.895, 0.825, 0.735, 0.64, 0.55, 0.465, 0.385, 0.30, 0.22]
CURVE = [0.18, 0.32, 0.55, 0.78, 0.95, 1.0, 0.97, 0.88, 0.76, 0.62, 0.48]

STARTER = {
    "_readme": "Every value here is a decision from the brief. Replace all of them; see references/identity.md.",
    "_options": {
        "color.palette": "roles in OKLCH {hue, chroma, lightness}: ground (required; lightness_dark and chroma_dark for the dark ground), primary (required: actions, current item, links), ink, secondary and highlight (optional, each with a job), surface (optional: a coloured card or panel). Start from python3 scripts/palette.py --apply ID design.json",
        "color.palette.*.lightness_dark": "lightness of that role in dark mode (default: lighter than in light mode)",
        "color.chart": "number of categorical chart colours to derive from the palette (default 6, 0 for none), or a list of hues",
        "color.semantic_chroma": "chroma of good, warn, bad and info (default: follows the primary, between 0.09 and 0.17)",
        "older keys": "color.neutral {hue, chroma, bg_lightness}, color.accent, color.second and color.ink still work when there is no palette",
        "color.modes": "[\"light\"], [\"dark\"] or both; list the primary one first",
        "chroma": "values above what sRGB can show are reduced automatically, so a strong yellow or lime may be set high",
        "shadow": "none, hairline, soft or hard",
        "deliberate": "tell ids from slop_check.py that are real decisions, each with a reason that names the subject",
        "color.focus": "\"ink\" to draw focus rings in the text colour, when the accent is not the action colour",
        "color.semantic": "hues for good, warn, bad, info; move warn away from the accent if they are close (a yellow accent and an amber warning)",
        "color.extra": "optional named colours beyond the roles, such as materials: {\"card-buff\": \"#e8d9b5\", \"pin\": {\"hue\": 25, \"chroma\": 0.15, \"lightness\": 0.55}}; a value may also be {\"light\": ..., \"dark\": ...}. Each becomes --NAME",
        "type.extra": "optional extra font roles beyond display, text and mono: {\"hand\": {\"family\": \"...\", \"fallback\": \"cursive\", \"source\": \"...\"}} or {\"hand\": \"Family\"}. Each becomes --font-ROLE",
        "type.base": "body text size in px; it should be one of the sizes. rem values are always relative to the 16px root, so a base of 18 does not rescale anything",
    },
    "signature": "The one deliberate, memorable choice and why it belongs to this subject.",
    "refusals": ["Three things this design will not use, each with its reason."],
    "deliberate": {},
    "name": "PROJECT NAME",
    "subject": "One sentence: what this is, for whom, and the one job of the product.",
    "type": {
        "display": {"family": "REPLACE", "fallback": "Georgia, serif", "source": "where the font comes from and its licence"},
        "text": {"family": "REPLACE", "fallback": "system-ui, sans-serif", "source": ""},
        "mono": {"family": "REPLACE", "fallback": "ui-monospace, monospace", "source": ""},
        "sizes": [12, 14, 16, 18, 22, 28, 36, 48],
        "base": 16,
        "leading": {"text": 1.5, "display": 1.1},
        "measure": 66,
        "fluid_from": 36,
    },
    "color": {
        "palette": {
            "harmony": "REPLACE: the relation you chose (palette.py --show ID names it)",
            "source": "REPLACE: the combination it started from and what in the subject moved it",
            "ground": {"hue": 0, "chroma": 0.0, "lightness": 0.985, "lightness_dark": 0.2},
            "ink": {"hue": 0, "chroma": 0.0, "lightness": 0.21},
            "primary": {"hue": 0, "chroma": 0.0, "lightness": 0.55},
            "secondary": {"hue": 0, "chroma": 0.0, "lightness": 0.6},
            "highlight": {"hue": 0, "chroma": 0.0, "lightness": 0.85},
        },
        "semantic": {"good": 150, "warn": 75, "bad": 27, "info": 240},
        "chart": 6,
        "modes": ["light", "dark"],
    },
    "space": {"base": 4, "steps": [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]},
    "radius": {"sm": 2, "md": 6, "lg": 12},
    "shadow": "hairline",
    "motion": {"press": 80, "fast": 150, "base": 200, "slow": 320, "ease": "cubic-bezier(.2,.8,.2,1)"},
}


def need(d, path):
    cur = d
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            sys.exit(f"design.json: missing '{path}'. The identity must state it; see references/identity.md.")
        cur = cur[key]
    if cur == "REPLACE" or cur == "PROJECT NAME":
        sys.exit(f"design.json: '{path}' still has the starter placeholder.")
    return cur


PALETTE_ROLES = ("ground", "surface", "ink", "primary", "secondary", "highlight")
SEMANTIC_RANGE = {"good": (125, 165), "warn": (55, 95), "bad": (15, 40), "info": (205, 265)}


def normalise(spec):
    """Map color.palette (roles) onto the neutral, accent, second, ink, highlight and surface keys that roles() reads."""
    c = spec.setdefault("color", {})
    p = c.get("palette")
    if not p:
        return spec
    for key in p:
        if key not in PALETTE_ROLES + ("harmony", "source", "note"):
            sys.exit(f"design.json: color.palette.{key} is not a role. Roles: {', '.join(PALETTE_ROLES)}.")
    for role in ("ground", "primary"):
        if role not in p:
            sys.exit(f"design.json: color.palette needs '{role}'.")
    for role in PALETTE_ROLES:
        if role in p:
            for k in ("hue", "chroma", "lightness") if role != "ground" else ("hue", "chroma"):
                if k not in p[role]:
                    sys.exit(f"design.json: color.palette.{role} needs {k}.")
    g = p["ground"]
    c["neutral"] = {"hue": g["hue"], "chroma": g.get("neutral_chroma", min(max(g["chroma"] * 1.5, 0.004), 0.04)),
                    "bg_lightness": g.get("lightness", 0.985), "bg_lightness_dark": g.get("lightness_dark", 0.2), "bg_chroma": g["chroma"]}
    if "chroma_dark" in g:
        c["neutral"]["bg_chroma_dark"] = g["chroma_dark"]
    c["accent"] = dict(p["primary"])
    for role, key in (("secondary", "second"), ("ink", "ink"), ("highlight", "highlight"), ("surface", "surface_colour")):
        if role in p:
            c[key] = dict(p[role])
    return spec


def ramp(hue, chroma):
    out = {}
    for step, L, k in zip(STEPS, LIGHT, CURVE):
        rgb, c, clipped = fit_oklch(L, chroma * k, hue)
        out[step] = {"hex": to_hex(rgb), "rgb": rgb, "L": L, "C": round(c, 4), "H": hue, "clipped": clipped}
    return out


def pick(L, c, h):
    rgb, cc, _ = fit_oklch(L, c, h)
    return {"hex": to_hex(rgb), "rgb": rgb, "L": round(L, 3), "C": round(cc, 4), "H": h}


def ensure(fg, bg, target, hue, chroma, darker=True):
    """Move the lightness of fg until it reaches the target contrast on bg."""
    L = fg["L"]
    target += 0.08  # margin for rounding to 8-bit hex
    for _ in range(60):
        if wcag_contrast(fg["rgb"], bg["rgb"]) >= target:
            break
        L = L - 0.01 if darker else L + 0.01
        if not 0.02 < L < 0.99:
            break
        fg = pick(L, chroma, hue)
    return fg


def roles(spec, mode):
    n, a = spec["color"]["neutral"], spec["color"]["accent"]
    nh, nc = n["hue"], n["chroma"]
    ah, ac, aL = a["hue"], a["chroma"], a["lightness"]
    sem = spec["color"].get("semantic", {})
    ink = spec["color"].get("ink") or {"hue": nh, "chroma": min(0.03, nc * 1.5)}
    second = spec["color"].get("second")
    hl = spec["color"].get("highlight")
    sem = semantic_hues(sem, a)
    sc_sem = spec["color"].get("semantic_chroma", min(0.17, max(0.09, ac)))
    r = {}
    if mode == "light":
        r["bg"] = pick(n.get("bg_lightness", 0.985), n.get("bg_chroma", nc * 0.5), nh)
        sc = spec["color"].get("surface_colour")
        r["surface"] = pick(sc["lightness"], sc["chroma"], sc["hue"]) if sc else pick(min(0.999, r["bg"]["L"] + 0.012), r["bg"]["C"] * 0.8, nh)
        r["sunken"] = pick(r["bg"]["L"] - 0.03, max(nc * 0.7, r["bg"]["C"]), nh)
        r["border"] = pick(r["bg"]["L"] - 0.09, nc, nh)
        r["border-strong"] = ensure(pick(r["bg"]["L"] - 0.36, nc, nh), r["bg"], 3.0, nh, nc, darker=True)
        r["text"] = pick(ink.get("lightness", 0.21), ink["chroma"], ink["hue"])
        low = min((r["sunken"], r["surface"]), key=lambda x: x["L"])  # the darkest light surface: text must hold on it too
        r["text"] = ensure(r["text"], low, 7.0, ink["hue"], ink["chroma"], darker=True)
        r["text-muted"] = ensure(pick(0.48, nc * 1.2, nh), low, 4.5, nh, nc * 1.2, darker=True)
        r["text-subtle"] = ensure(pick(0.6, nc, nh), low, 3.0, nh, nc, darker=True)
        r["accent"] = pick(aL, ac, ah)
        r["accent-hover"] = pick(max(0.1, aL - 0.06), ac, ah)
        r["accent-tint"] = pick(0.95, ac * 0.25, ah)
        r["accent-text"] = ensure(pick(min(aL, 0.5), ac, ah), low, 4.5, ah, ac, darker=True)
        if second:
            r["second"] = pick(second.get("lightness", 0.6), second["chroma"], second["hue"])
            r["second-text"] = ensure(pick(min(second.get("lightness", 0.6), 0.5), second["chroma"], second["hue"]), low, 4.5,
                                      second["hue"], second["chroma"], darker=True)
        if hl:
            r["highlight"] = pick(hl["lightness"], hl["chroma"], hl["hue"])
            r["highlight-text"] = ensure(pick(min(hl["lightness"], 0.5), hl["chroma"], hl["hue"]), low, 4.5, hl["hue"], hl["chroma"], darker=True)
        for name, hue in sem.items():
            r[name] = ensure(pick(0.52, sc_sem, hue), low, 4.5, hue, sc_sem, darker=True)
            r[name + "-tint"] = pick(0.95, min(0.04, sc_sem * 0.3), hue)
    else:
        r["bg"] = pick(n.get("bg_lightness_dark", 0.2), n.get("bg_chroma_dark", min(nc, 0.02)), nh)
        sc = spec["color"].get("surface_colour")
        r["surface"] = pick(sc["lightness_dark"], sc["chroma"] * 0.6, sc["hue"]) if sc and "lightness_dark" in sc else \
            pick(r["bg"]["L"] + 0.035, max(r["bg"]["C"], min(nc, 0.022)), nh)
        r["sunken"] = pick(max(0.08, r["bg"]["L"] - 0.03), min(nc, 0.018), nh)
        r["border"] = pick(r["bg"]["L"] + 0.11, min(nc, 0.025), nh)
        r["border-strong"] = ensure(pick(r["bg"]["L"] + 0.34, min(nc, 0.03), nh), r["bg"], 3.0, nh, min(nc, 0.03), darker=False)
        r["text"] = pick(0.94, min(ink["chroma"], 0.02), ink["hue"])
        high = r["surface"]  # the lightest dark surface
        r["text-muted"] = ensure(pick(0.72, min(nc, 0.02), nh), high, 4.5, nh, min(nc, 0.02), darker=False)
        r["text-subtle"] = ensure(pick(0.58, min(nc, 0.02), nh), high, 3.0, nh, min(nc, 0.02), darker=False)
        dark_l = a.get("lightness_dark", min(0.8, max(aL + 0.12, 0.68)))
        r["accent"] = pick(dark_l, ac * 0.9, ah)
        r["accent-hover"] = pick(min(0.92, dark_l + 0.05), ac * 0.9, ah)
        r["accent-tint"] = pick(0.27, ac * 0.3, ah)
        r["accent-text"] = ensure(pick(dark_l, ac * 0.9, ah), high, 4.5, ah, ac * 0.9, darker=False)
        if second:
            sl = second.get("lightness_dark", min(0.82, max(second.get("lightness", 0.6) + 0.1, 0.7)))
            r["second"] = pick(sl, second["chroma"] * 0.9, second["hue"])
            r["second-text"] = ensure(pick(sl, second["chroma"] * 0.9, second["hue"]), high, 4.5, second["hue"], second["chroma"] * 0.9, darker=False)
        if hl:
            hL = hl.get("lightness_dark", max(hl["lightness"], 0.72))
            r["highlight"] = pick(hL, hl["chroma"] * 0.9, hl["hue"])
            r["highlight-text"] = ensure(pick(hL, hl["chroma"] * 0.9, hl["hue"]), high, 4.5, hl["hue"], hl["chroma"] * 0.9, darker=False)
        for name, hue in sem.items():
            r[name] = ensure(pick(0.75, sc_sem * 0.87, hue), high, 4.5, hue, sc_sem * 0.87, darker=False)
            r[name + "-tint"] = pick(0.27, min(0.05, sc_sem * 0.35), hue)
    white, black = (1.0, 1.0, 1.0), (0.07, 0.07, 0.07)
    r["accent"], on = fill_for_text(r["accent"], ah, white, black)
    r["accent-hover"] = pick(max(0.1, r["accent"]["L"] - 0.06) if on == white else min(0.97, r["accent"]["L"] + 0.06), r["accent"]["C"], ah)
    r["on-accent"] = {"hex": to_hex(on), "rgb": on, "L": 1.0 if on == white else 0.18, "C": 0, "H": 0}
    if hl:
        r["highlight"], on_h = fill_for_text(r["highlight"], hl["hue"], white, black)
        r["on-highlight"] = {"hex": to_hex(on_h), "rgb": on_h, "L": 1.0 if on_h == white else 0.18, "C": 0, "H": 0}
    for i, col in enumerate(chart_colours(spec, mode, r["bg"]), 1):
        r[f"chart-{i}"] = col
    r["focus"] = r["accent-text"]
    if spec["color"].get("focus") == "ink":  # when the accent is not the action colour
        r["focus"] = r["text"]
    for name, value in (spec["color"].get("extra") or {}).items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name) or name in r:
            sys.exit(f"design.json: color.extra name '{name}' must be lower-case letters, digits and hyphens, and not a role name.")
        r[name] = extra_colour(name, value.get(mode, value.get("light")) if isinstance(value, dict) and ("light" in value or "dark" in value) else value)
    return r


def extra_colour(name, value):
    """A named colour from color.extra: a CSS colour string or {hue, chroma, lightness} in OKLCH."""
    if isinstance(value, dict):
        try:
            return pick(value["lightness"], value["chroma"], value["hue"])
        except KeyError:
            sys.exit(f"design.json: color.extra '{name}' needs hue, chroma and lightness, or a CSS colour.")
    col = parse_color(str(value)) if value is not None else None
    if not col:
        sys.exit(f"design.json: color.extra '{name}' is not a colour: {value!r}")
    L, c, h = srgb_to_oklch(*col[:3])
    return {"hex": to_hex(col), "rgb": tuple(col[:3]), "L": round(L, 3), "C": round(c, 4), "H": round(h, 1)}


def fill_for_text(fill, hue, white, black):
    """A fill that carries text (a button, a tag): keep its hue and chroma, and move its lightness the least distance
    that lets white or near-black text reach 4.5:1 on it. Mid-lightness oranges and greens otherwise fail with both."""
    best = max((white, black), key=lambda t: wcag_contrast(t, fill["rgb"]))
    if wcag_contrast(best, fill["rgb"]) >= 4.58:
        return fill, best
    for step in range(1, 60):
        for L, text in ((fill["L"] - step * 0.01, white), (fill["L"] + step * 0.01, black)):
            if 0.05 < L < 0.98:
                cand = pick(L, fill["C"], hue)
                if wcag_contrast(text, cand["rgb"]) >= 4.58:
                    return cand, text
    return fill, best


def semantic_hues(sem: dict, accent: dict) -> dict:
    """Keep status colours apart from the primary: a semantic hue within 20 degrees of a coloured primary moves to the far
    end of its own range (good stays green, bad stays red). Returns the hues to use."""
    out = {}
    for name, hue in sem.items():
        lo, hi = SEMANTIC_RANGE.get(name, (hue, hue))
        if accent.get("chroma", 0) >= 0.08 and hue_diff(hue, accent["hue"]) < 20:
            far = max((lo, hi, hue), key=lambda h: hue_diff(h, accent["hue"]))
            hue = far
        out[name] = hue
    return out


def chart_colours(spec, mode, bg):
    """Categorical chart colours from the palette: its own hues first, then hues spaced around the wheel, alternating in
    lightness so neighbours separate for colour-blind readers, each at least 3:1 on the ground (WCAG 1.4.11)."""
    c = spec["color"]
    want = c.get("chart", 6)
    if not want:
        return []
    base_c = min(0.16, max(0.1, c["accent"]["chroma"]))
    if isinstance(want, list):
        hues = [float(h) for h in want]
    else:
        hues = []
        for key in ("accent", "second", "highlight"):
            v = c.get(key)
            if v and v.get("chroma", 0) >= 0.05 and all(hue_diff(v["hue"], h) >= 30 for h in hues):
                hues.append(float(v["hue"]))
        if not hues:
            hues.append(float(c["accent"]["hue"]))
        while len(hues) < int(want):
            best = max(range(0, 360, 5), key=lambda h: min(hue_diff(h, x) for x in hues))
            hues.append(float(best))
    light = mode == "light"
    out = []
    for i, h in enumerate(hues):
        L = (0.5 if i % 2 == 0 else 0.62) if light else (0.78 if i % 2 == 0 else 0.66)
        cc = base_c if light else base_c * 0.9
        out.append(ensure(pick(L, cc, h), bg, 3.0, h, cc, darker=light))
    return out


def palette_check(spec, data) -> dict:
    """Harmony, colourfulness and competing pairs of the palette as built (light mode, or the first mode)."""
    r = data["roles"][data["modes"][0]]
    named = [("ground", r["bg"])]
    if spec["color"].get("surface_colour"):
        named.append(("surface", r["surface"]))
    named += [(k, r[k]) for k in ("accent", "second", "highlight") if k in r]
    named += [(k, r[k]) for k in data.get("extra", [])]
    colours = [(v["L"], v["C"], v["H"], 1.0) for _k, v in named]
    harmony, hues, note = classify_harmony(colours)
    prof = chroma_profile([(v["L"], v["C"], v["H"]) for _k, v in named])
    g = r["bg"]
    carriers = [k for k, v in named if (k == "ground" and v["C"] >= 0.03) or (k != "ground" and is_chromatic(v["L"], v["C"], 0.06))]
    strong = [(k, v["L"], v["C"], v["H"]) for k, v in named if k != "ground"]
    deliberate = spec.get("deliberate") or {}
    declared = (spec["color"].get("palette") or {}).get("harmony", "")
    out = {"harmony": harmony, "hues": hues, "note": note, "declared": declared, "profile": prof, "carriers": carriers,
           "competing": competing_pairs(strong), "timid": len(carriers) <= 1, "ground": g["hex"]}
    out["timid_ok"] = "palette-timid" in deliberate
    out["competing_ok"] = "palette-competing" in deliberate
    charts = [r[k] for k in r if k.startswith("chart-")]
    worst = None
    for kind in ("deutan", "protan"):
        for i in range(len(charts)):
            for j in range(i + 1, min(len(charts), i + 3)):  # neighbours in a legend matter most
                d = oklab_distance(simulate_cvd(charts[i]["rgb"], kind), simulate_cvd(charts[j]["rgb"], kind))
                if worst is None or d < worst[0]:
                    worst = (round(d, 3), kind, f"chart-{i + 1}", f"chart-{j + 1}")
    out["chart_cvd"] = worst
    return out


def type_tokens(spec):
    t = spec["type"]
    base = ROOT_PX  # not t["base"]: that is the body size, and spacing and radii also assume the 16px root
    lead_t, lead_d = t["leading"]["text"], t["leading"]["display"]
    fluid_from = t.get("fluid_from")
    out = []
    sizes = sorted(t["sizes"])
    for i, px in enumerate(sizes):
        if px <= 20:
            lh = lead_t if px >= 14 else max(lead_t - 0.1, 1.3)
        elif px >= 40:
            lh = lead_d
        else:
            lh = round(lead_t - (lead_t - lead_d) * (px - 20) / 20, 3)
        track = 0.0
        if px >= 56:
            track = -0.025
        elif px >= 36:
            track = -0.018
        elif px >= 24:
            track = -0.01
        elif px <= 12:
            track = 0.01
        value = f"{round(px / base, 5):g}rem"
        if fluid_from and px >= fluid_from:
            lo = max(sizes[max(0, i - 2)], round(px * 0.68))
            slope = (px - lo) / (1280 - 360) * 100
            icpt = (lo - slope * 3.6) / base
            value = f"clamp({round(lo / base, 5):g}rem, {icpt:.4g}rem + {slope:.3g}vw, {round(px / base, 5):g}rem)"
        out.append({"name": f"text-{i}", "px": px, "value": value, "line": round(lh, 3), "track": track})
    return out


def shadows(kind, mode):
    k = "0 0 0 / " if mode == "light" else "0 0 0 / "
    table = {
        "none": {"1": "none", "2": "none", "3": "none"},
        "hairline": {"1": f"0 0 0 1px rgb({k}0.06)", "2": f"0 1px 2px rgb({k}0.08), 0 0 0 1px rgb({k}0.06)",
                     "3": f"0 8px 24px -8px rgb({k}0.18), 0 0 0 1px rgb({k}0.06)"},
        "soft": {"1": f"0 1px 2px rgb({k}0.06)", "2": f"0 4px 12px -2px rgb({k}0.10)", "3": f"0 16px 40px -12px rgb({k}0.22)"},
        "hard": {"1": "2px 2px 0 currentColor", "2": "4px 4px 0 currentColor", "3": "8px 8px 0 currentColor"},
    }
    if kind not in table:
        sys.exit(f"design.json: shadow must be one of {sorted(table)}")
    return table[kind]


def fonts(spec):
    """Font roles: display, text and mono, plus any named under type.extra (a family string or a dict)."""
    out = {k: v for k, v in spec["type"].items() if k in ("display", "text", "mono")}
    for role, value in (spec["type"].get("extra") or {}).items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*", role) or role in out:
            sys.exit(f"design.json: type.extra role '{role}' must be lower-case letters, digits and hyphens, and not display, text or mono.")
        out[role] = value if isinstance(value, dict) else {"family": str(value)}
        if not out[role].get("family") or out[role]["family"] == "REPLACE":
            sys.exit(f"design.json: type.extra '{role}' needs a family.")
    return out


def build(spec):
    spec = normalise(spec)
    for p in ("name", "type.display.family", "type.text.family", "type.sizes", "type.leading.text", "type.leading.display",
              "color.neutral.hue", "color.neutral.chroma", "color.accent.hue", "color.accent.chroma", "color.accent.lightness",
              "space.base", "space.steps", "radius", "shadow"):
        need(spec, p)
    modes = spec["color"].get("modes", ["light"])
    data = {"name": spec["name"], "modes": modes,
            "ramps": {"neutral": ramp(spec["color"]["neutral"]["hue"], max(spec["color"]["neutral"]["chroma"], 0.0)),
                      "accent": ramp(spec["color"]["accent"]["hue"], spec["color"]["accent"]["chroma"])},
            "roles": {m: roles(spec, m) for m in modes}, "type": type_tokens(spec),
            "space": {str(s): spec["space"]["base"] * s for s in spec["space"]["steps"]},
            "radius": spec["radius"], "shadow": {m: shadows(spec["shadow"], m) for m in modes},
            "motion": spec.get("motion", {}), "fonts": fonts(spec),
            "measure": spec["type"].get("measure", 66), "body": spec["type"].get("base"),
            "extra": sorted((spec["color"].get("extra") or {}).keys())}
    second = spec["color"].get("second")
    if second:
        data["ramps"]["second"] = ramp(second["hue"], second["chroma"])
    hl = spec["color"].get("highlight")
    if hl:
        data["ramps"]["highlight"] = ramp(hl["hue"], hl["chroma"])
    data["palette"] = palette_check(spec, data)
    return data


def css_vars(data, selector_light=":root"):
    def block(mode):
        lines = [f"  --{k}: {v['hex']};" for k, v in data["roles"][mode].items()]
        lines += [f"  --shadow-{k}: {v};" for k, v in data["shadow"][mode].items()]
        return lines
    first = data["modes"][0]
    o = [f"/* {data['name']}: generated by human-design tokens.py from design.json. Edit design.json, not this file. */",
         f"{selector_light} {{", f"  color-scheme: {first};"]
    for role, f in data["fonts"].items():
        o.append(f"  --font-{role}: \"{f['family']}\", {f.get('fallback', 'sans-serif')};")
    for t in data["type"]:
        o += [f"  --{t['name']}: {t['value']};", f"  --{t['name']}-line: {t['line']};", f"  --{t['name']}-track: {t['track']}em;"]
    o.append(f"  --measure: {data['measure']}ch;")
    o += [f"  --space-{k}: {round(v / 16, 5):g}rem;" for k, v in data["space"].items()]
    o += [f"  --radius-{k}: {v}px;" for k, v in data["radius"].items()]
    o += [f"  --{k}: {v}{'ms' if isinstance(v, (int, float)) else ''};".replace("--ease", "--ease-out")
          for k, v in ((f"dur-{k}" if k != "ease" else "ease", v) for k, v in data["motion"].items())
          if isinstance(v, (int, float)) or k == "ease"]
    for name, r in data["ramps"].items():
        o += [f"  --{name}-{s}: {v['hex']};" for s, v in r.items()]
    o += block(first) + ["}"]
    if len(data["modes"]) > 1:
        other = data["modes"][1]
        guard = "dark" if other == "dark" else "light"
        opposite = "light" if guard == "dark" else "dark"
        o += [f"@media (prefers-color-scheme: {guard}) {{", f"  :root:not([data-theme=\"{opposite}\"]) {{", f"    color-scheme: {guard};"]
        o += ["  " + ln for ln in block(other)] + ["  }", "}", f":root[data-theme=\"{guard}\"] {{", f"  color-scheme: {guard};"]
        o += block(other) + ["}"]
    o += ["@media (prefers-reduced-motion: reduce) {", "  :root { --dur-press: 0ms; --dur-fast: 0ms; --dur-base: 0ms; --dur-slow: 0ms; }", "}"]
    return "\n".join(o) + "\n"


def tailwind(data):
    o = ["/* Tailwind v4: import after \"tailwindcss\". Generated by human-design tokens.py. */", "@theme {"]
    for role, f in data["fonts"].items():
        o.append(f"  --font-{role}: \"{f['family']}\", {f.get('fallback', 'sans-serif')};")
    for t in data["type"]:
        o += [f"  --text-{t['name'][5:]}: {t['value']};", f"  --text-{t['name'][5:]}--line-height: {t['line']};",
              f"  --text-{t['name'][5:]}--letter-spacing: {t['track']}em;"]
    o += [f"  --spacing-{k}: {v / 16:.4g}rem;" for k, v in data["space"].items()]
    o += [f"  --radius-{k}: {v}px;" for k, v in data["radius"].items()]
    for name, r in data["ramps"].items():
        o += [f"  --color-{name}-{s}: {v['hex']};" for s, v in r.items()]
    o += [f"  --color-{k}: var(--{k});" for k in data["roles"][data["modes"][0]]]
    o.append("}")
    return "\n".join(o) + "\n"


def swift(data):
    def col(v):
        r, g, b = v["rgb"]
        return f"Color(red: {r:.4f}, green: {g:.4f}, blue: {b:.4f})"
    name = "".join(ch for ch in data["name"].title() if ch.isalnum()) or "Design"
    o = ["// Generated by human-design tokens.py (iOS; use NSColor on macOS). Prefer system text styles and semantic",
         "// colours where the platform has them; these are for the brand's own roles.",
         "import SwiftUI", "", f"enum {name}Tokens {{"]
    light = data["roles"][data["modes"][0]]
    dark = data["roles"].get("dark")
    for k, v in light.items():
        ident = "".join(p.title() if i else p for i, p in enumerate(k.split("-")))
        if dark and data["modes"][0] != "dark":
            o.append(f"    static let {ident} = Color(UIColor {{ $0.userInterfaceStyle == .dark ? UIColor({col(dark[k])}) : UIColor({col(v)}) }})")
        else:
            o.append(f"    static let {ident} = {col(v)}")
    o += [f"    static let space{k}: CGFloat = {v}" for k, v in data["space"].items()]
    o += [f"    static let radius{k.title()}: CGFloat = {v}" for k, v in data["radius"].items()]
    o.append("}")
    return "\n".join(o) + "\n"


def kotlin(data):
    name = "".join(ch for ch in data["name"].title() if ch.isalnum()) or "Design"
    o = ["// Generated by human-design tokens.py. Map these onto a Material 3 ColorScheme; do not bypass the theme.",
         "import androidx.compose.ui.graphics.Color", "import androidx.compose.ui.unit.dp", "", f"object {name}Tokens {{"]
    for mode in data["modes"]:
        o.append(f"    object {mode.title()} {{")
        for k, v in data["roles"][mode].items():
            ident = "".join(p.title() for p in k.split("-"))
            o.append(f"        val {ident} = Color(0xFF{v['hex'][1:].upper()})")
        o.append("    }")
    o += [f"    val Space{k} = {v}.dp" for k, v in data["space"].items()]
    o += [f"    val Radius{k.title()} = {v}.dp" for k, v in data["radius"].items()]
    o.append("}")
    return "\n".join(o) + "\n"


def report(data):
    o = [f"# Tokens: {data['name']}", ""]
    for mode in data["modes"]:
        r = data["roles"][mode]
        pairs = [("text", "bg", 4.5), ("text", "surface", 4.5), ("text-muted", "bg", 4.5), ("text-subtle", "bg", 3.0),
                 ("accent-text", "bg", 4.5), ("on-accent", "accent", 4.5), ("border-strong", "bg", 3.0), ("focus", "bg", 3.0)]
        pairs += [(k, "bg", 4.5) for k in r if k in ("good", "warn", "bad", "info", "second-text", "highlight-text")]
        pairs += [("on-highlight", "highlight", 4.5)] if "highlight" in r else []
        pairs += [(k, "bg", 3.0) for k in r if k.startswith("chart-")]
        rows = []
        for fg, bg, target in pairs:
            ratio = wcag_contrast(r[fg]["rgb"], r[bg]["rgb"])
            rows.append([f"{fg} on {bg}", r[fg]["hex"], r[bg]["hex"], f"{ratio:.2f}", f"{apca(r[fg]['rgb'], r[bg]['rgb']):.0f}",
                         f"{target}", "ok" if ratio >= target else "FAIL"])
        o += [f"## Roles, {mode}", "", md_table(["pair", "foreground", "background", "WCAG ratio", "APCA Lc", "needs", "result"], rows), ""]
    for name, r in data["ramps"].items():
        o += [f"## Ramp: {name}", "", md_table(["step", "hex", "L", "C", "clipped to sRGB"],
                                             [[s, v["hex"], v["L"], v["C"], "yes" if v["clipped"] else ""] for s, v in r.items()]), ""]
    o += ["## Type", "", md_table(["token", "px", "value", "line height", "tracking"],
                                 [[t["name"], t["px"], t["value"], t["line"], f"{t['track']}em"] for t in data["type"]]), ""]
    sizes = [t["px"] for t in data["type"]]
    if data.get("body") and data["body"] not in sizes:
        o.append(f"Note: type.base (the body size, {data['body']}px) is not one of the sizes. Add it, or set base to the body size you use.")
    extra = [k for k in data["roles"][data["modes"][0]] if k in data.get("extra", [])]
    if extra:
        o.append("Extra colours: " + ", ".join(f"--{k} {data['roles'][data['modes'][0]][k]['hex']}" for k in extra) + ".")
    if len(sizes) > 9:
        o.append(f"Note: {len(sizes)} sizes. Product UI rarely needs more than 6 or 7; every extra size weakens the hierarchy.")
    o += [""] + palette_report(data["palette"])
    acc = data["roles"][data["modes"][0]]["accent"]
    if wcag_contrast(acc["rgb"], data["roles"][data["modes"][0]]["bg"]["rgb"]) < 3:
        o.append("Note: the accent itself is under 3:1 on the background. Use it for fills with on-accent text; use accent-text for links and icons.")
    return "\n".join(o)


def palette_report(pc) -> list:
    o = ["## Palette", "", f"Harmony: {pc['harmony']} ({pc['note']}; hue families at {', '.join(f'{h:.0f}' for h in pc['hues']) or 'none'})."]
    said = re.split(r"[:(;,]", pc["declared"] or "")[0].strip().lower()
    if said and not said.startswith("replace") and said != pc["harmony"]:
        o.append(f"Declared harmony is \"{pc['declared']}\"; the built palette reads as {pc['harmony']}. Fix the roles or the declaration.")
    p = pc["profile"]
    o.append(f"Colourfulness: {p['level']} (strongest chroma {p['max']}, {p['chromatic']} colours carry a hue; colour comes from: "
             f"{', '.join(pc['carriers']) or 'nothing'}).")
    if pc["timid"]:
        o.append(("Declared deliberate: " if pc["timid_ok"] else "ERROR timid palette: ") +
                 "only one colour carries any hue; everything else is grey or near-white. Give a second colour a job (secondary, "
                 "highlight, a coloured surface) or tint the ground from the subject, or record \"palette-timid\" under deliberate "
                 "with the reason the subject needs this restraint.")
    for a, b, d in pc["competing"]:
        o.append(("Declared deliberate: " if pc["competing_ok"] else "ERROR competing colours: ") +
                 f"{a} and {b} are {d} degrees apart at similar strength and lightness, so neither leads. Move one in lightness "
                 "(at least 0.15), lower its chroma, or move its hue to a neighbour or an opposite; or record \"palette-competing\" "
                 "under deliberate.")
    if pc.get("chart_cvd"):
        d, kind, x, y = pc["chart_cvd"]
        o.append(f"Charts: closest neighbours for a {kind} reader are {x} and {y} (OKLab distance {d})." +
                 (" Too close: add a pattern or label, or change the order." if d < 0.05 else ""))
    return o


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?", help="design.json")
    ap.add_argument("--init", metavar="FILE", help="write a starter design.json and exit")
    ap.add_argument("--css")
    ap.add_argument("--tailwind")
    ap.add_argument("--json")
    ap.add_argument("--swift")
    ap.add_argument("--kotlin")
    a = ap.parse_args(argv)
    if a.init in ("-", "/dev/stdout"):
        print(json.dumps(STARTER, indent=2))
        return 0
    if a.init:
        if os.path.exists(a.init):
            sys.exit(f"{a.init} exists; not overwriting.")
        with open(a.init, "w", encoding="utf-8") as fh:
            json.dump(STARTER, fh, indent=2)
        print(f"Wrote {a.init}. Replace every value from the brief before generating tokens.")
        return 0
    if not a.spec:
        ap.error("give design.json or --init FILE")
    with open(a.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    data = build(spec)
    wrote = []
    for path, fn in ((a.css, css_vars), (a.tailwind, tailwind), (a.swift, swift), (a.kotlin, kotlin)):
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(fn(data))
            wrote.append(path)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=1, default=lambda x: list(x) if isinstance(x, tuple) else str(x))
        wrote.append(a.json)
    print(report(data))
    if wrote:
        print("\nWrote: " + ", ".join(wrote))
    fails = [1 for m in data["modes"] for fg, bg, t in (("text", "bg", 4.5), ("text-muted", "bg", 4.5), ("on-accent", "accent", 4.5))
             if wcag_contrast(data["roles"][m][fg]["rgb"], data["roles"][m][bg]["rgb"]) < t]
    pc = data["palette"]
    if (pc["timid"] and not pc["timid_ok"]) or (pc["competing"] and not pc["competing_ok"]):
        fails.append(1)
    return 2 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
