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
import contrast_check, design_lib as d, fingerprint, render_check, slop_check, tokens  # noqa: E402,E401

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
        data["color"]["neutral"] = {"hue": 70, "chroma": 0.012}
        data["color"]["accent"] = {"hue": 245, "chroma": 0.11, "lightness": 0.46}
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


if __name__ == "__main__":
    unittest.main()
