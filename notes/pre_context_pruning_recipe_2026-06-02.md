# Pre-context pruning recipe — main thread → subagent dispatch

**Purpose:** reduce subagent input tokens by ~40% by extracting just the relevant 5 candidate items + bands in the dispatch prompt itself, instead of letting the subagent re-read 10-30k chars of routing files.

**Applies to:** exp_dev (refill), verdict_handler (batch processing), strategy_scribe (annotation-only).

**Rule of thumb:** if main thread has already read the routing file in this conversation, INLINE the relevant 5-item slice. If main thread has NOT read it (e.g., post-compaction), pass the file path so subagent reads once.

---

## Pre-flight: 5 questions main thread answers BEFORE composing the dispatch prompt

1. **What's the cycle's PRIORITY ORDER?** (top 5 only — already have this from recent verdict_handler routing or strategy_request)
2. **For each priority, what are the pre-reg HP/MID/HF bands?** (quote verbatim if known; "TBD per anchor family conventions" if new)
3. **What's the resource (GPU/CPU) + wall estimate per priority?** (from research routing or strategy spec)
4. **What's in the global BLOCKED list?** (read `data/blocked_items.json` once; never re-list in prompts)
5. **What ANCHOR-FAMILY templates apply?** (Q-A3 / Q-B1 / PP-48 / PP-52 / etc. — point exp_dev at the right `experiments/_templates/<family>.py`)

If all 5 are known, INLINE them. If any are unknown, pass file paths for the subagent to read.

---

## exp_dev dispatch template (post-pruning)

```
v<VERSION> REFILL — N ANCHOR MAX. Queue empty + GPU idle.

CONTEXT: cap_map v<VERSION>. HONEST <COUNT>. LVH <COUNT>. Portfolio 32+74. Pause flag ABSENT.

PRIORITY CANDIDATES (already-pruned; pick <=N):
A. <ANCHOR_FAMILY> <PARAM> at N=<N> 5-seed (<RESOURCE>, ~<WALL>) — HP <CRITERION>; HF <CRITERION>
B. <ANCHOR_FAMILY> <PARAM> at N=<N> 5-seed (<RESOURCE>, ~<WALL>) — HP <CRITERION>; HF <CRITERION>
...

GLOBALLY BLOCKED: read `data/blocked_items.json`; auto-skip matching patterns.

ANCHOR TEMPLATES: stamp from `experiments/_templates/<family>.py` via
`python tools/stamp_anchor.py <family> --param <PARAM> --N <N> --out experiments/exp_<name>.py`.
Override only if template missing.

DISCIPLINE: PROT-018/019/021/022. ASCII. GPU template MANDATORY for GPU. Smoke (N=1024 or 4096) BEFORE FULL.

DELIVERABLES: scripts + preregs (use `preregs/_template.md`) + smoke verify + queue_add + REMOTE VERIFY + commit deferred.

Return ONE line: N shipped + REMOTE VERIFY pass/total + smoke results + dropped + commit hash deferred.
```

**Removed from old prompt** (now redundant):
- Full priority order list with descriptions (replaced by 5-line PRIORITY CANDIDATES table)
- "EXPLICITLY SKIP combo1_v5 + pp47_v3" (replaced by blocked_items.json reference)
- Verbose anchor-family rationale paragraphs (replaced by inline `(<RESOURCE>, ~<WALL>)`)

---

## verdict_handler dispatch template (post-pruning)

```
CYCLE <N> BATCH — <COUNT> verdicts. NEUTRAL classification.

CONTEXT: cap_map v<VERSION>. HONEST <COUNT>. LVH <COUNT>. Queue: <STATE>.

VERDICTS (NEUTRAL; honest re-read decides):
1. <anchor_name> | prereg <path> | HP <bands_verbatim> | MID <band> | HF <band>
2. <anchor_name> | prereg <path> | HP <bands_verbatim> | MID <band> | HF <band>
...

ENFORCEMENT:
- REMOTE-FIRST: SCP metrics.json + experiment.log per anchor
- Honest re-read MANDATORY
- LVH catches: flag if any metric contradicts another
- ASCII; PROT-018/019/021/022 audit
- cap_map cumulative; single atomic commit v<V> -> v<V+1> if state changes
- Decisions log + visibility log + log_event

Return ONE line: classified N (HP/MID/HF counts) + cap_map delta + commit hash deferred + LVH catches + headline.
```

**Removed from old prompt:**
- Per-anchor "(prereg path) — descriptor sentence" prose (replaced by 1-line table with HP/MID/HF inline)
- "Q-B1 ceiling-chase pattern: if d-X passes consider BAND-LIFT" preframing (downgraded — verdict_handler decides BAND-LIFT eligibility from cap_map row criteria itself)

---

## strategy_scribe dispatch template (post-pruning)

```
ANNOTATION + cap_map v<V> -> v<V+1>. Pause flag absent.

SOURCE: <routing_file_path> sections <which>.

ANNOTATIONS:
- <I-NUMBER>: <OLD STATUS> -> <NEW STATUS>; reason: <ONE_SENTENCE>
- <ROW>: append sub-property "<text>"
...

REQUIRED ACTIONS:
- Move routing to routed_completed with append: "<acted-on text>"
- Append decisions log
- Visibility log + log_event
- Single atomic commit

Return ONE line: <each_action> YES/NO + commit hash deferred.
```

---

## Token budget targets (post-pruning)

| Dispatch type | Pre-pruning input tokens | Post-pruning target |
|---|---|---|
| exp_dev refill (5 anchors) | 12k-18k | 4k-6k |
| verdict_handler (5 anchors) | 8k-12k | 3k-5k |
| strategy_scribe (annotation) | 6k-10k | 2k-4k |

Track actual delta in `notes/efficiency_rollout_2026-06-02.md` Token-Budget column over 3 cycles.

---

## When pre-context pruning DOESN'T apply

- Post-compaction (main thread hasn't read anything yet): pass file paths
- Novel anchor family with no template + no clear priors: subagent needs full context
- LVH catch suspected: subagent needs full prereg + log to do honest re-read
- User explicitly asks "include the full routing"

In those cases, fall back to the legacy prompt style.
