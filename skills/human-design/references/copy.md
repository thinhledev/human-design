# Words in the interface

Copy is design material. Generated layouts are often built around placeholder
sentences, which is why they fit any product. Write the words first; the
layout follows from what there is to say.

## 1. Rules

- **Say the concrete thing.** What it does, for whom, with what result: "Booking for pottery studios: classes, kiln slots and memberships in one calendar." If a competitor could use the sentence unchanged, rewrite it.
- **From the user's side of the screen.** Name things as people know them ("notifications"), not as the system is built ("webhook config").
- **One claim per sentence.** Short, plain, in the order a person would say it to one other person.
- **A speaker.** The references people remember have a voice: first person, a flat claim, sometimes a joke. Decide person, tense and formality in DESIGN.md and keep them.
- **Sentence case** for headings, buttons and labels, unless the brand guide says otherwise. Windows asks for it explicitly; Apple and Google use it throughout.
- **Controls say what happens**: "Publish", then "Published". "Start a 14-day trial", "See a sample report", not "Get started" and "Learn more".
- **Busy and done**: the verb in -ing with an ellipsis ("Saving…"), then the past tense ("Saved").
- **Errors**: what went wrong, what state things are in now, what to do. "Could not delete the video. It is back in your library." No apology, no code without a sentence.
- **Empty states**: what will be here, why it is empty, the one action that fills it.
- **Numbers and proof are real or absent.** No invented user counts, star ratings, uptime figures, logos, testimonials or people. An honest gap is better. Fake reviews and fake social proof are illegal in the US (FTC rule 16 CFR 465, effective 21 Oct 2024) and the EU (UCPD Annex I, points 23b and 23c).
- **Use the subject's own terms and units** as content: cone 6, SKU, bar 32, gate B14. One real detail does more than a paragraph of adjectives.
- **Real punctuation**: curly quotes and apostrophes, en dashes for ranges (`typography.md`).

## 2. Shapes to avoid

`slop_check.py` flags the first four.

- **Stock vocabulary**: elevate, seamless, supercharge, unlock, unleash, effortless, streamline, empower, leverage, cutting-edge, next-generation, all-in-one, blazing fast, reimagine, transform your, the future of, world-class, robust, intuitive, AI-powered.
- **Mannered sentences**: em-dash asides; "not just X, but Y"; "It's not X. It's Y."; "The result?" and other self-answered questions; three one-word sentences ("Fast. Simple. Secure."); adjective triads.
- **Template chrome**: middot-separated fragments ("Design · Build · Ship"), arrows glued to every button, capitalised kickers with a dash.
- **Title Case On Every Heading**, and headlines that end in a full stop for effect on every section.
- **Headline, then the same idea three more times** in the subhead, the first paragraph and the button.
- **Section labels that describe the page instead of the product**: "Features", "Why choose us", "How it works", "Testimonials". Use a heading that makes a claim, or none.
- **Hedging and filler**: "simply", "just", "easily", "in today's fast-paced world".

## 3. A marketing page, in order of what the buyer asks

1. What is this, and is it for me? (headline and one line; a visitor should know within seconds: nngroup.com/articles/homepage-design-principles/)
2. Show me. (the product working: a real screen, an example, a result)
3. Why believe you? (specifics, real names with permission, numbers with a source)
4. What does it cost? (price is the information B2B buyers want most; show it or a sample: nngroup.com/articles/show-price/)
5. What happens when I click? (the action, named)
6. What if it does not fit? (limits, refund, how to leave)

Cut any section with nothing true to put in it. A page of four honest sections
beats eight template ones.

## 4. Product UI

- Labels are nouns; buttons are verbs; the same thing has the same name everywhere.
- Confirm destructive actions by naming the object and the consequence: "Delete 3 invoices? This cannot be undone."
- Prefer the specific to the polite: "2 fields need fixing" over "Oops! Something went wrong".
- Dates, times, currency and units in the user's locale; relative times ("3 min ago") with the exact time on hover or tap.
- Do not explain the interface in the interface. If a control needs a paragraph, redesign it.

## 5. Checklist

- The headline could not be used by a competitor unchanged.
- No number, name, logo or quote without a source.
- Buttons name what happens; errors say what state things are in.
- One voice, one case, one name per thing.
- No stock vocabulary, template chrome or placeholder text (`slop_check.py`).
