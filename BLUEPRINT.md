# Blueprint: tracker-jira-server

A LADO kit that lets the roles of any process kit work with a Jira Server / Data Center
tracker, while LADO's core knows nothing about trackers. It has no agents and no flows:
it provides one skill, `tracker`, that a session adds next to a process kit
(`lado start <repo> --kit <process-kit> --kit tracker-jira-server`). The skill reaches Jira
through a script in its own folder; each project keeps its own settings in its repository.
The first Jira it serves is a corporate Jira Server 8.13 project, but the kit is for any
project.

## 1. Requirements

- **R1** The kit is universal: it works for any project on Jira Server / Data Center 8.4
  or newer (8.x before 8.4 lacks the create metadata R7 uses), not for one project. Nothing project- or company-specific (Jira address, project key,
  issue type or status names, custom field ids) is in the skill's text or the script.
  *Source:* the human, design round (Q6 follow-up: "we are building a universal kit, used
  for different projects, not only one"); brief, settled 6; the version floor from report
  `kit-reports/tracker-jira-server-0.1.1-2026-10-08.md` (37181e0), F5.2.
- **R2** The kit has no agents and no flows and no `supervisor:`; it provides exactly one
  skill, named `tracker`, so a process kit's roles say "use the tracker skill" and a role
  that cannot work without it lists `skills: [tracker]`. Jira Cloud is out of scope (a
  later `tracker-jira-cloud` kit). *Source:* brief, settled 1–2, 7; Out of scope.
- **R3** The skill does six actions and says in its own words how to do each: find tasks
  by JQL (`search`, paged by `startAt`/`maxResults`), read a task (`get`: fields, status,
  description, recent comments), create a task (`create`: issue type, summary,
  description, optionally an epic through the Epic Link field), change its status
  (`transition`: without a target it lists the available transitions; when the transition
  screen requires fields it names them), comment (`comment`), link a branch or commit URL
  (`link`, a remote link; with no URL, e.g. a repository without a remote, the branch and
  hash go in a `comment`). Nothing else (no delete, assign, user search,
  attachments, boards or sprints); more commands are added when a project needs them.
  *Source:* brief, settled 3; design round Q6 (the human: "decide as we work"; the brief's
  six are taken).
- **R4** No MCP server. The skill reaches Jira with `skills/tracker/jira.py`, on Python's
  standard library only. *Source:* brief, settled 4.
- **R5** Credentials come from the agent's environment, `JIRA_URL`, `JIRA_USER`,
  `JIRA_PASSWORD` (Basic auth on each request; the password comes from the OS keychain in
  the user's shell profile). The kit never writes them to disk and never prints them.
  Personal access tokens (8.14+, sent as `Bearer`) are not supported, and the README says
  so. *Source:* brief, settled 5; Jira 8.13 section (no personal access tokens before
  8.14); report 37181e0, F5.4.
- **R6** A project's settings live in its repository, `.lado/tracker.yaml`, read only by
  the script, found from the current directory upward to the repository root. The script
  reads a strict YAML subset: `key: value` lines, one level of nested maps, inline
  `[a, b]` lists, `#` comments; anything else stops it with the path, the line and what is
  wrong (an unknown or misshaped top-level key names its line too, F5.5). Only the project key is required; the other sections (issue type names, the
  mapping of process status words to the board's statuses, labels, custom field ids such
  as Epic Link) are optional, and an action that needs a missing setting names it. The
  format is minimal and grows with real projects. Issue type and status names
  are written as Jira shows them: on a localized Jira (e.g. Russian UI) they come
  translated, and the README says so. *Source:* brief, settled 6;
  design round Q3 (strict subset), Q2 (the first project's facts deferred to the trial).
- **R7** The script follows Jira Server 8.4+: REST API v2 only (`/rest/api/2/...`, no v3,
  no ADF); users by `name`; search by `/rest/api/2/search`; create metadata by
  `/rest/api/2/issue/createmeta/{project}/issuetypes[/{id}]`; epics through the Epic Link
  custom field (an epic needs Epic Name; `parent` is for sub-tasks only); remote links by
  `/rest/api/2/issue/{key}/remotelink`; TLS verified through the system store or
  `SSL_CERT_FILE`, never disabled. SKILL.md teaches Jira wiki markup (`h2.`, `*bold*`,
  `{code}`, `[text|url]`, lists, `[~username]`) briefly, its coverage checked against the
  structure of netresearch's `jira-syntax` skill (headings, code, tables, mentions,
  panels; no text copied, the skill is CC-BY-SA); the script converts nothing.
  *Source:* brief, section "Jira Server / Data Center 8.13".
- **R8** Each failure is one plain line saying what happened and what to do, with an exit
  code per kind, and is never guessed over or retried: task not found (404), no access
  (403), a credential variable unset (named), credentials refused (401, or 403 with
  `X-Authentication-Denied-Reason`: never retried, the CAPTCHA case named — log in in a
  browser), Jira not reachable (connection error or timeout: "VPN?"), TLS failure
  (corporate CA hint, `SSL_CERT_FILE`), required fields on create or transition (named),
  `.lado/tracker.yaml` missing or invalid (path and what is wrong), rate limited (429:
  report it, not a request to fix). SKILL.md tells the agent what to do on each exit code,
  with one rule after "report it": wait for the answer when the step cannot go on without
  the tracker, otherwise go on. After Jira did not answer (exit 9) the agent sends Jira
  nothing more until told it answers again; the script's message says so. A refused login
  or CAPTCHA (exit 5) says in the script's own message that every agent stops using Jira
  until the human fixes it, so a lead without the skill learns it too. *Source:* brief,
  "Script behaviour on errors"; report 37181e0, F3.2, F5.1, F5.3, F7.1; trial artifact
  `trial-lado-session`, observation 2.
- **R9** What agents write in Jira in the user's name is marked by the script: every
  comment and every created task's description starts with `[LADO: <agent>]`, the agent's
  name taken from `LADO_AGENT` (which LADO sets for each agent); without `LADO_AGENT` (the
  user runs the script by hand) there is no mark. *Source:* design round Q4.
- **R11** One default write scope in SKILL.md: reading is always fine; create, transition,
  comment or link only when the agent's role, its step or the human asks for it, and only
  on the tasks named. A process kit's roles and steps may allow more. *Source:* critic's
  finding F12.1 and Question 1; the human agreed at the second design visit.
- **R10** Release: v0.1.x were tried on a test Jira Server 8.13.19 (the script, artifact
  `trial-test-server`; a live LADO session with a throwaway process kit, artifact
  `trial-lado-session`); these trials stand for the trial on the human's real Jira.
  v1.0.0 is released after the same sandbox trial is repeated on the built branch, before
  the human's release approval; the first real project is the first use after the
  release, not a condition of it. The official marketplace takes the repository renamed
  to `lado-kit-tracker-jira-server` (`lado-kit-format`, "Publishing"); the rename is done
  at the release step with the human's yes. *Source:* brief, settled 8; design round Q7;
  improve triage 2026-10-08 (report 37181e0, F12.1, F12.4; the human: "после обновления
  повторим эксперимент", "согласен со всеми пунктами").

Decided at the improve triage (2026-10-08): no limits for agents beyond R11 (deletes,
closing tasks, others' tasks); the kit has no delete, and a process kit may set its own
(brief, settled 7; report 37181e0, F7.2, Question 2).

## 2. Starting point

No archetype: the kit has no roles and no flows, so none of the team shapes applies. It is
a skill pack, the shape the LADO plan for trackers (`docs/design/trackers.md` in the LADO
repository, "For kit authors") sets for every tracker kit: a kit without agents whose skill
`tracker` describes one tracker, with the project's specifics in `.lado/tracker.yaml`.

Alternatives researched before the second design approval (session artifact
`research-jira-8-13`), none taken: MCP servers (sooperset/mcp-atlassian needs 8.14+ and a
personal access token, which 8.13 lacks; those with password auth are archived or have no
community; and a kit without roles cannot give an MCP server to another kit's roles),
netresearch/jira-skill (about 10k lines on third-party packages, built for tokens, keeps
credentials in a file), and wrapping ankitpokhrel/jira-cli (each user installs a binary
and runs `jira init`; the mark and the error rules would not be ours). The human chose the
own standard-library script; the research only added the two notes in R6 and R7.

Flow skeletons: none; the kit has no flows (R2), so there are no diagrams.

## 3. Traceability

| Element | Kind | Covers | Why it exists / why nothing simpler |
|---|---|---|---|
| `kit.yaml` | manifest | R2 | name, version, description; no `supervisor:` (the kit never leads a session) and no `dependencies.skills` |
| `tracker` (`skills/tracker/SKILL.md`) | skill | R1, R2, R3, R6, R7, R8, R9, R11 | the one skill the convention names; how to run each action, Jira wiki markup, where the settings are and their format with an example, what each exit code means and what to do; no project-specific values |
| `skills/tracker/jira.py` | skill script | R3, R4, R5, R6, R7, R8, R9 | the only way to Jira without MCP; one file, standard library only; commands `get`, `search`, `create`, `transition`, `comment`, `link`; reads env credentials and `.lado/tracker.yaml`; adds the mark |
| `tests/test_jira.py` | tests (outside the skill) | R7, R8, R9, R10 | the trial touches the real Jira only with the human's yes, so the script's requests, the YAML subset, the mark and every error path are checked before it against a local fake Jira (standard library `unittest` and `http.server`); outside `skills/` so it does not ship into agents' skill folders |
| `README.md` | doc | R2, R5, R6 | how to add the kit to a session, set the credentials and write a project's `.lado/tracker.yaml` |

Reverse check:
- R1: `tracker` skill, `jira.py` (no project values in either).
- R2: `kit.yaml`, `tracker` skill, `README.md`.
- R3: `tracker` skill, `jira.py`.
- R4: `jira.py`.
- R5: `jira.py`, `README.md`.
- R6: `tracker` skill, `jira.py`, `README.md`.
- R7: `tracker` skill, `jira.py`, `tests/test_jira.py`.
- R8: `tracker` skill, `jira.py`, `tests/test_jira.py`.
- R9: `tracker` skill, `jira.py`, `tests/test_jira.py`.
- R11: `tracker` skill.
- R10: `tests/test_jira.py`; the release itself is the `create` run's step, not a kit file.

## 4. Complexity budget

Output of the kit-budget script on the built kit (1.0.0):

| Measure | Where | Value | Green / yellow up to | Zone |
|---|---|---|---|---|
| Worker roles (not supervisor) | kit | 0 | 3 / 5 | green |
| Work steps in a flow | no flows | 0 | 5 / 8 | green |
| Gates in a flow | no flows | 0 | 2 / 3 | green |
| Words in a role prompt | no roles | 0 | 800 / 1500 | green |
| Words in the lead's prompt | no lead role | 0 | 1000 / 1500 | green |
| Own skills | kit | 1 | 5 / 10 | green |
| MCP servers | kit | 0 | 2 / 4 | green |

Similar paragraphs (55% or more): none. Overall: green.

## 5. Change log

How the kit changed and the fact that caused it, newest first. Empty for a new kit.

| Date | Version | Change | ← Fact (session, run, metric or report) |
|---|---|---|---|
| 2026-10-08 | 1.0.0 | Supported versions named as Jira 8.4 or newer | Report `kit-reports/tracker-jira-server-0.1.1-2026-10-08.md` (37181e0), F5.2 |
| 2026-10-08 | 1.0.0 | README: personal access tokens not supported; login check without typing the password | Same report, F5.4, F12.3 |
| 2026-10-08 | 1.0.0 | Exit 9: no more requests to Jira until it answers again (script message and SKILL.md); one rule after "report it" | Trial artifact `trial-lado-session`, observation 2 (2 x 30 s); same report, F5.3, F5.1 |
| 2026-10-08 | 1.0.0 | Exit 5 message asks the lead to stop every agent's use of Jira | Same report, F7.1 |
| 2026-10-08 | 1.0.0 | 429 reported as rate limiting, not a request to fix | Same report, F3.2 |
| 2026-10-08 | 1.0.0 | `--epic-name` hint only when `fields.epic_name` is set; `--epic-name` in the `create` row | Same report, F3.1, F9.1 |
| 2026-10-08 | 1.0.0 | `link` with no URL (no git remote): branch and hash in a comment | Trial artifact `trial-lado-session`, observation 1; same report, F3.3 |
| 2026-10-08 | 1.0.0 | Settings errors on top-level keys name their line | Same report, F5.5 |
| 2026-10-08 | 1.0.0 | R10: test-Jira trials stand for the real-Jira trial, sandbox trial repeated before release; repository renamed; no limits beyond R11 | Same report, F12.1, F12.4, F7.2; the human at the triage |
| 2026-10-08 | 1.0.0 | The first project's name and key removed from BLUEPRINT.md | Same report, F12.2 |
| 2026-10-08 | 0.1.1 | `create` of an epic without Epic Name points to `--epic-name` (and drops "a Epic") | Trial on a test Jira Server 8.13.19, user without admin rights (session kit-tracker-jira-server, artifact `trial-test-server`): the exit 8 line advised `--field id=value` |
| 2026-10-08 | 0.1.1 | `get` of a task without comments prints "Comments: none" | Same trial: "Comments: 0, the last 0 shown" |
| 2026-10-08 | 0.1.1 | README and SKILL.md: Jira may ask for a CAPTCHA after the first failed login, not only after a few | Same trial: one wrong password for a throwaway user gave 403 `X-Authentication-Denied-Reason: CAPTCHA_CHALLENGE`, then refusal even with the right password; the script's exit 5 held |
