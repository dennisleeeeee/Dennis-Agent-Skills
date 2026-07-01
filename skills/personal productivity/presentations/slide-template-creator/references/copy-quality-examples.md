# Copy Quality — Bad / Good Examples

Reference for `slide-template-creator`. Load this when writing slide copy.

> **The principle:** every text element should read like a finished document, not a note to self. If a reader can't tell *who*, *what*, or *so what* from a single glance, the text is too thin.

---

## 1. Slide titles = insight sentences

A title is the slide's headline. It should state the finding AND its implication.

❌ Topic labels:
- "M365 Copilot 介紹"
- "AI 的優點"
- "主要發現"
- "企業 AI 導入"

✅ Insight sentences:
- "49% 的 Copilot 對話處理決策與推理，已跨越執行層工作"
- "組織設計對 AI 成效的影響是個人心態的 2 倍"
- "只有 1/5 的員工身處真正準備好 AI 的組織"
- "Agent 數量年成長 15 倍，大型企業達 18 倍"

Formula: `<stat or finding> + <its implication>`, one declarative sentence.

---

## 2. Stat card `desc` = complete context clause

Answer: "X% of **whom**, doing **what**?"

❌ Category labels:
```python
{"num":"49", "unit":"%", "desc":"認知工作", "color":BLUE}
```

✅ Full clauses:
```python
{"num":"49", "unit":"%",
 "desc":"of M365 Copilot chats support analysis, reasoning & decisions",
 "color":BLUE}
{"num":"66", "unit":"%",
 "desc":"of AI users now spend more time on high-value work",
 "color":TEAL}
```

Keep to 1–2 lines but make it a grammatical clause.

---

## 3. Callout bars = takeaways, not just sources

Two distinct uses — they can both appear on the same slide:

❌ Source-only callout:
```python
draw_callout_bar(slide, "Source: Microsoft", style="source_bar")
```

✅ Takeaway + source pair:
```python
draw_callout_bar(slide,
    "31% of AI users are misaligned with their org — half sit in the emergent middle still forming.",
    style="solid_navy", y=5.8)
draw_callout_bar(slide,
    "Source: Microsoft 2026 Work Trend Index — 20,000 workers across 10 markets",
    style="source_bar", y=6.45)
```

- `solid_navy` → bold conclusion
- `source_bar` → citation
- `soft_bg` → softer insight

---

## 4. Card body text = full sentences or action phrases

❌ One-word labels:
```python
"ex": ["效率提升", "減少錯誤", "節省時間"]
```

✅ Specific action phrases:
```python
"ex": [
    "Turn raw meeting notes into a structured recap",
    "Run recurring reports from standard template inputs",
    "Compile source-grounded competitive research"
]
```

---

## 5. Section label `topic_text` = descriptive subtitle (≥ 5 words)

❌ One-word topic:
```python
draw_section_label(slide, "PART 1 · SETUP", "背景")
```

✅ Framing subtitle:
```python
draw_section_label(slide, "PART 1 · THE SETUP",
    "Four numbers that reframe what work is now for")
```

The `topic_text` answers "why does this section matter?" — not just what it's called.
