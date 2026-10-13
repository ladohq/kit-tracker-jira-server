#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Jira Server / Data Center 8.4 or newer from the command line: REST API v2, Basic auth.

Commands: get, search, create, edit, transition, comment, assign, label, link, attach,
download, whoami (run with --help). Credentials come from JIRA_URL, JIRA_USER and
JIRA_PASSWORD; the password and JIRA_URL are never printed, the login only as an account
Jira shows anyway: an assignee, or whoami's answer.
Text sent to Jira is Markdown, converted to Jira wiki markup (--wiki sends it as it is).
Project settings come from .lado/tracker.yaml, found from the current directory up to
the repository root. Python standard library only, run by `uv run --script`.
"""

import argparse
import base64
import http.client
import json
import os
import re
import socket
import ssl
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

# Exit codes, one per kind of failure; SKILL.md tells the agent what to do on each.
OK = 0
USAGE = 2
CONFIG = 3
SETUP = 4
CREDENTIALS_REFUSED = 5
NO_ACCESS = 6
NOT_FOUND = 7
FIELDS_REQUIRED = 8
UNREACHABLE = 9
TLS = 10
REFUSED = 11
SERVER_ERROR = 12

TIMEOUT = 30
LOOPBACK = ("127.0.0.1", "localhost", "::1")
APPLIED = ("; the change may have been applied: once Jira answers again, check with get "
           "or search before running it again")
# Jira answered a 5xx, so nobody will say it answers again: check before running it again.
APPLIED_ANSWERED = ("; the change may have been applied: check with get or search before "
                    "running it again")
STOP_ALL = ("; the lead tells every agent to stop using Jira until the human says it is "
            "fixed")
WAIT = "; send Jira nothing more until you are told it answers again"
NOT_JIRA = ("the answer is not Jira's: JIRA_URL is not Jira's base address (with its "
            "context path, if Jira has one)")
CONFIG_PATH = os.path.join(".lado", "tracker.yaml")
CONFIG_MAPS = ("issue_types", "statuses", "fields", "link_types")
CONFIG_LISTS = ("labels",)
CONFIG_KEYS = ("project",) + CONFIG_MAPS + CONFIG_LISTS
GET_FIELDS = ["summary", "status", "issuetype", "priority", "assignee", "reporter",
              "labels", "created", "updated", "parent", "description", "comment",
              "issuelinks", "attachment"]
# A link word, meaning "KEY <word> KEY2": the server's link type name (link_types may
# replace it) and how the script says it.
LINK_WORDS = {"relates": ("Relates", "relates to"), "blocks": ("Blocks", "blocks"),
              "duplicates": ("Duplicate", "duplicates"),
              "derived": ("Relates", "derived from")}
ISSUE_KEY = re.compile(r"^[A-Za-z][A-Za-z0-9_]*-\d+$")


class Failure(Exception):
    """One plain line for the user and the exit code of its kind."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = None  # the HTTP status of a refused request
        self.denied = False  # Jira's X-Authentication-Denied-Reason came with it


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
    lines = {}
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
            lines[key] = number
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
        lines[section + "." + key] = number
    return _validate(data, path, lines)


