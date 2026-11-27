# States and motion: designs that answer

A screen drawn only at rest is half a design. The static look of generated UI
comes from mockups with one state per component and motion added afterwards as
decoration. Draw the states first; then motion is just how one state becomes
the next.

## 1. Every interactive component has six states

Design all six on the state sheet (`assets/state-sheet.template.html`) before
building screens.

| State | What it must show | Rules |
| --- | --- | --- |
| Rest | that it can be used | interactive things look interactive; text links are underlined or clearly coloured |
| Hover | "this responds" (pointer devices only) | a colour or underline change; no layout movement, no growing cards |
| Focus-visible | where the keyboard is | a ring at 3:1 against its surroundings, never removed without a replacement |
| Pressed | "I felt that", within one frame | `:active` scale to about 0.97 or a darker fill, 80ms; before any handler runs |
| Busy | work is happening | full opacity, progress in place (spinner beside the label, label in -ing), `aria-busy="true"`, `cursor: progress`; the control keeps its resting width |
| Disabled | not available, and why | reduced contrast, `cursor: not-allowed`; say why nearby when it is not obvious |

Busy is not disabled. A faded, unresponsive button after a click reads as
broken.

After the work: **done** (the label says the past tense, "Saved", with a
check, for about 1.2s) or **failed** (what went wrong and what state things
are in now).

Inputs add: filled, invalid (message under the field, not only a red border),
read-only. Selections add: selected, and selected plus focus.

## 2. Every data view has five states

| State | Design |
| --- | --- |
| Loading | a skeleton shaped like the content it replaces, built from the real layout; "show something as soon as possible" (documented: Apple HIG, loading) |
| Empty | what will appear here, why it is empty, and the one action that fills it (research: nngroup.com/articles/empty-state-interface-design/) |
| Error | what failed, what still works, how to retry; inline where the content would be |
| Partial | some data, more coming or some failed: say which |
| Ideal | the screenshot everyone designs |

On phones add offline and permission denied (ask in context, explain the
benefit, degrade gracefully). Draw empty and error for every list and
dashboard panel; they are the first screens a new user sees.

## 3. What each action should do

| Action | Treatment |
| --- | --- |
| Toggle, mark read, rename, reorder, dismiss, pause or resume | Optimistic: change now, request behind, take the server's value on success, revert and say why on failure |
| Delete | Remove at once after the confirm, or with Undo; on failure put it back in place and say so |
| Create, publish, pay, upload, generate, anything the server validates or charges for | Not optimistic: busy, then the real result |
| Save on a page that stays | Busy, then done for about 1.2s |
| Leaving for checkout, sign-in or another site | Busy until the page leaves; reset if the user comes back |
| Navigation | A pending sign on the link at once, then the route's skeleton, then the page |
| Polled progress | Ease between values; never jump or restart |

Report a failure inline when the control is still on screen, otherwise in a
toast; never both, and never a toast for a change the screen already shows.
Success toasts hide themselves in about 4 seconds; errors stay until
dismissed.

## 4. Motion

Motion explains a change: where something came from, what it became, that the
tap registered. If it does not explain a change, it is decoration and usually
makes a design look more generated, not less.

**Tokens** (put them in design.json; `tokens.py` emits them):

| Token | Value | Use |
| --- | --- | --- |
| press | 80ms | pressed state |
| fast | 150ms | hover, colour, small fades |
| base | 200ms | things entering or leaving, menus, toasts |
| slow | 300 to 400ms | large surfaces (sheets, drawers), progress easing |
| ease-out | `cubic-bezier(.2,.8,.2,1)` | entering and responding |

**Rules**

- Animate `transform` and `opacity` only. Width, height, top, left, margin and `background-position` cause layout or repaint every frame.
- Name the properties; never `transition: all`.
- Enter with ease-out, exit faster than enter, never bounce or overshoot on interface chrome.
- One orchestrated moment per screen at most (a page-load sequence, a hero demonstration, a scroll scene on a landing page). Not the same fade-up on every section. Content in view is visible at rest, and nothing waits at `opacity: 0` for a script; marketing pages follow `scroll-motion.md`.
- No count-up numbers, typewriter headlines or endless ambient loops. A spinner and a skeleton sweep are the only endless animations that earn their place.
- **Reduced motion**: under `prefers-reduced-motion: reduce`, remove movement (transforms, slides, parallax, auto-play) and keep meaning (a spinner becomes a slow opacity pulse). `render_check.py` counts animations that keep running.
- Performance beats motion. If an animation could cost a frame on a slow phone, leave it out.

**Give the motion a character from the identity**, in one line of DESIGN.md:
"quick and flat" (a tool), "weighted, things settle" (a physical-product
store), "none beyond state changes" (a reading app). Then the same durations
and easing everywhere.

**Platform capabilities** (status in `platform-web.md`): same-document View
Transitions for state changes that move an element, `@starting-style` with
`transition-behavior: allow-discrete` for entering from `display: none`,
`linear()` easing for a spring where the platform calls for one,
scroll-driven animations as a progressive enhancement, with every hidden start
state inside the reduced-motion and `@supports` guards (`scroll-motion.md`). Native: use the platform's own springs and transitions
(Material 3 motion scheme; SwiftUI's defaults) before custom curves.

## 5. Native and desktop

- iOS and Android: system components already carry pressed, focus and disabled states and the platform's haptics; custom controls must reproduce them. Use haptics only for their documented meanings.
- Desktop: hover and focus matter more (pointer and keyboard); add selected-but-inactive (window not focused), drag over, and drop target states. Windows in the background look different from the key window.
- Keyboard: every action reachable, focus order follows reading order, focus returns to the trigger when a dialog closes.

## 6. Checklist

- A state sheet exists and covers every interactive component and every data view.
- Pressed and focus-visible are present everywhere (`slop_check.py` flags their absence).
- Busy is distinct from disabled; done and failed are designed.
- Each action follows the treatment table; failures say what happened and what state things are in.
- Motion uses the tokens, only transform and opacity, with a reduced-motion path.
- Nothing in the first screen starts invisible; nothing in view is invisible at rest; nothing is hidden without scripts or under reduced motion (`render_check.py --motion`).
