# Typography

Type is most of an interface, and the typeface is the first thing that makes
one product look like another. Facts below were checked on 22 November 2026;
sources are given as site and path. Grades: documented (a standard or official
guideline), practice (a recognised practitioner's published guide), vendor,
inference.

## 1. Choosing typefaces

Choose for the subject, then check the practicalities. Never start from "what
do I usually use".

1. **Write three words for the voice** from the brief (for example: exact, warm, unhurried). Reject any face that does not carry at least two of them at text size.
2. **Look in the subject's world.** What do its documents, signs, packaging, instruments, tickets or screens look like? A railway timetable, a seed catalogue, a legal filing and a synth panel each imply different letterforms.
3. **Text face first.** It carries 90% of the words. Test it at 14 to 16px in a real paragraph and a real table: x-height, the shapes of a, g, l, 1, 0, O, and whether it has tabular figures.
4. **Then decide whether a second face is needed at all.** One family with weights, widths or optical sizes goes far (practice: practicaltypography.com/mixing-fonts.html; fonts.google.com/knowledge/choosing_type/pairing_typefaces). Add a display face only when headings need a voice the text face cannot give.
5. **Give every face one job** and keep it: display, text, data or code. Most products tolerate two families; a third is usually a mono for real code or tabular data.
6. **Check the licence and delivery**: where the files come from, whether self-hosting is allowed, WOFF2, the weights actually needed (two or three), a variable font when more.
7. **Record the choice and the reason** in DESIGN.md, including the fallback stack.

Pairing that holds up (practice; Butterick and Google's guide disagree on how
much contrast, so use judgement):

- Pair by contrast of structure (a serif with a sans, a wide display with a quiet text face) while sharing something: x-height, proportions, era or the same designer.
- Two similar grotesques clash. So do a display face used for body text and Light or Thin weights at small sizes (Apple: avoid them).

### The defaults, and the next defaults

These are fine typefaces; the problem is that nobody chose them.

| Status | Faces | Evidence |
| --- | --- | --- |
| Default now | Inter, Geist, Space Grotesk, Instrument Serif, system-ui | Named by Anthropic as the generic look (claude.com/blog/improving-frontend-design-through-skills, vendor) and measured in a scan of about 1,500 Show HN pages (adriankrebs.ch/blog/design-slop/, 20 Apr 2026, single author) |
| Default by reputation | Plus Jakarta Sans, Poppins, Outfit, Sora, Manrope, DM Sans, Montserrat, Playfair Display | Inference from template and tutorial use; no measurement found |
| Becoming defaults | Bricolage Grotesque, IBM Plex, Source Sans 3, Newsreader, Crimson Pro, JetBrains Mono, Fraunces | Inference: the anti-generic prompts recommend exactly these, so generated work converges on them next |

Rule: a face from this table needs a reason in DESIGN.md that names the
subject. "It is clean and modern" is not a reason. `fingerprint.py` and
`slop_check.py` flag the first two rows.

### Free faces worth knowing

All are SIL Open Font License unless noted, hosted on Google Fonts unless noted
(verified in github.com/google/fonts metadata). Character notes are judgement.

| Face | Class | Character and fit |
| --- | --- | --- |
| Instrument Sans | neo-grotesque, width axis | brand UI with some tension |
| Hanken Grotesk | neo-grotesque | quiet product text |
| Schibsted Grotesk | grotesque | news, publishing |
| Familjen Grotesk | grotesque | warm Scandinavian brands |
| Figtree | geometric | friendly, clean apps |
| Onest | humanist sans | Latin plus Cyrillic UI |
| Mona Sans, Hubot Sans | grotesque, width axis | developer brands (also on GitHub) |
| Atkinson Hyperlegible Next | humanist grotesque | public services, low-vision legibility |
| Public Sans | neo-grotesque | government, forms |
| Libre Franklin | grotesque | American news feel |
| Work Sans | grotesque | mid-size screen text |
| Commissioner | humanist sans, flare axis | civic, cultural |
| Red Hat Display and Text | geometric humanist | open-source and tech brands |
| Recursive | sans to mono, casual axis | code beside UI |
| Roboto Flex | neo-grotesque, 13 axes | finely tuned UI |
| Archivo | grotesque, width axis | sport, strong headlines |
| Unbounded | wide display sans | events, loud brands |
| Syne | display sans | art and culture |
| Gabarito | geometric display | playful education |
| Literata | old-style serif | long-form reading |
| Source Serif 4 | transitional, optical size | docs, academic |
| Spectral | old-style | elegant screen reading |
| EB Garamond | old-style | books, humanities |
| Cormorant | old-style display | high contrast, large sizes only |
| Roboto Serif | transitional, many axes | serif for UI |
| Young Serif | heavy old-style display | warm headlines |
| Gloock, Bodoni Moda | didone | luxury, magazines |
| Bitter, Zilla Slab | slab | sturdy reading, tech brands |
| Commit Mono (GitHub: eigilnikolajsen/commit-mono) | mono | neutral code |
| Departure Mono (GitHub: rektdeckard/departure-mono) | pixel mono | lo-fi; use multiples of 11px |
| Monaspace (GitHub: githubnext/monaspace) | mono superfamily | five matching voices |

Other libraries: Collletttivo (all OFL: Ronzino, Apfel Grotezk, Borges),
The League of Moveable Type (OFL: League Spartan, League Gothic, Junction),
Open Foundry (a directory; licences vary), Uncut (a catalogue; licences are per
font). Fontshare is free for commercial use but not open source and its licence
text could not be retrieved: link to it, do not bundle or assume self-hosting.
Paid faces from independent foundries are often the most distinctive choice;
suggest them when the project has a budget.

### System fonts

When the product should feel native (desktop tools, settings, utilities), the
system face is the right decision, stated as one:

- Apple: SF Pro; default 17pt on iOS, 13pt on macOS; minimum 11pt and 10pt (documented: developer.apple.com/design/human-interface-guidelines/typography).
- Windows 11: Segoe UI Variable; body 14/20; minimum 12px regular, 14px semibold; sentence case (documented: learn.microsoft.com/en-us/windows/apps/design/signature-experiences/typography).
- Android: Roboto is the Material 3 default.
- Web stack: `system-ui, sans-serif`. `system-ui` resolves by OS language (on Simplified Chinese Windows it becomes Microsoft YaHei UI), and `ui-sans-serif`, `ui-serif`, `ui-rounded`, `ui-monospace` are Safari only (web-features dataset).

## 2. Size, leading, measure

| Rule | Number | Source |
| --- | --- | --- |
| Measure | 45 to 75 characters, 66 ideal; 40 to 50 in multiple columns | practice: Bringhurst via webtypography.net/2.1.2 |
| Measure, upper limit | 80 characters (WCAG 1.4.8, AAA) | documented: w3.org/WAI/WCAG22/Understanding/visual-presentation.html |
| In CSS | `max-inline-size: 60ch` to `66ch`; ch or rem, never px | practice: every-layout.dev/rudiments/axioms/; web.dev/learn/design/typography |
| Body line height | 1.2 to 1.45 (Butterick); at least 1.5 in paragraphs for WCAG 1.4.8 (AAA) | practice: practicaltypography.com/line-spacing.html; documented: WCAG |
| Must survive user spacing | line height 1.5, paragraph spacing 2x, letter spacing 0.12em, word spacing 0.16em (WCAG 1.4.12, AA) | documented: w3.org/WAI/WCAG22/Understanding/text-spacing.html |
| Leading falls as size rises | Apple 17/22 body, 34/41 large title; Material 16/24 body, 57/64 display | documented |
| Paragraph spacing | 50 to 100% of body size, or a first-line indent, never both | practice: practicaltypography.com/space-between-paragraphs.html |
| Caps and small caps | track +0.05em to +0.12em | practice: practicaltypography.com/letterspacing.html |
| Display sizes | tighten slightly; the amount is specific to the typeface (Apple's SF numbers do not transfer) | documented, inference |

Practical defaults for running text on the web: 16 to 18px, line height 1.5 to
1.6, measure 60 to 70ch. For UI text: 13 to 15px with 1.35 to 1.5. Headings:
1.05 to 1.2. `tokens.py` computes line height and tracking per size from
design.json; `render_check.py` measures characters per line on the rendered
page.

## 3. Scale

- Shipping systems are hand-tuned, not pure ratios: Apple has 11 text styles from 11 to 34pt, Windows 12, 14, 18, 20, 28, 40, 68, and Google says of Material's 15 styles "Your product will likely not need all 15" (documented).
- Nielsen Norman Group: no more than three sizes for a clear hierarchy in a view (research: nngroup.com/articles/visual-hierarchy-ux-definition/).
- Working rule (inference): product UI needs 5 to 7 sizes between about 11 and 34px; a marketing page adds two or three display sizes, where a ratio (1.2 to 1.333) helps keep the jumps even.
- A modular scale is a tool, not a law: Tim Brown calls scales "tools, not dogma" (practice: alistapart.com/article/more-meaningful-typography/). Break it when the content needs a size between steps, then add that size to the scale.
- Hierarchy comes from size, weight, colour and position together. If two levels differ only by 1 or 2px, merge them or separate them properly.

Fluid type: `clamp(min, rem + vw, max)`, never `vw` alone. WCAG 1.4.4 needs
text to reach 200% on zoom; keep the maximum at most 2.5 times the minimum and
test at 500% zoom (practice: smashingmagazine.com/2023/11/addressing-accessibility-concerns-fluid-type/;
adrianroselli.com/2019/12/responsive-type-and-zoom.html). Use fluid sizes for
display text only; body text stays fixed.

## 4. Details that show a hand

- **Real punctuation**: curly quotes and apostrophes; en dash for ranges; no double hyphens (practice: practicaltypography.com/straight-and-curly-quotes.html). Straight marks only for feet, inches and code.
- **`text-wrap: balance`** on headings, captions and short blocks (widely available since 13 Nov 2026). It balances up to 6 lines in Chromium and 10 in Firefox and needs a max width. **`text-wrap: pretty`** on paragraphs avoids short last lines (Chromium and Safari; harmless elsewhere).
- **Figures**: `font-variant-numeric: tabular-nums` in tables, prices, timers and anything that updates; proportional in prose; `slashed-zero` for ids. Only works when the font has the feature: check.
- **Optical sizes**: prefer families with an `opsz` axis for text that appears both small and large; `font-optical-sizing: auto` is the default.
- **Hanging punctuation** is Safari only; CSS `widows` and `orphans` affect only page and column breaks. Do not rely on either.
- **Weights**: two or three (for example 400, 500 or 600, 700). Use weight to rank, not to decorate. Avoid faux bold and faux italic: load the real styles.
- **Alignment**: left-aligned, ragged right for anything over two lines. Centre only short, isolated lines. Never justify on the web without hyphenation.
- **Case**: sentence case for headings and buttons unless the brand says otherwise. All caps only for short labels, tracked.
- **Numbers and units** in the subject's own conventions (currency position, date order, thin space before units where the locale uses it).

## 5. Loading

- WOFF2 only. Preload the one or two files used above the fold.
- `font-display: swap` for brand faces, `optional` when performance matters more than the face (documented: web.dev/articles/font-best-practices).
- Prevent layout shift with a metric-matched fallback: `size-adjust` (widely available since 18 Mar 2026) plus `ascent-override`, `descent-override`, `line-gap-override` (not in Safari). Tools such as Fontaine, Capsize and next/font compute them (documented: developer.chrome.com/blog/font-fallbacks).
- Always declare a real fallback stack of the same class (serif for serif).
- `render_check.py` reports any declared face that did not load. A silent fallback to the system face is the most common way a design loses its identity between mockup and production.