def _validate(data, path, lines):
    def where(key):
        return "%s line %d: " % (path, lines[key]) if key in lines else path + ": "
    for key in data:
        if key not in CONFIG_KEYS:
            raise ValueError(where(key) + "unknown key '%s'; known keys: %s"
                             % (key, ", ".join(CONFIG_KEYS)))
    if not isinstance(data.get("project"), str) or not data.get("project"):
        raise ValueError(where("project") + "'project' (the Jira project key) is required")
    for key in CONFIG_MAPS:
        value = data.setdefault(key, {})
        if not isinstance(value, dict):
            raise ValueError(where(key) + "'%s' must be a map of 'name: value' lines" % key)
        for name, item in value.items():
            if not isinstance(item, str) or not item:
                raise ValueError(where(key + "." + name) + "'%s.%s' must be one plain value"
                                 % (key, name))
    for key in CONFIG_LISTS:
        value = data.setdefault(key, [])
        if isinstance(value, str):
            raise ValueError(where(key) + "'%s' must be a list, e.g. [a, b]" % key)
        if isinstance(value, dict):
            raise ValueError(where(key) + "'%s' must be a list, e.g. [a, b], not a map"
                             % key)
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
            raise Failure(SETUP, "%s not set: the user sets it in their login shell's "
                                 "profile, then starts a new session" % ", ".join(missing))
        self.base = os.environ["JIRA_URL"].rstrip("/")
        try:
            url = urllib.parse.urlsplit(self.base)
            url.port  # raises ValueError on a malformed port
        except ValueError:
            url = None
        if not url or not url.hostname:
            raise Failure(SETUP, "JIRA_URL is not a valid address (host, port): it must be "
                                 "Jira's https:// base address")
        # The password goes in every request: only over TLS, or to this machine (tests).
        if not (url.scheme == "https" or (url.scheme == "http" and url.hostname in LOOPBACK)):
            raise Failure(SETUP, "JIRA_URL must be Jira's https:// base address: the "
                                 "password is sent with every request")
        login = "%s:%s" % (os.environ["JIRA_USER"], os.environ["JIRA_PASSWORD"])
        self.auth = "Basic " + base64.b64encode(login.encode("utf-8")).decode("ascii")
        cafile = os.environ.get("SSL_CERT_FILE") or None
        try:
            context = ssl.create_default_context(cafile=cafile)
        except (OSError, ssl.SSLError) as error:
            raise Failure(TLS, "SSL_CERT_FILE (%s) cannot be read: %s; the user points it "
                               "to a file with the corporate CA" % (cafile, error))
        self.opener = urllib.request.build_opener(
            _NoRedirect, urllib.request.HTTPSHandler(context=context))

    def call(self, method, path, query=None, body=None, missing=None, sent=(),
             upload=None):
        """`sent`: the fields the request sets, to tell refused values from missing ones;
        None for a request that takes no other fields, whose field errors are refusals.
        `upload`: (data, content type) of a multipart body, sent instead of JSON."""
        url = self.base + "/rest/api/2/" + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        headers = {"Accept": "application/json"}
        data = None
        if upload:
            data, headers["Content-Type"] = upload
            headers["X-Atlassian-Token"] = "no-check"  # else Jira refuses it as XSRF
        elif body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        raw = self.send(method, url, data, headers, missing, sent)
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError:
            raise Failure(SETUP, NOT_JIRA)

    def same_server(self, url):
        """Whether url is on JIRA_URL's scheme, host and port: only there go credentials."""
        ours, theirs = urllib.parse.urlsplit(self.base), urllib.parse.urlsplit(url)
        ports = {"http": 80, "https": 443}
        try:
            return (theirs.scheme == ours.scheme and theirs.hostname == ours.hostname
                    and (theirs.port or ports.get(theirs.scheme))
                    == (ours.port or ports.get(ours.scheme)))
        except ValueError:
            return False

    def send(self, method, url, data=None, headers=None, missing=None, sent=()):
        """The body of the answer, as bytes."""
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Authorization", self.auth)
        for name, value in (headers or {}).items():
            request.add_header(name, value)
        try:
            with self.opener.open(request, timeout=TIMEOUT) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            failure = self._http_failure(error, method, missing, sent)
            failure.status = error.code
            failure.denied = bool(error.headers.get("X-Authentication-Denied-Reason"))
            raise failure
        except urllib.error.URLError as error:
            raise self._network_failure(error.reason, method)
        except (socket.timeout, TimeoutError, ConnectionError, ssl.SSLError,
                http.client.HTTPException) as error:
            raise self._network_failure(error, method)

    @staticmethod
    def _network_failure(reason, method):
        if isinstance(reason, ssl.SSLError):
            why = getattr(reason, "reason", None) or type(reason).__name__
            return Failure(TLS, "TLS failed (%s): if Jira's certificate is from a corporate "
                                "CA, set SSL_CERT_FILE to a file with that CA" % why)
        # A write that got no answer may still have been applied.
        after = WAIT + (APPLIED if method != "GET" else "")
        if isinstance(reason, (socket.timeout, TimeoutError)):
            return Failure(UNREACHABLE, "Jira did not answer in %d seconds: are you on the "
                                        "VPN or the company network?%s" % (TIMEOUT, after))
        return Failure(UNREACHABLE, "Jira is not reachable (%s): are you on the VPN or the "
                                    "company network?%s" % (type(reason).__name__, after))

    @staticmethod
    def _http_failure(error, method, missing, sent):
        code = error.code
        denied = error.headers.get("X-Authentication-Denied-Reason")
        try:
            payload = json.loads(error.read().decode("utf-8"))
        except ValueError:
            payload = None
        is_jira = isinstance(payload, dict)
        payload = payload if is_jira else {}
        messages = list(payload.get("errorMessages") or [])
        fields = payload.get("errors") or {}
        detail = "; ".join(messages + ["%s: %s" % item for item in sorted(fields.items())])
        detail = ": " + detail if detail else ""
        if denied or (code == 403 and "captcha" in detail.lower()):
            return Failure(CREDENTIALS_REFUSED, "Jira refused the login and wants a CAPTCHA "
                                                "after failed logins: the user logs in to "
                                                "Jira in a browser once (not retried)"
                                                + STOP_ALL)
        if code == 401:
            return Failure(CREDENTIALS_REFUSED, "Jira refused the credentials (401): check "
                                                "JIRA_USER and JIRA_PASSWORD; not retried, "
                                                "since more failed logins make Jira ask "
                                                "for a CAPTCHA" + STOP_ALL)
        if 300 <= code < 400:
            return Failure(SETUP, "Jira answered with a redirect (%d), not followed: "
                                  "JIRA_URL is not Jira's base address, or a login page "
                                  "(SSO) is in front of it" % code)
        if code == 404 and not is_jira:
            return Failure(SETUP, NOT_JIRA)
        if code == 403:
            return Failure(NO_ACCESS, "no access (403)%s" % detail)
        if code == 404:
            return Failure(NOT_FOUND, missing or "not found (404)%s" % detail)
        if code == 413:
            return Failure(REFUSED, "Jira refused the request as too large (413)%s" % detail)
        if code == 429:
            # Rate limiting refuses the request before it runs, so nothing was applied.
            return Failure(SERVER_ERROR, "Jira is rate limiting requests (429): report it, "
                                         "do not retry")
        if code >= 500:
            # A proxy's 502/504 or a failing post-function can follow an applied write.
            return Failure(SERVER_ERROR, "Jira failed (%d)%s%s" % (
                code, detail, APPLIED_ANSWERED if method != "GET" else ""))
        if fields and sent is not None and not set(fields) & set(sent):
            names = ", ".join("%s (%s)" % item for item in sorted(fields.items()))
            return Failure(FIELDS_REQUIRED, "Jira needs the fields: %s" % names)
        if fields:
            names = ", ".join("%s (%s)" % item for item in sorted(fields.items()))
            return Failure(REFUSED, "Jira refused the values: %s" % names)
        return Failure(REFUSED, "Jira refused the request (%d)%s" % (code, detail))


# --- Markdown -> Jira wiki markup: a minimal subset, the rest passes as it is ----------

FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*([\w+#.-]*)\s*$")
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)(?:\s+#+)?\s*$")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
CODE_SPAN = re.compile(r"(`+)(.+?)\1")
# One level of balanced parentheses in the URL: [a](http://x/y_(z)).
LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)")
BOLD = re.compile(r"(?<![\w*])\*\*(?=\S)(.+?)(?<=\S)\*\*(?![\w*])"
                  r"|(?<![\w_])__(?=\S)(.+?)(?<=\S)__(?![\w_])")
# The languages Jira 8.13 highlights; any other gets {code:none}: a bare {code} is Java.
CODE_LANGUAGES = {"actionscript", "ada", "applescript", "bash", "c", "c#", "c++", "cpp",
                  "css", "erlang", "go", "groovy", "haskell", "html", "java", "javascript",
                  "js", "json", "lua", "none", "nyan", "objc", "perl", "php", "python", "r",
                  "rainbow", "ruby", "scala", "sh", "sql", "swift", "visualbasic", "xml",
                  "yaml"}
CODE_SYNONYMS = {"shell": "bash", "console": "bash", "zsh": "bash", "ts": "javascript",
                 "typescript": "javascript"}
ITALIC = re.compile(r"(?<![\w*])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![\w*])")
SLOT = re.compile("\x00(\\d+)\x00")
# A link or image to a file of the task: attachment:NAME, the name URL-encoded
# (attachment:my%20file.png), or <attachment:my file.png> as it is.
ATTACHMENT = re.compile(r"(!?)\[([^\]\n]*)\]\((?:<attachment:([^<>\n]+)>"
                        r"|attachment:((?:[^()\s]|\([^()\s]*\))+))\)")
CODE_ESCAPE = re.compile(r"([*_\-+^~{}\[\]|])")


def _attachment(match, names):
    name = match.group(3) or urllib.parse.unquote(match.group(4))
    names.append(name)
    if match.group(1):
        return "!%s!" % name  # Jira's image markup has no alt text
    return "[%s|^%s]" % (_inline(match.group(2)) if match.group(2) else name, name)


def _inline(text, names=None):
    # Code spans and link targets are set aside first, so no markup is read inside them;
    # Jira reads markup inside {{...}}, so its wiki characters are escaped there.
    slots = []
    names = [] if names is None else names

    def keep(value):
        slots.append(value)
        return "\x00%d\x00" % (len(slots) - 1)

    text = CODE_SPAN.sub(lambda m: keep(
        "{{%s}}" % CODE_ESCAPE.sub(r"\\\1", m.group(2).strip())), text)
    text = ATTACHMENT.sub(lambda m: keep(_attachment(m, names)), text)
    text = LINK.sub(lambda m: "[%s|%s]" % (m.group(1), keep(m.group(2))), text)
    text = BOLD.sub(lambda m: "\x01%s\x01" % (m.group(1) or m.group(2)), text)
    text = ITALIC.sub(r"_\1_", text).replace("\x01", "*")
    while SLOT.search(text):
        text = SLOT.sub(lambda m: slots[int(m.group(1))], text)
    return text


def _language(name):
    name = CODE_SYNONYMS.get(name.lower(), name.lower())
    return name if name in CODE_LANGUAGES else "none"


def _item(match):
    return (len(match.group(1).expandtabs(4)),
            "#" if match.group(2)[0].isdigit() else "*")


def _same_list(lists, match):
    """Whether a list item after a blank line goes on the open list: a deeper item, or one
    of the same kind at an open level (another kind there starts another list)."""
    if not match:
        return False
    indent, kind = _item(match)
    levels = dict(lists)
    return indent > lists[-1][0] or levels.get(indent, kind) == kind


def _wiki(text, names):
    out = []
    lists = []  # (indent, "*" or "#") of the open list levels
    fence = None
    held = []  # blank lines inside a list: a blank line ends a list in Jira
    for line in text.split("\n"):
        if fence:
            if line.strip().startswith(fence) and not line.strip().strip(fence[0]):
                out.append("{code}")
                fence = None
            else:
                out.append(line)
            continue
        if lists and not line.strip():
            held.append(line)
            continue
        if held and not _same_list(lists, LIST_ITEM.match(line)):
            out.extend(held)
            lists = []
        held = []
        match = FENCE.match(line)
        if match:
            fence = match.group(1)
            out.append("{code:%s}" % _language(match.group(2)))
            lists = []
            continue
        match = LIST_ITEM.match(line)
        if match:
            indent, kind = _item(match)
            while lists and lists[-1][0] > indent:
                lists.pop()
            if lists and lists[-1][0] == indent:
                lists[-1] = (indent, kind)
            else:
                lists.append((indent, kind))
            out.append("%s %s" % ("".join(k for _, k in lists),
                                  _inline(match.group(3), names)))
            continue
        if line.strip():
            lists = []
        match = HEADING.match(line)
        if match:
            out.append("h%d. %s" % (len(match.group(1)), _inline(match.group(2), names)))
        else:
            out.append(_inline(line, names))
    out.extend(held)
    if fence:  # a block left open is closed before the text's last newline
        out.insert(len(out) - (out[-1] == ""), "{code}")
    return "\n".join(out)


def to_wiki(text, names=None):
    """Markdown to Jira wiki markup; the text as it is if the conversion fails. The names
    of the files its attachment: links name are added to `names`."""
    found = []
    try:
        text = _wiki(text, found)
    except Exception:
        return text
    if names is not None:
        names.extend(found)
    return text


def text_arg(value, wiki, names=None):
    text = read_text(value)
    if wiki:
        return text
    found = []
    text = to_wiki(text, found)
    for name in found:
        if re.search(r"[!|\]]", name):
            raise Failure(REFUSED, "file name '%s' cannot be linked in Jira's wiki markup "
                                   "(it has !, | or ]): nothing written; attach the file "
                                   "under another name and link that" % name)
    if names is not None:
        names.extend(found)
    return text


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
    # Escaped: a bare [LADO: x] is a link in Jira, shown red as a broken one.
    label = "\\[LADO: %s\\]" % agent
    return "%s\n\n%s" % (label, text) if text else label


# A mark at the very start, as Jira keeps it (escaped) or as an agent may retype it; not a
# link whose text starts with "LADO:" (wiki [LADO: x|url], Markdown [LADO: x](url)).
LEADING_MARK = re.compile(r"\A\s*\\?\[LADO: [^\]\n|\\]*\\?\](?!\()\s*")


def remark(text):
    """The mark of a description edit writes: a leading mark is replaced by this agent's."""
    if not os.environ.get("LADO_AGENT", "").strip():
        return text
    return mark(LEADING_MARK.sub("", text, count=1))


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


def _person(user):
    """An account as Jira shows an assignee, comparable with whoami: 'Name (login)'."""
    if not user:
        return "unassigned"
    login = user.get("name") or user.get("key")
    name = user.get("displayName")
    if name and login and name != login:
        return "%s (%s)" % (name, login)
    return login or name or "?"


def _read_issue(jira, key):
    """The task with the fields get shows, and the Epic Link field id or None."""
    config = load_config(required=False)
    names = list(GET_FIELDS)
    epic = (config or {}).get("fields", {}).get("epic_link")
    if epic:
        names.append(epic)
    issue = jira.call("GET", "issue/" + urllib.parse.quote(key),
                      {"fields": ",".join(names)}, missing=missing_issue(key))
    return issue or {}, epic


def cmd_get(jira, args):
    issue, epic = _read_issue(jira, args.key)
    _print_issue(issue, epic, args.comments)
    return OK


def _print_issue(issue, epic, count):
    fields = issue.get("fields") or {}
    print("%s  %s" % (issue.get("key"), fields.get("summary")))
    print("Type: %s   Status: %s   Priority: %s" % (
        _name(fields.get("issuetype")), _name(fields.get("status")),
        _name(fields.get("priority"))))
    print("Assignee: %s   Reporter: %s" % (
        _person(fields.get("assignee")), _name(fields.get("reporter"))))
    if fields.get("labels"):
        print("Labels: " + ", ".join(fields["labels"]))
    if fields.get("parent"):
        print("Parent: " + fields["parent"].get("key", "?"))
    if epic and fields.get(epic):
        print("Epic: %s" % fields[epic])
    links = [_link_phrase(link) for link in fields.get("issuelinks") or []]
    if links:
        print("Links: " + "; ".join(links))
    print("Created: %s   Updated: %s" % (fields.get("created"), fields.get("updated")))
    print("\nDescription:\n%s" % (fields.get("description") or "(empty)"))
    files = fields.get("attachment") or []
    if files:
        print("\nFiles: %d" % len(files))
    for item in files:
        print("%s %s (%s, %s, %s)" % (item.get("id"), item.get("filename"),
                                      _size(item.get("size") or 0),
                                      _name(item.get("author")), item.get("created")))
    comments = (fields.get("comment") or {}).get("comments") or []
    shown = comments[-count:] if count > 0 else []
    if comments:
        print("\nComments: %d, the last %d shown" % (len(comments), len(shown)))
    else:
        print("\nComments: none")
    for comment in shown:
        print("\n--- comment %s, %s, %s\n%s" % (
            comment.get("id"), _name(comment.get("author")), comment.get("created"),
            comment.get("body")))


def _size(count):
    for unit in ("B", "KB", "MB"):
        if count < 1024 or unit == "MB":
            break
        count /= 1024.0
    return "%d %s" % (count, unit) if unit == "B" or count >= 10 else "%.1f %s" % (
        count, unit)


def _link_phrase(link):
    """A link as seen from the task that has it: 'blocks XYZ-9', 'is blocked by XYZ-9'."""
    kind = link.get("type") or {}
    if link.get("outwardIssue"):
        return "%s %s" % (kind.get("outward") or "?", link["outwardIssue"].get("key"))
    return "%s %s" % (kind.get("inward") or "?", (link.get("inwardIssue") or {}).get("key"))


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
            fields.get("summary"), _person(fields.get("assignee"))))
    if start + len(issues) < total:
        print("More: run again with --start %d" % (start + len(issues)))
    return OK


