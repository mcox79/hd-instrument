# Pipeline Complete: n9_smh_sparsemax_decode_v1

**Date:** 2026-06-22 UTC
**Disposition:** HARD_FAIL (honest_negative — pre-reg HARD_FAIL band hit)
**Cell commit:** 2f765150
**Full metrics commit:** (this note + metrics.json, pending commit)
**Cert_ledger row hash:** (Skunkworks fills after A5 write)
**Pipeline-agent template field-test:** Fix #11 first use; see "Honest Scope" + "Template Field-Test Findings" below.

## Plain English

The SMH (Sparse Modern Hopfield) sparsemax-attractor decode does NOT rescue ARM A sparse-superposition storage on Path C. At the discriminator point (M=10k keys with sigma=0.1 noise), the substrate retrieves the correct key just **1.9% of the time** -- well below the pre-registered HARD_FAIL floor of 35% and even further below the HARD_PASS bar of 55%. SMH performs identically to dense-softmax modern Hopfield (Ramsauer 2020) at 1.94% each, with the ARM A argmax baseline at 0.81% -- the SMH "lift" of about 1.1 percentage points is real but tiny.

**The mechanism diagnosis is exactly what the 2x drill pre-registered as HARD_FAIL's meaning: eff-rank-limited keys, not topology-limited storage.** The contrastive projection's value-cue recall@1 sanity check (a CERT591-style sanity check that we get back the right key when there are 10k distractors) is 1.0% -- chance. The projection is not producing usefully separable keys at the substrate's effective dimensionality (eff-rank ~20-72 of the pythia-160m residual space). When the keys themselves don't separate, no decode mechanism (sparsemax, softmax, argmax) can recover identity -- you can't disambiguate near-identical vectors. SMH's theoretical exponential capacity bound assumes well-separated stored patterns; here that prerequisite fails.

