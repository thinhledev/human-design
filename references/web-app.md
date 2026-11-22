# Web app UI

Product interfaces are operated, not read. The craft shifts from expression
to information design: what the user needs to see, decide and do, with the
least looking. Research checked 22 November 2026.

## 1. Start from tasks and objects

- List the user's top five tasks and the objects they act on (invoices, classes, runs, tickets). The navigation is the list of objects; each screen serves one task.
- For each screen write: what the user came to find out, what they will do next, what would make them stop. Put the answer to the first where the eye lands.
- Use real data to design: real names of real length, the largest plausible number, the row with the missing field, zero items and ten thousand.

## 2. The generated dashboard, and what to do instead

The default is four stat cards, a chart and a table, inside cards, inside a
sidebar layout, with a different pastel on each icon.

- **Summary before detail, but only the numbers that drive a decision.** If nobody acts on a figure, it is decoration. Three related figures often read better as one sentence or a small table than as tiles.
- **State in form, not only numbers**: what needs attention is visible at a glance (a status label, a count on the nav item, the overdue rows first).
- **One surface.** Use space and hairlines to separate regions; keep cards for objects the user picks up (a draggable task, a selectable plan).
- **Charts with the care of type**: a title that states the finding, direct labels instead of a legend, a faint grid, real units, the last point emphasised, colours from the tokens. A chart is only worth its space when the shape matters.
- **Semantic colour is separate from the accent**: good, warning, bad mean something everywhere they appear, and never rely on colour alone.

## 3. Navigation and structure

- Visible, persistent navigation on desktop: a sidebar for many destinations, tabs for a few peers. Hidden navigation halves discovery (research: nngroup.com/articles/hamburger-menus/).
- Tell users where they are: the current item marked, a page title that matches the nav label, breadcrumbs only for real depth.
- Keep primary actions in one place per screen type; destructive actions away from them.
- URL per view, so back, reload and sharing work.
- Search and a command palette for tools used daily.

## 4. Tables and lists

Tables serve four tasks: find a record, compare records, view or edit one row,
act on several (research: nngroup.com/articles/data-tables/).

- First column: a human-readable identifier. Numbers right-aligned with `tabular-nums`; text left-aligned; units in the header.
- Freeze the header (and the first column when wide). Row hover or zebra to hold place; not both.
- Row height by density (`layout.md`): 32 to 40px for working tools.
- Sorting, filtering and column choice where there are more than a screenful of rows; show applied filters and a clear-all.
- Bulk actions appear when rows are selected, with the count.
- Truncate with care: never the identifier; show the full value on hover or in the detail.
- Empty, loading (skeleton rows shaped like real rows) and error states designed (`states-motion.md`).

## 5. Forms

- One column, labels above fields, in the order people think about the answers (research: nngroup.com/articles/web-form-design/).
- No placeholder as a label; placeholders vanish and fail contrast (research: nngroup.com/articles/form-design-placeholders/).
- Mark optional fields (or both required and optional when mixed). Ask only for what is needed now.
- Field width hints at the expected length. Group related fields; use the right input type and `autocomplete`.
- Validate on blur or submit, not on every keystroke; say what is wrong and how to fix it, beside the field; keep what the user typed.
- The submit button names the action and shows busy, then done.
- Long forms: save drafts; steps only when the task really has stages.

## 6. Onboarding and empty states

- Skip onboarding when the product can be understood by using it; keep any instructions brief and optional (research: nngroup.com/articles/mobile-app-onboarding/).
- The empty state is the onboarding: show what will be here, why it is empty and the one action that starts it (research: nngroup.com/articles/empty-state-interface-design/). Sample data, clearly marked, beats an illustration.
- First-run defaults should produce a useful screen without configuration.

## 7. Feedback and behaviour

Every control answers; predictable actions are optimistic; data views have
loading, empty, error and partial states; navigation gives a pending sign at
once. All of it is in `states-motion.md` and is part of the design, drawn on
the state sheet before the screens.

## 8. Density, type and colour

- Decide density from who uses it and for how long. Tools used all day: 13 to 14px text, compact rows, more on screen.
- Five to seven type sizes; weight and colour do most of the ranking.
- The accent marks the primary action and the current selection, and little else. Most of a tool is neutral.
- System font stacks are a legitimate, deliberate choice for tools; a chosen text face with good figures is the alternative. Either way it is written in DESIGN.md.
- Dark mode is a second design (`color.md`).

## 9. Accessibility floor

- Everything reachable and operable by keyboard, focus visible and in order; dialogs trap focus and return it.
- Names and roles for controls; status changes announced (`aria-live`, `aria-busy`).
- Targets 24px minimum; text contrast 4.5:1; never colour alone.
- Works at 200% zoom and 320px width without two-way scrolling, except data tables.

## 10. Checklist

- Each screen serves one named task; the answer the user came for is where the eye lands.
- No tiles, charts or cards that nobody acts on.
- Real data, including the awkward rows, zero and many.
- All states drawn; keyboard path works.
- Passes `slop_check.py --surface app` and `render_check.py`; critiqued by eye.