def cmd_create(jira, args):
    config = load_config(required=True)
    description = None
    if args.description is not None:
        names = []
        description = text_arg(args.description, args.wiki, names)
        if names:
            raise Failure(USAGE, "a new task has no files for attachment: links (%s): "
                                 "create it without them, attach the files, then edit "
                                 "the description" % ", ".join(names))
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
    if description is not None:
        fields["description"] = description
    if config["labels"]:
        fields["labels"] = list(config["labels"])
    if args.epic:
        fields[setting(config, "fields", "epic_link", "--epic")] = args.epic
    if args.epic_name:
        fields[setting(config, "fields", "epic_name", "--epic-name")] = args.epic_name
    fields.update(parse_fields(args.field))
    description = mark(fields.get("description") or "")
    if description:
        fields["description"] = description
    meta = (jira.call("GET", "%s/%s" % (base, type_id), {"maxResults": 500})
            or {}).get("values") or []
    # Jira Server may list the reporter as required, yet fills it with the caller.
    lacking = [f for f in meta
               if f.get("required") and not f.get("hasDefaultValue")
               and f.get("fieldId") not in fields and f.get("fieldId") != "reporter"]
    epic_name = (config.get("fields") or {}).get("epic_name")
    hints = []
    for f in lacking:
        label = "%s (%s)" % (f.get("name"), f.get("fieldId"))
        if epic_name and f.get("fieldId") == epic_name:
            hints.append("%s: give it with --epic-name '<name>'" % label)
        elif f.get("name", "").lower() == "epic name":
            # --epic-name writes fields.epic_name, which is unset or another field here.
            hints.append("%s: give it with --field %s=<name>" % (label, f.get("fieldId")))
        else:
            hints.append("%s: give it with --field id=value" % label)
    if hints:
        raise Failure(FIELDS_REQUIRED, "creating %s in %s needs: %s"
                      % (type_name, project, "; ".join(hints)))
    created = jira.call("POST", "issue", body={"fields": fields}, sent=fields)
    print("%s created" % created.get("key"))
    return OK


def _same(old, new):
    return ((old or "").replace("\r\n", "\n").strip()
            == (new or "").replace("\r\n", "\n").strip())


