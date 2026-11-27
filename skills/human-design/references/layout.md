# Layout, space and hierarchy

Checked 22 November 2026. Grades: documented, practice, research, vendor, inference.

## 1. Start from content and a concept

- **Real content first.** Layout is a response to what there is to show: how long the names are, how many columns the data has, whether there are photographs. Placeholder text produces placeholder layout.
- **One layout concept, said in a sentence**, from the subject: "a ledger", "a workbench with a parts tray", "a contact sheet", "a departures board", "a printed season brochure". It decides the grid, the rules and the density, and it is what keeps screens consistent.
- **Decide the hierarchy before the boxes.** For each screen: what is first, second, third? If everything is second, nothing has been decided.

## 2. Hierarchy

- Tools: size, weight, colour or contrast, position, space around. Use two at a time, not all five.
- Limits that keep hierarchy readable (research: nngroup.com/articles/visual-hierarchy-ux-definition/ and principles-visual-design/): about three type sizes in a view, at most two large elements, contrast of value more than hue.
- **Squint test**: blur the screen and check what still stands out; it should be the first and second things. `render_check.py --squint` saves the blurred image.
- Position carries rank: top-left reads first in left-to-right scripts. Research found 57% of viewing time above the fold and 74% in the first two screenfuls (research: nngroup.com/articles/scrolling-and-attention/).
- Unformatted walls of text get an F-shaped scan; front-load headings and first words (research: nngroup.com/articles/f-shaped-pattern-reading-web-content/).
- Anything that looks like an advert is skipped (research: nngroup.com/articles/banner-blindness-old-and-new-findings/), so do not style important content as a promo box.

## 3. Space

- **Proximity is grouping.** Things that belong together sit closer than things that do not; a label is nearer its field than the field above. Space can outweigh colour and shape (research: nngroup.com/articles/gestalt-proximity/). Recheck groups at each breakpoint.
- **Space before lines, lines before boxes.** Separate with space first; add a hairline when space is not enough; draw a box only around a real object.
- **A scale, not a ruler.** Steps on a 4px base (4, 8, 12, 16, 24, 32, 48, 64, 96) cover most needs (practice: spec.fm/specifics/8-pt-grid; vendor: carbondesignsystem.com/elements/spacing/overview/). Dense tools need the 4px steps; 8px alone is too coarse (vendor: webflow.com/blog/why-were-using-a-4-point-grid-in-webflow). `render_check.py` reports the share of off-scale values.
- **Uneven on purpose.** Equal padding everywhere is a generator's habit. More space above a heading than below it; more between sections than within; outer margins larger than inner gaps.
- **Optical corrections** beat arithmetic: a play triangle centred by its box looks off-centre; text in a button needs a touch more space below caps-height than above. Nudge by eye.
- **Vertical rhythm**: strict baseline grids are fragile on the web because CSS splits leading above and below each line (practice: webtypography.net/2.2.1). Keep line heights and spacing as multiples of one unit instead; `lh` and `rlh` units are widely available.

## 4. Grids

- **Column grid** for pages: 4 columns on phones, 8 on tablets, 12 or 16 on desktop, with consistent gutters. Carbon uses 4, 8 and 16 columns with 32px gutters (vendor: carbondesignsystem.com/elements/2x-grid/overview/).
- **Modular thinking** (Müller-Brockmann, 1981, as usually summarised): the page divides into fields; images occupy 1, 2, 3 or 4 fields; fewer different sizes read calmer.
- **Asymmetry reads as intent.** A wide column and a narrow one (8 and 4, or 7 and 5), text hung on a left edge with one tall image right, a headline off-centre: the references people remember rarely centre a stack. Centre only short, isolated things.
- **Align to few edges.** Count the vertical edges on a screen; fewer, stronger edges look designed. Subgrid (widely available since Mar 2026) lets nested content share the parent's tracks.
- **Unequal things get unequal space.** Three features are almost never equally important; a 3-up of equal cards hides that. Try one large and two small, a list, a table, or one worked example.

## 5. Density

Density is a decision from the brief, not a style.

| Density | For | Typical values |
| --- | --- | --- |
| Compact | tools used all day, tables, IDE-like apps | 12 to 13px text, rows 24 to 32px, 4 to 8px gaps |
| Regular | most product UI | 14 to 15px text, rows 36 to 44px, 8 to 16px gaps |
| Airy | reading, selling, onboarding | 16 to 18px text, generous section space |

- Carbon's table rows are 24, 32, 40, 48 and 64px, the last for two-line rows (vendor: carbondesignsystem.com/components/data-table/style/).
- Targets stay reachable at any density: 24 by 24 CSS px minimum (WCAG 2.5.8, AA), 44 by 44 for touch (Apple) and 48dp (Android).
- Expert users prefer more on screen with clear structure over less with scrolling; give tools a density setting when the audience is mixed.

## 6. Shape and depth

- **Radius by role**: controls, containers and media can differ. One large radius on everything is the most recognisable generated look after the gradient. Choose a small set (for example 2, 6 and full for pills) and say what each is for. Nested radii: inner = outer minus the gap.
- **Depth**: pick a model and keep to two or three levels: none (flat, lines only), hairline (1px borders), soft (subtle shadows for things that float: menus, dialogs), or hard (offset solid shadows as a graphic device). Shadows are for objects that sit above the page, not for every section.
- **Cards**: a card says "this is one separate object you can act on". Do not wrap sections, text blocks or whole pages in cards, and never nest cards in cards.
- **Borders**: one hairline colour for separation, a stronger one (3:1) for control boundaries.

## 7. Responsive

- **Content-driven breakpoints**: add a breakpoint where the content breaks, not at device names. Intrinsic layouts mix fixed, fluid and content-sized tracks and need few media queries (practice: Jen Simmons, 2018; every-layout.dev).
- **Container queries** (widely available since Aug 2025) make components respond to their own width, which is what a card in a sidebar needs.
- **Window size classes** for apps: compact under 600, medium 600 to 839, expanded 840 to 1199, large 1200 to 1599, extra-large above (documented: developer.android.com, use-window-size-classes).
- **Phone is not desktop squeezed**: reorder by importance, collapse columns, keep line length, enlarge targets. `render_check.py` reports sideways scroll, squeezed columns and small targets at each width.
- **Never** let the page scroll sideways; give wide tables and code their own scroll container.

## 8. Checklist

- The layout concept is one sentence and visible on screen.
- First, second and third are obvious in the squint image.
- Groups are made by space; boxes only around real objects; no nested cards.
- Few vertical edges; something is deliberately off-centre.
- Spacing values come from the scale; radius and depth follow their roles.
- Density matches the brief; targets still meet their minimums.
- Works at 390 and 1440 wide with no sideways scroll (`render_check.py`).
