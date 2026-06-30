# Common Pitfalls

Reference for `slide-template-creator`. Load when something visually wrong appears in the output.

| Pitfall | Fix |
|---|---|
| Card subtitle overlaps the title (e.g. "Boundary Collapse" wraps onto the subtitle line) | Use **one short English word** for `title` in numbered cards (≤ 12 chars). "Expansion" not "Task Expansion"; "Boundary" not "Boundary Collapse". |
| Quote slide leaves a visible empty title placeholder | Pass empty string: `set_layout_title(slide, "")`. |
| Mock UI panel looks empty | Always include exactly 3 mock stat cards in `dashboard` type. Bar-chart mock auto-renders. |
| Hub-and-spoke connectors poke through cards | Helper places arrows BEFORE cards in z-order so cards cover endpoints. Don't reorder. |
| Card title in `WHITE` renders as black | Title placeholder inherits master font color. Always re-apply font in helper functions (they do this automatically). |
| Flow-pipeline arrows have unwanted arrowheads | Pipeline arrows are single-direction. Don't add `headEnd` unless reversing. |
| Slide looks bare | Add `draw_callout_bar` at `y=6.45` (takeaway) or `y=5.5` (mid-slide source). |
| `inspect_template` returns the wrong role | Override manually: `content_layout = prs.slide_layouts[info["layouts"].index("Blank")]`. |
| Two adjacent slides feel monotonous | Prefer pattern variety, but it's a tiebreaker, not a rule. If the same pattern is genuinely the right carrier (e.g. three quarters of stat cards in a status update), keep it and let copy do the differentiating. |
| Title overflows one line | Shorten OR allow two lines, but never let it collide with the content region (y ≥ 1.5). |
| Cover slide ships with a placeholder line like "Speaker name or subtitle text" | You called `hide_body_phs(slide)` on the cover, or used `add_slide()` directly. Use `add_cover_slide(prs, title, subtitle, lang=...)` — it fills both placeholders and leaves master styling intact. |
| Chinese cover/section title renders in an unstyled fallback font | `set_layout_title()` forced `Segoe UI Semibold`, which has no CJK glyphs. Use `add_cover_slide(prs, title, subtitle, lang="zh-tw")` and on content slides call `set_layout_title(slide, text, keep_master_font=True)` then set `r.font.name = CN_TITLE_FONT` on each run. |
| Closing slide looks empty | That's correct — layout 111 has no text placeholders and the master decoration stands alone. Don't add a text box unless explicitly asked. |
| Decorations on cover (extra shapes, colour bars, logos) clash with the master | The cover layout owns the brand. Don't draw on it. If you need a custom cover, fork the layout — don't paint over it. |

## Common Slide Construction Errors

- ❌ Writing into native body placeholders for content slides (`placeholder.text = "..."`)
- ❌ Hardcoding layout names (`add_slide(prs, "Title Only")`) — use `find_layout_by_role(prs, "content")`
- ❌ Skipping `hide_body_phs(slide)` after `add_slide()` on content slides
- ❌ Calling `hide_body_phs(slide)` on a cover slide — kills the subtitle placeholder
- ❌ Building cover / section / closing with `add_slide` + manual drawing instead of `add_cover_slide` / `add_section_slide` / `add_closing_slide`
- ❌ Adding a "rebuild on template" step in the plan — single-pass only
- ❌ Setting `prs.slide_width` or `prs.slide_height`
- ❌ Inserting logos manually — the master already has them
- ❌ Hard-coding font names; use `CN_TITLE_FONT` / `CN_BODY_FONT` for Chinese decks
