---
name: tracker
description: >-
  The project's task tracker on Jira Server / Data Center: find tasks by JQL, read one,
  create one (also under an epic), change its status, comment, assign it, add or remove
  labels, link a branch or commit, say which account you work as. Use whenever your work touches a task in the tracker,
  e.g. "file a bug", "take the task", "assign it to me", "move it to review", "mark it
  waiting for release", "close it", "tell the task what changed".
---

# Tracker: Jira Server / Data Center

You reach Jira only through the script in this skill's folder, from inside the project's
repository (it reads the project's settings there):

```bash
uv run --quiet --script ${SKILL_DIR}/jira.py <command> ...      # --help on any command
```

If your CLI does not expand `${SKILL_DIR}`, use the folder this SKILL.md is in. The
script logs in with the user's `JIRA_URL`, `JIRA_USER` and `JIRA_PASSWORD`; never ask
for them, print them or put them in a file. Whatever you write in Jira appears in the
user's name, so the script starts every comment and every new task's description with
`[LADO: <your agent name>]`; leave that mark to it.

Reading is always fine. Create, transition, comment, assign, label or link only when your role, your
step or the human asks for it, and only on the tasks named; your process kit's roles and
steps may allow more.

## Actions

| To | Run |
|---|---|
| find tasks | `search '<JQL>' [--start N] [--max N]` |
| read a task (each comment with its id) | `get KEY-1 [--comments N]` |
| create a task | `create --type <type> --summary '<text>' [--description -] [--wiki] [--epic KEY-9] [--epic-name '<name>'] [--field id=value]` |
| see where a task can go | `transition KEY-1` |
| change its status | `transition KEY-1 '<status or transition>' [--resolution Fixed] [--comment -] [--wiki]` |
| comment | `comment KEY-1 - [--wiki]` (the text on stdin) |
| assign a task | `assign KEY-1 <me \| login \| none> [--reassign]` (`none` unassigns) |
| add or remove labels | `label KEY-1 [--add L ...] [--remove L ...]` |
| link a branch, commit or pull request | `link KEY-1 <url> [--title '<text>']` |
| see which account you work as | `whoami` |

The `link` URL is the branch's or commit's page on the repository's host; a repository
with no remote has no such page, so give the branch and the commit hash in a `comment`.

- **search**: `{project}` in the JQL is the project's key, e.g.
  `search 'project = {project} AND assignee = currentUser() AND resolution = Unresolved
  ORDER BY updated DESC'`. A full page ends with the `--start` of the next one.
- **create**: `--type` is an issue type of the project or a word of `issue_types` in the
  settings ("bug"). An epic also needs its Epic Name: `--epic-name` when the settings
  name `fields.epic_name`, otherwise the `--field` the script names (exit 8). When the
  project requires more fields, the script names them (exit 8); give each with
  `--field id=value`, a value starting with `{` or `[` as JSON:
  `--field 'priority={"name": "High"}'`.
- **transition**: the target is a transition's name or id, a target status, or a word of
  `statuses` in the settings ("review"). With no target it lists the transitions open to
  you now; run that first when you are unsure. A screen that asks for fields is named
  (exit 8): add `--resolution`, `--field` or `--comment`.
- **comment**, **transition --comment**: print the new comment's id; `get` shows the
  same id on each comment, so look for it there to see that your comment is in. If
  `transition --comment` prints no id, find your `\[LADO: …\]` comment in `get`, as Jira keeps it escaped.
- **get**, **search**, **whoami** show an account as `Display Name (login)`, a task with
  no assignee as `unassigned`. To tell whether a task is yours, compare the login of its
  assignee with the one `whoami` prints.
- **assign**: use only a login you were given; on exit 11 report it and do not try
  another login, since a guess may assign the task to someone else. A task another
  account holds is refused (exit 11, the holder named) whatever the target: report it,
  and add `--reassign` only when the human or your step says to take it from them.
- **assign**, **label**: when the task is already so, they change nothing and say so;
  that is success. `label` leaves the task's other labels as they are and prints its
  labels; a label is one word, no spaces (`waiting_for_release`).
- Text of more than one line goes on stdin with `-`:

  ```bash
  uv run --quiet --script ${SKILL_DIR}/jira.py comment KEY-1 - <<'EOF'
  **Done:** the login form checks the password length.
  EOF
  ```

## Writing in Jira: Markdown

Write descriptions and comments in Markdown; the script converts it to Jira's wiki markup
and keeps headings, bold, italic, inline code, fenced code blocks (a language Jira lacks
becomes plain code), bullet and numbered lists (nested by indentation) and links
`[text](url)`. Mentions `[~login]` and a bare `KEY-1` pass as they are. Wiki markup that
looks like Markdown is converted wrongly (wiki `*bold*`, `#` lists, e.g. text taken from
`get`), and Markdown lacks panels and `{noformat}`: for such text, write the whole text in
wiki markup and add `--wiki`: it is sent unconverted.
Write each paragraph on one line: Jira shows every line break.
A description given as `--field description=...` is never converted. `get` shows the
text as Jira keeps it, in wiki markup.

## Project settings: `.lado/tracker.yaml`

The project's repository keeps its Jira settings in `.lado/tracker.yaml`; the script
finds it from the current directory up to the repository root. Only `project` is
required; an action that needs a missing setting names it (exit 3). The file is a strict
subset of YAML: `key: value` lines, one level of nesting, `[a, b]` lists, `#` comments.

```yaml
project: ABC                  # the Jira project key
issue_types:                  # a word of your process -> the project's issue type
  bug: Bug
  task: Task
statuses:                     # words process kits use -> the board's status
  in progress: In Progress
  review: Code Review
  done: Done
labels: [lado]                # added to every task you create
fields:                       # custom field ids of this Jira (Jira's REST resource `field`)
  epic_link: customfield_10100
  epic_name: customfield_10101
```

Read it when you need the project's words; the user changes it, not you.

## When the script fails

It prints one line saying what happened and stops; it never retries. A line that does
not start with `jira.py` or `usage: jira.py` comes from `uv`, which runs the script (it
could not find or install the Python the script needs): treat it as exit 1. To **report** a
failure: as a worker, send the supervisor that line and the command with `send_message`;
as the lead, tell the human. Then wait for the answer if your step cannot go on without
the tracker; otherwise go on with it. Act on the exit code:

| Exit | What happened | What you do |
|---|---|---|
| 1 | the script crashed | report its last line |
| 2 | wrong arguments, or empty text | fix the command (`--help`) |
| 3 | `.lado/tracker.yaml` missing, invalid, or lacks a setting | report it; the user fixes the file |
| 4 | a Jira variable is unset, or `JIRA_URL` is wrong (not `https://`, a redirect, not Jira's answer) | report it; the user fixes their shell profile and restarts the session |
| 5 | credentials refused, or Jira wants a CAPTCHA | stop using Jira and report it: Jira asks for a CAPTCHA after failed logins (on some servers after the first), so one more try can lock the login. As the line says, every agent stops using Jira until the human says it is fixed; the lead tells them |
| 6 | no access to the task or project | report what you tried; look for no way around |
| 7 | task or project not found | check the key; report it if the key came from someone else |
| 8 | Jira needs fields (named) | give them and run again; if you cannot know the values, report it |
| 9 | Jira not reachable or did not answer | report it (VPN or company network?) and send Jira nothing more until you are told it answers again |
| 10 | TLS failed | report it: a corporate CA goes in a file named by `SSL_CERT_FILE` |
| 11 | Jira refused the request (bad JQL, a refused field value, unknown type, transition not open), or `assign` refused a task another account holds | read the line, fix the request once; if it still fails, report it (`assign`: report it, never try another login or `--reassign` on your own) |
| 12 | Jira itself failed (5xx), or it is rate limiting requests (429) | report it |

A failed write may have been applied. After exit 9 on a write, once you are told Jira
answers again, `get` or `search` before running it again; after exit 1 or a 5xx exit 12
on a write, there is nothing to wait for: `get` or `search` before running it again. Whatever the code, never guess the task's state from a failed run: say what failed.
