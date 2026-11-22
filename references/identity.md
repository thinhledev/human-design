# The project's design identity

Generated design looks the same everywhere because nothing in it was decided
for the project: every value is the most likely one. The fix is not a list of
banned looks (each ban has bred the next default) but a record of decisions
that come from this subject, kept in the repository and obeyed by every later
screen.

Two files hold it:

- `DESIGN.md`: the reasoning, for people and agents (template: `assets/DESIGN.template.md`).
- `design.json`: the same decisions as numbers; `scripts/tokens.py` turns it into tokens.

Precedence, always: the user's own words, then the project's existing system
(brand guide, tokens, component library), then this method. When a system
exists, write it down in DESIGN.md and extend it; do not replace it.

## 1. Brief (ask once, at most eight questions)

1. What is it, in one sentence, and who uses it?
2. What is the one job of this screen or site? What should a visitor do next?
3. Where will people use it (phone on the move, a desk all day, a shop floor, a studio at night)?
4. What exists already: logo, colours, fonts, a product people know, photographs?
5. Three words for how it should feel, and one it must never feel like.
6. Two or three things you admire (any medium) and why. One you dislike.
7. Constraints: platform, framework, accessibility level, languages, performance, budget for fonts or images.
8. What real content exists now (copy, product data, screenshots, numbers)?

No answer is also an answer: record "not decided" and choose in step 4 with a stated reason.
If a personal taste file exists at `~/.human-design/taste.md`, read it first.

Before choosing anything, run `python3 scripts/fingerprint.py --taken`. It
lists the typefaces, grounds and accents the owner's other projects already
use. A new, unrelated product may not reuse a typeface from that list, nor a
ground and accent pair.

## 2. Study the subject's world (15 minutes, written down)

List concrete things, not adjectives. Each line can become a decision.

- **Materials and objects**: what the people in this world touch (clay, receipts, cables, seed packets, boarding passes).
- **Its documents and screens**: timetables, invoices, score sheets, lab notebooks, shipping labels, terminal output. Their typography is a vernacular you can borrow from.
- **Its colours, with a source for each**: "kiln brick, slip grey, celadon glaze", not "warm neutrals".
- **Its units, terms and conventions**: cone numbers, SKUs, bar numbers, tail numbers. At least one must appear in the design as content.
- **Its pace and stakes**: calm or urgent, playful or exact, private or public.

Then look at up to three products in the category and write (open them when
you can; when their screens are not public, use what the owner says about them
and mark it inference; do not spend long hunting for vendor pages):

- **Conventions users rely on** (keep): where the cart is, how a calendar reads, what a "run" button looks like.
- **What everyone does out of habit** (question): the stock hero, the same illustration style, the same blue.
- **One thing nobody does** that the subject would justify.

Describe what you see in your own words. Never copy a competitor's layout,
assets, illustration or text.

## 3. Voice

Three words from the brief, each with what it means on screen:

| Word | Means | Does not mean |
| --- | --- | --- |
| exact | tabular figures, aligned edges, real units | cold, grey, tiny |
| warm | tinted neutrals, a text face with some stroke contrast, first-person copy | beige, rounded, cute |

## 4. Decide (each with a reason that names the subject)

| Decision | Options to weigh | Reference |
| --- | --- | --- |
| Text face, display face, mono | from the world study; one family may be enough | `typography.md` |
| Type scale | 5 to 7 sizes for product UI; add display sizes for marketing | `typography.md` |
| Ground | white, tinted, cream, grey, dark; why this one for where it is used | `color.md` |
| Neutrals | tinted toward which hue, how strongly | `color.md` |
| Accent | one hue with its source in the subject; where it may appear | `color.md` |
| Density | compact (tools used all day), regular, airy (reading, selling) | `layout.md` |
| Grid and layout concept | one sentence: "a ledger: hairline rows, numbers right-aligned" | `layout.md` |
| Shape | radius by role (controls, containers, media), or none | `layout.md` |
| Depth | none, hairline, soft, hard; how many levels | `layout.md` |
| Imagery | the product itself, photography (whose), illustration (what style, by whom), none | surface references |
| Motion | character in one line: "quick and flat", "weighted", "none beyond state changes" | `states-motion.md` |
| Copy voice | person, tense, case, how numbers are written | `copy.md` |
| Signature | the one thing a visitor would describe to someone else | below |
| Refusals | three things this design will not use, and why | below |

