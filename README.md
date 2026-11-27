# Human design

An agent skill for designing and building interfaces that look made by a person for this product, not generated. It covers marketing sites, web apps, desktop apps, iOS and Android apps and online stores, and works in Claude Code, Codex and any agent that reads `SKILL.md`.

**This repository is private.** The skill is sold on Agensi under a proprietary license (see [LICENSE](LICENSE)). Don't make the repository public, publish it to a plugin marketplace, or put its contents in a free skill.

| | |
| --- | --- |
| Listing | [Human Design: UI That Doesn't Look AI-Made](https://www.agensi.io/skills/human-design-ui-that-doesn-t-look-ai-made) |
| Price | $9.99 one-time |
| Version | 1.1 submitted 27 November 2026 (in review); 1.0 live until it is approved |
| Category | Frontend & Web Apps |
| Companions | `smooth-ux` (free; the interaction-state pass this skill builds on), `seo` |

## What makes it different

- **An identity per project.** The design is derived from the subject (its materials, documents, colours and terms) and recorded in `DESIGN.md` and `design.json`, so every later screen obeys the same decisions. The skill ships no finished palette, font pairing, layout or component kit to reuse.
- **Colour chosen as a set.** `palette.py` ranks a library of colour combinations (Figma's 100, analysed, plus its own for thin domains) for the product's category (24 presets: what users expect, what the category does from habit), the brief's words, the place of use and the hues the owner's other projects already use, and shows the candidates on real components in light and dark. `tokens.py` turns the chosen one into roles, chart colours and status colours in harmony, and fails a palette that is timid or whose colours compete.
- **A defence against its own signature.** `fingerprint.py` compares each design with the default looks AI tools converge on and with the owner's other projects, and fails when unrelated products look alike.
- **It looks at the result.** `render_check.py` drives headless Chrome, saves screenshots at several widths in light and dark (plus a blurred squint image), and measures what was drawn: fonts that silently fell back, contrast, characters per line, sideways scroll, small targets, centred text, off-scale spacing, animations that ignore reduced motion.
- **Nothing static.** Every control is drawn in six states and every data view in five before the screens are built. Landing pages get scroll motion built with CSS scroll timelines; `render_check.py --motion` proves it costs nothing: first paint complete, LCP and layout shift measured, nothing hidden without scripts, under reduced motion or from a crawler that does not scroll.
- **Real pictures.** Photographs of the subject, the owner's or from free libraries with their licences recorded, never hand-drawn stand-ins.
- **Tells in three generations and in native code.** `slop_check.py` finds first-generation defaults, the second-generation reactions (cream with a serif and terracotta, near-black with one neon), dead interface and stock copy, in HTML, CSS, JSX or TSX, Vue, Svelte, Astro, Liquid, SwiftUI and Compose. Deliberate choices are declared, not silenced.
- **Sourced.** Platform guidelines, research and practice with dates (November 2026), a licence table, and a list of what is unverified.

## Layout

| Path | What | In the sale ZIP |
| --- | --- | --- |
| `SKILL.md` | Operating rules, job router, four workflows, scripts, lessons | Yes |
| `references/` | Eighteen references: identity, slop, typography, colour, colour combinations (and the generated catalogue), layout, states and motion, copy, critique, five surfaces, web platform, hand-off, sources; `references/data/` holds the combination library and the domain presets | Yes |
| `scripts/` | Six Python CLIs plus `design_lib.py` | Yes |
| `assets/` | `DESIGN.template.md`, a palette-board template, a state-sheet template and a directions template (structure only, no look) | Yes |
| `LICENSE` | Proprietary license for buyers | Yes |
| `tests/` | Unit and end-to-end tests (the render test needs Chrome) | No |
| `evals/` | Two eval cases in the skill-creator format, both fictional | No |
| `README.md` | This file | No |

## Scripts

Python 3.8 or newer, standard library only. `render_check.py` needs Chrome, Chromium or Edge.

```bash
python3 scripts/palette.py --domain dev-tools --mood exact,warm --place dim --board board.html
python3 scripts/tokens.py --init design.json
python3 scripts/palette.py --apply hd-terminal-amber design.json
python3 scripts/tokens.py design.json --css tokens.css --tailwind theme.css
python3 scripts/render_check.py index.html --out shots --widths 390,1440 --schemes light,dark --squint
python3 scripts/slop_check.py src --identity design.json --surface app
python3 scripts/fingerprint.py src --save my-project --against
python3 scripts/contrast_check.py --css tokens.css
```

## Tests

```bash
python3 -m unittest discover -s tests
```

## Release a new version to Agensi

1. Keep `SKILL.md`'s `description` at 1,024 characters or fewer (Agensi's limit; it is 1,022 now) and keep dated facts dated ("checked <date>").
2. Run the tests, commit and push. Then build the ZIP from the committed files (this leaves out `evals/`, `tests/`, `plans/`, this README and any `__pycache__`):

   ```bash
   rm -rf dist && mkdir -p dist/human-design
   git archive HEAD SKILL.md LICENSE references scripts assets | tar -x -C dist/human-design
   (cd dist && zip -qr human-design-skill.zip human-design)
   ```

3. In Agensi, Creator Studio, open the listing's editor (the pencil on its card), open **Replace Skill ZIP**, and upload `dist/human-design-skill.zip`. Agensi fills fields from the ZIP's frontmatter: check that the name, summary and full description are still yours. Set the version (one higher than the current) and write the changelog.
4. **Save & Resubmit for Review**. Agensi then offers its paid tools (decline unless you want them) and asks for a final review of auto-filled fields, permissions and price. A new ZIP goes through a security scan and review (24 to 48 hours) while the previous version stays live; text, price and image changes go live at once, and a changelog can be edited later without review.

## Installing locally

```bash
ln -s "$PWD" ~/.claude/skills/human-design
```
