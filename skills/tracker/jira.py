#!/usr/bin/env python3
"""Jira Server / Data Center 8.x from the command line: REST API v2, Basic auth.

Commands: get, search, create, transition, comment, link (run with --help).
Credentials come from JIRA_URL, JIRA_USER and JIRA_PASSWORD and are never printed.
Project settings come from .lado/tracker.yaml, found from the current directory up to
the repository root. Python standard library only.
"""

import argparse
import base64
import json
import os
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

# Exit codes, one per kind of failure; SKILL.md tells the agent what to do on each.
OK = 0
USAGE = 2
CONFIG = 3
CREDENTIALS_UNSET = 4
CREDENTIALS_REFUSED = 5
NO_ACCESS = 6
NOT_FOUND = 7
FIELDS_REQUIRED = 8
UNREACHABLE = 9
TLS = 10
REFUSED = 11
SERVER_ERROR = 12

TIMEOUT = 30
CONFIG_PATH = os.path.join(".lado", "tracker.yaml")
CONFIG_MAPS = ("issue_types", "statuses", "fields")
CONFIG_LISTS = ("labels",)
CONFIG_KEYS = ("project",) + CONFIG_MAPS + CONFIG_LISTS
GET_FIELDS = ["summary", "status", "issuetype", "priority", "assignee", "reporter",
              "labels", "created", "updated", "parent", "description", "comment"]


