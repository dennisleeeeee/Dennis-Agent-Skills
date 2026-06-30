# Brand Reference — Extracted from `temp01.pptx`

> Read this **first** when starting any deck. These are the assets the master template owns. The agent's job is to fill them, not redraw them.

---

## Two-tier rule

| Tier | Slides | Source of truth | Agent's job |
|---|---|---|---|
| **Brand layer** | cover, section dividers, closing | The master layouts (logo, colour band, type) | Fill placeholders, do **not** draw on top |
| **Content layer** | everything else | Free composition with the pattern library + primitives | Compose what the content needs |

The brand layer is what makes the deck look "branded". Touching it (e.g. adding a custom text box on the cover, overriding the title font) is the fastest way to break visual identity.

---

## Pinned layout indices (verified in `temp01.pptx`)

| Role | Index | Layout name | Placeholders |
|---|---|---|---|
| `cover` | **2** | `Title Slide` | `idx=0` Title + `idx=12` Subtitle |
| `section` | **106** | `Section Title` | `idx=0` Title only |
| `closing` | **111** | `Closing logo slide` | None — pure decoration |
| `content` (default) | **18** | `Title Only` | `idx=0` Title |

Use `find_layout_by_role(prs, "cover" \| "section" \| "content" \| "closing")` — it resolves to these indices by name match, so the code stays stable if the template is updated.

### Other useful content layouts

- `[7]` End Slide Color Bkg, `[8]` End Slide Black Bkg — alternative closings
- `[102–105]` Section Divider 1–4 — colour variants of section dividers
- `[108]` Blank 12 Column, `[109]` Blank 12 Column Dark Bkg — grid-friendly content canvases

---

## Brand palette

Defined in `slide_helpers.py`. Use these constants; never hard-code hex.

| Name | Hex | When to use |
|---|---|---|
| `BLUE` | `#0078D4` | Primary accent, CTAs, positive stats |
| `NAVY` | `#243A5E` | Headers, anchor text |
| `CYAN` | `#50E6FF` | Highlights, secondary accent |
| `TEAL` | `#008575` | Secondary positive, flow steps |
| `DARKTEAL` | `#274B47` | Footer bars, dark surfaces |
| `GRAY` | `#737373` | Supporting copy, dividers |
| `LIGHT` | `#E6E6E6` | Card borders |
| `SOFT_BG` | `#F3F6FA` | Section backgrounds |
| `RED` | `#D83B01` | Warnings, deltas down |
| `WHITE` / `BLACK` | — | Surfaces / type |

---

## Typography

| Audience | Title | Body | Notes |
|---|---|---|---|
| English | `Segoe UI Semibold` | `Segoe UI` | Default — `set_layout_title()` forces this |
| 繁體中文 | `Microsoft JhengHei UI` | `Microsoft JhengHei` | Pass `lang="zh-tw"` to `add_cover_slide()` / `add_section_slide()`, or call `set_layout_title(slide, text, keep_master_font=True)` and set the font yourself |

`CN_TITLE_FONT` and `CN_BODY_FONT` constants live in `slide_helpers.py`.

**Never** override the cover / section / closing title fonts when generating a Chinese deck unless you set them to the CN equivalents explicitly. Leaving `Segoe UI Semibold` on Chinese text causes the OS to fall back to a generic UI font and the slide looks unstyled.

---

## What's protected

Do **not** modify on brand-layer slides:

- Logo position (top-right on cover, bottom-right on closing)
- Background colour bands or rules
- Title placeholder position / size
- The closing slide's decoration — it's designed to stand alone with no text

On content slides, you may draw freely as long as the brand palette is respected and the title placeholder is left in its default position.
