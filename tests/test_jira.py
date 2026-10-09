"""Tests of skills/tracker/jira.py against a fake Jira on localhost.

Run from the repository root: uv run --no-project python -m unittest discover -s tests
Standard library only; the TLS test needs the `openssl` command and is skipped without it.
"""

import base64
import contextlib
import io
import json
import os
import shutil
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True  # keep the skill folder free of __pycache__
sys.path.insert(0, os.path.join(HERE, "..", "skills", "tracker"))
import jira  # noqa: E402

PASSWORD = "s3cret-Passw0rd"
CONFIG = """\
# settings of the test project
project: TEST
issue_types:
  bug: Bug          # a word of the process -> the board's name
  epic: Epic
statuses:
  review: Code Review
  done: Done
labels: [lado, "agent made"]
fields:
  epic_link: customfield_10100
  epic_name: 'customfield_10101'
"""


class Raw:
    """A payload sent as it is; `length` claims a longer body that never comes."""

    def __init__(self, data, length=None):
        self.data, self.length = data, length


class Seq:
    """Payloads answered one per request, the last one from then on."""

    def __init__(self, *payloads):
        self.payloads = list(payloads)

    def next(self):
        return self.payloads.pop(0) if len(self.payloads) > 1 else self.payloads[0]


class FakeJira:
    """Answers each (method, path) from `routes`, records every request."""

    def __init__(self, tls_context=None):
        self.routes = {}
        self.requests = []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                url = urllib.parse.urlsplit(self.path)
                fake.requests.append({
                    "method": self.command, "path": url.path,
                    "query": dict(urllib.parse.parse_qsl(url.query)),
                    "headers": dict(self.headers),
                    "body": json.loads(body) if body else None})
                route = fake.routes.get((self.command, url.path))
                if route is None:
                    status, headers, payload = 404, {}, {"errorMessages": ["no route"]}
                else:
                    status, headers, payload = route
                    if isinstance(payload, Seq):
                        payload = payload.next()
                raw = payload if isinstance(payload, Raw) else Raw(
                    json.dumps(payload).encode() if payload is not None else b"")
                data = raw.data
                self.send_response(status)
                for name, value in headers.items():
                    self.send_header(name, value)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(raw.length or len(data)))
                self.end_headers()
                self.wfile.write(data)

            do_GET = do_POST = do_PUT = do_DELETE = _answer

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        if tls_context:
            self.server.socket = tls_context.wrap_socket(self.server.socket,
                                                         server_side=True)
        scheme = "https" if tls_context else "http"
        self.url = "%s://127.0.0.1:%d" % (scheme, self.server.server_address[1])
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       args=(0.05,), daemon=True)
        self.thread.start()

    def route(self, method, path, payload=None, status=200, headers=None):
        self.routes[(method, "/rest/api/2/" + path)] = (status, headers or {}, payload)

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class JiraTestCase(unittest.TestCase):
    def setUp(self):
        self.jira = FakeJira()
        self.addCleanup(self.jira.close)
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        os.mkdir(os.path.join(self.repo, ".git"))
        os.mkdir(os.path.join(self.repo, ".lado"))
        self.write_config(CONFIG)
        old = os.getcwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, old)
        env = {"JIRA_URL": self.jira.url + "/", "JIRA_USER": "agent.user",
               "JIRA_PASSWORD": PASSWORD, "LADO_AGENT": "developer"}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)

    def write_config(self, text):
        with open(os.path.join(self.repo, ".lado", "tracker.yaml"), "w") as handle:
            handle.write(text)

    def run_jira(self, *argv, stdin=""):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                mock.patch("sys.stdin", io.StringIO(stdin)):
            try:
                code = jira.main(list(argv))
            except SystemExit as exit:
                code = exit.code
        self.assertNotIn(PASSWORD, out.getvalue() + err.getvalue())
        # assign and whoami print accounts as Jira shows them, JIRA_USER's login too.
        if argv[:1] not in (("assign",), ("whoami",)):
            self.assertNotIn("agent.user", out.getvalue() + err.getvalue())
        return code, out.getvalue(), err.getvalue()

    def sent(self, method, path):
        return [r for r in self.jira.requests
                if r["method"] == method and r["path"] == "/rest/api/2/" + path]


