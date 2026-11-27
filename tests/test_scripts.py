"""Unit and end-to-end tests for the human-design scripts.
Run: python3 -m unittest discover -s tests
The render test needs Chrome, Chromium or Edge and is skipped without one."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import contrast_check, design_lib as d, fingerprint, palette, render_check, slop_check, tokens  # noqa: E402,E401

SLOP = """<!doctype html><html lang="en"><head><title>Vite + React</title><style>
body{margin:0;font-family:"Inter",sans-serif;background:#fff;color:#111}
.hero{text-align:center;padding:96px 24px;background:linear-gradient(135deg,#6366f1,#a855f7);color:#fff}
h1{font-size:60px;background:linear-gradient(90deg,#fff,#e9d5ff);-webkit-background-clip:text;color:transparent}
.btn{display:inline-block;padding:12px 24px;border-radius:12px;background:#fff;color:#6366f1}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;text-align:center}
.card{border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.08);padding:24px}.card p{color:#b0b0b0}
</style></head><body><section class="hero"><h1>Elevate your workflow</h1>
<p>The all-in-one platform to supercharge your team. Seamless and effortless. Trusted by 10,000+ teams.</p>
<a class="btn" href="#">Get Started</a><a class="btn" href="#">Learn More</a></section>
<section class="grid"><div class="card">\U0001F680<h3>Fast</h3><p>Blazing fast.</p></div><div class="card">\U0001F512<h3>Secure</h3><p>Safe.</p></div>
<div class="card">✨<h3>Smart</h3><p>Lorem ipsum dolor sit amet.</p></div></section></body></html>"""

HUMAN = """<!doctype html><html lang="en"><head><title>Kilnfolk: booking for pottery studios</title><style>
:root{--bg:#f3f1ee;--ink:#1d2430;--glaze:#1f5f8b;--line:#c9c4bb}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 "Literata",Georgia,serif}
h1{font:600 44px/1.05 "Archivo",system-ui,sans-serif;max-width:14ch;margin:0}
.wrap{display:grid;grid-template-columns:7fr 5fr;gap:48px;padding:64px 48px 32px}
table{border-collapse:collapse;font-variant-numeric:tabular-nums}td{border-top:1px solid var(--line);padding:8px 16px 8px 0}
a.book{display:inline-block;padding:12px 20px;background:var(--glaze);color:#fff;border-radius:2px;text-decoration:none}
a.book:hover{background:#184c70}a.book:active{transform:scale(.97)}a.book:focus-visible{outline:2px solid #1d2430;outline-offset:2px}
@media (prefers-reduced-motion: reduce){a.book{transition:none}}
</style></head><body><div class="wrap"><div><h1>Fill the kiln, not a spreadsheet</h1>
<p>Classes, kiln slots and memberships in one calendar, for studios with up to twelve wheels.</p>
<a class="book" href="/trial">Start a 14-day trial</a></div>
<table><tr><td>Tue</td><td>Wheel throwing, cone 6</td><td>8 of 10</td></tr><tr><td>Thu</td><td>Glaze firing</td><td>full</td></tr></table></div></body></html>"""


def run(mod, args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        try:
            code = mod.main(args)
        except SystemExit as e:
            code = e.code
    return code, buf.getvalue()


class Colour(unittest.TestCase):
    def test_oklch_and_contrast(self):
        L, c, h = d.srgb_to_oklch(*d.parse_color("#6366f1")[:3])
        self.assertAlmostEqual(L, 0.585, places=2)
        self.assertAlmostEqual(h, 277, delta=1.5)
        self.assertAlmostEqual(d.wcag_contrast(d.parse_color("#777777"), d.parse_color("#fff")), 4.48, places=2)
        self.assertAlmostEqual(d.apca(d.parse_color("#000"), d.parse_color("#fff")), 106.0, delta=0.5)
        self.assertAlmostEqual(d.apca(d.parse_color("#fff"), d.parse_color("#000")), -107.9, delta=0.5)
        self.assertEqual(d.to_hex(d.parse_color("hsl(210 50% 40%)")), "#336699")
        self.assertEqual(d.parse_color("rgb(255 0 0 / 50%)")[3], 0.5)
        self.assertIsNone(d.parse_color("var(--x)"))
        rgb, c, clipped = d.fit_oklch(0.7, 0.4, 150)
        self.assertTrue(clipped and d.in_gamut(rgb))

    def test_parsing_sources(self):
        s = d.Source("a.tsx", 'import { Inter, Space_Grotesk } from "next/font/google"\n<div className="p-4 md:text-center" style="color:#fff">x</div>')
        self.assertEqual([f for f, _l, _h in d.font_mentions(s)], ["inter", "space grotesk"])
        self.assertIn("md:text-center", [t for t, _l in d.class_tokens(s)])
        css = d.Source("a.css", "@media (min-width:600px){.b{padding:1rem 2rem}} .a{color:red}")
        self.assertEqual([(sel, p) for sel, p, _v, _l, _at in d.declarations(css)], [(".b", "padding"), (".a", "color")])


class Fixes(unittest.TestCase):
    """Problems found when agents used the skill on real briefs."""

    def test_rem_ignores_body_base(self):
        spec = json.loads(json.dumps(tokens.STARTER))
        spec["type"]["base"] = 18
        self.assertEqual({t["px"]: t["value"] for t in tokens.type_tokens(spec)}[18], "1.125rem")

    def test_stars_are_not_emoji(self):
        self.assertIsNone(slop_check.EMOJI.search("Rated \u2605\u2605\u2605\u2606 \u2713 \u2192 \u25b2"))
        self.assertIsNotNone(slop_check.EMOJI.search("\U0001F680"))
        self.assertIsNotNone(slop_check.EMOJI.search("\u2764\uFE0F"))

    def test_grounds_and_status_colours(self):
        self.assertEqual(fingerprint.ground_of(d.parse_color("#f2f0eb")), "warm white")
        self.assertEqual(fingerprint.ground_of(d.parse_color("#f5f0e1")), "cream")
        css = d.Source("a.css", ":root{--bg:#fff;--success:#1a7f37}body{background:var(--bg)}a{color:#1f5f8b}"
                                ".stock{color:#1a7f37}.x{color:var(--success)}.y{color:var(--success)}")
        self.assertEqual(fingerprint.extract([css])["accent"], ["blue"])

    def test_import_is_followed_and_directions_do_not_clash(self):
        tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmp, "directions"))
        open(os.path.join(tmp, "tokens.css"), "w").write(":root{--bg:#f5f0e1}")
        open(os.path.join(tmp, "app.css"), "w").write('@import "tokens.css";\nbody{background:var(--bg)}')
        self.assertEqual(fingerprint.extract(d.collect([os.path.join(tmp, "app.css")]))["ground"], "cream")
        paths = []
        for n in "abc":
            paths.append(os.path.join(tmp, "directions", n + ".html"))
            open(paths[-1], "w").write('<style>body{font-family:"Archivo";background:#f3f1ee}h1{font-size:%dpx}</style>' % (30 + len(paths) * 9))
        _code, out = run(fingerprint, ["--compare"] + paths)
        self.assertNotIn("Clash:", out)
        self.assertIn("do not apply", out)

    def test_extra_colours_and_fonts(self):
        spec = json.loads(json.dumps(tokens.STARTER))
        spec.update(name="Pinboard")
        for role, fam in (("display", "Fraunces"), ("text", "Literata"), ("mono", "Commit Mono")):
            spec["type"][role]["family"] = fam
        spec["type"]["extra"] = {"hand": {"family": "Caveat", "fallback": "cursive"}}
        spec["color"]["extra"] = {"card-buff": "#e8d9b5", "pin": {"hue": 25, "chroma": 0.15, "lightness": 0.55}}
        data = tokens.build(spec)
        css, tw = tokens.css_vars(data), tokens.tailwind(data)
        self.assertIn('--font-hand: "Caveat", cursive;', css)
        self.assertIn("--card-buff: #e8d9b5;", css)
        self.assertIn("--pin: #", css)
        self.assertIn("--color-card-buff: var(--card-buff);", tw)
        self.assertIn("cardBuff", tokens.swift(data))


class Scripts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.slop = os.path.join(cls.tmp, "slop", "index.html")
        cls.human = os.path.join(cls.tmp, "human", "index.html")
        for path, text in ((cls.slop, SLOP), (cls.human, HUMAN)):
            os.makedirs(os.path.dirname(path))
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)

    def test_tokens(self):
        spec = os.path.join(self.tmp, "design.json")
        code, _ = run(tokens, ["--init", spec])
        self.assertEqual(code, 0)
        code, _ = run(tokens, [spec])  # placeholders must be refused
        self.assertNotEqual(code, 0)
        data = json.load(open(spec))
        data.update(name="Kilnfolk")
        data["type"]["display"]["family"] = "Archivo"
        data["type"]["text"]["family"] = "Literata"
        data["type"]["mono"]["family"] = "Commit Mono"
        data["color"]["palette"] = {
            "harmony": "complementary", "source": "kiln brick against cobalt glaze",
            "ground": {"hue": 70, "chroma": 0.012, "lightness": 0.975},
            "ink": {"hue": 250, "chroma": 0.03, "lightness": 0.22},
            "primary": {"hue": 245, "chroma": 0.11, "lightness": 0.46},
            "secondary": {"hue": 45, "chroma": 0.12, "lightness": 0.62}}
        json.dump(data, open(spec, "w"))
        css = os.path.join(self.tmp, "tokens.css")
        code, out = run(tokens, [spec, "--css", css, "--tailwind", os.path.join(self.tmp, "t.css"),
                                 "--swift", os.path.join(self.tmp, "T.swift"), "--kotlin", os.path.join(self.tmp, "T.kt")])
        self.assertEqual(code, 0, out)
        self.assertNotIn("FAIL", out)
        text = open(css).read()
        self.assertIn("--accent:", text)
        self.assertIn("prefers-color-scheme: dark", text)
        code, out = run(contrast_check, ["--css", css, "--pairs", "text:bg", "text-muted:surface", "on-accent:accent"])
        self.assertEqual(code, 0, out)

    def test_contrast(self):
        code, out = run(contrast_check, ["#777", "#fff", "--fix"])
        self.assertEqual(code, 2)
        self.assertIn("#767676", out)

    def test_slop_check(self):
        code, out = run(slop_check, [os.path.dirname(self.slop)])
        self.assertEqual(code, 2)
        for tid in ("type-default-face", "colour-purple", "colour-gradient", "image-emoji-icons", "copy-invented-proof", "copy-lorem",
                    "meta-generator-leftovers", "dead-no-pressed-state", "look-"):
            self.assertIn(tid, out)
        code, out = run(slop_check, [os.path.dirname(self.human)])
        self.assertEqual(code, 0, out)
        self.assertIn("0 strong", out)
        code, out = run(slop_check, ["--list"])
        self.assertGreater(out.count("- `"), 55)

    def test_deliberate_is_declared(self):
        ident = os.path.join(self.tmp, "ident.json")
        json.dump({"deliberate": {"colour-purple": "the brand has been violet since 2019"}}, open(ident, "w"))
        _code, out = run(slop_check, [os.path.dirname(self.slop), "--identity", ident])
        self.assertIn("Declared deliberate", out)
        self.assertIn("violet since 2019", out)

    def test_fingerprint(self):
        a = fingerprint.extract(d.collect([os.path.dirname(self.slop)]))
        b = fingerprint.extract(d.collect([os.path.dirname(self.human)]))
        self.assertEqual(fingerprint.nearest_default(a)[0][0].split(" (")[0], "framework default")
        self.assertGreaterEqual(fingerprint.nearest_default(a)[0][1], 0.75)
        self.assertLess(fingerprint.nearest_default(b)[0][1], 0.55)
        self.assertLess(fingerprint.similarity(a, b)[0], 0.5)
        self.assertGreater(fingerprint.similarity(a, a)[0], 0.95)
        reg = os.path.join(self.tmp, "reg")
        run(fingerprint, [os.path.dirname(self.slop), "--save", "one", "--registry", reg])
        code, out = run(fingerprint, [os.path.dirname(self.slop), "--against", "--registry", reg])
        self.assertEqual(code, 2)
        self.assertIn("same product", out)

    @unittest.skipUnless(render_check.find_chrome(), "no Chrome, Chromium or Edge")
    def test_render_check(self):
        out_dir = os.path.join(self.tmp, "shots")
        code, out = run(render_check, [self.slop, "--out", out_dir, "--widths", "390,1280", "--squint"])
        self.assertEqual(code, 2)
        self.assertIn("did not load", out)
        self.assertIn("contrast", out)
        self.assertIn("centred", out)
        self.assertEqual(len([f for f in os.listdir(out_dir) if f.endswith(".png")]), 4)
        code, out = run(render_check, [self.human, "--widths", "1280", "--json"])
        facts = json.loads(out)[0]
        self.assertEqual(facts["lowContrastCount"], 0)
        self.assertEqual(facts["overflowX"], 0)
        self.assertLess(facts["centeredShare"], 0.2)

    @unittest.skipUnless(render_check.find_chrome(), "no Chrome, Chromium or Edge")
    def test_render_settles_and_names_what_was_drawn(self):
        page = os.path.join(self.tmp, "dark", "dial.html")
        os.makedirs(os.path.dirname(page))
        with open(page, "w", encoding="utf-8") as fh:
            fh.write("""<!doctype html><html lang="en"><head><title>Dial</title><style>
body{margin:0;background:#141414;color:#eee;font:16px/1.5 Georgia,serif}
@keyframes rise{from{opacity:0}to{opacity:1}} h1{font-size:40px;animation:rise 3s both}
@media (prefers-reduced-motion: reduce){h1{animation:none}}
.toast{position:fixed;left:0;right:0;top:1500px;height:80px;background:#f00}
.led{display:inline-block;width:30px;height:30px}.a{box-shadow:0 0 6px #f00}.b{box-shadow:0 0 6px #0f0}.c{box-shadow:0 0 6px #00f}
.d{box-shadow:0 0 6px #ff0}.e{box-shadow:0 0 6px #0ff}.small{font-size:10px}
</style></head><body><h1>Dial</h1><p style="height:1800px">Body text long enough to count in the measurement.</p>
<svg width="300" height="60"><text x="0" y="20" font-size="8">0 10 20 30 40 50 60 70 80 90 100 110 120</text></svg>
<span class="led a"></span><span class="led b"></span><span class="led c"></span><span class="led d"></span><span class="led e"></span>
<p class="small">Small print that is a decision here.</p><div class="toast"></div></body></html>""")
        with open(os.path.join(os.path.dirname(page), "design.json"), "w") as fh:
            json.dump({"deliberate": {"small-text": "tick labels like a printed dial"}}, fh)
        out_dir = os.path.join(self.tmp, "dshots")
        code, out = run(render_check, [page, "--out", out_dir, "--widths", "1280", "--tile", "0"])
        self.assertEqual(os.listdir(out_dir), ["dial-1280-dark.png"])
        self.assertIn("drew a dark ground", out)
        self.assertIn("declared deliberate: tick labels", out)
        self.assertNotIn("distinct shadows", out)
        code, out = run(render_check, [page, "--widths", "1280", "--json"])
        facts = json.loads(out)[0]
        self.assertGreater(facts["svgChars"], 0)
        self.assertNotIn(8, [size for size, _share in facts["sizes"]])
        self.assertEqual(facts["shadows"], 1)


class Colour(unittest.TestCase):
    """Colour chosen as a set: the combination library, domain presets, harmony and the palette checks."""

    @staticmethod
    def spec(**palette_roles):
        s = json.loads(json.dumps(tokens.STARTER))
        s.update(name="Test")
        for role, fam in (("display", "Archivo"), ("text", "Literata"), ("mono", "Commit Mono")):
            s["type"][role]["family"] = fam
        s["color"]["palette"] = {"harmony": "", "source": "test", **palette_roles}
        return s

    def test_library_loads_and_is_complete(self):
        combos, domains = palette.load()
        self.assertEqual(len([c for c in combos if c.startswith("figma-")]), 100)
        self.assertEqual(len(domains), 24)
        for c in combos.values():
            self.assertEqual(len(c["colours"]), 4, c["id"])
            for h in c["colours"]:
                self.assertIsNotNone(d.parse_color(h), (c["id"], h))
        for dm in domains.values():
            for cid in dm["candidates"]:
                self.assertIn(cid, combos, (dm["id"], cid))
        text = open(os.path.join(HERE, "..", "references", "data", "domains.json"), encoding="utf-8").read()
        self.assertNotIn("\u2014", text)  # no em dashes in written content

    def test_harmony_names(self):
        def h(*lch):
            return d.classify_harmony([(L, c, hh, 1) for L, c, hh in lch])[0]
        self.assertEqual(h((0.5, 0.15, 30), (0.7, 0.1, 32), (0.3, 0.08, 28)), "monochromatic")
        self.assertEqual(h((0.97, 0.01, 250), (0.55, 0.15, 260)), "accented neutral")
        self.assertEqual(h((0.6, 0.15, 40), (0.6, 0.14, 220)), "complementary")
        self.assertEqual(h((0.6, 0.15, 30), (0.6, 0.15, 70)), "analogous")
        self.assertEqual(h((0.98, 0.05, 105), (0.5, 0.15, 30)), "accented neutral")  # cream is a ground, not a hue
        self.assertEqual(d.competing_pairs([("a", 0.6, 0.15, 40), ("b", 0.62, 0.14, 130)]), [("a", "b", 90)])
        self.assertEqual(d.competing_pairs([("a", 0.4, 0.15, 40), ("b", 0.8, 0.14, 130)]), [])

    def test_ranking_fits_the_domain_and_skips_taken_hues(self):
        combos, domains = palette.load()
        top = palette.shortlist(combos, domains["dev-tools"], ["technical"], "dim", {}, 6)
        self.assertTrue(all(an["has_dark"] for _s, _c, an, _w in top[:3]))
        self.assertEqual(len({an["harmony"] for _s, _c, an, _w in top[:3]}), 3)
        food = palette.shortlist(combos, domains["food"], [], "", {}, 3)
        self.assertTrue(all(an["temperature"] == "warm" for _s, _c, an, _w in food))
        first = food[0][2]["primary_family"]
        again = palette.shortlist(combos, domains["food"], [], "", {first: ["older-project"]}, 3)
        self.assertNotEqual(again[0][1]["id"], food[0][1]["id"])
        self.assertEqual(palette.guess_domain("an app to learn a new language", domains)[0][1], "education")

    def test_apply_board_and_tokens(self):
        tmp = tempfile.mkdtemp()
        spec = os.path.join(tmp, "design.json")
        json.dump(self.spec(ground={"hue": 0, "chroma": 0}, primary={"hue": 0, "chroma": 0, "lightness": 0.5}), open(spec, "w"))
        code, out = run(palette, ["--apply", "figma-36", spec])
        self.assertEqual(code, 0, out)
        data = json.load(open(spec))
        self.assertIn("primary", data["color"]["palette"])
        self.assertIn("figma-36", data["color"]["palette"]["source"])
        code, out = run(tokens, [spec, "--css", os.path.join(tmp, "t.css")])
        self.assertEqual(code, 0, out)
        css = open(os.path.join(tmp, "t.css")).read()
        for role in ("--second:", "--highlight:", "--chart-1:", "--chart-6:", "--on-highlight:"):
            self.assertIn(role, css)
        self.assertIn("Harmony:", out)
        board = os.path.join(tmp, "board.html")
        code, out = run(palette, ["--domain", "kids", "--board", board, "--top", "3"])
        self.assertEqual(code, 0, out)
        page = open(board).read()
        self.assertEqual(page.count('class="cand"'), 3)
        self.assertIn("--chart-1:", page)

    def test_timid_and_competing_palettes_fail_unless_deliberate(self):
        timid = self.spec(ground={"hue": 250, "chroma": 0.004, "lightness": 0.985}, primary={"hue": 255, "chroma": 0.15, "lightness": 0.5})
        data = tokens.build(timid)
        self.assertTrue(data["palette"]["timid"])
        timid["deliberate"] = {"palette-timid": "a tax form: the register is plain on purpose"}
        self.assertTrue(tokens.build(timid)["palette"]["timid_ok"])
        rich = self.spec(ground={"hue": 70, "chroma": 0.02, "lightness": 0.97}, primary={"hue": 40, "chroma": 0.15, "lightness": 0.6},
                         secondary={"hue": 130, "chroma": 0.14, "lightness": 0.62})
        data = tokens.build(rich)
        self.assertFalse(data["palette"]["timid"])
        self.assertTrue(data["palette"]["competing"])

    def test_fills_carry_text_and_status_moves_off_the_primary(self):
        spec = self.spec(ground={"hue": 60, "chroma": 0.01, "lightness": 0.98}, primary={"hue": 35, "chroma": 0.18, "lightness": 0.6},
                         highlight={"hue": 95, "chroma": 0.15, "lightness": 0.62})
        data = tokens.build(spec)
        for mode in data["modes"]:
            r = data["roles"][mode]
            self.assertGreaterEqual(d.wcag_contrast(r["on-accent"]["rgb"], r["accent"]["rgb"]), 4.5)
            self.assertGreaterEqual(d.wcag_contrast(r["on-highlight"]["rgb"], r["highlight"]["rgb"]), 4.5)
        self.assertGreaterEqual(d.hue_diff(tokens.semantic_hues({"bad": 27}, {"hue": 35, "chroma": 0.18})["bad"], 35), 18)

    def test_older_schema_still_builds(self):
        spec = self.spec(ground={"hue": 0, "chroma": 0}, primary={"hue": 0, "chroma": 0, "lightness": 0.5})
        spec["color"].pop("palette")
        spec["color"]["neutral"] = {"hue": 70, "chroma": 0.012}
        spec["color"]["accent"] = {"hue": 245, "chroma": 0.11, "lightness": 0.46}
        spec["color"]["second"] = {"hue": 45, "chroma": 0.12, "lightness": 0.62}
        data = tokens.build(spec)
        self.assertIn("second", data["roles"]["light"])
        self.assertFalse(data["palette"]["timid"])

    def test_primary_hue_reuse_clashes_and_directions_need_different_harmonies(self):
        a = {"fonts": ["x"], "display": "x", "text": "x", "accent": ["blue"], "ground": "white"}
        b = {"fonts": ["y"], "display": "y", "text": "y", "accent": ["blue"], "ground": "cream"}
        self.assertTrue(any("primary hue family blue" in c for c in fingerprint.clash("a", a, "b", b)))
        tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmp, "directions"))
        pages = {"a": "#c2410c;--b:#0e7490", "b": "#b91c1c;--b:#0369a1", "c": "#15803d;--b:#16a34a"}
        paths = []
        for n, cols in pages.items():
            paths.append(os.path.join(tmp, "directions", n + ".html"))
            first, second = cols.split(";--b:")
            open(paths[-1], "w").write('<style>body{font-family:"F%s";background:#fff}a{color:%s}.x{color:%s}.y{color:%s}</style>'
                                       % (n, first, second, second))
        code, out = run(fingerprint, ["--compare"] + paths)
        self.assertEqual(code, 2, out)
        self.assertIn("share a complementary palette", out)


class TrialFixes(unittest.TestCase):
    """Problems found by the first colour trial (27 November 2026)."""

    def test_highlight_is_not_a_second_primary(self):
        combos, _ = palette.load()
        roles = palette.analyse(combos["figma-36"])["roles"]
        self.assertIn("highlight", roles)
        for other in ("secondary", "highlight"):
            self.assertGreaterEqual(d.hue_diff(roles[other]["hue"], roles["primary"]["hue"]), 25)

    def test_brief_outweighs_candidate_list(self):
        combos, domains = palette.load()
        moods, _ = palette.brief_tags(["warm", "encouraging", "grown-up"])
        avoid, _ = palette.brief_tags(["childish"])
        top = palette.shortlist(combos, domains["education"], moods, "", {}, 6, avoid)
        self.assertNotIn("figma-28", [c["id"] for _s, c, _a, _w in top[:3]])

    def test_magenta_is_pink(self):
        self.assertEqual(d.hue_name(348, 0.15, 0.65), "pink")
        self.assertEqual(d.hue_name(20, 0.15, 0.55), "red")

    def test_boards_are_skipped_in_folders(self):
        tmp = tempfile.mkdtemp()
        open(os.path.join(tmp, "index.html"), "w").write("<style>a{color:#c2410c}</style>")
        open(os.path.join(tmp, "board.html"), "w").write("<!-- human-design:board --><style>a{color:#0369a1}</style>")
        self.assertEqual([os.path.basename(x.path) for x in d.collect([tmp])], ["index.html"])
        self.assertEqual(len(d.collect([os.path.join(tmp, "board.html")])), 1)

    def test_motion_notes_are_not_tokens(self):
        spec = Colour.spec(ground={"hue": 70, "chroma": 0.02, "lightness": 0.97}, primary={"hue": 40, "chroma": 0.15, "lightness": 0.5},
                           secondary={"hue": 200, "chroma": 0.1, "lightness": 0.5})
        spec["motion"]["character"] = "quick and flat"
        self.assertNotIn("--dur-character", tokens.css_vars(tokens.build(spec)))


MOTION_BAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Bad</title><style>
body{margin:0;font:18px/1.5 Georgia,serif}.reveal{opacity:0;transform:translateY(40px);transition:opacity .8s,transform .8s}.reveal.in{opacity:1;transform:none}
section{min-height:90vh;padding:40px}</style></head><body><section><h1 class="reveal">Fresh bread every Saturday</h1></section>
<section><h2 class="reveal">The loaves</h2><p class="reveal">Country loaf, seeded rye and spelt with honey.</p></section>
<script>setTimeout(()=>{const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)e.target.classList.add('in')}));
document.querySelectorAll('.reveal').forEach(el=>io.observe(el))},1500);</script></body></html>"""

MOTION_GOOD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Good</title><style>
body{margin:0;font:18px/1.5 Georgia,serif}section{min-height:90vh;padding:40px}
@keyframes rise{from{opacity:0;transform:translateY(32px)}}
@media (prefers-reduced-motion:no-preference){@supports (animation-timeline:view()){
.reveal{animation:rise linear both;animation-timeline:view();animation-range:entry 5% cover 30%}}}
</style></head><body><section><h1>Fresh bread every Saturday</h1></section>
<section><h2 class="reveal">The loaves</h2><p class="reveal">Country loaf, seeded rye and spelt with honey.</p></section></body></html>"""


class MotionAndImagery(unittest.TestCase):
    """Scroll motion that costs no speed or SEO, and real pictures before drawn ones (27 November 2026)."""

    def write(self, name, text):
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return path

    def test_static_tells(self):
        _code, out = run(slop_check, [self.write("bad.html", MOTION_BAD), "--surface", "marketing"])
        self.assertIn("motion-hidden-start", out)
        _code, out = run(slop_check, [self.write("good.html", MOTION_GOOD), "--surface", "marketing"])
        self.assertNotIn("motion-hidden-start", out)
        lenis = self.write("app.js", "import Lenis from 'lenis'\nconst l = new Lenis()\nwindow.addEventListener('scroll', () => move())\n")
        _code, out = run(slop_check, [lenis])
        self.assertIn("motion-scroll-hijack", out)
        self.assertIn("motion-scroll-handler", out)
        loaf = '<svg viewBox="0 0 64 48"><ellipse cx="32" cy="24" rx="28" ry="18"/><path d="M10 20 Q32 4 54 20"/></svg>'
        drawn = self.write("index.html", "<!doctype html><title>Bakery</title><main>" + loaf * 4 + "</main>")
        _code, out = run(slop_check, [drawn, "--surface", "marketing"])
        self.assertIn("image-drawn-art", out)
        photo = self.write("index.html", '<!doctype html><title>Bakery</title><main><img src="loaf.webp" alt="A loaf">' + loaf * 4 + "</main>")
        _code, out = run(slop_check, [photo, "--surface", "marketing"])
        self.assertNotIn("image-drawn-art", out)

    @unittest.skipUnless(render_check.find_chrome(), "no Chrome, Chromium or Edge")
    def test_motion_render(self):
        code, out = run(render_check, [self.write("bad.html", MOTION_BAD), "--widths", "1280", "--motion"])
        self.assertEqual(code, 2)
        for phrase in ("first screen were invisible", "prefers-reduced-motion", "tall viewport", "JavaScript off"):
            self.assertIn(phrase, out)
        code, out = run(render_check, [self.write("good.html", MOTION_GOOD), "--widths", "1280", "--motion"])
        self.assertEqual(code, 0, out)
        self.assertIn("Scroll timelines in CSS: yes", out)


if __name__ == "__main__":
    unittest.main()
