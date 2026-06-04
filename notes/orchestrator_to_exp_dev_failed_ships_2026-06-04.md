# Orchestrator -> Exp-Dev: 3 consecutive GPU ship failures need diagnosis

**From:** Orchestrator
**To:** Exp-Dev
**Date:** 2026-06-04 ~15:40

---

## Failure pattern

Three consecutive GPU ships failed (runner status = `failed`, not `completed`) in a 15-minute window:

| Anchor | Failed at |
|---|---|
| `substrate_resonator_dense_capacity_ksweep_v1_n4096` | 2026-06-04T15:18:46 |
| `substrate_resonator_dense_capacity_ksweep_v1b_n4096` | 2026-06-04T15:21:24 |
| `substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512` | 2026-06-04T15:32:39 |

These do NOT have valid metrics; they aren't verdict-candidates. Verdict_handler would just label them UNKNOWN/INFRA_FAILURE.

## Pattern signal

- **Mode-4 resonator falsifier** (v1 + v1b both failed) — script issue, not a substrate question
- **CFRPE+STDP heterogeneous superadditive** — failed first try

Both come from the post-cycle-67 routing batch (`routing_mode4_resonator_falsifier_test_2026-06-04.md` + `routing_cfrpe_stdp_superadditive_test_2026-06-04.md`). My guess: a recent script change broke something shared (helper import, GPU template enforcement, or a missing constant).

## What I'm asking

Before re-shipping any anchor from this routing batch:

1. **SCP the failed run logs** back from marsh@home and diagnose. Common failure modes for substrate experiments:
   - Missing `assert cuda` or `device='cuda'` (GPU template lint)
   - ASCII violation in print/verdict_msg (Windows cp1252 stdout crash; see [[feedback-ascii-only-in-scripts]])
   - Helper import mismatch from a refactored module
   - Missing PROT-022 self-test cells
   - Numerical NaN at unusual `K` or `p` values (resonator K-sweep at K=1 is a known sharp edge)

2. **Fix at the source** (not workaround per-anchor). If two consecutive v1 + v1b failed the same way, it's structural.

3. **Re-ship only after smoke + self-test pass on the runner**. Don't ship 3+ variants at once from a routing batch that hasn't yet produced one clean run.

## Not a scope problem, an engineering problem

These are good experiments to run (mode-4 resonator falsifier is a real Research-handed question, and CFRPE+STDP heterogeneous superadditivity is the right follow-up to cycle 67's cfrpe+sparse MIDDLE_BAND finding). They just need the script bug fixed before they run.

## MANDATORY: re-ship after fix

**User-directed (2026-06-04 ~15:42): all 3 failed anchors MUST be re-shipped successfully once the script bug is diagnosed.** Do not silently drop them. They carry real science questions (resonator mode-4 falsifier + heterogeneous-arch superadditivity), so a runner failure is NOT a verdict — it's a temporary block on those data points.

Track in your `notes/exp_dev_to_orchestrator_shipped_<date>_<cycle>.md` result file:
- `substrate_resonator_dense_capacity_ksweep_v1_n4096` — RE-SHIPPED or DEFERRED-with-reason
- `substrate_resonator_dense_capacity_ksweep_v1b_n4096` — RE-SHIPPED or DEFERRED-with-reason
- `substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512` — RE-SHIPPED or DEFERRED-with-reason

If you choose to consolidate or simplify (e.g. ship the cleanest variant only, drop a redundant `v1b`), say so explicitly and explain why. Don't drop silently.

## Lower-priority observation

CPU runner has one item still running for ~1h (`substrate_trained_mini_lm_readout_fix_nsweep_v2_capped`, started 14:45). That's the n_steps-scaled rescue for the cycle-57 readout-fix HF — long is expected. No action needed; let it land.

## State (orchestrator-side)

- cap_map v399
- HONEST 843
- LVH 217
- Queue: GPU empty + idle ~50 min; CPU 1 running 2 pending
- No verdicts pending from me

---

**END.** No priorities file from me this cycle — your existing routings + the bug-fix above are plenty. Surface back via your next `notes/exp_dev_to_orchestrator_shipped_*.md` when the failures are diagnosed + script(s) re-shipped.
