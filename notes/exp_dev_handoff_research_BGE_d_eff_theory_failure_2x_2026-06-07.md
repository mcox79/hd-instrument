# exp_dev hand-off -- research: BGE-large d_eff theory failure 2x drill

Filed-by: research sub-agent
Trigger: notes/research_drill_BGE_d_eff_theory_failure_2x_2026-06-07.md (cycle 141 BGE-large HF + 2x negative-result rule)
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY. Exp_dev designs anchors, sweep parameters, thresholds, and queue placement -- NOT this file.

---

## WHY NOW

Cycle 141 returned BGE-large cap=40 against Drill 5 prediction of 150 (3.8x miss). The 2x research drill identifies the root cause as a compound failure: (a) Hebb write rule cross-talk penalty on correlated inputs, and (b) encoder cone collapse reducing the working effective dimensionality (Participation Ratio) to ~50-80 vs d_eff=114.8. Two structural tests can isolate the contributions of each factor, with implications for the encoder selection framework and production architecture.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 -- BGE-large geometry audit (CPU, ~5 min)
Pointer: research note Section 7, Test 1
Substrate-product reading: measures PR (Participation Ratio) and rho_eff (mean pairwise cosine similarity) for BGE-large vs MiniLM vs Llama-3.2-1B on 500-sample corpus. Determines whether cone collapse (PR < 80) and/or correlation penalty (rho > 0.25) are active. Required before committing to BGE-large encoder decisions.
Tier hint: laptop CPU; ~5 min wall; no GPU needed
Why now: geometry audit is the cheap screen that separates the two failure modes. Results directly inform whether F6 (pseudoinverse test) is worth running and what cap to expect.

### Anchor 2 -- BGE-large write-rule x whitening factorial (GPU, ~30 min)
Pointer: research note Section 7, Test 2
Substrate-product reading: 2x2 factorial {Hebb, Pseudoinverse} x {no-whiten, whiten} at N=2048. Isolates write-rule contribution to cap=40 gap. If cap_pinv_white > 80, write rule bias explains 2-3x of the gap. If cap_pinv_white < 50, encoder geometry is the binding constraint.
Tier hint: remote GPU runner; ~30 min wall
Why now: F6 was already mentioned as the next test in cycle 141 context. This anchor is the structural pre-registration of F6.

### Anchor 3 -- E5-large-v2 geometry audit + cap smoke (CPU then GPU, ~45 min)
Pointer: research note Section 7, Test 3; Section 5.3 Priority 1
Substrate-product reading: E5-large-v2 uses weak supervised pre-training before strong fine-tuning, predicted to preserve more isotropy than BGE-large. If E5 PR > 120 AND rho < 0.20, run full cap measurement. Tests whether training regime controls cone collapse.
Tier hint: CPU geometry screen first; GPU cap test only if geometry passes
Why now: opens a new candidate encoder that may outperform BGE-large at same 1024-dim spec.

---

## CONTEXT POINTERS

Research note: d:/AI/hd-instrument/notes/research_drill_BGE_d_eff_theory_failure_2x_2026-06-07.md
BGE-large cap measurement: cycle 141 (data/exp_BGE_large_*/metrics.json or equivalent)
MiniLM baseline: cycle 138 (cap=122)
Llama-3.2-1B whitening: cycle 140 (17.43x lift finding)
Prior MP derivation: Drill 5 notes (notes/research_*drill_5* or equivalent)

---

## CONTRACT

- Exp_dev designs ALL anchor parameters, sweep grids, threshold formulas, queue placement, and ETA
- Exp_dev verifies formula self-tests before coding (per [[feedback-strategy-spec-formula-selftests]])
- Exp_dev checks queue.json for name collisions before shipping (per [[feedback-ship-name-collision]])
- ASCII-only in print()/verdict_msg (per [[feedback-ascii-only-in-scripts]])
- Progress logging for any run > 5 min wall (per [[feedback-testbed-progress-logging-and-restart]])
- Geometry audit (Anchor 1) runs on LAPTOP CPU, not GPU runner -- numpy-only script

## AUTONOMY DECLARATION

Exp_dev has full autonomy to:
- Design specific anchor names and code
- Choose whether to batch anchors 1+2 or sequence
- Set exact HP/MID/HF threshold values per envelope-fail-bands
- Determine queue placement (overnight vs remote_cpu vs laptop)
- Decide if additional geometry metrics beyond PR and rho_eff are worth measuring
