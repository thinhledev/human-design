# Imagery: real photographs before drawn art

Checked 27 November 2026. Grades: documented, practice, research, vendor, inference.

A page that needs pictures gets real ones. Hand-drawn stand-ins (an SVG loaf,
a cartoon plant, a vector person at a laptop) read as filler and as generated;
a good photograph of the actual thing persuades. When there is no illustrator,
do not imitate one (`marketing.md` section 5). Draw only what is a diagram,
a chart, an icon or the product's own interface.

## 1. Where pictures come from, in order

1. **The owner's own**: photographs of the product, the place, the people, the work. Ask for them in the brief (`identity.md` section 1). Nothing beats them.
2. **The product itself**: real screens with real data, the real object.
3. **Free photo libraries**, searched for this subject (section 2).
4. **Open collections** for history, science, nature and art: museum and agency archives (section 2).
5. **Generated images** only when the owner asks for them, and never as people presented as customers or staff.

Placeholders are the last resort: label them with what goes there and the aspect
ratio, and say so in the hand-off.

## 2. Free sources and their licences

| Source | Licence in short | Notes |
| --- | --- | --- |
| Pexels (pexels.com) | free for commercial use, no attribution required, may be modified; not for selling unaltered copies, implying endorsement by people or brands shown, or use as a trademark (documented: pexels.com/license, read 27 November 2026) | Search pages refuse plain HTTP clients; search in a browser, then download from the image CDN (section 3). |
| Unsplash (unsplash.com) | free for commercial use, no attribution required, may be modified; not for selling without significant change or building a competing service (documented: unsplash.com/license, read 27 November 2026) | The site sits behind a bot check; use a browser. Apps built on the Unsplash API must hotlink and credit (documented: help.unsplash.com API guidelines); a downloaded file used on a page is under the plain licence. |
| Pixabay (pixabay.com) | its own content licence, similar to Pexels | Not checked here; read the licence on the page before use. |
| Openverse (openverse.org; api.openverse.org) | Creative Commons and public-domain works from Flickr, museums and others; each image carries its own licence | Its API answers without a key. Filter for commercial use and modification; CC BY and BY-SA need attribution, BY-SA needs share-alike. |
| Wikimedia Commons (commons.wikimedia.org) | per file: public domain, CC0, CC BY, CC BY-SA | Its API answers without a key; send a descriptive User-Agent. Read each file's licence. |
| Museum open access: The Met, Art Institute of Chicago, Rijksmuseum, Smithsonian Open Access | public-domain works released as CC0 (practice; check each object page) | Paintings, prints, objects, archive photography: strong for editorial, food history, craft. |
| NASA image library | most media not copyrighted (practice; logos and some third-party images excepted) | Space, Earth, science. |

Whatever the source: no photograph of an identifiable person may stand in for a
customer, a testimonial, a team member or a user (`copy.md`: no invented proof).
Stock people may appear as people doing the activity, never as evidence.

## 3. Finding the right photograph

- **Search with the world study's words, not the category's**: "scored sourdough on a cooling rack", "flour on a steel bench at dawn", not "bakery". Try three to five searches and look at forty pictures before choosing.
- **Choose for the identity**: light (dawn, overcast, tungsten), colour that sits with the palette (a photograph can supply the palette: sample it), distance (macro, table, room) and the same treatment across the page. Prefer one photographer or one series for a page; mixed styles read as stock.
- **Avoid the stock look**: handshakes, people pointing at laptops, staged diversity groups, glossy perfect food, skylines that could be anywhere.
- **Crop with intent**: a photograph is a layout element. Decide where the text sits (a dark quiet side, a plain sky) before cropping.

In practice for an agent: search pages of Pexels and Unsplash need a real
browser (the host's browser tool); Openverse and Wikimedia Commons have open
APIs. On a Pexels result, the photo id gives a sized download:
`https://images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg?auto=compress&cs=tinysrgb&w=2000`.
Download into the project and host it there; do not hotlink from a library
page.

## 4. Serving it without costing speed or SEO

- Export at the sizes the layout needs (for example 800, 1400 and 2000px wide) as WebP or AVIF with a JPEG fallback (`cwebp`, `avifenc`, `sips`, `ffmpeg` or the framework's image pipeline). A hero rarely needs more than 200 to 300 KB.
- `<img>` with `srcset` and `sizes`, `width` and `height` (or `aspect-ratio`) so nothing shifts, and an `alt` that says what the picture shows in this page's words (good for screen readers and image search).
- The first screen's main image is eager, `fetchpriority="high"`, and never behind an animation (`scroll-motion.md`). Every other image is `loading="lazy"` and `decoding="async"`.
- Text over a photograph needs a scrim or a quiet area and must pass contrast where it sits (`color.md` section 4; `render_check.py` lists text over images for a look).
- Keep the file name and the `alt` descriptive (`scored-sourdough-loaves-on-rack.webp`).

## 5. Credit and record

List every picture in DESIGN.md under Assets: file, source page URL,
photographer, licence, date downloaded, and any change made. Credit
photographers on the page where the licence asks for it (CC BY), and where it
does not, a small credit line is still good practice.
