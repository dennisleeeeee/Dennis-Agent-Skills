# GitHub MCP — Tool & Query Cheatsheet

Companion reference for the `github-repo-workflow` skill. Load when you need exact
search syntax, connector behaviour, or auth troubleshooting.

## Connector

| Property | Value |
|---|---|
| Endpoint | `https://api.githubcopilot.com/mcp/` |
| Transport | Streamable HTTP (JSON-RPC 2.0) |
| Auth | OAuth — user signs in once, Cowork reuses the grant |
| Scope | Everything the signed-in GitHub user can see; org SSO may need separate authorization |
| Source | https://github.com/github/github-mcp-server |

Tool availability varies by toolset configuration on the server. Always trust
`tools/list` over this document.

## Search qualifiers

Scope every search — unscoped queries return thousands of irrelevant hits.

| Qualifier | Example | Applies to |
|---|---|---|
| `repo:` | `repo:github/github-mcp-server` | code, issues, PRs |
| `org:` / `user:` | `org:microsoft` | code, repos, issues |
| `is:` | `is:open`, `is:closed`, `is:merged`, `is:draft` | issues, PRs |
| `label:` | `label:bug`, `label:"good first issue"` | issues, PRs |
| `author:` / `assignee:` | `author:dennisli` | issues, PRs |
| `review:` | `review:required`, `review:approved` | PRs |
| `path:` | `path:src/auth` | code |
| `language:` | `language:typescript` | code, repos |
| `in:` | `in:title`, `in:body` | issues, PRs |
| `created:` / `updated:` | `updated:>2026-06-01` | issues, PRs |

Sort/order params (`sort:updated`, `sort:comments`) reduce follow-up calls.

## Reading efficiently

- `search_code` returns fragments, not full files. Follow up with `get_file_contents`
  on the exact `path` (and `ref` when you need a specific branch/SHA).
- `pull_request_read` supports methods for details / diff / files / comments /
  reviews / status — request only the one you need.
- `list_commits` accepts `sha` (branch) and `path` to scope history to one file.
- For large files, prefer fetching a known path over searching repeatedly.

## Permalinks

Cite `https://github.com/<owner>/<repo>/blob/<commit-sha>/<path>#L10-L20`.
Branch-based links (`/blob/main/...`) rot as soon as the branch moves.

## Rate limits & timeouts

- Cowork tool calls must return in **< 30 s**; a broad `search_code` across a large org
  can exceed that — narrow the query instead of retrying.
- GitHub API secondary rate limits apply per user. On a 403 with a rate-limit message,
  stop and tell the user to retry later rather than looping.

## Auth troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 401 / "not authenticated" | Connector never authorized, or grant expired | Reconnect the GitHub connector in Cowork |
| 404 on a repo the user says exists | Private repo not covered by the grant, or org SSO not authorized | User authorizes the OAuth app for that org in GitHub → Settings → Applications |
| 403 on write | Token lacks write scope, or branch protection | Check repo permissions / open a PR instead of pushing |
| Tool missing from `tools/list` | Toolset disabled server-side | Use an alternative tool family; don't fabricate the call |

## Manifest note — authorization mode

The manifest omits `toolSource.remoteMcpServer.authorization`, which selects
**DynamicClientRegistration** (RFC 7591): Cowork registers its own OAuth client with
GitHub at connect time. If the tenant requires a pre-provisioned client instead, swap in:

```json
"authorization": {
  "type": "OAuthPluginVault",
  "referenceId": "<Enterprise Token Store reference id>"
}
```

`referenceId` is required for every type except `None`, and must be absent when the
type is `None`. Secrets never live in the manifest.
