# Strategy response to testbed: PP-8 Round 4 D1-1 + Option A authorized

**Date**: 2026-06-01
**Filed by**: strategy_scribe (on behalf of orchestrator)
**Trigger**: v1+v1' bundle HARD-PASS (val=38.2%, 391x random, loss decrease 98.1%) per `notes/testbed_pp8_week2_phase25_v1_v1prime_2026-06-01.md`; cap_map v316 -> v317 PP-8 LIFT fired; Round 4 dispatch pre-authorized.
**Pause state**: ABSENT; all operations proceed normally.
**Cap_map version at time of filing**: v317.

Per [[feedback-no-experiment-design-in-prompts]]: this file names ANCHORS + POINTERS only. Testbed determines exact implementation.

---

## AUTHORIZED 2-PRONGED PARALLEL DISPATCH

### Prong 1: D1-1 Frozen-random hidden-state control (PIVOT TEST)

**Purpose**: Discriminate Mechanism 1 (M1-dominant: Phi-3 hidden states unnecessary; random vectors sufficient) from Mechanism 2 (M2 load-bearing: Phi-3 semantic geometry required).

**Anchor pointer**: `d1_1_frozen_random_hidden_state_control`

**Substrate-product reading**: If M1-dominant (random vectors within 8pp of 38.2%), Phi-3 is unnecessary overhead; substrate SimHash projection + soft-attention does the work. If M2 load-bearing (delta > 23pp), Phi-3 semantic geometry is the signal source; substrate-LLM coupling is architecturally necessary.

**Tier hint**: CPU or cheap H100 (~$0.50-1); ~30 min wall-time.

**Pre-reg**:
- HARD-PASS (M1-dominant): val_random >= 30% (within 8pp of v1+v1' baseline 38.2%)
- HARD-FAIL (M2 load-bearing): val_random < 15% (delta from v1+v1' > 23pp)
- MIDDLE-BAND: val_random 15-30% (partial signal; escalate to user)

**Context pointers**:
- `notes/testbed_pp8_week2_phase25_v1_v1prime_2026-06-01.md` (v1+v1' baseline for comparison)
- `notes/research_pp8_round4_3_drills_synthesis_2026-06-01.md` (Round 4 decision tree)

**Deliverable**: `notes/testbed_pp8_week2_d1_1_frozen_random_2026-06-01.md`

**Autonomy**:
- Exact implementation of frozen-random Gaussian (one reproducible seed per key_idx; record seed in manifest)
- All other setup identical to v1+v1' (SimHash projection + soft-attention + Phase 2.5 pipeline)
- SCP-back-hardened per [[feedback-always-verbose-remote-dispatch]]
- ASCII-only per [[feedback-ascii-only-in-scripts]]
- Per-experiment --timeout per [[feedback-per-experiment-timeout-required]]
- Honest verdict per [[feedback-verdict-msg-honest-reread]]
- Framing: M1-dominant and M2 load-bearing are EQUALLY LEGITIMATE outcomes; do NOT pre-frame either as positive per [[feedback-no-smoke-preframing-in-task-prompts]]

---

### Prong 2: Option A - Path 1a v2 held-out generalization test

**Purpose**: Test Mechanism 2 (LLM embedding geometry inheritance) on truly held-out keys not in the training overlap set.

**Anchor pointer**: `option_a_held_out_generalization_test`

**Substrate-product reading**: HARD-PASS confirms substrate LLM coupling generalizes beyond overlap condition; unblocks D3-Path-A KV-cache integration smoke. HARD-FAIL means coupling is overlap-dependent; architectural implications for Phase 3.

**Tier hint**: H100; ~$1-2; ~15 min wall-time.

**Pre-reg**:
- HARD-PASS (Mechanism 2 confirmed): held-out val >= 25% AND held-out / train-overlap ratio >= 0.5
- HARD-FAIL (Mechanism 1 load-bearing or FM-5 train/val leak): held-out val < 5% OR ratio < 0.3
- MIDDLE-BAND: val 5-25% or ratio 0.3-0.5 (partial inheritance; escalate to user)

**Context pointers**:
- `notes/testbed_pp8_week2_phase25_v1_v1prime_2026-06-01.md` (v1+v1' result baseline)
- `notes/research_pp8_v1_v1prime_outcome_analysis_2026-06-01.md` (Mechanism 1+2 analysis)
- `notes/research_pp8_round4_3_drills_synthesis_2026-06-01.md` (Round 4 decision tree)

**Deliverable**: `notes/testbed_pp8_week2_option_a_held_out_2026-06-01.md`

**Autonomy**:
- Dataset: `dataset_v1` (original 1000 held-out keys; NOT overlapping `dataset_v1c`)
- Eval pool-mask: existing per f707662 commit
- SCP-back-hardened per [[feedback-always-verbose-remote-dispatch]]
- ASCII-only per [[feedback-ascii-only-in-scripts]]
- Per-experiment --timeout per [[feedback-per-experiment-timeout-required]]
- Honest verdict per [[feedback-verdict-msg-honest-reread]]

---

## PRE-AUTHORIZED CONDITIONAL DISPATCH (testbed executes atomically on outcomes)

**If D1-1 M1-dominant AND Option A HARD-PASS**:
- SKIP D2 (Phi-3-specific layer/precision investigation moot)
- Authorize D3-Path-A KV-cache integration smoke (~$10-15 + 3-4 eng-days)
- File `notes/testbed_pp8_round4_d3_path_a_authorized_<date>.md`

**If D1-1 M2 load-bearing AND Option A HARD-PASS**:
- Authorize D2-1+D2-2 layer x precision sweep (~$12-15 combined)
- Authorize D3-Path-A KV-cache smoke in parallel
- File `notes/testbed_pp8_round4_d2_and_d3_authorized_<date>.md`

**If Option A HARD-FAIL (regardless of D1-1)**:
- DEFER D2 and D3-Path-A
- Authorize D1-2 layer ablation (~$3-6)
- Escalate to user/research for architecture rescue path decision
- File `notes/testbed_pp8_round4_option_a_fail_escalation_<date>.md`

**If D1-1 MIDDLE OR Option A MIDDLE**:
- File deliverable + escalate to user; no auto-iteration

---

## PARALLEL DISPATCH NOTE

Both D1-1 and Option A are independent; dispatch simultaneously for ~$1.50-3 marginal total.

Cumulative cloud today: ~$11.58 -> ~$14 of $50 testbed-check-in cap.

---

## ENFORCEMENT

- ASCII-only per [[feedback-ascii-only-in-scripts]]
- Per-experiment --timeout per [[feedback-per-experiment-timeout-required]]
- Honest verdict per [[feedback-verdict-msg-honest-reread]]
- No pre-framing of either outcome as positive per [[feedback-no-smoke-preframing-in-task-prompts]]
- SCP-back hardened per [[feedback-always-verbose-remote-dispatch]]
- Both dispatches simultaneously (independent)
