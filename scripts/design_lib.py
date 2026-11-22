"""Shared helpers for the human-design scripts: colour maths (sRGB, OKLab, OKLCH,
WCAG 2 contrast, APCA lightness contrast), CSS and class extraction from source
files, and small report utilities.

Standard library only. Python 3.8+. No network access, no environment variables.
"""
from __future__ import annotations

import math
import os
import re
from collections import Counter

SOURCE_EXT = {".html", ".htm", ".css", ".scss", ".less", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro",
              ".swift", ".kt", ".dart", ".liquid", ".php", ".erb", ".md", ".mdx"}
STYLE_EXT = {".css", ".scss", ".less"}
MARKUP_EXT = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".liquid", ".php", ".erb", ".mdx"}
NATIVE_EXT = {".swift", ".kt", ".dart"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", ".svelte-kit", "out", "coverage", "vendor",
             ".venv", "venv", "__pycache__", ".turbo", ".cache", "Pods", "DerivedData", ".gradle", ".human-design"}

NAMED = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000", "blue": "#0000ff", "gray": "#808080",
         "grey": "#808080", "silver": "#c0c0c0", "navy": "#000080", "teal": "#008080", "purple": "#800080", "orange": "#ffa500",
         "yellow": "#ffff00", "pink": "#ffc0cb", "indigo": "#4b0082", "violet": "#ee82ee", "gold": "#ffd700", "beige": "#f5f5dc",
         "ivory": "#fffff0", "whitesmoke": "#f5f5f5", "gainsboro": "#dcdcdc", "lightgray": "#d3d3d3", "lightgrey": "#d3d3d3",
         "darkgray": "#a9a9a9", "darkgrey": "#a9a9a9", "dimgray": "#696969", "slategray": "#708090", "tomato": "#ff6347",
         "crimson": "#dc143c", "coral": "#ff7f50", "salmon": "#fa8072", "royalblue": "#4169e1", "dodgerblue": "#1e90ff",
         "rebeccapurple": "#663399", "lime": "#00ff00", "aqua": "#00ffff", "cyan": "#00ffff", "magenta": "#ff00ff",
         "fuchsia": "#ff00ff", "maroon": "#800000", "olive": "#808000", "linen": "#faf0e6", "snow": "#fffafa"}


# ----------------------------------------------------------------- colour
def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def srgb_to_oklab(r: float, g: float, b: float):
    r, g, b = _lin(r), _lin(g), _lin(b)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklab_to_srgb(L: float, a: float, b: float):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(math.copysign(_gam(abs(v)), v) for v in (r, g, bl))


def srgb_to_oklch(r: float, g: float, b: float):
    L, a, bb = srgb_to_oklab(r, g, b)
    c = math.hypot(a, bb)
    h = math.degrees(math.atan2(bb, a)) % 360 if c > 1e-4 else 0.0
    return L, c, h


def oklch_to_srgb(L: float, c: float, h: float):
    return oklab_to_srgb(L, c * math.cos(math.radians(h)), c * math.sin(math.radians(h)))


def in_gamut(rgb, eps: float = 0.0005) -> bool:
    return all(-eps <= v <= 1 + eps for v in rgb)


def fit_oklch(L: float, c: float, h: float):
    """Reduce chroma until the colour fits sRGB. Returns (rgb, chroma used, clipped?)."""
    rgb = oklch_to_srgb(L, c, h)
    if in_gamut(rgb):
        return tuple(min(1.0, max(0.0, v)) for v in rgb), c, False
    lo, hi = 0.0, c
    for _ in range(40):
        mid = (lo + hi) / 2
        if in_gamut(oklch_to_srgb(L, mid, h)):
            lo = mid
        else:
            hi = mid
    return tuple(min(1.0, max(0.0, v)) for v in oklch_to_srgb(L, lo, h)), lo, True


def to_hex(rgb) -> str:
    return "#" + "".join(f"{round(min(1.0, max(0.0, v)) * 255):02x}" for v in rgb[:3])


_FUNC = re.compile(r"^(rgba?|hsla?|oklch|oklab)\(\s*([^)]*)\)$", re.I)


