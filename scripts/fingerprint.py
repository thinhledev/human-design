#!/usr/bin/env python3
"""Fingerprint a design and compare it with other projects and with the default
looks that AI tools converge on.

Usage:
  python3 fingerprint.py src/                         # this project's fingerprint and its nearest default look
  python3 fingerprint.py src/ --save acme             # remember it under a name
  python3 fingerprint.py src/ --against               # compare with every saved project (reads only)
  python3 fingerprint.py --taken                      # what saved projects already use; read before choosing
  python3 fingerprint.py --compare projA/src projB/src [projC/src]
  python3 fingerprint.py mockup.html --json

The fingerprint is what makes one interface recognisable next to another:
type families and how they are used, the accent hue and the temperature of the
neutrals, the ground (white, cream, grey, near-black), corner radius, shadow
style, type-scale ratio, how much is centred, the column habit, gradients and
glass. Two projects by a designer on autopilot share most of it.

Saved fingerprints live in ~/.human-design/fingerprints (or --registry DIR) so
that a design made in one repository can be checked against the others. Only
the fingerprint is stored: no source code, no content. --against only reads
the registry; nothing is written without --save.

Two rules apply between unrelated projects whatever the score: they may not
share a text or display typeface, and they may not share both ground and accent
hue. Pass --same-brand when the projects belong to one brand. --compare on
directions or screens of one project (files in one folder, a directions/
folder, or paths under one design.json or DESIGN.md) prints a note instead of
clashes.

Light-mode declarations are read; custom properties (tokens) are resolved. Give
each design its own files: one HTML or CSS file per direction when comparing
directions.

It reads source files (HTML, CSS, JSX or TSX, Vue, Svelte, Astro, Tailwind
classes). For a rendered page, pass the JSON from render_check.py --json with
--render. Standard library only. No network access.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design_lib import (class_tokens, collect, declarations, family_of, font_mentions, font_shorthand_size, hue_name,  # noqa: E402
                        is_dark_context, length_px, md_table, parse_color, resolve_vars, size_px, srgb_to_oklch)

GENERIC = {"serif", "sans-serif", "monospace", "system-ui", "ui-sans-serif", "ui-serif", "ui-monospace", "ui-rounded",
           "-apple-system", "blinkmacsystemfont", "inherit", "segoe ui", "roboto", "helvetica neue", "helvetica", "arial",
           "apple color emoji", "segoe ui emoji", "noto sans", "liberation sans", "sf pro text", "sf pro display"}
TW_HUE = {"red": 25, "orange": 50, "amber": 75, "yellow": 95, "lime": 125, "green": 150, "emerald": 162, "teal": 180,
          "cyan": 210, "sky": 235, "blue": 260, "indigo": 277, "violet": 293, "purple": 305, "fuchsia": 325, "pink": 350,
          "rose": 15}
TW_NEUTRAL = {"slate": "cool", "gray": "cool", "zinc": "cool", "neutral": "none", "stone": "warm"}
TW_RADIUS = {"rounded-none": 0, "rounded-sm": 2, "rounded": 4, "rounded-md": 6, "rounded-lg": 8, "rounded-xl": 12,
             "rounded-2xl": 16, "rounded-3xl": 24, "rounded-4xl": 32, "rounded-full": 999}
TW_TEXT = {"text-xs": 12, "text-sm": 14, "text-base": 16, "text-lg": 18, "text-xl": 20, "text-2xl": 24, "text-3xl": 30,
           "text-4xl": 36, "text-5xl": 48, "text-6xl": 60, "text-7xl": 72, "text-8xl": 96, "text-9xl": 128}
DISPLAY_SEL = re.compile(r"\bh[1-3]\b|\.(display|hero|title|headline|heading)\b|\bhgroup\b", re.I)
BODY_SEL = re.compile(r"(^|[\s,>])(body|html|:root|p|main|article)\b|\.(prose|body|text)\b", re.I)

# The looks AI tools converge on. Each is a partial fingerprint; a design near one of them is on autopilot.
DEFAULT_LOOKS = {
    "framework default (shadcn or Tailwind starter)": {
        "fonts": ["inter", "geist", "geist sans", "(system)"], "ground": ["white", "near-black"], "neutral": ["cool", "none"],
        "radius": ["8-12", "16+"], "shadow": ["soft"], "accent": ["neutral", "blue", "indigo"]},
    "purple gradient SaaS": {
        "fonts": ["inter", "poppins", "plus jakarta sans", "(system)", "manrope", "dm sans"], "ground": ["white", "near-black"],
        "accent": ["indigo", "purple", "blue", "pink"], "radius": ["8-12", "16+", "pill"], "shadow": ["soft"], "gradient": [True],
        "centred": [True]},
    "cream editorial (second-generation default)": {
        "fonts": ["instrument serif", "playfair display", "fraunces", "cormorant garamond", "cormorant", "newsreader", "dm serif display",
                  "libre baskerville", "eb garamond", "lora"],
        "ground": ["cream", "warm white"], "neutral": ["warm"], "accent": ["orange", "red", "green", "amber"], "radius": ["0", "1-3", "4-6"],
        "shadow": ["none", "hairline"]},
    "dark with a neon accent": {
        "fonts": ["inter", "geist", "space grotesk", "jetbrains mono", "geist mono", "(system)"], "ground": ["near-black"],
        "accent": ["lime", "green", "cyan", "teal", "orange", "red"], "radius": ["0", "1-3", "4-6", "8-12"], "shadow": ["none", "glow"]},
    "glass and glow": {
        "fonts": ["inter", "sf pro display", "(system)", "plus jakarta sans", "outfit", "sora"], "ground": ["near-black", "white"],
        "accent": ["blue", "purple", "indigo", "cyan", "pink"], "radius": ["16+", "pill"], "glass": [True], "gradient": [True]},
    "sage paper and pine ink (third-generation default)": {
        "ground": ["sage"], "ink": ["green", "teal", "lime"], "accent": ["indigo", "blue", "purple"], "neutral": ["cool", "warm"],
        "radius": ["0", "1-3", "4-6"], "shadow": ["none", "hairline"]},
    "techno mono (space grotesk and mono labels)": {
        "fonts": ["space grotesk", "space mono", "jetbrains mono", "ibm plex mono", "geist mono", "dm mono"],
        "ground": ["white", "cream", "near-black"], "radius": ["0", "1-3"], "shadow": ["none", "hard"], "mono_labels": [True]},
}
# Traits a design must share before it can be called that look; without them the score is capped.
MUST = {"framework default (shadcn or Tailwind starter)": ["fonts"], "purple gradient SaaS": ["gradient", "accent"],
        "cream editorial (second-generation default)": ["ground", "fonts"], "dark with a neon accent": ["ground", "accent"],
        "glass and glow": ["glass"], "techno mono (space grotesk and mono labels)": ["fonts"],
        "sage paper and pine ink (third-generation default)": ["ground", "accent"]}
WEIGHTS = {"fonts": 0.30, "accent": 0.17, "ground": 0.12, "ink": 0.06, "neutral": 0.05, "radius": 0.10, "shadow": 0.06, "ratio": 0.05,
           "centred": 0.05, "gradient": 0.04, "glass": 0.03, "mono_labels": 0.02}


def radius_bucket(px: float) -> str:
    if px >= 500:
        return "pill"
    if px <= 0:
        return "0"
    return "1-3" if px <= 3 else "4-6" if px <= 6 else "8-12" if px <= 13 else "16+"


def ground_of(rgb) -> str:
    L, c, h = srgb_to_oklch(*rgb[:3])
    if L < 0.3:
        return "near-black"
    if L < 0.6:
        return "mid"
    if c < 0.006:
        return "white" if L > 0.975 else "grey"
    if 40 <= h < 110:
        # cream is a visibly yellowed paper (#f5f0e1, chroma 0.012 or more); lime-wash or newsprint just off white is not
        return "cream" if c >= 0.011 else "warm white"
    if 110 <= h < 175:
        return "sage"
    if 175 <= h < 290:
        return "cool"
    return "blush"


GROUND_SEL = re.compile(r"(^|[\s,>])(body|html|:root|main)\b|#(root|app|__next)\b|\.(app|page|wrap|wrapper|layout|shell|site)\b|^x$")
GROUND_VARS = {"--bg", "--background", "--paper", "--ground", "--canvas", "--color-bg", "--color-background", "--page", "--surface-0",
               "--base", "--bg-page", "--page-bg"}
INK_VARS = {"--ink", "--text", "--fg", "--foreground", "--color-text", "--text-primary", "--color-fg"}


def extract(sources) -> dict:
    """Fingerprint from source files. Light-mode declarations only; custom properties are resolved."""
    table, rows = {}, []
    for src in sources:
        for sel, prop, val, _line, at in declarations(src):
            dark = is_dark_context(sel, at)
            rows.append((src, sel, prop, val, dark))
            if prop.startswith("--") and not dark and prop not in table:
                table[prop] = val
    only_dark = bool(rows) and all(r[4] for r in rows if r[2] in GROUND_VARS or r[2].startswith("background"))
    fams, display, body = Counter(), Counter(), Counter()
    # status classes whose text colour is only used for state ("In stock", "Failed"), never for the brand
    status_sel = re.compile(r"status|stock|availab|\b(valid|invalid|ok|done|paid|overdue|late|online|offline)\b", re.I)
    chroma_hues, bgs, neutral_tint, ink = Counter(), Counter(), Counter(), Counter()
    radii, shadows, sizes = Counter(), Counter(), Counter()
    centred = text_align = gradient = glass = cols3 = mono_small = 0
    tw = Counter()
    for src in sources:
        for fam, _line, how in font_mentions(src):
            if fam and fam not in GENERIC:
                fams[fam] += 2
                if how in ("next/font", "geist package", "tailwind config") and "mono" not in fam:
                    body[fam] += 1
    for src, sel, prop, raw, dark in rows:
        if dark and not only_dark:
            continue
        val = resolve_vars(raw, table)
        low = val.lower()
        fam = family_of(prop, val)
        if fam and fam not in GENERIC:
            fams[fam] += 1
            if DISPLAY_SEL.search(sel) or "display" in prop or "heading" in prop:
                display[fam] += 2
            if (BODY_SEL.search(sel) and not prop.startswith("--")) or prop in ("--font-sans", "--font-body", "--font-text"):
                body[fam] += 3 if re.search(r"\b(body|html)\b", sel) else 2
        is_ground = (prop in GROUND_VARS and re.search(r":root|html|body", sel)) or \
                    (prop in ("background", "background-color") and GROUND_SEL.search(sel + " "))
        is_ink = (prop in INK_VARS and re.search(r":root|html|body", sel)) or (prop == "color" and re.search(r"(^|[\s,])(body|html|:root)\b", sel))
        for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b|(?:rgba?|hsla?|oklch|oklab)\([^)]*\)", val):
            col = parse_color(m.group(0))
            if not col or col[3] < 0.5:
                continue
            L, c, h = srgb_to_oklch(*col[:3])
            if is_ink:
                ink[hue_name(h, c, L) if c >= 0.012 else "neutral"] += 1
            if is_ground and (L > 0.85 or L < 0.3):
                bgs[ground_of(col)] += 3 if re.search(r"body|html|:root", sel) else 1
                continue
            if prop.startswith("--") and re.search(r"-(\d{2,3})$", prop):
                continue  # ramp steps are raw material, not usage
            if re.search(r"(?<![a-z])(?:good|warn(?:ing)?|bad|info|danger|success|errors?|alert|critical|positive|negative|caution|ok)(?![a-z])",
                         prop + " " + sel + " " + raw, re.I):
                continue  # semantic colours (named so in the property, the selector or the token used) are not the brand's accent
            if prop == "color" and status_sel.search(sel):
                continue  # status text such as "In stock" in green
            if c >= 0.07 and 0.25 < L < 0.92:
                chroma_hues[hue_name(h, c, L)] += 1
            elif c >= 0.004:
                neutral_tint["warm" if (h < 115 or h > 340) else "cool"] += 1
            else:
                neutral_tint["none"] += 1
        if prop.endswith("radius") and not prop.startswith("--"):
            first = low.split()[0] if low.split() else ""
            if re.search(r"9999|999px|100vmax|infinity", low):
                radii["pill"] += 1
            elif first.endswith("%"):
                pass  # circles (spinners, avatars) say nothing about the radius habit
            else:
                px = length_px(first)
                if px is not None:
                    radii[radius_bucket(px)] += 1
        if prop == "box-shadow" and low not in ("none", "0", "unset", "inherit", "initial"):
            parts = re.sub(r"\([^)]*\)", "", low).split(",")[0].split()
            nums = [length_px(x) for x in parts if length_px(x) is not None]
            blur = nums[2] if len(nums) > 2 else 0
            if not ("inset" in low and len(nums) < 3):
                if len(nums) >= 2 and blur == 0 and (abs(nums[0]) >= 2 or abs(nums[1]) >= 2):
                    shadows["hard"] += 1
                elif len(nums) >= 4 and nums[0] == 0 and nums[1] == 0 and blur == 0:
                    shadows["hairline"] += 1
                elif blur and blur >= 16 and nums[0] == 0 and nums[1] == 0 and re.search(r"#(?!000)[0-9a-f]{3,8}|rgba?\(\s*(?!0[\s,]+0[\s,]+0)|oklch|hsl", raw.lower()):
                    shadows["glow"] += 1
                else:
                    shadows["soft"] += 1
        px = size_px(low) if prop == "font-size" else (font_shorthand_size(low) if prop == "font" else None)
        if px and 9 <= px <= 200:
            sizes[round(px)] += 1
        if prop == "text-align":
            text_align += 1
            centred += low.startswith("center")
        if "gradient(" in low and prop.startswith("background") and not re.search(r"transparent\s*[\d.]*%?\s*,\s*transparent|1px", low):
            gradient += 1
        if prop in ("backdrop-filter", "-webkit-backdrop-filter") and "blur" in low:
            glass += 1
        if prop == "grid-template-columns" and re.search(r"repeat\(\s*3\s*,|^(1fr\s+){2}1fr$", low):
            cols3 += 1
        if family_of(prop, val) and "mono" in family_of(prop, val) and re.search(r"label|eyebrow|kicker|tag|badge|caption|meta|overline|th\b", sel, re.I):
            mono_small += 1
    for src in sources:
        for tok, _line in class_tokens(src):
            tw[tok.split(":")[-1].lstrip("!-")] += 1
    tw_used = sum(tw.values()) > 20 and any(k.startswith(("flex", "grid", "px-", "py-", "text-")) for k in tw)
    if tw_used:
        for k, n in tw.items():
            m = re.match(r"(?:bg|text|from|via|to|border|ring|fill|stroke|outline|decoration|accent|shadow)-([a-z]+)-(\d{2,3})(?:/\d+)?$", k)
            if m:
                name, step = m.group(1), int(m.group(2))
                if name in TW_HUE and 300 <= step <= 800:
                    chroma_hues[hue_name(TW_HUE[name], 0.15, 0.6)] += n
                elif name in TW_NEUTRAL:
                    neutral_tint[TW_NEUTRAL[name]] += n
            if k in TW_RADIUS and k != "rounded-full":
                radii[radius_bucket(TW_RADIUS[k])] += n
            if re.match(r"shadow(-(sm|md|lg|xl|2xl))?$", k):
                shadows["soft"] += n
            if k in TW_TEXT:
                sizes[TW_TEXT[k]] += n
            if k == "text-center":
                centred += n
                text_align += n
            elif k in ("text-left", "text-right", "text-start", "text-end"):
                text_align += n
            if k.startswith("bg-gradient-to-") or k.startswith("bg-linear-to-"):
                gradient += n
            if k.startswith("backdrop-blur"):
                glass += n
            if k == "grid-cols-3":
                cols3 += n
            if k == "font-mono" and (tw.get("uppercase") or tw.get("tracking-widest") or tw.get("tracking-wider")):
                mono_small += 1
            if k in ("bg-white", "bg-background"):
                bgs["white"] += 1
            if re.match(r"bg-(black|zinc-9\d0|neutral-9\d0|slate-9\d0|gray-9\d0)$", k):
                bgs["near-black"] += 1
    fonts = [f for f, _n in fams.most_common(4)] or ["(system)"]
    non_mono = [f for f in fonts if "mono" not in f] or fonts
    text_face = (body.most_common(1) or [(non_mono[0], 0)])[0][0]
    display_face = (display.most_common(1) or [(text_face, 0)])[0][0]
    sz = sorted(sizes)
    ratios = [b / a for a, b in zip(sz, sz[1:]) if 1.05 < b / a < 1.7]
    total_r = sum(radii.values())
    accents = [h for h, _n in chroma_hues.most_common(2)] or ["neutral"]
    return {
        "fonts": fonts, "display": display_face, "text": text_face,
        "accent": accents,
        "accent_spread": len([h for h, n in chroma_hues.items() if n >= max(2, 0.12 * sum(chroma_hues.values()))]),
        "neutral": (neutral_tint.most_common(1) or [("none", 0)])[0][0],
        "ground": (bgs.most_common(1) or [("unknown", 0)])[0][0],
        "ink": (ink.most_common(1) or [("unknown", 0)])[0][0],
        "radius": (radii.most_common(1) or [("0", 0)])[0][0],
        "radius_uniform": round(radii.most_common(1)[0][1] / total_r, 2) if total_r else 0.0,
        "shadow": (shadows.most_common(1) or [("none", 0)])[0][0],
        "sizes": sz[:14],
        "ratio": round(statistics.median(ratios), 3) if ratios else None,
        "centred": bool(text_align and centred / text_align > 0.6 and centred >= 4),
        "gradient": gradient >= 2, "glass": glass >= 2, "three_columns": cols3 >= 2, "mono_labels": mono_small >= 2,
        "tailwind": bool(tw_used),
        "evidence": {"font_declarations": sum(fams.values()), "colours": sum(chroma_hues.values()) + sum(neutral_tint.values()),
                     "radii": total_r, "files": len(sources)},
    }


def from_render(path: str) -> dict:
    """Fingerprint from render_check.py --json output (the widest light run)."""
    with open(path, encoding="utf-8") as fh:
        runs = json.load(fh)
    light = [r for r in runs if r.get("scheme") != "dark"] or runs
    f = max(light, key=lambda r: r.get("width", 0))
    named = [(x["name"].lower(), x["share"]) for x in f["families"] if x["share"] > 0.02 and not x.get("generic")]
    fams = [n for n, _s in named] or ["(system)"]
    non_mono = [(n, sh) for n, sh in named if "mono" not in n] or named or [("(system)", 1)]
    text_face = max(non_mono, key=lambda x: x[1])[0]
    big = (f.get("fold", {}).get("largest") or {}).get("family", "").lower()
    display_face = big if big and big not in GENERIC else text_face
    hues = Counter()
    ink = "unknown"
    for i, (hexv, share) in enumerate(f["textColors"]):
        col = parse_color(hexv)
        L, c, h = srgb_to_oklch(*col[:3])
        if i == 0:
            ink = hue_name(h, c, L) if c >= 0.02 else "neutral"
        elif c >= 0.07:
            hues[hue_name(h, c, L)] += share
    for hexv in f.get("fills", []):
        col = parse_color(hexv)
        L, c, h = srgb_to_oklch(*col[:3])
        if c >= 0.07 and 0.25 < L < 0.92:
            hues[hue_name(h, c, L)] += 0.05
    page_bg = f.get("pageBackground") or (f["backgrounds"][0] if f["backgrounds"] else "#ffffff")
    bg = parse_color(page_bg) or (1, 1, 1, 1)
    radii = [(k, n) for k, n in f["radii"] if not str(k).endswith("%")]
    rad = radii[0][0] if radii else "0"
    total_r = sum(n for _k, n in radii) or 1
    sz = [round(x) for x, share in f["sizes"]]
    ratios = [b / a for a, b in zip(sz, sz[1:]) if 1.05 < b / a < 1.7]
    return {"fonts": fams, "display": display_face, "text": text_face, "accent": [h for h, _ in hues.most_common(2)] or ["neutral"],
            "accent_spread": len(hues), "neutral": "unknown", "ground": ground_of(bg), "ink": ink,
            "radius": rad if rad == "pill" else radius_bucket(float(re.sub(r"[^0-9.]", "", rad) or 0)),
            "radius_uniform": round((radii[0][1] if radii else 0) / total_r, 2),
            "shadow": "soft" if f["shadows"] else "none", "sizes": sz, "ratio": round(statistics.median(ratios), 3) if ratios else None,
            "centred": f["centeredShare"] > 0.6, "gradient": f["gradients"] >= 2 or f["gradientText"] > 0, "glass": f["backdropBlur"] >= 2,
            "three_columns": False, "mono_labels": False, "tailwind": False, "evidence": {"rendered": True}}


def faces(fp: dict) -> set:
    """The typefaces that carry a design: display and text faces, without system and mono families."""
    return {f for f in (fp.get("display"), fp.get("text")) if f and f != "(system)" and "mono" not in f and f not in GENERIC}


def similarity(a: dict, b: dict):
    """Return (score 0..1, list of shared traits) for two full fingerprints."""
    shared, score, total = [], 0.0, 0.0
    fa, fb = faces(a) or set(a["fonts"][:2]), faces(b) or set(b["fonts"][:2])
    total += WEIGHTS["fonts"]
    if fa & fb:
        score += WEIGHTS["fonts"] * len(fa & fb) / max(1, min(len(fa), len(fb)))
        shared.append("typefaces: " + ", ".join(sorted(fa & fb)))
    total += WEIGHTS["accent"]
    if a["accent"][0] == b["accent"][0]:
        score += WEIGHTS["accent"]
        shared.append("accent hue: " + a["accent"][0])
    elif set(a["accent"]) & set(b["accent"]):
        score += WEIGHTS["accent"] * 0.5
        shared.append("a shared hue: " + ", ".join(sorted(set(a["accent"]) & set(b["accent"]))))
    for key, labelf in (("ground", "ground: {}"), ("ink", "ink: {}"), ("neutral", "neutrals: {}"), ("radius", "corner radius: {}"),
                        ("shadow", "shadows: {}")):
        if a.get(key, "unknown") == "unknown" or b.get(key, "unknown") == "unknown":
            continue
        total += WEIGHTS[key]
        if a[key] == b[key]:
            score += WEIGHTS[key]
            shared.append(labelf.format(a[key]))
    if a.get("ratio") and b.get("ratio"):
        total += WEIGHTS["ratio"]
        if abs(a["ratio"] - b["ratio"]) <= 0.03:
            score += WEIGHTS["ratio"]
            shared.append(f"type-scale ratio about {a['ratio']}")
    for key, name in (("centred", "mostly centred text"), ("gradient", "gradient fills"), ("glass", "blurred glass"),
                      ("mono_labels", "monospace labels")):
        if a.get(key) or b.get(key):  # a habit neither has is not a resemblance
            total += WEIGHTS[key]
            if a.get(key) == b.get(key):
                score += WEIGHTS[key]
                shared.append(name)
    return (score / total if total else 0.0), shared


def shared_faces(a: dict, b: dict) -> set:
    return faces(a) & faces(b)


def nearest_default(fp: dict):
    """Score a fingerprint against each default look. Returns [(name, score, matched traits)], best first."""
    out = []
    for name, look in DEFAULT_LOOKS.items():
        score = total = 0.0
        hit, matched = [], set()
        roles = {fp["display"], fp["text"]} | ({f for f in fp["fonts"] if "mono" in f} if fp.get("mono_labels") else set())
        for key, allowed in look.items():
            w = WEIGHTS.get(key, 0.03)
            total += w
            mine = fp.get(key)
            if key == "fonts":
                got = roles & set(allowed)
                if got:
                    score += w
                    matched.add(key)
                    hit.append("type " + ", ".join(sorted(got)))
            elif key == "accent":
                got = set(fp["accent"]) & set(allowed)
                if got:
                    score += w
                    matched.add(key)
                    hit.append("accent " + ", ".join(sorted(got)))
            elif mine in allowed and mine != "unknown":
                score += w
                matched.add(key)
                if mine not in (False, None):
                    hit.append(f"{key} {mine}" if not isinstance(mine, bool) else key.replace("_", " "))
        value = score / total if total else 0.0
        if any(k not in matched for k in MUST.get(name, [])):
            value = min(value, 0.45) * 0.9
        out.append((name, value, hit))
    return sorted(out, key=lambda x: -x[1])


def describe(fp: dict) -> list:
    return [["Typefaces", ", ".join(fp["fonts"]) + (f" (display: {fp['display']}; text: {fp['text']})" if len(fp["fonts"]) > 1 else "")],
            ["Accent hue", ", ".join(fp["accent"]) + (f"; {fp['accent_spread']} hue families in use" if fp.get("accent_spread", 0) > 2 else "")],
            ["Neutrals", fp["neutral"]], ["Ground", fp["ground"]], ["Ink", fp.get("ink", "unknown")],
            ["Corner radius", ("pill" if fp["radius"] == "pill" else f"{fp['radius']}px") + (f", on {fp['radius_uniform']:.0%} of rounded boxes" if fp.get("radius_uniform") else "")],
            ["Shadows", fp["shadow"]], ["Type sizes", ", ".join(str(s) for s in fp["sizes"]) or "not found"],
            ["Scale ratio", fp["ratio"] or "irregular or not found"],
            ["Habits", ", ".join(k.replace("_", " ") for k in ("centred", "gradient", "glass", "three_columns", "mono_labels") if fp.get(k)) or "none flagged"]]


def registry_dir(a) -> str:
    return a.registry or os.path.join(os.path.expanduser("~"), ".human-design", "fingerprints")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="source files or folders of one project")
    ap.add_argument("--compare", nargs="+", metavar="PATH", help="two or more projects to compare with each other")
    ap.add_argument("--render", help="JSON from render_check.py --json, used instead of source files")
    ap.add_argument("--save", metavar="NAME", help="store this fingerprint under a name")
    ap.add_argument("--against", action="store_true", help="compare with every saved fingerprint")
    ap.add_argument("--registry", help="folder for saved fingerprints (default ~/.human-design/fingerprints)")
    ap.add_argument("--taken", action="store_true", help="list what the saved projects already use (typefaces, ground, ink, accent), to read before choosing")
    ap.add_argument("--same-brand", action="store_true", help="the projects belong to one brand: sharing typefaces and colours is intended")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.taken:
        reg = registry_dir(a)
        rows = []
        if os.path.isdir(reg):
            for f in sorted(os.listdir(reg)):
                if f.endswith(".json"):
                    with open(os.path.join(reg, f), encoding="utf-8") as fh:
                        o = json.load(fh)
                    rows.append([f[:-5], ", ".join(sorted(faces(o))) or o["fonts"][0], o.get("ground", "?"), o.get("ink", "?"), ", ".join(o["accent"]),
                                 o.get("radius", "?"), o.get("shadow", "?")])
        if not rows:
            print(f"No saved projects in {reg}. Nothing is taken yet.")
            return 0
        print("# Already used by this owner's projects\n\n" + md_table(["project", "typefaces", "ground", "ink", "accent", "radius", "shadow"], rows))
        print("\nA new, unrelated product must not reuse a typeface from this list, nor a ground and accent pair. Choose from its own subject.")
        return 0
    if a.compare:
        if len(a.compare) < 2:
            ap.error("--compare needs two or more paths")
        fps = [(os.path.basename(os.path.abspath(p).rstrip("/")) or p, extract(collect([p]))) for p in a.compare]
        o = ["# Fingerprint comparison", ""]
        rows, worst, clashes = [], 0.0, []
        for i in range(len(fps)):
            for j in range(i + 1, len(fps)):
                s, shared = similarity(fps[i][1], fps[j][1])
                worst = max(worst, s)
                rows.append([f"{fps[i][0]} vs {fps[j][0]}", f"{s:.0%}", "; ".join(shared) or "nothing notable"])
                clashes += clash(fps[i][0], fps[i][1], fps[j][0], fps[j][1])
        o += [md_table(["pair", "similarity", "shared"], rows), ""]
        for name, fp in fps:
            o += [f"## {name}", "", md_table(["trait", "value"], describe(fp)), ""]
        o.append(verdict(worst))
        same = a.same_brand or one_project(a.compare)
        if clashes and not a.same_brand and same:
            o += ["", "Note: these paths are directions or screens of one project (one folder, a directions/ folder, or under one "
                      "design.json or DESIGN.md), so the clash rules for unrelated products do not apply. Shared typefaces are "
                      "expected; judge the directions by how far apart the similarity puts them."]
        elif clashes and not same:
            o += [""] + clashes
        print(json.dumps({"pairs": rows, "clashes": [] if same else clashes, "one_project": same and not a.same_brand,
                          "fingerprints": dict(fps)}, indent=1) if a.json else "\n".join(o))
        return 2 if (round(worst, 2) >= 0.75 or (clashes and not same)) else 0
    if not a.paths and not a.render:
        ap.error("give a project path, --render FILE, or --compare A B")
    fp = from_render(a.render) if a.render else extract(collect(a.paths))
    near = nearest_default(fp)
    o = ["# Design fingerprint", "", md_table(["trait", "value"], describe(fp)), "", "## Nearest default looks", "",
         md_table(["default look", "match", "shared traits"], [[n, f"{s:.0%}", ", ".join(hit) or "-"] for n, s, hit in near[:4]]), ""]
    top_name, top_score, _hit = near[0]
    if top_score >= 0.75:
        o.append(f"This design is {top_score:.0%} of the way to \"{top_name}\". That is a default, not a decision: go back to the "
                 "identity (references/identity.md) and change the traits that came from habit, starting with type and ground.")
    elif top_score >= 0.55:
        o.append(f"Partly \"{top_name}\" ({top_score:.0%}). Check that each shared trait was chosen for this subject.")
    else:
        o.append("Not close to any catalogued default look.")
    ev = fp.get("evidence", {})
    if not ev.get("rendered") and ev.get("font_declarations", 0) == 0 and fp["fonts"] == ["(system)"]:
        o.append("No font-family declarations found: the design uses the framework or system default face. Choosing no typeface is "
                 "the most common tell of all.")
    worst = 0.0
    reg = registry_dir(a)
    if a.against:
        rows, clashes = [], []
        if os.path.isdir(reg):
            for f in sorted(os.listdir(reg)):
                if f.endswith(".json") and f[:-5] != (a.save or ""):
                    with open(os.path.join(reg, f), encoding="utf-8") as fh:
                        other = json.load(fh)
                    s, shared = similarity(fp, other)
                    worst = max(worst, s)
                    rows.append([f[:-5], f"{s:.0%}", "; ".join(shared) or "nothing notable"])
                    clashes += clash("this design", fp, f[:-5], other)
        o += ["", "## Against your other projects", ""]
        o += [md_table(["project", "similarity", "shared"], sorted(rows, key=lambda r: -float(r[1][:-1]))), "", verdict(worst)] if rows else \
            [f"No saved fingerprints in {reg}. Save each project once with --save NAME."]
        if clashes and not a.same_brand:
            o += [""] + clashes
            worst = max(worst, 0.75)
    if a.save:
        os.makedirs(reg, exist_ok=True)
        with open(os.path.join(reg, re.sub(r"[^A-Za-z0-9._-]+", "-", a.save) + ".json"), "w", encoding="utf-8") as fh:
            json.dump(fp, fh, indent=1)
        o += ["", f"Saved as \"{a.save}\" in {reg}."]
    print(json.dumps({"fingerprint": fp, "defaults": near, "worst_project_similarity": worst}, indent=1) if a.json else "\n".join(o))
    return 2 if (top_score >= 0.75 or round(worst, 2) >= 0.75) else 0


def one_project(paths) -> bool:
    """True when the compared paths are directions or screens of one project rather than unrelated products: files in
    one folder, anything under a directions/ folder, or a common folder (or one above it) holding design.json or DESIGN.md."""
    full = [os.path.abspath(p) for p in paths]
    if any("directions" in p.split(os.sep) for p in full):
        return True
    dirs = [p if os.path.isdir(p) else os.path.dirname(p) for p in full]
    if len(set(dirs)) == 1:
        return True
    try:
        cur = os.path.commonpath(dirs)
    except ValueError:
        return False
    stop = {os.path.expanduser("~"), os.path.dirname(os.path.expanduser("~")), os.path.abspath(os.sep)}
    while cur not in stop and cur != os.path.dirname(cur):
        if any(os.path.isfile(os.path.join(cur, m)) for m in ("design.json", "DESIGN.md")):
            return True
        cur = os.path.dirname(cur)
    return False


def clash(name_a: str, a: dict, name_b: str, b: dict) -> list:
    """Hard rules between two unrelated projects of one owner, whatever the overall score."""
    out = []
    both = shared_faces(a, b)
    if both:
        out.append(f"Clash: {name_a} and {name_b} both set type in {', '.join(sorted(both))}. Unrelated products should not share a "
                   "text or display face: choose another for the newer one from its own subject (or pass --same-brand).")
    if a.get("ground") == b.get("ground") and a.get("ground") not in ("unknown", "white") and a["accent"][0] == b["accent"][0] != "neutral":
        out.append(f"Clash: {name_a} and {name_b} share the same ground ({a['ground']}) and accent hue ({a['accent'][0]}). "
                   "Re-derive the newer one's colours from its own subject (or pass --same-brand).")
    return out


def verdict(worst: float) -> str:
    worst = round(worst, 2)
    if worst >= 0.75:
        return (f"Verdict: {worst:.0%} similar. These would be taken for the same product. Different subjects need different type, "
                "ground and accent at the least; re-derive the newer one's identity from its own subject.")
    if worst >= 0.55:
        return f"Verdict: {worst:.0%} similar. A family resemblance; fine for one brand, a problem for unrelated products."
    return f"Verdict: {worst:.0%} similar at most. Distinct."


if __name__ == "__main__":
    sys.exit(main())
