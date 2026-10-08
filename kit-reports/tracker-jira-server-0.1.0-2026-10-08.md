# Kit report: tracker-jira-server 0.1.0

- Date: 2026-10-08
- Kit: `.` (the run's worktree of `create/tracker-jira-server`), path given
- Commit: 444ed6a
- Evaluated by: kit-builder critic (layers a and b)
- Mode: re-evaluation against this report's previous version (commit cef230c, kit at
  548abd2), `git diff cef230c -- kit.yaml README.md BLUEPRINT.md agents flows skills`.
  This is the third round. The first round (eeb9073) was a full evaluation; the second
  (cef230c) was three full passes over the whole kit, since in `create` all of the text is
  new. This round reviews the fix commit 444ed6a.
- Passes: three independent sub-agents, each with the rubric, the kit folder, this
  report's previous version and the diff. They started from SKILL.md's changed sections
  (pass 1), from `jira.py`'s diff and the `sent` semantics (pass 2), and from the README
  and the raw SKILL.md with `--word-diff` (pass 3). Each covered all 12 criteria and the
  known holes over the changed text and the places it points to. I checked the cut rules
  myself as well. Of 2 one-pass findings, 2 were kept as confirmed and 0 dropped.

Findings are candidates for the human to weigh, not a pass/fail grade.

## Card

| Layer | Result |
|---|---|
| a. `lado kits check` | OK; 0 warnings |
| a. Budget | green; no yellow or red measure |
| a. Flows | 0 drawn (the kit has no flows); `--compare` not applicable, see "Flows" |
| b. Rubric | 2 findings (0 high, 0 medium, 2 low); 11 of 12 criteria without findings. All 5 previous findings RESOLVED |
| Covers | re-evaluation of the changed text (README.md:66-70; SKILL.md "Writing in Jira" and "When the script fails"; `jira.py` `Jira.__init__`, `call`, `_network_failure`, `_http_failure`, `cmd_comment`, `cmd_link`), with what it points to; no full pass, since the three passes of the previous round were full; tests/test_jira.py run (46 tests, OK) |
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

Nothing blocks. Both findings are low and concern the same `JIRA_URL` check; they can wait
for the `improve` run after the trial:

1. Parse `JIRA_URL` inside the `try` and give a malformed port its own message. (F3.1,
   F3.2)

## Findings

### 1. Role boundaries

