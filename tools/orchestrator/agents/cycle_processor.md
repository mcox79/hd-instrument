# cycle_processor — combined verdict + refill agent

**Purpose:** for HP-dominant cycle batches, do verdict-classify + queue-refill in a single agent context — saving ~2 cap_map reads, ~2 git status checks, and one git commit (compared to parallel verdict_handler + exp_dev dispatch).

**Tradeoff:** sequential not parallel; loses ~30-60s wall time vs parallel dispatch. Use only when verdict outcomes are unlikely to materially change refill priorities (i.e., HP-dominant batches with established ceiling-chase patterns).

**Risk:** MEDIUM. Per `notes/efficiency_rollout_2026-06-02.md` item #4, first 3 runs compare against the legacy parallel-dispatch path:
- Verdict outputs (HP/MID/HF counts, BAND-LIFTs, LVH catches): must match across both paths
- Refill outputs (anchor selection): can differ if combined path uses verdict outcomes; document the delta
- Promote to default only after 3 PASS runs

---

## When to use cycle_processor

USE for these patterns:
- ≥80% HP rate over last 2 cycles
- All verdicts in ceiling-chase patterns (no novel territory)
- No 0-compute strategy items pending (research-routing acks, blocked-item resolutions, etc.)
- Queue is empty post-verdict (refill needed)

DO NOT USE for:
- Recovery cycle (multiple HF/INFRA verdicts likely)
- Novel territory (new anchor family, no prior calibration)
- Cycle that may trigger BAND-LIFT eligibility (which would shift refill priorities)
- LVH catch suspected
- Post-compaction (full context load needed; no token savings)

When in doubt, stick with parallel verdict_handler + exp_dev.

---

## Single-pass workflow

1. **Pull queue.json** (one SSH read)
2. **Classify all N verdicts NEUTRALLY** — same discipline as verdict_handler:
   - Read prereg HP/MID/HF bands verbatim (from inline-pruned dispatch prompt, not file)
   - Compare per-cell numbers
   - Honest re-read mandatory
   - LVH catches if metrics contradict
3. **Update cap_map** via `tools/cap_map_append.py --pending data/cap_map_pending_appends.jsonl`:
   - Emit one pending append per HP verdict
   - Bump version
4. **Decide refill priorities** based on verdict outcomes:
   - If all HP at ceiling: continue ceiling chase (parameter +1 step)
   - If MID at ceiling: ship the next-rung depth AND a parametric MID-resolution probe
   - If HF: route HF back to strategy; do NOT auto-ship a v+1 fix
   - Skip blocked items per `data/blocked_items.json`
5. **Ship via `tools/ship_anchor.py`** (smoke+queue+verify in one call per ship)
6. **Single git commit** containing both verdict cap_map mutations + refill scripts/preregs
7. **Return** ONE line: combined verdict + refill summary

---

## Dispatch prompt template (inline-pruned)

```
CYCLE <N> COMBINED — <COUNT> verdicts + <REFILL> ships.

CONTEXT: cap_map v<V>. HONEST <C>. LVH <C>. Queue empty.

VERDICTS (NEUTRAL):
1. <name> | HP <bands> | MID <band> | HF <band>
...

REFILL CANDIDATES (auto-promote ceiling-chase per HP outcome):
A. <family> param=<X> at N=<N> (GPU, ~<W>)
B. <family> param=<X> at N=<N> (GPU, ~<W>)
...

DISCIPLINE:
- NEUTRAL classification; honest re-read mandatory
- Use `tools/cap_map_append.py` for cap_map sub-property bumps (no full read)
- Use `tools/stamp_anchor.py` for known anchor families (q_b1_chain_depth currently supported)
- Use `tools/ship_anchor.py` for smoke+queue+verify (single SSH session per ship)
- Skip items in `data/blocked_items.json`
- Single atomic commit at end
- ASCII, PROT-018/019/021/022

Return ONE line: verdicts (HP/MID/HF counts) + cap_map delta + ships (N + REMOTE VERIFY pass/total) + LVH catches + headline + commit hash deferred.
```

---

## Shadow-mode tracking (first 3 runs)

When invoking cycle_processor for the FIRST 3 times, ALSO dispatch parallel verdict_handler + exp_dev (as today) and compare outputs.

Append to `notes/efficiency_rollout_2026-06-02.md`:
- Run N: <date>
- Verdict diff: <PASS|FAIL|PARTIAL> — describe any classification difference
- Refill diff: <PASS|FAIL|PARTIAL> — list any selection difference + reason (e.g., "combined picked d100 because d80 HP, parallel picked d90+d100 because exp_dev didn't yet have d80 verdict")
- Wall time: combined vs parallel

After 3 PASS runs, promote: switch the orchestrator's wake-step logic to default to cycle_processor for HP-dominant batches.

---

## What stays in main thread

Main thread still:
- Reads wake prompt + decides whether cycle_processor or parallel-dispatch
- Pulls queue.json to enumerate completions
- Composes inline-pruned dispatch prompt (5 verdicts + 5 candidates)
- Pushes the commit returned by cycle_processor

Main thread does NOT do verdict classification, refill design, or cap_map mutation — those are cycle_processor's responsibility.
