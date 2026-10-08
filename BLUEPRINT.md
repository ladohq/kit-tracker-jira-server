# Blueprint: tracker-jira-server

A LADO kit that lets the roles of any process kit work with a Jira Server / Data Center
tracker, while LADO's core knows nothing about trackers. It has no agents and no flows:
it provides one skill, `tracker`, that a session adds next to a process kit
(`lado start <repo> --kit <process-kit> --kit tracker-jira-server`). The skill reaches Jira
through a script in its own folder; each project keeps its own settings in its repository.
The first Jira it serves is a corporate Jira Server 8.13; the first project to try it on is
Clens (Jira project CRM3), but the kit is for any project.

## 1. Requirements

- **R1** The kit is universal: it works for any project on Jira Server / Data Center 8.x,
  not for one project. Nothing project- or company-specific (Jira address, project key,
  issue type or status names, custom field ids) is in the skill's text or the script.
  *Source:* the human, design round (Q6 follow-up: "we are building a universal kit, used
  for different projects, not only Clens"); brief, settled 6.
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
  (`link`, a remote link). Nothing else in v0.1.0 (no delete, assign, user search,
  attachments, boards or sprints); more commands are added when a project needs them.
  *Source:* brief, settled 3; design round Q6 (the human: "decide as we work"; the brief's
  six are taken).
- **R4** No MCP server. The skill reaches Jira with `skills/tracker/jira.py`, on Python's
  standard library only. *Source:* brief, settled 4.
- **R5** Credentials come from the agent's environment, `JIRA_URL`, `JIRA_USER`,
  `JIRA_PASSWORD` (Basic auth on each request; the password comes from the OS keychain in
  the user's shell profile). The kit never writes them to disk and never prints them.
  *Source:* brief, settled 5; Jira 8.13 section (no personal access tokens before 8.14).
- **R6** A project's settings live in its repository, `.lado/tracker.yaml`, read only by
  the script, found from the current directory upward to the repository root. The script
  reads a strict YAML subset: `key: value` lines, one level of nested maps, inline
  `[a, b]` lists, `#` comments; anything else stops it with the path, the line and what is
  wrong. Only the project key is required; the other sections (issue type names, the
  mapping of process status words to the board's statuses, labels, custom field ids such
  as Epic Link) are optional, and an action that needs a missing setting names it. The
  format is minimal in v0.1.0 and grows with real projects. Issue type and status names
  are written as Jira shows them: on a localized Jira (e.g. Russian UI) they come
  translated, and the README says so. *Source:* brief, settled 6;
  design round Q3 (strict subset), Q2 (CRM3's facts deferred to the trial).
- **R7** The script follows Jira Server 8.x: REST API v2 only (`/rest/api/2/...`, no v3,
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
  `.lado/tracker.yaml` missing or invalid (path and what is wrong). SKILL.md tells the
  agent what to do on each exit code. *Source:* brief, "Script behaviour on errors".
- **R9** What agents write in Jira in the user's name is marked by the script: every
  comment and every created task's description starts with `[LADO: <agent>]`, the agent's
  name taken from `LADO_AGENT` (which LADO sets for each agent); without `LADO_AGENT` (the
  user runs the script by hand) there is no mark. *Source:* design round Q4.
- **R11** One default write scope in SKILL.md: reading is always fine; create, transition,
  comment or link only when the agent's role, its step or the human asks for it, and only
  on the tasks named. A process kit's roles and steps may allow more. *Source:* critic's
  finding F12.1 and Question 1; the human agreed at the second design visit.
- **R10** Release: `lado kits check . --tag v0.1.0`; then a trial on one test task in the
  real Jira (project CRM3), only with the human's yes; v1.0.0 and the official marketplace
  after the trial and its fixes, in an `improve` run. *Source:* brief, settled 8; design
  round Q7.

Open, decided at the trial (not in v0.1.0):
- Further limits for agents (deletes, closing tasks, others' tasks): none beyond R11 for
  now; the human decides at the trial (design round Q5: "not sure yet, decide as we
  work"). A process kit may set its own (brief, settled 7).
- CRM3's facts (issue types, statuses, Epic Link id, required fields, Jira Software) and
  the test task: gathered by the human before the trial (design round Q2).

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

Output of the kit-budget script on the built kit (0.1.0):

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
