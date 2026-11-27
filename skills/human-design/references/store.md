# Online stores

A store sells when buyers can see the product, trust the seller and pay
without friction. The generated store is rounded cards, star ratings, sale
ribbons, "Shop now" gradients and a discount popup. Research checked 22
November 2026; Baymard figures are from its public pages (baymard.com).

## 1. The numbers that should shape the design

- **Cart abandonment averages 70.22%** across 50 studies. Reasons given by shoppers: extra costs too high 40%, delivery too slow 20%, did not trust the site with card details 19%, had to create an account 18%, checkout too long or complicated 17%, website errors 17%, returns policy 13%, could not see the total up front 12%, card declined 10%, too few payment methods 9% (research: baymard.com/lists/cart-abandonment-rate).
- **Checkout length**: the average US checkout has 23.48 form elements (14.88 fields); 12 to 14 elements (7 to 8 fields) is achievable. Baymard estimates better checkout design could lift conversion by 35.26% (research, same page).
- **Checkout failings** (2026): 47% of sites do not make guest checkout the most prominent option; 56% do not delay account creation to the confirmation step; 50% do not mark both required and optional fields (research: baymard.com/blog/current-state-of-checkout-ux).
- **Product pages** (2026): rated mediocre or worse on 52% of desktop and 62% of mobile sites; 57% lack size buttons, 81% lack price per unit where it applies, 44% hide the return policy (research: baymard.com/blog/current-state-ecommerce-product-page-ux).
- **Lists and filters**: poor to mediocre on 58% of desktop and 78% of mobile sites; 51% lack all five essential filter types; 20% lack an overview of applied filters (research: baymard.com/research-articles/current-state-product-list-and-filtering).

## 2. Home and navigation

- Say what the store sells within the first screen: the products themselves, a clear category structure, not a lifestyle slideshow.
- Categories in visible navigation; search prominent when the catalogue is large.
- No auto-rotating carousel: use one strong static image or a static set (research: nngroup.com/articles/designing-effective-carousels/).
- No popup on arrival. Offer the newsletter in the page or at exit, once.

## 3. Product lists

- Consistent photography on a consistent ground; the same aspect ratio for every tile.
- Per tile: image, name, price (and unit price when relevant), variant swatches when they change the picture. No card chrome needed: the references use the grid and two lines of text.
- Filters that match how people choose in this category (size, colour, price, material, availability), an overview of applied filters, and a clear-all.
- Sorting that includes price and newness; sensible default order.
- Show stock and delivery signals truthfully ("ships Friday"), not fake scarcity.

## 4. Product pages

Above the fold on desktop, and in the first two screens on a phone:

- Large images: several angles, scale or in-use shots, zoom; do not rely on swipe alone in galleries (documented: Shopify product media guidance).
- Name, price, unit price where it applies, variants as buttons (not a dropdown) with unavailable ones marked, quantity, the buy button.
- Delivery cost and date, and the return policy, visible near the button. Extra costs discovered late are the top reason for abandonment.
- Then: a specific description (materials, dimensions, care, what is in the box), specifications in a table, real reviews with their distribution, related products that relate.
- On phones: a sticky buy bar once the main button scrolls away.

## 5. Cart and checkout

- Cart: editable quantities, a clear total including estimated delivery and tax as early as possible, accepted payment methods shown, the way back to shopping.
- **Guest checkout first and most prominent**; offer an account after the order.
- One column; labels above fields; correct input types and autofill; address lookup; mark optional and required; inline, specific errors that keep what was typed.
- Ask only for what the order needs. A phone number needs a reason.
- Show the order summary and total throughout; no surprises on the last step.
- Express payment (wallets) above the form on phones.
- A confirmation page that says what happens next and when.

## 6. Trust without tricks

- Real contact details, a real returns policy, security shown by behaviour (a known payment provider, HTTPS, no errors), real photographs.
- Reviews only when real and verified. Fake, bought or insider reviews and fake social proof are banned in the US (FTC rule 16 CFR 465, effective 21 Oct 2024, penalties up to 51,744 USD per violation) and the EU (UCPD Annex I, 23b and 23c).
- No fake urgency: false "limited time" claims are unlawful in the EU (UCPD Annex I, point 7). No pre-ticked paid extras (Consumer Rights Directive, article 22). No interface that deceives or manipulates (Digital Services Act, article 25).
- Cancelling a subscription should be as easy as starting it; several jurisdictions require it.

## 7. Identity for a store

The product is the hero and usually supplies the colour.

- Photography with a point of view (straight-on against a tile, a lived-in room, grainy film) is the strongest identity a store can have. Decide it in DESIGN.md.
- Type and ground chosen for the goods: a custom grotesque in light weights for hardware, a serif and olive ink for garden goods, one neutral grotesque and warm white for fashion.
- Restraint in chrome: no badges, ribbons or ratings unless they inform.
- A voice in product names and descriptions.
- A signature that belongs to the goods: pictogram navigation, catalogue numbers, a lookbook.

## 8. Platforms

- **Shopify**: Theme Store themes must average at least 60 for Lighthouse performance and 90 for accessibility across home, product and collection pages, use JSON templates with sections everywhere, and support app blocks (documented: shopify.dev, themes store requirements). The reference themes Dawn (HTML-first, JavaScript only as needed) and Horizon (theme blocks) are for study: their licences allow use only for Shopify themes, and Horizon derivatives may not be sold or distributed. Design in sections and blocks so merchants can rearrange; keep text and images editable.
- **WooCommerce block themes**: HTML block templates in the theme's templates folder, styling through theme.json per block rather than CSS on block class names; Cart and Checkout are blocks (documented: developer.woocommerce.com, block theme development). WordPress.org themes are GPL: study freely, but GPL code cannot go into a proprietary product.
- Never copy a theme's code, images or copy. Learn its structure and write your own.

## 9. Checklist

- The first screen shows what is sold; categories and search are visible.
- Product page: images, price, variants as buttons, delivery and returns near the buy button.
- Guest checkout first; 12 to 14 form elements or fewer; total visible throughout.
- No invented reviews, urgency or pre-ticked extras.
- Photography direction, type and ground decided in DESIGN.md; chrome kept quiet.
- Phone layout checked: sticky buy bar, 44px targets, wallets first.
