# Colour

Checked 22 November 2026; sections 1 and 2 on 27 November 2026. Grades: documented, practice, research, vendor, inference.

## 1. Where the palette comes from

A palette is a set, chosen as a set. Picking a ground, then one accent, then
greys produced the same restrained, greyish result in every project (the
owner's complaint of November 2026: timid, wrong for the domain, the same hues
each time, no harmony). The method now has three inputs: what the category
expects, a proven combination, and the subject's own colours.

1. **Read the domain preset.** `python3 scripts/palette.py --domains` lists 24. Each states the convention users rely on (keep it), the category's habit (question it), and a twist. Research supports fitting the category: colour judged appropriate to the product type is preferred (research: Bottomley and Doyle 2006, Marketing Theory 6(1)), and colours carry brand personality, blue toward competence and red toward excitement (research: Labrecque and Milne 2012, JAMS 40). Logo counts show the other side: most of a category already wears the same hue, midnight blue in finance and healthcare, black in technology (vendor: Bynder, 15,388 logos). Fit the convention's structure; do not copy its hue.
2. **Rank combinations for the brief.** `python3 scripts/palette.py --domain ID --mood w1,w2,w3 --place P` scores the library (Figma's 100 combinations plus this skill's own for thin domains; `color-combinations.md`) on the domain, the brief's three words, the place of use, and the hues your other projects already lead with (read from the fingerprint registry). The first three it returns differ in harmony: one per direction.
3. **Look at them on components.** `palette.py --board board.html ...` shows each candidate on the same small screen in light and dark: text, a primary and a quiet button, a link, a focused field, a card with the highlight and the secondary, status chips and chart bars. Swatches lie; components do not. Publish the board for the owner when the host can.
4. **Twist it from the subject.** Apply the chosen one (`palette.py --apply ID design.json`), then move hues toward the world study's colours, each with a named source (the hardware's orange, a country's tiles, kiln brick). `--rotate DEG` turns every hue together and keeps the relations. Record what moved it in `palette.source`. A combination used unchanged is a template, and the registry will catch the next project that reaches for it.
5. **Give every colour a job.** Roles: ground, surface, ink, primary (actions, current item, links), secondary (a second kind of emphasis: the current filter, a category, the other series), highlight (what is new, selected text, a sticker), plus semantic colours. Write where each may appear: "Primary: buttons, current nav, links. Highlight: new items and the onboarding sticker. Never backgrounds."
6. **Semantic colours stay separate** from the brand: good, warn, bad, info. `tokens.py` moves a semantic hue to the far end of its range when it sits within 20 degrees of a coloured primary, and sets its chroma to follow the palette. Colour is never the only signal (WCAG 1.4.1): add an icon, a word or a shape.

Ratios still matter: most of the screen is ground and ink, the colours occupy
less (practice: the 60-30-10 rule, nngroup.com/articles/color-enhance-design/,
does not guarantee legibility). What changed is that "most of the screen is
neutral" no longer means "only one colour exists".

