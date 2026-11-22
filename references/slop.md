# What makes design read as generated

`python3 scripts/slop_check.py --list` prints the current catalogue with a fix
for each tell. This file explains why the tells exist, which matter, and how
not to trade one cliché for another. Sources checked 22 November 2026.

## 1. The cause

Models produce the most likely interface: the centre of everything they have
seen (Anthropic calls it distributional convergence; vendor:
claude.com/blog/improving-frontend-design-through-skills). Three forces shape
that centre:

- **Training defaults**: tutorial and template code. The indigo button is traced to Tailwind UI's demos, reinforced by generated pages being scraped back (secondary: prg.sh, 26 Oct 2025).
- **Framework defaults**: an untouched component kit (its radius, neutral scale and icon set), the starter font.
- **The safe average**: when nothing is decided, everything gets a container, a centre alignment and the same value.

A tell is therefore evidence of a missing decision. The cure is a decision
(`identity.md`), not a prohibition.

## 2. Three generations

**First: the defaults.** One default sans for everything; indigo or violet
accents and gradients; gradient headline text; a centred hero with a pill, a
headline, a line and two buttons; three equal icon-topped cards; icons in
tinted rounded squares; one large radius and one soft shadow on every box;
emoji as icons; glass panels and glow orbs; the stock section order (hero,
logos, features, how it works, testimonials, pricing, FAQ, call to action);
invented proof.

**Second: the reactions.** Told not to do the above, models converge on the
next most likely answers: a cream ground with a serif display face and a
terracotta accent; near-black with one acid-green or vermilion accent;
"editorial" broadsheet hairlines on everything; one italic serif word inside a
sans headline; monospace uppercase labels; 01 / 02 / 03 markers; the same
"tasteful" free fonts. Anthropic's own design skill was rewritten in 2026 to
name these (primary: github.com/anthropics/skills, frontend-design, commits of
9 Jun and 3 Sep 2026). Each ban list so far has bred the next default.

**Third: the lifeless.** Zero tells and still nothing there: correct,
tasteful, interchangeable. No signature, no point of view, a mockup with one
state per component, motion as decoration. No checker finds this; the
critique does (`critique.md`).

## 3. How common, and what people notice

- In a count of 16 signs on 120 AI-built pages, 57 pages showed six or more; the commonest were the untouched kit (61%), a single default sans (60%), three or four identical cards (63%) and the centred hero with a pill (51%) (primary, single author: buildtolaunch.substack.com, 28 Oct 2026).
- A scan of Show HN pages with deterministic checks reported about 5 to 10% false positives overall by the author's own review (primary, single author: adriankrebs.ch/blog/design-slop/, 20 Apr 2026).
- A ranking mined from Reddit discussion puts the untouched kit and "AI purple" at the top; bento grids, glass and aurora backgrounds near the bottom (primary, measured opinion: github.com/JCarterJohnson/vibecoded-design-tells, Jun 2026).
- Evidence for mobile apps is thin; the native checks in `slop_check.py` are this skill's own extrapolation from the web tells and platform guidelines.

**Stacks, not single hits.** One weak tell means little: a real brand can be
violet, a real product can have three plans. A page reads as generated when
several tells stack. `slop_check.py` therefore fails (exit status 2) only on
strong tells and on a whole-look match.

## 4. Using the checker well

- Run it on source: `python3 scripts/slop_check.py <paths> --surface app|marketing|mobile|desktop|store`.
- A tell that is a real decision goes in design.json: `"deliberate": {"colour-purple": "brand colour since 2019"}`, then `--identity design.json`. It is listed as declared. Do not declare things to silence the checker; a reason must name the subject.
- Static checks cannot see rendered results. `render_check.py` measures the page (centred share, one radius everywhere, gradients, contrast, fonts that did not load). `fingerprint.py` compares the whole look with the catalogued defaults and with the owner's other projects.
- Known false positives: violet brands, documentation and developer tools that rightly use monospace labels, a real three-plan price list, numbered steps that are a real sequence, glass on Apple platforms where it is the system material.
- The checker is a floor. Passing it means "no obvious defaults", never "good".

## 5. Not becoming the fourth generation

A skill that hands out the same "distinctive" answers creates its own
signature. This one avoids it by construction:

- It contains no palette, font pairing, layout or component kit to reuse. Every value comes from the project's brief and world study.
- The typefaces it mentions are examples to evaluate, with a list of the ones already turning into defaults (`typography.md`).
- `fingerprint.py --against` compares each new design with the owner's previous ones. Two unrelated projects above 75% similarity is a failure of method, whatever the tells say.
- The identity records refusals and rejected directions, so the same idea is not proposed twice.

If you notice yourself reaching for the same face, ground or layout concept as
in the last project, stop and return to the world study.

## 6. The opposite failure

Do not strip a design to nothing out of fear of tells, and do not add
strangeness for its own sake. Conventions users rely on (where navigation is,
how a form behaves, what a cart looks like) are not slop. The aim is a design
in which every visible choice has a reason from the subject, including the
choice to be conventional.
