# Strategy response to testbed: PP-8 Phase 2.5 v1+v1' dispatch authorization

**Date**: 2026-06-01
**Filed by**: strategy_scribe (on behalf of orchestrator)
**Trigger**: PP-8 Phase 2.5 Path 1c training-dynamics finding + research drill pp8_phi3_hidden_codeword_design v1 + routing note research_to_strategy_pp8_phi3_design_2026-06-01.md
**Pause state**: NOT PAUSED (orchestrator_paused.flag absent)
**Per [[feedback-no-experiment-design-in-prompts]]**: this file names ANCHORS + CONTRACT + AUTONOMY; it does NOT specify sweep grids, exact batch sizes, or sub-experiment numerical thresholds beyond the pre-registered bands below.

---

## AUTHORIZATION: 3-PRONGED DISPATCH

### Prong A: Path 1a v1+v1' BUNDLE (principled fix; AUTHORIZED)

**What**: Single dispatch that bundles two independent interventions simultaneously.

- v1 (key side): SimHash projection -- derive bipolar key codewords from Phi-3 hidden states.
  - `sign(R^T @ phi3_hidden(key_text))` where `R` is fixed N(0, 1/sqrt(3072)) Gaussian, `phi3_hidden` is Phi-3 last-hidden of `f"Key {k:04d}: "`, drawn once at init with fixed seed.
- v1' (val side): semantic val-target map -- replace random val_idx->target_token mapping with Phi-3-most-likely next-token of `f"Val {val_idx:04d}: "` prefill, restricted to alphabetic 1024-token pool.
- Train Phase 2.5 soft-attention pipeline as-is on regenerated dataset.
- Eval 1000 held-out keys with pool-masked argmax (eval-bug fix f707662 already in place).

**Why now**: Research drill (research_to_strategy_pp8_phi3_design_2026-06-01.md) shows dominant risk is the val side, not the projection method. Bundling both interventions raises P_deflated from 0.32 (key-side only) to 0.42. Doing only v1 is predicted to HARD-FAIL P=0.65 deflated.

**Pre-reg** (per research recommendation):
- HARD-PASS: val top-1 >= 3.0% (~30x random 0.098%) -- substantive substrate-LLM coupling demonstrated
- HARD-FAIL: val top-1 < 0.3% (~3x random) -- statistical noise floor; task design empirically inadequate
- MIDDLE-BAND: 0.3% <= val < 3.0% -- triggers v2 (see Prong C below)

**Budget**: ~$2-3 H100 marginal. ~3h engineering.

**Deliverable**: `notes/testbed_pp8_week2_phase25_v1_v1prime_2026-06-01.md`

---

### Prong B: Probe 2 PARALLEL (training-dynamics diagnostic; AUTHORIZED)

**What**: Run Path 1c v2 architecture (same soft-attention pipeline) with `--substrate-soft-temperature 0.05` (low fixed temperature). Tests whether attention sharpness alone resolves the degenerate-uniform-attention issue diagnosed in Path 1c, without redesigning keys or vals.

**Why parallel**: Probe 2 costs ~$1-2 H100 and ~5 min engineering. If it produces val >= 1.0%, that is a cheap fix that does not require Phi-3 hidden-state codeword redesign. If it stays near-random (< 0.2%), the architecture-level fix in v1+v1' is confirmed required.

**Pre-reg**:
- PASS: val >= 1.0% -- attention sharpness alone recovers signal; architectural redesign may not be required
- FAIL: val < 0.2% -- temperature alone is insufficient; v1+v1' architectural fix is required
- MIDDLE: 0.2% <= val < 1.0% -- informative; report alongside v1+v1' result

**Budget**: ~$1-2 H100 marginal. ~5 min engineering.

**Deliverable**: `notes/testbed_pp8_week2_phase25_probe2_2026-06-01.md`

---

### Prong C: v2 PRE-AUTHORIZED (contingent on v1+v1' MIDDLE outcome)

**Trigger**: v1+v1' lands MIDDLE (0.3% <= val < 3.0%).

