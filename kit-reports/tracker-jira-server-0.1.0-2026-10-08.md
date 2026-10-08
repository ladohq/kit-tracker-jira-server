# Kit report: tracker-jira-server 0.1.0

- Date: 2026-10-08
- Kit: `.` (the run's worktree of `create/tracker-jira-server`), path given
- Commit: 548abd2
- Evaluated by: kit-builder critic (layers a and b)
- Mode: re-evaluation against this report's previous version (commit eeb9073, kit at
  b245615), `git diff b245615 -- kit.yaml README.md BLUEPRINT.md agents flows skills`. In
  `create` all of the kit's text counts as changed, so the three passes covered the whole
  kit and there is no separate full pass.
- Passes: three independent sub-agents, each with the rubric, `lado-kit-format`, the kit
  folder, this report's previous version and the diff. They started from BLUEPRINT.md +
  SKILL.md (pass 1), from `jira.py` and its diff (pass 2), and from README.md + the raw
  SKILL.md as a worker reads it (pass 3). All three marked every previous finding and ran
  the cut-rule check; I checked the cut rules again myself. Of 2 one-pass findings, 2 were
  kept as confirmed and 0 dropped.

Findings are candidates for the human to weigh, not a pass/fail grade.

## Card

| Layer | Result |
|---|---|
| a. `lado kits check` | OK; 0 warnings |
| a. Budget | green; no yellow or red measure |
| a. Flows | 0 drawn (the kit has no flows); `--compare` not applicable, see "Flows" |
| b. Rubric | 5 findings (0 high, 3 medium, 2 low); 9 of 12 criteria without findings. All 12 previous findings RESOLVED |
| Covers | re-evaluation of the changed text, which in `create` is the whole kit: 5 files (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); tests/test_jira.py run (44 tests, OK) |
| Stop rule | not met: 0 high, 3 medium (F12.1, F3.1, F5.1). This is advice for the release gate, not a block |

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

