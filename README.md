# Human Design

A skill for AI coding agents that designs and builds interfaces that look made by a person for the product, not generated. It covers marketing sites, web apps, desktop apps, iOS and Android apps and online stores, and works in Claude Code, Claude, Codex and any agent that reads `SKILL.md`.

Ask an AI for a landing page and you get the page everyone gets: one default sans, a purple gradient, three icon cards. Ask a careful one and you get the newer defaults: cream paper, a serif, sage green. Human Design fixes the cause: nothing in a generated design was decided for the product. It makes the agent decide from the subject, write the decisions down, draw every state, then render the result in Chrome, measure it and fix what it finds.

## What it does

- **An identity per project.** The design is derived from the subject (its materials, documents, colours and terms) and recorded in `DESIGN.md` and `design.json`, so every later screen obeys the same decisions. The skill ships no finished palette, font pairing, layout or component kit to reuse.
- **Colour chosen as a set.** `palette.py` ranks a library of colour combinations (Figma's 100, analysed, plus its own for thin domains) for the product's category (24 presets: what users expect, what the category does from habit), the brief's words, the place of use and the hues the owner's other projects already use, and shows the candidates on real components in light and dark. `tokens.py` turns the chosen one into roles, chart colours and status colours in harmony, and fails a palette that is timid or whose colours compete.
- **A defence against its own signature.** `fingerprint.py` compares each design with the default looks AI tools converge on and with the owner's other projects, and fails when unrelated products look alike.
- **It looks at the result.** `render_check.py` drives headless Chrome, saves screenshots at several widths in light and dark (plus a blurred squint image), and measures what was drawn: fonts that silently fell back, contrast, characters per line, sideways scroll, small targets, centred text, off-scale spacing, animations that ignore reduced motion.
- **Nothing static.** Every control is drawn in six states and every data view in five before the screens are built. Landing pages get scroll motion built with CSS scroll timelines; `render_check.py --motion` proves it costs nothing: first paint complete, LCP and layout shift measured, nothing hidden without scripts, under reduced motion or from a crawler that does not scroll.
- **Real pictures.** Photographs of the subject, the owner's or from free libraries with their licences recorded, never hand-drawn stand-ins.
- **Tells in three generations and in native code.** `slop_check.py` finds first-generation defaults, the second-generation reactions (cream with a serif and terracotta, near-black with one neon), dead interface and stock copy, in HTML, CSS, JSX or TSX, Vue, Svelte, Astro, Liquid, SwiftUI and Compose. Deliberate choices are declared, not silenced.
- **Sourced.** Platform guidelines, research and practice with dates (November 2026), a licence table, and a list of what is unverified.

## Install

### Claude Code

```bash
claude plugin marketplace add thinhledev/human-design
claude plugin install human-design@human-design
```

Then ask for any UI work ("design the landing page", "this looks like AI", "the colours are dull"), or run `/human-design:human-design`.

### Claude (claude.ai, Cowork)

Add **Human Design** from the plugin directory once it is listed.

### Codex

```bash
codex plugin marketplace add thinhledev/human-design
```

Then install **Human Design** from the Plugins Directory.

### Any agent that reads Agent Skills

Copy `skills/human-design/` into the agent's skills folder (for example `~/.claude/skills/` or `~/.codex/skills/`).

## What it runs and what it sends

- The scripts are Python 3.8 or newer, standard library only, and make no network requests.
- `render_check.py` starts the Chrome, Chromium or Edge installed on your machine in headless mode with a temporary profile, and talks to it over the DevTools protocol on 127.0.0.1. It loads only the file or URL you give it (for example your dev server).
- `fingerprint.py --save NAME` writes a small JSON summary of a design (typeface names, colour families, radius; no code or content) to `~/.human-design/fingerprints`. `palette.py` and `fingerprint.py --taken` read it. Nothing else is written unless you ask for a file.
- When the skill needs photographs, it tells your agent to search free libraries (Pexels, Unsplash, Openverse, Wikimedia Commons) with the agent's own web tools and to record each photo's licence.

See [PRIVACY.md](PRIVACY.md).

## Licence

Free to use, including for commercial work, and what you make with it is yours. You may modify it for your own use. You may not sell it or republish it, modified or not, as a skill, plugin, template or package anywhere. See [LICENSE](LICENSE).

## Layout

| Path | What |
| --- | --- |
| `skills/human-design/SKILL.md` | Operating rules, job router, four workflows, scripts, lessons |
| `skills/human-design/references/` | Twenty references: identity, slop, typography, colour, colour combinations (and the generated catalogue), scroll motion, imagery, layout, states and motion, copy, critique, five surfaces, web platform, hand-off, sources; `references/data/` holds the combination library and the domain presets |
| `skills/human-design/scripts/` | Six Python CLIs plus `design_lib.py` |
| `skills/human-design/assets/` | `DESIGN.template.md`, a palette-board template, a state-sheet template and a directions template (structure only, no look) |
| `.claude-plugin/`, `.codex-plugin/`, `.agents/`, `plugin.json` | Plugin and marketplace manifests |
| `tests/` | Unit and end-to-end tests (the render tests need Chrome) |
| `evals/` | Three eval cases in the skill-creator format, all fictional |
| `plans/` | Specs for past changes |

## Scripts

Run them by path from `skills/human-design/`.

```bash
python3 scripts/palette.py --domain dev-tools --mood exact,warm --place dim --board board.html
python3 scripts/tokens.py --init design.json
python3 scripts/palette.py --apply hd-terminal-amber design.json
python3 scripts/tokens.py design.json --css tokens.css --tailwind theme.css
python3 scripts/render_check.py index.html --out shots --widths 390,1440 --schemes light,dark --squint --motion
python3 scripts/slop_check.py src --identity design.json --surface app
python3 scripts/fingerprint.py src --save my-project --against
python3 scripts/contrast_check.py --css tokens.css
```

## Develop

```bash
python3 -m unittest discover -s tests
claude plugin validate .
ln -s "$PWD/skills/human-design" ~/.claude/skills/human-design   # use the working copy locally
```

## Release

Raise `version` in `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `plugin.json` and the `metadata.version` in `SKILL.md`, keep the `SKILL.md` description at 1,024 characters or fewer (it is 1,022 now), run the tests, commit and push. The Claude directory picks up pushes to `main` and screens each version.

For Agensi, build the ZIP from the committed files:

```bash
rm -rf dist && mkdir -p dist/human-design
git archive HEAD:skills/human-design | tar -x -C dist/human-design
git show HEAD:LICENSE > dist/human-design/LICENSE
(cd dist && zip -qr human-design-skill.zip human-design)
```

Then in Agensi's Creator Studio, open the listing's editor, use **Replace Skill ZIP**, check that the name, summary and description were not overwritten by the auto-fill, set the version and changelog, and **Save & Resubmit for Review**. A new ZIP is scanned and reviewed (24 to 48 hours) while the previous version stays live. Listing: [Human Design: UI That Doesn't Look AI-Made](https://www.agensi.io/skills/human-design-ui-that-doesn-t-look-ai-made).
