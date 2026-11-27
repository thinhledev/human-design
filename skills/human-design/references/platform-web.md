# The web platform, November 2026

What CSS and HTML can do now, so designs use the platform instead of
libraries and hacks. Status comes from the web-features dataset behind the
Baseline badges on MDN and web.dev (version 3.47.0, snapshot with Chrome 158,
Firefox 160, Safari 27.2; github.com/web-platform-dx/web-features), checked 22
November 2026. "Newly" means in all three engines since that date; "widely"
means 30 months later. Re-check anything older than six months.

## Safe everywhere (widely available)

| Feature | Use it for | Since |
| --- | --- | --- |
| Container size queries | components that respond to their own width | Aug 2025 |
| `:has()` | parent and state selection without JavaScript | Jun 2026 |
| Subgrid | nested content aligned to the parent's tracks | Mar 2026 |
| `oklch()`, `oklab()`, `color-mix()` | perceptual palettes and mixing | Nov 2025 |
| `light-dark()`, `color-scheme` | per-mode colours inline | Nov 2026 |
| `text-wrap: balance` | even headings and captions | Nov 2026 |
| `linear()` easing | springs and custom curves | Jun 2026 |
| `lh` and `rlh` units | spacing in line heights | May 2026 |
| `size-adjust` in `@font-face` | fallback fonts that do not shift layout | Mar 2026 |
| `prefers-reduced-motion`, `prefers-contrast` | honouring user settings (mandatory) | 2022, 2024 |

## Newly available: use with a sensible fallback

| Feature | Use it for | Since | Fallback |
| --- | --- | --- | --- |
| View Transitions, same document | animating between states of one page | Oct 2025 | instant change |
| `@starting-style`, `transition-behavior: allow-discrete` | entry and exit transitions from `display: none` | Aug 2024 | appears without transition |
| Relative colour syntax | deriving hover, tint and shade from one token | Sep 2024 | a literal colour first |
| `@property` | typed, animatable custom properties | Jul 2024 | static value |
| Popover | menus and tooltips in the top layer without JavaScript | Jan 2025 | fine for most audiences |
| Style queries on custom properties | variants driven by a token | May 2026 | default variant |
| Scroll-driven animations | scroll scenes, entrances, parallax, progress, off the main thread (`scroll-motion.md`) | Oct 2026 | static page; hidden start states only inside `@supports` |
| `field-sizing` | inputs and textareas that grow with content | Jun 2026 | fixed size |
| `sibling-index()`, `sibling-count()` | staggered delays without inline styles | Aug 2026 | no stagger |
| `shape()` | responsive clip paths | Feb 2026 | rectangular |
| `contrast-color()` | automatic black or white text on a colour | Apr 2026 | a chosen colour first |
| Invoker commands (`command`, `commandfor`) | declarative button actions | Dec 2025 | check the audience's browsers |

## Not yet in every engine: progressive enhancement only

| Feature | Status | Note |
| --- | --- | --- |
| Anchor positioning | core in all engines since Jan 2026, but the dataset still marks the whole feature as not Baseline (some values lack Firefox) | give a fallback position |
| View Transitions, cross-document | Chrome and Safari, not Firefox | navigations still work without |
| `text-wrap: pretty` | Chrome and Safari | harmless elsewhere |
| Customizable `<select>` | Chrome and Safari 27 | falls back to the native select |
| `interpolate-size`, `calc-size()` | Chrome only | no animation to `auto` elsewhere |
| Scroll-state queries | Chrome only | style stuck or snapped states as an extra |
| `corner-shape` (squircles, notches) | Chrome only | falls back to round corners |
| CSS `if()` | Chrome only | only after a normal declaration |
| Grid lanes (masonry) | Safari only | falls back to grid |
| `reading-flow` | Chrome only | keep DOM order correct; do not rely on it |
| `hanging-punctuation` | Safari only | cosmetic |
| `ui-sans-serif`, `ui-serif`, `ui-rounded`, `ui-monospace` | Safari only | use `system-ui` and named stacks |

## What this replaces

- JavaScript for layout decisions: container queries, `:has()`, subgrid.
- Animation libraries for simple state changes: View Transitions, `@starting-style`, `linear()`.
- Popper-style positioning code: popover and anchor positioning, with a fallback.
- Preprocessor colour functions: `color-mix()`, relative colours, `light-dark()`.
- Scroll listeners for progress and sticky effects: scroll-driven animations, as an enhancement.
- Hand-inserted `<br>` in headings: `text-wrap: balance`.

A motion or component library is still reasonable for complex gestures,
shared-element choreography and accessible composite widgets. Choose it for
that, not by habit, and record it in DESIGN.md.

## Rules

- Write the plain version first, then enhance inside `@supports` or with a fallback declaration before the new one.
- Content never depends on an enhancement: a hidden start state exists only inside `@supports (animation-timeline: view())` and `prefers-reduced-motion: no-preference`, so browsers without the feature, and reduced motion, show the finished page.
- Everything animated has a `prefers-reduced-motion` path.
- Test in the browsers the audience uses, not only the one at hand. `render_check.py` uses Chrome; say so when reporting.
