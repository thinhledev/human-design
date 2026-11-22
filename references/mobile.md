# Mobile apps: iOS and Android

On phones, "human" mostly means "native": the app behaves the way the
platform taught its users to expect, and spends its originality on content,
type, colour and one signature, not on reinvented navigation. Guidelines
checked 22 November 2026; Apple links are under
developer.apple.com/design/human-interface-guidelines/, Android under
developer.android.com and the Material components documentation
(github.com/material-components/material-components-android, docs).

## 1. iOS 26 (Liquid Glass)

| Topic | Rule (documented, Apple HIG) |
| --- | --- |
| Hit targets | 44 by 44 pt; 28 by 28 pt absolute minimum |
| Text | default 17 pt, minimum 11 pt; avoid Ultralight, Thin and Light |
| Text styles at the default size (size/leading) | Large Title 34/41, Title 1 28/34, Title 2 22/28, Title 3 20/25, Headline 17/22 semibold, Body 17/22, Callout 16/21, Subhead 15/20, Footnote 13/18, Caption 1 12/16, Caption 2 11/13 |
| Dynamic Type | support it; layouts reflow at larger sizes (stack side-by-side views, let rows grow) |
| Contrast | at least 4.5:1; check light, dark, Increase Contrast and Reduce Transparency |
| Layout | respect safe areas; decide by size class, not device; extend backgrounds under bars; use scroll edge effects, not solid bars |
| Tab bar | navigation only, never actions; always visible except under modals; do not hide or disable tabs; avoid a More tab; one-word labels; filled symbols |
| Search | a search tab or a toolbar field; at the bottom when there is room |
| Sheets | medium and large detents, a grabber when resizable; no navigation stacks inside; full-screen modals for long flows |
| Liquid Glass | for the control and navigation layer only: "Don't use Liquid Glass in the content layer"; use sparingly on custom controls; the clear variant only over rich media with a dimming layer |
| Colour | semantic system colours, not hard-coded values; tint the backgrounds of primary actions, not symbols or text on glass; never colour alone |
| Dark mode | follow the system; no app-specific switch; soften white image backgrounds |
| SF Symbols | four rendering modes; never in app icons, logos or trademarks |
| Haptics | system patterns for their documented meanings only |
| Permissions | ask in context, not at launch unless essential; explain the benefit |
| Also avoid | custom window chrome, text "Back" or "Close" where standard symbols exist |

## 2. Android 16 (Material 3 Expressive)

| Topic | Rule (documented) |
| --- | --- |
| Touch targets | 48 by 48 dp |
| Type roles (sp) | Display 57, 45, 36; Headline 32, 28, 24; Title 22, 16, 14; Body 16, 14, 12; Label 14, 12, 11. Expressive adds an emphasized variant of each |
| Shape scale (dp) | 0, 4, 8, 12, 16, 20, 28, 32, 48 |
| Colour | roles from a tonal palette; surface-container tones replace elevation overlays; dynamic colour maps roles to the user's palette |
| Motion | spring-based scheme: spatial and effects springs in fast, default and slow; fast for small components, slow for full-screen |
| Navigation | navigation bar for 3 to 5 destinations on compact and medium widths; navigation rail on larger windows; the drawer is being deprecated in Expressive in favour of the expanded rail |
| Window size classes | compact under 600 dp, medium 600 to 839, expanded 840 to 1199, large 1200 to 1599, extra-large above; never "is tablet" logic |
| Large screens | from Android 16, orientation and resizability locks are ignored at 600 dp and wider: design for resizing |
| Edge to edge | mandatory when targeting API 36; draw behind system bars and inset content |
| Back | support predictive back; use back callbacks only for UI logic |

Use the app's own type and colour through the theme (a Material `ColorScheme`
and `Typography` built from the project's tokens), never by bypassing it with
literal values in composables.

## 3. Where a mobile app gets its identity

Not from custom navigation, hand-made glass or a gradient header. From:

- **Content and its presentation**: giant numerals for the one figure that matters, a real map, real artwork, real photographs.
- **Type**: a brand face for titles and key numbers with system text styles for the rest, or system type used with a strong, consistent hierarchy. Custom fonts must scale with Dynamic Type (`Font.custom(_:size:relativeTo:)`) and font scale.
- **Colour**: a restrained brand palette mapped to system roles, working in light and dark.
- **One signature**: a distinctive way of showing the core object (a boarding-pass card, a waveform, a dial), a characteristic transition, an icon style.
- **Icon and widgets**: often the most seen surfaces of the app.
- **Words**: the brand's voice in empty states, notifications and onboarding.

## 4. Every screen needs its states

Loading (placeholders, not a blank screen: "Show something as soon as
possible"), empty (keep the tab and explain why it is empty), error, partial,
offline, permission denied (the feature degrades; a way to grant access
later), and restored state on relaunch. Draw them with the screen.

## 5. Cross-platform apps

Flutter adapts navigation transitions, back gestures, scroll physics,
typography, haptics and text editing per platform; widgets that bypass these
feel foreign (documented: docs.flutter.dev/ui/adaptive-responsive/platform-adaptations).
The usual mistakes with any cross-platform kit:

- Material components and ripples on iOS; iOS-style sheets and switches on Android.
- No edge-swipe back on iOS; no predictive back on Android.
- Wrong scroll physics and overscroll.
- Ignoring Dynamic Type or font scale; fixed phone layouts on tablets and foldables.
- A hamburger drawer where the platform uses a tab bar or navigation bar.
- Web habits: hover-only affordances, tiny tap targets, toasts for errors that need action, text that cannot be selected where the platform allows it.

## 6. Tells in native code

`slop_check.py --surface mobile` reads Swift and Kotlin for: fixed font sizes
instead of text styles or theme roles, template colours left in (Purple80,
0xFF6200EE, purple-to-blue gradients), the same large corner radius and shadow
on every container, emoji as icons, and hidden system navigation. Evidence for
native tells is thin; these checks extend the web tells and the platform rules
above (inference).

## 7. Designing mobile screens as mockups

- Draw at 390 by 844 pt (iPhone) and 412 by 915 dp (Android) with the real status bar, home indicator and system bars; then check a small phone and a tablet or foldable width.
- Use the platform's real metrics for bars and lists; do not approximate system chrome with web-style boxes.
- Put the primary action within thumb reach; destructive actions away from it.
- Show the keyboard state for any screen with input.
- An HTML mockup of a native screen is a picture, not the implementation: say so, and hand off as SwiftUI or Compose guidance plus tokens (`tokens.py --swift`, `--kotlin`).

## 8. Checklist

- Navigation, back, sheets and search follow the platform.
- Text scales; targets are 44 pt or 48 dp; contrast holds in both modes.
- System materials and colours are used as the platform intends.
- The identity lives in content, type, colour and one signature.
- All states drawn; tablet or large-window layout considered.
