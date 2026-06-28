# exp_dev hand-off — research: drill_B_hersche_block_sparse_hierarchical

**Filed by.** research (Opus 4.7-1M)
**Date.** 2026-06-28
**Trigger.** `d:/AI/hd-instrument/notes/research_drill_B_hersche_block_sparse_hierarchical_2026-06-28.md` recommends `CLOSURE_PREMATURE_ITERATE` for hierarchical-planning capability box (3 prior HARD_FAILs all used dense encoding; block-sparse axis untested). Companion to Drill A: `d:/AI/hd-instrument/notes/exp_dev_handoff_research_bacon_roy_option_critic_2026-06-28.md` (if Drill A author filed one).

**Pause state.** Honors `d:/AI/hd-instrument/data/orchestrator_paused.flag`. If paused, file only; do not ship.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off provides ANCHOR POINTERS + context paths + tier hints + why-now. Experiment design (arms structure, smoke gate, pre-reg bands) is exp_dev's call. Anchor candidates below are RANKED but not prescriptive.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 (TIER: chain-grade-eligible; novel-composition) — `substrate_hierarchical_block_sparse_v1`

**Anchor pointer.** `d:/AI/hd-instrument/data/exp_substrate_hierarchical_block_sparse_v1/metrics.json` (new anchor).

**Substrate-product reading.** If HARD_PASS: substrate gains block-sparse compositional planning capability + a 4th datapoint demonstrating Hersche-line GSBC encoding is the right representation for multi-mechanism composition on substrate. If HARD_FAIL alongside Drill A: 2x-drill discipline satisfied for closure; capability-closed atom can be filed with cross-drill evidence (orthogonal axes both falsified).

**Tier hint.** Default classification at smoke: **MIDDLE_BAND** (P_deflated=0.30; thrice-burned mechanism class; novel-composition cap). Skunkworks may tier UP to chain-grade if substrate-physics signal is clean (block-locality discriminator fires; ARM_BLOCK_SPARSE_RANDOM_BLOCKS at floor). NEVER tier UP without Skunkworks-VET per A5 role separation.

**Why-now.** The 2x-drill discipline (`feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28.md`) requires this cell + Drill A cell to BOTH return before closure-atom is final. The atomization `hierarchical_planning_substrate_native_closed_three_failures_2026-06-28` (commit `eda3d108`) is currently marked preliminary; Drill B verdict is the second of two required gates. Cell is cheap (~10min wall on Local CPU) and durable (answers "is block-sparse the right encoding for compositional planning?" which is broader than hierarchical planning alone).

**Substrate primitives already chain-grade for this cell (MEASURED@ verified):**
- `d:/AI/hd-instrument/data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json` — block-local sparse resonator HARD_PASS K4=1.00 K8=1.00
- `d:/AI/hd-instrument/data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json` — hierarchical 2-level partition routing CHAIN_GRADE_AT_M_10M 2LEVEL=0.9783

**Novel substrate primitives needed (cell-author may need to add to `hdlab/`):**
- Block-aware cleanup: per-block ℓ∞ similarity (Hersche 2023 metric) instead of dense cosine. ~50 LOC wrap around `hdlab/cleanup.py`
- Block-restricted iter_cleanup_chain: confine the multi-hop chain to a designated block subset per option. ~30 LOC wrap around `hdlab/multi_hop.py`

**Predicted compute.** Smoke at N=8192, L=64 blocks, 6 arms × 1 seed × 20 goals: ~30s pure compute → ~150s wall on Local CPU. Full at 3 seeds × 50 goals: ~10min wall. No remote needed; routing rule N_DIM≥8192 satisfied but matmul load is low.

---

### Anchor 2 (TIER: defer; only fire if Anchor 1 HARD_FAILs) — `substrate_hierarchical_option_critic_block_sparse_v1`

**Anchor pointer.** `d:/AI/hd-instrument/data/exp_substrate_hierarchical_option_critic_block_sparse_v1/metrics.json` (new anchor; 5th attempt; combines Drill A + Drill B mechanisms).

**Substrate-product reading.** Both mechanism (learned π/β) and encoding (block-sparse) axes are tested simultaneously. This is the MAXIMUM-INFORMATION cell if Anchor 1 HARD_FAILs but the block-sparse encoding shows partial lift (e.g., ARM_BLOCK_SPARSE_POLICY_ONLY > 0.10). If Drill A's option-critic cell also HARD_FAILs at single-encoding, the joint cell may rescue.