def _num(tok: str, scale: float = 1.0) -> float:
    tok = tok.strip()
    if tok.endswith("%"):
        return float(tok[:-1]) / 100.0 * scale
    return float(re.sub(r"(deg|turn|rad)$", "", tok))


def parse_color(raw: str):
    """Return (r, g, b, alpha) in sRGB 0..1, or None when the value is not a plain colour."""
    if not raw:
        return None
    s = raw.strip().lower().rstrip(";").replace("!important", "").strip()
    if s in ("transparent", "currentcolor", "inherit", "initial", "unset", "none") or "var(" in s:
        return None
    if s in NAMED:
        s = NAMED[s]
    if s.startswith("#"):
        h = s[1:]
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        if len(h) not in (6, 8) or not re.fullmatch(r"[0-9a-f]+", h):
            return None
        vals = [int(h[i:i + 2], 16) / 255 for i in range(0, len(h), 2)]
        return (vals[0], vals[1], vals[2], vals[3] if len(vals) == 4 else 1.0)
    m = _FUNC.match(s)
    if not m:
        return None
    fn = m.group(1).lower()
    body = m.group(2).replace("/", " / ")
    parts = [p for p in re.split(r"[\s,]+", body) if p]
    alpha = 1.0
    if "/" in parts:
        i = parts.index("/")
        try:
            alpha = _num(parts[i + 1])
        except (ValueError, IndexError):
            alpha = 1.0
        parts = parts[:i]
    elif len(parts) == 4:
        try:
            alpha = _num(parts[3])
        except ValueError:
            alpha = 1.0
        parts = parts[:3]
    if len(parts) != 3 or any(p in ("none", "from") for p in parts):
        return None
    try:
        if fn.startswith("rgb"):
            r, g, b = (_num(p, 255.0) / 255.0 for p in parts)
            return (r, g, b, alpha)
        if fn.startswith("hsl"):
            h, sat, li = _num(parts[0]) % 360, _num(parts[1]), _num(parts[2])
            sat = sat / 100 if sat > 1 else sat
            li = li / 100 if li > 1 else li
            c = (1 - abs(2 * li - 1)) * sat
            x = c * (1 - abs((h / 60) % 2 - 1))
            m0 = li - c / 2
            r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(h // 60) % 6]
            return (r + m0, g + m0, b + m0, alpha)
        if fn == "oklch":
            L, c, h = _num(parts[0]), _num(parts[1], 0.4), _num(parts[2])
            rgb, _c, _clip = fit_oklch(L, c, h)
            return (rgb[0], rgb[1], rgb[2], alpha)
        if fn == "oklab":
            L, a, b = _num(parts[0]), _num(parts[1], 0.4), _num(parts[2], 0.4)
            rgb = oklab_to_srgb(L, a, b)
            return (min(1, max(0, rgb[0])), min(1, max(0, rgb[1])), min(1, max(0, rgb[2])), alpha)
    except (ValueError, IndexError):
        return None
    return None


def luminance(rgb) -> float:
    return 0.2126 * _lin(rgb[0]) + 0.7152 * _lin(rgb[1]) + 0.0722 * _lin(rgb[2])


def wcag_contrast(fg, bg) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def apca(fg, bg) -> float:
    """APCA lightness contrast Lc (0.0.98G-4g constants). Positive: dark text on light; negative: light on dark."""
    def y(rgb):
        v = 0.2126729 * rgb[0] ** 2.4 + 0.7151522 * rgb[1] ** 2.4 + 0.0721750 * rgb[2] ** 2.4
        return v + (0.022 - v) ** 1.414 if v < 0.022 else v
    yt, yb = y(fg), y(bg)
    if abs(yb - yt) < 0.0005:
        return 0.0
    if yb > yt:
        s = (yb ** 0.56 - yt ** 0.57) * 1.14
        return 0.0 if s < 0.1 else (s - 0.027) * 100
    s = (yb ** 0.65 - yt ** 0.62) * 1.14
    return 0.0 if s > -0.1 else (s + 0.027) * 100


def blend(fg, bg):
    """Composite a colour with alpha over an opaque background."""
    a = fg[3] if len(fg) > 3 else 1.0
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3))


