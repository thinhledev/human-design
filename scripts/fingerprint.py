#!/usr/bin/env python3
"""Fingerprint a design and compare it with other projects and with the default
looks that AI tools converge on.

Usage:
  python3 fingerprint.py src/                         # this project's fingerprint and its nearest default look
  python3 fingerprint.py src/ --save acme             # remember it under a name
  python3 fingerprint.py src/ --against               # compare with every saved project
  python3 fingerprint.py --compare projA/src projB/src [projC/src]
  python3 fingerprint.py mockup.html --json

The fingerprint is what makes one interface recognisable next to another:
type families and how they are used, the accent hue and the temperature of the
neutrals, the ground (white, cream, grey, near-black), corner radius, shadow
style, type-scale ratio, how much is centred, the column habit, gradients and
glass. Two projects by a designer on autopilot share most of it.

Saved fingerprints live in ~/.human-design/fingerprints (or --registry DIR) so
that a design made in one repository can be checked against the others. Only
the fingerprint is stored: no source code, no content.

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
from design_lib import (class_tokens, collect, declarations, first_family, hue_name, length_px, md_table,  # noqa: E402
                        parse_color, srgb_to_oklch)

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
        "ground": ["cream"], "neutral": ["warm"], "accent": ["orange", "red", "green", "amber"], "radius": ["0", "1-3", "4-6"],
        "shadow": ["none", "hairline"]},
    "dark with a neon accent": {
        "fonts": ["inter", "geist", "space grotesk", "jetbrains mono", "geist mono", "(system)"], "ground": ["near-black"],
        "accent": ["lime", "green", "cyan", "teal", "orange", "red"], "radius": ["0", "1-3", "4-6", "8-12"], "shadow": ["none", "glow"]},
    "glass and glow": {
        "fonts": ["inter", "sf pro display", "(system)", "plus jakarta sans", "outfit", "sora"], "ground": ["near-black", "white"],
        "accent": ["blue", "purple", "indigo", "cyan", "pink"], "radius": ["16+", "pill"], "glass": [True], "gradient": [True]},
    "techno mono (space grotesk and mono labels)": {
        "fonts": ["space grotesk", "space mono", "jetbrains mono", "ibm plex mono", "geist mono", "dm mono"],
        "ground": ["white", "cream", "near-black"], "radius": ["0", "1-3"], "shadow": ["none", "hard"], "mono_labels": [True]},
}
# Traits a design must share before it can be called that look; without them the score is capped.
MUST = {"framework default (shadcn or Tailwind starter)": ["fonts"], "purple gradient SaaS": ["gradient", "accent"],
        "cream editorial (second-generation default)": ["ground", "fonts"], "dark with a neon accent": ["ground", "accent"],
        "glass and glow": ["glass"], "techno mono (space grotesk and mono labels)": ["fonts"]}
WEIGHTS = {"fonts": 0.30, "accent": 0.17, "ground": 0.12, "neutral": 0.06, "radius": 0.10, "shadow": 0.06, "ratio": 0.05,
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
    if L > 0.985 and c < 0.004:
        return "white"
    if c >= 0.006 and 40 <= h <= 110:
        return "cream"
    return "tinted" if c >= 0.012 else ("white" if L > 0.965 else "grey")


def extract(sources) -> dict:
    fams, display, body = Counter(), Counter(), Counter()
    hues, chroma_hues, bgs, neutral_tint = Counter(), Counter(), Counter(), Counter()
    radii, shadows, sizes = Counter(), Counter(), Counter()
    centred = text_align = gradient = glass = cols3 = mono_small = 0
    tw = Counter()
    for src in sources:
        for sel, prop, val, _line, _at in declarations(src):
            low = val.lower()
            if prop in ("font-family", "--font-sans", "--font-display", "--font-serif", "--font-heading", "--font-body", "--font-text",
                        "--font-mono") or (prop == "font" and "," in val):
                fam = first_family(val.split("/")[-1] if prop == "font" else val)
                fam = re.sub(r"^\d+(px|rem|em)\s+", "", fam)
                if fam and fam not in GENERIC:
                    fams[fam] += 1
                    if DISPLAY_SEL.search(sel) or "display" in prop or "heading" in prop:
                        display[fam] += 2
                    if BODY_SEL.search(sel) or prop in ("--font-sans", "--font-body", "--font-text"):
                        body[fam] += 2
            for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b|(?:rgba?|hsla?|oklch|oklab)\([^)]*\)", val):
                col = parse_color(m.group(0))
                if not col or col[3] < 0.5:
                    continue
                L, c, h = srgb_to_oklch(*col[:3])
                if c >= 0.07 and 0.25 < L < 0.92:
                    chroma_hues[hue_name(h, c, L)] += 1
                elif c >= 0.004:
                    neutral_tint["warm" if (h < 115 or h > 340) else "cool"] += 1
                else:
                    neutral_tint["none"] += 1
                if prop in ("background", "background-color", "--bg", "--background", "--color-bg", "--surface", "--paper") and \
                        re.search(r"(^|[\s,])(body|html|:root|main|\.app|\.page|#root|#app)\b|^x$", sel + " ") and (L > 0.9 or L < 0.3):
                    bgs[ground_of(col)] += 3 if re.search(r"body|html|:root", sel) else 1
            if prop.endswith("radius"):
                px = length_px(low.split()[0]) if low.split() else None
                if "9999" in low or "999px" in low or low.startswith("50%") or "infinity" in low:
                    radii["pill"] += 1
                elif px is not None:
                    radii[radius_bucket(px)] += 1
            if prop == "box-shadow" and low not in ("none", "0", "unset", "inherit"):
                parts = re.sub(r"\([^)]*\)", "", low).split(",")[0].split()
                nums = [length_px(p) for p in parts if length_px(p) is not None]
                blur = nums[2] if len(nums) > 2 else 0
                if "inset" in low and len(nums) < 3:
                    continue
                if len(nums) >= 2 and blur == 0 and (abs(nums[0]) >= 2 or abs(nums[1]) >= 2):
                    shadows["hard"] += 1
                elif len(nums) >= 4 and nums[0] == 0 and nums[1] == 0 and blur == 0:
                    shadows["hairline"] += 1
                elif blur and blur >= 16 and re.search(r"#[0-9a-f]{3,8}|rgba?\(\s*(?!0[\s,]+0[\s,]+0)", low) and "0 0 " in low:
                    shadows["glow"] += 1
                else:
                    shadows["soft"] += 1
            if prop == "font-size":
                px = length_px(low)
                if px and 9 <= px <= 160:
                    sizes[round(px)] += 1
            if prop == "text-align":
                text_align += 1
                centred += low.startswith("center")
            if "gradient(" in low and prop.startswith("background"):
                gradient += 1
            if prop in ("backdrop-filter", "-webkit-backdrop-filter") and "blur" in low:
                glass += 1
            if prop == "grid-template-columns" and re.search(r"repeat\(\s*3\s*,|^(1fr\s+){2}1fr$", low):
                cols3 += 1
            if prop == "font-family" and "mono" in low and re.search(r"label|eyebrow|kicker|tag|badge|caption|meta|overline", sel, re.I):
                mono_small += 1
        for tok, _line in class_tokens(src):
            base = tok.split(":")[-1].lstrip("!-")
            tw[base] += 1
    # Tailwind classes
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
            if k in TW_RADIUS:
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
            if k in ("grid-cols-3", "md:grid-cols-3", "lg:grid-cols-3"):
                cols3 += n
            if k == "font-mono" and (tw.get("uppercase") or tw.get("tracking-widest") or tw.get("tracking-wider")):
                mono_small += 1
            if k in ("bg-white", "bg-background"):
                bgs["white"] += 1
            if re.match(r"bg-(black|zinc-9\d0|neutral-9\d0|slate-9\d0|gray-9\d0)$", k):
                bgs["near-black"] += 1
    fonts = [f for f, _n in fams.most_common(4)]
    if not fonts:
        fonts = ["(system)"]
    sz = sorted(s for s, n in sizes.items() if n >= 1)
    ratios = [b / a for a, b in zip(sz, sz[1:]) if 1.05 < b / a < 1.7]
    total_r = sum(radii.values())
    fp = {
        "fonts": fonts,
        "display": (display.most_common(1) or [(fonts[0], 0)])[0][0],
        "text": (body.most_common(1) or [(fonts[-1] if len(fonts) > 1 else fonts[0], 0)])[0][0],
        "accent": [h for h, _n in chroma_hues.most_common(2)] or ["neutral"],
        "accent_spread": len([h for h, n in chroma_hues.items() if n >= max(2, 0.12 * sum(chroma_hues.values()))]),
        "neutral": (neutral_tint.most_common(1) or [("none", 0)])[0][0],
        "ground": (bgs.most_common(1) or [("unknown", 0)])[0][0],
        "radius": (radii.most_common(1) or [("0", 0)])[0][0],
        "radius_uniform": round(radii.most_common(1)[0][1] / total_r, 2) if total_r else 0.0,
        "shadow": (shadows.most_common(1) or [("none", 0)])[0][0],
        "sizes": sz[:14],
        "ratio": round(statistics.median(ratios), 3) if ratios else None,
        "centred": bool(text_align and centred / text_align > 0.6 and centred >= 4),
        "gradient": gradient >= 2,
        "glass": glass >= 2,
        "three_columns": cols3 >= 2,
        "mono_labels": mono_small >= 2,
        "tailwind": bool(tw_used),
        "evidence": {"font_declarations": sum(fams.values()), "colours": sum(chroma_hues.values()) + sum(neutral_tint.values()),
                     "radii": total_r, "files": len(sources)},
    }
    return fp


def from_render(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        runs = json.load(fh)
    f = max(runs, key=lambda r: r.get("width", 0))
    fams = [x["name"].lower() for x in f["families"] if x["share"] > 0.02 and not x.get("generic")] or ["(system)"]
    hues = Counter()
    for hexv, share in f["textColors"]:
        col = parse_color(hexv)
        L, c, h = srgb_to_oklch(*col[:3])
        if c >= 0.07:
            hues[hue_name(h, c, L)] += share
    bg = parse_color(f["backgrounds"][0]) if f["backgrounds"] else (1, 1, 1, 1)
    rad = f["radii"][0][0] if f["radii"] else "0"
    total_r = sum(n for _k, n in f["radii"]) or 1
    sz = [round(s) for s, share in f["sizes"] if share > 0.005]
    ratios = [b / a for a, b in zip(sz, sz[1:]) if 1.05 < b / a < 1.7]
    return {"fonts": fams, "display": fams[0], "text": fams[-1], "accent": [h for h, _ in hues.most_common(2)] or ["neutral"],
            "accent_spread": len(hues), "neutral": "none", "ground": ground_of(bg),
            "radius": rad if rad == "pill" else radius_bucket(float(re.sub(r"[^0-9.]", "", rad) or 0)),
            "radius_uniform": round((f["radii"][0][1] if f["radii"] else 0) / total_r, 2),
            "shadow": "soft" if f["shadows"] else "none", "sizes": sz, "ratio": round(statistics.median(ratios), 3) if ratios else None,
            "centred": f["centeredShare"] > 0.6, "gradient": f["gradients"] >= 2 or f["gradientText"] > 0, "glass": f["backdropBlur"] >= 2,
            "three_columns": False, "mono_labels": False, "tailwind": False, "evidence": {"rendered": True}}


def similarity(a: dict, b: dict):
    """Return (score 0..1, list of shared traits) for two full fingerprints."""
    shared, score, total = [], 0.0, 0.0
    fa, fb = set(a["fonts"]), set(b["fonts"])
    total += WEIGHTS["fonts"]
    if fa & fb:
        part = len(fa & fb) / max(1, min(len(fa), len(fb)))
        score += WEIGHTS["fonts"] * part
        shared.append("typefaces: " + ", ".join(sorted(fa & fb)))
    total += WEIGHTS["accent"]
    if set(a["accent"]) & set(b["accent"]):
        score += WEIGHTS["accent"]
        shared.append("accent hue: " + ", ".join(sorted(set(a["accent"]) & set(b["accent"]))))
    for key, labelf in (("ground", "ground: {}"), ("neutral", "neutrals: {}"), ("radius", "corner radius: {}"), ("shadow", "shadows: {}")):
        total += WEIGHTS[key]
        if a[key] == b[key] and a[key] != "unknown":
            score += WEIGHTS[key]
            shared.append(labelf.format(a[key]))
    total += WEIGHTS["ratio"]
    if a.get("ratio") and b.get("ratio") and abs(a["ratio"] - b["ratio"]) <= 0.03:
        score += WEIGHTS["ratio"]
        shared.append(f"type-scale ratio about {a['ratio']}")
    for key, name in (("centred", "mostly centred text"), ("gradient", "gradient fills"), ("glass", "blurred glass"),
                      ("mono_labels", "monospace labels")):
        total += WEIGHTS[key]
        if a.get(key) == b.get(key):
            score += WEIGHTS[key]
            if a.get(key):
                shared.append(name)
    return score / total, shared


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
            elif mine in allowed:
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
            ["Neutrals", fp["neutral"]], ["Ground", fp["ground"]],
            ["Corner radius", f"{fp['radius']}px bucket" + (f", on {fp['radius_uniform']:.0%} of rounded boxes" if fp.get("radius_uniform") else "")],
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
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.compare:
        if len(a.compare) < 2:
            ap.error("--compare needs two or more paths")
        fps = [(os.path.basename(os.path.abspath(p).rstrip("/")) or p, extract(collect([p]))) for p in a.compare]
        o = ["# Fingerprint comparison", ""]
        rows, worst = [], 0.0
        for i in range(len(fps)):
            for j in range(i + 1, len(fps)):
                s, shared = similarity(fps[i][1], fps[j][1])
                worst = max(worst, s)
                rows.append([f"{fps[i][0]} vs {fps[j][0]}", f"{s:.0%}", "; ".join(shared) or "nothing notable"])
        o += [md_table(["pair", "similarity", "shared"], rows), ""]
        for name, fp in fps:
            o += [f"## {name}", "", md_table(["trait", "value"], describe(fp)), ""]
        o.append(verdict(worst))
        print(json.dumps({"pairs": rows, "fingerprints": dict(fps)}, indent=1) if a.json else "\n".join(o))
        return 2 if worst >= 0.75 else 0
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
        rows = []
        if os.path.isdir(reg):
            for f in sorted(os.listdir(reg)):
                if f.endswith(".json") and f[:-5] != (a.save or ""):
                    with open(os.path.join(reg, f), encoding="utf-8") as fh:
                        other = json.load(fh)
                    s, shared = similarity(fp, other)
                    worst = max(worst, s)
                    rows.append([f[:-5], f"{s:.0%}", "; ".join(shared) or "nothing notable"])
        o += ["", "## Against your other projects", ""]
        o += [md_table(["project", "similarity", "shared"], sorted(rows, key=lambda r: -float(r[1][:-1]))), "", verdict(worst)] if rows else \
            [f"No saved fingerprints in {reg}. Save each project once with --save NAME."]
    if a.save:
        os.makedirs(reg, exist_ok=True)
        with open(os.path.join(reg, re.sub(r"[^A-Za-z0-9._-]+", "-", a.save) + ".json"), "w", encoding="utf-8") as fh:
            json.dump(fp, fh, indent=1)
        o += ["", f"Saved as \"{a.save}\" in {reg}."]
    print(json.dumps({"fingerprint": fp, "defaults": near, "worst_project_similarity": worst}, indent=1) if a.json else "\n".join(o))
    return 2 if (top_score >= 0.75 or worst >= 0.75) else 0


def verdict(worst: float) -> str:
    if worst >= 0.75:
        return (f"Verdict: {worst:.0%} similar. These would be taken for the same product. Different subjects need different type, "
                "ground and accent at the least; re-derive the newer one's identity from its own subject.")
    if worst >= 0.55:
        return f"Verdict: {worst:.0%} similar. A family resemblance; fine for one brand, a problem for unrelated products."
    return f"Verdict: {worst:.0%} similar at most. Distinct."


if __name__ == "__main__":
    sys.exit(main())