**Tier hint.** P_deflated=0.20 (compound novel; both axes simultaneously). Default MIDDLE_BAND; do NOT tier UP without Skunkworks-VET.

**Why-now.** DEFER until Anchor 1 verdict + Drill A's option-critic cell verdict. Composite cell only earns budget if BOTH single-axis cells produce signal (HARD_PASS or MIDDLE_BAND) suggesting joint composition is fruit-bearing.

---

## CONTEXT POINTERS (file paths; not summaries)

**Research drill:**
- `d:/AI/hd-instrument/notes/research_drill_B_hersche_block_sparse_hierarchical_2026-06-28.md` (this drill; sections 2-4 contain lit-scan + mechanism diagnosis + cell architecture)
- `d:/AI/hd-instrument/notes/research_drill_A_bacon_roy_option_critic_hierarchical_2026-06-28.md` (parallel Drill A; option-critic angle)
- `d:/AI/hd-instrument/notes/research_sutton_precup_options_hierarchical_planning_redesign_2026-06-28.md` (original v3 cell design rationale)
- `d:/AI/hd-instrument/notes/research_drill_sparse_key_composition_partners_2x_2026-06-06.md` (prior block-sparse / hierarchical VQ composition analysis; section 2c on block-sparsity nesting + section 1b construction A on independent per-row masks)

**Prior HARD_FAILs (must NOT be re-run; cell-author verifies they replicate as regression baseline):**
- `d:/AI/hd-instrument/data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/metrics.json` — TREE=0.000
- `d:/AI/hd-instrument/data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke/metrics.json` — BOTH=0.000
- `d:/AI/hd-instrument/data/exp_substrate_hierarchical_options_v1_smoke/metrics.json` — OPTS=0.000 (THIRD_FAILURE_GATE)
- `d:/AI/hd-instrument/preregs/2026-06-28_substrate_hierarchical_options_v1.md` (v3 pre-reg; ARM_CLOSED_FORM_BASELINE in this cell IS the regression baseline)

**Substrate primitive existence proofs:**
- `d:/AI/hd-instrument/data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json`
- `d:/AI/hd-instrument/data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json`
- `d:/AI/hd-instrument/experiments/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000.py` (reference implementation for block-local sparse cleanup)
- `d:/AI/hd-instrument/hdlab/cleanup.py` (dense cleanup primitive; cell-author wraps/extends)
- `d:/AI/hd-instrument/hdlab/multi_hop.py` (iter_cleanup_chain; cell-author wraps with block-restriction)
- `d:/AI/hd-instrument/hdlab/store.py` (partition routing primitives; reuse for per-option block assignment)

**Discipline pointers:**
- `C:/Users/marsh/.claude/projects/d--AI/memory/feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28.md` (parent discipline)
- `C:/Users/marsh/.claude/projects/d--AI/memory/feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26.md` (smoke at N=8192 required; do NOT run smoke at N=1024 then full at N=8192)
- `C:/Users/marsh/.claude/projects/d--AI/memory/feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive_2026-06-26.md` (smoke must FIRE discriminator: ARM_BLOCK_SPARSE_OPTIONS_FULL must distinguish from ARM_BLOCK_SPARSE_RANDOM_BLOCKS at smoke or band-floor=inconclusive applies)
- `C:/Users/marsh/.claude/projects/d--AI/memory/feedback_cardinality_ok_mandatory_prereg_field_for_sweep_axis_cells_2026-06-26.md` (pre-reg must declare EXPECTED_N_UNITS + HARD_FAIL_CARDINALITY_BREACH for 6-arm cell)

---

## CONTRACT

exp_dev implements `experiments/exp_substrate_hierarchical_block_sparse_v1.py` with:

