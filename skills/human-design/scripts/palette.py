#!/usr/bin/env python3
"""Rank colour combinations for a brief, show them on real components, and
write the chosen one into design.json as a role palette.

Usage:
  python3 palette.py --domains                                   # the domain presets
  python3 palette.py --domain dev-tools --mood exact,warm --place dim
  python3 palette.py --brief "a language-learning app for adults"  # guess the domain from words
  python3 palette.py --show figma-36                             # one combination, analysed
  python3 palette.py --board board.html --domain food --mood cosy # top candidates on UI pieces, light and dark
  python3 palette.py --board board.html --ids figma-36,hd-grid,figma-11
  python3 palette.py --apply figma-36 design.json [--rotate 12] [--dark-first]
  python3 palette.py --catalogue > references/combinations.md

The library is references/data/combinations.json (Figma's 100 combinations,
analysed, plus this skill's own for thin domains) and the presets are
references/data/domains.json. A domain preset keeps the category's convention
(what users rely on) and names its habit (what to question). The ranking also
reads the owner's saved fingerprints (~/.human-design/fingerprints) and pushes
down any combination whose primary hue family another project already uses.

The shortlist is a starting point, not a palette: adapt the chosen combination
from the subject's world (references/color.md, section 1), then generate tokens.

Standard library only. No network access.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from design_lib import (chroma_profile, classify_harmony, hue_diff, hue_name, is_chromatic, md_table, mean_hue,  # noqa: E402
                        parse_color, srgb_to_oklch)

DATA = os.path.join(HERE, "..", "references", "data")
BOARD = os.path.join(HERE, "..", "assets", "palette-board.template.html")

# Words people use in a brief, mapped to the tags in the library.
SYNONYMS = {
    "exact": "technical", "precise": "technical", "engineered": "technical", "technical": "technical", "nerdy": "technical",
    "trust": "trustworthy", "trusted": "trustworthy", "reliable": "trustworthy", "safe": "trustworthy", "steady": "trustworthy",
    "calm": "calm", "quiet": "calm", "peaceful": "calm", "relaxed": "calm", "gentle": "soft", "soft": "soft", "tender": "soft",
    "warm": "warm", "cosy": "cosy", "cozy": "cosy", "homely": "cosy", "friendly": "friendly", "kind": "friendly", "human": "friendly",
    "approachable": "friendly", "welcoming": "friendly", "playful": "playful", "fun": "playful", "witty": "playful", "cheeky": "playful",
    "cheerful": "cheerful", "happy": "cheerful", "sunny": "cheerful", "optimistic": "cheerful", "bold": "bold", "loud": "bold",
    "confident": "bold", "striking": "bold", "energetic": "energetic", "fast": "energetic", "dynamic": "energetic", "lively": "energetic",
    "serious": "serious", "professional": "serious", "sober": "serious", "formal": "serious", "elegant": "elegant", "refined": "elegant",
    "premium": "luxurious", "luxurious": "luxurious", "luxury": "luxurious", "rich": "luxurious", "expensive": "luxurious",
    "natural": "natural", "organic": "organic", "earthy": "earthy", "rustic": "earthy", "grounded": "earthy", "fresh": "fresh",
    "clean": "fresh", "crisp": "fresh", "clinical": "clinical", "sterile": "clinical", "minimal": "minimal", "plain": "minimal",
    "restrained": "minimal", "dreamy": "dreamy", "romantic": "romantic", "retro": "retro", "vintage": "retro", "nostalgic": "retro",
    "dramatic": "dramatic", "moody": "dramatic", "dark": "nocturnal", "night": "nocturnal", "nocturnal": "nocturnal",
    "futuristic": "futuristic", "modern": None, "young": "youthful", "youthful": "youthful", "crafted": "crafted",
    "handmade": "artisanal", "artisan": "artisanal", "artisanal": "artisanal", "tasty": "appetising", "appetising": "appetising",
    "delicious": "appetising", "urban": "urban", "industrial": "industrial", "urgent": "urgent", "sporty": "sporty",
    "athletic": "sporty", "tropical": "tropical", "festive": "festive", "creative": "creative", "artistic": "creative",
    "cool": "cool", "honest": "crafted", "careful": "crafted", "encouraging": "friendly", "grown-up": "elegant",
    "adult": "elegant", "mature": "elegant", "sophisticated": "elegant", "childish": "youthful", "cartoon": "playful",
    "corporate": "serious", "cute": "playful", "neon": "futuristic", "generous": "cosy", "exactness": "technical",
}
PLACES = {
    "dim": "dark grounds suit a dim room or night use", "night": "dark grounds suit a dim room or night use",
    "studio": "dark grounds suit a dim room or night use", "bright": "light, high-contrast grounds hold up in daylight",
    "outdoor": "light, high-contrast grounds hold up in daylight", "shop": "light, high-contrast grounds hold up in daylight",
    "desk": "all-day use wants moderate chroma, not neon", "office": "all-day use wants moderate chroma, not neon",
    "all-day": "all-day use wants moderate chroma, not neon", "phone": "", "mobile": "",
}


# ----------------------------------------------------------------- data
def load(path: str = DATA):
    with open(os.path.join(path, "combinations.json"), encoding="utf-8") as fh:
        combos = json.load(fh)["combinations"]
    with open(os.path.join(path, "domains.json"), encoding="utf-8") as fh:
        domains = json.load(fh)["domains"]
    return {c["id"]: c for c in combos}, {d["id"]: d for d in domains}


def lch_of(hexv: str):
    col = parse_color(hexv)
    L, c, h = srgb_to_oklch(*col[:3])
    return round(L, 3), round(c, 4), round(h, 1)


def analyse(combo: dict) -> dict:
    """Harmony, colourfulness, temperature, ground options and the roles for light and dark."""
    lch = [lch_of(h) for h in combo["colours"]]
    harmony, hues, note = classify_harmony([(L, c, h, 1.0) for L, c, h in lch])
    prof = chroma_profile(lch)
    chrom = [(h, c) for L, c, h in lch if is_chromatic(L, c)]
    if chrom:
        mh = mean_hue(chrom)
        warm = sum(c for h, c in chrom if h < 110 or h >= 330)
        cool = sum(c for h, c in chrom if 150 <= h < 300)
        temp = "warm" if warm > cool * 1.5 else "cool" if cool > warm * 1.5 else "mixed"
    else:
        mh, temp = None, "neutral"
    tags = list(combo.get("tags", []))
    tags += [t for t in (temp if temp in ("warm", "cool") else None,
                         "bold" if prof["level"] in ("rich", "neon") else None,
                         "soft" if sum(1 for L, c, _h in lch if L >= 0.8 and 0.03 <= c <= 0.14) >= 3 else None) if t and t not in tags]
    roles_light = derive_roles(lch, dark_first=False)
    roles_dark = derive_roles(lch, dark_first=True)
    return {"lch": lch, "harmony": harmony, "hues": hues, "harmony_note": note, "profile": prof, "temperature": temp,
            "mean_hue": mh, "has_light": any(L >= 0.9 for L, _c, _h in lch), "has_dark": any(L <= 0.25 for L, _c, _h in lch),
            "tags": tags, "roles": roles_light, "roles_dark_first": roles_dark,
            "primary_family": hue_name(roles_light["primary"]["hue"], roles_light["primary"]["chroma"], roles_light["primary"]["lightness"])}


def _r(L, c, h, **extra):
    d = {"hue": round(h % 360, 1), "chroma": round(c, 3), "lightness": round(L, 3)}
    d.update(extra)
    return d


def derive_roles(lch, dark_first: bool = False, rotate: float = 0.0) -> dict:
    """Map a combination onto roles: ground, ink, primary, secondary, highlight (and surface when the set has a second
    pale tint). Colours keep their hue and most of their chroma; lightness is moved only as far as a role needs."""
    cols = [(L, c, (h + rotate) % 360) for L, c, h in lch]
    used = set()
    chromatic = [i for i, (L, c, _h) in enumerate(cols) if is_chromatic(L, c, 0.05)]
    # primary: the strongest colour that can be a fill for an action
    cand = [i for i in chromatic if 0.25 <= cols[i][0] <= 0.88] or chromatic or list(range(len(cols)))
    p = max(cand, key=lambda i: cols[i][1] - abs(cols[i][0] - 0.56) * 0.25)
    used.add(p)
    pL, pc, ph = cols[p]
    out = {"primary": _r(min(0.82, max(0.32, pL)), pc, ph)}
    lights = sorted((i for i, (L, c, _h) in enumerate(cols) if L >= 0.88 and i not in used), key=lambda i: -cols[i][0])
    darks = sorted((i for i, (L, _c, _h) in enumerate(cols) if L <= 0.42 and i not in used), key=lambda i: cols[i][0])
    if dark_first and darks and cols[darks[0]][0] <= 0.3:
        d = darks[0]
        used.add(d)
        L, c, h = cols[d]
        hue = h if c >= 0.006 else ph
        out["ground"] = _r(0.975, min(max(c, 0.006), 0.02), hue, lightness_dark=round(min(0.24, max(0.13, L)), 3),
                           chroma_dark=round(min(c, 0.03), 3))
    elif lights:
        g = lights[0]
        used.add(g)
        L, c, h = cols[g]
        hue = h if c >= 0.006 else ph
        dk = [cols[i] for i in darks if cols[i][0] <= 0.25]
        out["ground"] = _r(min(0.99, max(0.955, L)), min(c, 0.035), hue, lightness_dark=round(min(0.24, max(0.15, dk[0][0])), 3) if dk else 0.2,
                           chroma_dark=round(min(dk[0][1], 0.03), 3) if dk else round(min(c, 0.02), 3))
    else:
        out["ground"] = _r(0.978, 0.012, ph, lightness_dark=0.2, chroma_dark=0.015, derived=True)
    inks = [i for i in darks if i not in used]
    if inks:
        L, c, h = cols[inks[0]]
        used.add(inks[0])
        out["ink"] = _r(min(L, 0.26), min(c, 0.06), h if c >= 0.006 else out["ground"]["hue"])
    else:
        out["ink"] = _r(0.21, 0.02, out["ground"]["hue"], derived=True)
    rest = [i for i in chromatic if i not in used]
    sec = [i for i in rest if hue_diff(cols[i][2], ph) >= 30]
    if sec:
        s = max(sec, key=lambda i: cols[i][1])
        used.add(s)
        L, c, h = cols[s]
        out["secondary"] = _r(min(0.85, max(0.3, L)), c, h)
    taken_hues = [ph] + ([out["secondary"]["hue"]] if "secondary" in out else [])
    rest = [i for i in chromatic if i not in used and all(hue_diff(cols[i][2], t) >= 25 for t in taken_hues)]
    if rest:
        hl = max(rest, key=lambda i: cols[i][1])
        used.add(hl)
        L, c, h = cols[hl]
        out["highlight"] = _r(min(0.92, max(0.3, L)), c, h)
    tints = [i for i, (L, c, _h) in enumerate(cols) if i not in used and 0.86 <= L < 0.97 and 0.02 <= c <= 0.1]
    if tints and "highlight" in out:
        L, c, h = cols[tints[0]]
        out["surface"] = _r(min(0.97, L), min(c, 0.05), h)
    return out


# ----------------------------------------------------------------- ranking
def brief_tags(words):
    tags, unknown = [], []
    for w in words:
        w = w.strip().lower()
        if not w:
            continue
        t = SYNONYMS.get(w, "?")
        if t == "?":
            unknown.append(w)
        elif t and t not in tags:
            tags.append(t)
    return tags, unknown


def guess_domain(text: str, domains: dict):
    text = " " + re.sub(r"[^a-z0-9 ]+", " ", text.lower()) + " "
    scored = []
    for d in domains.values():
        hits = [k for k in d["keywords"] if f" {k} " in text or (len(k) > 4 and k in text)]
        if hits:
            scored.append((len(hits), d["id"], hits))
    return sorted(scored, reverse=True)


def taken_families(registry: str):
    out = {}
    if registry and os.path.isdir(registry):
        for f in sorted(os.listdir(registry)):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(registry, f), encoding="utf-8") as fh:
                        fp = json.load(fh)
                except (OSError, ValueError):
                    continue
                acc = (fp.get("accent") or ["neutral"])[0]
                if acc != "neutral":
                    out.setdefault(acc, []).append(f[:-5])
    return out


def score(combo, an, domain, moods, place, taken, avoid=()):
    s, why = 0.0, []
    if domain:
        pref = domain["prefer"]
        if combo["id"] in domain["candidates"]:
            s += 2.0
            why.append(f"listed for {domain['name']}")
        shared = [t for t in an["tags"] if t in pref.get("moods", [])]
        if shared:
            s += min(3, len(shared)) * 1.0
            why.append("fits " + ", ".join(shared[:3]))
        bad = [t for t in an["tags"] if t in pref.get("avoid", [])]
        if bad:
            s -= 1.5 * len(bad)
            why.append("but reads " + ", ".join(bad))
        if an["profile"]["level"] in pref.get("chroma", []):
            s += 1.0
        else:
            s -= 1.0
            why.append(f"{an['profile']['level']} chroma is unusual here")
        t = pref.get("temperature", "either")
        if t in ("warm", "cool"):
            s += 0.7 if an["temperature"] == t else -0.5 if an["temperature"] in ("warm", "cool") else 0
        if pref.get("dark_first"):
            s += 1.0 if an["has_dark"] else -0.5
        if an["primary_family"] in domain.get("cliche", []):
            s -= 0.8
            why.append(f"{an['primary_family']} is the category habit")
    for m in moods:
        if m in an["tags"]:
            s += 1.5
            why.append(f"says {m}")
    for m in avoid:
        if m in an["tags"]:
            s -= 2.5
            why.append(f"reads {m}, which the brief refuses")
    if place in ("dim", "night", "studio"):
        s += 1.0 if an["has_dark"] else -0.3
    elif place in ("bright", "outdoor", "shop"):
        s += 0.5 if an["profile"]["lightness_span"] >= 0.45 else -0.3
    elif place in ("desk", "office", "all-day"):
        s += -1.0 if an["profile"]["level"] == "neon" else 0.3
    if an["primary_family"] in taken:
        s -= 3.0
        why.append(f"primary {an['primary_family']} is taken by {', '.join(taken[an['primary_family']])}")
    return round(s, 2), why


def shortlist(combos, domain, moods, place, taken, n=6, avoid=()):
    rows = []
    for c in combos.values():
        an = analyse(c)
        sc, why = score(c, an, domain, moods, place, taken, avoid)
        rows.append((sc, c, an, why))
    rows.sort(key=lambda r: -r[0])
    picked, seen = [], set()
    for r in rows:  # the first three differ in harmony, so the three directions start apart
        if len(picked) >= 3:
            break
        if r[2]["harmony"] not in seen:
            picked.append(r)
            seen.add(r[2]["harmony"])
    for r in rows:
        if len(picked) >= n:
            break
        if r not in picked:
            picked.append(r)
    return picked


# ----------------------------------------------------------------- output
def swatch_line(combo):
    return " ".join(combo["colours"])


def describe(combo, an) -> str:
    o = [f"# {combo['name']} ({combo['id']})", ""]
    src = combo.get("url") or "human-design (inference)"
    o += [f"Source: {src}", f"Purpose: {combo['purpose']}" if combo.get("purpose") else "", ""]
    rows = [[h, f"{L:.2f}", f"{c:.3f}", f"{hh:.0f}", hue_name(hh, c, L) if is_chromatic(L, c) else "neutral"]
            for h, (L, c, hh) in zip(combo["colours"], an["lch"])]
    o += [md_table(["colour", "L", "C", "H", "reads as"], rows), ""]
    o += [f"Harmony: {an['harmony']} ({an['harmony_note']}).", f"Colourfulness: {an['profile']['level']}; lightness span {an['profile']['lightness_span']}.",
          f"Temperature: {an['temperature']}. Tags: {', '.join(an['tags'])}.", "",
          "## Roles (light first)", "", md_table(["role", "hue", "chroma", "lightness", "note"],
                                                   [[k, v["hue"], v["chroma"], v["lightness"], "derived" if v.get("derived") else ""]
                                                    for k, v in an["roles"].items()]), "",
          "## Roles (dark first)", "", md_table(["role", "hue", "chroma", "lightness", "dark ground"],
                                                  [[k, v["hue"], v["chroma"], v["lightness"], v.get("lightness_dark", "")]
                                                   for k, v in an["roles_dark_first"].items()])]
    if combo.get("note"):
        o += ["", "Note: " + combo["note"]]
    return "\n".join(x for x in o if x is not None)


def apply(combo, an, design_path, rotate=0.0, dark_first=False):
    roles = derive_roles(an["lch"], dark_first=dark_first, rotate=rotate)
    for v in roles.values():
        v.pop("derived", None)
    with open(design_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    col = spec.setdefault("color", {})
    for old in ("neutral", "accent", "second", "ink"):
        col.pop(old, None)
    harmony = classify_harmony([(v["lightness"], v["chroma"], v["hue"], 1.0) for k, v in roles.items() if k != "ink"])[0]
    col["palette"] = {"harmony": harmony,
                      "source": f"{combo['id']} {combo['name']}" + (f", hues turned {rotate:+g} degrees" if rotate else "") +
                                ". REPLACE with what in the subject moved it",
                      **roles}
    if dark_first:
        modes = col.get("modes") or ["dark", "light"]
        col["modes"] = ["dark"] + [m for m in modes if m != "dark"]
    with open(design_path, "w", encoding="utf-8") as fh:
        json.dump(spec, fh, indent=2, ensure_ascii=False)
    return roles


def board(entries, out_path, title, domain=None, moods=(), dark_first=False):
    import tokens  # same folder
    with open(BOARD, encoding="utf-8") as fh:
        tpl = fh.read()
    cards = []
    for i, (sc, combo, an, why) in enumerate(entries):
        roles = an["roles_dark_first"] if dark_first else an["roles"]
        spec = {"color": {"palette": {k: {kk: vv for kk, vv in v.items() if kk != "derived"} for k, v in roles.items()},
                          "semantic": {"good": 150, "warn": 75, "bad": 27, "info": 240}, "chart": 6}}
        spec = tokens.normalise(spec)
        panes = []
        for mode in (("dark", "light") if dark_first else ("light", "dark")):
            r = tokens.roles(spec, mode)
            style = ";".join(f"--{k}:{v['hex']}" for k, v in r.items())
            panes.append(PANE.format(mode=mode, style=style, name=html.escape(combo["name"]),
                                     hl="highlight" in r, chips=CHIPS, bars=bars(r)))
        src = combo.get("url")
        link = f'<a href="{html.escape(src)}">Figma</a>' if src else "this skill's own (inference)"
        sw = "".join(f'<span class="sw" style="background:{h}" title="{h}"></span>' for h in combo["colours"])
        cards.append(CARD.format(n=i + 1, id=html.escape(combo["id"]), name=html.escape(combo["name"]), link=link,
                                 harmony=html.escape(an["harmony"]), level=an["profile"]["level"], temp=an["temperature"],
                                 why=html.escape("; ".join(why[:4]) or "-"), score=sc, swatches=sw, panes="".join(panes)))
    sub = []
    if domain:
        sub.append(f"{domain['name']}. Keep: {domain['convention']} Question: {domain['habit']} Twist: {domain['twist']}")
    if moods:
        sub.append("Brief words: " + ", ".join(moods) + ".")
    doc = (tpl.replace("{{TITLE}}", html.escape(title)).replace("{{SUBTITLE}}", html.escape(" ".join(sub) or "Candidates on real components."))
           .replace("<!--CARDS-->", "\n".join(cards)))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(doc)


def bars(r):
    hs = [62, 88, 45, 74, 30, 56]
    return "".join(f'<span style="height:{h}%;background:var(--chart-{i + 1})"></span>' for i, h in enumerate(hs) if f"chart-{i + 1}" in r)


CHIPS = ('<span class="chip" style="color:var(--good);background:var(--good-tint)">Paid</span>'
         '<span class="chip" style="color:var(--warn);background:var(--warn-tint)">Due soon</span>'
         '<span class="chip" style="color:var(--bad);background:var(--bad-tint)">Failed</span>'
         '<span class="chip" style="color:var(--info);background:var(--info-tint)">Draft</span>')

PANE = """<div class="pane" data-mode="{mode}" style="{style}">
  <div class="bar"><b>{name}</b><span class="nav"><span class="cur">Overview</span><span>Orders</span><span>Settings</span></span></div>
  <div class="body">
    <h3>Twelve orders need you today</h3>
    <p>Three are late. <a href="#">See the late ones</a> or work down the list.</p>
    <div class="row"><button class="primary">Ship 12 orders</button><button class="ghost">Export</button></div>
    <label class="field"><span>Search orders</span><input value="Ferreira" aria-label="Search orders"></label>
    <div class="card"><span class="tag">New</span><b>Second colour at work</b><span class="muted">secondary marks the filter, highlight marks what is new</span>
      <span class="sec">Filter: this week</span></div>
    <div class="chips">{chips}</div>
    <div class="chart" aria-hidden="true">{bars}</div>
  </div>
