# Marketing sites and landing pages

Where the generated look is most obvious, because the template is strongest
here. Research checked 22 November 2026.

## 1. What the page is for

One page, one job, one next action. Before layout, write: who arrives, from
where, knowing what; what they must understand; what they should do next. A
visitor decides fast: people often leave within 10 to 20 seconds unless the
page states its value (research: nngroup.com/articles/how-long-do-users-stay-on-web-pages/),
and most viewing time is spent above the fold (57%, and 74% in the first two
screenfuls: nngroup.com/articles/scrolling-and-attention/).

## 2. The first screen

It must answer "what is this and is it for me" without scrolling, and it
should open with the most characteristic thing in the subject's world.

Ways to open that are not the stock hero:

- **The product, working**: a real editor window with real text, a live terminal panel, an interactive demo, the store's best photograph.
- **A plain claim, set large and off-centre**, in the brand's voice, with the action beside it.
- **A real example of the result**: the report, the booked calendar, the finished page.
- **The object**: for physical products, the thing itself, shot straight on.

Avoid: the centred stack (pill, headline, one line, two buttons); a hero that
fills the whole viewport and hides what comes next; abstract gradients, blobs
and dotted grids that could sit behind any product; a floating, tilted
screenshot with a glow; auto-playing background video without a still
fallback.

Size the hero to its content. The top of the next section should be visible
on a laptop screen.

## 3. Sections

Order them by the buyer's questions (`copy.md`, section 3), not by the
template. Each section needs something true and specific to say; delete those
that do not.

| Template section | Do this instead |
| --- | --- |
| Logo strip, "Trusted by" | Only real customers with permission; better: one named customer with what they did. Otherwise nothing |
| Three feature cards with icons | Show the features in use: annotated screens, a short list with real detail, a comparison table, one worked example. Unequal things get unequal space |
| "How it works" in 3 numbered steps | Only if it really is a sequence; show the actual steps with actual screens |
| Testimonials carousel | Two or three real quotes with name, role and company, static. Carousels hide content: auto-forwarding ones made a user miss the largest offer on a page (research: nngroup.com/articles/auto-forwarding/) |
| Stats row | Real numbers with a source and a date, or none |
| Pricing: three tiers, middle one ringed | The plans the business has; say who each fits. Price is the most wanted information on B2B sites (research: nngroup.com/articles/show-price/) |
| FAQ accordion | Answer the real objections in the page; keep an FAQ for the long tail |
| Final call-to-action band | Repeat the one action, with what happens next |

## 4. Layout and type

- A layout concept from the subject (`layout.md`): a printed brochure, a spec sheet, a catalogue, a desktop, a poster.
- Asymmetry: hang text from a left edge; pair a wide column with a narrow one; let one element break the grid on purpose.
- Display type is the personality: one distinctive decision (a condensed wordmark edge to edge, a huge quiet serif, a single weight throughout), not an effect (no gradient text, no accent-coloured word, no italic serif word in a sans headline).
- Body copy at 16 to 18px, 60 to 70 characters wide, left-aligned.
- Navigation: visible links on desktop. Hidden navigation is used less and found later (research, n=179: nngroup.com/articles/hamburger-menus/).

## 5. Imagery

- Real product screens, at a size where they can be read, cropped to the part that matters. Not a full dashboard shrunk to a thumbnail.
- Real photography of the real people, place or object: the owner's first, then a free library (Pexels, Unsplash, open museum collections), searched with the world study's words and credited in DESIGN.md (`imagery.md`). Stock photos of "diverse team at laptop" read as filler; so do generated images of the same.
- Never draw the subject by hand in SVG or CSS as a stand-in for a photograph (an SVG loaf, a cartoon plant): it reads as low quality (`slop_check.py` tell `image-drawn-art`). Illustration only with a point of view and an illustrator; draw only diagrams, charts, icons and the product's interface.
- No photograph found and none supplied: an honest placeholder labelled with what goes there and its aspect ratio, said in the hand-off.
- Every image has width and height (or `aspect-ratio`) and an `alt` that says what it shows.

## 6. Interaction

- Visible hover, focus and pressed states on every link and button (`states-motion.md`).
- Scroll motion is welcome on a landing page when it tells the subject's story: one scene scrubbed by scroll, quieter entrances below the fold, a hero whose picture settles on load. It must cost nothing: first screen complete at the first paint, everything visible without scripts or with reduced motion, compositor-only, CSS scroll timelines before any library (`scroll-motion.md`; check with `render_check.py --motion`).
- Forms: one column, labels above fields, no placeholder as label (research: nngroup.com/articles/web-form-design/; single-column forms were completed 15.4s faster in a CXL study, n=702).
- Cookie banners: accept, reject and manage offered equally, as a small overlay; no trick toggles (research: nngroup.com/articles/cookie-permissions/). Hiding "reject" is a dark pattern and unlawful in the EU.

## 7. Technical floor

- Text in HTML, one `h1`, headings in order, a real `<title>` and description.
- Responsive from 360px; no sideways scroll; targets 44px on phones.
- Fonts loaded with a metric-matched fallback; images sized and lazy below the fold.
- Works without JavaScript for reading; honours reduced motion and both colour schemes (or one, by decision).
- The `seo` skill covers search; do not add markup "for SEO" here.

## 8. Checklist

- A stranger can say what it is and what to do after two seconds on the first screen.
- The first screen shows something only this product has.
- Every section answers a buyer's question with something true.
- No stock hero, no template order, no invented proof (`slop_check.py`).
- Rendered and critiqued at 390 and 1440 (`render_check.py`, `critique.md`).
