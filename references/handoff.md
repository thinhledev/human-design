# From design to code

The identity survives only if the code uses it. Most designs lose their
character in implementation: the font silently falls back, a component kit's
defaults win, one-off values creep in.

## 1. Tokens are the contract

```bash
python3 scripts/tokens.py design.json --css src/styles/tokens.css        # any web project
python3 scripts/tokens.py design.json --tailwind src/styles/theme.css    # Tailwind v4 @theme
python3 scripts/tokens.py design.json --json tokens.json                 # other pipelines
python3 scripts/tokens.py design.json --swift Tokens.swift --kotlin Tokens.kt
```

- Edit `design.json`, regenerate, commit both. Never hand-edit generated files.
- Components use roles (`--bg`, `--surface`, `--text`, `--text-muted`, `--accent`, `--second`, `--highlight`, `--border`, `--good` and the other status roles), never ramp steps or literal colours. Charts use `--chart-1` to `--chart-6` in order. Ramps exist for rare one-offs.
- Type uses the scale tokens with their own line height and tracking. No `text-[13px]`.
- Spacing, radius, shadow and motion use their tokens. A value not in the scale is a design decision: add it to design.json or use the scale.

## 2. Web frameworks

- **Plain CSS, CSS modules, Vue, Svelte, Astro**: import `tokens.css` once at the root; write components against the custom properties.
- **Tailwind v4**: import the generated `@theme` file after `tailwindcss`; it defines the font, text, spacing, radius and colour utilities from the tokens. Remove or avoid the default palette classes (`bg-indigo-500`); use role utilities (`bg-surface`, `text-muted`).
- **Tailwind v3**: map the custom properties in `tailwind.config` (`colors: { bg: 'var(--bg)' }` and so on) and turn off the default palette if the team agrees.
- **A component kit (shadcn/ui, Radix themes, MUI, Chakra)**: a kit is scaffolding. Replace its theme tokens with the project's before building any screen: font variables, radius, the neutral scale, primary and ring colours, shadows. Then restyle the few components that carry the identity (button, input, card or its absence, table, navigation). An untouched kit is the single most recognised generated look.
- **Icons**: one set, one stroke weight, sized on the type scale; decide in DESIGN.md which things get icons at all.
- **Fonts**: self-host WOFF2 or use the framework's font loader; declare a metric-matched fallback; confirm with `render_check.py` that the face loaded in the built app.

## 3. Native

- **SwiftUI**: brand colours as an asset catalogue or the generated tokens, mapped to roles; system text styles, or custom fonts with `relativeTo:` so they scale; system materials and controls first. Use NSColor on macOS.
- **Jetpack Compose**: build a Material 3 `ColorScheme`, `Typography` and `Shapes` from the tokens and pass them to the theme. No literal `Color(0x…)` or `.sp` sizes in composables. Delete the starter theme's Purple80 and friends.
- **React Native, Flutter**: one theme object from the tokens; platform-adaptive components for navigation, back, switches, sheets and pickers.

## 4. States and motion in code

- Build the primitives once (button with busy and done, field with invalid, skeleton, toast, link pending), from the state sheet, then apply them screen by screen.
- Motion tokens on the root; `prefers-reduced-motion` handled once, centrally.
- Optimistic updates with a revert path for predictable actions (`states-motion.md`, section 3).

## 5. Verifying the build

1. `python3 scripts/slop_check.py src --identity design.json --surface <surface>`: no strong tells.
2. Start the app; `python3 scripts/render_check.py http://localhost:3000/<route> --out shots --widths 390,1440 --schemes light,dark --squint` for each main route: no errors.
3. Compare the screenshots with the mockups and with DESIGN.md. Differences are either bugs or decisions to record.
4. `python3 scripts/fingerprint.py src --save <project> --against`.
5. Run the project's own checks (types, lint, tests, build).

## 6. Mockups

An HTML mockup made with this skill is a design artefact, not production code:
real content, the real tokens, every state, phone and desktop widths. Keep
mockups and the state sheet in the repository (for example `design/`), so the
next change starts from them. When a mockup stands for a native screen, say
plainly that it is a picture and list what the native implementation must
take from the platform.