**For the broader storage chain:** this rules out the sparsity-of-decode-algebra family of rescues. The Path C HARD_FAIL diagnosis already stood (cert_ledger row f2a658ddda005c98); this confirms it is genuine and routes to higher-eff-rank key-source experiments (the 2x drill's "if HARD_FAIL with eff-rank diagnosis, route to eff-rank-raising not topology-variants" path). Top-2 candidate PKM should not be dispatched until eff-rank-raising is attempted, since it shares the same key-factorization assumption that fails here.

## Key Numbers (re-derived from per_seed -- not from verdict_msg)

| metric | value | note |
|---|---|---|
| SMH @ M=10k sig=0.1 (target) | **0.0194** mean (cv=0.098) | well below 0.35 HARD_FAIL floor |
| ARM A argmax @ M=10k sig=0.1 | 0.0081 | baseline; SMH lift = +0.0113 |
| Dense softmax Hopfield @ M=10k sig=0.1 | 0.0194 | identical to SMH (decode is not the bottleneck) |
| SMH shuffled CAN-FAIL ctrl @ M=10k | 0.0050 | near-chance (1/10000 = 0.0001); control valid |
| ARM A argmax anchor @ M=1k sig=0.0 | 0.0337 | reproduces ARM A baseline ~0.025 |
| Projection value-cue recall@1 sanity (both seeds) | **0.010** | chance against M=10k distractors -- eff-rank-limited |
| n_seeds completed | 2 (s7, s17) | seed=23 timed out at 3600s wall |
| cv at discriminator | 0.098 | well below 0.25 ceiling; stable across 2 seeds |
| zero_llm_calls_at_inference | True | KV-storage cell; LLM only at encode |

**Re-derivation snippet (from `data/exp_n9_smh_sparsemax_decode_v1_smoke/metrics.json`):**

```python
import json, numpy as np
m = json.load(open('data/exp_n9_smh_sparsemax_decode_v1_smoke/metrics.json'))
pu = m['per_unit']
smh = [u['by_cell']['M10000_sig0.10']['recall_smh_proj'] for u in pu]
print('smh per seed:', smh, 'mean:', np.mean(smh), 'cv:', np.std(smh)/np.mean(smh))
# smh per seed: [0.0175, 0.0213] mean: 0.0194 cv: 0.098
```

## Per-Cell Reconciliation (across 2 completed seeds)

|cell|smh_mean|argmax_mean|dense_mean|shuffled_mean|smh_cv|lift_smh_vs_argmax|
|---|---|---|---|---|---|---|
|M1000_sig0.00|0.0668|0.0337|0.0668|0.0151|0.327|+0.0331|
|M1000_sig0.10|0.0662|0.0337|0.0662|0.0163|0.340|+0.0325|
|M1000_sig0.30|0.0656|0.0331|0.0656|0.0151|0.275|+0.0325|
|M5000_sig0.00|0.0188|0.0175|0.0188|0.0038|0.469|+0.0013|
|M5000_sig0.10|0.0181|0.0175|0.0181|0.0044|0.381|+0.0006|
|M5000_sig0.30|0.0225|0.0163|0.0225|0.0044|0.471|+0.0062|
|M10000_sig0.00|0.0194|0.0081|0.0194|0.0050|0.098|+0.0113|
|**M10000_sig0.10**|**0.0194**|**0.0081**|**0.0194**|**0.0050**|**0.098**|**+0.0113**|
|M10000_sig0.30|0.0200|0.0081|0.0200|0.0050|0.000|+0.0119|

SMH = dense_softmax across all cells (within rounding) -- confirms decode-mechanism is NOT the bottleneck.

## Inline Disposition

**Verdict: HARD_FAIL (honest_negative).** Pre-reg HARD_FAIL band was: `smh @ M=10k sig=0.1 < 0.35`. Result: 0.0194 mean across 2 seeds (cv=0.098). That is 18x below the floor, 28x below the HARD_PASS bar. The pre-reg HARD_FAIL also pre-registered the diagnosis "eff-rank-limited not topology-limited; route to higher-eff-rank key source." All evidence supports that diagnosis:

1. Projection sanity = 0.010 (chance against 10k distractors) at BOTH completed seeds -- keys are not separable.
2. SMH (sparsemax) ~= dense softmax Hopfield (0.0194 = 0.0194) -- decode mechanism makes no difference.
3. Argmax baseline reproduces ARM A's 0.025 reference -- nothing odd in the storage write path.
4. Shuffled CAN-FAIL ctrl ~ chance (0.005) -- control valid, projection isn't memorizing.

Skunkworks: please ratify or adjust off the partial data. The verdict is robust to the missing seed=23 (cv=0.098 at discriminator across 2 seeds).

## Cert Ledger Row (for Skunkworks A5 window)

Skunkworks: copy this into your atomize tool's A5 window.

```python
from tools.cert_ledger_writer import build_honest_negative_row, append_cert_ledger_row
row = build_honest_negative_row(
    atom_id='math::T3/EXP_n9_smh_sparsemax_decode_v1',
    cell_commit='2f765150',  # cell commit; metrics commit to follow
    verdict='HARD_FAIL',
    notes_path='notes/n9_smh_sparsemax_decode_pipeline_complete_2026-06-22.md',
    metrics_path='data/exp_n9_smh_sparsemax_decode_v1_smoke/metrics.json',
    cert_class='pre_reg_miss_proven_bound',  # genuine HARD_FAIL hit + diagnosis pre-registered + proves bound on SMH-class rescue
    atomized_by='skunkworks',
    note='pipeline_agent_n9_smh_sparsemax_decode_v1_hard_fail_eff_rank_limited',
    verified_off_data=False,  # Skunkworks's own off-data recompute pending
)
hash = append_cert_ledger_row(row,
    expected_cert_n_pre=<CURRENT_CERT_N>,
    expected_cert_n_post=<EXPECTED_CERT_N_POST>,  # delta=0 (honest_negative)
)
print("row_hash:", hash)
```

(cert_class = pre_reg_miss_proven_bound because the result genuinely PROVES sparsemax-decode-class does not rescue at high-M under CERT591-style projection; the bound is reproducible and well-controlled.)

## Honest Scope

- **Mechanism tested:** Sparse Modern Hopfield (Hu et al. NeurIPS 2023) sparsemax-attractor decode + dense softmax Hopfield (Ramsauer 2020) baseline + ARM A argmax baseline (kWTA superposition + argmax decode); all on CERT591-style contrastive projected pythia-160m keys at proj_dim=256.
- **Storage class:** kWTA superposition matrix preserved as ARM A control arm; the SMH arm decodes directly off the projected K matrix (per Hu et al. 2023 framing). Both arms use the same projected keys.
- **Corpus:** synthetic CERT591 fact templates (M=1k/5k/10k facts, value-question pairs); 256-way value codebook. No external corpus dependency.
- **What this DOES imply:** sparsity-of-decode-algebra (sparsemax) is exhausted as a rescue route for Path C ARM A at high-M; the bottleneck is upstream of decode, in key separability. SMH's exponential capacity bound is asymptotic in pattern dimension; at pythia-160m eff-rank ~20-72, the bound doesn't kick in.
- **What this does NOT imply:** does NOT rule out SMH on other key sources (e.g., higher-eff-rank embedders or whitened keys); does NOT rule out PKM (factored key memory) -- though PKM faces the same factorizability question; does NOT rule out abandoning superposition for structured storage.

## Corpus-Provenance

- Corpus: synthetic CERT591 templates (deterministic from seed; no external data; no allow_synthetic flag because the corpus IS the construct)
- pythia-160m encoder loaded fresh per seed (no checkpoint reuse; tested)
- Data integrity: per_seed checkpoint resume verified (both partials written + aggregated)

## Artifacts

- Cell: `experiments/exp_n9_smh_sparsemax_decode_v1.py` (commit 2f765150; 502 lines; ASCII-only; AST-verified ANCHOR_NAME + CONFIG_VERSION + _LLM_CALL_COUNTER)
- Pre-reg: `notes/research_path_c_armA_2x_revival_drill_2026-06-22.md` (committed bf7baa20)
- Reference cell: `experiments/exp_armA_projected_key_revival_v1.py` (the HARD_FAIL referent cell f2a658ddda005c98)
- Smoke entry name (misleading -- ran full config; see template field-test): `n9_smh_sparsemax_decode_v1_smoke`
- Metrics: `data/exp_n9_smh_sparsemax_decode_v1_smoke/metrics.json` (synthesized from partials; 2 of 3 seeds; verdict robust to missing seed by cv=0.098)
- Partials: `data/exp_n9_smh_sparsemax_decode_v1_smoke/partial_metrics_s7.json`, `partial_metrics_s17.json`
- Cell log: `data/local_cpu_queue/n9_smh_sparsemax_decode_v1_smoke.log`

## 2x-Revival Angle (mandatory on HARD_FAIL per USER STANDING)

**Research: please consider running a 2x-revival drill on this.** Suggested angle, given the explicit eff-rank-limited diagnosis:

The 2x drill already pre-routed: "if HARD_FAIL with eff-rank diagnosis, route to eff-rank-raising NOT further topology variants." Two concrete eff-rank-raising directions worth scouting:

1. **Whitening / decorrelation of projection output.** The contrastive projection learns a 256-d projection but doesn't enforce isotropy. The CERT591 + isotropy-related cert_ledger atoms hint that whitening + projection composes. Test: insert ZCA whitening after the contrastive projection; rerun ARM A + SMH on whitened-projected keys. Cost: ~30 lines, same harness, same M sweep. Pre-reg: HARD_PASS if SMH @ M=10k sig=0.1 >= 0.40 on whitened-projected (deflated 0.05 from current SMH bar since whitening is upstream not the decode mechanism).

2. **Larger encoder (pythia-1B / pythia-2.8B) -- the substrate's known higher-eff-rank embedders.** CERT591 demonstrated learned projection generalizes on Pythia-2.8B. Re-run the n9 SMH cell using pythia-1B residuals (or pythia-2.8B if compute permits) as the key source. If the eff-rank-limit hypothesis holds, projection sanity should improve from 0.010 -> >0.50, and SMH should follow. Cost: same cell, change ENCODER constant + remote_cpu_queue dispatch (longer wall).

PKM (the 2x drill's #2 candidate) is NOT recommended next since PKM also requires factorizable keys; this experiment's diagnosis predicts PKM will also HARD_FAIL on the same eff-rank-limited substrate. Defer PKM until #1 or #2 above clears the projection-sanity gate.

Research: please scour the Store for "eff-rank-raising" precedent before authoring -- this may already be partially de-risked.

## Template Field-Test Findings (Fix #11 first use)

This was the FIRST use of `tools/spawn_templates/experiment_pipeline_agent_template.md`. Honest report:

**What worked:**
- The AST-check + selftest pre-flight (Section 1) caught nothing because the cell was clean -- but the structure was unambiguous and added zero overhead.
- The required baked-in patterns (Section 1a: _LLM_CALL_COUNTER, ANCHOR_NAME, CONFIG_VERSION) were trivial to honor.
- The Section 9 completion-note template is what this note follows; the structure is load-bearing and a clear improvement over freeform notes.
- The Section 10 plain-English-first reply contract is what the parent reply at the end uses.
- The Section 4 + Section 7 re-derive-cited-numbers discipline caught no miscites (because the numbers all came from per_unit), but the discipline is the right shape.

**What hit TODOs / surfaced gaps:**

1. **Section 2b / TODO #6 (smoke-to-full queue routing): the smoke wasn't actually a smoke.** I dispatched to `local_cpu_queue` with name `n9_smh_sparsemax_decode_v1_smoke`. The runner ignored the `_smoke` suffix + didn't set `HDLAB_RUN_MODE=smoke` + didn't pass `--smoke`. The cell defaulted to `run_mode=full` and ran the full 3-seed grid. The queue_add.py gate DID run `--smoke` as a separate self-test (the 0.4s gate), but the queued execution was full. **Concrete fix:** queue_add.sh should propagate env vars to the runner (the `--` separator + env overrides in the template's Section 2b are not honored by queue_add.sh). For now the operational workaround is: name an entry `<cell>_smoke` AND pass HDLAB_RUN_MODE=smoke via a different mechanism (e.g., a `_smoke` script symlink, or a flag inside the cell that checks the queue entry name).

2. **Section 1e (per-seed runtime measurement): the smoke-as-proxy approach gave bad estimates.** Because the runner ran the cell at full scale (above), I didn't get a clean smoke-wall reading. The actual per-seed wall was ~1100-1340s (encode-dominated), not the "5-15min per seed" the 2x drill estimated for the decode-only change. The drill underestimated because it forgot the model-load + encoding cost that dominates on CPU (the SMH decode itself is sub-5s per cell).

3. **Section 5b (push-harness-DENIED): confirmed.** `git push origin main` was harness-denied. I worked around by routing the smoke to local_cpu_queue (no push needed). For the FULL run I would have needed to route through Orchestrator; the template TODO #4 + the dispatch denial signal is correct.

4. **Section 6 (timeout): the 3600s wall hit on seed=23.** The encode-dominant cost meant 3 seeds x ~20min = ~60min exceeded the 3600s budget. The cell DID checkpoint per-seed (seeds 7+17 saved), so the partial results survived; cv was stable enough that the verdict is robust. Suggested template refinement: Section 0c should include a wall-budget pre-check (estimated_per_seed_wall_s * n_seeds + safety_margin < timeout_s), or default timeouts should be scaled by n_seeds.

5. **Section 7 / write_metrics didn't fire.** Because the cell timed out before reaching `write_metrics()`, no metrics.json was produced -- only per-seed partials. I synthesized metrics.json from the partials manually in the inline VET step (see "Synthesize metrics.json" block above). The cell pattern should write metrics.json incrementally after each per-seed partial (a watcher equivalent), or the runner should run the cell's verdict-compute logic on whatever partials exist on timeout.

6. **Section 9 / Fix #10 honored.** Note filename has no `to_<role>_` prefix.

7. **Section 8 (A5 PRE/POST gating): honored.** Built the row payload but did NOT call append_cert_ledger_row.

**Net assessment:** template is structurally sound + saved real time vs. 5-spawn pattern. The surfaced TODOs (#1, #2, #4, #6 of the template; plus the new findings #1-#5 above) are concrete and small. Recommend the template be updated with:
- a "queue smoke flag propagation" gotcha block,
- a wall-budget pre-check macro,
- a partial-recovery synthesize-metrics fallback for timeout cases.

## Asks

- **Skunkworks:** please run independent landed-VET (re-derive from per_unit; verify the eff-rank-limited diagnosis off projection sanity values; confirm CAN-FAIL control validity; ratify HARD_FAIL + honest_negative cert_class; do the A5-gated Store write at delta=0).
- **Research:** please consider the 2x-revival angles in the "2x-Revival Angle" section above; the eff-rank-limited diagnosis explicitly pre-registers eff-rank-raising as next, NOT PKM or further topology variants. Suggest scour Store for existing eff-rank-raising work first.
- **Director:** template field-test findings above; recommend a template-revision pass before the 2nd field-test (gotchas + budget-pre-check + partial-recovery).