- ASCII-only output (`feedback_ascii_only_in_scripts` obsoleted but practice maintained for scripts; Unicode in research notes is fine)
- L1-L4 hardening per substrate discipline: L1 early metrics-write at init / L2 per-arm runtime / L3 outer try / L4 import-sentinel
- atomic-final-metrics-write (tmp + os.replace) per META_RULE_AH
- cardinality_ok per pre-reg: EXPECTED_N_UNITS_SMOKE + EXPECTED_N_UNITS_FULL declared with HARD_FAIL_CARDINALITY_BREACH gate
- SHA-256 per-arm seq trace; arms_distinct == True required
- No silent except blocks (record + halt OR re-raise; per `feedback_three_smoke_disciplines_2026-06-26`)
- Discriminator FIRES at smoke (block-sparse beats random-block-assignment by ≥0.15 at smoke N=8192 or smoke is INCONCLUSIVE not HARD_FAIL)
- Number tagging: MEASURED@ for substrate primitive reuse; HYPOTHESIZED@ for block-sparse-on-planning generalization; THEORETICAL@ for Frady-Sommer-Kanerva capacity bound
- Pre-reg HARD_PASS / MIDDLE_BAND / HARD_FAIL bands locked at module init per `feedback_envelope_expansion_fail_bands`
- Self-test mode (`--self-test`): N=1024, L=8 blocks, 1 seed, 4 goals, depth=4; verify all 6 arms produce non-empty per-arm dict, no NaN, arms_distinct, RANDOM<0.10

Verification scaffold-free witness: `verification/test_block_sparse_options.py` — synthetic 3-option BlocksWorld where each option's β_target is uniquely identifiable by its block-restricted cosine signature (oracle test: cleanup returns correct β_target index ≥0.95 of the time at smoke N).

---

## AUTONOMY

exp_dev's call on:
- Exact L (block count) and per-block sparsity k (suggested L=64 blocks × 128-dim each at k=8 active per block; cell-author may choose L=32 × 256-dim if smoke shows L=64 has too-narrow blocks)
- Number of blocks per option (suggested 16 of 64; reserve 16 for state/control)
- Whether to use Hersche's ℓ∞ similarity OR cosine restricted-to-block (ℓ∞ is closer to Hersche paper; cosine matches substrate's existing cleanup; cell-author chooses based on cheap synthetic test)
- Whether to add ARM_BLOCK_SPARSE_OPTION_CRITIC composite arm (would compound Drill A + Drill B in single cell; default OFF unless Drill A cell already HARD_FAILed)
- Queue choice (Local CPU recommended; ~10min wall well under remote routing threshold)

**Hard rules (per discipline pointers above):**
- pre-existing dependency check: confirm `hdlab/cleanup.py` and `hdlab/multi_hop.py` exist before adding wraps
- ship_name uniqueness check pre-ship per `feedback_ship_name_collision`
- predispatch verify-the-referent gate per Fix #26: run `python d:/AI/hd-instrument/tools/predispatch_check.py substrate_hierarchical_block_sparse_v1` before any spawn
- post-ship REMOTE VERIFY per role contract: peek per-arm metrics, do NOT propagate verdict_msg framing without per-arm verification (Fix #28)
- foreground execution for sequential Store+cert_ledger writes per `feedback_foreground_vs_background_for_sequential_store_ledger_writes`

**Composite cell (Anchor 2) is DEFERRED.** Do NOT ship Anchor 2 until Anchor 1 verdict AND Drill A's `exp_substrate_hierarchical_option_critic_v1` verdict are both in. Composite earns budget only if BOTH single-axis cells produce signal.

---

## VERDICT IMPLICATIONS (for verdict_handler)

- ARM_BLOCK_SPARSE_OPTIONS_FULL HARD_PASS ≥ 0.30 with discriminator lift over RANDOM_BLOCKS ≥ +0.15 → file as MIDDLE_BAND default; Skunkworks-VET tiers UP to chain-grade-eligible if block-locality discriminator clean; capability box stays OPEN; retract `hierarchical_planning_substrate_native_closed_three_failures_2026-06-28` atom
- ARM_BLOCK_SPARSE_OPTIONS_FULL HARD_FAIL ≤ 0.10 alongside Drill A's HARD_FAIL → 2x-drill discipline satisfied; capability-closed atom confirmed; both drills cited in atom evidence
- MIDDLE_BAND at smoke → exp_dev's call on whether to push to full (3 seeds, 50 goals) for tier upgrade or defer pending Drill A verdict

Final research-side line: `RECOMMENDATION: CLOSURE_PREMATURE_ITERATE`
