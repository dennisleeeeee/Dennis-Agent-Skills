---
name: github-repo-workflow
description: Use when the user asks about anything living in GitHub — repositories, source files, code search, issues, pull requests, code review, commits, branches, releases, GitHub Actions runs, or security alerts. Trigger phrases include "look at this repo", "check the GitHub issue", "review this PR", "what changed in the last commits", "why did the build fail", "find where this function is defined", "summarize open issues", "create an issue for...", "list my notifications", "what's in the release notes", "看一下這個 repo", "幫我看這個 PR". Requires the github-mcp connector; all access is scoped to the signed-in user's GitHub OAuth permissions.
license: MIT
compatibility: Cowork (Frontier), Claude Code, VS Code Copilot
metadata:
  author: Dennis Li
  version: 1.0.0
  source: https://api.githubcopilot.com/mcp/
  category: Developer Tools
  connector: github-mcp
---

# GitHub Repo Workflow

Ground answers about code, issues, and pull requests in the **actual state of the
repository** by calling the `github-mcp` connector instead of recalling from training
data. Repos change constantly — never describe a file, issue, or PR you have not read.

## When to trigger

- Anything referencing a GitHub URL, `owner/repo`, an issue/PR number, or a commit SHA
- Code questions about a specific repository ("where is X implemented", "does this repo use Y")
- Development-status questions ("what's open", "who's reviewing", "is CI green")
- Write requests: open an issue, comment, create a branch, open a PR

Do **not** trigger for generic programming questions with no repository context, or for
GitLab / Azure DevOps / Bitbucket.

## Tool families on the connector

Tool names come from `tools/list` at runtime — discover before assuming. Expect these
families:

| Family | Typical use |
|---|---|
| Repos & files | `get_file_contents`, `list_branches`, `list_commits`, `get_commit`, `list_tags`, `list_releases` |
| Search | `search_code`, `search_repositories`, `search_issues`, `search_pull_requests`, `search_users` |
| Issues | `list_issues`, `issue_read`, `issue_write`, `add_issue_comment`, `sub_issue_write` |
| Pull requests | `list_pull_requests`, `pull_request_read`, `pull_request_review_write`, `add_comment_to_pending_review`, `merge_pull_request` |
| Writes | `create_branch`, `create_or_update_file`, `push_files`, `create_pull_request`, `create_repository` |
| Actions & security | workflow run listing/logs, `run_secret_scanning`, code-scanning and Dependabot alerts |
| Copilot agent | `assign_copilot_to_issue`, `create_pull_request_with_copilot`, `get_copilot_job_status` |

## Workflow

1. **Resolve the target.** Extract `owner` and `repo` from the URL or ask once if
   ambiguous. Never guess an org name.
2. **Read before writing.** For a PR: `pull_request_read` (details → files → comments)
   before commenting. For an issue: `issue_read` before replying.
3. **Search, then fetch.** Use `search_code` to locate a symbol, then
   `get_file_contents` on the specific path for real content. Don't paste whole files.
4. **Prefer narrow queries.** Scope searches with `repo:owner/name`, `is:open`,
   `path:`, `language:` qualifiers — unscoped searches return noise and burn tokens.
5. **Cite.** Link every claim to the GitHub URL (file permalink with line range, issue
   or PR number). Use `blob/<sha>/path#L10-L20` permalinks, not `blob/main/...`.

## Write-operation rules (important)

Writes are irreversible from the user's perspective. Before any tool that creates,
edits, merges, or closes:

- **State exactly what you are about to do** (target repo, branch, title, body) and
  **wait for explicit confirmation**.
- Never push directly to `main`/`master` — create a branch and open a PR.
- Never merge a PR, close an issue, or force-push without an explicit instruction
  naming that action.
- Never write secrets, tokens, or internal customer data into an issue, comment, or file.
- If a secret appears in tool output, redact it in your reply and warn the user.

Read-only calls (search, read, list) need no confirmation.

## Answer style

- Lead with the direct answer in 1–3 sentences, then a compact table or bullet list.
- PR/issue summaries: state status, author, age, blocking reviews, and CI result.
- CI failures: quote only the relevant log lines, then the likely cause.
- Match the user's language. Traditional Chinese with English technical terms is fine;
  never use Simplified Chinese.
- End with **Sources** listing the GitHub URLs used.

## Failure modes to avoid

- ❌ Describing code from memory instead of calling `get_file_contents`.
- ❌ Assuming a default branch is `main` — read it from the repo metadata.
- ❌ Dumping a 2,000-line file into the answer; fetch and quote the relevant range.
- ❌ Silently retrying a failed write. If auth fails, say the user needs to reconnect
  the GitHub connector, and stop.
- ❌ Treating a 404 as "does not exist" — for private repos it usually means the
  OAuth grant lacks access to that org.

## Example interactions

> **User**: 幫我看一下 github/github-mcp-server 最近有哪些 open issue 是 bug。
>
> **Action**: `search_issues("repo:github/github-mcp-server is:issue is:open label:bug")`
> → summarize top items in a table with number, title, age, assignee → Sources.

> **User**: Why did the CI fail on PR #142?
>
> **Action**: `pull_request_read(#142)` → find the failing check → fetch the workflow
> run logs → quote the failing step → propose a fix.

> **User**: Open an issue about the flaky auth test.
>
> **Action**: Draft title + body, show it to the user, **wait for confirmation**, then
> `issue_write` and return the new issue URL.

## References

- `references/tool-cheatsheet.md` — search qualifiers, connector limits, auth troubleshooting.