What reads as generated (see `slop.md`): an accent with no source (the
indigo-to-violet family is the Tailwind and tutorial default), gradients as
decoration, a different hue on every card with no lead, glow shadows, and the
replacement defaults: cream ground with a serif and terracotta, near-black with
one acid accent, and (this skill's own) a pale cool ground with one blue.

## 2. Harmony, chroma and competing colours

The classic colour-wheel relations name how the hues of a set relate
(practice). `palette.py --show ID` and `tokens.py` name the relation of any
palette; the thresholds are this skill's (inference).

| Harmony | Hues | In an interface |
| --- | --- | --- |
| monochromatic | one family, several lightnesses | calm, strong identity; needs lightness contrast and a separate semantic set |
| accented neutral | one hue on greys | the habitual default; fine for tools only when the subject asks for restraint |
| analogous | neighbours within about 75 degrees | warm or cool moods; give one hue the lead and let the others support |
| complementary | opposites | one leads (actions), the other marks a different kind of thing (highlight, a second series); never equal areas |
| split-complementary | one hue against the two either side of its opposite | contrast with less tension; good for primary plus two supporting roles |
| analogous with complement | two neighbours and the opposite of their middle | a warm family with one cool signal, or the reverse |
| triadic, square, tetradic | three or four spaced hues | playful and bright; needs strict roles or it becomes a different hue on every card |
| polychrome | many families | playful brands, kids, games, art; works only with a lead colour and lots of ground |

Three rules the scripts check:

- **Not timid.** If only one colour carries any hue (the rest grey or near-white), `tokens.py` fails. Give a second colour a job, or tint the ground from the subject. When restraint is the subject's (a legal register, a reading app), record `"palette-timid"` under `deliberate` with that reason.
- **No competing pair.** Two strong colours 60 to 110 degrees apart at similar chroma and lightness fight, because neither leads. Lightness difference is what most raises perceived harmony between two colours (research: Ou and Luo 2006, Color Research and Application 31(3)), so separate them by at least 0.15 in lightness, lower one's chroma, or move it to a neighbour or an opposite. Deliberately electric palettes (pop art, a festival) record `"palette-competing"`.
- **Directions differ.** The three directions use three different harmonies (`fingerprint.py --compare directions/*.html` fails when two share one), so the owner chooses between real alternatives.

Chroma is not a risk to minimise. Rich colour is right for food, kids, sport,
music and many consumer products; muted colour for tools used all day, health
and finance. The domain preset says which range the category reads as fitting.

## 3. Building it in OKLCH

OKLab and OKLCH (Ottosson, 2020) keep lightness, chroma and hue independent,
so a ramp with a fixed hue looks like one colour getting lighter, which HSL
does not (research: bottosson.github.io/posts/oklab/).

- Ranges: L 0 to 1, H 0 to 360, C below about 0.37, with the maximum depending on hue and gamut (practice: evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl).
- Ramps: hold hue, step lightness, let chroma peak in the middle. `tokens.py` does this and reduces chroma where a step would leave sRGB.
- A proven ramp shape (vendor: Radix, 12 steps): 1 to 2 backgrounds, 3 to 5 component fills, 6 to 8 borders, 9 to 10 solid fills, 11 to 12 text.
- States derive from the base: `oklch(from var(--accent) calc(l - 0.06) c h)` for hover (relative colour syntax; newly available since Sep 2024, give a fallback).
- Wide gamut: browsers clip out-of-gamut colours. Ship an sRGB value and override inside `@media (color-gamut: p3)` when the brand needs the stronger colour.
- CSS support: `oklch()`, `oklab()`, `color-mix()` widely available since Nov 2025; `light-dark()` widely available since Nov 2026; `contrast-color()` newly available since Apr 2026 (needs a fallback).

`design.json` holds the role palette (`color.palette`: ground, surface, ink,
primary, secondary, highlight, each as hue, chroma and lightness) and the
semantic hues. `tokens.py` generates ramps and roles for light and dark, a
categorical chart set (`chart-1` to `chart-6` by default, spaced around the
palette's own hues, alternating in lightness, each 3:1 on the ground), and a
contrast table. Fills that carry text (primary, highlight) are moved in
lightness until white or near-black text reaches 4.5:1. It exits with status 2
when a text pair fails, the palette is timid or two colours compete.

## 4. Contrast

WCAG 2.2 (documented: w3.org/WAI/WCAG22/Understanding/contrast-minimum.html and non-text-contrast.html):

| Case | AA | AAA |
| --- | --- | --- |
| Body text | 4.5:1 | 7:1 |
| Large text (24px, or 18.66px bold) | 3:1 | 4.5:1 |
| Control boundaries, states, meaningful graphics | 3:1 | none |

- No rounding: 4.499 fails. Disabled controls and logos are exempt. Placeholder text is text: it needs 4.5:1.
- Never lower contrast to de-emphasise; use size, weight or position (research: nngroup.com/articles/visual-hierarchy-ux-definition/).
- Text on photographs or gradients cannot be measured by ratio: add a scrim, a solid plate, or move the text. `render_check.py` lists such text for a look.
- APCA: WCAG 3.0 is a Working Draft (10 Sep 2026) and says its contrast algorithm "is yet to be determined" (documented: w3.org/TR/wcag-3.0/). Use APCA as a second opinion, mainly for dark mode and thin type: Lc 90 preferred and 75 minimum for body text, 60 for other content text, 45 for large headlines, 30 for placeholders, 15 for dividers (vendor: git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html). Conformance still means the WCAG 2.2 ratios.
- Tools: `python3 scripts/contrast_check.py FG BG [--size 14] [--fix]`, or `--css tokens.css` for every pair.

## 5. Dark mode

Dark mode is a second design, not an inversion.

- **Ground**: a dark grey, not pure black, for large surfaces. Material's base is #121212 (documented: codelabs.developers.google.com/codelabs/design-material-darktheme). Apple's guidance does not forbid black; OLED-first media apps use it deliberately.
- **Elevation by lightness**: higher surfaces get lighter, because shadows barely show on dark (Material tonal surfaces; Apple's base and elevated background sets).
- **Text**: not pure white on dark grey for body copy; Material uses 87%, 60% and 38% white for high, medium and disabled emphasis.
- **Accents**: lighter and slightly less saturated than in light mode; saturated colours "vibrate" on dark (documented, Material).
- **Images**: dim or frame images with white backgrounds (documented: developer.apple.com/design/human-interface-guidelines/dark-mode).
- **Contrast**: check every pair again; aim above the minimum with custom colours (Apple suggests 7:1).
- **Do not add an in-app theme switch** on Apple platforms unless the app has a real reason; follow the system (documented, Apple). On the web, follow `prefers-color-scheme` and let an explicit toggle win.
- Structure tokens so each role is defined once per mode (`tokens.py --css` writes this shape) and no component uses a literal colour.

## 6. Colour vision

About 1 in 12 men has a colour vision deficiency, most often red-green
(documented: nei.nih.gov). Check charts, statuses and form errors without
colour: do they still read? `tokens.py` simulates deutan and protan vision
(Machado, Oliveira and Fernandes 2009) on neighbouring chart colours and
reports the closest pair; under about 0.05 apart in OKLab, add a pattern or a
direct label. Links distinguished only by colour need 3:1
against the surrounding text, and an underline is simpler.

## 7. Checklist

- The domain preset read; its convention kept, its habit questioned.
- A combination ranked for the brief, seen on the palette board, and moved by the subject (palette.source says how).
- Every colour has a role, a job and a stated source; a lead colour is clear.
- Ground chosen for the place of use; neutrals tinted to match.
- Harmony named; not timid; no competing pair (`tokens.py` report), or each declared deliberate with a reason.
- The three directions use different harmonies; the primary hue family is not one your other projects lead with.
- Semantic colours distinct from the accent, never the only cue.
- All text pairs pass in every mode (`tokens.py` report, `contrast_check.py`).
- No gradient, glow or extra hue without a reason from the subject.
- Fingerprint is not within 75% of a default look (`fingerprint.py`).