class Failure(Exception):
    """One plain line for the user and the exit code of its kind."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


# --- .lado/tracker.yaml: a strict YAML subset ------------------------------------------


def _strip_comment(line):
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'" and line[:i].rstrip()[-1:] in (":", "[", ","):
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
    return line


def _scalar(text, where):
    text = text.strip()
    if text[:1] in "\"'":
        if len(text) < 2 or text[-1] != text[0]:
            raise ValueError(where + "a quoted value must end with the same quote")
        return text[1:-1]
    if text[:1] in "{&*!|>":
        raise ValueError(where + "write a plain value: flow maps, anchors, tags and block "
                                 "text are not supported")
    return text


def _value(text, where):
    text = text.strip()
    if text.startswith("["):
        if not text.endswith("]"):
            raise ValueError(where + "an inline list must end with ']'")
        inner = text[1:-1].strip()
        if not inner:
            return []
        items = [_scalar(item, where) for item in inner.split(",")]
        if any(not item for item in items):
            raise ValueError(where + "an empty item in the list")
        return items
    return _scalar(text, where)


def parse_config(text, path):
    """Parse the subset: `key: value`, one level of nested maps, `[a, b]`, `#` comments."""
    data = {}
    section = None
    indent = None
    for number, raw in enumerate(text.splitlines(), 1):
        where = "%s line %d: " % (path, number)
        if "\t" in raw[:len(raw) - len(raw.lstrip())]:
            raise ValueError(where + "indent with spaces, not tabs")
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        depth = len(line) - len(line.lstrip(" "))
        body = line.strip()
        if body.startswith("- "):
            raise ValueError(where + "block lists are not supported; write [a, b]")
        if body in ("---", "..."):
            raise ValueError(where + "one document only; remove '%s'" % body)
        key, colon, rest = body.partition(":")
        key = key.strip()
        if not colon or not key or (rest and not rest.startswith(" ")):
            raise ValueError(where + "expected 'key: value'")
        if depth == 0:
            if key in data:
                raise ValueError(where + "'%s' is given twice" % key)
            if rest.strip():
                data[key] = _value(rest, where)
                section = None
            else:
                data[key] = {}
                section, indent = key, None
            continue
        if section is None:
            raise ValueError(where + "unexpected indent")
        if indent is None:
            indent = depth
        if depth != indent:
            raise ValueError(where + "only one level of nesting; indent like the line above")
        if not rest.strip():
            raise ValueError(where + "'%s' needs a value (only one level of nesting)" % key)
        if key in data[section]:
            raise ValueError(where + "'%s' is given twice in '%s'" % (key, section))
        data[section][key] = _value(rest, where)
    return _validate(data, path)


def _validate(data, path):
    where = path + ": "
    for key in data:
        if key not in CONFIG_KEYS:
            raise ValueError(where + "unknown key '%s'; known keys: %s"
                             % (key, ", ".join(CONFIG_KEYS)))
    if not isinstance(data.get("project"), str) or not data.get("project"):
        raise ValueError(where + "'project' (the Jira project key) is required")
    for key in CONFIG_MAPS:
        value = data.setdefault(key, {})
        if not isinstance(value, dict):
            raise ValueError(where + "'%s' must be a map of 'name: value' lines" % key)
        for name, item in value.items():
            if not isinstance(item, str) or not item:
                raise ValueError(where + "'%s.%s' must be one plain value" % (key, name))
    for key in CONFIG_LISTS:
        value = data.setdefault(key, [])
        if isinstance(value, str):
            raise ValueError(where + "'%s' must be a list, e.g. [a, b]" % key)
        if isinstance(value, dict):
            raise ValueError(where + "'%s' must be a list, e.g. [a, b], not a map" % key)
    return data


def find_config(start):
    """Return the path of .lado/tracker.yaml from start up to the repository root."""
    here = os.path.abspath(start)
    while True:
        candidate = os.path.join(here, CONFIG_PATH)
        if os.path.isfile(candidate):
            return candidate
        if os.path.exists(os.path.join(here, ".git")):
            return None
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent


def load_config(required):
    path = find_config(os.getcwd())
    if path is None:
        if not required:
            return None
        raise Failure(CONFIG, "%s not found from %s up to the repository root: create it "
                              "with at least 'project: <KEY>'" % (CONFIG_PATH, os.getcwd()))
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        return parse_config(text, path)
    except (OSError, UnicodeDecodeError) as error:
        raise Failure(CONFIG, "%s cannot be read: %s" % (path, error))
    except ValueError as error:
        raise Failure(CONFIG, str(error))


def setting(config, section, name, why):
    value = (config or {}).get(section, {}).get(name)
    if not value:
        raise Failure(CONFIG, "%s needs '%s.%s' in %s" % (why, section, name, CONFIG_PATH))
    return value


# --- HTTP ------------------------------------------------------------------------------


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Jira:
    def __init__(self):
        missing = [name for name in ("JIRA_URL", "JIRA_USER", "JIRA_PASSWORD")
                   if not os.environ.get(name)]
        if missing:
            raise Failure(CREDENTIALS_UNSET, "%s not set: the user sets it in their login "
                                             "shell's profile, then starts a new session"
                          % ", ".join(missing))
        self.base = os.environ["JIRA_URL"].rstrip("/")
        login = "%s:%s" % (os.environ["JIRA_USER"], os.environ["JIRA_PASSWORD"])
        self.auth = "Basic " + base64.b64encode(login.encode("utf-8")).decode("ascii")
        cafile = os.environ.get("SSL_CERT_FILE") or None
        context = ssl.create_default_context(cafile=cafile)
        self.opener = urllib.request.build_opener(
            _NoRedirect, urllib.request.HTTPSHandler(context=context))

    def call(self, method, path, query=None, body=None, missing=None):
        url = self.base + "/rest/api/2/" + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Authorization", self.auth)
        request.add_header("Accept", "application/json")
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with self.opener.open(request, timeout=TIMEOUT) as response:
                raw = response.read()
        except urllib.error.HTTPError as error:
            raise self._http_failure(error, missing)
        except urllib.error.URLError as error:
            raise self._network_failure(error.reason)
        except (socket.timeout, TimeoutError, ConnectionError, ssl.SSLError) as error:
            raise self._network_failure(error)
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError:
            raise Failure(REFUSED, "Jira answered with something that is not JSON: is "
                                   "JIRA_URL the base address of Jira?")

    @staticmethod
    def _network_failure(reason):
        if isinstance(reason, ssl.SSLError):
            why = getattr(reason, "reason", None) or type(reason).__name__
            return Failure(TLS, "TLS failed (%s): if Jira's certificate is from a corporate "
                                "CA, set SSL_CERT_FILE to a file with that CA" % why)
        if isinstance(reason, (socket.timeout, TimeoutError)):
            return Failure(UNREACHABLE, "Jira did not answer in %d seconds: are you on the "
                                        "VPN or the company network?" % TIMEOUT)
        return Failure(UNREACHABLE, "Jira is not reachable (%s): are you on the VPN or the "
                                    "company network?" % type(reason).__name__)

    @staticmethod
    def _http_failure(error, missing):
        code = error.code
        denied = error.headers.get("X-Authentication-Denied-Reason")
        try:
            payload = json.loads(error.read().decode("utf-8"))
        except ValueError:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        messages = list(payload.get("errorMessages") or [])
        fields = payload.get("errors") or {}
        detail = "; ".join(messages + ["%s: %s" % item for item in sorted(fields.items())])
        if denied or (code == 403 and "captcha" in detail.lower()):
            return Failure(CREDENTIALS_REFUSED, "Jira refused the login and wants a CAPTCHA "
                                                "after failed logins: log in to Jira in a "
                                                "browser, then run again (not retried)")
        if code == 401:
            return Failure(CREDENTIALS_REFUSED, "Jira refused the credentials (401): check "
                                                "JIRA_USER and JIRA_PASSWORD; not retried, "
                                                "since more failed logins make Jira ask "
                                                "for a CAPTCHA")
        if code == 403:
            return Failure(NO_ACCESS, "no access (403)%s: ask the project's Jira admin for "
                                      "the permission" % (": " + detail if detail else ""))
        if code == 404:
            return Failure(NOT_FOUND, missing or "not found (404)%s"
                           % (": " + detail if detail else ""))
        if 300 <= code < 400:
            return Failure(REFUSED, "Jira answered with a redirect (%d), not followed: set "
                                    "JIRA_URL to Jira's base address" % code)
        if code >= 500:
            return Failure(SERVER_ERROR, "Jira failed (%d)%s: try later or tell the user"
                           % (code, ": " + detail if detail else ""))
        if fields:
            names = ", ".join("%s (%s)" % item for item in sorted(fields.items()))
            return Failure(FIELDS_REQUIRED, "Jira refused the fields: %s" % names)
        return Failure(REFUSED, "Jira refused the request (%d)%s"
                       % (code, ": " + detail if detail else ""))


# --- commands --------------------------------------------------------------------------


def read_text(value):
    text = sys.stdin.read() if value == "-" else value
    if not text.strip():
        raise Failure(USAGE, "the text is empty")
    return text


def mark(text):
    agent = os.environ.get("LADO_AGENT", "").strip()
    if not agent:
        return text
    return "[LADO: %s]\n\n%s" % (agent, text) if text else "[LADO: %s]" % agent


def parse_fields(pairs):
    fields = {}
    for pair in pairs or []:
        name, equals, value = pair.partition("=")
        if not equals or not name:
            raise Failure(USAGE, "--field takes id=value, got '%s'" % pair)
        if value[:1] in "{[":
            try:
                value = json.loads(value)
            except ValueError:
                raise Failure(USAGE, "--field %s: the value is not valid JSON" % name)
        fields[name] = value
    return fields


def missing_issue(key):
    return "task %s not found (404): check the key, or you may not see it" % key


def _name(value, attr="name"):
    if isinstance(value, dict):
        return value.get("displayName") or value.get(attr) or value.get("key") or "?"
    return value or "-"


def cmd_get(jira, args):
    config = load_config(required=False)
    names = list(GET_FIELDS)
    epic = (config or {}).get("fields", {}).get("epic_link")
    if epic:
        names.append(epic)
    issue = jira.call("GET", "issue/" + urllib.parse.quote(args.key),
                      {"fields": ",".join(names)}, missing=missing_issue(args.key))
    fields = issue.get("fields") or {}
    print("%s  %s" % (issue.get("key"), fields.get("summary")))
    print("Type: %s   Status: %s   Priority: %s" % (
        _name(fields.get("issuetype")), _name(fields.get("status")),
        _name(fields.get("priority"))))
    print("Assignee: %s   Reporter: %s" % (
        _name(fields.get("assignee")), _name(fields.get("reporter"))))
    if fields.get("labels"):
        print("Labels: " + ", ".join(fields["labels"]))
    if fields.get("parent"):
        print("Parent: " + fields["parent"].get("key", "?"))
    if epic and fields.get(epic):
        print("Epic: %s" % fields[epic])
    print("Created: %s   Updated: %s" % (fields.get("created"), fields.get("updated")))
    print("\nDescription:\n%s" % (fields.get("description") or "(empty)"))
    comments = (fields.get("comment") or {}).get("comments") or []
    shown = comments[-args.comments:] if args.comments > 0 else []
    print("\nComments: %d, the last %d shown" % (len(comments), len(shown)))
    for comment in shown:
        print("\n--- %s, %s\n%s" % (_name(comment.get("author")), comment.get("created"),
                                    comment.get("body")))
    return OK


def cmd_search(jira, args):
    jql = args.jql
    if "{project}" in jql:
        jql = jql.replace("{project}", load_config(required=True)["project"])
    result = jira.call("GET", "search", {
        "jql": jql, "startAt": args.start, "maxResults": args.max,
        "fields": "summary,status,issuetype,assignee"})
    issues = result.get("issues") or []
    total = result.get("total", len(issues))
    start = result.get("startAt", args.start)
    if not issues:
        print("No tasks (total %d)." % total)
        return OK
    print("Tasks %d-%d of %d" % (start + 1, start + len(issues), total))
    for issue in issues:
        fields = issue.get("fields") or {}
        print("%s  [%s]  %s  %s  (%s)" % (
            issue.get("key"), _name(fields.get("status")), _name(fields.get("issuetype")),
            fields.get("summary"), _name(fields.get("assignee"))))
    if start + len(issues) < total:
        print("More: run again with --start %d" % (start + len(issues)))
    return OK


def cmd_create(jira, args):
    config = load_config(required=True)
    project = config["project"]
    type_name = config["issue_types"].get(args.type, args.type)
    base = "issue/createmeta/%s/issuetypes" % urllib.parse.quote(project)
    missing_project = "project %s not found (404): check 'project' in %s" % (
        project, CONFIG_PATH)
    types = (jira.call("GET", base, {"maxResults": 200}, missing=missing_project)
             or {}).get("values") or []
    match = [t for t in types if t.get("name", "").lower() == type_name.lower()]
    if not match:
        raise Failure(REFUSED, "issue type '%s' is not in project %s; its types: %s"
                      % (type_name, project, ", ".join(t.get("name", "?") for t in types)))
    type_id = match[0]["id"]
    fields = {"project": {"key": project}, "issuetype": {"id": type_id},
              "summary": args.summary}
    if args.description is not None:
        fields["description"] = mark(read_text(args.description))
    elif os.environ.get("LADO_AGENT", "").strip():
        fields["description"] = mark("")
    if config["labels"]:
        fields["labels"] = list(config["labels"])
    if args.epic:
        fields[setting(config, "fields", "epic_link", "--epic")] = args.epic
    if args.epic_name:
        fields[setting(config, "fields", "epic_name", "--epic-name")] = args.epic_name
    fields.update(parse_fields(args.field))
    meta = (jira.call("GET", "%s/%s" % (base, type_id), {"maxResults": 500})
            or {}).get("values") or []
    lacking = ["%s (%s)" % (f.get("name"), f.get("fieldId")) for f in meta
               if f.get("required") and not f.get("hasDefaultValue")
               and f.get("fieldId") not in fields]
    if lacking:
        raise Failure(FIELDS_REQUIRED, "creating a %s in %s needs: %s; give each with "
                                       "--field id=value" % (type_name, project,
                                                             ", ".join(lacking)))
    created = jira.call("POST", "issue", body={"fields": fields})
    print("%s created" % created.get("key"))
    return OK


def _transitions(jira, key, transition_id=None):
    query = {"expand": "transitions.fields"}
    if transition_id:
        query["transitionId"] = transition_id
    result = jira.call("GET", "issue/%s/transitions" % urllib.parse.quote(key), query,
                       missing=missing_issue(key))
    return (result or {}).get("transitions") or []


def _describe(transition):
    return "%s: %s -> %s" % (transition.get("id"), transition.get("name"),
                             _name(transition.get("to")))


def cmd_transition(jira, args):
    if not args.target:
        transitions = _transitions(jira, args.key)
        if not transitions:
            print("%s: no transitions available to you" % args.key)
        for transition in transitions:
            print(_describe(transition))
        return OK
    config = load_config(required=False)
    status = (config or {}).get("statuses", {}).get(args.target, args.target)
    issue = jira.call("GET", "issue/" + urllib.parse.quote(args.key), {"fields": "status"},
                      missing=missing_issue(args.key))
    current = _name((issue.get("fields") or {}).get("status"))
    transitions = _transitions(jira, args.key)
    wanted = {args.target.lower(), status.lower()}
    match = [t for t in transitions if t.get("id") == args.target]
    match = match or [t for t in transitions if t.get("name", "").lower() in wanted]
    match = match or [t for t in transitions if _name(t.get("to")).lower() in wanted]
    if not match and current.lower() == status.lower():
        print("%s is already in %s" % (args.key, current))
        return OK
    available = "; ".join(_describe(t) for t in transitions) or "none"
    if len(match) != 1:
        problem = "is ambiguous" if match else "is not available from %s" % current
        raise Failure(REFUSED, "transition '%s' %s; available: %s"
                      % (args.target, problem, available))
    transition = match[0]
    fields = parse_fields(args.field)
    if args.resolution:
        fields["resolution"] = {"name": args.resolution}
    lacking = ["%s (%s)" % (spec.get("name", field_id), field_id)
               for field_id, spec in sorted((transition.get("fields") or {}).items())
               if spec.get("required") and not spec.get("hasDefaultValue")
               and field_id not in fields]
    if lacking:
        raise Failure(FIELDS_REQUIRED, "transition '%s' needs: %s; give them with "
                                       "--resolution or --field id=value"
                      % (transition.get("name"), ", ".join(lacking)))
    body = {"transition": {"id": transition["id"]}}
    if fields:
        body["fields"] = fields
    if args.comment is not None:
        body["update"] = {"comment": [{"add": {"body": mark(read_text(args.comment))}}]}
    jira.call("POST", "issue/%s/transitions" % urllib.parse.quote(args.key), body=body,
              missing=missing_issue(args.key))
    print("%s: %s -> %s" % (args.key, current, _name(transition.get("to"))))
    return OK


def cmd_comment(jira, args):
    body = {"body": mark(read_text(args.text))}
    result = jira.call("POST", "issue/%s/comment" % urllib.parse.quote(args.key),
                       body=body, missing=missing_issue(args.key))
    print("%s: comment %s added" % (args.key, (result or {}).get("id")))
    return OK


def cmd_link(jira, args):
    body = {"globalId": args.url, "object": {"url": args.url, "title": args.title or args.url}}
    jira.call("POST", "issue/%s/remotelink" % urllib.parse.quote(args.key), body=body,
              missing=missing_issue(args.key))
    print("%s: linked %s" % (args.key, args.url))
    return OK


# --- command line ----------------------------------------------------------------------


def parser():
    top = argparse.ArgumentParser(
        prog="jira.py", description="Jira Server / Data Center 8.x through REST API v2.")
    sub = top.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    p = sub.add_parser("get", help="read a task: fields, status, description, comments")
    p.add_argument("key")
    p.add_argument("--comments", type=int, default=5, help="last N comments (default 5)")
    p.set_defaults(run=cmd_get)

    p = sub.add_parser("search", help="find tasks by JQL; {project} is the project key")
    p.add_argument("jql")
    p.add_argument("--start", type=int, default=0, help="index of the first task")
    p.add_argument("--max", type=int, default=20, help="tasks per page (default 20)")
    p.set_defaults(run=cmd_search)

    p = sub.add_parser("create", help="create a task in the project")
    p.add_argument("--type", required=True, help="issue type, or a word of issue_types")
    p.add_argument("--summary", required=True)
    p.add_argument("--description", help="wiki markup; '-' reads it from stdin")
    p.add_argument("--epic", help="key of the epic (needs fields.epic_link)")
    p.add_argument("--epic-name", help="Epic Name, for an epic (needs fields.epic_name)")
    p.add_argument("--field", action="append", metavar="ID=VALUE",
                   help="another field; a value starting with { or [ is JSON")
    p.set_defaults(run=cmd_create)

    p = sub.add_parser("transition", help="list transitions, or move a task")
    p.add_argument("key")
    p.add_argument("target", nargs="?",
                   help="transition id or name, target status, or a word of statuses")
    p.add_argument("--resolution", help="resolution name, when the screen asks for it")
    p.add_argument("--comment", help="comment to add; '-' reads it from stdin")
    p.add_argument("--field", action="append", metavar="ID=VALUE",
                   help="a field the screen asks for; a value starting with { or [ is JSON")
    p.set_defaults(run=cmd_transition)

    p = sub.add_parser("comment", help="comment on a task")
    p.add_argument("key")
    p.add_argument("text", help="wiki markup; '-' reads it from stdin")
    p.set_defaults(run=cmd_comment)

    p = sub.add_parser("link", help="link a branch, commit or pull request URL to a task")
    p.add_argument("key")
    p.add_argument("url")
    p.add_argument("--title", help="link text (default: the URL)")
    p.set_defaults(run=cmd_link)
    return top


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        jira = Jira()
        return args.run(jira, args)
    except Failure as failure:
        print("jira.py: " + failure.message, file=sys.stderr)
        return failure.code


if __name__ == "__main__":
    sys.exit(main())
