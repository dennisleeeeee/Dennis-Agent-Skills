# Visual Pattern Library

Reference for `slide-template-creator`. Load this when you need to pick a pattern or remember its signature.

> **Mindset:** patterns are a *starter palette*, not a fixed menu. If your content's structural intent doesn't match any pattern below, compose primitives (`add_card`, `add_text_box`, `add_arrow`) directly — that's allowed and encouraged.

---

## How to choose

Match the **structural intent** of the content, not the topic:

| Content shape | Pattern |
|---|---|
| 2–4 headline numbers / KPIs | 1 — Stat Cards |
| 3–6 sequential states or a chain reaction | 2 — Flow Pipeline |
| 2–4 parallel concepts each with 3–5 bullets | 3 — Numbered Cards |
| Paradigm shift across multiple dimensions | 4 — Comparison Table |
| Central concept + 3–4 radiating questions | 5 — Hub & Spoke |
| Two contrasting formats / interfaces | 6 — Mock UI Side-by-Side |
| 2–4 icon-led categories | 7 — Icon Cards |
| Single pull-quote with attribution | 8 — Quote Slide |
| Behavior change (abandon → adopt) | 9 — Stop / Start |
| One-line takeaway or source line | 10 — Callout Bar |
| Narrative text + key metrics on same slide | 11 — Text + Visual Split |
| Section opener (part label + subtitle) | 12 — Section Label |

Mix & match: a single slide can carry section label + main pattern + callout bar, or none of the above — primitives (`add_card`, `add_text_box`, `add_arrow`, raw shapes) are first-class. Adjacent slides may repeat a pattern if the content calls for it; variety is a tiebreaker, not a constraint.

---

## Signatures

### Pattern 1 — `draw_stat_cards(slide, stats, y=1.55, h=1.7, gap=0.3)`
`stats = [{"num": "49", "unit": "%", "desc": "...", "color": BLUE}, ...]`

### Pattern 2 — `draw_flow_pipeline(slide, items, colors, y=4.05, h=0.75, gap=0.18)`
Final box can be `RED` for failure states.

### Pattern 3 — `draw_numbered_cards(slide, cards, y=1.55, h=4.2, gap=0.3)`
`cards = [{"num": "01", "title": "Expansion", "subtitle": "...", "bullets": [...], "color": BLUE}, ...]`

### Pattern 4 — `draw_comparison_table(slide, left_header, right_header, rows, ...)`
Left header gray (= before), right header blue (= after). Rows alternate soft-bg / white.

### Pattern 5 — `draw_hub_spoke(slide, hub_text, nodes, hub_color=NAVY, hub_size=1.8, cx=None, cy=3.95)`

### Pattern 6 — `draw_mock_ui_comparison(slide, left, right, y=1.55, h=4.5, gap=0.5)`
Each side: `{"header": "...", "type": "textwall"|"dashboard", "footer": "..."}`.

### Pattern 7 — `draw_icon_cards(slide, cards, y=1.55, h=4.2, gap=0.3)`
`cards = [{"icon": "💡", "tag": "...", "title": "...", "desc": "...", "ex": [...], "color": BLUE}, ...]`

### Pattern 8 — `draw_quote_slide(slide, quote, author, source)`
Empty the layout title first: `set_layout_title(slide, "")`.

### Pattern 9 — `draw_stop_start_rows(slide, items, y=1.6, row_h=1.35, gap=0.2)`
`items = [{"num": "01", "stop": "...", "start": "..."}, ...]`

### Pattern 10 — `draw_callout_bar(slide, text, y=6.45, h=0.7, style="solid_navy")`
Styles: `"solid_navy"` (bold takeaway), `"soft_bg"` (insight), `"source_bar"` (citation).
You may call it twice on the same slide — takeaway at `y=5.8`, source at `y=6.45`.

### Pattern 11 — `draw_text_visual_split(slide, text_blocks, visual_items, ...)`
```python
draw_text_visual_split(slide,
    text_blocks=[
        {"label": "CHALLENGE", "body": "Legacy processes...", "color": GRAY},
        {"label": "APPROACH",  "body": "AI-native design...", "color": BLUE},
        {"label": "OUTCOME",   "body": "+38% efficiency...",  "color": TEAL},
    ],
    visual_items=[
        {"num": "+38%", "unit": "",    "desc": "生產力提升",   "color": TEAL},
        {"num": "10K+", "unit": "hr",  "desc": "每年節省工時", "color": BLUE},
        {"num": "3×",   "unit": "",    "desc": "回應速度提升", "color": NAVY},
    ])
```

### Pattern 12 — `draw_section_label(slide, part_text, topic_text, x=0.8, y=1.1)`
Sits ABOVE the main pattern. Remember to push the main pattern's `y` down (e.g. `y=2.5`).