def cmd_edit(jira, args):
    if args.summary is None and args.description is None:
        raise Failure(USAGE, "give --summary, --description or both")
    if args.summary is not None and not args.summary.strip():
        raise Failure(USAGE, "the summary is empty")
    wanted = {}
    names = []
    if args.summary is not None:
        wanted["summary"] = args.summary
    if args.description is not None:
        wanted["description"] = remark(text_arg(args.description, args.wiki, names))
    issue, epic = _read_issue(jira, args.key)
    current = issue.get("fields") or {}
    _check_files(args.key, names, current.get("attachment"))
    # A field already so is not sent, so an edit run twice changes nothing the second time.
    fields = {name: value for name, value in wanted.items()
              if not _same(current.get(name), value)}
    if not fields:
        print("%s: %s already so, nothing changed\n" % (args.key, " and ".join(wanted)))
        _print_issue(issue, epic, 0)
        return OK
    jira.call("PUT", "issue/" + urllib.parse.quote(args.key), body={"fields": fields},
              missing=missing_issue(args.key), sent=None)
    try:
        issue, epic = _read_issue(jira, args.key)
    except Failure as failure:
        raise Failure(failure.code, "%s: %s changed, but reading the task back failed (do "
                                    "not run it again): %s"
                      % (args.key, " and ".join(fields), failure.message))
    print("%s: %s changed\n" % (args.key, " and ".join(fields)))
    _print_issue(issue, epic, 0)
    return OK


def _transitions(jira, key):
    result = jira.call("GET", "issue/%s/transitions" % urllib.parse.quote(key),
                       {"expand": "transitions.fields"}, missing=missing_issue(key))
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
    names = []
    comment = None
    if args.comment is not None:
        comment = mark(text_arg(args.comment, args.wiki, names))
    config = load_config(required=False)
    status = (config or {}).get("statuses", {}).get(args.target, args.target)
    issue = jira.call("GET", "issue/" + urllib.parse.quote(args.key),
                      {"fields": "status,attachment" if names else "status"},
                      missing=missing_issue(args.key))
    current = _name((issue.get("fields") or {}).get("status"))
    _check_files(args.key, names, (issue.get("fields") or {}).get("attachment"))
    transitions = _transitions(jira, args.key)
    wanted = {args.target.lower(), status.lower()}
    match = [t for t in transitions if t.get("id") == args.target]
    match = match or [t for t in transitions if t.get("name", "").lower() in wanted]
    match = match or [t for t in transitions if _name(t.get("to")).lower() in wanted]
    if not match and current.lower() == status.lower():
        if args.resolution or args.field:
            # Nothing is sent, the comment neither, so nothing is half done.
            raise Failure(REFUSED, "%s is already in %s: --resolution and --field were not "
                                   "applied, and no comment was posted" % (args.key, current))
        there = "%s is already in %s" % (args.key, current)
        if comment is not None:
            there += ", comment %s added" % _add_comment(jira, args.key, comment)
        print(there)
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
               and field_id not in fields
               and not (field_id == "comment" and args.comment is not None)]
    if lacking:
        raise Failure(FIELDS_REQUIRED, "transition '%s' needs: %s; give them with "
                                       "--resolution, --comment or --field id=value"
                      % (transition.get("name"), ", ".join(lacking)))
    body = {"transition": {"id": transition["id"]}}
    if fields:
        body["fields"] = fields
    # Jira drops update.comment of a transition with no comment field on its screen.
    inline = comment is not None and "comment" in (transition.get("fields") or {})
    if inline:
        body["update"] = {"comment": [{"add": {"body": comment}}]}
    sent = list(fields) + (["comment"] if inline else [])
    jira.call("POST", "issue/%s/transitions" % urllib.parse.quote(args.key), body=body,
              missing=missing_issue(args.key), sent=sent)
    moved = "%s: %s -> %s" % (args.key, current, _name(transition.get("to")))
    if inline:
        found = _comment_id(jira, args.key, comment)
        moved += ", comment %s added" % found if found else ", comment added"
    elif comment is not None:
        try:
            moved += ", comment %s added" % _add_comment(jira, args.key, comment)
        except Failure as failure:
            # No answer or a 5xx may follow a comment Jira did add; a 429 runs nothing.
            # The advice keeps the failure's own rule: only a refused comment is fixed and
            # sent again at once; after 9 wait, after any other failure report it first.
            rate_limited = failure.status == 429
            unsure = failure.code == UNREACHABLE or (failure.code == SERVER_ERROR
                                                     and not rate_limited)
            check = "check with get, then send the comment with comment if it is not there"
            if failure.code == UNREACHABLE:
                advice = "once you are told Jira answers again, " + check
            elif unsure:
                advice = check
            elif failure.code == REFUSED:
                advice = "fix the text the line names, then send the comment with comment"
            else:
                advice = "report it; send the comment with comment once you are told to"
            raise Failure(failure.code, "%s done, but %s (do not run the transition again; "
                                        "%s): %s" % (
                moved, "the comment may not have been added" if unsure
                else "the comment was not added", advice, failure.message))
    print(moved)
    return OK


def _comment_id(jira, key, text):
    """The id of the newest comment with this text, or None: Jira returns no id for a
    comment sent with a transition, and the transition is done whatever this finds."""
    try:
        result = jira.call("GET", "issue/%s/comment" % urllib.parse.quote(key),
                           missing=missing_issue(key))
    except Failure:
        return None
    want = text.replace("\r\n", "\n").strip()
    for comment in reversed((result or {}).get("comments") or []):
        if (comment.get("body") or "").replace("\r\n", "\n").strip() == want:
            return comment.get("id")
    return None


def _add_comment(jira, key, text):
    result = jira.call("POST", "issue/%s/comment" % urllib.parse.quote(key),
                       body={"body": text}, missing=missing_issue(key), sent=None)
    return (result or {}).get("id")


def cmd_comment(jira, args):
    names = []
    text = mark(text_arg(args.text, args.wiki, names))
    if names:
        _check_files(args.key, names, _files(jira, args.key))
    comment_id = _add_comment(jira, args.key, text)
    print("%s: comment %s added" % (args.key, comment_id))
    return OK


def _user(name):
    return name or "unassigned"