class ConfigTest(unittest.TestCase):
    def parse(self, text):
        return jira.parse_config(text, "tracker.yaml")

    def test_full_example(self):
        config = self.parse(CONFIG)
        self.assertEqual(config["project"], "TEST")
        self.assertEqual(config["issue_types"], {"bug": "Bug", "epic": "Epic"})
        self.assertEqual(config["labels"], ["lado", "agent made"])
        self.assertEqual(config["fields"]["epic_name"], "customfield_10101")

    def test_localized_names(self):
        config = self.parse("project: A\nstatuses:\n  review: Ревью кода  # translated\n")
        self.assertEqual(config["statuses"]["review"], "Ревью кода")

    def test_only_project_is_required(self):
        config = self.parse("project: ABC\n")
        self.assertEqual(config["statuses"], {})
        self.assertEqual(config["labels"], [])
        with self.assertRaisesRegex(ValueError, "'project'.*required"):
            self.parse("labels: [a]\n")

    def test_hash_inside_quotes_is_kept(self):
        self.assertEqual(self.parse("project: 'A#B' # comment\n")["project"], "A#B")
        config = self.parse("project: A\nstatuses:\n  wontfix: Won't Fix  # note\n")
        self.assertEqual(config["statuses"]["wontfix"], "Won't Fix")

    def test_errors_name_the_line(self):
        cases = {
            "project: A\n\tlabels: [a]\n": "line 2: indent with spaces",
            "project: A\nlabels:\n  - a\n": "line 3: block lists",
            "project: A\nfields:\n  a:\n    b: c\n": "line 3: .*one level",
            "project: A\nfields:\n  a: b\n    c: d\n": "line 4: only one level",
            "project A\n": "line 1: expected 'key: value'",
            "project: A\nproject: B\n": "line 2: 'project' is given twice",
            "project: A\nlabels: [a, b\n": "line 2: .*end with ']'",
            "project: 'A\n": "line 1: .*same quote",
            "project: A\n  x: y\n": "line 2: unexpected indent",
            "project: {a: b}\n": "line 1: .*flow maps",
        }
        for text, message in cases.items():
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, "tracker.yaml " + message):
                    self.parse(text)

    def test_unknown_key_and_wrong_shapes(self):
        with self.assertRaisesRegex(ValueError, "line 2: unknown key 'statuss'"):
            self.parse("project: A\nstatuss:\n  done: Done\n")
        with self.assertRaisesRegex(ValueError, "line 3: 'labels' must be a list"):
            self.parse("project: A\n\nlabels: lado\n")
        with self.assertRaisesRegex(ValueError, "line 2: 'statuses' must be a map"):
            self.parse("project: A\nstatuses: Done\n")
        with self.assertRaisesRegex(ValueError, "line 4: 'statuses.done' must be one plain"):
            self.parse("project: A\nstatuses:\n  review: Review\n  done: [x]\n")
        with self.assertRaisesRegex(ValueError, "tracker.yaml: 'project'.* is required"):
            self.parse("labels: [a]\n")

    def test_found_upward_but_not_above_the_repository(self):
        top = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, top)
        repo = os.path.join(top, "repo")
        deep = os.path.join(repo, "src", "deep")
        os.makedirs(deep)
        os.makedirs(os.path.join(top, ".lado"))
        open(os.path.join(top, ".lado", "tracker.yaml"), "w").close()
        open(os.path.join(repo, ".git"), "w").close()  # a worktree's .git is a file
        self.assertIsNone(jira.find_config(deep))
        os.makedirs(os.path.join(repo, ".lado"))
        open(os.path.join(repo, ".lado", "tracker.yaml"), "w").close()
        self.assertEqual(jira.find_config(deep),
                         os.path.join(os.path.abspath(repo), ".lado", "tracker.yaml"))


class MarkdownTest(unittest.TestCase):
    def assertWiki(self, markdown, wiki):
        self.assertEqual(jira.to_wiki(markdown), wiki)

    def test_headings(self):
        self.assertWiki("# One\n###### Six ##", "h1. One\nh6. Six")
        self.assertWiki("#no space", "#no space")

    def test_emphasis_and_code(self):
        self.assertWiki("**b** __b__ *i* _i_ `c`", "*b* *b* _i_ _i_ {{c}}")
        self.assertWiki("**bold with *italic***", "*bold with _italic_*")
        self.assertWiki("`a **b** [x](y)`", r"{{a \*\*b\*\* \[x\](y)}}")
        self.assertWiki("run `**/*.py` and `{x}`", r"run {{\*\*/\*.py}} and {{\{x\}}}")
        self.assertWiki("2 * 3 * 4 and snake_case_name", "2 * 3 * 4 and snake_case_name")

    def test_links(self):
        self.assertWiki("see [the PR](https://h/a__b__c) now",
                        "see [the PR|https://h/a__b__c] now")
        self.assertWiki("[**bold** link](http://x)", "[*bold* link|http://x]")
        self.assertWiki("![alt](http://x/y.png)", "![alt](http://x/y.png)")
        self.assertWiki("[a](http://x/y_(z)) and (see [b](http://w))",
                        "[a|http://x/y_(z)] and (see [b|http://w])")

    def test_lists_nest_by_indent(self):
        self.assertWiki("- a\n  * b\n    1. c\n  + d\n- e\n\n1. f\n2. g",
                        "* a\n** b\n**# c\n** d\n* e\n\n# f\n# g")
        self.assertWiki("1. a\n   - b", "# a\n#* b")

    def test_blank_lines_inside_a_list_are_dropped(self):
        self.assertWiki("1. one\n\n2. two\n\n  - sub\n\nafter\n",
                        "# one\n# two\n#* sub\n\nafter\n")
        self.assertWiki("- e\n\n1. f", "* e\n\n# f")

    def test_code_block_content_is_untouched(self):
        self.assertWiki("```python\n# not a heading\n**x** `y`\n```\nafter **z**",
                        "{code:python}\n# not a heading\n**x** `y`\n{code}\nafter *z*")
        self.assertWiki("~~~\n- x\n", "{code:none}\n- x\n{code}\n")

    def test_code_block_language_is_one_jira_knows(self):
        for given, sent in [("Python", "python"), ("c#", "c#"), ("yaml", "yaml"),
                            ("shell", "bash"), ("console", "bash"), ("zsh", "bash"),
                            ("ts", "javascript"), ("TypeScript", "javascript"),
                            ("rust", "none"), ("diff", "none"), ("", "none")]:
            self.assertWiki("```%s\nx\n```" % given, "{code:%s}\nx\n{code}" % sent)

    def test_wiki_characters_and_the_rest_pass_as_they_are(self):
        text = "[~jdoe] {noformat} [text|http://x] ||h|| > quote\n| a | b |\n"
        self.assertWiki(text, text)

    def test_failure_sends_the_original_text(self):
        with mock.patch.object(jira, "_wiki", side_effect=RuntimeError):
            self.assertEqual(jira.to_wiki("**x**"), "**x**")


