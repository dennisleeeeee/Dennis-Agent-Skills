---
name: ms-learn-docs
description: |
  Ground every Microsoft / Azure / M365 answer in official Microsoft Learn
  documentation via the Microsoft Learn MCP Server (https://learn.microsoft.com/api/mcp).
  Runs the full docs workflow in one pass: SEARCH for breadth
  (microsoft_docs_search), FETCH for depth on a specific page
  (microsoft_docs_fetch), and CODE SAMPLE search for runnable snippets
  (microsoft_code_sample_search). Always cite the official Learn URL; never
  fabricate APIs, CLI flags, SDK names, portal steps, or version numbers.
  Use whenever the user asks a Microsoft/Azure/M365/.NET/Entra/Foundry/Fabric
  question, wants official docs, a how-to, a migration guide, or sample code,
  or says "check the docs", "official source", "MS Learn", "查官方文件",
  "有沒有官方範例", "根據文件".
  Do NOT use for non-Microsoft products or when the user explicitly wants a
  quick answer from memory without citations.
license: MIT
compatibility: Cowork (Frontier), Claude Code, VS Code / GitHub Copilot, Cursor, Foundry
metadata:
  author: Dennis Li
  version: 1.0.0
  category: research
  icon: BookOpen
---

# MS Learn Docs

Ground Microsoft/Azure/M365 answers in **official** Microsoft Learn content using the
Microsoft Learn MCP Server. Three tools, one workflow: **search → fetch → code sample**.
Breadth first, depth on demand, code when asked.

> Prerequisite: the Microsoft Learn MCP server must be connected (see
> `references/reference.md` for the endpoint + client config). If the tools aren't
> available, say so and fall back to a clearly-labelled "from memory, verify against
> Learn" answer — never pretend a citation exists.

## The three tools

| Tool | Use it for | Returns |
| --- | --- | --- |
| `microsoft_docs_search` | **Breadth.** First call, always. Find the right articles. | Up to 10 chunks (≤500 tokens each) with title + URL |
| `microsoft_docs_fetch` | **Depth.** Full article when you need step-by-step, prerequisites, full code, or the search chunk was truncated/incomplete. | Full page as markdown |
| `microsoft_code_sample_search` | **Code.** Runnable snippets and implementation examples. Optional `language` filter. | Up to 20 code samples |

## Workflow (one pass — don't over-iterate)

1. **Search first.** Call `microsoft_docs_search` with a specific, keyword-rich query
   (product + service + task). Read the top chunks and note the best 1–3 URLs.
2. **Decide if you need depth.**
   - Simple factual answer fully covered by a chunk → answer now, cite the URL. Stop.
   - Tutorial, prerequisites, multi-step config, or a truncated/partial chunk →
     `microsoft_docs_fetch` the single best URL for the complete content.
3. **Add code only when relevant.** If the task needs sample code, call
   `microsoft_code_sample_search` (pass `language` when known: csharp, python,
   typescript, javascript, powershell, azurecli, java, bicep-via-`al`/`sql` n/a, go,
   rust, etc.). Adapt the official snippet — keep it minimal and correct.
4. **Answer as quote + explain + cite.** For every point taken from Learn, present the
   verbatim **原文** (quote), a **解釋** (explanation), and the **來源** Learn URL — see
   *Output shape*. Never paraphrase without the paired quote and link.

Keep it tight: 1 search is usually enough. Fetch at most the 1–2 pages that matter.
Don't fan out into many searches for the same question.

## Query tips

- Be specific: `"Azure Functions Flex Consumption plan pricing"` beats `"functions pricing"`.
- Include the exact SDK/class/CLI when known: `az containerapp update`, `DefaultAzureCredential`, `Microsoft.Graph`.
- If the first search misses, refine with a different keyword angle **once**, not five times.
- For "latest / what's new" questions, prefer fetching the specific release-notes / what's-new page.

## Grounding rules (non-negotiable)

- **Cite the official Learn URL** for every non-trivial claim (APIs, CLI flags, portal
  steps, limits, prices measured in the doc's own units, version numbers).
- **Every referenced point ships as 原文 (verbatim quote) + 解釋 + 來源 link** — never a
  bare paraphrase without the exact quote and its URL.
- **Never fabricate** an endpoint, parameter, SDK name, or step. If the docs don't say
  it, say the docs don't say it. If you have no verbatim Learn text for a claim, say so
  rather than inventing a quote.
- Prefer the **most recent** and **most specific** article over a general overview.
- If two docs conflict, surface the conflict and cite both rather than guessing.
- Match the user's language (English or 繁體中文); quotes/identifiers stay verbatim.

## Output shape (mandatory: 原文 + 解釋 + 來源)

Whenever the answer draws on Microsoft Learn, present **every** point with all three
parts. Do not reply with only a paraphrase.

1. **原文 (Quote)** — the relevant sentence(s) copied **verbatim** from the Learn page,
   in a blockquote. Do not paraphrase inside the quote.
2. **解釋 (Explanation)** — interpret it in the user's language, in the context of their
   question.
3. **來源 (Source)** — the exact Learn article URL the quote came from.

Per-point layout:

> 原文：“<verbatim excerpt from Microsoft Learn>”
>
> — <article title>, <https://learn.microsoft.com/...>

**解釋**：<plain-language explanation in the user's language>

Multiple points → repeat the block per point; every quote stays paired with its own URL
(don't collapse several quotes under one link). You may add a one-line summary answer at
the top, but the quote+explain+source blocks are required below it.

For code: show the adapted snippet, note the language, quote any critical doc note
verbatim (原文), explain it (解釋), and link the sample's source page (來源).

## References

- `references/reference.md` — MCP endpoint, client config (VS Code / Copilot / Foundry),
  tool contracts, transport/auth details, and troubleshooting.
