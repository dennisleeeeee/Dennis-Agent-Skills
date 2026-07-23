---
name: slide-template-creator
description: |
  Build a branded .pptx deck by (1) reading the brand palette/fonts from
  temp01.pptx, (2) generating the CONTENT slides with the general-purpose
  presentation skill (pptxgenjs) so the body looks its best, then (3) bolting
  the template's brand cover ("首頁") and closing ("thank you") slides onto the
  front and back via a python-pptx merge. Triggers on: 製作簡報, slide deck,
  presentation, .pptx, PowerPoint, deck generation, 投影片.
metadata:
  version: "2026-05-30-v5"
---

# slide-template-creator

You produce a polished deck whose **body** is built by the strongest available
slide engine, and whose **cover + closing** come straight from the corporate
template `temp01.pptx` (16:9, brand logos / colour bands baked into its
layouts).

This skill is a **bookend wrapper**: it does NOT hand-draw the content. It
reads the brand look, delegates the content to the content engine, then
re-attaches the template's first and last pages.

---

## The three steps

```
1. Read brand  →  2. Build content (pptxgenjs)  →  3. Bolt template bookends
```

### 1 — Read the brand brief

Read `references/brand.md` first. For this workflow you only need:

- **Palette** — `BLUE #0078D4`, `NAVY #243A5E`, `CYAN #50E6FF`, `TEAL #008575`,
  `RED #D83B01`, `SOFT_BG #F3F6FA`, … — feed these to the content engine so the
  body matches the cover/closing.
- **Fonts** — English: `Segoe UI` / `Segoe UI Semibold`; 繁中: `Microsoft
  JhengHei` / `Microsoft JhengHei UI`. For a Chinese deck, tell the content
  engine to use the JhengHei family.

You do **not** need the layout indices, patterns, or `slide_helpers` content
primitives here — those belong to the legacy self-draw mode (see bottom).

### 2 — Build the content with the content engine

Delegate the body to the general PowerPoint skill's **pptxgenjs** path:

- Read `~/.copilot/skills/pptx/pptxgenjs.md` and build there.
- **Canvas: 13.333 × 7.5 in** (pptxgenjs `LAYOUT_WIDE`) to match `temp01.pptx`.
  (A different size still works — the assembler uniformly rescales — but
  matching avoids any risk.)
- Apply the **brand palette + fonts** from step 1. Honour the copy guidance in
  `references/copy-quality-examples.md` (insight-sentence titles,
  evidence-bearing visuals, one takeaway per slide) and, if useful, the deck
  arcs in `references/deck-recipes.md`.
- **Always make the FIRST content slide an agenda / 大綱 slide** that lists the
  deck's sections (number + section title + one-line gist). It sits right after
  the template cover. Use the brand colours (e.g. NAVY background with CYAN
  numbers). This is fixed — every deck gets one.
- **Do NOT add a cover/title slide or a closing/thank-you slide** — those are
  the template's job. Produce only the content slides (agenda + body).
- **Do NOT add a footer bar or page numbers** on content slides. Leave the
  bottom margin clean so they can be added/adjusted by hand in PowerPoint.
- **Use one main title per slide — no English kicker / eyebrow label** above
  it. Just the big title (and the short CYAN accent rule). Skip the small
  all-caps line like `CONCEPTUAL ARCHITECTURE`.
- Save the content deck, e.g. `mydeck_content.pptx`.

### 3 — Bolt the template bookends

Run the assembler to prepend the brand cover (with your title/subtitle) and
append the brand closing:

```bash
python scripts/assemble_deck.py mydeck_content.pptx \
    --title "簡報標題" --subtitle "副標 — 2026" --lang zh-tw \
    --out mydeck_final.pptx
```

- `--lang zh-tw` makes the cover title/subtitle use the JhengHei fonts;
  `--lang en` keeps the master font.
- The assembler loads a clean `temp01.pptx`, adds the **native** cover and
  closing (so logos / colour bands are preserved), then imports every content
  slide with its images and relationships intact, uniformly scaling geometry
  and font sizes if the content canvas differs from the template.
- Default output is `<content>_final.pptx`; default template is `temp01.pptx`
  next to this skill.

---

## What you must NOT do

- Don't hand-redraw the cover or closing — using the template's own first/last
  pages is the whole point. The assembler fills the cover title/subtitle and
  stops.
- Don't let the content engine emit its own title/thank-you slide; that
  duplicates the bookends.
- Don't add a footer bar or page numbers to content slides — keep the bottom
  clean for manual editing.
- Don't add an English kicker / eyebrow label above slide titles — main title
  only.
- Don't override the cover/closing fonts to `Segoe UI` on a Chinese deck — pass
  `--lang zh-tw`.

---

## After saving, report

- Final file path and slide count (`= content slides + 2`).
- Language (`en` / `zh-tw`) and the title/subtitle used on the cover.
- That the content was built by the pptxgenjs engine and bookended by this skill.

---

## Files

- `temp01.pptx` — master template (brand cover / closing / theme).
- `scripts/assemble_deck.py` — the bookend merge (step 3): cross-deck slide
  import with relationship remap + uniform scaling.
- `slide_helpers.py` — provides `load_clean_template`, `find_layout_by_role`,
  `add_cover_slide`, `add_closing_slide` used by the assembler.
- `references/brand.md` — palette, fonts, layout map (read for the brief).
- `references/copy-quality-examples.md` — copy quality (engine-agnostic).
- `references/deck-recipes.md` — deck arcs for planning.

### Legacy self-draw mode (fallback only)

If no pptxgenjs/Node engine is available, you can still hand-compose content on
`temp01.pptx` with the original toolkit: `slide_helpers.py` primitives +
`references/visual-patterns.md` + `references/pitfalls.md`, validated by
`scripts/validate_deck.py` and `scripts/inspect_template.py`. This is the v4
behaviour; prefer the bookend workflow above whenever the content engine is
available.