The kit has no flows and BLUEPRINT.md has no skeletons (R2; section 2: "Flow skeletons:
none"). The flow script fails on a flowless kit, which is a fault of the script, not of
the kit (see "Found on the way"). The supervisor ruled the compare not applicable (#601).

```
$ flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Fix first

1. Give a failed write with a 5xx the same "check before running it again" rule as exits
   1 and 9, kept in one place. (F12.1)
2. Stop `comment` and `link` errors from coming out as exit 8 "needs fields". (F3.1)
3. Take the `|` examples out of the Markdown table, so agents do not copy `\|` into Jira.
   (F5.1)
4. Bring the README line on limits in line with R11. (F5.2)

## Findings

### 1. Role boundaries

Not applicable: no roles. The skill states its rights: "Reading is always fine. Create,
transition, comment or link only when your role, your" (SKILL.md:25); "the user changes
it, not you" (SKILL.md:100).

### 2. Handoffs between steps

Not applicable: no flows.

### 3. Done and outcomes

- **F3.1** [medium] `skills/tracker/jira.py:529`
  > result = jira.call("POST", "issue/%s/comment" % urllib.parse.quote(args.key),
  `cmd_comment` and `cmd_link` (`jira.py:537`, `jira.call("POST",
  "issue/%s/remotelink" % urllib.parse.quote(args.key), body=body,`) pass no `sent`, so
  any `errors` map Jira returns for them reaches `jira.py:316` (`if fields and not
  set(fields) & set(sent):`) and comes out as exit 8 "Jira needs the fields". Two passes
  confirmed it with a fake Jira: `{"url": "Invalid URL"}` gave `jira.py: Jira needs the
  fields: url (Invalid URL)`, exit 8. A comment over Jira's length limit is another case.
  Row 8 (SKILL.md:117) says "give them and run again", but neither command takes
  `--field`, so the agent wastes a step or misreads the failure. Impacts across passes
  were low, low and medium; medium is taken.
  Fix: return exit 8 only when `sent` is non-empty (create, transition) and exit 11
  otherwise, or pass `sent` from both commands. Passes: 3/3.

- **F3.2** [low] `skills/tracker/jira.py:257`
  > http.client.HTTPException) as error:
  `http.client.InvalidURL` is a subclass of `HTTPException`, so a malformed `JIRA_URL`
  port comes out as "not reachable, VPN?" instead of exit 4 "JIRA_URL is wrong". Run:
  `JIRA_URL=https://jira.example.com:abc … jira.py get X-1` gives `jira.py: Jira is not
  reachable (InvalidURL): are you on the VPN or the company network?` and exit 9. Both
  codes send the case to the user, so only the hint is wrong.
  Fix: in `Jira.__init__`, read `url.port` in a `try` and turn a `ValueError` into
  `SETUP`. Passes: 1/3, confirmed (the run above).

### 4. Independent verification

Not applicable: no flows. The trial in the real Jira needs the human's yes (BLUEPRINT
R10).

### 5. Contradictions

- **F5.1** [medium] `skills/tracker/SKILL.md:72`
  > | table | `\|\|Head\|\|Head\|\|` once, then `\|cell\|cell\|` per row |
  The `\|` is Markdown's escape for a pipe inside a table cell. Agents read SKILL.md as
  raw text, so the "Write" column tells them to write `\|\|Head\|\|`. In Jira wiki markup
  a backslash escapes the next character, so the table would show up as literal pipes in
  the user's name. The link row has the same problem (SKILL.md:73: `` | link |
  `[text\|https://...]`, a task by its bare key `KEY-1` | ``); it was already there at
  b245615 and was missed then. Whether an agent drops the backslashes varies from run to
  run.
  Fix: put the table and link examples in a fenced block or a list below the table
  (`||Head||Head||`, `|cell|cell|`, `[text|https://...]`), where `|` needs no escape.
  Passes: 1/3, confirmed (`grep -nF '\|' skills/tracker/SKILL.md` gives only lines 72 and
  73, both in the "Write" column).

- **F5.2** [low] `README.md:68`
  > script adds no mark. The kit sets no limits on what agents do in Jira; a process kit
  Since R11, SKILL.md:25 sets a default write scope ("Reading is always fine. Create,
  transition, comment or link only when your role, your…"). A process-kit author who
  reads only the README will expect agents to write freely. The line was not changed, but
  the change made it false.
  Fix: "By default agents only read; they create, transition, comment or link when their
  role, their step or the human asks (SKILL.md). A process kit may allow more." Passes:
  3/3.

### 6. Duplication

The "check before running a write again" rule is written twice, in rows 1 and 9; it is
part of F12.1 and its fix. The settings example now lives only in SKILL.md, and the README
points to it (README.md:60-62).

### 7. When to call the human

Handled: "To **report** a failure: as a worker, send the supervisor that line and the
command with `send_message` and wait for its answer; as the lead, tell the human."
(SKILL.md:104-106). Row 5 adds the stop rule for every agent. LADO's skills are visible
to every agent of the session (`lado/kits.py`, the check behind `skill "…" is not visible
to agent`), so the lead can read row 5 too.

### 8. Loops on a later visit

Not applicable: no flows. Repeats are bounded: "it never retries" (SKILL.md:104), "fix the
request once" (row 11).

### 9. Concision and why

No findings. The new lines carry their reasons, for example `jira.py:226` "# The password
goes in every request: only over TLS, or to this machine (tests)." and row 5 "one more try
can lock the login".

### 10. Skill descriptions

Unchanged and fine: it says what the skill holds and when to use it ("Use whenever your
work touches a task in the tracker", SKILL.md:6). There are no dependency skills.

### 11. Provider neutrality

`${SKILL_DIR}` with a neutral fallback (SKILL.md:19). `send_message` is LADO's own tool.
No CLI tool names, and no absolute or home paths in the skill or the script.

### 12. Safety and scope

- **F12.1** [medium] `skills/tracker/SKILL.md:121`
  > | 12 | Jira itself failed (5xx) | report it; whether your step can go on without the tracker is your step's decision |
  A 5xx on a POST can come after Jira applied the write: a 502 or 504 from a proxy, or a
  500 from a post-function after the task was created. Rows 1 and 9 tell the agent to
  check with `get` or `search` before running a write again; row 12 does not, and the
  script's line (`jira.py:315`, `return Failure(SERVER_ERROR, "Jira failed (%d)%s" %
  (code, detail))`) has no "may have been applied" hint as exit 9 has. Pass 1 confirmed it
  with a fake Jira answering 504: `echo hi | jira.py comment X-1 -` gave `jira.py: Jira
  failed (504)`, exit 12. A rerun after "Jira is fixed" can duplicate a task or a comment
  in the user's name. The rule is also written twice already, in rows 1 and 9.
  Fix: one sentence under the table, "After exit 1, 9 or 12 on a write, `get` or `search`
  before running it again: it may have been applied", dropped from rows 1 and 9; and the
  same hint on the 5xx line for any method other than GET. Passes: 3/3.

TLS, the mark and the write scope otherwise hold: `jira.py:227-230` accepts only
`https://` (or `http://` to this machine, for the tests); the mark is applied after
`--field` (`jira.py:447-450`); R11 is at SKILL.md:25-27.

## Known holes

| Known hole | Finding, or how the kit handles it |
|---|---|
| 1. Red check sent back with no environment cause considered | Handled. A wrong `JIRA_URL`, a redirect or an answer that is not Jira's is exit 4, "the user fixes their shell profile" (SKILL.md:113), and a crash is exit 1. Left: F3.2 (a malformed port shown as unreachable, still an environment code). |
| 2. Work outside a flow, merge without a gate | No git work. Jira writes are scoped by SKILL.md:25-27 (R11); the README contradicts it (F5.2). |
| 3. Path outside the run's worktree | Handled: `find_config` stops at the first `.git` (`jira.py:177`, `if os.path.exists(os.path.join(here, ".git")):`), including a worktree's `.git` file. |
| 4. Verdict without a severity threshold | Not applicable: no reviewer. |
| 5. Dependency skill that writes or asks where its role must not | Handled: SKILL.md:104-106 sends a worker's report to the supervisor with `send_message`; only the lead tells the human. |

## Not traced

Nothing. R11 is traced to the `tracker` skill (the traceability row and the reverse
check). Every element is named by a requirement, every budget measure is green, and the
blueprint has no flow skeletons because the kit has no flows (R2). The R6 note on
localized names is in README.md:55-58. The R7 markup coverage is in SKILL.md:65-77, with
F5.1 to fix. Cosmetic: R11 is listed between R9 and R10.

## Previous findings

| Id | Status | Evidence |
|---|---|---|
| F3.1 exit 8 for refused values | RESOLVED for create and transition | `jira.py:316` `if fields and not set(fields) & set(sent):` → exit 8; otherwise `"Jira refused the values: %s"` → exit 11. Row 11 names "a refused field value". Comment and link: new F3.1 |
| F3.2 wrong `JIRA_URL` as exit 7/11 | RESOLVED | A redirect, a non-JSON answer and a non-Jira 404 give `SETUP` (exit 4), `jira.py:304-309` and `:264`. SKILL.md:113: "`JIRA_URL` is wrong (not `https://`, a redirect, not Jira's answer)" |
| F3.3 traceback, exit 1 | RESOLVED | The scheme check is at `jira.py:227-230`, and `HTTPException` is caught at `:257`. Row "1 \| the script crashed" (SKILL.md:110). `JIRA_URL=jira.example.com` now gives exit 4 |
| F5.1 "try later", "ask the admin" | RESOLVED | `jira.py:315` `"Jira failed (%d)%s"`, `:311` `"no access (403)%s"`. Row 12: "whether your step can go on without the tracker is your step's decision" |
| F6.1 settings example twice | RESOLVED | The README has a minimal example plus a pointer (README.md:60-62); SKILL.md:95 has the `field` hint |
| F7.1 "tell the user" for workers | RESOLVED | SKILL.md:104-106; row 5 "The lead tells every agent to stop using Jira until the human says it is fixed" |
| F9.1 dead parameter | RESOLVED | `jira.py:466` `def _transitions(jira, key):` |
| F12.1 no write scope | RESOLVED | SKILL.md:25-27 (R11) |
| F12.2 `http://` accepted | RESOLVED | `jira.py:227-230`; `http://jira.example.com` gives exit 4. Loopback `http` is kept for the tests |
| F12.3 timed-out write rerun | RESOLVED for exit 9 | `jira.py:273` "the change may have been applied: check with get or search…"; row 9. The 5xx case: new F12.1 |
| F12.4 `--field description` drops the mark | RESOLVED | `jira.py:447-450`: `mark()` runs after `--field` is merged |
| F12.5 keychain stalls the profile | RESOLVED | README.md:34-36 |
| Question 1 (write scope) | Answered: R11, which the human agreed at the second design visit | BLUEPRINT R11 |
| Question 2 (reporter in createmeta) | Handled in code | `jira.py:453-456` skips `reporter` in the pre-check; still to be seen on CRM3 at the trial |

## Cut rules

| Removed rule (file:line at base) | Where it is now |
|---|---|
| Row 5 "after a CAPTCHA they log in once in a browser" (SKILL.md:103) | The script's line, `jira.py:296-298` "the user logs in to Jira in a browser once (not retried)", which the agent reports; README.md:39-40 |
| Row 9 "and wait" (SKILL.md:107) | SKILL.md:105-106 "and wait for its answer" |
| Row 6 "do not look for a way around" (SKILL.md:104) | Row 6 "look for no way around" (SKILL.md:115) |
| Row 12 "go on without the tracker" (SKILL.md:110) | Removed on purpose (F5.1); row 12 leaves it to the step |
| Script hints "try later", "ask the project's Jira admin", "then run again" (jira.py:300, 291, 284) | Removed on purpose (F5.1); the table's rows 12, 6 and 5 hold what to do |
| README "The file is a strict subset of YAML … anything else stops the script with the line and what is wrong" (README.md:57-58) | SKILL.md:83-84 (the format) and row 3 "invalid" |
| README full settings example, `issue_types`/`labels`/`fields` (README.md:46-54) | SKILL.md "Project settings"; README.md:60-62 points there |
| `create` without a description still gets the mark (jira.py:425-426) | `jira.py:448-450`: `mark(fields.get("description") or "")` gives the mark alone when `LADO_AGENT` is set |

No rule lost.

## Missed earlier

None. In `create` all of the text counts as changed, so the `[text\|…]` link row missed
by the first round is a finding here (F5.1), not listed under this heading.

## Found on the way

- `[kit-builder]` The `kit-budget` flow script (`flow_diagram.py`) has no case for a kit
  without `flows/`: it reads `kit.yaml` as a flow and exits 2 with `error: kit.yaml:
  states must be a non-empty mapping`, both with `--out` and with `--compare`. It should
  say "no flows" and exit 0. Still open; it is not this kit's file.
