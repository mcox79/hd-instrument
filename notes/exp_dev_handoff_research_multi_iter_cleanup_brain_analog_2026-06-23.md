# exp_dev hand-off — research: multi-iter cleanup brain-analog 2x drill

**Filed-by:** Research (Opus 4.7 / 1M)
**Trigger:** `notes/research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md`
**Pause state:** check `data/orchestrator_paused.flag` before dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: anchor candidates only; exp_dev owns cell-design.

---

## Anchor candidates (rank-ordered)

### PRIMARY — `iterative_cleanup_cue_clamped_v1`

**Substrate-product reading:** cue-clamped multi-iter cleanup (`y_{t+1} = normalize(alpha * y_0 + (1-alpha) * softmax(beta * y_t @ cb.T) @ cb)`) — adds persistent `y_0` re-injection term to `hdlab/iterative_attractor.py`. Brain-canonical mechanism matching CA3 perforant-path drive + Hasselmo retrieval phase + Attractor LM (arXiv:2605.12466 +46.6% perplexity).

**Anchor pointer:** modify lines 105-107 of `hdlab/iterative_attractor.py`; add `alpha` parameter (default 0.5); capture `q0` at entry; replace `state = _l2_normalize(_softmax(...) @ cb_norm)` with `state = _l2_normalize(alpha * q0 + (1.0 - alpha) * _softmax(...) @ cb_norm)`.

**Tier hint:** smoke at N=2048 (~10 min CPU laptop, numpy). Cell-author smoke + Fix #17 measurement on laptop is FINE here (small N; not matmul-bound).

**Why now:**
- This is the rescue for the multi-iter cleanup HARD_FAIL that closed off a major substrate-as-LM lever.
- 2-line code edit on existing primitive; reuses entire parent cell harness.
- Direct lit precedent (arXiv:2605.12466 2026) showing +32-46% LM perplexity lift on standard Transformer with this exact mechanism gap.
- P_deflated = 0.50 for HARD_PASS; either way (PASS or FAIL) closes a major exploration axis definitively.
- HARD_PASS opens substrate-as-LM lever; HARD_FAIL closes the multi-iter direction structurally with brain-canonical mechanism IMPLEMENTED CORRECTLY → defensible structural-closure atom.

**Pre-reg HARD bands (sacrosanct):**
- HARD_PASS: best ARM_CLAMPED accuracy >= ARM_SINGLE_STEP + 0.05 absolute AND cv across 3 seeds <= 0.10 AND monotonic iteration-vs-accuracy curve (no overthinking dip)
- HARD_FAIL: best ARM_CLAMPED matches ARM_SINGLE_STEP within +/- 0.02 across alpha in {0.3, 0.5, 0.7}
- MIDDLE_BAND: 0.02-0.05 partial lift; queue production scale

**Suggested arms:**
- ARM_CURRENT (alpha=0.0) — reproduces current self-consistent HARD_FAIL
- ARM_CLAMPED_ALPHA_03 / 05 / 07 — brain-canonical sweep
- ARM_SINGLE_STEP — control / floor
- 3 seeds = {7, 17, 23} per substrate convention

**Discriminator:** ARM_CLAMPED_ALPHA_05 vs ARM_SINGLE_STEP on cleanup-recovery accuracy at noise SNR=2dB.

---

### SECONDARY — conditional on PRIMARY HARD_PASS: `iterative_cleanup_cue_clamped_production_v1`

**Substrate-product reading:** if PRIMARY HARD_PASSes, re-test all 5+ prior cleanup-side HARD_FAILed cells (att1, CA3 cell, multi-iter at N=8192) with cue-clamping enabled. Possible chain-grade pipeline revival.

**Anchor pointer:** patch all in-tree experiment cells that call `iterative_cleanup` to call `iterative_cleanup_cue_clamped` with alpha=0.5; re-run on overnight queue at production scale.

**Tier hint:** queue at production N=8192 on overnight_queue / remote_cpu_queue (Fix #14 ≤3-in-flight budget; route per Fix #24 if GPU-applicable).

**Why now:** if PRIMARY confirms the brain-canonical mechanism is correct, revival of 5+ prior HARD_FAILs at scale is the natural follow-up. Possible compound lift with cf-RPE chain-grade arm.

---

### TERTIARY — conditional on PRIMARY HARD_FAIL: `multi_iter_cleanup_structural_closure_v1`

**Substrate-product reading:** definitive falsification cell that closes multi-iter as substrate-LM lever forever. 3-arm comparison: ARM_OMP_CLEANUP (sparse-decompose) + ARM_CLAMPED_RESCUE (re-run) + ARM_NO_CLEANUP (zero-iter baseline).

**Anchor pointer:** reuse parent multi-iter cell with 3 arms; ARM_NO_CLEANUP is the structural floor.

**Tier hint:** smoke at N=2048 first (~5 min CPU); if no arm beats no-cleanup, ship structural-closure atom.

**Why now:** if cue-clamping fails (brain-canonical mechanism implemented correctly + still no lift), multi-iter is structurally not a substrate-as-LM lever. Worth definitive closure rather than ambiguous "didn't try hard enough" state.

**HARD_FAIL criteria:** ARM_OMP_CLEANUP AND ARM_CLAMPED_RESCUE both fail to beat ARM_NO_CLEANUP at production scale → atomize `multi_iter_cleanup_NOT_substrate_LM_lever_even_with_cue_clamping_brain_canonical_5plus_attempts`.

---

## Context pointers (file paths, no summaries)

- `notes/research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md` (parent research note)
- `notes/research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md` (predecessor; claim 3 verdict)
- `notes/research_2x_revival_ca3_lm_HF_2026-06-23.md` (CA3 cleanup-undoes-binding diagnosis; same root cause)
- `notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md` (orthogonal OMP / CAN cleanup directions)
- `hdlab/iterative_attractor.py` (the primitive to patch; lines 95-108 are the iteration loop)
- `data/exp_*_multi_iter_cleanup_*/metrics.json` (the HARD_FAIL referenced in trigger)
- arXiv:2605.12466 "Solve the Loop: Attractor Models for Language and Reasoning" (the SOTA precedent; +32-46% LM perplexity lift via cue-clamping)

---

## Contract section

Per `tools/orchestrator/agents/exp_dev.md` (and Fix #11 pipeline-template):
- Pre-flight `tools/predispatch_check.py iterative_cleanup_cue_clamped_v1` per Fix #26
- Smoke run on .venv per `reference_hd_instrument_cert_suite_requires_venv_not_system_python_duckdb`
- VET schema + REQUIRED_FIELDS pre-dispatch
- Commit cell + pre-reg to origin/main BEFORE remote dispatch (irrelevant here; cell is laptop-CPU-only)
- Post-dispatch verdict goes through verdict_handler with Step 0 honest re-read per Fix #28
- Atomic landing (Store + cert_ledger sequential foreground per `feedback_foreground_vs_background_for_sequential_store_ledger_writes`)

---

## Autonomy declaration

exp_dev decides:
- Smoke vs full dispatch order
- Whether to ship PRIMARY first then conditional SECONDARY/TERTIARY (recommended) OR PRIMARY + TERTIARY in parallel (more compute, faster definitive answer)
- Whether to add ARM_TEMP_SWEEP for compound discrimination (cleanup-iteration vs temperature)
- Exact discriminator-test design beyond the pre-reg HARD bands

Research has done the brain-analog mechanism derivation + 2-line code edit identification + pre-reg HARD bands; exp_dev owns the cell.
