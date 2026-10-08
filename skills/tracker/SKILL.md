---
name: tracker
description: >-
  The project's task tracker on Jira Server / Data Center: find tasks by JQL, read one,
  create one (also under an epic), change its status, comment, link a branch or commit.
  Use whenever your work touches a task in the tracker, e.g. "file a bug", "take the
  task", "move it to review", "close it", "tell the task what changed".
---

# Tracker: Jira Server / Data Center

You reach Jira only through the script in this skill's folder, from inside the project's
repository (it reads the project's settings there):

```bash
python3 ${SKILL_DIR}/jira.py <command> ...      # --help on any command
```

If your CLI does not expand `${SKILL_DIR}`, use the folder this SKILL.md is in. The
script logs in with the user's `JIRA_URL`, `JIRA_USER` and `JIRA_PASSWORD`; never ask
for them, print them or put them in a file. Whatever you write in Jira appears in the
user's name, so the script starts every comment and every new task's description with
`[LADO: <your agent name>]`; leave that mark to it.

## Actions

| To | Run |
|---|---|
| find tasks | `search '<JQL>' [--start N] [--max N]` |
| read a task | `get KEY-1 [--comments N]` |
| create a task | `create --type <type> --summary '<text>' [--description -] [--epic KEY-9] [--field id=value]` |
| see where a task can go | `transition KEY-1` |
| change its status | `transition KEY-1 '<status or transition>' [--resolution Fixed] [--comment -]` |
| comment | `comment KEY-1 -` (the text on stdin) |
| link a branch, commit or pull request | `link KEY-1 <url> [--title '<text>']` |

- **search**: `{project}` in the JQL is the project's key, e.g.
  `search 'project = {project} AND assignee = currentUser() AND resolution = Unresolved
  ORDER BY updated DESC'`. A full page ends with the `--start` of the next one.
- **create**: `--type` is an issue type of the project or a word of `issue_types` in the
  settings ("bug"). An epic also needs `--epic-name`. When the project requires more
  fields, the script names them (exit 8); give each with `--field id=value`, a value
  starting with `{` or `[` as JSON: `--field 'priority={"name": "High"}'`.
- **transition**: the target is a transition's name or id, a target status, or a word of
  `statuses` in the settings ("review"). With no target it lists the transitions open to
  you now; run that first when you are unsure. A screen that asks for fields is named
  (exit 8): add `--resolution`, `--field` or `--comment`.
- Text of more than one line goes on stdin with `-`:

  ```bash
  python3 ${SKILL_DIR}/jira.py comment KEY-1 - <<'EOF'
  *Done:* the login form checks the password length.
  EOF
  ```

## Writing in Jira: wiki markup, not Markdown

Jira Server shows descriptions and comments as wiki markup and the script sends your
text as it is:

| Want | Write |
|---|---|
| heading | `h2. Steps` at the start of a line |
| bold, italic, code | `*bold*`, `_italic_`, `{{code}}` |
| code block | `{code:python}` ... `{code}` on lines of their own |
| link | `[text\|https://...]` |
| bullet, numbered list | `* item`, `# item` (`**` nests) |
| mention a user | `[~login]` |

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
statuses:                     # a word of your process -> the board's status
  review: Code Review
  done: Done
labels: [lado]                # added to every task you create
fields:                       # custom field ids of this Jira (Jira's REST resource `field`)
  epic_link: customfield_10100
  epic_name: customfield_10101
```

Read it when you need the project's words; the user changes it, not you.

## When the script fails

It prints one line saying what happened and stops; it never retries. To **report** a
failure: as a worker, send the supervisor that line and the command with `send_message`
and wait for its answer; as the lead, tell the human. Act on the exit code:

| Exit | What happened | What you do |
|---|---|---|
| 1 | the script crashed | report its last line; repeat no write before you checked with `get` or `search` |
| 2 | wrong arguments, or empty text | fix the command (`--help`) |
| 3 | `.lado/tracker.yaml` missing, invalid, or lacks a setting | report it; the user fixes the file |
| 4 | a Jira variable is unset, or `JIRA_URL` is wrong (not `https://`, a redirect, not Jira's answer) | report it; the user fixes their shell profile and restarts the session |
| 5 | credentials refused, or Jira wants a CAPTCHA | stop using Jira and report it: one more try can lock the login. The lead tells every agent to stop using Jira until the human says it is fixed |
| 6 | no access to the task or project | report what you tried; look for no way around |
| 7 | task or project not found | check the key; report it if the key came from someone else |
| 8 | Jira needs fields (named) | give them and run again; if you cannot know the values, report it |
| 9 | Jira not reachable | report it (VPN or company network?). After a write, `get` or `search` before running it again: it may have been applied |
| 10 | TLS failed | report it: a corporate CA goes in a file named by `SSL_CERT_FILE` |
| 11 | Jira refused the request (bad JQL, a refused field value, unknown type, transition not open) | read the line, fix the request once; if it still fails, report it |
| 12 | Jira itself failed (5xx) | report it; whether your step can go on without the tracker is your step's decision |

Whatever the code, never guess the task's state from a failed run: say what failed.