def cmd_assign(jira, args):
    login = {"me": os.environ["JIRA_USER"], "none": None}.get(args.user, args.user)
    path = "issue/%s" % urllib.parse.quote(args.key)
    issue = jira.call("GET", path, {"fields": "assignee"}, missing=missing_issue(args.key))
    holder = (issue.get("fields") or {}).get("assignee")
    current = (holder or {}).get("name") or (holder or {}).get("key")
    if (current or "").lower() == (login or "").lower():
        print("%s: assignee %s already, nothing changed" % (args.key, _user(current)))
        return OK
    # Taking a task from another account is the human's decision, never a side effect.
    mine = os.environ["JIRA_USER"].lower()
    if current and current.lower() != mine and not args.reassign:
        raise Failure(REFUSED, "%s is assigned to %s, another account: not changed; "
                               "report it, and add --reassign only when the human or your "
                               "step says to take it from them" % (args.key, _person(holder)))
    try:
        jira.call("PUT", path + "/assignee", body={"name": login},
                  missing=missing_issue(args.key), sent=None)
    except Failure as failure:
        # Jira answers this request with 401 for a missing permission and 404 for an
        # unknown user; the GET above has just passed the login and found the task.
        if failure.status == 401 and not failure.denied:
            raise Failure(NO_ACCESS, "no permission to assign %s (401)" % args.key)
        if login is None:
            if failure.code == NOT_FOUND:
                raise Failure(NOT_FOUND, "Jira refused to unassign %s: the task is gone or "
                                         "not visible to you (404)" % args.key)
            if failure.code == REFUSED:
                raise Failure(REFUSED, "Jira refused to unassign %s: %s"
                              % (args.key, failure.message))
            raise
        if failure.code in (NOT_FOUND, REFUSED):
            raise Failure(REFUSED, "Jira refused to assign %s to %s: no such user, or the "
                                   "user cannot be assigned in this project (%s)"
                          % (args.key, _user(login), failure.message
                             if failure.status != 404 else "404"))
        raise
    print("%s: assignee %s -> %s" % (args.key, _user(current), _user(login)))
    return OK


def cmd_whoami(jira, args):
    me = jira.call("GET", "myself")
    print("You work as %s" % _person(me or {}))
    return OK


def _labels(jira, key):
    issue = jira.call("GET", "issue/" + urllib.parse.quote(key), {"fields": "labels"},
                      missing=missing_issue(key))
    return list((issue.get("fields") or {}).get("labels") or [])


def cmd_label(jira, args):
    add = [label for group in args.add or [] for label in group]
    remove = [label for group in args.remove or [] for label in group]
    if not add and not remove:
        raise Failure(USAGE, "give --add or --remove with at least one label")
    for label in add + remove:
        # Jira takes no whitespace in a label: refused here, before any request.
        if not label or re.search(r"\s", label):
            raise Failure(USAGE, "label '%s': a label has no spaces; write it as one word, "
                                 "e.g. waiting_for_release" % label)
    before = _labels(jira, args.key)
    changes = ([{"add": label} for label in add if label not in before]
               + [{"remove": label} for label in remove if label in before])
    if not changes:
        print("%s: labels %s, nothing changed" % (args.key, ", ".join(before) or "none"))
        return OK
    jira.call("PUT", "issue/" + urllib.parse.quote(args.key),
              body={"update": {"labels": changes}}, missing=missing_issue(args.key),
              sent=None)
    try:
        after = _labels(jira, args.key)
    except Failure as failure:
        raise Failure(failure.code, "%s: labels changed, but reading them back failed (do "
                                    "not run it again): %s" % (args.key, failure.message))
    print("%s: labels %s" % (args.key, ", ".join(after) or "none"))
    return OK


def cmd_link(jira, args):
    if re.match(r"^https?://", args.target):
        if args.type:
            raise Failure(USAGE, "--type is for a link to a task, not to a URL")
        return _link_url(jira, args.key, args.target, args.title)
    if not ISSUE_KEY.match(args.target):
        raise Failure(USAGE, "'%s' is neither an http(s):// URL nor a task key such as "
                             "ABC-12" % args.target)
    if args.title is not None:
        raise Failure(USAGE, "--title is for a link to a URL, not to a task")
    if args.target.lower() == args.key.lower():
        raise Failure(USAGE, "a task cannot be linked to itself")
    return _link_task(jira, args.key, args.target, args.type or "relates")


def _link_task(jira, key, other, word):
    if word not in LINK_WORDS:
        raise Failure(REFUSED, "link type '%s' is unknown; use one of: %s"
                      % (word, ", ".join(LINK_WORDS)))
    name, phrase = LINK_WORDS[word]
    config = load_config(required=False)
    name = (config or {}).get("link_types", {}).get(word, name)
    said = "%s %s" % (phrase, other)
    issue = jira.call("GET", "issue/" + urllib.parse.quote(key), {"fields": "issuelinks"},
                      missing=missing_issue(key))
    for link in (issue.get("fields") or {}).get("issuelinks") or []:
        kind = link.get("type") or {}
        if (kind.get("name") or "").lower() != name.lower():
            continue
        # A type that reads the same both ways (Relates) counts in either direction.
        ends = ["outwardIssue"]
        if kind.get("inward") == kind.get("outward"):
            ends.append("inwardIssue")
        if any((link.get(end) or {}).get("key", "").lower() == other.lower()
               for end in ends):
            print("%s: already linked (%s), nothing changed" % (key, said))
            return OK
    # Jira's REST API names the ends backwards: the inwardIssue is the one that "blocks".
    body = {"type": {"name": name}, "inwardIssue": {"key": key},
            "outwardIssue": {"key": other}}
    try:
        jira.call("POST", "issueLink", body=body, sent=None)
    except Failure as failure:
        # Jira answers this request with 401 for a missing permission; the GET above has
        # just passed the login.
        if (failure.status == 401 and not failure.denied) or failure.code == NO_ACCESS:
            raise Failure(NO_ACCESS, "no permission to link %s and %s (%d)"
                          % (key, other, failure.status))
        refused = failure.code == REFUSED
        if failure.code == NOT_FOUND:
            # Jira 8.13 answers an unknown link type with 404 too; KEY was just found.
            try:
                jira.call("GET", "issue/" + urllib.parse.quote(other), {"fields": "key"})
                refused = True
            except Failure as missing:
                if missing.code != NOT_FOUND:
                    raise
                raise Failure(NOT_FOUND, "cannot link %s and %s: a task is missing or not "
                                         "visible to you (%s)" % (key, other, failure.message))
        if refused:
            raise Failure(REFUSED, "Jira refused link type '%s' (%s): if this Jira names "
                                   "it otherwise, the user sets 'link_types.%s' in %s"
                          % (name, failure.message, word, CONFIG_PATH))
        raise
    print("%s: linked (%s)" % (key, said))
    return OK