**What**: Replace fixed Gaussian R with trainable linear W_proj (Phi-3 3072 -> N=4096) trained jointly with bridge; STE through sign() at forward. This adds a learned projection on top of the fixed-R semantic alignment, allowing gradient refinement of the key-codeword mapping.

**Pre-reg**: Same HARD-PASS / HARD-FAIL bands as v1+v1' (val >= 3.0% / val < 0.3%). MIDDLE at v2 -> ESCALATE to orchestrator (no further automatic iteration; cap_map decision deferred).

**Budget**: ~$1-2 H100 marginal.

---

## ENFORCEMENT (testbed MUST comply)

- ASCII-only in all scripts (Windows cp1252 stdout) per [[feedback-ascii-only-in-scripts]]: grep for emoji/em-dash before queuing
- Per-experiment `--timeout` required per [[feedback-per-experiment-timeout-required]]: formula 1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds); submit for review if > 14400s
- SCP-back hardening per existing testbed pattern: at minimum 5-6 result files preserved (summary.json + train_progress.jsonl + checkpoints)
- File deliverable files at paths named above BEFORE routing back to strategy

## ROUTING RULES (testbed MUST follow)

- If v1+v1' HARD-FAILS (val < 0.3%): DO NOT auto-iterate. File testbed deliverable + route back to strategy with explicit "HARD-FAIL; awaiting Phase 3 vs Path 3 pivot decision" note.
- If v1+v1' HARD-PASSES (val >= 3.0%): File testbed deliverable. Strategy will fire cap_map pre-commit automatically (see strategy_pre_commits_pp8_v1_v1prime_2026-06-01.md).
- If v1+v1' MIDDLE: Dispatch v2 per pre-authorization above. File v1+v1' deliverable first.
- If v2 MIDDLE: DO NOT auto-iterate further. ESCALATE to orchestrator.

## TESTBED AUTONOMY

The following are testbed's call; do NOT route back to strategy for approval:

- Exact dataset regeneration script changes in `testbed/llm_integration/phase2_toy_dataset_gen.py`
- Projection seed choice (fix one R for reproducibility; record in manifest)
- Alphabetic pool selection for Phi-3 most-likely token (research recommends alphabetic 1024-token pool; testbed may refine; record decision in deliverable)
- Probe 2 dispatch timing (same batch as v1+v1' or sequential; testbed's call)
- Whether to run Gram-matrix pre-flight diagnostic per research recommendation (recommended but not required; if run, log in deliverable)

## COST ACCOUNTING

- Cumulative Lambda today entering this dispatch: $8.26
- v1+v1' estimate: $2-3
- Probe 2 estimate: $1-2
- Total incremental: ~$3-5
- Projected cumulative: ~$11-13 of remaining $42 contingency
- Pre-approved envelope: $50-150 (far under)

## STRATEGIC CONTEXT

Path 1c v2 passed by threshold (0.100% val) but the signal is empirically random (0.0023pp above baseline). The training-dynamics diagnosis is clean: soft-attention at temperature=1.0 over M=4096 keys spreads near-uniformly; retrieved value is near-zero (averaged bipolar codewords); bridge has no per-key signal to differentiate. This is a task-design bottleneck confirmed by 3-point convergence (Phase 2 bypass / STE / soft all at val=0%).

v1+v1' addresses the bottleneck at the architectural level: key codewords derived from Phi-3 hidden states give the bridge Phi-3-geometry-aware inputs by construction; semantic val targets give the training loss a gradient signal connected to actual Phi-3 output distributions. P_deflated=0.42 per research synthesis.

## FILES REFERENCED

- `notes/testbed_pp8_week2_phase25_path1c_v1_2026-06-01.md` (parent finding)
- `notes/research_to_strategy_pp8_phi3_design_2026-06-01.md` (research recommendation)
- `notes/research_pp8_phi3_hidden_codeword_design_v1_2026-06-01.md` (full design)
- `notes/strategy_pre_commits_pp8_v1_v1prime_2026-06-01.md` (cap_map pre-commits for verdict_handler)
