#!/usr/bin/env python3
"""Find the tells that make an interface read as machine-made, in source files.

Usage:
  python3 slop_check.py src/                      # HTML, CSS, JSX/TSX, Vue, Svelte, Astro, Liquid, SwiftUI, Compose
  python3 slop_check.py mockup.html --identity design.json
  python3 slop_check.py app/ --surface app --json
  python3 slop_check.py --list                    # the catalogue, to read before designing
  python3 slop_check.py src/ --ignore copy-stock-words,type-eyebrow

It reports four kinds of finding, each with file and line:
  default    what generators produce when nothing was decided (first generation):
             the framework font, indigo-to-purple gradients, three equal cards,
             emoji icons, everything centred and rounded
  reaction   what "make it not look like AI" now produces just as predictably
             (second generation): cream ground with a serif and terracotta,
             near-black with one neon, monospace labels on everything
  dead       interface with no life in it: no pressed or focus state, focus
             outlines removed, everything fades up on scroll, nothing for
             loading, empty or error
  copy       stock phrases, invented proof, placeholder people and numbers

A tell is evidence of a decision nobody made, not a banned technique. When a
choice is deliberate, record it in design.json under "deliberate" with the
reason, pass --identity design.json, and it is listed as declared, not counted.

This is the floor, not the judgement: a page with zero tells can still be
lifeless. Look at it (render_check.py) and critique it (references/critique.md).
Exit status 2 when any strong tell remains. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design_lib import (MARKUP_EXT, NATIVE_EXT, STYLE_EXT, class_tokens, collect, declarations, family_of, first_family,  # noqa: E402,F401
                        font_mentions, length_px, rel, visible_text)
from fingerprint import extract, nearest_default  # noqa: E402

DEFAULT_FONTS = {"inter", "inter variable", "inter tight", "geist", "geist sans", "geist variable", "roboto", "arial", "helvetica",
                 "helvetica neue", "segoe ui", "open sans", "system-ui", "-apple-system", "sf pro text", "sf pro display"}
FIRST_GEN_DISPLAY = {"space grotesk", "plus jakarta sans", "poppins", "outfit", "sora", "manrope", "dm sans", "montserrat",
                     "urbanist", "lexend", "satoshi", "cal sans", "clash display", "general sans"}
SECOND_GEN_DISPLAY = {"instrument serif", "playfair display", "fraunces", "cormorant", "cormorant garamond", "dm serif display",
                      "dm serif text", "libre baskerville", "newsreader", "young serif", "gloock", "bodoni moda"}
STOCK = ["elevate", "seamless", "seamlessly", "supercharge", "supercharged", "unleash", "unlock the", "unlock your", "effortless",
         "effortlessly", "revolutionize", "revolutionary", "cutting-edge", "cutting edge", "next-generation", "next generation",
         "game-changer", "game-changing", "game changer", "empower", "empowering", "streamline", "leverage", "harness the power",
         "to the next level", "all-in-one", "all in one platform", "blazing fast", "blazingly fast", "lightning fast", "lightning-fast",
         "reimagine", "reimagined", "transform your", "transform the way", "built for the modern", "the future of", "world-class",
         "best-in-class", "state-of-the-art", "robust", "delve", "tapestry", "in today's fast-paced", "take control of your",
         "designed for teams", "everything you need", "one platform", "simple, powerful", "say goodbye to", "meet your new",
         "your journey", "peace of mind", "like never before", "at your fingertips", "at scale", "scale with confidence",
         "ai-powered", "powered by ai", "intelligent insights", "actionable insights", "data-driven", "frictionless", "intuitive"]
FAKE_PROOF = [r"\btrusted by\s+(over\s+)?[\d,.]+\s*[kKmM+]", r"\bjoin\s+(over\s+)?[\d,.]+\s*[kKmM+]?\+?\s+(happy\s+)?(users|customers|teams|developers|companies|creators|people)",
              r"\b[\d,.]+\s*[kKmM]?\+\s+(happy\s+|active\s+)?(users|customers|teams|developers|companies|downloads|reviews)\b",
              r"\b(4\.[89]|5\.0)\s*(/\s*5|out of 5|stars?)\b", r"\b99\.9+%\s+uptime\b", r"\b\d{1,3}x\s+(faster|more productive|productivity|roi)\b",
              r"\b(john|jane)\s+(doe|smith)\b", r"\bsarah\s+(johnson|chen|miller|williams)\b", r"\bacme\s+(inc|corp|co)\b",
              r"\b(ceo|cto|founder|head of \w+)\s+(at|,)\s+(techcorp|acme|company|startup ?x|example)\b", r"\bas seen (in|on)\b",
              r"\bloved by\s+(thousands|millions|teams|developers)\b"]
PLACEHOLDER_HOSTS = r"(via\.placeholder\.com|placehold\.co|placeholder\.com|picsum\.photos|source\.unsplash\.com|loremflickr\.com|dummyimage\.com|placekitten\.com|i\.pravatar\.cc|ui-avatars\.com|randomuser\.me|placeholder\.svg|/api/placeholder)"
# Emoji, not text symbols: pictographs drawn in colour by default (Unicode Emoji_Presentation), or any symbol
# followed by the emoji variation selector U+FE0F. Stars, check marks, arrows and geometric shapes such as
# ☆ ★ ✓ → ▲ are typography and are not flagged.
EMOJI_PRESENTATION = ("\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\U0001F7E0-\U0001F7EB\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF"
                      "\u231A\u231B\u23E9-\u23EC\u23F0\u23F3\u25FD\u25FE\u2614\u2615\u2648-\u2653\u267F\u2693\u26A1\u26AA\u26AB"
                      "\u26BD\u26BE\u26C4\u26C5\u26CE\u26D4\u26EA\u26F2\u26F3\u26F5\u26FA\u26FD\u2705\u270A\u270B\u2728\u274C"
                      "\u274E\u2753-\u2755\u2757\u2795-\u2797\u27B0\u27BF\u2B1B\u2B1C\u2B50\u2B55")
EMOJI = re.compile("[" + EMOJI_PRESENTATION + "]\uFE0F?|[\u2190-\u21FF\u2300-\u23FF\u25A0-\u27BF\u2900-\u297F\u2B00-\u2BFF\u3030\u303D"
                   "\u3297\u3299\u00A9\u00AE\u203C\u2049\u2122\u2139]\uFE0F")
PURPLE = re.compile(r"\b(?:bg|from|via|to|text|border|ring|shadow)-(indigo|violet|purple|fuchsia)-(400|500|600|700)\b")
PURPLE_HEX = re.compile(r"#(6366f1|4f46e5|4338ca|8b5cf6|7c3aed|6d28d9|a855f7|9333ea|7e22ce|c084fc|a78bfa|818cf8|667eea|764ba2|6c63ff|5b21b6)\b", re.I)


class Doc:
    def __init__(self, sources, root):
        self.sources, self.root = sources, root
        self.markup = [s for s in sources if s.ext in MARKUP_EXT or s.ext in (".js", ".ts")]
        self.native = [s for s in sources if s.ext in NATIVE_EXT]
        self.decls = [(s, *d) for s in sources for d in declarations(s)]
        self.classes = [(s, tok, line) for s in sources for tok, line in class_tokens(s)]
        self.tw = Counter(tok.split(":")[-1].lstrip("!") for _s, tok, _l in self.classes)
        self.tw_raw = Counter(tok for _s, tok, _l in self.classes)
        self.text = {s.path: visible_text(s) for s in sources}
        self.all_text = " ".join(self.text.values())
        self.words = max(1, len(self.all_text.split()))
        self.fp = extract(sources) if sources else {}
        self.fonts = [(s.path, line, family_of(prop, val)) for s, _sel, prop, val, line, _at in self.decls if family_of(prop, val)]
        self.fonts += [(s.path, line, fam) for s in sources for fam, line, _how in font_mentions(s)]

    def find(self, pattern, exts=None, flags=re.I, limit=6, text_only=False):
        rx = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        out = []
        for s in self.sources:
            if exts and s.ext not in exts:
                continue
            hay = s.text
            for m in rx.finditer(hay):
                out.append((s.path, s.line_of(m.start()), m.group(0)[:70].replace("\n", " ")))
                if len(out) >= 200:
                    return out
        return out

    def cls(self, pattern, limit=200):
        rx = re.compile(pattern)
        return [(s.path, line, tok) for s, tok, line in self.classes if rx.search(tok)][:limit]

    def decl(self, prop_rx, val_rx=None, sel_rx=None):
        p, v, sl = re.compile(prop_rx, re.I), re.compile(val_rx, re.I) if val_rx else None, re.compile(sel_rx, re.I) if sel_rx else None
        return [(s.path, line, f"{sel} {{ {prop}: {val[:50]} }}") for s, sel, prop, val, line, _at in self.decls
                if p.fullmatch(prop) and (not v or v.search(val)) and (not sl or sl.search(sel))]


TELLS = []


def tell(tid, kind, strength, title, fix):
    def wrap(fn):
        TELLS.append({"id": tid, "kind": kind, "strength": strength, "title": title, "fix": fix, "fn": fn})
        return fn
    return wrap


# ------------------------------------------------------------------ type
@tell("type-default-face", "default", "strong", "The typeface is the framework or system default (Inter, Geist, Roboto, system-ui) or none was chosen",
      "Choose text and display faces for this subject and record why in DESIGN.md (references/typography.md).")
def _(d):
    skip = ("inherit", "serif", "sans-serif", "monospace", "ui-monospace", "ui-sans-serif", "ui-serif", "")
    named = [f for f in d.fonts if f[2] not in skip]
    custom = [f for f in named if f[2] not in DEFAULT_FONTS and "mono" not in f[2]]
    if custom:
        return []
    if named:
        return [(p, l, f"typeface: {n}") for p, l, n in named[:4]]
    if d.markup and (d.tw.get("font-sans") or sum(d.tw.values()) > 40 or d.decls):
        s = d.markup[0]
        return [(s.path, 1, "no typeface chosen anywhere: the browser or framework default is the design")]
    return []


@tell("type-first-gen-display", "default", "weak", "Display face from the short list every generator reaches for (Space Grotesk, Plus Jakarta Sans, Poppins, Outfit, Sora, Manrope)",
      "Keep it only if the brief gives a reason; otherwise pick from the subject's world (references/typography.md).")
def _(d):
    return [(p, l, f"typeface: {n}") for p, l, n in d.fonts if n in FIRST_GEN_DISPLAY][:4]


@tell("type-second-gen-display", "reaction", "weak", "Serif display face that anti-AI prompts now default to (Instrument Serif, Playfair Display, Fraunces, Cormorant)",
      "A serif is not a personality. Keep it only when the subject calls for it and the rest of the system is not the cream editorial default.")
def _(d):
    return [(p, l, f"typeface: {n}") for p, l, n in d.fonts if n in SECOND_GEN_DISPLAY][:4]


@tell("type-gradient-text", "default", "strong", "Gradient-filled headline text", "Set headlines in a solid colour from the palette; let size, weight and the typeface carry emphasis.")
def _(d):
    return (d.decl(r"(-webkit-)?background-clip", r"\btext\b") + d.cls(r"^(\w+:)*bg-clip-text$"))[:6]


@tell("type-italic-accent-word", "reaction", "weak", "One italic serif word dropped into a sans headline",
      "Emphasis by switching typeface mid-headline is the current tell. Let the sentence carry the emphasis.")
def _(d):
    return d.find(r"<h[12][^>]*>(?:(?!</h[12]>).){0,160}<(?:em|i|span)[^>]*(?:class(?:Name)?=[\"'{`][^\"'`>]*(?:italic|font-serif)[^\"'`>]*[\"'`}])?[^>]*>\s*[\w'-]+(?:\s+[\w'-]+){0,2}\s*</(?:em|i|span)>",
                  flags=re.I | re.S)[:3] if d.find(r"<h[12][^>]*>(?:(?!</h[12]>).){0,160}<(?:em|i)\b|<h[12][^>]*>(?:(?!</h[12]>).){0,160}class(?:Name)?=[\"'{`][^\"'`>]*\b(?:italic|font-serif)\b", flags=re.I | re.S) else []


@tell("type-accent-word", "default", "weak", "One headline word picked out in the accent colour",
      "If one word matters most, write the headline so it lands on that word.")
def _(d):
    return d.find(r"<h[12][^>]*>(?:(?!</h[12]>).){0,160}<span[^>]*class(?:Name)?=[\"'{`][^\"'`>]*\btext-(?!white|black|inherit|current|foreground|muted)[a-z]+(?:-\d{2,3})?\b[^\"'`>]*[\"'`}][^>]*>\s*[\w'-]+(?:\s+[\w'-]+){0,2}\s*</span>",
                  flags=re.I | re.S)[:3]


@tell("type-eyebrow", "default", "weak", "Small uppercase letter-spaced label above headings, repeated as decoration",
      "Use a label only where it tells the reader something the heading does not (a category, a date, a status).")
def _(d):
    hits = d.find(r"""class(?:Name)?\s*=\s*["'{`][^"'`>]*\buppercase\b[^"'`>]*\btracking-(wide|wider|widest)\b[^"'`>]*["'`}]|class(?:Name)?\s*=\s*["'{`][^"'`>]*\btracking-(wide|wider|widest)\b[^"'`>]*\buppercase\b""")
    css = [x for x in d.decl(r"text-transform", r"uppercase") if any(p == x[0] for p, _l, _t in d.decl(r"letter-spacing", r"0?\.(0[5-9]|[1-3])\d*em|[1-4]px"))]
    hits += css
    return hits[:6] if len(hits) >= 3 else []


@tell("type-mono-labels", "reaction", "weak", "Monospace used for labels, eyebrows and metadata throughout",
      "Monospace says code or tabular data. Use the text face for labels unless the subject is technical.")
def _(d):
    hits = d.find(r"""class(?:Name)?\s*=\s*["'{`][^"'`>]*\bfont-mono\b[^"'`>]*\b(uppercase|text-xs|tracking-\w+)\b""")
    hits += [x for x in d.decl(r"font-family", r"mono", r"label|eyebrow|kicker|tag|badge|caption|meta|overline|nav")]
    return hits[:6] if len(hits) >= 4 else []


@tell("type-no-scale", "craft", "weak", "More than nine font sizes: no type scale", "Define 6 to 8 sizes in design.json and use only those (tokens.py).")
def _(d):
    sizes = defaultdict(list)
    for s, _sel, prop, val, line, _at in d.decls:
        if prop == "font-size":
            px = length_px(val)
            if px:
                sizes[round(px, 1)].append((s.path, line, f"font-size: {val}"))
    for s, tok, line in d.classes:
        m = re.search(r"(?:^|:)text-\[(\d+(?:\.\d+)?)(px|rem)\]$", tok)
        if m:
            sizes[round(float(m.group(1)) * (16 if m.group(2) == "rem" else 1), 1)].append((s.path, line, tok))
    if len(sizes) <= 9:
        return []
    return [(v[0][0], v[0][1], f"{len(sizes)} sizes: " + ", ".join(f"{k:g}" for k in sorted(sizes)))
            for v in [sizes[sorted(sizes)[0]]]]


@tell("type-arbitrary-values", "craft", "weak", "Many one-off pixel values in class names (text-[13px], p-[18px], w-[347px])",
      "One-off values are decisions made per element. Put the value in the scale or use the scale.")
def _(d):
    hits = d.cls(r"(?:^|:)(text|p[xytblr]?|m[xytblr]?|gap|w|h|leading|tracking|rounded)-\[\d")
    return hits[:6] if len(hits) >= 12 else []


# ------------------------------------------------------------------ colour
@tell("colour-purple", "default", "strong", "Indigo, violet or purple as the accent (the Tailwind and tutorial default)",
      "Derive the accent from the subject (references/color.md). If the brand really is purple, declare it in design.json.")
def _(d):
    hits = [(s.path, line, tok) for s, tok, line in d.classes if PURPLE.search(tok)]
    hits += [(p, l, t) for p, l, t in d.find(PURPLE_HEX)]
    return hits[:6] if len(hits) >= 3 else []


@tell("colour-gradient", "default", "strong", "Decorative gradient fills (hero, buttons, cards)",
      "Use flat colour. A gradient needs a reason in the subject: light, depth, a photograph, a material.")
def _(d):
    hits = d.cls(r"^(\w+:)*bg-(gradient|linear|radial|conic)-") + [x for x in d.decl(r"background(-image)?", r"(linear|radial|conic)-gradient\(")
                                                                   if not re.search(r"transparent\s*\d*%?\s*,\s*transparent|currentcolor|1px", x[2], re.I)]
    return hits[:6] if len(hits) >= 2 else []


@tell("colour-glow", "default", "weak", "Coloured glow shadows", "Shadows describe light and elevation; keep them neutral and few.")
def _(d):
    hits = d.cls(r"(?:^|:)shadow-(indigo|violet|purple|fuchsia|pink|blue|cyan|emerald|lime|green|rose)-\d{3}")
    hits += d.cls(r"(?:^|:)drop-shadow-\[0_0_")
    hits += [x for x in d.decl(r"box-shadow", r"0\s+0\s+\d{2,}px[^,;]*(rgba?\((?!\s*0[\s,]+0[\s,]+0)|#(?!000)[0-9a-f]{3,8}|hsl|oklch)")]
    return hits[:6]


@tell("colour-rainbow", "default", "weak", "A different hue for every feature card or icon", "One accent, used sparingly; let semantic colours mean something.")
def _(d):
    hues = defaultdict(list)
    for s, tok, line in d.classes:
        m = re.search(r"(?:^|:)(?:bg|text)-(red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(100|500|600)(?:/\d+)?$", tok)
        if m:
            hues[m.group(1)].append((s.path, line, tok))
    if len(hues) < 5:
        return []
    return [v[0] for v in list(hues.values())[:6]]


@tell("colour-pale-text", "craft", "weak", "Pale grey body text (gray-400 and lighter on a light ground)", "Muted text still needs 4.5:1. Run contrast_check.py.")
def _(d):
    dark = d.fp.get("ground") == "near-black" or d.tw.get("dark", 0)
    if dark:
        return []
    hits = d.cls(r"^text-(gray|zinc|slate|neutral|stone)-(300|400)$")
    return hits[:6] if len(hits) >= 4 else []


@tell("colour-pure-neutrals", "craft", "weak", "Neutrals are pure greys (#333, #666, #999, #f5f5f5) with no relation to the accent",
      "Tint neutrals slightly toward the brand hue (tokens.py does this from design.json).")
def _(d):
    hits = d.find(r"#(111|222|333|444|555|666|777|888|999|aaa|bbb|ccc|ddd|eee|f5f5f5|fafafa|e5e5e5|d4d4d4|a3a3a3|737373|525252|404040|262626|171717)\b",
                  exts=STYLE_EXT | MARKUP_EXT)
    return hits[:5] if len(hits) >= 8 else []


# ------------------------------------------------------------------ layout and components
@tell("layout-all-centred", "default", "weak", "Almost everything is centred", "Align text to an edge; centre only short, isolated lines. Asymmetry reads as intent.")
def _(d):
    c = d.tw.get("text-center", 0) + len(d.decl(r"text-align", r"^center"))
    other = sum(d.tw.get(k, 0) for k in ("text-left", "text-right", "text-start", "text-end")) + len(d.decl(r"text-align", r"^(left|right|start|end)"))
    if c >= 5 and c >= 3 * max(1, other):
        return (d.cls(r"(?:^|:)text-center$") + d.decl(r"text-align", r"^center"))[:5]
    return []


@tell("layout-three-cards", "default", "weak", "Three equal cards in a row (icon, heading, two lines), the feature-grid default",
      "Ask what the three things are. Unequal things deserve unequal space; a list, a table or one worked example often says more.")
def _(d):
    hits = d.cls(r"(?:^|:)grid-cols-3$") + d.decl(r"grid-template-columns", r"repeat\(\s*3\s*,|^\s*1fr\s+1fr\s+1fr\s*$")
    return hits[:5] if len(hits) >= 1 and (d.tw.get("rounded-xl", 0) + d.tw.get("rounded-2xl", 0) + d.tw.get("rounded-lg", 0) >= 3
                                           or len(d.decl(r"border-radius", r"\b(8|10|12|16|20|24)px|0?\.(5|75)rem|1rem|1\.5rem")) >= 2) else []


@tell("layout-uniform-radius", "default", "weak", "The same large radius on every box", "Vary radius by role, or choose one small radius and say why. Cards, inputs and buttons need not match.")
def _(d):
    if d.fp.get("radius") in ("8-12", "16+") and d.fp.get("radius_uniform", 0) >= 0.8 and d.fp.get("evidence", {}).get("radii", 0) >= 8:
        return (d.cls(r"(?:^|:)rounded-(lg|xl|2xl|3xl)$") + d.decl(r"border-radius", r"\d"))[:4]
    return []


@tell("layout-card-everything", "default", "weak", "Every block is a card: border, radius and shadow on all of them",
      "A card marks a separate object. Use space and alignment to group; keep cards for things that are really objects.")
def _(d):
    hits = d.cls(r"(?:^|:)shadow-(md|lg|xl|2xl)$")
    return hits[:5] if len(hits) >= 6 else []


@tell("layout-glass", "default", "weak", "Frosted glass panels (backdrop blur over translucent fills)",
      "On the web, glass is decoration unless content scrolls beneath it. On iOS 26 use the system material, not a hand-made one.")
def _(d):
    hits = d.cls(r"(?:^|:)backdrop-blur") + d.decl(r"(-webkit-)?backdrop-filter", r"blur")
    return hits[:5] if len(hits) >= 2 else []


@tell("layout-pill-announcement", "default", "weak", "A pill badge above the hero headline (\"New\", \"Now in beta\", a sparkle)",
      "If there is news, it is content: give it a sentence and a link in the page. If there is none, delete the pill.")
def _(d):
    return d.find(r"""<(?:div|span|a|p)[^>]*class(?:Name)?=["'{`][^"'`>]*rounded-full[^"'`>]*(?:text-xs|text-sm)[^"'`>]*["'`}][^>]*>(?:(?!</(?:div|span|a|p)>).){0,220}</(?:div|span|a|p)>\s*(?:<[^h/][^>]*>\s*){0,3}<h1""", flags=re.I | re.S)[:3]


@tell("layout-icon-chip", "default", "weak", "Icons in tinted rounded squares above each card heading",
      "Drop the chip. Use an icon only where it is recognised faster than the word; otherwise a number, a picture of the thing, or nothing.")
def _(d):
    hits = d.find(r"""class(?:Name)?=["'{`][^"'`>]*\b(?:w|h|size)-(?:8|9|10|11|12|14)\b[^"'`>]*\brounded-(?:md|lg|xl|2xl|full)\b[^"'`>]*\bbg-\w+-(?:50|100|500/\d+|600/\d+)[^"'`>]*["'`}]|class(?:Name)?=["'{`][^"'`>]*\bbg-\w+-(?:50|100|500/10|500/20)\b[^"'`>]*\brounded-(?:md|lg|xl|2xl|full)\b[^"'`>]*\b(?:w|h|size)-(?:8|9|10|11|12|14)\b""")
    return hits[:5] if len(hits) >= 3 else []


@tell("layout-accent-rail", "default", "weak", "Coloured bar on one edge of rounded cards", "State is better shown by a label or position; a rail on a rounded box is a tell.")
def _(d):
    hits = d.find(r"""class(?:Name)?=["'{`][^"'`>]*\bborder-[lt]-(?:2|4|8)\b[^"'`>]*\brounded""") + d.find(r"""class(?:Name)?=["'{`][^"'`>]*\brounded[^"'`>]*\bborder-[lt]-(?:2|4|8)\b""")
    return hits[:4] if len(hits) >= 2 else []


@tell("layout-blobs", "default", "weak", "Blurred colour blobs or a dotted grid behind the hero", "Background decoration that could sit behind any product says nothing about this one.")
def _(d):
    hits = d.find(r"""class(?:Name)?=["'{`][^"'`>]*\babsolute\b[^"'`>]*\bblur-(?:2xl|3xl)\b|class(?:Name)?=["'{`][^"'`>]*\bblur-(?:2xl|3xl)\b[^"'`>]*\babsolute\b""")
    hits += d.cls(r"bg-\[radial-gradient|bg-grid|bg-dot") + d.decl(r"filter", r"blur\((4\d|[5-9]\d|\d{3})px\)")
    return hits[:4]


@tell("layout-template-sections", "default", "weak", "The landing page follows the template order: hero, logos, features, how it works, testimonials, pricing, FAQ, call to action",
      "Order sections by the questions this buyer asks, in the order they ask them. Cut the sections that have nothing true to say.")
def _(d):
    order = [("logos", r"trusted by|as seen|used by teams|loved by|powering"), ("features", r"\bfeatures?\b|everything you need|why choose"),
             ("how", r"how it works|get started in|three (simple|easy) steps|3 (simple|easy) steps"), ("testimonials", r"testimonials?|what (our )?(customers|users|people) (are )?say"),
             ("pricing", r"\bpricing\b|simple, transparent|choose your plan"), ("faq", r"\bfaq\b|frequently asked"),
             ("cta", r"ready to (get started|start|transform|dive)|get started today|start (your|for) free")]
    for s in d.markup:
        heads = [(m.start(), re.sub(r"<[^>]+>|\{[^}]*\}", " ", m.group(2))) for m in re.finditer(r"<h([1-3])[^>]*>(.*?)</h\1>", s.text, re.S | re.I)]
        seen, pos = [], -1
        for name, rx in order:
            hit = next((p for p, t in heads if p > pos and re.search(rx, t, re.I)), None)
            if hit is not None:
                seen.append(name)
                pos = hit
        if len(seen) >= 5:
            return [(s.path, 1, "sections in template order: " + ", ".join(seen))]
    return []


@tell("layout-stat-row", "default", "weak", "A row of big-number tiles opening the page", "Lead with numbers only when they are real, sourced and the point of the page.")
def _(d):
    hits = d.find(r"""(?:grid-cols-4|grid-cols-3)[^"'`>]*["'`}][^>]*>(?:(?!</section>).){0,900}?(?:text-(?:3xl|4xl|5xl)[^"'`>]*font-(?:bold|semibold|extrabold)|font-(?:bold|semibold|extrabold)[^"'`>]*text-(?:3xl|4xl|5xl))[^>]*>\s*[\d$][\d,.]*\s*[kKmM%+x]*\+?\s*<""", flags=re.S)
    return hits[:3]


@tell("layout-numbered-markers", "default", "weak", "01 / 02 / 03 markers on things that are not a sequence", "Number steps only when order matters to the reader.")
def _(d):
    hits = d.find(r">\s*0[1-6]\s*<")
    if d.find(r">\s*(0[7-9]|[1-9]\d)\s*<", limit=1):
        return []  # a longer numbered list is a catalogue or an index, not three decorated steps
    return hits[:4] if len(hits) >= 3 else []


@tell("layout-full-height-hero", "default", "weak", "A hero that fills the whole first screen", "Size the hero to its content so the next thing is visible; the first screen should show what the product is.")
def _(d):
    return (d.find(r"""<(?:section|div|header)[^>]*class(?:Name)?=["'{`][^"'`>]*\b(?:min-h-screen|h-screen|min-h-\[100[sd]?vh\])\b[^"'`>]*["'`}][^>]*>(?:(?!</(?:section|header)>).){0,1500}<h1""", flags=re.I | re.S)
            + d.decl(r"(min-)?height", r"100[sdl]?vh", r"hero"))[:3]


# ------------------------------------------------------------------ icons and imagery
@tell("image-emoji-icons", "default", "strong", "Emoji used as icons, bullets or section markers", "Remove them. Use words, a real icon set with one stroke weight, or pictures of the actual thing.")
def _(d):
    out = []
    for s in d.markup:
        for m in EMOJI.finditer(s.text):
            ctx = s.text[max(0, m.start() - 60):m.start() + 20]
            if re.search(r"//|/\*|console\.|aria-label|alt=", ctx.split("\n")[-1]):
                continue
            out.append((s.path, s.line_of(m.start()), s.text[max(0, m.start() - 12):m.start() + 14].replace("\n", " ")))
    return out[:6] if len(out) >= 2 else []


@tell("image-sparkles", "default", "weak", "A sparkle icon standing for AI or newness", "Say what the feature does in words.")
def _(d):
    return d.find(r"<Sparkles?\b|\bSparkles?Icon\b|\bWandSparkles\b|icon=[\"']sparkles?[\"']|\u2728")[:4]


@tell("image-placeholders", "default", "strong", "Placeholder images or avatars from a stock service", "Use the product's real screens and real pictures. Until they exist, draw an honest, labelled placeholder.")
def _(d):
    return d.find(PLACEHOLDER_HOSTS)[:6]


@tell("meta-generator-leftovers", "default", "strong", "Starter-template leftovers (default title, favicon or generator tags)",
      "Replace the title, description, favicon and social image with the product's own.")
def _(d):
    return d.find(r"<title>\s*(Vite \+ \w+|Create Next App|React App|v0 App|Lovable( App)?|Bolt|Welcome to SvelteKit|Astro|Document|My App|Untitled)\s*</title>|"
                  r"Generated by create next app|content=[\"']v0\.(dev|app)[\"']|lovable-tagger|/vite\.svg|/next\.svg|gpt-engineer")[:5]


@tell("meta-untouched-kit", "default", "strong", "The component kit's stock theme is untouched (default radius, neutral base colour, stock primary)",
      "A kit is scaffolding. Replace its tokens with the project's own from design.json before building screens.")
def _(d):
    radius = d.decl(r"--radius", r"^0\.(5|625|75)rem$")
    stock = d.decl(r"--primary", r"^(222\.2 47\.4% 11\.2%|240 5\.9% 10%|0 0% 9%|24 9\.8% 10%|oklch\(0\.20[58] 0(\.0\d+)? [\d.]+\)|221\.2 83\.2% 53\.3%)$")
    return (stock + radius)[:4] if stock and radius else []


@tell("layout-centred-hero", "default", "weak", "The stock hero: centred headline, one line of subtext, two buttons",
      "Open with the most characteristic thing in the subject's world: the product working, a real example, a strong claim set off-centre.")
def _(d):
    return d.find(r"<(?:section|div|header)[^>]*class(?:Name)?=[\"'{`][^\"'`>]*\b(?:text-center|items-center)\b[^\"'`>]*[\"'`}][^>]*>(?:(?!</(?:section|header)>).){0,900}?<h1(?:(?!</(?:section|header)>).){0,500}?<p(?:(?!</(?:section|header)>).){0,700}?(?:<(?:a|button|Button|Link)\b(?:(?!</(?:section|header)>).){0,400}?){2}",
                  flags=re.S)[:2]


@tell("layout-pricing-trio", "default", "weak", "Three pricing tiers with the middle one ringed and labelled \"Most popular\"",
      "Show the plans the business really has. If one plan fits most buyers, say who it fits instead of ringing it.")
def _(d):
    return d.find(r"most popular|recommended plan|best value", exts=MARKUP_EXT)[:3] if d.find(r"\bring-2\b|\bscale-105\b|border-2\s+border-\w+-500|\.popular|\.featured", limit=1) else []


@tell("image-stock-effects", "default", "weak", "Stock effect components (spotlight, beams, meteors, border beam, marquee, aurora, number ticker)",
      "Effects that ship in a component gallery appear on thousands of sites. Remove them or build one effect that belongs to the subject.")
def _(d):
    return d.find(r"\b(Spotlight|BackgroundBeams|Meteors|BorderBeam|NumberTicker|AuroraBackground|ShineBorder|AnimatedGradientText|SparklesCore|"
                  r"BackgroundGradient|LampContainer|WavyBackground|ShootingStars|Particles|DotPattern|GridPattern|RetroGrid|TypewriterEffect)\b", flags=0)[:5]


@tell("image-worn-icons", "default", "weak", "The same handful of icons every generated page uses (sparkles, zap, rocket, shield, brain, bar chart)",
      "Pick icons for what they denote in this product, or use none.")
def _(d):
    hits = d.find(r"\b(Sparkles|Zap|Rocket|ShieldCheck|Shield|Brain|BarChart3|Lightbulb|Target|Globe|Layers)\b(?=\s*[,}/]|\s+className|\s+size)", flags=0)
    names = {h[2].strip() for h in hits}
    return hits[:5] if len(names) >= 4 else []


@tell("image-pulsing-dot", "default", "weak", "A pulsing dot as a \"live\" or \"online\" badge", "Show status with a word. Pulse only something that is really changing.")
def _(d):
    return d.find(r"class(?:Name)?=[\"'{`][^\"'`>]*\banimate-(?:ping|pulse)\b[^\"'`>]*\brounded-full\b|class(?:Name)?=[\"'{`][^\"'`>]*\brounded-full\b[^\"'`>]*\banimate-(?:ping|pulse)\b")[:3]


@tell("code-section-comments", "default", "weak", "Section-label comments in the markup (Hero Section, Features Section, CTA Section)",
      "They mark a page assembled from a template order. Name components by what they contain.")
def _(d):
    hits = d.find(r"\{/\*\s*(Hero|Features?|Pricing|CTA|Footer|Testimonials?|FAQ|Stats|Header|Navigation)( Section)?\s*\*/\}|<!--\s*(Hero|Features?|Pricing|CTA|Testimonials?|FAQ|Stats)( Section)?\s*-->")
    return hits[:4] if len(hits) >= 4 else []


@tell("code-no-tokens", "craft", "weak", "Colours written as raw palette classes or hex values everywhere: no tokens",
      "Generate tokens from design.json (tokens.py) and use roles (bg, surface, text, accent), so one decision changes one place.")
def _(d):
    raw = d.cls(r"(?:^|:)(?:bg|text|border|ring|from|to|via)-(?:red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|slate|gray|zinc|neutral|stone)-\d{2,3}(?:/\d+)?$")
    tokens = d.find(r"var\(--|@theme\b|--color-|bg-(background|foreground|primary|surface|accent|muted)\b", limit=1)
    return raw[:4] if len(raw) >= 40 and not tokens else []


# ------------------------------------------------------------------ copy
@tell("copy-stock-words", "copy", "weak", "Stock marketing vocabulary (elevate, seamless, supercharge, unlock, effortless)",
      "Say the concrete thing the product does, for whom, with a number or example if you have a true one (references/copy.md).")
def _(d):
    out = []
    for path, text in d.text.items():
        low = text.lower()
        for w in STOCK:
            for m in re.finditer(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low):
                out.append((path, 0, text[max(0, m.start() - 20):m.end() + 20].strip()))
    return out[:8] if len(out) >= max(3, d.words // 400) else []


@tell("copy-invented-proof", "copy", "strong", "Proof that looks invented: round user counts, star ratings, uptime, named testimonials, placeholder people",
      "Delete any number, logo or quote you cannot source. An honest empty space beats a fake testimonial; fake reviews are also illegal in several markets.")
def _(d):
    out = []
    for path, text in d.text.items():
        for rx in FAKE_PROOF:
            for m in re.finditer(rx, text, re.I):
                out.append((path, 0, text[max(0, m.start() - 15):m.end() + 15].strip()))
    return out[:8]


@tell("copy-lorem", "copy", "strong", "Lorem ipsum or placeholder copy", "Write the real words first; the layout depends on them.")
def _(d):
    return d.find(r"lorem ipsum|dolor sit amet|consectetur adipiscing|your (headline|tagline|text|description) (goes )?here|placeholder text|\bTODO: copy\b")[:5]


@tell("copy-generic-cta", "copy", "weak", "Generic button pair: \"Get Started\" and \"Learn More\"", "Name what happens next: \"Start a 14-day trial\", \"See a sample report\".")
def _(d):
    t = d.all_text
    a = re.search(r"\bget started( today| now| for free| free)?\b", t, re.I)
    b = re.search(r"\blearn more\b|\bsee how it works\b|\bwatch (the )?demo\b|\bbook a demo\b", t, re.I)
    if a and b:
        return d.find(r">\s*(Get Started( Today| Now| for Free| Free)?|Learn More)\s*(<|\{)", flags=re.I)[:4] or [(next(iter(d.text)), 0, "Get Started / Learn More")]
    return []


@tell("copy-mannered", "copy", "weak", "Mannered sentence shapes: em dashes, \"not just X, but Y\", three-word triads, colon reveals",
      "Write it the way you would say it to one person. One claim per sentence.")
def _(d):
    out = []
    for path, text in d.text.items():
        for rx in (r"\S+ \u2014 \S+", r"\b(it'?s |this is |we'?re )?not just [^.]{3,40}[,;] (but|it'?s)\b", r"\b(isn'?t|is not) (just )?(about )?[^.]{3,40}[.;,] it'?s\b",
                   r"\b[A-Z][a-z]+\. [A-Z][a-z]+\. [A-Z][a-z]+\.(?= |$)", r"\bthe result\? |\bthe best part\? |\bhere'?s the thing\b"):
            for m in re.finditer(rx, text):
                out.append((path, 0, text[max(0, m.start() - 15):m.end() + 15].strip()))
    return out[:6] if len(out) >= 3 else []


@tell("copy-title-case", "copy", "weak", "Headings In Title Case Throughout", "Use sentence case for headings and buttons unless the brand's style guide says otherwise.")
def _(d):
    heads = []
    for s in d.markup:
        for m in re.finditer(r"<h([1-4])[^>]*>([^<{]{12,90})</h\1>", s.text):
            heads.append((s.path, s.line_of(m.start()), m.group(2).strip()))
    def titled(t):
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", t) if len(w) > 3]
        return len(words) >= 3 and sum(w[0].isupper() for w in words) / len(words) >= 0.8
    hits = [h for h in heads if titled(h[2])]
    return hits[:5] if len(heads) >= 4 and len(hits) / len(heads) >= 0.6 else []


@tell("copy-template-chrome", "reaction", "weak", "Template chrome: middot-separated fragments, arrows glued to every button, spaced-dash kickers",
      "Chrome like \"Design · Build · Ship\" and trailing arrows is decoration posing as content. Cut it.")
def _(d):
    out = []
    for path, text in d.text.items():
        for rx in (r"\b\w+ · \w+ · \w+", r"\b[A-Z]{3,}(?: [A-Z]{2,})? — \w+", r"[A-Za-z] ?→(?= |$)"):
            for m in re.finditer(rx, text):
                out.append((path, 0, text[max(0, m.start() - 12):m.end() + 12].strip()))
    return out[:5] if len(out) >= 3 else []


@tell("copy-any-product-headline", "copy", "weak", "A headline that would fit any product", "Name the thing, the person and the result. If a competitor could use the sentence unchanged, rewrite it.")
def _(d):
    return d.find(r"<h1[^>]*>\s*(?:<[^>]+>\s*)*(?:[^<]{0,60}\b(faster|smarter|better|without limits|the future of|made simple|made easy|reimagined|for modern teams|"
                  r"that works for you|your \w+, (simplified|supercharged|reimagined)|build \w+ faster|ship faster|work smarter)\b[^<]{0,40})", flags=re.I)[:3]


# ------------------------------------------------------------------ dead interface
@tell("dead-no-pressed-state", "dead", "strong", "No pressed or hover state anywhere: clicks get no answer",
      "Every control needs rest, hover, focus-visible, pressed, busy and disabled (references/states-motion.md).")
def _(d):
    if not (d.find(r"<button\b|<a\s[^>]*href|role=[\"']button[\"']|<Button\b") and (d.decls or sum(d.tw.values()) > 20)):
        return []
    has = d.find(r":active\b|\bactive:[a-z]|data-\[state=|whileTap|:hover\b|\bhover:[a-z]|\[aria-pressed|\.is-pressed|:focus-visible|focus-visible:", limit=3)
    active = d.find(r":active\b|\bactive:[a-z]|whileTap|\[data-pressed|aria-pressed")
    if not has:
        s = (d.markup or d.sources)[0]
        return [(s.path, 1, "no :hover, :active or :focus-visible rule and no hover:, active: or focus-visible: class")]
    if not active:
        s = (d.markup or d.sources)[0]
        return [(s.path, 1, "hover styles exist but nothing for :active (pressed)")]
    return []


@tell("dead-outline-removed", "dead", "strong", "Focus outlines removed with no replacement", "Keep a visible :focus-visible ring at 3:1 contrast on every interactive element.")
def _(d):
    removed = d.decl(r"outline", r"^(none|0)\b") + d.cls(r"(?:^|:)outline-none$")
    replaced = d.find(r":focus-visible|focus-visible:(ring|outline|border|shadow)|focus:(ring|outline|border|shadow)-", limit=2)
    return removed[:5] if removed and not replaced else []


@tell("dead-fade-up-everything", "dead", "weak", "Everything fades or slides up on scroll, the same way",
      "The same reveal on every block reads generated. Choreograph by role: one scene that tells the subject's story, quieter "
      "entrances elsewhere, CSS scroll timelines with the content visible at rest (references/scroll-motion.md).")
def _(d):
    hits = d.find(r"whileInView=|data-aos=|\bIntersectionObserver\b|initial=\{\{\s*opacity:\s*0,\s*y:\s*\d+|animate-fade-in-up|animate-in fade-in|fade-up|reveal-on-scroll")
    return hits[:5] if len(hits) >= 5 else []


REVEAL_SEL = re.compile(r"reveal|fade|appear|aos|in-?view|on-?scroll|animate|enter|rise|slide-?in|stagger", re.I)
GUARD = re.compile(r"prefers-reduced-motion:\s*no-preference|animation-timeline|view-timeline|scroll-timeline", re.I)


@tell("motion-hidden-start", "dead", "strong", "Content starts invisible with no guard (opacity 0 waiting for a reveal)",
      "Keep content visible by default. Put the hidden start state inside @media (prefers-reduced-motion: no-preference) and "
      "@supports (animation-timeline: view()), or in the keyframes' from, so no-JS, reduced motion, crawlers and the first paint "
      "all see the content (references/scroll-motion.md).")
def _(d):
    hits = []
    for src, sel, prop, val, line, at in d.decls:
        if prop == "opacity" and re.fullmatch(r"0(\.0+)?", val.strip()) and REVEAL_SEL.search(sel) and not GUARD.search(at or "") \
                and "keyframes" not in (at or "").lower() and not re.search(r"(^|[\s,])(html)?\.(js|motion|has-js|motion-ok)\b", sel):
            hits.append((src.path, line, f"{sel} {{ opacity: {val} }}"))
    hits += d.find(r"initial=\{\{\s*opacity:\s*0", limit=4)
    return hits[:5]


@tell("motion-scroll-hijack", "dead", "weak", "Scrolling is taken over by a smooth-scroll library (Lenis, Locomotive, fullPage)",
      "Native scrolling keeps keyboard, find-in-page, anchor links and the platform's own feel, and costs no script. Use scroll "
      "timelines for the effects; if the owner wants smooth scrolling, record \"smooth-scroll\" under deliberate.")
def _(d):
    return d.find(r"from\s+[\"'](?:@studio-freight/|)lenis|new\s+Lenis\(|locomotive-scroll|LocomotiveScroll|fullpage(?:\.js|\.min\.js|_api)|smooth-scrollbar")[:3]


@tell("motion-scroll-handler", "dead", "weak", "Motion driven from scroll event handlers",
      "Scroll handlers run on the main thread on every frame and cost responsiveness. Drive scroll effects with CSS "
      "animation-timeline: scroll() or view(); if a script must listen, pass { passive: true } and only toggle a class.")
def _(d):
    hits = d.find(r"addEventListener\(\s*[\"']scroll[\"']\s*,[^)]*\)(?![^\n]*passive)|window\.onscroll\s*=|\$\(window\)\.scroll\(", exts={".js", ".ts", ".jsx", ".tsx", ".html", ".vue", ".svelte", ".astro"})
    return [h for h in hits if "passive" not in h[2]][:3]


@tell("image-drawn-art", "default", "weak", "Pictures of the subject drawn by hand in SVG where a photograph would do",
      "Hand-drawn stand-ins (loaves, plants, people, devices) read as filler. Use the owner's photographs, or real photographs "
      "from a free library (Pexels, Unsplash, open museum collections), credited in DESIGN.md (references/imagery.md).")
def _(d):
    if d.surface not in ("marketing", "store"):
        return []
    photos = d.find(r"<img[^>]+src=[\"'][^\"']+\.(?:jpe?g|webp|avif|png)|<source[^>]+srcset=|images\.(?:pexels|unsplash)\.com|background-image:\s*url\(", limit=1)
    if photos:
        return []
    drawn = []
    for src in d.markup:
        for m in re.finditer(r"<svg\b(.*?)</svg>", src.text, re.S | re.I):
            body = m.group(1)
            shapes = len(re.findall(r"<(path|circle|ellipse|polygon|rect|line|polyline)\b", body, re.I))
            vb = re.search(r"viewBox=[\"']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)", body)
            big = vb and max(float(vb.group(1)), float(vb.group(2))) > 32  # icons are drawn on a 16 to 32 unit grid
            if (big and shapes >= 2) or shapes >= 8:
                drawn.append((src.path, src.line_of(m.start()), "<svg> artwork"))
    return drawn[:4] if len(drawn) >= 3 else []


@tell("dead-hover-scale", "dead", "weak", "Cards that grow on hover", "Hover should confirm that something is clickable (colour, underline, a small shift), not move the layout.")
def _(d):
    hits = d.cls(r"hover:scale-1(05|10|25)$") + d.decl(r"transform", r"scale\(1\.(0[5-9]|[1-9])", r":hover")
    return hits[:4] if len(hits) >= 3 else []


@tell("dead-transition-all", "dead", "weak", "transition: all, or animated layout properties (width, height, top, left, margin)",
      "Animate transform and opacity only, 150 to 250ms, and name the properties.")
def _(d):
    hits = d.decl(r"transition(-property)?", r"\b(all|width|height|top|left|right|bottom|margin|padding)\b") + d.cls(r"(?:^|:)transition-all$")
    return hits[:4] if len(hits) >= 4 else []


@tell("dead-no-reduced-motion", "dead", "weak", "Animation with no prefers-reduced-motion handling", "Turn motion off or down under prefers-reduced-motion: reduce.")
def _(d):
    anim = d.decl(r"animation(-name)?|transition", r"\w") + d.cls(r"(?:^|:)animate-(?!none)") + d.find(r"framer-motion|from [\"']motion/react[\"']|gsap", limit=2)
    handled = d.find(r"prefers-reduced-motion|motion-reduce:|motion-safe:|useReducedMotion|reducedMotion", limit=1)
    return anim[:3] if len(anim) >= 4 and not handled else []


@tell("dead-endless-animation", "dead", "weak", "Several endless decorative animations (pulse, bounce, float, gradient)",
      "Ambient motion competes with content. Keep one at most, and only if it means something. Spinners and skeleton sweeps do not count.")
def _(d):
    work = re.compile(r"spin|sweep|skelet|load|progress|busy|shimmer", re.I)
    names = {}
    for s, _sel, prop, val, line, _at in d.decls:
        if prop in ("animation", "animation-name") and ("infinite" in val or prop == "animation-name"):
            name = next((t for t in re.split(r"[\s,]+", val) if re.fullmatch(r"[A-Za-z_][\w-]*", t)
                         and t not in ("infinite", "linear", "ease", "ease-in", "ease-out", "ease-in-out", "alternate", "both", "forwards",
                                       "backwards", "normal", "reverse", "running", "paused", "none")), "")
            if name and not work.search(name) and "infinite" in val:
                names.setdefault(name, (s.path, line, f"animation: {val[:50]}"))
    hits = list(names.values()) + d.cls(r"(?:^|:)animate-(pulse|bounce|ping|float|spin-slow|gradient|marquee)$")
    return hits[:4] if len(names) + len({h[2] for h in hits[len(names):]}) >= 3 else []


@tell("dead-toy-motion", "dead", "weak", "Count-up numbers, typewriter headlines, bouncing or elastic easing",
      "Motion that performs for the visitor delays the content. Show the number; ease out, do not bounce.")
def _(d):
    hits = d.find(r"\b(CountUp|NumberTicker|Typewriter|TypeAnimation|typed\.js|react-countup|AnimatedCounter)\b", flags=0)
    hits += d.cls(r"(?:^|:)animate-bounce$")
    hits += d.decl(r"(transition|animation)(-timing-function)?", r"cubic-bezier\(\s*[\d.]+\s*,\s*(-\d|1\.[2-9]|[2-9])")
    return hits[:4]


@tell("dead-no-data-states", "dead", "weak", "Data screens with no loading, empty or error state", "Design all four: loading (a skeleton shaped like the content), empty, error, and partial.")
def _(d):
    if d.surface not in ("app", "desktop", "mobile", "store"):
        return []
    fetches = d.find(r"\buseQuery\b|\buseSWR\b|\bfetch\(|\baxios\.|\buseLoaderData\b|\.task\s*\{|LaunchedEffect|collectAsState|async let|URLSession")
    states = d.find(r"skeleton|isLoading|isPending|aria-busy|loading\.tsx|<Suspense|empty[ -_]?state|EmptyState|isError|error\.tsx|ErrorBoundary|ProgressView|"
                    r"CircularProgressIndicator|ContentUnavailableView|\.redacted\(", limit=3)
    return fetches[:3] if fetches and not states else []


@tell("dead-busy-is-disabled", "dead", "weak", "Busy buttons shown as disabled (faded) with no busy state", "Busy is not disabled: keep full opacity, show progress in place, set aria-busy.")
def _(d):
    hits = d.find(r"disabled=\{\s*(is)?(loading|submitting|pending|busy|saving)\w*\s*\}")
    busy = d.find(r"aria-busy|data-busy|data-loading|isLoading\s*&&\s*<(Spinner|Loader)", limit=1)
    return hits[:4] if hits and not busy else []


# ------------------------------------------------------------------ native
@tell("native-fixed-font-sizes", "default", "weak", "Fixed font sizes in native code: no Dynamic Type or type roles",
      "SwiftUI: text styles (.body, .headline) or custom fonts with relativeTo. Compose: MaterialTheme.typography roles.")
def _(d):
    hits = d.find(r"\.font\(\.system\(size:\s*\d+|\bfontSize\s*=\s*\d+(\.\d+)?\.sp\b|Font\.custom\([^)]*size:\s*\d+\s*\)(?!.*relativeTo)", exts=NATIVE_EXT)
    return hits[:5] if len(hits) >= 5 else []


@tell("native-template-colours", "default", "strong", "Template colours left in the app (Purple80, Purple40, 0xFF6200EE, .purple to .blue gradients)",
      "Replace the starter theme with the project's own colour roles (tokens.py --kotlin or --swift).")
def _(d):
    return d.find(r"\bPurple(80|40|GreyDark|Grey80|Grey40)\b|\bPink(80|40)\b|0xFF6200EE|0xFF3700B3|0xFFBB86FC|0xFF03DAC[56]|"
                  r"LinearGradient\([^)]*\[\s*\.(purple|blue|indigo|pink)\s*,\s*\.(purple|blue|indigo|pink)|"
                  r"Brush\.(linear|horizontal|vertical)Gradient\(\s*(colors\s*=\s*)?listOf\(\s*Color\((0xFF)?(6366F1|8B5CF6|7C3AED|A855F7|667EEA)", exts=NATIVE_EXT)[:5]


@tell("native-uniform-cards", "default", "weak", "Every native card has the same large corner radius and a shadow",
      "Use the platform's grouped lists and system materials before inventing cards.")
def _(d):
    hits = d.find(r"\.cornerRadius\((1[6-9]|2\d)\)|RoundedRectangle\(cornerRadius:\s*(1[6-9]|2\d)|RoundedCornerShape\((1[6-9]|2\d)\.dp\)", exts=NATIVE_EXT)
    shadows = d.find(r"\.shadow\((color:|radius:)|elevation\s*=\s*\d+\.dp|shadowElevation", exts=NATIVE_EXT)
    return hits[:4] if len(hits) >= 5 and len(shadows) >= 4 else []


@tell("native-web-habits", "default", "weak", "Web habits in a native app (hamburger menus, custom tab bars, custom back buttons, toast-only errors)",
      "Use the platform's navigation: tab bar or navigation stack on iOS, navigation bar or rail on Android (references/mobile.md).")
def _(d):
    return d.find(r"line\.3\.horizontal|Icons\.(Default|Filled|Rounded)\.Menu\b.*(Drawer|drawer)|navigationBarBackButtonHidden\(true\)|"
                  r"\.toolbar\(\.hidden, for: \.tabBar\)", exts=NATIVE_EXT)[:4]


@tell("native-emoji-text", "default", "strong", "Emoji as icons in native views", "Use SF Symbols on Apple platforms and Material Symbols on Android, or the product's own icons.")
def _(d):
    out = []
    for s in d.native:
        for m in re.finditer(r"Text\(\s*\"[^\"]*\"", s.text):
            if EMOJI.search(m.group(0)):
                out.append((s.path, s.line_of(m.start()), m.group(0)[:60]))
    return out[:5] if len(out) >= 2 else []


# ------------------------------------------------------------------ whole-look checks
def look_tells(d):
    out = []
    if not d.fp:
        return out
    for name, score, hit in nearest_default(d.fp)[:2]:
        if score >= 0.75:
            kind = "reaction" if any(k in name for k in ("cream", "neon", "techno")) else "default"
            out.append({"id": "look-" + re.sub(r"[^a-z]+", "-", name.split("(")[0].strip().lower()).strip("-"), "kind": kind, "strength": "strong",
                        "title": f"The whole look matches a known default: {name} ({score:.0%})",
                        "fix": "Re-derive type, ground and accent from the subject (references/identity.md); changing one trait is not enough.",
                        "evidence": [("", 0, ", ".join(hit))]})
    return out


def run(paths, surface="marketing", ignore=(), identity=None):
    root = os.path.commonpath([os.path.abspath(p) for p in paths]) if paths else os.getcwd()
    if os.path.isfile(root):
        root = os.path.dirname(root)
    sources = collect(paths)
    d = Doc(sources, root)
    d.surface = surface
    deliberate = {}
    if identity and os.path.exists(identity):
        with open(identity, encoding="utf-8") as fh:
            deliberate = json.load(fh).get("deliberate", {}) or {}
    found, declared = [], []
    for t in TELLS:
        if t["id"] in ignore:
            continue
        try:
            ev = t["fn"](d)
        except re.error:
            ev = []
        if ev:
            item = {k: t[k] for k in ("id", "kind", "strength", "title", "fix")}
            item["evidence"] = ev
            (declared if t["id"] in deliberate else found).append(dict(item, reason=deliberate.get(t["id"])))
    for item in look_tells(d):
        if item["id"] not in ignore:
            (declared if item["id"] in deliberate else found).append(dict(item, reason=deliberate.get(item["id"])))
    return d, found, declared


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--surface", choices=["marketing", "app", "desktop", "mobile", "store"], default="marketing")
    ap.add_argument("--identity", help="design.json; tells listed under \"deliberate\" are reported as declared")
    ap.add_argument("--ignore", default="", help="comma-separated tell ids to skip")
    ap.add_argument("--list", action="store_true", help="print the catalogue and exit")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.list:
        for kind, label in (("default", "Defaults (first generation)"), ("reaction", "Reactions (second generation)"),
                            ("dead", "Dead interface"), ("copy", "Copy"), ("craft", "Craft")):
            print(f"## {label}\n")
            for t in TELLS:
                if t["kind"] == kind:
                    print(f"- `{t['id']}` ({t['strength']}): {t['title']}. {t['fix']}")
            print()
        print("Whole-look checks: the fingerprint is compared with the catalogued default looks (fingerprint.py).")
        return 0
    if not a.paths:
        ap.error("give files or folders, or --list")
    d, found, declared = run(a.paths, a.surface, set(filter(None, a.ignore.split(","))), a.identity)
    if not d.sources:
        sys.exit("No source files found (looked for HTML, CSS, JSX/TSX, Vue, Svelte, Astro, Liquid, Swift, Kotlin).")
    strong = [f for f in found if f["strength"] == "strong"]
    if a.json:
        print(json.dumps({"files": len(d.sources), "strong": len(strong), "tells": found, "declared": declared, "fingerprint": d.fp}, indent=1))
        return 2 if strong else 0
    o = [f"# Tell check: {len(d.sources)} files", "",
         f"{len(found)} tells ({len(strong)} strong)" + (f", {len(declared)} declared deliberate" if declared else "") + ". "
         "One weak tell means little; a design reads as generated when several stack up.", ""]
    labels = {"default": "Defaults nobody decided", "reaction": "Reactions that became defaults", "dead": "Dead interface", "copy": "Copy", "craft": "Craft"}
    for kind, label in labels.items():
        items = [f for f in found if f["kind"] == kind]
        if not items:
            continue
        o += [f"## {label}", ""]
        for f in sorted(items, key=lambda x: x["strength"] != "strong"):
            o.append(f"- **{f['strength']}** `{f['id']}`: {f['title']}.")
            for path, line, snip in f["evidence"][:3]:
                where = f"{rel(path, d.root)}:{line}" if path and line else (rel(path, d.root) if path else "")
                o.append(f"  - {where + ' ' if where else ''}`{snip.strip()[:90]}`")
            if len(f["evidence"]) > 3:
                o.append(f"  - and {len(f['evidence']) - 3} more")
            o.append(f"  - Fix: {f['fix']}")
        o.append("")
    if declared:
        o += ["## Declared deliberate (not counted)", ""] + [f"- `{f['id']}`: {f['reason'] or 'no reason given'}" for f in declared] + [""]
    if not found:
        o += ["No tells found. That is the floor, not the verdict: render the page and critique it (references/critique.md).", ""]
    if not os.path.exists(os.path.join(d.root, "DESIGN.md")) and not a.identity and not os.path.exists(os.path.join(d.root, "design.json")):
        o.append("No DESIGN.md or design.json beside these files: the project has no recorded identity, so the next screen will drift "
                 "back to defaults (references/identity.md).")
    print("\n".join(o))
    return 2 if strong else 0


if __name__ == "__main__":
    sys.exit(main())