def _link_url(jira, key, url, title):
    body = {"globalId": url, "object": {"url": url, "title": title or url}}
    jira.call("POST", "issue/%s/remotelink" % urllib.parse.quote(key), body=body,
              missing=missing_issue(key), sent=None)
    print("%s: linked %s" % (key, url))
    return OK


# --- files of a task --------------------------------------------------------------------


def _files(jira, key):
    issue = jira.call("GET", "issue/" + urllib.parse.quote(key), {"fields": "attachment"},
                      missing=missing_issue(key))
    return (issue.get("fields") or {}).get("attachment") or []


def _file_list(files):
    return ", ".join(sorted({f.get("filename") or "?" for f in files})) or "none"


def _check_files(key, names, files, more=()):
    """Refuse attachment: links to files the task does not have, before any write."""
    known = {f.get("filename") for f in files or []} | set(more)
    unknown = [name for name in names if name not in known]
    if unknown:
        raise Failure(REFUSED, "%s has no file %s for the attachment: links, nothing "
                               "written; its files: %s"
                      % (key, ", ".join(unknown), _file_list(files or [])))


def _newest(files):
    return max(files, key=lambda f: (f.get("created") or "", _number(f.get("id"))))


def _number(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def attachment_ref(name):
    """The attachment: form of a name, ready to paste into Markdown."""
    return "attachment:" + urllib.parse.quote(name, safe="")


def _multipart(path, name):
    boundary = "lado-" + base64.b16encode(os.urandom(12)).decode("ascii")
    quoted = name.replace("\\", "\\\\").replace('"', '\\"')
    with open(path, "rb") as handle:
        content = handle.read()
    head = ('--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\n'
            'Content-Type: application/octet-stream\r\n\r\n' % (boundary, quoted))
    data = head.encode("utf-8") + content + ("\r\n--%s--\r\n" % boundary).encode("ascii")
    return data, "multipart/form-data; boundary=" + boundary


def _readable(path):
    if not os.path.exists(path):
        return "not found"
    if os.path.isdir(path):
        return "a folder, not a file"
    try:
        with open(path, "rb"):
            return None
    except OSError as error:
        return "cannot be read (%s)" % (error.strerror or error)


def cmd_attach(jira, args):
    for path in args.files:
        problem = _readable(path)
        if problem:
            raise Failure(USAGE, "%s: %s; nothing uploaded" % (path, problem))
    names = []
    comment = None
    if args.comment is not None:
        comment = mark(text_arg(args.comment, args.wiki, names))
    files = _files(jira, args.key)
    _check_files(args.key, names, files, [os.path.basename(p) for p in args.files])
    done = []
    for number, path in enumerate(args.files):
        name = os.path.basename(path)
        try:
            answer = jira.call("POST", "issue/%s/attachments" % urllib.parse.quote(args.key),
                               upload=_multipart(path, name), missing=missing_issue(args.key),
                               sent=None)
        except Failure as failure:
            if failure.status == 404:
                # The task was just found: Jira 8.13 answers a file over its size limit
                # 404, with a plain-text body (tried on 8.13.19).
                failure = Failure(REFUSED, "Jira refused %s (404): larger than its "
                                           "attachment size limit (jira.attachment.size), "
                                           "or the task is gone" % name)
            elif failure.code == NO_ACCESS and "disabled" in failure.message.lower():
                failure = Failure(REFUSED, "attachments are disabled in this Jira: %s"
                                  % failure.message)
            if not done and failure.code in (REFUSED, NO_ACCESS):
                raise failure
            # No answer or a 5xx may follow an upload Jira did keep; a 429 runs nothing.
            unsure = failure.code == UNREACHABLE or (failure.code == SERVER_ERROR
                                                     and failure.status != 429)
            rest = [os.path.basename(p) for p in args.files[number + unsure:]]
            raise Failure(failure.code, "%s: uploaded %s;%s not uploaded %s%s: %s" % (
                args.key, ", ".join(done) or "none",
                " may have been uploaded %s (check with get before attaching it again);"
                % name if unsure else "", ", ".join(rest) or "none",
                "; no comment added" if comment is not None else "", failure.message))
        for item in answer or []:
            print("%s %s %s" % (item.get("id"), item.get("filename"),
                                attachment_ref(item.get("filename") or name)))
        done.append(name)
    if comment is not None:
        try:
            comment_id = _add_comment(jira, args.key, comment)
        except Failure as failure:
            raise Failure(failure.code, "%s: uploaded %s, but the comment was not added "
                                        "(do not attach again; send it with comment): %s"
                          % (args.key, ", ".join(done), failure.message))
        print("%s: comment %s added" % (args.key, comment_id))
    return OK


def _safe_name(name, fallback):
    name = re.split(r"[/\\]", name or "")[-1]
    name = re.sub(r"[\x00-\x1f\x7f]", "", name).strip()
    return fallback if name in ("", ".", "..") else name


def _free_path(folder, name):
    stem, ext = os.path.splitext(name)
    path, number = os.path.join(folder, name), 0
    while os.path.exists(path):
        number += 1
        path = os.path.join(folder, "%s-%d%s" % (stem, number, ext))
    return path


def cmd_download(jira, args):
    if args.to is not None:
        folder = os.path.abspath(args.to)
        if not os.path.isdir(folder) or not os.access(folder, os.W_OK | os.X_OK):
            raise Failure(USAGE, "--to %s is not a folder you can write to" % args.to)
    files = _files(jira, args.key)
    chosen = []
    for wanted in args.names:
        found = [f for f in files if str(f.get("id")) == wanted]
        found = found or [f for f in files if f.get("filename") == wanted]
        if not found:
            raise Failure(NOT_FOUND, "%s has no file '%s'; its files: %s" % (
                args.key, wanted, "; ".join("%s %s" % (f.get("id"), f.get("filename"))
                                            for f in files) or "none"))
        chosen.append(_newest(found))
    for item in chosen:
        if not jira.same_server(item.get("content") or ""):
            raise Failure(REFUSED, "%s's file %s is served from another address than "
                                   "JIRA_URL: not downloaded, the credentials not sent "
                                   "(Jira's base URL differs from JIRA_URL); report it"
                          % (args.key, item.get("filename")))
    if args.to is None:
        folder = tempfile.mkdtemp(prefix="lado-jira-")
    done = []
    for number, item in enumerate(chosen):
        try:
            data = jira.send("GET", item["content"])
            path = _free_path(folder, _safe_name(item.get("filename"),
                                                 "file-%s" % item.get("id")))
            with open(path, "xb") as handle:
                handle.write(data)
        except (Failure, OSError) as failure:
            status = getattr(failure, "status", None)
            if status == 404:
                failure = Failure(NOT_FOUND, "file %s not found (404)" % item.get("filename"))
            elif status and 300 <= status < 400:
                failure = Failure(REFUSED, "Jira answered file %s with a redirect (%d), not "
                                           "followed: the credentials go only to JIRA_URL; "
                                           "report it" % (item.get("filename"), status))
            message = getattr(failure, "message", None) or "cannot write: %s" % failure
            raise Failure(getattr(failure, "code", USAGE),
                          "%s: downloaded %s; not downloaded %s: %s" % (
                              args.key, ", ".join(done) or "none",
                              ", ".join(f.get("filename") or "?" for f in chosen[number:]),
                              message))
        print(path)
        done.append(path)
    return OK


# --- command line ----------------------------------------------------------------------


def parser():
    top = argparse.ArgumentParser(
        prog="jira.py",
        description="Jira Server / Data Center 8.4 or newer through REST API v2.")
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
    p.add_argument("--description", help="Markdown; '-' reads it from stdin")
    p.add_argument("--wiki", action="store_true",
                   help="send --description as it is, as Jira wiki markup")
    p.add_argument("--epic", help="key of the epic (needs fields.epic_link)")
    p.add_argument("--epic-name", help="Epic Name, for an epic (needs fields.epic_name)")
    p.add_argument("--field", action="append", metavar="ID=VALUE",
                   help="another field; a value starting with { or [ is JSON")
    p.set_defaults(run=cmd_create)

    p = sub.add_parser("edit", help="change a task's summary or description")
    p.add_argument("key")
    p.add_argument("--summary", help="the new summary")
    p.add_argument("--description", help="the new description, Markdown; '-' reads it "
                                         "from stdin")
    p.add_argument("--wiki", action="store_true",
                   help="send --description as it is, as Jira wiki markup")
    p.set_defaults(run=cmd_edit)

    p = sub.add_parser("transition", help="list transitions, or move a task")
    p.add_argument("key")
    p.add_argument("target", nargs="?",
                   help="transition id or name, target status, or a word of statuses")
    p.add_argument("--resolution", help="resolution name, when the screen asks for it")
    p.add_argument("--comment", help="comment to add, Markdown; '-' reads it from stdin")
    p.add_argument("--wiki", action="store_true",
                   help="send --comment as it is, as Jira wiki markup")
    p.add_argument("--field", action="append", metavar="ID=VALUE",
                   help="a field the screen asks for; a value starting with { or [ is JSON")
    p.set_defaults(run=cmd_transition)

    p = sub.add_parser("comment", help="comment on a task")
    p.add_argument("key")
    p.add_argument("text", help="Markdown; '-' reads it from stdin")
    p.add_argument("--wiki", action="store_true",
                   help="send the text as it is, as Jira wiki markup")
    p.set_defaults(run=cmd_comment)

    p = sub.add_parser("assign", help="assign a task to you, to a login, or to nobody")
    p.add_argument("key")
    p.add_argument("user", help="'me' (JIRA_USER), a login, or 'none' to unassign")
    p.add_argument("--reassign", action="store_true",
                   help="also when another account holds the task (refused otherwise)")
    p.set_defaults(run=cmd_assign)

    p = sub.add_parser("label", help="add or remove labels, the task's others untouched")
    p.add_argument("key")
    p.add_argument("--add", action="append", nargs="+", metavar="LABEL")
    p.add_argument("--remove", action="append", nargs="+", metavar="LABEL")
    p.set_defaults(run=cmd_label)

    p = sub.add_parser("link", help="link a branch, commit or pull request URL, or another "
                                    "task, to a task")
    p.add_argument("key")
    p.add_argument("target", help="an http(s):// URL, or the key of another task")
    p.add_argument("--title", help="link text, for a URL (default: the URL)")
    p.add_argument("--type", help="for a task: %s (default relates), meaning 'KEY <type> "
                                  "TARGET'" % ", ".join(LINK_WORDS))
    p.set_defaults(run=cmd_link)

    p = sub.add_parser("attach", help="upload files to a task; prints each one's "
                                      "attachment: link")
    p.add_argument("key")
    p.add_argument("files", nargs="+", metavar="FILE")
    p.add_argument("--comment", help="comment to add after the upload, Markdown; '-' reads "
                                     "it from stdin")
    p.add_argument("--wiki", action="store_true",
                   help="send --comment as it is, as Jira wiki markup")
    p.set_defaults(run=cmd_attach)

    p = sub.add_parser("download", help="download a task's files; prints each file's path")
    p.add_argument("key")
    p.add_argument("names", nargs="+", metavar="NAME_OR_ID",
                   help="a file's id, or its name (the newest file of that name)")
    p.add_argument("--to", help="an existing folder (default: a new temporary folder)")
    p.set_defaults(run=cmd_download)

    p = sub.add_parser("whoami", help="the account you work as: display name (login)")
    p.set_defaults(run=cmd_whoami)
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