class CommandsTest(JiraTestCase):
    def test_get(self):
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1", "fields": {
            "summary": "Fix login", "status": {"name": "Open"},
            "issuetype": {"name": "Bug"}, "assignee": {"name": "ann", "displayName": "Ann"},
            "description": "h2. Steps\n# open", "customfield_10100": "TEST-9",
            "comment": {"comments": [{"id": str(100 + i), "author": {"displayName": "Bob"},
                                      "body": "c%d" % i, "created": "2026-10-0%d" % i}
                                     for i in range(1, 8)]}}})
        code, out, err = self.run_jira("get", "TEST-1", "--comments", "2")
        self.assertEqual(code, 0, err)
        self.assertIn("TEST-1  Fix login", out)
        self.assertIn("Status: Open", out)
        self.assertIn("Assignee: Ann (ann)", out)
        self.assertIn("Epic: TEST-9", out)
        self.assertIn("h2. Steps", out)
        self.assertIn("Comments: 7, the last 2 shown", out)
        self.assertIn("--- comment 107, Bob, 2026-10-07\nc7", out)
        self.assertNotIn("c5", out)
        request = self.jira.requests[0]
        expected = "Basic " + base64.b64encode(
            ("agent.user:" + PASSWORD).encode()).decode()
        self.assertEqual(request["headers"]["Authorization"], expected)
        self.assertIn("customfield_10100", request["query"]["fields"])

    def test_get_without_comments(self):
        self.jira.route("GET", "issue/TEST-2", {"key": "TEST-2", "fields": {
            "summary": "Quiet", "comment": {"comments": []}}})
        code, out, err = self.run_jira("get", "TEST-2")
        self.assertEqual(code, 0, err)
        self.assertIn("Comments: none", out)
        self.assertIn("Assignee: unassigned", out)
        self.assertNotIn("shown", out)

    def test_search_pages_and_project_placeholder(self):
        self.jira.route("GET", "search", {"startAt": 20, "total": 45, "issues": [
            {"key": "TEST-%d" % i, "fields": {"summary": "s", "status": {"name": "Open"},
                                             "issuetype": {"name": "Task"},
                                             "assignee": {"name": "ann", "displayName": "Ann"}
                                             if i else None}}
            for i in range(20)]})
        code, out, err = self.run_jira("search", "project = {project} AND status = Open",
                                       "--start", "20")
        self.assertEqual(code, 0, err)
        query = self.jira.requests[0]["query"]
        self.assertEqual(query["jql"], "project = TEST AND status = Open")
        self.assertEqual((query["startAt"], query["maxResults"]), ("20", "20"))
        self.assertIn("Tasks 21-40 of 45", out)
        self.assertIn("More: run again with --start 40", out)
        self.assertIn("TEST-0  [Open]  Task  s  (unassigned)", out)
        self.assertIn("TEST-1  [Open]  Task  s  (Ann (ann))", out)

    def test_whoami(self):
        self.jira.route("GET", "myself", {"name": "agent.user", "displayName": "Agent User",
                                          "emailAddress": "agent@example.com"})
        code, out, err = self.run_jira("whoami")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "You work as Agent User (agent.user)\n")
        self.assertNotIn("127.0.0.1", out + err)

    def route_createmeta(self, required=()):
        self.jira.route("GET", "issue/createmeta/TEST/issuetypes", {"values": [
            {"id": "1", "name": "Bug"}, {"id": "10000", "name": "Epic"}]})
        fields = [{"fieldId": "summary", "name": "Summary", "required": True},
                  {"fieldId": "reporter", "name": "Reporter", "required": True,
                   "hasDefaultValue": True}]
        fields += [{"fieldId": f, "name": f.title(), "required": True} for f in required]
        self.jira.route("GET", "issue/createmeta/TEST/issuetypes/1", {"values": fields})
        self.jira.route("POST", "issue", {"key": "TEST-5"}, status=201)

    def test_create_with_mark_labels_and_epic(self):
        self.route_createmeta()
        code, out, err = self.run_jira("create", "--type", "bug", "--summary", "Crash",
                                       "--description", "-", "--epic", "TEST-9",
                                       stdin="## Steps\n1. run")
        self.assertEqual(code, 0, err)
        self.assertIn("TEST-5 created", out)
        fields = self.sent("POST", "issue")[0]["body"]["fields"]
        self.assertEqual(fields["issuetype"], {"id": "1"})
        self.assertEqual(fields["project"], {"key": "TEST"})
        self.assertEqual(fields["description"], "\\[LADO: developer\\]\n\nh2. Steps\n# run")
        self.assertEqual(fields["labels"], ["lado", "agent made"])
        self.assertEqual(fields["customfield_10100"], "TEST-9")

    def test_create_wiki_description_is_not_converted(self):
        self.route_createmeta()
        code, _, err = self.run_jira("create", "--type", "Bug", "--summary", "x", "--wiki",
                                     "--description", "**as is**")
        self.assertEqual(code, 0, err)
        fields = self.sent("POST", "issue")[0]["body"]["fields"]
        self.assertEqual(fields["description"], "\\[LADO: developer\\]\n\n**as is**")

    def test_marked_description_through_field(self):
        self.route_createmeta()
        code, _, err = self.run_jira("create", "--type", "Bug", "--summary", "x",
                                     "--field", "description=by **field**")
        self.assertEqual(code, 0, err)
        fields = self.sent("POST", "issue")[0]["body"]["fields"]
        self.assertEqual(fields["description"], "\\[LADO: developer\\]\n\nby **field**")

    def test_reporter_is_left_to_jira(self):
        self.route_createmeta(required=["reporter"])
        code, _, err = self.run_jira("create", "--type", "Bug", "--summary", "x")
        self.assertEqual(code, 0, err)
        self.assertNotIn("reporter", self.sent("POST", "issue")[0]["body"]["fields"])

    def test_create_names_required_fields(self):
        self.route_createmeta(required=["components"])
        code, _, err = self.run_jira("create", "--type", "Bug", "--summary", "Crash")
        self.assertEqual(code, jira.FIELDS_REQUIRED)
        self.assertIn("Components (components)", err)
        self.assertNotIn("Reporter", err)
        self.assertEqual(self.sent("POST", "issue"), [])
        code, _, err = self.run_jira("create", "--type", "Bug", "--summary", "Crash",
                                     "--field", 'components=[{"name": "UI"}]')
        self.assertEqual(code, 0, err)
        fields = self.sent("POST", "issue")[0]["body"]["fields"]
        self.assertEqual(fields["components"], [{"name": "UI"}])
        self.assertEqual(fields["description"], "\\[LADO: developer\\]")

    def test_create_epic_without_name_points_to_epic_name(self):
        self.route_createmeta()
        self.jira.route("GET", "issue/createmeta/TEST/issuetypes/10000", {"values": [
            {"fieldId": "customfield_10101", "name": "Epic Name", "required": True},
            {"fieldId": "components", "name": "Components", "required": True}]})
        code, _, err = self.run_jira("create", "--type", "epic", "--summary", "Login")
        self.assertEqual(code, jira.FIELDS_REQUIRED)
        self.assertIn("creating Epic in TEST needs", err)
        self.assertIn("Epic Name (customfield_10101): give it with --epic-name '<name>'",
                      err)
        self.assertIn("Components (components): give it with --field id=value", err)
        self.assertEqual(self.sent("POST", "issue"), [])

    def test_create_epic_name_of_another_field_points_to_field(self):
        for config in ("project: TEST\nissue_types:\n  epic: Epic\n",
                       CONFIG.replace("customfield_10101", "customfield_10999")):
            with self.subTest(config=config):
                self.write_config(config)
                self.route_createmeta()
                self.jira.route("GET", "issue/createmeta/TEST/issuetypes/10000", {
                    "values": [{"fieldId": "customfield_10101", "name": "Epic Name",
                                "required": True}]})
                code, _, err = self.run_jira("create", "--type", "epic", "--summary", "x")
                self.assertEqual(code, jira.FIELDS_REQUIRED)
                self.assertIn("Epic Name (customfield_10101): give it with "
                              "--field customfield_10101=<name>", err)
                self.assertNotIn("--epic-name", err)

    def test_create_epic_needs_its_setting(self):
        self.write_config("project: TEST\n")
        self.route_createmeta()
        code, _, err = self.run_jira("create", "--type", "Bug", "--summary", "x",
                                     "--epic", "TEST-9")
        self.assertEqual(code, jira.CONFIG)
        self.assertIn("'fields.epic_link'", err)

    def test_create_unknown_type_lists_types(self):
        self.route_createmeta()
        code, _, err = self.run_jira("create", "--type", "Story", "--summary", "x")
        self.assertEqual(code, jira.REFUSED)
        self.assertIn("its types: Bug, Epic", err)

    def test_create_needs_the_config(self):
        os.remove(os.path.join(self.repo, ".lado", "tracker.yaml"))
        code, _, err = self.run_jira("create", "--type", "Bug", "--summary", "x")
        self.assertEqual(code, jira.CONFIG)
        self.assertIn(".lado/tracker.yaml not found", err)
        self.assertEqual(self.jira.requests, [])

    def route_transitions(self, required=False):
        fields = {"comment": {"name": "Comment", "required": False}}
        if required:
            fields["resolution"] = {"name": "Resolution", "required": True}
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1",
                                                "fields": {"status": {"name": "In Progress"}}})
        self.jira.route("GET", "issue/TEST-1/transitions", {"transitions": [
            {"id": "21", "name": "Send to review", "to": {"name": "Code Review"},
             "fields": {}},
            {"id": "31", "name": "Close", "to": {"name": "Done"}, "fields": fields}]})
        self.jira.route("POST", "issue/TEST-1/transitions", None, status=204)

    def test_transition_lists_without_target(self):
        self.route_transitions()
        code, out, err = self.run_jira("transition", "TEST-1")
        self.assertEqual(code, 0, err)
        self.assertIn("21: Send to review -> Code Review", out)
        self.assertEqual(self.sent("POST", "issue/TEST-1/transitions"), [])

    def test_transition_comment_on_its_screen(self):
        self.route_transitions()
        code, out, err = self.run_jira("transition", "TEST-1", "done",
                                       "--comment", "**Ready.**")
        self.assertEqual(code, 0, err)
        self.assertIn("TEST-1: In Progress -> Done, comment added", out)
        body = self.sent("POST", "issue/TEST-1/transitions")[0]["body"]
        self.assertEqual(body["transition"], {"id": "31"})
        self.assertEqual(body["update"]["comment"][0]["add"]["body"],
                         "\\[LADO: developer\\]\n\n*Ready.*")
        self.assertEqual(self.sent("POST", "issue/TEST-1/comment"), [])

    def test_transition_without_comment_field_posts_the_comment_after(self):
        self.route_transitions()
        self.jira.route("POST", "issue/TEST-1/comment", {"id": "100"}, status=201)
        code, out, err = self.run_jira("transition", "TEST-1", "review",
                                       "--comment", "**Ready.**")
        self.assertEqual(code, 0, err)
        self.assertIn("TEST-1: In Progress -> Code Review, comment 100 added", out)
        body = self.sent("POST", "issue/TEST-1/transitions")[0]["body"]
        self.assertEqual(body, {"transition": {"id": "21"}})
        self.assertEqual(self.sent("POST", "issue/TEST-1/comment")[0]["body"]["body"],
                         "\\[LADO: developer\\]\n\n*Ready.*")
        self.run_jira("transition", "TEST-1", "review", "--wiki", "--comment", "**as is**")
        self.assertEqual(self.sent("POST", "issue/TEST-1/comment")[1]["body"]["body"],
                         "\\[LADO: developer\\]\n\n**as is**")

    def test_transition_done_but_comment_failed_says_so(self):
        self.route_transitions()
        self.jira.route("POST", "issue/TEST-1/comment",
                        {"errors": {"comment": "Too long"}}, status=400)
        code, out, err = self.run_jira("transition", "TEST-1", "review", "--comment", "x")
        self.assertEqual(code, jira.REFUSED)
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertIn("In Progress -> Code Review done, but the comment was not added", err)
        self.assertIn("do not run the transition again", err)
        self.assertEqual(len(self.sent("POST", "issue/TEST-1/transitions")), 1)

    def test_transition_done_but_comment_unanswered_says_check_first(self):
        self.route_transitions()
        self.jira.route("POST", "issue/TEST-1/comment", None, status=504)
        code, _, err = self.run_jira("transition", "TEST-1", "review", "--comment", "x")
        self.assertEqual(code, jira.SERVER_ERROR)
        self.assertIn("done, but the comment may not have been added", err)
        self.assertIn("(do not run the transition again; check with get, then send the "
                      "comment", err)
        self.jira.route("POST", "issue/TEST-1/comment", None, status=429)
        code, _, err = self.run_jira("transition", "TEST-1", "review", "--comment", "x")
        self.assertIn("done, but the comment was not added", err)
        self.assertIn("report it; send the comment with comment once you are told to", err)

    def test_transition_done_but_comment_unreachable_waits_first(self):
        self.route_transitions()
        event = threading.Event()
        self.addCleanup(event.set)
        handler = self.jira.server.RequestHandlerClass
        posts = handler.do_POST
        handler.do_POST = lambda request: (
            event.wait(5) if request.path.endswith("/comment") else posts(request))
        self.addCleanup(setattr, handler, "do_POST", posts)
        with mock.patch.object(jira, "TIMEOUT", 0.3):
            code, _, err = self.run_jira("transition", "TEST-1", "review", "--comment", "x")
        self.assertEqual(code, jira.UNREACHABLE, err)
        self.assertIn("the comment may not have been added", err)
        self.assertIn("once you are told Jira answers again, check with get", err)

    def test_transition_names_required_fields(self):
        self.route_transitions(required=True)
        code, _, err = self.run_jira("transition", "TEST-1", "done")
        self.assertEqual(code, jira.FIELDS_REQUIRED)
        self.assertIn("Resolution (resolution)", err)
        self.assertEqual(self.sent("POST", "issue/TEST-1/transitions"), [])
        code, _, err = self.run_jira("transition", "TEST-1", "Close",
                                     "--resolution", "Fixed")
        self.assertEqual(code, 0, err)
        body = self.sent("POST", "issue/TEST-1/transitions")[0]["body"]
        self.assertEqual(body["fields"], {"resolution": {"name": "Fixed"}})

    def test_transition_required_comment_is_given_by_comment(self):
        self.route_transitions()
        self.jira.route("GET", "issue/TEST-1/transitions", {"transitions": [
            {"id": "31", "name": "Close", "to": {"name": "Done"},
             "fields": {"comment": {"name": "Comment", "required": True}}}]})
        code, _, err = self.run_jira("transition", "TEST-1", "done")
        self.assertEqual(code, jira.FIELDS_REQUIRED)
        self.assertIn("--comment", err)
        self.jira.route("GET", "issue/TEST-1/comment", {"comments": [
            {"id": "200", "body": "\\[LADO: developer\\]\r\n\r\nwhy"},
            {"id": "201", "body": "another"}]})
        code, out, err = self.run_jira("transition", "TEST-1", "done", "--comment", "why")
        self.assertEqual(code, 0, err)
        self.assertIn("-> Done, comment 200 added", out)
        body = self.sent("POST", "issue/TEST-1/transitions")[0]["body"]
        self.assertNotIn("fields", body)
        self.assertEqual(body["update"]["comment"][0]["add"]["body"],
                         "\\[LADO: developer\\]\n\nwhy")

    def test_transition_not_available_lists_the_others(self):
        self.route_transitions()
        code, _, err = self.run_jira("transition", "TEST-1", "Reopen")
        self.assertEqual(code, jira.REFUSED)
        self.assertIn("not available from In Progress", err)
        self.assertIn("31: Close -> Done", err)

    def test_transition_already_there(self):
        self.route_transitions()
        code, out, _ = self.run_jira("transition", "TEST-1", "In Progress")
        self.assertEqual(code, 0)
        self.assertIn("already in In Progress", out)
        self.assertEqual(self.sent("POST", "issue/TEST-1/comment"), [])

    def test_transition_already_there_still_posts_the_comment(self):
        self.route_transitions()
        self.jira.route("POST", "issue/TEST-1/comment", {"id": "100"}, status=201)
        code, out, err = self.run_jira("transition", "TEST-1", "In Progress",
                                       "--comment", "**Ready.**")
        self.assertEqual(code, 0, err)
        self.assertIn("already in In Progress, comment 100 added", out)
        self.assertEqual(self.sent("POST", "issue/TEST-1/comment")[0]["body"]["body"],
                         "\\[LADO: developer\\]\n\n*Ready.*")
        self.assertEqual(self.sent("POST", "issue/TEST-1/transitions"), [])

    def test_transition_already_there_refuses_resolution_and_fields(self):
        self.route_transitions()
        for extra in (["--resolution", "Fixed"], ["--field", "x=1"]):
            code, out, err = self.run_jira("transition", "TEST-1", "In Progress",
                                           "--comment", "x", *extra)
            self.assertEqual(code, jira.REFUSED, err)
            self.assertIn("already in In Progress: --resolution and --field were not "
                          "applied, and no comment was posted", err)
        self.assertEqual([r for r in self.jira.requests if r["method"] != "GET"], [])

    def route_assignee(self, name):
        assignee = {"name": name, "displayName": "Someone"} if name else None
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1",
                                                "fields": {"assignee": assignee}})
        self.jira.route("PUT", "issue/TEST-1/assignee", None, status=204)

    def test_assign(self):
        self.route_assignee(None)
        code, out, err = self.run_jira("assign", "TEST-1", "bob")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "TEST-1: assignee unassigned -> bob\n")
        self.assertEqual(self.sent("PUT", "issue/TEST-1/assignee")[0]["body"], {"name": "bob"})
        code, out, err = self.run_jira("assign", "TEST-1", "me")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "TEST-1: assignee unassigned -> agent.user\n")
        self.assertEqual(self.sent("PUT", "issue/TEST-1/assignee")[1]["body"],
                         {"name": "agent.user"})
        self.route_assignee("Agent.User")
        code, out, err = self.run_jira("assign", "TEST-1", "bob")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "TEST-1: assignee Agent.User -> bob\n")

    def test_assign_refuses_a_task_held_by_another_account(self):
        self.route_assignee("ann")
        for user in ("me", "bob", "none"):
            code, out, err = self.run_jira("assign", "TEST-1", user)
            self.assertEqual(code, jira.REFUSED, err)
            self.assertIn("TEST-1 is assigned to Someone (ann), another account: not "
                          "changed", err)
            self.assertIn("--reassign", err)
            self.assertEqual(out, "")
        self.assertEqual(self.sent("PUT", "issue/TEST-1/assignee"), [])

    def test_assign_reassign_takes_it_from_another_account(self):
        self.route_assignee("ann")
        code, out, err = self.run_jira("assign", "TEST-1", "me", "--reassign")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "TEST-1: assignee ann -> agent.user\n")
        self.assertEqual(self.sent("PUT", "issue/TEST-1/assignee")[0]["body"],
                         {"name": "agent.user"})

    def test_unassign(self):
        self.route_assignee("agent.user")
        code, out, err = self.run_jira("assign", "TEST-1", "none")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "TEST-1: assignee agent.user -> unassigned\n")
        self.assertEqual(self.sent("PUT", "issue/TEST-1/assignee")[0]["body"], {"name": None})

    def test_assign_already_so_changes_nothing(self):
        for name, user, shown in [("Agent.User", "me", "Agent.User"), ("ann", "ANN", "ann"),
                                  (None, "none", "unassigned")]:
            self.route_assignee(name)
            code, out, err = self.run_jira("assign", "TEST-1", user)
            self.assertEqual(code, 0, err)
            self.assertEqual(out, "TEST-1: assignee %s already, nothing changed\n" % shown)
        self.assertEqual(self.sent("PUT", "issue/TEST-1/assignee"), [])

    def route_labels(self, *labels):
        self.jira.route("GET", "issue/TEST-1", Seq(*[
            {"key": "TEST-1", "fields": {"labels": list(each)}} for each in labels]))
        self.jira.route("PUT", "issue/TEST-1", None, status=204)

    def test_label_add_and_remove(self):
        self.route_labels(["lado", "old"], ["lado", "waiting_for_release"])
        code, out, err = self.run_jira("label", "TEST-1", "--add", "waiting_for_release",
                                       "lado", "--remove", "old", "absent")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "TEST-1: labels lado, waiting_for_release\n")
        self.assertEqual(self.sent("PUT", "issue/TEST-1")[0]["body"], {"update": {
            "labels": [{"add": "waiting_for_release"}, {"remove": "old"}]}})

    def test_label_remove_the_last(self):
        self.route_labels(["old"], [])
        code, out, err = self.run_jira("label", "TEST-1", "--remove", "old")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "TEST-1: labels none\n")

    def test_label_already_so_changes_nothing(self):
        self.route_labels(["lado"])
        code, out, err = self.run_jira("label", "TEST-1", "--add", "lado", "--remove", "x")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "TEST-1: labels lado, nothing changed\n")
        self.assertEqual(self.sent("PUT", "issue/TEST-1"), [])

    def test_label_with_a_space_or_none_is_refused_before_any_request(self):
        for argv in (["--add", "waiting for release"], ["--remove", "a b"], []):
            code, _, err = self.run_jira("label", "TEST-1", *argv)
            self.assertEqual(code, jira.USAGE, err)
        self.assertEqual(self.jira.requests, [])

    def test_comment_marked_only_for_an_agent(self):
        self.jira.route("POST", "issue/TEST-1/comment", {"id": "100"}, status=201)
        code, out, err = self.run_jira("comment", "TEST-1", "**Done**: see [PR](http://x)")
        self.assertEqual(code, 0, err)
        self.assertIn("comment 100 added", out)
        self.assertEqual(self.sent("POST", "issue/TEST-1/comment")[0]["body"]["body"],
                         "\\[LADO: developer\\]\n\n*Done*: see [PR|http://x]")
        with mock.patch.dict(os.environ, {"LADO_AGENT": ""}):
            self.run_jira("comment", "TEST-1", "by hand")
        self.assertEqual(self.sent("POST", "issue/TEST-1/comment")[1]["body"]["body"],
                         "by hand")

    def test_comment_wiki_is_sent_as_it_is(self):
        self.jira.route("POST", "issue/TEST-1/comment", {"id": "1"}, status=201)
        code, _, err = self.run_jira("comment", "TEST-1", "--wiki", "-",
                                     stdin="{panel}\n**x**\n{panel}\n")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.sent("POST", "issue/TEST-1/comment")[0]["body"]["body"],
                         "\\[LADO: developer\\]\n\n{panel}\n**x**\n{panel}\n")

    def test_comment_works_without_config(self):
        os.remove(os.path.join(self.repo, ".lado", "tracker.yaml"))
        self.jira.route("POST", "issue/TEST-1/comment", {"id": "1"}, status=201)
        code, _, err = self.run_jira("comment", "TEST-1", "x")
        self.assertEqual(code, 0, err)

    def test_empty_text_is_refused(self):
        code, _, err = self.run_jira("comment", "TEST-1", "-", stdin="  \n")
        self.assertEqual(code, jira.USAGE)
        self.assertEqual(self.jira.requests, [])

    def test_link(self):
        self.jira.route("POST", "issue/TEST-1/remotelink", {"id": 7}, status=201)
        url = "https://git.example/repo/commit/abc"
        code, out, err = self.run_jira("link", "TEST-1", url, "--title", "commit abc")
        self.assertEqual(code, 0, err)
        body = self.sent("POST", "issue/TEST-1/remotelink")[0]["body"]
        self.assertEqual(body, {"globalId": url,
                                "object": {"url": url, "title": "commit abc"}})


