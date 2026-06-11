# exp_dev hand-off -- research: cls_2substrate_rescue_2x

Filed-by: research sub-agent
Date: 2026-06-11
Trigger: two_substrate_fastslow_cls HARD_FAIL cycle 228 (recent=0.689, old_consolidated=0.378,
         n=5 confirms cls_old=0.487 std=0.027); PROT-004/006 rescue sketches authorized

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors, rationale, and
context pointers. It does NOT specify implementation. Exp_dev reads the research note and
decides how to build each anchor.

Research note path: d:/AI/hd-instrument/notes/research_drill_cls_2substrate_rescue_2x_2026-06-11.md

---

## Pause state

Experiments are active (no pause flag expected). This handoff is for the exp_dev queue
pick-up cycle. CLS is the open Sprint-4 axis (3/4 v3.2 primitives seed-robust; CLS is
the remaining gap per v32_multiseed cls_old=0.487 std=0.027).

---

## Anchor candidates (rank-ordered)

### Anchor 1: cls_rescue4_dedicated_pass_cpu_v1

Substrate-product reading: RESCUE-4 from research note. Offline consolidation pass --
W_slow receives writes ONLY during a scheduled replay phase (every N_buffer=50 new items),
not at write time. W_fast handles all new writes. Temporal age-gating on retrieval blend:
beta=1.0 for fresh items (age < N_buffer), beta=0.0 for old items.

Tier hint: EXPLORATORY (same tier as cycle-228 Sprint-4 primitives).

Why-now: highest P_deflated of all rescues (0.48). Direct application of the temporal+contextual
meta-pattern (cycle 226, PP-350): every Sprint-3/4 HARD_PASS uses temporal mechanics;
RESCUE-4 adds temporal scheduling to CLS. Structural analogy to PP-349 (core_periphery
TEMPORAL REFRESH rescues recall from 0.002 to 1.000) -- same mechanic, CLS context.

Pre-reg bands:
  HARD-PASS: old_consolidated >= 0.80, recent_recall >= 0.90
  MIDDLE-BAND: old_consolidated 0.60-0.80 (partial; add RESCUE-2 on next iteration)
  HARD-FAIL: old_consolidated < 0.55 (mechanism does not help; try RESCUE-10)

### Anchor 2: cls_rescue24_combined_cpu_v1

Substrate-product reading: RESCUE-4 (temporal consolidation pass) + RESCUE-2 (asymmetric
capacity: N_slow=8192, N_fast=2048). Research note section 3 identifies this combination
as highest expected P_deflated overall (0.44). The ROME interference budget math (section 7.4)
shows that at N=1024, 100 replay items per pass already exceeds the safe editing budget
(~32). N_slow=8192 expands budget to ~91, clearing the interference ceiling.

Tier hint: EXPLORATORY.

Why-now: should follow cls_rescue4 if RESCUE-4 smoke lands MIDDLE_BAND (0.60-0.80). Can
also run in parallel with cls_rescue4 if CPU capacity allows. Asymmetric capacity is a
no-code-change from RESCUE-4 (just a different N parameter).

Pre-reg bands:
  HARD-PASS: old_consolidated >= 0.80, recent_recall >= 0.90
  MIDDLE-BAND: old_consolidated 0.65-0.80
  HARD-FAIL: old_consolidated < 0.55 (N_slow scaling does not help; capacity not the bottleneck)

### Anchor 3: cls_rescue5_retrieval_gated_cpu_v1

Substrate-product reading: RESCUE-5 from research note. Retrieval-gated transfer --
items with >= k_transfer (default 3) retrievals migrate from W_fast to W_slow. Items
below threshold stay in W_fast only. Builds on existing frequency-decay ledger (Sprint-2,
STATIC ROBUST). Only adds: "migrated" flag + W_slow accumulation at k_transfer threshold.

Tier hint: EXPLORATORY.

Why-now: P_deflated 0.42. Uses existing frequency-decay ledger with minimal new code.
Implements the biological synaptic tagging and capture mechanism (Frey and Morris 1997,
PP-11968991 2025). Directly addresses the root cause: W_slow should encode frequently-used
facts, not all facts equally.

Pre-reg bands:
  HARD-PASS: old_consolidated >= 0.80; P(W_slow correct | W_fast incorrect) >= 0.60
  MIDDLE-BAND: old_consolidated 0.60-0.80
  HARD-FAIL: old_consolidated < 0.55 (retrieval count not discriminating; test set lacks usage variation)

### Anchor 4: cls_rescue4_v32_composite_cpu_v1

Substrate-product reading: RESCUE-4 temporal consolidation pass composing with the
existing v3.2 wrapper (PP-357: per_role + write_lock + rs_parity). Validates that CLS
consolidation is compositional with the three Sprint-4 primitives already HARD_PASS.
Research note section 6 specifies the interaction: consolidation pass skips write-locked
items; W_slow gets its own RS-parity shards; per-role isolation means each role has its
own W_slow.

