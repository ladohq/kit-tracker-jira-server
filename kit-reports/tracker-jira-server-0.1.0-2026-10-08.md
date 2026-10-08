# Kit report: tracker-jira-server 0.1.0

- Date: 2026-10-08
- Kit: `.` (the run's worktree of `create/tracker-jira-server`), path given
- Commit: b245615
- Evaluated by: kit-builder critic (layers a and b)
- Mode: full (first evaluation in `create`; no previous report)
- Passes: three independent sub-agents, each with the rubric, `lado-kit-format` and the
  kit folder only, starting from kit.yaml + BLUEPRINT.md (pass 1), from `jira.py` (pass 2),
  and from README.md + SKILL.md read as a worker of a process kit (pass 3). The kit has no
  dependency skills. 9 one-pass findings: 5 kept as confirmed, 4 dropped. The dropped
  ones are task text as untrusted input, the key of a created task in the step's note,
  the repository name `lado-kit-*` (the task sets it), and a Jira behaviour that cannot be
  confirmed offline: createmeta marking `reporter` as required. That last one is under
  "Questions for the human" as a trial check.

Findings are candidates for the human to weigh, not a pass/fail grade.

## Card

| Layer | Result |
|---|---|
| a. `lado kits check` | OK; 0 warnings |
| a. Budget | green; no yellow or red measure |
| a. Flows | 0 drawn (the kit has no flows); `--compare` not applicable, see "Flows" |
| b. Rubric | 12 findings (2 high, 6 medium, 4 low); 6 of 12 criteria without findings |
| Covers | full evaluation of the whole kit, 5 files (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); tests/test_jira.py read and run (36 tests, OK) |

The count covers only what the row "Covers" names: a count of a re-evaluation and one of a
full evaluation are not comparable.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

### Budget script (exit status 0)

```
# Complexity budget: tracker-jira-server 0.1.0

| Measure | Where | Value | Green / yellow up to | Zone |
|---|---|---|---|---|
| Worker roles (not supervisor) | kit | 0 | 3 / 5 | green |
| Work steps in a flow | no flows | 0 | 5 / 8 | green |
| Gates in a flow | no flows | 0 | 2 / 3 | green |
| Words in a role prompt | no roles | 0 | 800 / 1500 | green |
| Words in the lead's prompt | no lead role | 0 | 1000 / 1500 | green |
| Own skills | kit | 1 | 5 / 10 | green |
| MCP servers | kit | 0 | 2 / 4 | green |

## Similar paragraphs (one rule, one place; 55% similar or more)

none

Overall: green
```

### Flows

The kit has no flows and BLUEPRINT.md has no skeletons (R2, section 2: "Flow skeletons:
none"), so there is nothing to draw or compare. The flow script fails on a flowless kit.
That is a fault of the script, not of the kit (see "Found on the way"); the supervisor
ruled the compare not applicable (#601).

```
$ flow_diagram.py . --out kit-reports/tracker-jira-server-0.1.0-2026-10-08
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
$ flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Fix first

1. Say in SKILL.md whom "tell the user" / "ask" means for a worker: the supervisor via
   `send_message`. The lead tells the human. (F7.1)
2. Add one scope line to SKILL.md: read freely; create, transition, comment or link only
   when your role, your step or the human asks for it. (F12.1)
3. Refuse a `JIRA_URL` that is not `https://`, and catch the exceptions that now escape
   as a traceback with exit 1. (F12.2, F3.3)
4. Split exit 8 ("needs fields") from "refused field values", and name a wrong
   `JIRA_URL` (redirect, non-JSON) as an environment fault, not a request to fix. (F3.1,
   F3.2)

## Findings

### 1. Role boundaries

Not applicable: the kit has no roles. The skill states its own limits on credentials and
settings: "never ask for them, print them or put them in a file" (SKILL.md:20); "Read it
when you need the project's words; the user changes it, not you." (SKILL.md:91). Write
rights in Jira: F12.1.

### 2. Handoffs between steps

Not applicable: no flows, no `produces` or `reads`. The script's output is stdout plus
one stderr line per failure.

### 3. Done and outcomes

- **F3.1** [medium] `skills/tracker/jira.py:302`
  > if fields:
  Every 4xx answer that carries an `errors` map becomes exit 8 "Jira refused the fields".
  That includes an invalid value (a wrong epic key, an unknown priority) and "Field
  'resolution' cannot be set. It is not on the appropriate screen". SKILL.md:106 reads
  exit 8 as "Jira needs fields (named) | give them and run again", so the agent adds
  fields where it should remove or correct one.
  Fix: send only errors for fields missing from the request to `FIELDS_REQUIRED`, and the
  rest to `REFUSED` (11). Or reword row 8 as "Jira refused or needs the named fields: add
  the missing ones, correct or remove the refused ones; once, then ask". Passes: 2/3
  (medium in both).

- **F3.2** [medium] `skills/tracker/SKILL.md:109`
  > | 11 | Jira refused the request (bad JQL, unknown type, transition not open) | read the line, fix the request once; if it still fails, ask |
  Exit 11 also covers a wrong `JIRA_URL`: a redirect (`jira.py:297` `return
  Failure(REFUSED, "Jira answered with a redirect (%d), not followed: set "`) and a
  non-JSON answer (`jira.py:253`). A URL without Jira's context path gives 404, which
  becomes exit 7 "task … not found: check the key". The agent then "fixes the request"
  or chases the key, when only the user can fix the environment (known hole 1).
  Fix: give the redirect and non-JSON cases their own code (for example 13 "JIRA_URL
  wrong or SSO: tell, do not retry"), or say in rows 7 and 11: "if the line names
  JIRA_URL, report it; do not change the request". Passes: 2/3 (medium in both).

- **F3.3** [medium] `skills/tracker/jira.py:585`
  > except Failure as failure:
  `main()` catches only `Failure`. A `JIRA_URL` without a scheme raises at `jira.py:234`
  (`request = urllib.request.Request(url, data=data, method=method)`, outside the
  `try`). `http.client.HTTPException` (`IncompleteRead`, `BadStatusLine`) also escapes.
  The agent gets a traceback and exit 1, which the SKILL.md table does not list.
  Confirmed by running it: `JIRA_URL=jira.example.com … jira.py get X-1` →
  `ValueError: unknown url type: 'jira.example.com/rest/api/2/issue/X-1?…'`, exit 1.
  Fix: check `JIRA_URL` in `Jira.__init__` (see F12.2), catch `http.client.HTTPException`
  as `UNREACHABLE`, and add a row "1 | the script crashed | report its last line; do not
  repeat a write". Passes: 2/3 (medium, low → medium).

### 4. Independent verification

Not applicable: no flows and nothing merged by the kit. The script is checked by 36 offline
tests before the trial in the real Jira, which needs the human's yes (BLUEPRINT R10).

### 5. Contradictions

- **F5.1** [medium] `skills/tracker/jira.py:300`
  > return Failure(SERVER_ERROR, "Jira failed (%d)%s: try later or tell the user"
  The script's line says "try later", but SKILL.md:95 says "it never retries" and the
  row for 12 (SKILL.md:110) says "tell the user and go on without the tracker". "Go on
  without the tracker" also overrides a process step whose result is a Jira change: the
  step can end as if the task had moved. In the same way, the 403 line (`jira.py:291`)
  tells the agent to "ask the project's Jira admin for the permission", which no agent
  can do.
  Fix: make the script's hints say only what the table says (drop "try later" and "ask
  the … admin"); change row 12 to "report it (F7.1); whether your step can go on without
  the tracker is your step's decision". Passes: 2/3 (medium, low → medium).

### 6. Duplication

- **F6.1** [low] `README.md:51`
  > labels: [lado]                # added to every task the agents create
  The `.lado/tracker.yaml` example is written twice, in README.md:44-55 and
  SKILL.md:77-89, and the copies already differ. SKILL.md has `task: Task` and "your
  process"; the `fields:` comment is "different in each Jira" in one and "from
  $JIRA_URL/rest/api/2/field" in the other. The README's hint on where to find field ids
  is useful to agents too and is missing from SKILL.md.
  Fix: keep the full example in SKILL.md, with the `/rest/api/2/field` hint, and give
  the README a minimal example plus a pointer. Passes: 2/3 (low in both).

### 7. When to call the human

- **F7.1** [high] `skills/tracker/SKILL.md:103`
  > | 5 | credentials refused, or Jira wants a CAPTCHA | stop using Jira and tell the user: one more try can lock the login; after a CAPTCHA they log in once in a browser |
  The exit table sends exits 3, 4, 5, 6, 9, 10 and 12 to "the user" and exits 7, 8 and 11
  to "ask", without saying whom. The skill is listed by roles of process kits, most of
  them workers, and in LADO only the lead talks to the human. A worker will message the
  human past the lead, or say it in its own pane where nobody reads it. Row 9 adds "and
  wait" with no condition for going on, so the step stalls. On exit 5 only the agent that
  hit it stops; others in the session using the same login keep trying toward the CAPTCHA
  lock. This is known hole 5 (also criterion 5); impacts high, high, medium, taken high.
  Fix: one line above the table: "Tell the user / ask: as a worker, send the printed line
  and the command to the supervisor with `send_message` and wait for its answer; as the
  lead, tell the human. On exit 5 the lead tells every agent to stop using Jira until the
  human says it is fixed." Passes: 3/3.

### 8. Loops on a later visit

Not applicable: no flows. Repeats are bounded in the text: "it never retries"
(SKILL.md:95), "fix the request once; if it still fails, ask" (SKILL.md:109).

### 9. Concision and why

- **F9.1** [low] `skills/tracker/jira.py:450`
  > if transition_id:
  `_transitions` takes a `transition_id` that no caller passes (`grep -n "_transitions("`:
  lines 464 and 475, both `_transitions(jira, args.key)`), so this branch is dead code.
  Fix: remove the parameter and the branch. Passes: 1/3, confirmed (the grep above).

The rest is concise, and the non-obvious rules carry their reasons: the mark ("Whatever
you write in Jira appears in the user's name", SKILL.md:21-22), exit 5 ("one more try can
lock the login").

### 10. Skill descriptions

The description says what the skill holds and when to use it: "Use whenever your work
touches a task in the tracker, e.g. "file a bug", "take the task"…" (SKILL.md:6-7). The
kit has one skill, no `dependencies.skills` and no neighbour; the future
`tracker-jira-cloud` kit shares the name by design (R2), and two tracker kits in one
session are refused by LADO.

### 11. Provider neutrality

`python3 ${SKILL_DIR}/jira.py` with a neutral fallback: "If your CLI does not expand
`${SKILL_DIR}`, use the folder this SKILL.md is in." (SKILL.md:19). No CLI tool names, and
no absolute or home paths in the skill or the script. The macOS `security` line is in the
human-facing README, marked "On macOS".

### 12. Safety and scope

- **F12.1** [high] `skills/tracker/SKILL.md:6`
  > Use whenever your work touches a task in the tracker, e.g. "file a bug", "take the
  Create, transition, comment and link leave the machine and appear in the user's name in
  the corporate Jira, yet the skill invites any agent to do them whenever its work
  "touches a task". The only scope rule is in the README (README.md:64: "The kit sets no
  limits on what agents do in Jira; a process kit"), which agents do not read. A role
  that lists the skill without its own rules may close or comment on tasks unasked
  (known hole 2). The blueprint leaves the *limits* (deletes, closing, others' tasks) to
  the trial, but that does not settle whether a write needs an ask at all. Impacts
  medium, high, medium, taken high.
  Fix: one line in SKILL.md: "Reading is always fine; create, transition, comment or link
  only when your role, your step or the human asks for it, and only on the tasks named."
  Passes: 3/3.

- **F12.2** [medium] `skills/tracker/jira.py:221`
  > self.base = os.environ["JIRA_URL"].rstrip("/")
  Any scheme is accepted. With an `http://` `JIRA_URL`, the Basic header carrying the
  user's own corporate password goes out in clear text on every request; 8.13 has no
  personal access tokens to limit the damage. This works against R7's "TLS verified …
  never disabled". Confirmed by running it: `JIRA_URL=http://127.0.0.1:9 … jira.py get X-1`
  → `jira.py: Jira is not reachable (ConnectionRefusedError): …`, exit 9, so the request
  was attempted. The tests use an `http://` fake Jira (`tests/test_jira.py:112`), which
  explains why.
  Fix: refuse a URL that is not `https://` with exit 4 or 3 and one line, and let the
  tests allow `http://127.0.0.1` only through a test-only switch. Passes: 1/3, confirmed
  (the run above).

- **F12.3** [medium] `skills/tracker/jira.py:263`
  > return Failure(UNREACHABLE, "Jira did not answer in %d seconds: are you on the "
  A timeout is reported the same way for a POST as for a GET, but a `create`, `comment`
  or `transition` that timed out may already be applied. Row 9 (SKILL.md:107) says
  "tell the user … and wait", and SKILL.md:112 says only "never guess the task's state".
  A rerun after the wait can then create a duplicate task or post a comment twice.
  Fix: in SKILL.md, for exit 9 after a write: "before running it again, `get` or
  `search` to see whether it was applied". Passes: 1/3, confirmed (`_network_failure`,
  jira.py:256-266, takes no method, and `create` has no idempotency key).

- **F12.4** [low] `skills/tracker/jira.py:433`
  > fields.update(parse_fields(args.field))
  This runs after the marked description is set (`jira.py:424`
  `fields["description"] = mark(read_text(args.description))`), so
  `--field description=...` replaces it and the task is created without
  `[LADO: <agent>]`, against R9.
  Fix: apply `mark()` to `fields["description"]` after merging `--field`, or refuse
  `description` in `--field`. Passes: 1/3, confirmed (the order of lines 424 and 433).

- **F12.5** [low] `README.md:31`
  > export JIRA_PASSWORD="$(security find-generic-password -s jira -a "$JIRA_USER" -w)"
  LADO builds each agent's environment by running the user's login shell with a time
  limit (`~/Projects/lado/src/lado/agent_env.py`: `TIMEOUT = 10  # seconds the shell may
  take`). A keychain prompt or a locked keychain stalls the profile, and every agent
  launch fails with a cause the README does not name.
  Fix: one README line: allow `security` to read the item ("Always Allow") and run the
  line once in a new terminal before the first session. Passes: 1/3, confirmed
  (agent_env.py).

TLS otherwise holds: `ssl.create_default_context(cafile=cafile)` (jira.py:225) keeps
verification and hostname checks. Redirects are not followed, so the Authorization header
never reaches another host. Credentials never appear in output (asserted by the tests).

## Known holes

| Known hole | Finding, or how the kit handles it |
|---|---|
| 1. Red check sent back with no environment cause considered | Mostly handled: environment faults have their own codes (4, 5, 9, 10, 12). A wrong `JIRA_URL` still comes out as exit 7 or 11, "fix the request" (F3.2), and a crash as exit 1 (F3.3). |
| 2. Work outside a flow, merge without a gate | No flows, no git work. Jira writes have no scope or ask in the skill (F12.1). |
| 3. Path outside the run's worktree | Handled: `find_config` stops at the first `.git`, a worktree's `.git` file included (`if os.path.exists(os.path.join(here, ".git")):`, jira.py:173). LADO excludes only `/.lado/worktrees/` from git, so a committed `.lado/tracker.yaml` reaches every worktree (README.md:41). |
| 4. Verdict without a severity threshold | Not applicable: no reviewer. |
| 5. Dependency skill that writes or asks where its role must not | The kit's own skill tells the agent to "tell the user" / "ask", and it is listed on workers (F7.1). |

## Not traced

Nothing. Every element (kit.yaml, the `tracker` skill, `jira.py`, `tests/test_jira.py`,
README.md) is named by a requirement in BLUEPRINT.md's table, every budget measure is
green, and the blueprint has no flow skeletons because the kit has no flows (R2). The
built skill and script meet R1–R10, except where F3.1 (R8: exit 8 also covers invalid
values), F12.2 (R7: TLS can be bypassed with `http://`) and F12.4 (R9: the mark can be
bypassed) name a gap.

## Questions for the human

1. Must a write to Jira (create, transition, comment, link) have an ask from the role,
   the step or you, from v0.1.0? The blueprint defers the *limits* to the trial; F12.1
   asks only for the scope line. Recommended: yes, one line in SKILL.md now, with the
   detailed limits at the trial.
2. Trial check, not confirmed offline: Jira Server's createmeta may list `reporter` as
   `required: true, hasDefaultValue: false`, even though a REST create without a reporter
   succeeds and uses the caller. If CRM3 does, every `create` stops with exit 8 "needs:
   Reporter". Recommended: look at CRM3's createmeta during the trial, before the first
   `create`, and exempt `reporter` in the pre-check if needed.

## Found on the way

- `[kit-builder]` The `kit-budget` flow script (`flow_diagram.py`) has no case for a kit
  without `flows/`. Given the kit folder, it reads `kit.yaml` as a flow and exits 2 with
  `error: kit.yaml: states must be a non-empty mapping`, both with `--out` and with
  `--compare BLUEPRINT.md`. It should report "no flows" and, for `--compare`, "no
  skeletons, no flows: nothing to compare" with exit 0.
