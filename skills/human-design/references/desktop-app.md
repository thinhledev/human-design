# Desktop apps: macOS, Windows, Linux, Electron and Tauri

A desktop app is a tool people keep open for hours, drive with a keyboard and
arrange beside other windows. The common failure is "a web page in a window".
Guidelines checked 22 November 2026.

## 1. What makes it feel like a desktop app

- **Density**: more on screen than a web page. System text is 13pt on macOS and 14px on Windows, not 16px.
- **Keyboard first**: every command has a menu item and, when frequent, a shortcut; focus is visible; tab order follows the layout.
- **Windows that behave**: resizable with sensible minimums, remembered size and position, a different look when not focused, several windows when the task calls for it.
- **Direct manipulation**: selection (single, range, multiple), drag and drop, context menus, undo for everything.
- **State kept**: reopening restores where the user was.
- **Quiet chrome**: the content is the interface; toolbars and sidebars recede.

## 2. macOS 26

| Topic | Rule (documented, Apple HIG) |
| --- | --- |
| Controls | 28 by 28 pt default, 20 by 20 minimum |
| Text | 13 pt default, 10 pt minimum; no Dynamic Type. Styles: Large Title 26, Title 1 22, Title 2 17, Title 3 15, Headline 13 bold, Body 13, Callout 12, Subheadline 11, Footnote and Captions 10 |
| Window | a frame (controls and toolbar) and a body; main, key and inactive states look different; nothing critical at the window bottom |
| Sidebar | at most two levels; can be hidden; collapses as the window narrows; icons follow the user's accent colour |
| Toolbar | leading: back, sidebar toggle, title; centre: common controls, customisable; trailing: inspector toggle, search, one prominent action. No home-made overflow menu |
| Inspector | a trailing panel that follows the selection, opened from the toolbar |
| Menu bar | standard menus in standard order; disable unavailable items, never hide them; an ellipsis when more input is needed |
| Shortcuts | honour the standard ones; Command is the main modifier, Shift second, Option sparingly, avoid Control |
| Settings | in the app menu, Command-Comma, a toolbar of panes; no settings button in the main toolbar |
| Drag and drop | everywhere it makes sense, multi-item, undoable |

## 3. Windows 11 (Fluent 2)

| Topic | Rule (documented, Microsoft Learn, Windows app design) |
| --- | --- |
| Type ramp (size/line) | Caption 12/16, Body 14/20, Body Strong 14/20 semibold, Body Large 18/24, Subtitle 20/28, Title 28/36, Title Large 40/52, Display 68/92; Segoe UI Variable; sentence case; semibold for emphasis |
| Title bar | 32 px tall (48 with search or a person picture); empty space draggable; double-click maximises |
| Navigation | NavigationView: expanded left pane from 1008 px, icons only from 641 to 1007; top navigation for 5 to 10 equal categories |
| Materials | Mica: the opaque base layer, shown in the title bar, applied once. Acrylic: transient surfaces only (menus, flyouts); do not stack |
| Spacing | 8 between buttons, 12 control to label, 16 surface edge to text (effective pixels) |
| Targets | 40 by 40 px for touch |
| Keyboard | every control in the tab order, F6 between panes, access keys, shortcuts for frequent commands |

## 4. Linux (GNOME)

Header bars hold a few controls that change with the view and keep empty space
for dragging; layouts adapt down to narrow widths (documented:
developer.gnome.org/hig). Follow the desktop's light and dark preference and
its accent colour.

## 5. Electron and Tauri: removing the web tells

Sourced from an app developer's write-up (vendor: dev.to/vadimdemedes,
"Making Electron apps feel native on Mac") and the platform guidelines above;
no Tauri-specific source was verified, but the same points apply to any web
view.

| Tell | Fix |
| --- | --- |
| Hand cursor on every button | `cursor: default` on chrome and controls; pointer only for real links |
| Selectable text in toolbars, labels and buttons | `user-select: none` on chrome; keep content selectable |
| 16px web type and web line heights | system font at 13 to 14px with compact leading |
| No title-bar drag area, or controls that drag | `app-region: drag` on the title area, `no-drag` on its controls |
| No native menu; shortcuts missing or browser ones active | a standard application menu with roles; disable reload and zoom shortcuts in production |
| Window forgets its size and position | persist and restore them |
| White flash on launch and resize | set the window background colour; show the window when ready |
| Looks the same when unfocused | dim the selection and chrome on blur |
| Web scrollbars and rubber-band scrolling in fixed panes | native overlay scrollbars; no overscroll on chrome |
| Web focus rings on click | focus rings for keyboard focus only (`:focus-visible`), in the system accent colour |
| Page-style navigation with full reloads and spinners | keep panes mounted; update in place |
| Web context menu, or none | native context menus for the selection |
| Toasts for everything | system notifications for background events; inline status for foreground ones |
| One platform's look everywhere | traffic lights on the left on macOS, caption buttons on the right on Windows; platform-correct shortcuts (Command or Control) and wording |

## 6. Layout for tools

- Common shape: navigation (sidebar), content (list or canvas), detail (inspector). Each pane resizable, collapsible, with remembered widths.
- Density by default: 24 to 32px rows, 13px text, 4 to 8px gaps (`layout.md`). Expert users want more on screen with clear structure; offer a density setting if the audience is mixed.
- Tables: frozen headers, a human-readable first column, hover or zebra to hold place (research: nngroup.com/articles/data-tables/). Show data, remove ink that does not (Tufte's data-ink idea, as usually summarised).
- Status bars and inspectors for secondary information; no marketing-style empty space.
- A command palette for apps with many commands.

## 7. Identity in a desktop app

Restraint is the convention, so identity is concentrated: the icon, the
accent and how it is used, the typography of the content area (a writing app
can own its text face), one signature view or interaction, the empty states,
the about and onboarding moments. The chrome stays native.

## 8. Mockups

Draw at 1280 by 800 and 1440 by 900 with real window chrome for the target
platform, a realistic working state (real file names, long lists, a
selection, an open inspector), and both focused and unfocused windows. State
that an HTML mockup is a picture; hand off tokens and the platform notes.

## 9. Checklist

- Every command is in a menu; frequent ones have shortcuts; focus is visible.
- Window chrome, sidebar, toolbar and settings follow the platform.
- Selection, drag and drop, context menus and undo are designed.
- Density suits long use; nothing looks like a web page in a window (section 5).
- Inactive window, empty, loading and error states are drawn.