Tier hint: EXPLORATORY (same as PP-357 which it extends).

Why-now: if Anchors 1-3 confirm CLS rescue works, this anchor determines whether CLS
composes cleanly with the v3.2 unified wrapper. The product claim (multi-timescale memory
with per-role isolation, write-lock tiers, fault tolerance, AND consolidation) requires this.

Pre-reg bands:
  HARD-PASS: per_role >= 0.90, write_lock >= 0.95, rs_parity >= 0.95, old_consolidated >= 0.80
  MIDDLE-BAND: CLS old_consolidated 0.60-0.80 while other 3 maintain HARD_PASS levels
  HARD-FAIL: old_consolidated < 0.55 OR any of per_role/write_lock/rs_parity drops > 0.05
             from baseline (CLS consolidation interferes with wrapper primitives)

### Anchor 5: cls_rescue4_multiseed_cpu_v1

Substrate-product reading: RESCUE-4 temporal consolidation pass at n_seeds=5.
This is the multi-seed hardening run assuming Anchor 1 (RESCUE-4 smoke) HARD_PASS.
Matches the multi-seed standard set by v32_multiseed (n=5, PP-358) which confirmed
write_lock=1.000 std=0.0, per_role=1.000 std=0.0, 3x=0.988 std=0.008 across seeds.
CLS must hit the same bar to be declared seed-robust and Sprint-4 Sprint complete.

Tier hint: EXPLORATORY (multi-seed confirmation run; not a new architecture probe).

Why-now: seed-robustness is the Sprint-4 completion criterion per cycle-228 architecture.
Only run after Anchor 1 confirms the mechanism works.

Pre-reg bands:
  HARD-PASS: old_consolidated mean >= 0.80 std <= 0.03, recent_recall mean >= 0.90 std <= 0.03, n=5
  MIDDLE-BAND: mean passes but std > 0.05 (needs HP stabilization)
  HARD-FAIL: mean old_consolidated < 0.70 across seeds (mechanism not robust; structural issue)

---

## Context pointers (file paths, not summaries)

Research note: d:/AI/hd-instrument/notes/research_drill_cls_2substrate_rescue_2x_2026-06-11.md
Prior CLS full 5x drill: d:/AI/hd-instrument/notes/research_drill_continual_full_cls_5x_2026-06-10.md
Prior CLS 2x lift drill: d:/AI/hd-instrument/notes/research_drill_dual_cls_lift_2x_2026-06-10.md
Cycle-228 verdict strategy decisions: d:/AI/hd-instrument/notes/strategy_decisions_2026-06-11.md
  (line ~168: two_substrate_fastslow_cls HARD_FAIL entry and PROT-004/006 sketches)
  (line ~186: v32_multiseed MIDDLE_BAND entry confirming cls_old=0.487 std=0.027)
v3.2 unified wrapper HARD_PASS (PP-357): strategy_decisions_2026-06-11.md line ~180
core_periphery temporal refresh HARD_PASS (PP-349): strategy_decisions_2026-06-11.md line ~116
temporal+contextual multiseed HARD_PASS (PP-350): strategy_decisions_2026-06-11.md line ~120
Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

Exp_dev reads the research note for mechanism detail. Exp_dev builds each anchor per its
own standard cell construction protocol (pre-dispatch speed+harden+progress audit).
Exp_dev ships anchors in order 1 -> 2 -> 3 -> 4 -> 5, gated on prior results per
the pre-reg decision tree (section 4 of research note).

If Anchor 1 HARD_FAIL (old_consolidated < 0.55): pivot to RESCUE-10 (hippocampal indexing,
section 2 of research note) before proceeding to Anchor 2. File a new routing note.

If Anchor 1 MIDDLE_BAND (0.60-0.80): proceed immediately to Anchor 2 (RESCUE-24 combined
capacity + consolidation pass) without waiting for Research to be re-invoked.

If any anchor produces unexpected behavior that the pre-reg does not anticipate:
escalate to Research via strategy_request_to_research note, not via in-cell workaround.

---

## Autonomy declaration

Exp_dev has full autonomy to:
- Choose N_buffer, alpha, k_transfer hyperparameters within ranges implied by research note
- Implement the consolidation pass function in any form consistent with the mechanism description
- Decide test item count and stream length within CPU budget
- Sequence anchors per the gating logic above

Exp_dev does NOT decide:
- Whether to accept a MIDDLE_BAND result as Sprint-4 complete (that is Orchestrator/verdict_handler)
- Whether to add new rescue paths not listed here (escalate to Research if the 5 anchors exhaust)
