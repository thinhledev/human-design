# Sources, studied references and licences

Everything here was checked on 22 November 2026. Re-check before relying on
anything older than six months. Sources are written as site and path.

## 1. What this skill is built from

- **Platform guidelines** (documented): Apple Human Interface Guidelines (developer.apple.com/design/human-interface-guidelines), Android and Material 3 documentation (developer.android.com; github.com/material-components/material-components-android docs), Windows app design (learn.microsoft.com/en-us/windows/apps/design), GNOME HIG (developer.gnome.org/hig), WCAG 2.2 (w3.org/WAI/WCAG22).
- **Research**: Nielsen Norman Group articles (nngroup.com/articles), Baymard Institute's public findings (baymard.com), Nouwens et al. 2020 on consent banners (arxiv.org/abs/2001.02479). Colour: Bottomley and Doyle 2006 on colour appropriateness to product type (Marketing Theory 6(1); orca.cardiff.ac.uk/id/eprint/2579), Labrecque and Milne 2012 on colour and brand personality (JAMS 40; doi 10.1007/s11747-010-0245-y), Ou and Luo 2006 on two-colour harmony (Color Research and Application 31(3)), Machado, Oliveira and Fernandes 2009 on simulating colour vision deficiency.
- **Colour combinations**: Figma's resource library, 100 combinations (figma.com/resource-library/color-combinations), read 27 November 2026. The skill stores each combination's name, group and printed hex codes with a link back, plus its own analysis and tags; it copies none of Figma's descriptions or images.
- **Vendor surveys of colour by sector**: Bynder's analysis of 15,388 logos (bynder.com/en/blog/the-most-and-least-used-colors-in-logos); 99designs' logo study as reported by The Drum (thedrum.com, 14 August 2018).
- **Practice**: Butterick's Practical Typography (practicaltypography.com), Bringhurst as summarised at webtypography.net, Every Layout (every-layout.dev), Evil Martians on OKLCH, Ottosson on OKLab (bottosson.github.io/posts/oklab/).
- **Platform status**: the web-features dataset (github.com/web-platform-dx/web-features).
- **Studies of generated design**: Anthropic's frontend-design skill and blog post (github.com/anthropics/skills; claude.com/blog/improving-frontend-design-through-skills), Adrian Krebs's scan of Show HN pages (adriankrebs.ch/blog/design-slop/), Jenny Ouyang's count on 120 pages (buildtolaunch.substack.com), J. Carter Johnson's ranking (github.com/JCarterJohnson/vibecoded-design-tells).
- **Observation of live work**: the references in section 2, opened in a browser and described in our own words.

No design, image, illustration, code or text from any third party is included
in this skill.

## 2. References studied (for taste calibration)

Opened on 22 November 2026 at about 800px wide. Typefaces were read from
computed styles; foundries are named only where certain. Sites change: treat
each note as what was observed that day. Use these to learn what decisions
look like, never as templates to copy.

