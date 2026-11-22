# Colour

Checked 22 November 2026. Grades: documented, practice, research, vendor, inference.

## 1. Where the palette comes from

A palette is found, not picked from a swatch library.

1. **Take colours from the subject's world**, each with a named source (the world study in `identity.md`): the hardware's orange, produce, a terminal's phosphor green, podcast artwork, brick and glaze. If the product has photographs or a physical object, sample from them.
2. **Decide the ground first.** It is most of the pixels. White, a tinted white, cream, a mid grey, a dark: choose for where the product is used (bright shop floor, dim studio, office all day) and what the content is (photographs want a quiet ground; data wants contrast).
3. **Tint the neutrals** toward the ground's hue or the accent's. Pure greys look unconsidered beside a coloured accent (vendor: radix-ui.com/colors/docs/palette-composition/composing-a-palette). Strongly saturated greys clash with coloured components, especially on dark.
4. **One accent**, used for the thing that matters (primary action, current selection, links). A second accent only with a job of its own. Rule of thumb: about 60% dominant, 30% secondary, 10% accent, mostly neutral (research: nngroup.com/articles/color-enhance-design/). It does not guarantee legibility.
5. **Semantic colours are separate** from the brand: good, warning, bad, info. They never double as decoration, and colour is never the only signal (WCAG 1.4.1): add an icon, a word or a shape.
6. **Write down where each colour may appear.** "Accent: primary buttons, the current nav item, links. Never backgrounds."

What reads as generated (see `slop.md`): an accent with no source (the
indigo-to-violet family is the Tailwind and tutorial default), gradients as
decoration, a different hue on every card, glow shadows, and the replacement
defaults: cream ground with a serif and terracotta, near-black with one acid
accent.

## 2. Building it in OKLCH

OKLab and OKLCH (Ottosson, 2020) keep lightness, chroma and hue independent,
so a ramp with a fixed hue looks like one colour getting lighter, which HSL
does not (research: bottosson.github.io/posts/oklab/).

- Ranges: L 0 to 1, H 0 to 360, C below about 0.37, with the maximum depending on hue and gamut (practice: evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl).
- Ramps: hold hue, step lightness, let chroma peak in the middle. `tokens.py` does this and reduces chroma where a step would leave sRGB.
- A proven ramp shape (vendor: Radix, 12 steps): 1 to 2 backgrounds, 3 to 5 component fills, 6 to 8 borders, 9 to 10 solid fills, 11 to 12 text.
- States derive from the base: `oklch(from var(--accent) calc(l - 0.06) c h)` for hover (relative colour syntax; newly available since Sep 2024, give a fallback).
- Wide gamut: browsers clip out-of-gamut colours. Ship an sRGB value and override inside `@media (color-gamut: p3)` when the brand needs the stronger colour.
- CSS support: `oklch()`, `oklab()`, `color-mix()` widely available since Nov 2025; `light-dark()` widely available since Nov 2026; `contrast-color()` newly available since Apr 2026 (needs a fallback).

`design.json` holds the seeds (neutral hue and chroma; accent hue, chroma and
lightness; semantic hues). `tokens.py` generates ramps and roles for light and
dark and prints a contrast table. It exits with status 2 when a text pair
fails.

## 3. Contrast

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

## 4. Dark mode

Dark mode is a second design, not an inversion.

- **Ground**: a dark grey, not pure black, for large surfaces. Material's base is #121212 (documented: codelabs.developers.google.com/codelabs/design-material-darktheme). Apple's guidance does not forbid black; OLED-first media apps use it deliberately.
- **Elevation by lightness**: higher surfaces get lighter, because shadows barely show on dark (Material tonal surfaces; Apple's base and elevated background sets).
- **Text**: not pure white on dark grey for body copy; Material uses 87%, 60% and 38% white for high, medium and disabled emphasis.
- **Accents**: lighter and slightly less saturated than in light mode; saturated colours "vibrate" on dark (documented, Material).
- **Images**: dim or frame images with white backgrounds (documented: developer.apple.com/design/human-interface-guidelines/dark-mode).
- **Contrast**: check every pair again; aim above the minimum with custom colours (Apple suggests 7:1).
- **Do not add an in-app theme switch** on Apple platforms unless the app has a real reason; follow the system (documented, Apple). On the web, follow `prefers-color-scheme` and let an explicit toggle win.
- Structure tokens so each role is defined once per mode (`tokens.py --css` writes this shape) and no component uses a literal colour.

## 5. Colour vision

About 1 in 12 men has a colour vision deficiency, most often red-green
(documented: nei.nih.gov). Check charts, statuses and form errors without
colour: do they still read? Links distinguished only by colour need 3:1
against the surrounding text, and an underline is simpler.

## 6. Checklist

- Every colour has a role and a stated source.
- Ground chosen for the place of use; neutrals tinted to match.
- One accent, with rules for where it may appear.
- Semantic colours distinct from the accent, never the only cue.
- All text pairs pass in every mode (`tokens.py` report, `contrast_check.py`).
- No gradient, glow or extra hue without a reason from the subject.
- Fingerprint is not within 75% of a default look (`fingerprint.py`).
