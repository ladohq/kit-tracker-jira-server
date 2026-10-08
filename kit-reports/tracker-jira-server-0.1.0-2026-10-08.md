# Kit report: tracker-jira-server 0.1.0

- Date: 2026-10-08
- Kit: `.` (the run's worktree of `create/tracker-jira-server`), path given
- Commit: ec8af0b
- Evaluated by: kit-builder critic (layers a and b)
- Mode: re-evaluation against this report's previous version (commit e46a075, kit at
  444ed6a), `git diff e46a075 -- kit.yaml README.md BLUEPRINT.md agents flows skills`.
  This is the fourth round. Round one (eeb9073) was a full evaluation, and round two
  (cef230c) made three full passes over the whole kit. This round reviews ec8af0b: 8
  changed lines in `Jira.__init__` of `jira.py`, plus tests.
- Passes: I made the three passes myself, without sub-agents, because the change is 8
  lines in one function. Pass 1 read the diff against SKILL.md row 4. Pass 2 read the code
  path of every `JIRA_URL` shape. Pass 3 ran the script with five `JIRA_URL` values (see
  "Previous findings"). Each pass covered all 12 criteria and the known holes over the
  change and what it points to (SKILL.md row 4, README "Credentials"). There were no
  one-pass findings.

Findings are candidates for the human to weigh, not a pass/fail grade.

## Card

| Layer | Result |
|---|---|
| a. `lado kits check` | OK; 0 warnings |
| a. Budget | green; no yellow or red measure |
| a. Flows | 0 drawn (the kit has no flows); `--compare` not applicable, see "Flows" |
| b. Rubric | 0 findings; 12 of 12 criteria without findings. Both previous findings RESOLVED |
| Covers | re-evaluation of the changed text (`jira.py` `Jira.__init__`, lines 221-240) and what it points to (SKILL.md row 4, README "Credentials"); no full pass, since round two's passes were full; tests/test_jira.py run (46 tests, OK) |
| Stop rule | holds: no high and no medium finding in the changed text |

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

Nothing.

## Findings

### 1. Role boundaries

Not applicable: no roles. Not touched by the change.

### 2. Handoffs between steps

Not applicable: no flows.

### 3. Done and outcomes

No findings. Every malformed `JIRA_URL` now ends in exit 4, which SKILL.md row 4 covers
("a Jira variable is unset, or `JIRA_URL` is wrong (not `https://`, a redirect, not
Jira's answer)"). Each line names its own cause: `jira.py:233` `raise Failure(SETUP,
"JIRA_URL is not a valid address (host, port): it must be "` for an address that does not
parse, and the "must be Jira's https:// base address" line only for a parsed address that
is not https. `urlsplit` is now inside the `try` (`jira.py:228`).

### 4. Independent verification

Not applicable: no flows. The trial in the real Jira needs the human's yes (BLUEPRINT
R10).

### 5. Contradictions

None. README.md:68-70 now matches R11 and SKILL.md:25-27: "By default agents only read;
they create, transition, comment or link when their role, their step or the human asks".
The markup examples are in a fenced block (SKILL.md:78-82), and SKILL.md has no `\|`
left.

### 6. Duplication

The "check before running a write again" rule is now in one place, SKILL.md:130-131
("After exit 1, 9 or 12 on a write, `get` or `search` before running it again: it may
have been applied."). In the script it is one constant, `APPLIED` (`jira.py:38`).

### 7. When to call the human

Unchanged and handled: SKILL.md:111-113 sends a worker's report to the supervisor with
`send_message`, and the lead tells the human.

### 8. Loops on a later visit

Not applicable: no flows.

### 9. Concision and why

No findings. The https rule keeps its reason: "# The password goes in every request: only
over TLS, or to this machine (tests)."

### 10. Skill descriptions

Unchanged; fine.

### 11. Provider neutrality

Nothing CLI-specific was added. The path `skills/tracker/SKILL.md` appears only in the
human-facing README.

### 12. Safety and scope

No findings. The change keeps the https-only check, now behind the parse check, and adds
no way past it. The write scope is stated in SKILL.md and the README, and they agree. A
failed write with exit 1, 9 or 12 is checked before it runs again.

## Known holes

| Known hole | Finding, or how the kit handles it |
|---|---|
| 1. Red check sent back with no environment cause considered | Handled. Every malformed `JIRA_URL` is exit 4 (an environment fault, "the user fixes their shell profile") with a line naming its cause; none is a traceback any more. |
| 2. Work outside a flow, merge without a gate | No git work. Jira writes are scoped by SKILL.md:25-27 (R11), and README.md:68-70 now agrees. |
| 3. Path outside the run's worktree | Unchanged, handled: `find_config` stops at the first `.git`. |
| 4. Verdict without a severity threshold | Not applicable: no reviewer. |
| 5. Dependency skill that writes or asks where its role must not | Unchanged, handled: SKILL.md:111-113. |

## Not traced

Nothing. BLUEPRINT.md did not change this round or the last one. Every element is named by a requirement,
every budget measure is green, and the blueprint has no flow skeletons because the kit has
no flows (R2). Cosmetic and left by the author: R11 is listed between R9 and R10.

## Previous findings

| Id | Status | Evidence |
|---|---|---|
| F3.1 malformed port gets the "must be https://" message | RESOLVED | `JIRA_URL=https://jira.example.com:abc … get X-1` → `jira.py: JIRA_URL is not a valid address (host, port): it must be Jira's https:// base address`, exit 4 |
| F3.2 `https://[::1` gives a traceback | RESOLVED | The same line and exit 4. `url = urllib.parse.urlsplit(self.base)` is now inside the `try` (`jira.py:228`) |

Other shapes checked in the same run: `http://jira.example.com` gives "must be Jira's
https:// base address", exit 4; `https://` and `jira.example.com` (no scheme) give "not a
valid address", exit 4. The tests cover both messages (`tests/test_jira.py:471`, `:475`).

## Cut rules

None removed: the diff only moves `urlsplit` into the `try` and splits one condition into
two, and the https-only rule (the `# The password goes in every request` check) is kept.

## Missed earlier

None.

## Found on the way

- `[kit-builder]` The `kit-budget` flow script (`flow_diagram.py`) has no case for a kit
  without `flows/`: it reads `kit.yaml` as a flow and exits 2 with `error: kit.yaml:
  states must be a non-empty mapping`, both with `--out` and with `--compare`. It should
  say "no flows" and exit 0. Still open; it is not this kit's file.
