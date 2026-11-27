# Colour combinations: spec

Agreed 27 November 2026, after a grilling session. Built the same day on the color-combinations branch; the first trial (evals/color, old against new) found six bugs, all fixed and tested.

## Problem

The owner is disappointed with the palettes the skill picks. All four symptoms apply:

1. Timid and greyish: low chroma, pale tinted grounds, one small accent.
2. Wrong for the domain: the palette does not feel like the product's category.
3. Same hues every time: blue or indigo accents on cool grounds (the one saved project, knightship, is cool ground, indigo ink, blue and orange accent).
4. No harmony: colours are chosen one at a time, not as a set.

Root causes in the current skill: `color.md` says "one accent, mostly neutral" and treats extra hues as a tell, so restraint is the default; `design.json` can only hold one neutral hue and one or two accents, so a 3 to 5 colour combination cannot be expressed; nothing knows what a domain expects; nothing checks harmony.

## Decisions

| Topic | Decision |
| --- | --- |
| Philosophy | Convention plus twist. A domain preset records what users of that category expect and which combinations fit. The skill keeps that structure and takes the exact hues from the world study, avoiding hues the owner's other projects use. The skill still ships no finished look. |
| Figma library | Extract all 100 combinations from figma.com/resource-library/color-combinations (hexes are printed inside the palette images). Store each analysed: roles, harmony type, OKLCH lightness and chroma pattern, mood tags, plus the measured hexes and a link to the source anchor. |
| Coverage gaps | Figma leans lifestyle. Add our own combinations for thin domains (dark-ground tool palettes, data-dense finance, clinical health), same structure, marked `source: human-design`, grade inference. |
| Palette model | design.json gains a role palette: ground, surface, ink, primary, secondary, highlight (any may be empty), plus the harmony type. tokens.py ramps each role, keeps the dark-mode derivation and contrast gate. The old neutral/accent schema keeps working. |
| Mechanism | New `scripts/palette.py` ranks combinations from domain, three mood words, place of use and hues already taken; returns a shortlist with reasons. The model adapts one per direction from the world study. Same brief, same shortlist. |
| Hard checks | (a) the three directions use different harmony types; (b) chroma floor: flag a palette whose only saturated colour is a small accent unless declared deliberate; (c) tokens.py reports the harmony type and warns on hues in no recognisable relation; (d) unrelated projects may not share the primary hue family. |
| Palette board | A new step before the three directions: each candidate applied to real UI pieces (text, button, card, chart, status chips) in light and dark, published for the owner to pick. |
| Domains | About 24: dev tools, AI products, B2B SaaS, fintech and banking, crypto, insurance, healthcare, mental health and wellness, fitness, education and language learning, kids, food and restaurants, grocery, fashion, beauty, luxury, home and interiors, travel, real estate, legal and government, climate and energy, media and news, music and gaming, creative tools. |
| Data colours | tokens.py derives a categorical chart palette (5 to 8 series, spaced in OKLCH around the palette's hues) and nudges good, warn, bad, info into harmony with it, checked for contrast and colour-vision separation. |
| Proof | A colour eval with three briefs (dev tool, language-learning app, bakery), graders for domain fit, harmony, chroma and hue reuse. Run the old and new skill and show the palette boards side by side. |

## What the research supports (graded)

- research: colour that fits the product type is judged more appropriate (functional products in functional colours, sensory-social in sensory-social colours). Bottomley and Doyle 2006, Marketing Theory 6(1). orca.cardiff.ac.uk/id/eprint/2579
- research: colours map to brand personality dimensions (blue to competence, red to excitement). Labrecque and Milne 2012, J. Academy of Marketing Science 40. doi:10.1007/s11747-010-0245-y
- vendor: logo colour by sector, 15,388 logos: midnight blue leads finance, healthcare and energy; black leads technology. bynder.com/en/blog/the-most-and-least-used-colors-in-logos
- vendor: blue in about 85% of popular healthcare logos (99designs, reported by The Drum, 2018).
- practice: developer tools lean dark, high-contrast, one signal hue, semantic colours with meaning (third-party descriptions of Linear, Vercel, Supabase; not their own token docs).
- Most "colour by industry" writing is marketing opinion. Domain presets are therefore graded practice or inference, and each lists the category habit to question as well as the convention to keep: the research says fit matters, the logo counts say everyone already uses the same blue.

## Build order

1. Extract the 100 Figma combinations (stdlib PNG decoding, sample each swatch, verify against the printed hex on a sample by eye). Write `references/data/combinations.json`.
2. Analyse each: OKLCH per colour, harmony type, lightness and chroma pattern, suggested roles, mood tags, candidate domains.
3. Add our own combinations for thin domains, marked.
4. `references/domains.md` and domain data: per domain, convention to keep, habit to question, expected ground, temperature, chroma range, candidate combinations, room for a twist, evidence grade.
5. `scripts/palette.py`: `--domain`, `--mood`, `--place`, reads taken hues from the fingerprint registry; prints a ranked shortlist; `--board out.html` renders the palette board; `--apply ID design.json` writes the role palette.
6. tokens.py: role palette, harmony report and warning, chroma floor, chart series, semantic nudging, colour-vision separation; backwards compatible.
7. fingerprint.py: record harmony and chroma level; primary hue family reuse block; `--compare` reports when directions share a harmony type.
8. `assets/palette-board.template.html`.
9. Rewrite `color.md` sections 1 and add harmony; update `identity.md`, `SKILL.md` Workflow A (palette board step), `sources.md`, README.
10. Unit tests for palette.py ranking, tokens.py role palette and checks, fingerprint hue block.
11. `evals/color/` with three briefs and graders; run old and new; publish the side-by-side boards.