| Reference | Surface | Tradition | What was decided |
| --- | --- | --- | --- |
| PostHog (posthog.com) | marketing | playful, illustrated | The site is a fake desktop with windows and icons; a hedgehog mascot; mustard buttons with a hard bottom edge like a key; self-aware copy |
| Oxide Computer (oxide.computer) | marketing | engineering drawing | One weight of a Swiss grotesque even at 65px; mono figure captions; phosphor green from terminals and rack LEDs; the hero is a working console |
| Low-tech Magazine, solar edition (solar.lowtechmagazine.com) | marketing | raw, editorial | No web fonts; dithered single-colour photos; page weight printed on the page; a background that shows the server's battery level |
| Floema (floema.com) | marketing | International style, warm | One sans, tightly tracked; paper ground and brown-black ink; a loose cloud of product photos around one sentence |
| MOXIE Theatre (moxietheatre.com) | marketing | poster, wood type | A condensed slab wordmark edge to edge; one flat pink with black; listings with thick rules and big dates like a season brochure |
| Are.na (are.na/explore) | web app | raw, utilitarian | Black and white only; outlined square cells; plain text lists for sorting; no icons, no brand colour |
| Kinopio (kinopio.club) | web app | handmade, playful | The homepage is a real canvas; personal imagery; dotted paper ground; a one-person voice |
| Linear (linear.app) | web app | dark precision | Widely imitated, which is the lesson: odd weights and negative tracking, a stepped cool grey scale, almost no accent, product UI as the hero |
| Ableton Live (ableton.com/en/live) | desktop app | expert tool, collage | Futura with a huge tight serif; hand-scrawled lettering over photos; a rotated sticker; real, messy studios |
| Nova by Panic (nova.app) | desktop app | Mac-native, retro neon | Wide-gamut navy, hot pink and lime; the hero is the real editor with the pitch written as a README |
| iA Writer (ia.net/writer) | desktop app | Swiss reduction | Its own type family; monochrome with one cyan for the caret; the hero is a window holding only text |
| Flighty (flighty.com) | mobile | dense, airport signage | System type, huge numerals; a phone held by a real hand; departure-board glyphs |
| (Not Boring) Software (notbor.ing) | mobile | toy-like 3D | Pale ground so rendered icons supply the colour; catalogue numbers like records; skins released as artist series |
| Pocket Casts (pocketcasts.com) | mobile | bold, media-led | One organic red shape on near-black; colour from real podcast artwork; Android first |
| Teenage Engineering store (teenage.engineering/store) | store | Swiss, industrial | Custom light grotesque, all lowercase, about 14px; pictogram navigation; straight-on product shots on grey tiles; orange only where the hardware has it |
| Flamingo Estate (flamingoestate.com) | store | warm craft | A serif display with a tracked grotesque for labels; olive ink on cream; colour from the produce; press mastheads as attributions |
| Our Legacy (ourlegacy.com) | store | fashion, raw minimal | One grotesque in two weights at 13.5px; warm white and brown-black; text hung left beside one tall image; no buttons or prices on the home page |
| Shopify Horizon demo (theme-horizon-demo.myshopify.com) | store | clean default | The neutral baseline: a four-up grid of consistent photos, name and price in two plain lines, no card chrome |

**What they share, and generated work lacks**

1. Type chosen for the subject, never the framework default.
2. One or two families, often one weight; hierarchy from size and position.
3. Tinted neutrals (putty, cream, olive, brown-black); pure white and pure black are rare.
4. An accent with a source: LEDs, produce, artwork, the product.
5. The real product or real photography as the hero; no abstract blobs.
6. Asymmetric layouts or text hung from one edge; centred stacks are the exception.
7. Small text that is confidently small (11 to 14px) and tracked on purpose.
8. Copy with a speaker: jokes, flat claims, first person.
9. One convention broken deliberately.
10. Cards, shadows, pills and icons left out unless they carry meaning.

## 3. Licences: what may be studied, reused and shipped

| Source | Study | Reuse in a commercial product | Redistribute inside a paid, proprietary product |
| --- | --- | --- | --- |
| Dribbble shots | view only | no; creators own the work | no; scraping is banned by the terms |
| Pinterest pins | view only | no | no; scraping is banned |
| Behance projects | view only | only where the creator set a Creative Commons licence | no |
| Figma Community free files | yes | yes, with attribution (CC BY 4.0 by default) | with attribution; paid files no |
| WordPress.org themes | yes | yes | only under GPL-compatible terms, so not in a proprietary product |
| Shopify Dawn | yes | only for Shopify themes | no |
| Shopify Horizon | yes | only for Shopify themes; derived themes may not be sold or distributed | no |
| Shopify Polaris | yes | only for apps that integrate with Shopify | no |
| Unsplash, Pexels | yes | yes | not sold unaltered or as a competing collection |
| Google Fonts (SIL OFL) | yes | yes | bundling allowed with the licence and notice; fonts not sold alone; modified versions stay OFL and drop reserved names |
| Fontshare (ITF free font licence) | yes | free commercial use; not open source | licence text not verified; link, do not bundle |
| Lucide (ISC); Phosphor, Tabler, Heroicons, Iconoir, Feather (MIT) | yes | yes | yes, with the notice |
| Material Symbols (Apache 2.0) | yes | yes | yes, with licence and notices |
| Remix Icon (own licence since Jan 2026) | yes | yes | only as part of a larger product, never as an icon pack |
| SF Symbols | yes | Apple-platform apps only; never in icons, logos or trademarks | no |
| shadcn/ui, Radix, Primer, Ant Design, Open Props (MIT) | yes | yes | yes, with the notice |
| Material, Carbon (Apache 2.0) | yes | yes | yes, with licence and notices |
| GOV.UK Frontend (MIT) | yes | yes, without the GDS Transport font or crown | same limits |
| Fluent UI (MIT) | yes | yes; fonts and icons under a separate licence | code yes, assets per their licence |