def hue_name(h: float, c: float, L: float) -> str:
    """Name an OKLCH hue. Pure sRGB red sits near 29 degrees, orange near 55, yellow near 100."""
    if c < 0.02:
        return "neutral"
    h = h % 360
    for limit, name in ((35, "red"), (65, "orange"), (90, "amber"), (112, "yellow"), (135, "lime"), (165, "green"),
                        (200, "teal"), (235, "cyan"), (268, "blue"), (290, "indigo"), (320, "purple"), (345, "pink")):
        if h < limit:
            return name
    return "red"


_VAR = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*((?:[^()]|\([^()]*\))*))?\)")
_DARK_SEL = re.compile(r"""\[data-(theme|mode|color-scheme)\s*=\s*["']?dark|(^|[\s.:(])dark(\b|$)|\.theme-dark|\.dark-mode""", re.I)


def resolve_vars(value: str, table: dict, depth: int = 0) -> str:
    """Replace var(--x) with its value from a table of custom properties (fallbacks honoured)."""
    if "var(" not in value or depth > 6:
        return value
    def sub(m):
        got = table.get(m.group(1))
        return got if got is not None else (m.group(2) or m.group(0))
    out = _VAR.sub(sub, value)
    return resolve_vars(out, table, depth + 1) if out != value else out


def is_dark_context(selector: str, at_rule: str) -> bool:
    """True for declarations that only apply in dark mode."""
    return ("prefers-color-scheme" in at_rule and "dark" in at_rule) or bool(_DARK_SEL.search(selector))


def size_px(value: str, base: float = 16.0):
    """Font size in px from a plain length or the upper bound of clamp(); None otherwise."""
    v = value.strip().lower()
    m = re.match(r"clamp\((.+)\)$", v)
    if m:
        parts = [x.strip() for x in re.split(r",(?![^()]*\))", m.group(1))]
        return length_px(parts[-1], base) if parts else None
    return length_px(v, base)


