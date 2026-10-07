# kit-tracker-jira-server

A LADO kit for Jira Server and Data Center: a skill named `tracker` that finds, reads,
creates, moves and comments on tasks through Jira's REST API v2, with a script on Python's
standard library (no MCP server). A kit without agents: combine it with a process kit
(`lado start <repo> --kit <process-kit> --kit tracker-jira-server`).

Work in progress. A project's settings for its tracker go in its `.lado/tracker.yaml`;
credentials come from the user's login shell (`JIRA_URL`, `JIRA_USER`, `JIRA_PASSWORD`).
