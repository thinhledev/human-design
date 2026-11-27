# Looking at it: the critique

A design is not finished until someone has looked at the rendered result and
changed it. One pass is not enough; the first render is a draft. This is the
step generated design skips, and the main reason it looks unconsidered.

## 1. The loop

1. **Render**: `python3 scripts/render_check.py <file or URL> --out shots --widths 390,1440 --squint --surface <surface>` (add `--schemes light,dark` when the identity has two modes). Tall pages are saved as several screenshots; open every one.
2. **Fix the measured problems first** (errors, then warnings): fonts that did not load, contrast, sideways scroll, squeezed columns, small targets, clipped text.
3. **Open every screenshot and look.** Go through the questions below and write down what is wrong in plain words ("the price is the same weight as the plan name", "the left edge wobbles between sections").
4. **Change the design**, not the notes. Fix the three worst things.
5. **Render again and compare.** Repeat until a pass finds nothing worth fixing: usually two or three rounds. Stop when changes stop improving it.
6. **Run the other checks**: `slop_check.py` on the source, `fingerprint.py` (and `--against` when other projects are saved).

Without a browser: ask the user for screenshots at phone and desktop width, or
review the code against the same questions and say plainly that nobody has
looked at the result.

When working with a user, show the screenshots, say what you changed between
rounds and why, and ask what feels wrong to them. Record their corrections in
DESIGN.md under Taste.

## 2. Questions, in order

**First glance (two seconds, from the squint image)**

- What is this, and what is the one thing to do? Can you tell without reading?
- What is first, second, third? Is that the right order?
- Does anything shout that should not? Is anything important quiet?

**Identity**

- Could this be any product in the category with the logo swapped? What on screen belongs only to this subject?
- Is the signature visible, and is everything around it quiet?
- Does it follow DESIGN.md: faces, ground, accent rules, layout concept, refusals?
- Place it beside the owner's other projects: would a stranger think the same person made both on the same day?
- Is it merely correct? Plain, square and grey-green is a house style too. Is there one moment of warmth or wit from the subject's world (a crossed-out Sunday in a diary, a price written as a ledger entry) that someone would mention to a colleague?
- Would anyone screenshot it?

**Type**

- Did the chosen faces load? (measured)
- Is running text 45 to 75 characters wide with enough leading?
- How many sizes and weights are on screen? Can two be merged?
- Do headings break well (no single-word last lines, no awkward hyphenation)?
- Do numbers align in columns?

**Space and alignment**

- Count the vertical edges. Can any be merged?
- Are groups made by space? Is any box doing nothing?
- Is spacing uneven where it should be (more above headings than below, more between sections than within)?
- Is anything centred that should hang from an edge?
- Any near-misses: things almost aligned, almost the same size, almost the same colour? Make them the same or clearly different.

**Colour**

- Does the accent appear only where the identity allows?
- Are there greys or hues that are not in the tokens?
- Is text on images or tints readable? (look; it cannot be measured)
- Does dark mode look designed, or inverted?

**Content**

- Is every sentence real, specific and true? Any placeholder, invented number or stock phrase?
- Is every image the real thing or an honest, labelled placeholder?
- Does each section earn its place? What happens if it is deleted?

**Behaviour**

- Does every control have pressed, focus, busy and disabled states? Is there a state sheet?
- Are loading, empty and error designed for every data view?
- Is the first screen complete at the first paint, and is everything in view visible once scrolling stops? On a landing page, does the scroll motion tell the subject's story, or is it the same fade on every block? Open the `--motion` scroll frames.
- Are the pictures real photographs of the subject, or drawn stand-ins?
- Tab through it: is focus visible and in reading order?

**Phone**

- Is it reordered for the small screen, or squeezed?
- Are targets at least 44px, with the primary action in reach?
- Does anything overflow or clip?

**Subtraction (last)**

- Remove one element at a time (a label, an icon, a rule, a card, a section). If nothing is lost, leave it out.
- Then check the opposite: is anything missing that the user needs to decide or act?

## 3. Reporting

After the last round, tell the user in a few lines: what was checked (which
widths and modes, which scripts), what was fixed between rounds, what is still
imperfect or not checked (for example "not tested in Safari", "photography is
placeholder"), and where the screenshots are. Do not claim it "looks great";
say what you verified.
