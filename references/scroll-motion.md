# Scroll motion on marketing pages

Checked 27 November 2026. Grades: documented, practice, research, vendor, inference.

A landing page may move as the visitor scrolls: a product assembling, a
photograph opening up, a sticky scene that plays across its height, a ground
that changes colour between chapters. Done well it is the part people
remember. Done carelessly it is the generated fade-up on every block, it
delays the largest paint, and it hides words from crawlers. This reference is
how to get the first without the rest.

For product UI (apps, dashboards, settings) none of this applies: motion there
explains state changes only (`states-motion.md` section 4).

## 1. Five guarantees, checked by `render_check.py --motion`

1. **Every word and image is in the HTML.** Motion moves content; it never creates, loads or swaps it. A crawler that does not run scripts, or does not scroll, reads the whole page (documented: Google's lazy-loading guidance says content must not depend on scrolling or clicking, developers.google.com/search/docs/crawling-indexing/javascript/lazy-loading). Split headings keep the full sentence readable as one string (see section 4).
2. **The first screen is complete at the first paint.** Nothing in the first viewport starts at `opacity: 0`, and the hero's heading and image are never behind an animation or a script. Chromium skips elements at opacity 0 when choosing the LCP element (documented: web.dev/articles/lcp), so a fading hero delays LCP until the fade, which has been measured at several seconds (vendor: debugbear.com/blog/opacity-animation-poor-lcp; shopify.dev, "Don't hide the LCP image behind animations"). On load, animate decorative layers (a veil, a gradient, an image's scale from 1.04 to 1), or move text that is already visible.
3. **Visible without the enhancement.** A hidden start state exists only inside `@media (prefers-reduced-motion: no-preference)` and `@supports (animation-timeline: view())`, or in a keyframe's `from`. With scripts off, with reduced motion, in print, in a browser without scroll timelines, and in a tall viewport that never scrolls, everything is visible. Content fully in view is visible once scrolling stops.
4. **Compositor only.** Animate `transform` and `opacity`; `clip-path` and `filter` sparingly and on small areas. Never width, height, top, left, margin or anything that moves layout (layout shift counts toward CLS, poor at 0.1: documented, web.dev/articles/cls). No scroll event handlers doing work on every frame.
5. **No script by default.** CSS scroll-driven animations (`animation-timeline: scroll()` and `view()`) run off the main thread and are Baseline newly available since October 2026: Chrome, Safari and Firefox 159 (documented: web.dev/blog/web-platform-10-2026). Browsers without them get the static page, which is complete. A library (GSAP with ScrollTrigger, Motion) only for a scene CSS cannot express, loaded with `defer` or `type="module"`, never in the critical path, and still obeying 1 to 4.

Native scrolling stays. Smooth-scroll libraries (Lenis, Locomotive, fullPage)
replace the platform's scrolling, cost script and can break keyboard paging,
find-in-page and anchor links; they are a deliberate choice of the owner's, not
a default (`slop_check.py` tell `motion-scroll-hijack`; record
`"smooth-scroll"` under `deliberate` when chosen).

## 2. What makes it feel designed rather than generated

- **Choreograph by role, not by element.** One scene per page carries the story (the `states-motion.md` rule of one orchestrated moment still holds). Around it, quieter entrances. The same fade-up on every block is the tell (`dead-fade-up-everything`).
- **The scene comes from the subject.** Observed on tasteskill.dev (27 November 2026): a warm gradient "sunrise" behind the hero on load, product cards that fan into place as the demo window scrolls in, a tall sticky scene whose live demo plays across its height, and a closing sunrise at the foot. Each motion shows what the product does. For a bakery, a rack of loaves that fills as you scroll; for a log tool, lines streaming past a cursor; for a language app, a phrase whose stressed syllables light up in order. Describe the idea in DESIGN.md under Motion before building.
- **Scrub what tells a story, trigger what only arrives.** A scene tied to scroll position (scrubbed) lets the visitor control it and is legible both ways. A simple entrance runs on entry only.
- **Use the identity's motion character** (`states-motion.md`): one easing, a few durations. For scrubbed effects use `linear` timing over a short `animation-range`; the scroll supplies the easing.
- **Small distances.** Entrances travel 16 to 40px and finish by about a third of the way into view. Parallax moves an image a few percent inside its frame, never the text.
- **Exits count too.** The hero can recede as it leaves (scale down slightly, dim), and a chapter can hand over its ground colour to the next. Fading out content that is leaving is fine; content in view at rest is never faded.

## 3. Recipes

All of these are progressive: without support or with reduced motion, the page is static and complete.

**Entrance below the fold** (never on the first screen):

```css
@keyframes arrive { from { opacity: 0; transform: translateY(28px); } }
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .arrive { animation: arrive linear both; animation-timeline: view(); animation-range: entry 0% cover 28%; }
  }
}
```

Only `from` is written: the end state is the element's own style, so nothing can stay hidden. Give siblings slightly different ranges (`cover 22%`, `cover 30%`) for a stagger without a script.

**A sticky scene scrubbed by scroll** (the page's one orchestrated moment):

```css
.scene { view-timeline: --scene block; }
.scene .stage { position: sticky; top: 0; }
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .scene { height: 260vh; }               /* the room to scroll through; static pages keep their natural height */
    .scene .stage { height: 100vh; overflow: clip; }
    .scene .piece { animation: assemble linear both; animation-timeline: --scene; animation-range: contain 0% contain 70%; }
  }
}
```

The keyframes end on the finished state, which is also what the static page
shows. Write the scene's text as normal HTML inside the stage.

**Parallax inside a frame** (images only, never text):

```css
.frame { overflow: clip; }
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .frame img { scale: 1.12; animation: drift linear both; animation-timeline: view(); }
  }
}
@keyframes drift { from { translate: 0 -5%; } to { translate: 0 5%; } }
```

**A photograph that opens up** (clip-path on one image):

```css
@keyframes open { from { clip-path: inset(18% 22% round 12px); } }
.reveal-photo { animation: open linear both; animation-timeline: view(); animation-range: entry 10% cover 45%; }
```

**Reading progress or a header that settles** use `animation-timeline: scroll(root)` on a `transform: scaleX()` bar or the header's own shadow.

**Hero on load:** animate a decorative layer, not the words.

```css
@media (prefers-reduced-motion: no-preference) {
  .hero-veil { animation: lift 900ms var(--ease-out) both; }   /* a layer over the photograph */
  .hero-photo { animation: settle 1200ms var(--ease-out) both; }
}
@keyframes lift { to { opacity: 0; } }
@keyframes settle { from { scale: 1.04; } }
```

**If a script is unavoidable** (a scene CSS cannot express): put the hidden
start state under a class the script adds (`html.motion .x { ... }`), add the
class from a tiny inline script, use IntersectionObserver or the library's
trigger with `once` for entrances, mark listeners `{ passive: true }`, load the
library with `defer`, and keep the no-script page complete.

## 4. Words that move

- Split a headline into words or lines, not letters, and keep the sentence intact for assistive technology and crawlers: the visible spans carry `aria-hidden="true"` and the element keeps the full text (`aria-label` on a heading is read by some screen readers but not all, so prefer a visually hidden copy of the full sentence).
- Never animate the hero heading's opacity from 0. Move it from visible, or leave it still and move the picture.
- No typewriter or count-up (`dead-toy-motion`).

## 5. Checking it

```bash
python3 scripts/render_check.py page.html --widths 1440 --motion --out shots
```

It measures LCP and its element (and fails a lazy-loaded LCP image), layout
shift and long tasks during load and a slow scroll, text in the first screen
invisible at load, content in view still invisible when scrolling stops,
anything hidden under reduced motion, with scripts off, or in a tall viewport,
text that exists only after JavaScript, smooth-scroll and render-blocking
motion libraries. It saves frames at four scroll positions: open them, because
the in-between states are the design. A local file gives a floor for the
timings; check a deployed page with PageSpeed Insights or the Chrome UX Report.

`slop_check.py` flags unguarded hidden start states (`motion-hidden-start`),
smooth-scroll libraries (`motion-scroll-hijack`), scroll handlers
(`motion-scroll-handler`) and the same reveal everywhere
(`dead-fade-up-everything`).

## 6. Checklist

- The scene is named in DESIGN.md under Motion with the subject it shows.
- First screen complete at the first paint; the LCP element never fades in, and the LCP image is eager with `fetchpriority="high"`.
- Every hidden start state is inside the reduced-motion and `@supports` guards (or the keyframe's `from`).
- Only transform, opacity and small clip-paths move; no layout shift.
- No script for motion, or a deferred one with a reason.
- `render_check.py --motion` passes; the scroll frames were opened and judged.
