# Design: <project>

Read this before designing or changing any screen. It records decisions already
made; follow them. To change one, change it here first, with a reason.

Numbers live in `design.json`; tokens are generated with
`python3 <skill>/scripts/tokens.py design.json --css <path>/tokens.css`.

## Subject

- What it is, for whom:
- The one job of the product (and of the main screen):
- Where and how it is used:
- Surfaces: <marketing site | web app | desktop app | mobile app | store>

## The subject's world

- Materials and objects:
- Its documents and screens (vernacular):
- Colours, each with its source:
- Units, terms and conventions that must appear as content:
- Category conventions kept:
- Category habits refused:

## Voice

| Word | Means on screen | Does not mean |
| --- | --- | --- |
| | | |

## Decisions

| Decision | Choice | Reason (names the subject) |
| --- | --- | --- |
| Text face | | |
| Display face | | |
| Mono or data face | | |
| Type scale | | |
| Ground | | |
| Neutrals | | |
| Palette: the combination it started from, and what in the subject moved it | | |
| Harmony (monochromatic, analogous, complementary...) | | |
| Primary and where it may appear | | |
| Secondary and highlight: the job of each | | |
| Density | | |
| Layout concept | | |
| Shape (radius by role) | | |
| Depth | | |
| Imagery | | |
| Motion | | |
| Copy voice | | |

## Signature

<The one deliberate, memorable choice, and the reason it belongs to this subject.>

## Refusals

1.
2.
3.

## States (every interactive component)

Rest, hover, focus-visible, pressed, busy, disabled; for data: loading, empty,
error, partial. Motion tokens and rules: see `design.json` "motion".

## Fonts and licences

| Face | Source | Licence | Files or link |
| --- | --- | --- | --- |

## Pictures and licences

Real photographs, never hand-drawn stand-ins (references/imagery.md).

| File | Shows | Source page | Photographer | Licence | Downloaded | Changes |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

## Scroll motion (marketing pages)

<The one scene and what in the subject it shows; the quieter entrances; what moves on load (decorative layers only). Checked with render_check.py --motion on DATE.>

## Directions considered

| Direction | Bet | Why rejected or chosen |
| --- | --- | --- |

## Taste (corrections from the owner)

- <date>: "<what they said>" -> <what changed>

## Decision log

- <date>: <decision>, because <reason>
