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
  or newer (8.x before 8.4 lacks the create metadata R7 uses), not for one project.
  Nothing project- or company-specific (Jira address, project key, issue type or status
  names, custom field ids) is in the skill's text or the script.
  *Source:* the human, design round (Q6 follow-up: "we are building a universal kit, used
  for different projects, not only one"); brief, settled 6; the version floor from report
  `kit-reports/tracker-jira-server-0.1.1-2026-10-08.md` (37181e0), F5.2.
- **R2** The kit has no agents and no flows and no `supervisor:`; it provides exactly one
  skill, named `tracker`, so a process kit's roles say "use the tracker skill" and a role
  that cannot work without it lists `skills: [tracker]`. Jira Cloud is out of scope (a
  later `tracker-jira-cloud` kit). *Source:* brief, settled 1–2, 7; Out of scope.
- **R3** The skill does twelve actions and says in its own words how to do each: find tasks
  by JQL (`search`, paged by `startAt`/`maxResults`), read a task (`get`: fields, status,
  description, recent comments, each with its id, the id `comment` prints), create a task (`create`: issue type, summary,
  description, optionally an epic through the Epic Link field), change its status
  (`transition`: without a target it lists the available transitions; when the transition
  screen requires fields it names them, `--comment` counting for a required comment
  field; a `--comment` on a transition whose screen has no
  comment field, or that has no screen, is posted as a separate comment after it, since
  Jira silently drops it otherwise; on a task already in the target status it is posted
  as a comment, with no transition, while `--resolution` or `--field` there is refused
  (exit 11) rather than dropped), comment (`comment`), assign a task (`assign`: to
  `JIRA_USER`, to a login, or unassigned; already so is success; one line before -> after;
  a task held by another account is refused with that account named, unless
  `--reassign`, which the agent passes only when the human or its step says so),
  add or remove labels on a task (`label`: other labels untouched; already so is success;
  prints the task's labels; a label with a space is exit 2 before any request), say which
  account the skill works as (`whoami`: login and display name from `/rest/api/2/myself`,
  never the password; SKILL.md names it by meaning, "which account do you work as"),
  link a branch, commit or pull request URL
  (`link KEY <url> [--title]`, a remote link; with no URL, e.g. a repository without a
  remote, the branch and hash go in a `comment`), link a task to a task (`link KEY KEY2
  [--type <word>]`, a Jira issue link: the second argument `http(s)://…` is a URL, an
  issue key is a task, anything else, a task linked to itself, `--type` with a URL or
  `--title` with a key is exit 2 before any request; the words are tracker-yougile's,
  so process kits link on both trackers alike: `relates` (default), `blocks`,
  `duplicates`, `derived`, meaning "KEY <word> KEY2"; each maps to a link type name by a
  fixed table, Relates, Blocks, Duplicate, Relates, which `link_types` (R6) may replace,
  and the name is sent as it is: no list of the server's types, no matching, the script
  never guesses a type; `derived` therefore reads as "relates to" in Jira; a link of
  that type to KEY2 already there in that direction, or in either for a symmetric type,
  is success with nothing changed; links across projects are allowed; nothing is read
  back after the write), change a task's summary or description (`edit KEY
  [--summary '<text>'] [--description -] [--wiki]`: at least one of the two; the flags
  repeat `create`'s, the action's name `edit` is tracker-yougile's (LAD-12), so process
  kits call both trackers by the same action; a field already so is left untouched and,
  when nothing changes, that is said and is success, as in `assign` and `label`; the
  output is the task's new state, as `get` prints it). `get` shows a task's links as one line `Links: relates to ABC-2; blocks XYZ-9`.
  `get` and `search` show the assignee as `Display Name (login)`,
  comparable with `whoami`, and an unassigned task as `unassigned`.
  Files of a task (1.5.0): `get` shows them as a block between the description and the
  comments, `Files: N` and a line per file `<id> <name> (<size>, <author>, <date>)`, no
  block without files (`search` unchanged); `attach KEY FILE... [--comment -] [--wiki]`
  uploads each file in its own request, after checking all of them (exist, readable, not a
  folder: exit 2, nothing sent), prints `<id> <name> attachment:<URL-encoded name>` per
  file, and with `--comment` then adds a marked comment, printed last as `KEY: comment
  <id> added`, whose `attachment:` names are checked against the task's files and this
  call's before the first upload; a failure after some uploads names those uploaded and
  those not; `download KEY <name|id>... [--to DIR]` takes an id first, then a name (the
  newest file of that name), saves into a new `tempfile.mkdtemp(prefix="lado-jira-")`
  folder or an existing `--to` folder, cleans the name (base name only, no control
  characters, `.`/`..` replaced), never overwrites (`-1`, `-2`), prints each absolute
  path, and sends the credentials only to a `content` URL on `JIRA_URL`'s scheme, host and
  port (another is refused, exit 11), following no redirect; a name the task lacks is
  exit 7 with its files listed. The interface (names, arguments, output, `attachment:`)
  is tracker-yougile 0.4.0's (LAD-47). Nothing else (no delete, user search, deleting or
  renaming files, thumbnails, boards or sprints, no "list all statuses": a task moves only by the transitions open now, which
  `transition KEY` lists); more commands are added when a project needs them. SKILL.md's
  description and Actions table name every action, since a process kit decides from them
  whether to ask the human. *Source:* brief, settled 3; design round Q6 (the human: "decide
  as we work"; the brief's six are taken); `assign`, `label`, comment ids from the sdlc
  kit's requirements T1–T3, T5 (session artifact
  `tracker-jira-server-requirements-6a653014.md`, the human: "согласен"); `whoami`, the
  assignee's login and the refusal to take another's task from the sdlc kit's
  requirements 1–3 (session artifact `tracker-requirements-690cd7a8.md`; report
  `kit-reports/tracker-jira-server-1.1.0-2026-10-09.md` (full, b3e0aec), F5.2, F12.1,
  F5.4; the human at the triage of run `improve/tracker-jira-server-whoami`: "да");
  `edit` from the Yougile task LAD-13 and the human at the triage of run
  `improve/tracker-jira-server-1-3-0`: "всё как рекомендуешь"; task-to-task `link` from
  the Yougile task LAD-21 (session artifacts `link-concept`, `lad-21-jira-brief`,
  simplified by the human: "Реализуем самый простой механизм поддержки. При
  необходимости точечно потом подправим"); files of a task from the Yougile task LAD-46
  (grown from LAD-45; session artifact `lad-45-concept`, the human: «Согласен со всеми
  рекомендациями»; the interface check with LAD-47, session artifact
  `lad-46-interface-check`, the human's decisions of 2026-10-13).
- **R4** No MCP server. The skill reaches Jira with `skills/tracker/jira.py`, on Python's
  standard library only, run by `uv` (`uv run --script`, the script's inline metadata
  naming the Python it needs and no dependencies), so `uv` finds or installs that Python.
  `uv` is the one command the kit cannot work without: `kit.yaml` names it in
  `expects.commands` (with `dependencies.lado: ">=0.30"`), and the README requires it.
  *Source:* brief, settled 4; report b3e0aec, F10.1; the human at the triage of run
  `improve/tracker-jira-server-whoami`: "более надежным запускать скрипт с помощью uv и
  добавить uv в expects.commands".
- **R5** Credentials come from the agent's environment, `JIRA_URL`, `JIRA_USER`,
  `JIRA_PASSWORD` (Basic auth on each request; the password comes from the OS keychain in
  the user's shell profile). The kit never writes them to disk and never prints the
  password or `JIRA_URL`; the login of `JIRA_USER` appears only as an account Jira shows
  anyway: as an assignee (`assign`, `get`, `search`) and in `whoami`. `JIRA_URL` is
  `https://`, or `http://` to localhost for tests.
  Personal access tokens (8.14+, sent as `Bearer`) are not supported, and the README says
  so. *Source:* brief, settled 5; Jira 8.13 section (no personal access tokens before
  8.14); report 37181e0, F5.4; the login in `assign`'s output: trial artifact
  `trial-1.1.0`, the human at the 1.1.0 release gate ("логин вместо me"); `whoami` and
  localhost: report b3e0aec, F5.2, F5.5.
- **R6** A project's settings live in its repository, `.lado/tracker.yaml`, read only by
  the script, found from the current directory upward to the repository root. The script
  reads a strict YAML subset: `key: value` lines, one level of nested maps, inline
  `[a, b]` lists, `#` comments; anything else stops it with the path, the line and what is
  wrong (an unknown or misshaped top-level key names its line too). Only the project key
  is required; the other sections (issue type names, the mapping of process status words
  to the board's statuses, labels, custom field ids such as Epic Link, `link_types`:
  a link word to the server's link type name) are optional, and
  an action that needs a missing setting names it. The format is minimal and grows with
  real projects. The example in SKILL.md and README maps the status words process kits
  use (`in progress`, `review`, `done`). Issue type and status names are written as Jira shows them: on a
  localized Jira (e.g. Russian UI) they come translated, and the README says so.
  *Source:* brief, settled 6; design round Q3 (strict subset), Q2 (the first project's
  facts are gathered at its first use); report 37181e0, F5.5; the sdlc kit's
  requirement T4.
- **R7** The script follows Jira Server 8.4+: REST API v2 only (`/rest/api/2/...`, no v3,
  no ADF); users by `name`; search by `/rest/api/2/search`; create metadata by
  `/rest/api/2/issue/createmeta/{project}/issuetypes[/{id}]`; epics through the Epic Link
  custom field (an epic needs Epic Name; `parent` is for sub-tasks only); remote links by
  `/rest/api/2/issue/{key}/remotelink`; links between tasks by `POST
  /rest/api/2/issueLink` with the type by name, the direction of `inwardIssue` and
  `outwardIssue` as tried on the test Jira (R10); files by `fields.attachment` of the
  task, uploaded by `POST /rest/api/2/issue/{key}/attachments` (multipart, field `file`,
  header `X-Atlassian-Token: no-check`), downloaded from each file's `content` URL; TLS verified through the system store or
  `SSL_CERT_FILE`, never disabled. Text goes to Jira as wiki markup (R12).
  *Source:* brief, section "Jira Server / Data Center 8.13".
- **R8** Each failure is one plain line saying what happened and what to do, with an exit
  code per kind, and is never guessed over or retried: task not found (404), no access
  (403), a credential variable unset (named), credentials refused (401, or 403 with
  `X-Authentication-Denied-Reason`: never retried, the CAPTCHA case named — log in in a
  browser), Jira not reachable (connection error or timeout: "VPN?"), TLS failure
  (corporate CA hint, `SSL_CERT_FILE`, also when that file cannot be read), required fields on create or transition (named),
  `.lado/tracker.yaml` missing or invalid (path and what is wrong), rate limited (429:
  report it, not a request to fix). Files (1.5.0): a 413, attachments disabled (a 403
  saying so) or a file over Jira's size limit (Jira 8 answers it 404, the task having just
  been read) is exit 11 with the reason; another 403 exit 6; a local file that cannot be
  read or a `--to` folder missing or not writable exit 2; a file served from another
  address than `JIRA_URL` or answered with a redirect exit 11; a failure in the middle of
  `attach` or `download` names what was already done, and after no answer or a 5xx the
  file that may have been uploaded (check with `get` before attaching it again). For `assign` only, a 401 without
  `X-Authentication-Denied-Reason` is no permission (exit 6) and a 404 an unknown user
  (exit 11), as Atlassian's REST v2 documents for that resource, and "no such user" is
  said only for a login, never for unassigning (a 404 there is the task gone or not
  visible, exit 7); an unknown login is reported, never
  guessed, and the exit-code table of SKILL.md says so in the row of 11. For `link`
  between tasks, a 401 on the write without `X-Authentication-Denied-Reason` is no
  permission to link (exit 6, no stop for every agent), a 404 on it is a task missing or
  not visible (exit 7, both named), a link word not in the table or a type Jira refuses
  is exit 11 (the second naming `link_types`; Jira 8.13 refuses an unknown type with 404
  too, so after a 404 the script reads KEY2 once: KEY2 there is exit 11, KEY2 missing
  exit 7, any other failure of that read keeps its own code); SKILL.md's rows 6, 7 and 11 say so. SKILL.md tells the agent what to do on each exit code,
  with one rule after "report it": wait for the answer when the step cannot go on without
  the tracker, otherwise go on. After Jira did not answer (exit 9) the agent sends Jira
  nothing more until told it answers again; the script's message says so. After a crash
  (exit 1) or a 5xx (exit 12) on a write, Jira did answer, so the agent checks with `get`
  or `search` whether the write was applied before running it again. When a comment
  after a transition fails, the script's advice keeps the rule of the failure: after 9,
  check with `get` only once told Jira answers again; after a 5xx, check with `get`;
  after a refused comment (11), fix the text the line names and send it again; after any
  other failure (4, 5, 6, 7, 10, 429), report it and send the comment only when told to.
  A message not from the script is named in SKILL.md: a Python traceback is a crash
  (exit 1, a write may have been applied); a message from `uv` or Python before the
  script ran (it cannot open `jira.py`, uv cannot get Python or write its cache, uv's
  exit 2) means nothing reached Jira: fix the path, or report it as exit 1. A refused login
  or CAPTCHA (exit 5) says in the script's own message that every agent stops using Jira
  until the human fixes it, so a lead without the skill learns it too. *Source:* brief,
  "Script behaviour on errors"; report 37181e0, F3.2, F5.1, F5.3, F7.1; trial artifact
  `trial-lado-session`, observation 2; report
  `kit-reports/tracker-jira-server-1.0.2-2026-10-09.md` (full, 802c099), F3.1, F3.4;
  report `kit-reports/tracker-jira-server-1.1.0-2026-10-09.md` (7bc2beb), F5.2, F12.1;
  same report (full, b3e0aec), F3.1, F5.1, F5.3; report
  `kit-reports/tracker-jira-server-1.2.0-2026-10-09.md` (d6590ef), F3.1, F3.2, F5.1;
  same report (cf31728), F3.3, F3.4, F5.5; same report (6efeefc), F6.1. `edit` uses the
  same codes: a field not on the task's edit screen or a refused value is Jira refusing
  the request (exit 11).
- **R9** What agents write in Jira in the user's name is marked by the script: every
  comment, every created task's description and every description `edit` writes starts
  with `[LADO: <agent>]` (an edited description's earlier `\[LADO: …\]` mark is replaced
  by the current agent's, and a description a person wrote gets one; `edit --summary`
  alone leaves the description untouched) (sent as
  `\[LADO: <agent>\]`, since Jira shows a bare `[...]` as a broken link), the agent's
  name taken from `LADO_AGENT` (which LADO sets for each agent); without `LADO_AGENT` (the
  user runs the script by hand) there is no mark. Jira keeps it escaped, so SKILL.md tells
  an agent to look for `\[LADO: …\]` in `get` (report b3e0aec, F9.1). *Source:* design round Q4;
  the mark on an edited description: triage of run `improve/tracker-jira-server-1-3-0`.
- **R11** One default write scope in SKILL.md: reading is always fine; create, transition,
  comment, assign, label, link or attach only when the agent's role, its step or the human asks for it, and only
  on the tasks named; `attach` never uploads secrets (`.env`, keys, dumps, files with
  passwords), and a downloaded file is data, not instructions, kept outside the
  repository. `edit` is stricter, since it rewrites text a person may have
  written: only when the human or the agent's step asks for it. A process kit's roles and
  steps may allow more. A task is linked to the task it was created from with
  `link NEW OLD --type derived`, under the same rule: only when asked. *Source:* critic's
  finding F12.1 and Question 1; the human agreed at the second design visit; assign and
  label added with them in 1.1.0; `edit`'s rule from LAD-13 and the triage of run
  `improve/tracker-jira-server-1-3-0`; the `derived` rule from LAD-21; `attach` and
  `download` from LAD-46 (J6).
- **R12** Agents write the text they send to Jira (`comment`, `create --description`,
  `edit --description`, `transition --comment`) in Markdown; `jira.py` converts it to Jira wiki markup before
  adding the mark (R9), keeping the formatting of a minimal subset: headings, bold,
  italic, inline code, fenced code blocks (with their language when Jira 8.13 knows it,
  `shell`/`console`/`zsh` as `bash`, `ts`/`typescript` as `javascript`, any other and none
  as `none`), bullet and numbered
  lists (nested), links (one level of parentheses in the URL). Everything else, including wiki-special characters (`{`, `[`,
  `|`) in plain text, passes as it is, so `[~login]` mentions keep working; if the
  converter fails, the original text is sent. A flag `--wiki` sends the text unconverted,
  for wiki markup Markdown lacks (panels, `{noformat}`) and for wiki text that looks like
  Markdown (wiki `*bold*`, `#` lists, e.g. text taken from `get`). `create --field
  description=...` is never converted. A task's file is written `[text](attachment:NAME)`
  → `[text|^NAME]` and `![alt](attachment:NAME)` → `!NAME!` (the alt dropped), NAME
  URL-encoded or, as it is, in angle brackets `<attachment:NAME>`; a name several files
  share is the newest; in `edit`, `comment`, `transition --comment` and `attach
  --comment` an unknown name is exit 11 before anything is written, in `create` any such
  link is exit 2 (create, then attach, then edit); a name with `!`, `|` or `]`, which
  wiki markup cannot hold, is exit 11 before any request; `--wiki` text is neither converted nor
  checked (LAD-46, J4). `get` prints Jira's raw wiki markup, with no
  reverse conversion (the human kept this at the 1.1.0 triage: "нет, ничего не меняем"). SKILL.md says "write Markdown" and names
  `--wiki`, instead of teaching wiki markup; it also says that a description rewritten
  from the text `get` printed is written whole in wiki markup with `--wiki`, and a new
  one in Markdown (triage of run `improve/tracker-jira-server-1-3-0`). *Source:* the human, 2026-10-09 (session
  kit-tracker-jira-server, messages #1253, #1263; triage of run
  `improve/tracker-jira-server-markdown`: "согласен со всеми вопросами, кроме вопроса 2";
  minimal subset: "давай сделаем пока минимальный"; target Jira 8.13); report
  `kit-reports/tracker-jira-server-1.0.2-2026-10-09.md` (full, 802c099), F5.1, F5.2.
- **R10** Release: v0.1.x were tried on a test Jira Server 8.13.19 (the script, artifact
  `trial-test-server`; a live LADO session with a throwaway process kit, artifact
  `trial-lado-session`); these trials stand for the trial on the human's real Jira.
  v1.0.0 is released after the same sandbox trial is repeated on the built branch, before
  the human's release approval; the first real project is the first use after the
  release, not a condition of it (trial of 1.0.0: artifact `trial-1.0.0` of run
  `improve/tracker-jira-server`). The repository keeps its name `kit-tracker-jira-server`:
  kits of the ladohq organisation are named `kit-<name>` (the official marketplace's
  README, "Propose a kit", 4). *Source:* brief, settled 8; design round Q7; improve triage
  2026-10-08 (report 37181e0, F12.1; the human: "после обновления повторим эксперимент",
  "согласен со всеми пунктами"); F12.4 of that report withdrawn by the human ("Не
  переименовываем репозиторий").

Decided at the improve triage (2026-10-08): no limits for agents beyond R11 (deletes,
closing tasks, others' tasks), except taking another account's task in `assign` (R3,
1.2.0); the kit has no delete, and a process kit may set its own
(brief, settled 7; report 37181e0, F7.2, Question 2; report
`kit-reports/tracker-jira-server-1.2.0-2026-10-09.md` (d6590ef), F5.4, the human at the
release gate of run `improve/tracker-jira-server-whoami`).

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
| `kit.yaml` | manifest | R2, R4 | name, version, description; `expects.commands: [uv]` and `dependencies.lado: ">=0.30"`; no `supervisor:` (the kit never leads a session) and no `dependencies.skills` |
| `uv` | command (expects) | R4 | runs `jira.py` with the Python its metadata names on every project; a session whose agents lack it does not start, instead of failing at the first tracker action |
| `tracker` (`skills/tracker/SKILL.md`) | skill | R1, R2, R3, R6, R7, R8, R9, R11, R12 | the one skill the convention names; how to run each action, write Markdown (`--wiki` for raw wiki markup), where the settings are and their format with an example, what each exit code means and what to do; no project-specific values |
| `skills/tracker/jira.py` | skill script | R3, R4, R5, R6, R7, R8, R9, R12 | the only way to Jira without MCP; one file, standard library only; commands `get`, `search`, `create`, `edit`, `transition`, `comment`, `assign`, `label`, `link`, `attach`, `download`, `whoami`; inline script metadata for `uv`; reads env credentials and `.lado/tracker.yaml`; converts Markdown to wiki markup; adds the mark |
| `tests/test_jira.py` | tests (outside the skill) | R7, R8, R9, R10, R12 | the trials run on a test Jira, so the script's requests, the YAML subset, the mark and every error path are checked before it against a local fake Jira (standard library `unittest` and `http.server`); outside `skills/` so it does not ship into agents' skill folders |
| `README.md` | doc | R2, R4, R5, R6 | how to add the kit to a session, that `uv` is required, set the credentials and write a project's `.lado/tracker.yaml` |

Reverse check:
- R1: `tracker` skill, `jira.py` (no project values in either).
- R2: `kit.yaml`, `tracker` skill, `README.md`.
- R3: `tracker` skill, `jira.py`.
- R4: `jira.py`, `uv`, `kit.yaml`, `README.md`.
- R5: `jira.py`, `README.md`.
- R6: `tracker` skill, `jira.py`, `README.md`.
- R7: `tracker` skill, `jira.py`, `tests/test_jira.py`.
- R8: `tracker` skill, `jira.py`, `tests/test_jira.py`.
- R9: `tracker` skill, `jira.py`, `tests/test_jira.py`.
- R11: `tracker` skill.
- R12: `tracker` skill, `jira.py`, `tests/test_jira.py`.
- R10: `tests/test_jira.py`; the release and the sandbox trial before it are the run's
  steps, not a kit file. From 1.3.0, a release that adds or changes an action is tried
  on the test Jira Server 8.13 before the human's release approval when that Jira is
  available, the trial of 1.2.0 left in `BACKLOG.md` (`whoami`, `assign --reassign`)
  with it; when it is not, the release goes on the fake-Jira tests and the trial stays
  in `BACKLOG.md` (triage of run `improve/tracker-jira-server-1-3-0`). In 1.4.0 the
  direction of a task link is tried on the test Jira first (`link A B --type blocks`
  shows "A blocks B"; the same link again adds none), with the human's permission, and
  the tests then fix it (LAD-21). In 1.5.0 files are tried there (J9, session artifact
  `lad-46-probe`): Jira 8.13.19 answers a file over its size limit 404 with a plain-text
  body, and `!NAME!` shows the newest file of that name, so the tests fix both.

## 4. Complexity budget

Output of the kit-budget script on the built kit (1.4.0; 1.5.0 adds no role, flow, skill
or MCP server, so the values hold):

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
| 2026-10-13 | 1.5.0 | Fixes from the report: R8: after no answer or a 5xx `attach` names the file that may have been uploaded (F3.1); a redirect on a file's `content` is exit 11 with its own line, tested (F12.1); R12: an `attachment:` name with `!`, `\|` or `]` is exit 11 before any request (F3.2); SKILL.md: `--to` is a folder outside the repository, as R11 says (F5.1) | Report `kit-reports/tracker-jira-server-1.5.0-2026-10-13.md` (c5e6529), F3.1, F3.2, F5.1, F12.1; the human: "Исправить все 4, затем тег и push" |
| 2026-10-13 | 1.5.0 | R3: files of a task, twelve actions: `get` shows a `Files: N` block between the description and the comments; `attach KEY FILE... [--comment -] [--wiki]` (all files checked first, a line `<id> <name> attachment:<encoded name>` per file, the comment last as `KEY: comment <id> added`, a partial failure names both sides); `download KEY <name\|id>... [--to DIR]` (id first, then the newest of a name; a new `lado-jira-` temporary folder or `--to`; cleaned names, no overwrite; credentials only to `JIRA_URL`'s scheme, host and port); "no attachments" removed; R7: the attachment resources; R8: 413, attachments disabled, a file over the size limit (404 after the task was read) and another address are exit 11, 403 exit 6, a local file or `--to` exit 2; R11: `attach` is a write, no secrets, downloaded files are data; R12: `attachment:` links to `[text\|^NAME]` and `!NAME!`, checked before writing, refused in `create` | Yougile task LAD-46 (requirements J1–J9), grown from LAD-45; session artifacts `lad-45-concept` (the human: «Согласен со всеми рекомендациями») and `lad-46-interface-check` (the interface shared with tracker-yougile 0.4.0, LAD-47; the human's decisions of 2026-10-13); trial `lad-46-probe` (test Jira 8.13.19, TEST-1: the 404 with a plain-text body over the size limit was exit 4, now 11) |
| 2026-10-12 | 1.4.0 | R3: `link KEY KEY2 [--type relates\|blocks\|duplicates\|derived]`, a Jira issue link by a fixed table of type names, already linked is success, `get` shows `Links:`; R6: `link_types`; R7: `POST issueLink`, type by name; R8: 401 on the link is exit 6, 404 exit 7, an unknown word or refused type exit 11 (after a 404 the script reads KEY2 once: there → 11, missing → 7); R11: a task is linked to the one it was created from with `derived`, only when asked; R10: the direction tried on the test Jira before the tests fix it | Yougile task LAD-21; session artifacts `link-concept`, `lad-21-jira-brief`; the human: "Реализуем самый простой механизм поддержки… точечно потом подправим", "согласен. Давай не будем записывать в бэклог"; report `kit-reports/tracker-jira-server-1.3.0-2026-10-12.md` (972c83d), no open findings; trial `trial-1.4.0` (local Jira 8.13.19: an unknown link type answered 404); report `kit-reports/tracker-jira-server-1.4.0-2026-10-12.md` (14dd988), F3.1, F3.2, F5.1, and the human at the release gate: "исправить F3.1, F3.2; F5.1 - только по просьбе" |
| 2026-10-12 | 1.3.0 | R3: `edit KEY [--summary] [--description -] [--wiki]`, ten actions; R9: the mark on an edited description replaced or added; R11: `edit` only when the human or the step asks; R12: `edit --description` converted, text from `get` rewritten with `--wiki`; R8: `edit`'s refusals are exit 11; 404 after `assign … none` reported (F3.5); advice after a failed comment lists 4 (F6.1); R10: trial on the test Jira before the release approval when it is available | Yougile task LAD-13; report `kit-reports/tracker-jira-server-1.2.0-2026-10-09.md` (6efeefc), F3.5, F6.1; the human at the triage of run `improve/tracker-jira-server-1-3-0`: "всё как рекомендуешь" |
| 2026-10-09 | 1.2.0 | R4: `jira.py` run by `uv run --script`, `uv` in `expects.commands`, `dependencies.lado: ">=0.30"` (F10.1). R3: `whoami`; assignee as `Display Name (login)` or `unassigned` in `get`/`search` (F5.2); `assign` refuses a task held by another account unless `--reassign` (F12.1); pull request named in `link`, kit description "link a branch or commit to tasks" (F5.4). R5: the login also in `whoami` and assignees; `http://` to localhost (F5.5). R8: row 11 for `assign` (F5.1); "no such user" only for a login (F3.1); advice after a failed comment keeps the rules of 9 and 429 (F5.3). R9: look for `\[LADO: …\]` (F9.1). From the re-evaluations of the build: advice after a failed comment says report first after 4, 5, 6, 7, 10 and 429, and to fix a refused comment's text (d6590ef F5.1, cf31728 F3.4); a 404 on unassigning is the task gone or not visible, exit 7 (d6590ef F3.2, cf31728 F3.3); `assign` finds the holder by `name` or `key` (d6590ef F12.1); SKILL.md tells uv's and Python's messages from the script's, a traceback being a crash (d6590ef F3.1, cf31728 F5.5); SKILL.md names whose login is shown (d6590ef F5.2, F5.3); `.gitignore` for `__pycache__` | The sdlc kit's requirements for `tracker` (session artifact `tracker-requirements-690cd7a8.md`); report `kit-reports/tracker-jira-server-1.1.0-2026-10-09.md` (full, b3e0aec), F3.1, F5.1–F5.5, F9.1, F10.1, F12.1; the human at the triage: "F10.1 — запускать скрипт с помощью uv и добавить uv в expects.commands", "1. да 2. да 3. все четыре 4. minor"; reports `kit-reports/tracker-jira-server-1.2.0-2026-10-09.md` (d6590ef, cf31728) and the human at the release gate: "исправить F5.5, F3.3, F3.4" |
| 2026-10-09 | 1.1.0 | R3: `assign` and `label` actions, comment ids in `get`, description and Actions table name them; `--comment` counts for a required comment field (F3.2); `--resolution`/`--field` on a task already in the target status refused (F3.3). R6: status words `in progress`, `review`, `done` in the example. R8: after exit 1 or 5xx on a write, check with `get`/`search` before running it again (F3.1); unreadable `SSL_CERT_FILE` is exit 10 (F3.4). R12: `--wiki` also for wiki text that looks like Markdown (F5.1); parentheses in link URLs (F5.2). From the 1.1.0 evaluation (7bc2beb) and trial `trial-1.1.0`: an unknown login is reported, not guessed (F12.1); a refused unassign is named (F3.2); a comment after a transition failing with 9 or 5xx may have been added, check with `get` (F5.3); R8 names `assign`'s 401/404 (F5.2); R5: `assign` prints the login of `JIRA_USER`, not `me` | The sdlc kit's requirements T1–T5 (session artifact `tracker-jira-server-requirements-6a653014.md`); report `kit-reports/tracker-jira-server-1.0.2-2026-10-09.md` (full, 802c099), F3.1–F3.4, F5.1, F5.2; the human: "согласен", "Да, всё как рекомендуешь"; the release gate: "Оставить F12.1/F5.3/F3.2, сделать F5.2, логин вместо me" |
| 2026-10-09 | 1.0.2 | F5.1: code-block languages limited to Jira 8.13's list with synonyms, the rest and none → `{code:none}`; `transition --comment` posted separately when the transition has no comment field, and F5.6: also when the task is already in the target status (R3); the mark sent as `\[LADO: …\]` (R9); SKILL.md's false phrase "a code block … ends the list" removed | Trial artifact `trial-1.0.1` (test Jira Server 8.13.19, TEST-20), items 1–4; report `kit-reports/tracker-jira-server-1.0.1-2026-10-09.md` (a0b8837), F5.1; the human: "Да, improve → 1.0.2 с пунктами 1–4"; report `kit-reports/tracker-jira-server-1.0.2-2026-10-09.md` (f20af91), F5.6, and the release gate: "исправить F5.6 и сразу проверить" |
| 2026-10-09 | 1.0.1 | R12: Markdown in, converted to wiki markup by `jira.py` (minimal subset, raw fallback, `--wiki`); SKILL.md's wiki-markup section replaced; R7 no longer says "converts nothing". Fixed from report 1.0.1 (16909d7): F5.2 blank lines inside a list dropped, SKILL.md says a code block ends a numbered list; F5.3 wiki characters escaped inside `{{…}}`; F5.4 images `![alt](url)` pass as they are; F5.5 SKILL.md: one paragraph per line. F5.1 (code-block languages) waits for the test-Jira trial. Patch, not minor, by the human's decision: the kit is not yet published | The human's request, 2026-10-09 (messages #1253, #1263, #1279); report `kit-reports/tracker-jira-server-1.0.0-2026-10-08.md` (1240f8d), 0 findings; report `kit-reports/tracker-jira-server-1.0.1-2026-10-09.md` (16909d7) and the release gate: "давай починим F5.2 - F5.5, а потом займемся тестированием" |
| 2026-10-08 | 1.0.0 | Supported versions named as Jira 8.4 or newer | Report `kit-reports/tracker-jira-server-0.1.1-2026-10-08.md` (37181e0), F5.2 |
| 2026-10-08 | 1.0.0 | README: personal access tokens not supported; login check without typing the password | Same report, F5.4, F12.3 |
| 2026-10-08 | 1.0.0 | Exit 9: no more requests to Jira until it answers again (script message and SKILL.md); one rule after "report it" | Trial artifact `trial-lado-session`, observation 2 (2 x 30 s); same report, F5.3, F5.1 |
| 2026-10-08 | 1.0.0 | Exit 5 message asks the lead to stop every agent's use of Jira | Same report, F7.1 |
| 2026-10-08 | 1.0.0 | 429 reported as rate limiting, not a request to fix | Same report, F3.2 |
| 2026-10-08 | 1.0.0 | `--epic-name` hint only when `fields.epic_name` is set; `--epic-name` in the `create` row | Same report, F3.1, F9.1 |
| 2026-10-08 | 1.0.0 | `link` with no URL (no git remote): branch and hash in a comment | Trial artifact `trial-lado-session`, observation 1; same report, F3.3 |
| 2026-10-08 | 1.0.0 | Settings errors on top-level keys name their line | Same report, F5.5 |
| 2026-10-08 | 1.0.0 | R10: test-Jira trials stand for the real-Jira trial, sandbox trial repeated before release; no limits beyond R11 | Same report, F12.1, F7.2; the human at the triage |
| 2026-10-08 | 1.0.0 | Repository not renamed; README keeps `kit-tracker-jira-server` | Same report, F12.4, withdrawn: the official marketplace's README names ladohq kits `kit-<name>`; the human at the release step |
| 2026-10-08 | 1.0.0 | The first project's name and key removed from BLUEPRINT.md | Same report, F12.2 |
| 2026-10-08 | 0.1.1 | `create` of an epic without Epic Name points to `--epic-name` (and drops "a Epic") | Trial on a test Jira Server 8.13.19, user without admin rights (session kit-tracker-jira-server, artifact `trial-test-server`): the exit 8 line advised `--field id=value` |
| 2026-10-08 | 0.1.1 | `get` of a task without comments prints "Comments: none" | Same trial: "Comments: 0, the last 0 shown" |
| 2026-10-08 | 0.1.1 | README and SKILL.md: Jira may ask for a CAPTCHA after the first failed login, not only after a few | Same trial: one wrong password for a throwaway user gave 403 `X-Authentication-Denied-Reason: CAPTCHA_CHALLENGE`, then refusal even with the right password; the script's exit 5 held |