**The signature.** Every reference a person remembers has one deliberate
choice that breaks a convention for a reason: a site built as a desktop, a
background that shows the server's battery, hand-scrawled lettering over a
photo, a wordmark that runs edge to edge. Choose one, from the subject, and
keep everything around it quiet. One is enough; three is noise.

**Refusals** keep later screens honest: "no icons in feature lists (the
product is text)", "no cards (it is one ledger)", "no accent on anything that
is not an action".

**Reasons must name the subject.** "Clean and modern", "professional",
"friendly", "legible" fit every product and therefore decide nothing. "Tabular
grotesque because the whole product is a timetable" is a reason.

**Know your own habits.** A careful model has defaults too. Observed in this
skill's own benchmark (22 November 2026), across unrelated products:

- a pale grey-green ground with dark green ink and an indigo or blue accent;
- Atkinson Hyperlegible Next, Instrument Sans or Schibsted Grotesk, with a mono for labels;
- square corners, hairlines, no shadows, no images: plain and correct.

Each can be right for a subject (ledger paper really is pale green), and each
was chosen for subjects where it was merely safe. If your decisions land on
this list, check that the reason is in the subject and not in you, and prefer
a different answer when the subject allows one. Plainness is also a default
when nothing in the brief asks for it: restraint needs a signature and some
warmth or wit from the subject's world, or it reads as a government form.

## 5. Three directions before one (new identities only)

Skip this when the project already has an identity.

1. Write three directions that answer the brief differently: a different lead decision in each (type-led, colour-led, layout-led, or image-led), not three colourways of one layout. At least one should be warmer or bolder than you would choose by habit.
2. Build each as one cheap thumbnail of the same real screen: the first screen, real copy, no polish. One file per direction, from `assets/direction.template.html` (`directions/a.html`, `b.html`, `c.html`), shown together with `assets/directions.template.html`.
3. Run `fingerprint.py directions/a.html` on each, and `fingerprint.py --compare directions/a.html directions/b.html directions/c.html`. Drop any that lands on a catalogued default look or clashes with a saved project; make any two that are more than 55% alike differ in type or ground.
4. Show the three with one line each on what it bets on and what it gives up. The owner picks, or mixes.
5. Record the choice and the two rejected directions in DESIGN.md, so they are not proposed again.

## 6. Check for sameness

- `python3 scripts/fingerprint.py <src>`: distance from the default looks AI tools converge on.
- `python3 scripts/fingerprint.py <src> --against`: similarity to the owner's other projects (reads the registry only).
- `python3 scripts/fingerprint.py <src> --save NAME`: add this project once its design is accepted (the registry is `~/.human-design/fingerprints`; only fingerprints are stored). Ask the owner before the first save.
- Two hard rules between unrelated products, whatever the score: no shared text or display typeface, and no shared ground with the same accent hue. Sister products of one brand should share them: pass `--same-brand`.
- Above 75% similarity between unrelated products, go back to step 2: the newer one borrowed the older one's answers.
- This skill must not become a signature either. If two projects made with it share type, ground and layout concept, the method was skipped.

## 7. Write it down and keep it current

- Fill `DESIGN.md` and `design.json`; generate tokens: `python3 scripts/tokens.py design.json --css tokens.css`. The starter from `tokens.py --init` lists the optional keys under `_options` (ground lightness, a separate ink, a second accent, one or two colour modes) and has places for the signature, refusals and deliberate choices.
- Every later screen starts by reading DESIGN.md. New decisions are appended to its log with a date and a reason; nothing is decided twice.
- A choice that looks like a known default but was made on purpose goes under `"deliberate"` in design.json with its reason: `{"deliberate": {"colour-purple": "the brand has been violet since 2019"}}`. `slop_check.py --identity design.json` then lists it as declared.
- When the owner corrects a design ("too playful", "tighter", "I never want pills"), record the correction in DESIGN.md under Taste, and offer to add lasting preferences to `~/.human-design/taste.md` so other projects inherit the taste, not the look.

## 8. Taste calibration (optional, ten minutes)

When the owner cannot yet say what they want, show instead of asking:

1. Pick six to eight references from different traditions (`sources.md` lists a studied set with what makes each one work).
2. Ask which feel right and which feel wrong, and one reason each.
3. Extract the common factors in their answers (density, type contrast, colour temperature, how much decoration, how loud the signature) and write them under Taste. Preferences are about qualities, never "make it look like that site".