class ErrorsTest(JiraTestCase):
    def assertFails(self, code, text, *argv):
        got, out, err = self.run_jira(*(argv or ("get", "TEST-1")))
        self.assertEqual(got, code, err)
        self.assertIn(text, err)
        self.assertEqual(len(err.strip().splitlines()), 1)
        return err

    def test_not_found(self):
        self.assertFails(jira.NOT_FOUND, "task TEST-1 not found")

    def test_no_access(self):
        self.jira.route("POST", "issue/TEST-1/comment",
                        {"errorMessages": ["You do not have the permission"]}, status=403)
        self.assertFails(jira.NO_ACCESS, "no access (403)", "comment", "TEST-1", "x")

    def test_no_access_to_assign_or_label(self):
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1", "fields": {
            "assignee": None, "labels": []}})
        denied = {"errorMessages": ["You do not have permission to assign issues."]}
        self.jira.route("PUT", "issue/TEST-1/assignee", denied, status=403)
        self.assertFails(jira.NO_ACCESS, "no access (403)", "assign", "TEST-1", "me")
        self.jira.route("PUT", "issue/TEST-1", denied, status=403)
        self.assertFails(jira.NO_ACCESS, "no access (403)", "label", "TEST-1", "--add", "x")

    def test_assign_without_permission_is_not_a_credentials_failure(self):
        # Jira's documented answer to assigning without the permission is 401.
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1", "fields": {"assignee": None}})
        self.jira.route("PUT", "issue/TEST-1/assignee", None, status=401)
        self.assertFails(jira.NO_ACCESS, "no permission to assign TEST-1 (401)",
                         "assign", "TEST-1", "me")
        self.jira.route("PUT", "issue/TEST-1/assignee", None, status=401, headers={
            "X-Authentication-Denied-Reason": "CAPTCHA_CHALLENGE; login-url=/login.jsp"})
        self.assertFails(jira.CREDENTIALS_REFUSED, "CAPTCHA", "assign", "TEST-1", "me")

    def test_assign_unknown_user_answered_404(self):
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1", "fields": {"assignee": None}})
        self.jira.route("PUT", "issue/TEST-1/assignee",
                        {"errorMessages": ["User 'nobody' does not exist."]}, status=404)
        self.assertFails(jira.REFUSED, "Jira refused to assign TEST-1 to nobody: no such user",
                         "assign", "TEST-1", "nobody")

    def test_unassign_refused_names_the_reason(self):
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1", "fields": {
            "assignee": {"name": "agent.user"}}})
        self.jira.route("PUT", "issue/TEST-1/assignee",
                        {"errors": {"assignee": "Issues must be assigned."}}, status=400)
        err = self.assertFails(jira.REFUSED, "Jira refused to unassign TEST-1: Jira refused "
                               "the values: assignee (Issues must be assigned.)",
                               "assign", "TEST-1", "none")
        self.assertNotIn("no such user", err)

    def test_unassign_answered_404_is_not_an_unknown_user(self):
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1", "fields": {
            "assignee": {"name": "agent.user"}}})
        self.jira.route("PUT", "issue/TEST-1/assignee",
                        {"errorMessages": ["Issue Does Not Exist"]}, status=404)
        err = self.assertFails(jira.NOT_FOUND, "task TEST-1 not found",
                               "assign", "TEST-1", "none")
        self.assertNotIn("no such user", err)

    def test_assign_answer_not_from_jira_is_not_an_unknown_user(self):
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1", "fields": {"assignee": None}})
        self.jira.route("PUT", "issue/TEST-1/assignee", Raw(b"<html>Not Found</html>"),
                        status=404)
        err = self.assertFails(jira.SETUP, "JIRA_URL is not Jira's base address",
                               "assign", "TEST-1", "bob")
        self.assertNotIn("no such user", err)

    def test_assign_unknown_user(self):
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1", "fields": {"assignee": None}})
        self.jira.route("PUT", "issue/TEST-1/assignee",
                        {"errors": {"assignee": "User 'nobody' does not exist."}}, status=400)
        self.assertFails(jira.REFUSED, "Jira refused to assign TEST-1 to nobody: no such user",
                         "assign", "TEST-1", "nobody")

    def test_unset_credentials_are_named(self):
        with mock.patch.dict(os.environ, {"JIRA_PASSWORD": "", "JIRA_URL": ""}):
            err = self.assertFails(jira.SETUP, "JIRA_URL, JIRA_PASSWORD not set")
        self.assertEqual(self.jira.requests, [])

    def test_refused_credentials_are_not_retried(self):
        self.jira.route("GET", "issue/TEST-1", None, status=401,
                        headers={"X-Seraph-LoginReason": "AUTHENTICATED_FAILED"})
        err = self.assertFails(jira.CREDENTIALS_REFUSED, "refused the credentials (401)")
        self.assertIn("the lead tells every agent to stop using Jira", err)
        self.assertEqual(len(self.jira.requests), 1)

    def test_captcha(self):
        self.jira.route("GET", "issue/TEST-1", None, status=403, headers={
            "X-Authentication-Denied-Reason": "CAPTCHA_CHALLENGE; login-url=/login.jsp"})
        err = self.assertFails(jira.CREDENTIALS_REFUSED, "logs in to Jira in a browser")
        self.assertIn("the lead tells every agent to stop using Jira", err)
        self.assertEqual(len(self.jira.requests), 1)

    def test_bad_jql(self):
        self.jira.route("GET", "search", {"errorMessages": ["The field 'x' does not exist"]},
                        status=400)
        self.assertFails(jira.REFUSED, "does not exist", "search", "x = 1")

    def test_field_errors_on_create(self):
        self.jira.route("GET", "issue/createmeta/TEST/issuetypes",
                        {"values": [{"id": "1", "name": "Bug"}]})
        self.jira.route("GET", "issue/createmeta/TEST/issuetypes/1", {"values": []})
        self.jira.route("POST", "issue", {"errors": {"priority": "Priority is required."}},
                        status=400)
        self.assertFails(jira.FIELDS_REQUIRED, "needs the fields: priority (Priority is "
                         "required.)", "create", "--type", "Bug", "--summary", "x")

    def test_refused_values_are_not_missing_fields(self):
        self.jira.route("GET", "issue/createmeta/TEST/issuetypes",
                        {"values": [{"id": "1", "name": "Bug"}]})
        self.jira.route("GET", "issue/createmeta/TEST/issuetypes/1", {"values": []})
        self.jira.route("POST", "issue", {"errors": {
            "customfield_10100": "Epic TEST-0 does not exist."}}, status=400)
        self.assertFails(jira.REFUSED, "refused the values: customfield_10100",
                         "create", "--type", "Bug", "--summary", "x", "--epic", "TEST-0")

    def test_url_must_be_https(self):
        for url in ("http://jira.example.com", "ftp://jira.example.com"):
            with self.subTest(url=url), mock.patch.dict(os.environ, {"JIRA_URL": url}):
                self.assertFails(jira.SETUP, "must be Jira's https://")
        for url in ("jira.example.com", "https://", "https://jira.example.com:abc",
                    "https://[::1"):
            with self.subTest(url=url), mock.patch.dict(os.environ, {"JIRA_URL": url}):
                self.assertFails(jira.SETUP, "not a valid address")
        self.assertEqual(self.jira.requests, [])

    def test_answer_that_is_not_jira(self):
        self.jira.route("GET", "issue/TEST-1", Raw(b"<html>Not Found</html>"), status=404)
        self.assertFails(jira.SETUP, "JIRA_URL is not Jira's base address")
        self.jira.route("GET", "issue/TEST-1", Raw(b"<html>login</html>"))
        self.assertFails(jira.SETUP, "JIRA_URL is not Jira's base address")

    def test_broken_answer(self):
        self.jira.route("GET", "issue/TEST-1", Raw(b'{"key"', length=100))
        self.assertFails(jira.UNREACHABLE, "IncompleteRead")

    def test_no_answer_to_a_write_says_check_first(self):
        event = threading.Event()
        self.addCleanup(event.set)
        handler = self.jira.server.RequestHandlerClass
        handler.do_POST = lambda request: event.wait(5)
        with mock.patch.object(jira, "TIMEOUT", 0.3):
            err = self.assertFails(jira.UNREACHABLE, "may have been applied",
                                   "comment", "TEST-1", "x")
        self.assertIn("once Jira answers again, check with get or search", err)

    def test_server_error(self):
        self.jira.route("GET", "issue/TEST-1", None, status=500)
        self.assertFails(jira.SERVER_ERROR, "Jira failed (500)")
        self.assertNotIn("may have been applied", self.assertFails(
            jira.SERVER_ERROR, "Jira failed (500)"))

    def test_rate_limit_is_reported_not_retried(self):
        self.jira.route("POST", "issue/TEST-1/comment", None, status=429)
        err = self.assertFails(jira.SERVER_ERROR, "rate limiting requests (429)",
                               "comment", "TEST-1", "x")
        self.assertIn("do not retry", err)
        self.assertNotIn("may have been applied", err)
        self.assertEqual(len(self.jira.requests), 1)

    def test_server_error_after_a_write_says_check_first(self):
        self.jira.route("POST", "issue/TEST-1/comment", None, status=504)
        err = self.assertFails(jira.SERVER_ERROR, "may have been applied",
                               "comment", "TEST-1", "x")
        self.assertIn("check with get or search before running it again", err)
        self.assertNotIn("once Jira answers again", err)

    def test_unreadable_ssl_cert_file(self):
        with mock.patch.dict(os.environ, {"SSL_CERT_FILE": "/nonexistent/ca.pem"}):
            self.assertFails(jira.TLS, "SSL_CERT_FILE (/nonexistent/ca.pem) cannot be read")
        self.assertEqual(self.jira.requests, [])

    def test_field_errors_on_comment_and_link_are_refusals(self):
        self.jira.route("POST", "issue/TEST-1/remotelink", {"errors": {"url": "Invalid URL"}},
                        status=400)
        self.assertFails(jira.REFUSED, "refused the values: url (Invalid URL)",
                         "link", "TEST-1", "not a url")
        self.jira.route("POST", "issue/TEST-1/comment", {"errors": {"comment": "Too long"}},
                        status=400)
        self.assertFails(jira.REFUSED, "refused the values", "comment", "TEST-1", "x")

    def test_redirect_is_not_followed(self):
        self.jira.route("GET", "issue/TEST-1", None, status=302,
                        headers={"Location": "http://127.0.0.1:1/sso"})
        self.assertFails(jira.SETUP, "redirect (302), not followed")
        self.assertEqual(len(self.jira.requests), 1)

    def test_unreachable(self):
        self.jira.close()
        err = self.assertFails(jira.UNREACHABLE, "VPN")
        self.assertIn("send Jira nothing more until you are told it answers again", err)

    def test_timeout(self):
        event = threading.Event()
        self.addCleanup(event.set)
        handler = self.jira.server.RequestHandlerClass
        handler.do_GET = lambda request: event.wait(5)
        with mock.patch.object(jira, "TIMEOUT", 0.3):
            err = self.assertFails(jira.UNREACHABLE, "did not answer")
        self.assertIn("send Jira nothing more", err)
        self.assertNotIn("may have been applied", err)

    def test_invalid_config(self):
        self.write_config("project: TEST\nlabels:\n  - lado\n")
        err = self.assertFails(jira.CONFIG, "line 3: block lists",
                               "create", "--type", "Bug", "--summary", "x")
        self.assertIn("tracker.yaml", err)
        self.assertEqual(self.jira.requests, [])


