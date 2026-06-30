# Deck Recipes — Starting Shapes by Deck Type

Reference for `slide-template-creator`. Treat as **inspiration**, not a fill-in-the-blank template. The right number of slides and right pattern mix depends on the source material.

> All recipes assume Step 0 (`inspect_template` + `find_layout_by_role`) has run, so `cover_layout` / `section_layout` / `content_layout` / `closing_layout` are in scope.

---

## Research-Report Deck

For industry analyses, study summaries, or long-form findings.

```
1. cover_layout
2. section_layout    — "Research Background"
3. content_layout    — Pattern 12 + Pattern 1 + Pattern 10 (source)
4. content_layout    — Pattern 3 + Pattern 10 (insight)
5. section_layout    — "Core Findings"
6. content_layout    — Pattern 4 (before / after)
7. content_layout    — Pattern 5 + Pattern 10
8. content_layout    — Pattern 8 (pull quote)
9. content_layout    — Pattern 9 + Pattern 10 (action)
10. closing_layout
```

## Product Pitch Deck

```
1. cover_layout
2. section_layout    — "Problem"
3. content_layout    — Pattern 1 (market size)
4. section_layout    — "Solution"
5. content_layout    — Pattern 6 (before / after UI)
6. content_layout    — Pattern 7 (3 capabilities)
7. section_layout    — "Why us"
8. content_layout    — Pattern 4 (vs competitors)
9. closing_layout
```

## Status Update Deck

```
1. cover_layout
2. content_layout    — Pattern 1 (this quarter's headline numbers)
3. content_layout    — Pattern 2 (project stage flow)
4. content_layout    — Pattern 3 (3 workstreams)
5. content_layout    — Pattern 9 (next quarter focus)
6. closing_layout
```

## Technical Deep-Dive

```
1. cover_layout
2. section_layout
3. content_layout    — Pattern 5 (architecture hub)
4. content_layout    — Pattern 4 (approach A vs B)
5. content_layout    — Pattern 11 (narrative + key metrics)
6. closing_layout
```

---

## When recipes don't fit

If the source material is unusual (one-off topic, no clear arc), don't force it into a recipe. Instead:

1. Read the source end to end.
2. Decide the **one** thing the reader should remember.
3. Build the deck *backwards* from that single takeaway: opening hook → 2–4 supporting evidence slides → that takeaway as the closing slide.
4. Pick patterns for each slide based on the structural intent of its content (see `visual-patterns.md`).
