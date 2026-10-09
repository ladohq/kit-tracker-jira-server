# Backlog

- Report `kit-reports/tracker-jira-server-1.2.0-2026-10-09.md` (6efeefc), F3.5 [low]: row 7 of SKILL.md's exit-code table says "check the key" also after a 404 on `assign … none`, where the key was found a moment before; add "(after `assign … none`: report it)".
- Same report, F6.1 [low]: R8 in BLUEPRINT.md lists "5, 6, 7, 10, 429" for the advice after a failed comment; the 1.2.0 log row and the code include 4 too.
- Trial of 1.2.0 on the test Jira Server 8.13 not done before the release: `whoami` (`/rest/api/2/myself`), `assign` refusing another's task and `--reassign`, the script run by `uv` in a LADO session.
