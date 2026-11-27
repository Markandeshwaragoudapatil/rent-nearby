# UI/UX design system

## Brand direction

Friendly, practical and trustworthy. The interface should feel like a curated local marketplace, not a classifieds board or a bank dashboard.

## Tokens

- Primary: deep forest `#145B46` (actions, navigation accents)
- Primary hover: `#104936`
- Accent: warm lime `#D7F36A` (small highlights only)
- Ink: `#18231F`
- Muted text: `#66736D`
- Surface: `#FFFFFF`
- Canvas: `#F6F7F3`
- Border: `#E5EAE4`
- Danger: `#B42318`; success: `#18794E`; warning: `#A15C07`

## Typography and layout

- Headings: Manrope; body: Inter/system sans.
- Content max width: 1200px; mobile gutters 20px, desktop 32px.
- 8px spacing rhythm; rounded cards 16–22px; pill controls only for compact filters/labels.
- Responsive breakpoints: 640px, 768px, 1024px, 1280px.

## Components

- Header: logo, browse, categories, how it works, list item, sign in and primary CTA.
- Search: keyword and locality fields; dates added in browse experience.
- Product card: image, category, title, locality, owner trust marker, daily price. Ratings only appear when real completed-rental reviews exist.
- Category tile: icon/illustration and short label.
- Trust indicator: explain the exact verification performed; never use a generic "verified" badge without a defined check.
- Forms: visible labels, inline errors, disabled/loading states and keyboard focus.
- Empty/error states: clear explanation and recovery action.

## Content rules

- Never show fabricated testimonials, ratings, owner names or live availability as real.
- Seed content in development must carry an explicit demo label.
- State currency as INR and distinguish rental fee, platform fee and refundable deposit.
- Do not publish exact private pickup addresses before booking acceptance.

## Accessibility

Target WCAG 2.2 AA. Use semantic landmarks, visible focus rings, sufficient contrast, descriptive image alt text, labels for all fields, reduced-motion support and keyboard-accessible dialogs/menus.