Not applicable: no roles. The skill states its rights at SKILL.md:25-27 ("Reading is
always fine. Create, transition, comment or link only when your role, your…"), unchanged.

### 2. Handoffs between steps

Not applicable: no flows.

### 3. Done and outcomes

- **F3.1** [low] `skills/tracker/jira.py:235`
  > raise Failure(SETUP, "JIRA_URL must be Jira's https:// base address: the "
  A malformed port (`https://jira.example.com:abc`) now gets the right code, 4, but still
  this message, which says the URL must be `https://` although it already is. Run:
  `jira.py: JIRA_URL must be Jira's https:// base address: the password is sent with
  every request`, exit 4. The user looks for the wrong mistake; row 4 does point at
  `JIRA_URL`.
  Fix: a separate line when the port is malformed, e.g. "JIRA_URL has a malformed port".
  Passes: 1/3, confirmed (the run above).

- **F3.2** [low] `skills/tracker/jira.py:227`
  > url = urllib.parse.urlsplit(self.base)
  `urlsplit` sits just above the new `try`, which only guards `url.port`. A malformed IPv6
  host raises there: `JIRA_URL='https://[::1' … jira.py get X-1` ends with `ValueError:
  Invalid IPv6 URL`, exit 1, instead of exit 4. Row 1 ("report its last line") still gets
  it to the user, so only the code is off. Pass 2 of the previous round noted it as
  covered by row 1. The line comes from 601bf60, so in `create` it counts as changed
  text, not "Missed earlier".
  Fix: move `urlsplit` into the same `try` and turn its `ValueError` into `SETUP`. Passes:
  1/3, confirmed (the run above; `git blame -L227,227` gives 601bf60).

Otherwise the exit codes match their rows. A field error on `comment` or `link` is exit 11
(`jira.py:324`, `if fields and sent is not None and not set(fields) & set(sent):`;
`sent=None` at `:538` and `:546`). A malformed port is exit 4. A write that fails with a
5xx carries the "may have been applied" hint (`jira.py:323`).

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

No findings. The new code comment carries its reason: `jira.py:321` "# A proxy's 502/504
or a failing post-function can follow an applied write."

### 10. Skill descriptions

Unchanged; fine.

### 11. Provider neutrality

Nothing CLI-specific was added. The path `skills/tracker/SKILL.md` appears only in the
human-facing README.

### 12. Safety and scope

No findings. The write scope is stated in SKILL.md and the README, and they agree. A
failed write with exit 1, 9 or 12 is checked before it runs again.

## Known holes

| Known hole | Finding, or how the kit handles it |
|---|---|
| 1. Red check sent back with no environment cause considered | Handled. A malformed port is now exit 4 (an environment fault), not "VPN?". Left: F3.1 (the message) and F3.2 (IPv6, exit 1). |
| 2. Work outside a flow, merge without a gate | No git work. Jira writes are scoped by SKILL.md:25-27 (R11), and README.md:68-70 now agrees. |
| 3. Path outside the run's worktree | Unchanged, handled: `find_config` stops at the first `.git`. |
| 4. Verdict without a severity threshold | Not applicable: no reviewer. |
| 5. Dependency skill that writes or asks where its role must not | Unchanged, handled: SKILL.md:111-113. |

## Not traced

Nothing. BLUEPRINT.md did not change this round. Every element is named by a requirement,
every budget measure is green, and the blueprint has no flow skeletons because the kit has
no flows (R2). Cosmetic and left by the author: R11 is listed between R9 and R10.

## Previous findings

| Id | Status | Evidence |
|---|---|---|
| F12.1 5xx after a write | RESOLVED | SKILL.md:130-131, once for exits 1, 9 and 12; `jira.py:323` adds `APPLIED` for any method other than GET. A fake Jira answering 504 to `comment` gave `Jira failed (504)…; the change may have been applied: check with get or search before running it again`, exit 12; a GET gave no hint |
| F3.1 comment/link field errors as exit 8 | RESOLVED | `sent=None` (`jira.py:538`, `:546`) and `:324`. A fake Jira gave `link` → `Jira refused the values: url (Invalid URL)`, exit 11; `comment` → exit 11 |
| F3.2 malformed port as exit 9 | RESOLVED | `jira.py:228-231` reads `url.port` in a `try`; `:abc` and `:99999` give exit 4. Message: new F3.1 |
| F5.1 `\|` in the markup table | RESOLVED | SKILL.md:72 `\| table, link \| see below the table \|`; fenced examples at :78-82; no `\|` in SKILL.md |
| F5.2 README "sets no limits" | RESOLVED | README.md:68-70 |

## Cut rules

| Removed rule (file:line at base) | Where it is now |
|---|---|
| Row 1 "repeat no write before you checked with `get` or `search`" (SKILL.md:110) | SKILL.md:130-131, for exit 1 on a write |
| Row 9 "After a write, `get` or `search` before running it again: it may have been applied" (SKILL.md:118) | SKILL.md:130-131, word for word, now also for exits 1 and 12 |
| Link row "a task by its bare key `KEY-1`" (SKILL.md:73) | SKILL.md:76 "a task's bare key `KEY-1` links to it" |
| README "The kit sets no limits on what agents do in Jira" (README.md:68) | Replaced on purpose by the R11 scope (F5.2) |

No rule lost.

## Missed earlier

None.

## Found on the way

- `[kit-builder]` The `kit-budget` flow script (`flow_diagram.py`) has no case for a kit
  without `flows/`: it reads `kit.yaml` as a flow and exits 2 with `error: kit.yaml:
  states must be a non-empty mapping`, both with `--out` and with `--compare`. It should
  say "no flows" and exit 0. Still open; it is not this kit's file.