# ----------------------------------------------------------------- sources
class Source:
    def __init__(self, path: str, text: str):
        self.path = path
        self.text = text
        self.ext = os.path.splitext(path)[1].lower()
        self._line_starts = None

    def line_of(self, pos: int) -> int:
        if self._line_starts is None:
            self._line_starts = [0] + [m.end() for m in re.finditer("\n", self.text)]
        lo, hi = 0, len(self._line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self._line_starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1


def collect(paths, max_bytes: int = 1_500_000):
    """Read source files under the given files or folders. Returns a list of Source."""
    out, seen = [], set()
    for p in paths:
        if os.path.isfile(p):
            files = [p]
        else:
            files = []
            for root, dirs, names in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
                files += [os.path.join(root, n) for n in sorted(names)]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext not in SOURCE_EXT or f in seen or f.endswith((".min.css", ".min.js", ".d.ts")):
                continue
            seen.add(f)
            try:
                if os.path.getsize(f) > max_bytes:
                    continue
                with open(f, encoding="utf-8", errors="ignore") as fh:
                    out.append(Source(f, fh.read()))
            except OSError:
                continue
    # follow local stylesheets linked from the pages, so a page checked alone still has its tokens
    for src in list(out):
        if src.ext not in (".html", ".htm"):
            continue
        for m in re.finditer(r"""<link[^>]+href=["']([^"'#?]+\.css)["']|@import\s+(?:url\()?["']([^"')]+\.css)["']""", src.text, re.I):
            href = m.group(1) or m.group(2)
            if re.match(r"^(?:[a-z]+:)?//", href):
                continue
            path = os.path.normpath(os.path.join(os.path.dirname(src.path), href))
            if path not in seen and os.path.isfile(path):
                seen.add(path)
                try:
                    with open(path, encoding="utf-8", errors="ignore") as fh:
                        out.append(Source(path, fh.read()))
                except OSError:
                    pass
    return out


_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
_INLINE_STYLE = re.compile(r"""style\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
_CLASS_ATTR = re.compile(r"""(?:class|className|:class|class:list)\s*=\s*(?:"([^"]*)"|'([^']*)'|\{`([^`]*)`\}|\{\s*"([^"]*)"\s*\})""")
_CLASS_CALL = re.compile(r"""\b(?:cn|clsx|classNames|cva|twMerge|tw)\(\s*((?:[^()]|\([^()]*\))*)\)""", re.S)
_STR = re.compile(r"""["'`]([^"'`\n]{2,400})["'`]""")


def css_of(src: Source):
    """Yield (css_text, offset) chunks found in a source file."""
    if src.ext in STYLE_EXT:
        yield src.text, 0
        return
    for m in _STYLE_BLOCK.finditer(src.text):
        yield m.group(1), m.start(1)
    for m in _INLINE_STYLE.finditer(src.text):
        g = 1 if m.group(1) is not None else 2
        yield "x{" + m.group(g) + "}", m.start(g) - 2


def declarations(src: Source):
    """Yield (selector, property, value, line, at_rule) for CSS declarations in a source file."""
    for css, off in css_of(src):
        text = _COMMENT.sub(lambda m: " " * len(m.group(0)), css)
        stack, buf, start = [], [], 0
        i, n = 0, len(text)
        while i < n:
            ch = text[i]
            if ch == "{":
                stack.append("".join(buf).strip())
                buf, start = [], i + 1
            elif ch == "}":
                chunk = "".join(buf)
                yield from _decls(chunk, stack, src, off + start)
                if stack:
                    stack.pop()
                buf, start = [], i + 1
            elif ch == ";" and stack:
                chunk = "".join(buf) + ";"
                yield from _decls(chunk, stack, src, off + start)
                buf, start = [], i + 1
            else:
                buf.append(ch)
            i += 1


def _decls(chunk, stack, src, pos):
    if not stack:
        return
    sel = next((s for s in reversed(stack) if not s.startswith("@")), stack[-1])
    at = " ".join(s for s in stack if s.startswith("@"))
    for part in chunk.split(";"):
        if ":" not in part:
            continue
        prop, _, val = part.partition(":")
        prop, val = prop.strip().lower(), val.strip()
        if prop and val and re.fullmatch(r"-{0,2}[a-z][a-z0-9-]*", prop):
            yield sel, prop, val, src.line_of(max(0, pos)), at


def class_tokens(src: Source):
    """Yield (token, line) for class names found in markup and in class helper calls."""
    if src.ext not in MARKUP_EXT and src.ext not in (".js", ".ts"):
        return
    for m in _CLASS_ATTR.finditer(src.text):
        val = next((g for g in m.groups() if g is not None), "")
        line = src.line_of(m.start())
        for tok in re.split(r"\s+", re.sub(r"\$\{[^}]*\}", " ", val)):
            if tok:
                yield tok, line
    for m in _CLASS_CALL.finditer(src.text):
        line = src.line_of(m.start())
        for s in _STR.finditer(m.group(1)):
            for tok in s.group(1).split():
                yield tok, line


_TAG = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)


def visible_text(src: Source) -> str:
    """Rough visible text of markup: tags, scripts and styles removed."""
    if src.ext not in MARKUP_EXT and src.ext not in (".md",):
        return ""
    t = _TAG.sub(" ", src.text)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\{[^{}]*\}", " ", t) if src.ext in (".jsx", ".tsx") else t
    return re.sub(r"\s+", " ", t)


_NEXT_FONT = re.compile(r"""import\s*\{([^}]+)\}\s*from\s*["']next/font/google["']""")
_GEIST = re.compile(r"""from\s*["']geist/font(?:/(sans|mono))?["']|\bGeist(Sans|Mono)\b""")
_GFONT_URL = re.compile(r"fonts\.googleapis\.com/css2?\?([^\"'\s>)]+)")
_FONTSOURCE = re.compile(r"""["']@fontsource(?:-variable)?/([a-z0-9-]+)""")
_TW_FAMILY = re.compile(r"""\b(sans|serif|mono|display|heading|body)\s*:\s*\[\s*["']([^"']+)["']""")
_NATIVE_FONT = re.compile(r"""\.custom\(\s*"([^"]+)"|Font\(\s*R\.font\.([a-z0-9_]+)|fontFamily:\s*['"]([^'"]+)['"]""")


def font_mentions(src: Source):
    """Yield (family, line, how) for typefaces named outside CSS declarations: next/font imports, the geist
    package, Google Fonts URLs, Fontsource packages, Tailwind config font families and native font calls."""
    t = src.text
    for m in _NEXT_FONT.finditer(t):
        for name in m.group(1).split(","):
            name = name.split(" as ")[0].strip()
            if name:
                yield re.sub(r"_", " ", name).lower(), src.line_of(m.start()), "next/font"
    for m in _GEIST.finditer(t):
        yield "geist mono" if "mono" in m.group(0).lower() else "geist", src.line_of(m.start()), "geist package"
    for m in _GFONT_URL.finditer(t):
        for fam in re.findall(r"family=([^:&]+)", m.group(1)):
            yield fam.replace("+", " ").replace("%20", " ").lower(), src.line_of(m.start()), "Google Fonts link"
    for m in _FONTSOURCE.finditer(t):
        yield m.group(1).replace("-", " "), src.line_of(m.start()), "fontsource"
    if "tailwind.config" in src.path or "fontFamily" in t:
        for m in _TW_FAMILY.finditer(t):
            yield m.group(2).lower(), src.line_of(m.start()), "tailwind config"
    if src.ext in NATIVE_EXT:
        for m in _NATIVE_FONT.finditer(t):
            name = next(g for g in m.groups() if g)
            yield re.sub(r"[-_](regular|bold|medium|semibold|light|italic|variable).*$", "", name, flags=re.I).replace("_", " ").lower(), src.line_of(m.start()), "native"


def first_family(value: str) -> str:
    """First concrete family name of a font-family value, lower-cased, without quotes."""
    for part in value.split(","):
        name = part.strip().strip("'\"").lower()
        if name and not name.startswith("var(") and name not in ("inherit", "initial", "unset"):
            return name
    return ""


_FONT_SHORTHAND = re.compile(r"(?:^|\s)(?:\d*\.?\d+(?:px|rem|em|pt|%)|var\([^)]*\)|clamp\([^)]*\)|(?:xx?-)?small|medium|(?:x+-)?large|smaller|larger)"
                             r"(?:\s*/\s*(?:var\([^)]*\)|[^\s,]+))?\s+(.+)$", re.I)


def family_of(prop: str, value: str) -> str:
    """The first concrete family named by a font-family, --font-* or font shorthand declaration ('' when none)."""
    if prop == "font-family" or prop.startswith("--font"):
        return first_family(value)
    if prop == "font":
        m = _FONT_SHORTHAND.search(value.strip())
        return first_family(m.group(1)) if m else ""
    return ""


def font_shorthand_size(value: str):
    """The size token of a `font:` shorthand, in px, or None."""
    m = re.search(r"(?:^|\s)(\d*\.?\d+(?:px|rem|em|pt)|clamp\([^)]*(?:\([^)]*\)[^)]*)*\))(?:\s*/|\s)", value.strip() + " ")
    return size_px(m.group(1)) if m else None


def length_px(value: str, base: float = 16.0):
    """Parse a single CSS length into px (rem and em use the base). None when not a plain length."""
    m = re.fullmatch(r"\s*(-?\d*\.?\d+)(px|rem|em|pt)?\s*", value.strip().lower())
    if not m:
        return None
    n = float(m.group(1))
    unit = m.group(2) or ("px" if n == 0 else None)
    if unit is None:
        return None
    return n * {"px": 1.0, "rem": base, "em": base, "pt": 4 / 3}[unit]


# ----------------------------------------------------------------- reporting
def md_table(headers, rows) -> str:
    def cell(x):
        return str(x).replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(cell(h) for h in headers) + " |", "|" + "|".join(" --- " for _ in headers) + "|"]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def rel(path: str, root: str = "") -> str:
    try:
        return os.path.relpath(path, root or os.getcwd())
    except ValueError:
        return path


def top(counter: Counter, n: int = 5) -> str:
    return ", ".join(f"{k} ({v})" for k, v in counter.most_common(n))