@unittest.skipUnless(shutil.which("openssl"), "needs the openssl command")
class TlsTest(JiraTestCase):
    def setUp(self):
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        self.cert = os.path.join(folder, "cert.pem")
        key = os.path.join(folder, "key.pem")
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                        "-keyout", key, "-out", self.cert, "-days", "2",
                        "-subj", "/CN=127.0.0.1",
                        "-addext", "subjectAltName=IP:127.0.0.1"],
                       check=True, capture_output=True)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.cert, key)
        super().setUp()
        self.jira.close()
        self.jira = FakeJira(tls_context=context)
        self.addCleanup(self.jira.close)
        os.environ["JIRA_URL"] = self.jira.url

    def test_untrusted_certificate(self):
        with mock.patch.dict(os.environ, {"SSL_CERT_FILE": ""}):
            code, _, err = self.run_jira("get", "TEST-1")
        self.assertEqual(code, jira.TLS, err)
        self.assertIn("SSL_CERT_FILE", err)

    def test_trusted_through_ssl_cert_file(self):
        self.jira.route("GET", "issue/TEST-1", {"key": "TEST-1", "fields": {}})
        with mock.patch.dict(os.environ, {"SSL_CERT_FILE": self.cert}):
            code, out, err = self.run_jira("get", "TEST-1")
        self.assertEqual(code, 0, err)
        self.assertIn("TEST-1", out)


if __name__ == "__main__":
    unittest.main()