Rules for any project made with this skill:

- Learn from anything you can view; describe patterns in your own words; copy nothing that is not licensed for the use.
- Check the licence of every font, icon and image before it ships, and list them in DESIGN.md.
- Never scrape design galleries. Never reproduce a competitor's layout, illustration or copy.

## 4. Other design skills (the landscape)

| Skill | What it does | Limits noted |
| --- | --- | --- |
| Anthropic frontend-design (Apache 2.0) | Studio-lead stance, token plan, named AI clusters including the cream and terracotta look | no checker; the same model critiques its own work |
| Impeccable (Apache 2.0) | commands for critique and polish, context files, a 62-rule deterministic detector | by its author's account strongest on existing UI, not one-shot design; web only |
| taste-skill (MIT) | deals a palette, font pairing and one of 11 hero layouts from bundled libraries; headless checker | company websites only; a finite deck can become a signature (inference) |
| ui-ux-pro-max (MIT) | searches CSV databases for a per-industry design system | retrieves stock recipes |
| Vercel web-design-guidelines | reviews files against interface rules | hygiene, not identity |
| Emil Kowalski's skills (MIT) | animation craft; logs taste corrections | motion-centred |

A deterministic tell detector is common. What was not found in any of them:
checks over SwiftUI or Compose source, measured false-positive rates per rule,
a published blind evaluation, and a defence against the skill's own
signature. This skill addresses the first and the last (`slop_check.py`
native checks; `fingerprint.py --against`); it has not yet published
false-positive rates or a blind evaluation, and says so.

## 5. This skill's own benchmark

22 November 2026. Two briefs (a landing page for a bookkeeping tool for
physiotherapy clinics; the main screen of a wholesale plant nursery app), each
built twice by a fresh agent: once with the host's default design guidance and
once with an earlier version of this skill, with the registry check disabled.
Measured with this skill's own scripts, so treat it as a first look, not an
independent evaluation.

| | Default guidance, landing page | Default guidance, app | Skill, landing page | Skill, app |
| --- | --- | --- | --- | --- |
| Type sizes at 1440px | 13 | 7 | 6 | 4 |
| Spacing off the 4px scale | 53% | 60% | 0% | 1% |
| Measured errors | none | contrast, targets under 24px | none | none |
| Identity recorded | no | no | yes | yes |
| Ground and ink | pale grey-green, pine | pale grey-green, pine | pale grey-green, pine | white, neutral |
| Accent | indigo | violet | blue | blue |
| Text face | Instrument Sans | Atkinson Hyperlegible Next | Atkinson Hyperlegible Next | Atkinson Hyperlegible Next |

Similarity between the two unrelated products: 50% with the default guidance,
75% with the earlier version of the skill (same typeface, accent hue, radius
and depth). The default-guidance pages had more visual personality; the skill
pages were plainer. The findings led to the `--taken` step, the hard rules on
shared typefaces and colours, the "sage paper and pine ink" look in the
catalogue, and the warnings about habits and plainness in `identity.md`.

## 6. Not verified (do not present as fact)

- Material's own site (m3.material.io) could not be read; Material numbers come from Google's Android component documentation.
- Fontshare's licence text; Velvetyne's licences; Behance's scraping clause.
- Baymard's survey year and sample for the abandonment reasons.
- Any controlled study of hero video; any Tauri-specific native-feel source.
- The "default" status of Plus Jakarta Sans, Poppins and Playfair Display (reputation, not measurement).
- Per-pattern percentages from the Show HN scan (reported second-hand with a conflicting sample size).
- Native-code tells: this skill's extrapolation; no published catalogue was found.
- Domain colour conventions: practice from secondary descriptions. The developer-tools description comes from third-party write-ups of Linear, Vercel and Supabase, not their own tokens. Neil Patel's claim that green tests best in health (6,306 A/B tests) was not checked against its method. The harmony thresholds, the timid and competing rules and every tag in the library are this skill's judgement (inference).