</div>"""

CARD = """<section class="cand" id="{id}">
  <header><span class="num">{n}</span><div><h2>{name}</h2><p class="meta">{id} &middot; {harmony} &middot; {level} &middot; {temp} &middot; {link}</p>
  <p class="why">{why} (score {score})</p></div><div class="sws" aria-label="the combination as published">{swatches}</div></header>
  <div class="panes">{panes}</div>
</section>"""


def catalogue(combos, domains) -> str:
    where = {}
    for d in domains.values():
        for cid in d["candidates"]:
            where.setdefault(cid, []).append(d["id"])
    o = ["# Colour combinations: catalogue", "",
         "Generated by `python3 scripts/palette.py --catalogue` from `references/data/combinations.json`. Do not edit by hand.",
         "figma-* are the combinations at figma.com/resource-library/color-combinations (hex codes as printed on Figma's palette images; "
         "names and groups are Figma's, the tags are this skill's reading). hd-* are this skill's own (inference).", "",
         "Read `color-combinations.md` for how to use them. Harmony, chroma and temperature are computed.", ""]
    groups = {}
    for c in combos.values():
        groups.setdefault(c["group"], []).append(c)
    for g, items in groups.items():
        rows = []
        for c in items:
            an = analyse(c)
            rows.append([c["id"], c["name"], " ".join(f"`{h}`" for h in c["colours"]), an["harmony"], an["profile"]["level"],
                         an["temperature"], ", ".join(c.get("tags", [])), ", ".join(where.get(c["id"], [])) or "-"])
        o += [f"## {g.title()}", "", md_table(["id", "name", "colours", "harmony", "chroma", "temperature", "tags", "listed for"], rows), ""]
    o += ["## Domains", "", md_table(["id", "domain", "keep", "question", "twist"],
                                     [[d["id"], d["name"], d["convention"], d["habit"], d["twist"]] for d in domains.values()]), ""]
    return "\n".join(o)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--domains", action="store_true", help="list the domain presets")
    ap.add_argument("--domain", help="domain preset id (see --domains)")
    ap.add_argument("--brief", help="a sentence about the product; used to guess the domain when --domain is not given")
    ap.add_argument("--mood", default="", help="comma-separated words from the brief, such as exact,warm,playful")
    ap.add_argument("--avoid", default="", help="comma-separated words the brief refuses, such as childish,corporate")
    ap.add_argument("--place", default="", help="where it is used: dim, night, studio, bright, outdoor, shop, desk, office, all-day")
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--show", metavar="ID", help="analyse one combination")
    ap.add_argument("--ids", help="comma-separated combination ids for --board, instead of a ranking")
    ap.add_argument("--board", metavar="HTML", help="write a palette board of the shortlist (or --ids)")
    ap.add_argument("--apply", nargs=2, metavar=("ID", "DESIGN_JSON"), help="write a combination's roles into design.json as color.palette")
    ap.add_argument("--rotate", type=float, default=0.0, help="turn every hue by this many degrees when applying (keeps the relations)")
    ap.add_argument("--dark-first", action="store_true", help="derive roles for a product whose main mode is dark")
    ap.add_argument("--registry", default=os.path.join(os.path.expanduser("~"), ".human-design", "fingerprints"),
                    help="saved fingerprints, whose primary hues count as taken")
    ap.add_argument("--catalogue", action="store_true", help="print the catalogue as Markdown")
    ap.add_argument("--data", default=DATA, help=argparse.SUPPRESS)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    combos, domains = load(a.data)
    if a.catalogue:
        print(catalogue(combos, domains))
        return 0
    if a.domains:
        print(md_table(["id", "domain", "keep", "question"], [[d["id"], d["name"], d["convention"], d["habit"]] for d in domains.values()]))
        return 0
    if a.show:
        if a.show not in combos:
            sys.exit(f"No combination '{a.show}'. Ids look like figma-36 or hd-grid; --catalogue lists them.")
        an = analyse(combos[a.show])
        print(json.dumps({"combination": combos[a.show], "analysis": an}, indent=1) if a.json else describe(combos[a.show], an))
        return 0
    if a.apply:
        cid, path = a.apply
        if cid not in combos:
            sys.exit(f"No combination '{cid}'.")
        if not os.path.exists(path):
            sys.exit(f"{path} does not exist. Create it with python3 scripts/tokens.py --init {path}.")
        roles = apply(combos[cid], analyse(combos[cid]), path, a.rotate, a.dark_first)
        print(f"Wrote color.palette from {cid} into {path}:\n")
        print(md_table(["role", "hue", "chroma", "lightness"], [[k, v["hue"], v["chroma"], v["lightness"]] for k, v in roles.items()]))
        print("\nNow adapt it: move hues toward the colours of the subject's world, write the reason in palette.source, then run "
              f"python3 scripts/tokens.py {path}.")
        return 0
    domain = None
    notes = []
    if a.domain:
        if a.domain not in domains:
            sys.exit(f"No domain '{a.domain}'. Known: {', '.join(domains)}.")
        domain = domains[a.domain]
    elif a.brief:
        g = guess_domain(a.brief, domains)
        if g:
            domain = domains[g[0][1]]
            notes.append(f"Domain guessed from the brief: {domain['id']} (words: {', '.join(g[0][2])})." +
                         (f" Also possible: {', '.join(x[1] for x in g[1:3])}." if len(g) > 1 else "") + " Pass --domain to choose.")
        else:
            notes.append("No domain matched the brief; ranking on mood and place only. Pass --domain (see --domains).")
    moods, unknown = brief_tags(a.mood.split(","))
    avoid, unknown_avoid = brief_tags(a.avoid.split(","))
    unknown += unknown_avoid
    if unknown:
        notes.append("Words with no colour meaning here: " + ", ".join(unknown) + ".")
    place = a.place.strip().lower()
    taken = taken_families(a.registry)
    if a.ids:
        ids = [x.strip() for x in a.ids.split(",") if x.strip()]
        missing = [x for x in ids if x not in combos]
        if missing:
            sys.exit("Unknown ids: " + ", ".join(missing))
        picked = []
        for x in ids:
            an = analyse(combos[x])
            sc, why = score(combos[x], an, domain, moods, place, taken, avoid)
            picked.append((sc, combos[x], an, why))
    else:
        picked = shortlist(combos, domain, moods, place, taken, a.top, avoid)
    dark_first = a.dark_first or bool(domain and domain["prefer"].get("dark_first")) or place in ("dim", "night", "studio")
    if a.board:
        title = f"Palette board: {domain['name']}" if domain else "Palette board"
        board(picked, a.board, title, domain, moods, dark_first)
        notes.append(f"Wrote {a.board}: {len(picked)} candidates on components, {'dark first' if dark_first else 'light first'}.")
    if a.json:
        print(json.dumps({"domain": domain, "moods": moods, "place": place, "taken": taken, "notes": notes,
                          "shortlist": [{"score": sc, "id": c["id"], "name": c["name"], "colours": c["colours"], "harmony": an["harmony"],
                                         "chroma": an["profile"]["level"], "temperature": an["temperature"], "why": why,
                                         "roles": an["roles_dark_first"] if dark_first else an["roles"]} for sc, c, an, why in picked]}, indent=1))
        return 0
    o = []
    if domain:
        o += [f"# {domain['name']}", "", f"Keep (users rely on it): {domain['convention']}", f"Question (category habit): {domain['habit']}",
              f"Twist: {domain['twist']}", "Evidence: " + "; ".join(domain["evidence"]), ""]
    if place in PLACES and PLACES[place]:
        o.append(f"Place: {PLACES[place]}.")
    if taken:
        o.append("Primary hues already used by your projects: " + "; ".join(f"{k} ({', '.join(v)})" for k, v in taken.items()) + ".")
    o += notes + ["", "## Shortlist", "",
                  md_table(["#", "id", "name", "colours", "harmony", "chroma", "temperature", "primary", "score", "why"],
                           [[i + 1, c["id"], c["name"], swatch_line(c), an["harmony"], an["profile"]["level"], an["temperature"],
                             an["primary_family"], sc, "; ".join(why[:4]) or "-"] for i, (sc, c, an, why) in enumerate(picked)]), "",
                  "The first three differ in harmony: give one to each direction. Then adapt hues from the subject's world "
                  "(palette.py --apply ID design.json, then edit), and check with tokens.py."]
    print("\n".join(o))
    return 0


if __name__ == "__main__":
    sys.exit(main())
