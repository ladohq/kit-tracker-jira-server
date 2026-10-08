# kit-tracker-jira-server

A LADO kit for Jira Server and Data Center 8.4 or newer. It gives the roles of any process kit a
skill named `tracker` that finds, reads, creates, moves and comments on tasks and links a
branch or commit to them, through Jira's REST API v2 and a script on Python's standard
library (no MCP server). Jira Cloud is not supported.

The kit has no agents and no flows: it adds the skill to a session led by a process kit.
A process kit's roles say "use the tracker skill"; a role that cannot work without it
lists `skills: [tracker]`, so a session without a tracker kit refuses to start. A lead
with its own `skills:` list adds `tracker` to it if it should read the tracker; the
script's credentials error (exit 5) says the lead tells every agent to stop using Jira.

## Install and start

```bash
lado kits add https://github.com/ladohq/kit-tracker-jira-server
lado start <repo> --kit <process-kit> --kit tracker-jira-server
```

The agents need `python3` (3.9 or newer) and a network path to Jira (VPN, if yours needs it).

## Credentials

The script logs in with Basic auth from three variables of the user's login shell, which
LADO's agents inherit. Personal access tokens (Jira 8.14 and newer) are not supported:
the script uses Basic auth with the user's own password, so keep it in the OS keychain,
not in the profile. On macOS:

```bash
# ~/.zprofile
export JIRA_URL=https://jira.example.com
export JIRA_USER=your.login
export JIRA_PASSWORD="$(security find-generic-password -s jira -a "$JIRA_USER" -w)"
```

LADO reads the profile through the login shell with a time limit, so a keychain prompt
stalls every agent's start: run the line once in a new terminal and allow `security` to
read the item ("Always Allow") before the first session.

Check the login once before a session, from the project's repository, without typing the
password: `python3 <kit>/skills/tracker/jira.py search 'project = ABC' --max 1`, where
`<kit>` is the kit's folder (`lado kits show tracker-jira-server` prints it).
A wrong password is never retried, since after failed logins (on some servers after the first) Jira
asks for a CAPTCHA and refuses REST logins until you log in in a browser. If Jira's certificate is from a corporate CA,
point `SSL_CERT_FILE` at a file with that CA; verification is never turned off. The script
refuses a `JIRA_URL` that is not `https://`, since the password goes with every request.

## Project settings: `.lado/tracker.yaml`

Each project commits its settings to its own repository, so every worktree has them. Only
`project` is required:

```yaml
project: ABC                  # the Jira project key
statuses:                     # a word of the process -> the board's status
  review: Code Review
```

Write issue type and status names as Jira shows them: on a localized Jira (a Russian UI,
for example) they come translated, so `review: Code Review` may need to be
`review: Ревью`. The skill's `transition` action without a
target lists a task's next statuses as Jira names them.

The other sections (issue types, labels, custom field ids such as Epic Link, which
`$JIRA_URL/rest/api/2/field` lists) and the format, a strict subset of YAML, are in
[`skills/tracker/SKILL.md`](skills/tracker/SKILL.md).

## What agents write

Every comment and every created task's description starts with `[LADO: <agent>]`, the
name of the agent that wrote it. Run by hand (no `LADO_AGENT` in the environment), the
script adds no mark. By default agents only read; they create, transition, comment or
link when their role, their step or the human asks (`skills/tracker/SKILL.md`). A process
kit says which roles touch the tracker and when, and may allow more.

## Development

```bash
python3 -m unittest discover -s tests     # the script against a fake Jira on localhost
lado kits check .
```

`BLUEPRINT.md` says why each part of the kit exists.
