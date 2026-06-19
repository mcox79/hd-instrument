# Prereg: multi_hop_higher_m_stress_v1_n4096

Date: 2026-05-30
Anchor: `multi_hop_higher_m_stress_v1_n4096`
Script: `experiments/exp_multi_hop_higher_m_stress_v1_n4096.py`
Queue: `overnight_queue` (GPU; matmul-heavy at N=4096 with 3 path mechanisms)
PROT-018 N-suffix: `_n4096`. Script production `N = 4096`.
PROT-019 timeout floor: 14400s (_n>=4096).
PROT-021 checkpoint: `_seed_checkpoint` per (path, M, depth, seed).
Composition class: PIPELINE (3 path mechanisms wrapped into a shared harness).

## Context

N-batch (commit `e457f1e`, dashboard verdict at `947b22e`) returned all three
multi-hop paths HARD_PASS at M=256 with unanimous 1.000 accuracy across
depths 2-5:

- Path B (continuous-output multi-hop, `exp_continuous_output_multi_hop_v1_n4096`)
- Path D (Bayesian path-probability propagation, `exp_path_probability_propagation_v1_n4096`)
- Path E (spectral path identification, `exp_spectral_path_identification_v1_n4096`)

Caveat: M=256 substrate is well below substrate capacity (~16K-20K at N=4096).
This may be a sub-capacity trivialization rather than a robust multi-hop
mechanism. The 1.000 accuracy across depths 2-5 leaves no margin to
discriminate which (if any) path is the load-bearing mechanism.

## Question

Does the triple-path multi-hop rescue (Paths B, D, E) sustain accuracy at
production-relevant M (M >= N/2), or was M=256 a sub-capacity trivialization?

Differential survival across paths IS the informative signal:

- ALL THREE paths survive to high M -> triple validation; multi-hop is durable
  at production scale via any of the three mechanisms.
- ONE path survives -> identifies the substrate's robust multi-hop mechanism;
  the other two were artifacts of the easy regime.
- NONE survive -> trivialization confirmed; the multi-hop claim is restricted
  to M << N regimes.

## Design

- N = 4096 (BSC codebook; PROT-018 binding).
- Paths = [B, D, E], each ported into a shared harness (re-implemented kernels
  in this script; original 3 single-path scripts also exist for verification).
- M grid = [2048, 4096, 8192] (sub-capacity / at-capacity / past-saturation).
- Depths = [3, 4, 5] (the depths where N-batch saw 1.000 unanimous).
- Seeds = [7, 17, 23, 31, 41] (5 seeds per cell).
- Cells: 3 paths x 3 M-points x 3 depths x 5 seeds = 135 cell-seeds.
- Per-cell-seed checkpointing via `_seed_checkpoint` (PROT-021).

Per-path mechanics (unchanged from N-batch scripts):

- Path B: q_{d+1} = q_d @ W.T; readout = argmax((codebook @ q_d) / N).
- Path D: log-posterior(p) = sum_i log_sigmoid(beta * <cb[p[i+1]], W cb[p[i]]> / N);
  top-1 = argmax over K=100 candidate paths (1 positive + 99 incoherent decoys).
- Path E: coherence_score = mean cos(top-K signature_i, top-K signature_{i+1});
  AUC against incoherent paths; reported as acc_E = clip(2*(AUC - 0.5), 0, 1)
  to put on uniform [0, 1] scale alongside B/D.

## Pre-registered bands (per user dispatch)

HARD_PASS:
  At least one path achieves ALL of:
  - M=2048 depth-5 accuracy >= 0.80 in >=3/5 seeds AND
  - M=4096 depth-5 accuracy >= 0.70 in >=3/5 seeds AND
  - M=8192 depth-5 accuracy >= 0.60 in >=3/5 seeds

HARD_FAIL:
  No path achieves >= 0.50 accuracy at ANY (M >= 2048, depth) cell.
  -> trivialization confirmed; sub-capacity-only claim stands.

MIDDLE_BAND:
  Otherwise. Examples:
  - Specific cells pass for one path but not the full HP gate (partial path-M survival)
  - All paths pass at M=2048 but fail at M=4096 (capacity-bounded substrate)
  - Some paths survive at intermediate depths only

## Verdict reporting

`verdict_msg` reports per-path-per-M-per-depth accuracy in a uniform format:

```
path_M_depth_acc: B_2048_3=0.X B_2048_4=0.X B_2048_5=0.X B_4096_3=0.X ...
                  D_2048_3=0.X ... E_2048_3=0.X ...
```

plus `paths_passing=[...]` listing which paths cleared the per-M HP gates at
depth 5.

This supports verdict_handler's "honest re-read" pattern -- whether per-cell
metrics contradict the headline verdict can be directly inspected.

## Formula self-tests (in script)

- N == 4096 (PROT-018).
- M_grid == [2048, 4096, 8192].
- depths == [3, 4, 5].
- HP_DEPTH == 5.
- Synthetic HP test: one path with accuracy = HP_THRESH[M] + 0.05 at depth 5
  in all 5 seeds across all 3 M, other paths at 0.20 everywhere -> HARD_PASS.
- Synthetic HF test: all 135 cells at acc=0.20 -> HARD_FAIL.
- Synthetic MB test: all 135 cells at acc=0.55 -> MIDDLE_BAND.
- AUC sanity: roc_auc([1,1,0,0], [0.9,0.8,0.4,0.2]) == 1.0.

## OOM check

M=8192, N=4096:
  - keys+vals = 8192 * 4096 * 4 bytes * 2 = 256 MiB.
  - W = 4096 * 4096 * 4 bytes = 64 MiB.
  - codebook (C=N=4096) = 4096 * 4096 * 4 bytes = 64 MiB.
  - Path D inner loop allocates K * depth pair indices = 500 * 5 = 2500 longs
    plus per-pair embeddings ~ 500 * 5 * 4096 * 4 bytes = 40 MiB transient.
  - Path E top-K signatures = depth * K = 5 * 16 floats per candidate.

Peak GPU memory at FULL ~ 1 GiB. Well under 6 GiB budget on 8 GiB GPU.

## Multi-scale smoke

Smoke at N=1024, M=128, depth=3, seed=17, 1 cell per path -> ran in 0.26s.
All 3 paths emitted valid accuracies (B=1.000, D=1.000, E=0.992).
HARD_FAIL verdict at smoke is EXPECTED ARTIFACT (no smoke cell has M >= 2048;
the HF gate's "no path achieves HF at M >= 2048" is therefore vacuously
true at smoke). Self-test gates HP/HF/MB all pass at the synthetic-input
level (in `_instrumentation_selftest`).

## Walk-back / borderline check

Smoke effect size at M=128 is saturating (1.0, 1.0, 0.992 are at-ceiling),
which is by design at sub-capacity. The borderline-effect-size walk-back
rule does NOT apply here because smoke is intentionally at the easy regime;
the FULL run is the discriminating test.

## Timeout estimate

Composite cells = 135. Per-cell wall on GPU at production:
- Path B: ~5-15s (1 substrate build + matmul chain).
- Path D: ~30-90s (1 substrate build + K=100 candidate-set scoring per query,
  ~50 queries per cell).
- Path E: ~10-30s (1 substrate build + 80 pos + 80 neg AUC).

Mean ~30-45s per cell x 135 cells ~ 4050-6075s. Add 2x safety margin and
seed-checkpoint overhead -> 12000s. Use 14400s (PROT-019 floor for _n4096).

`timeout_s = 14400`. Within 14400s hard limit (no upstream-push required).

## Dependencies verified

- `experiments/_metric_battery.py` (make_substrate) -- present
- `experiments/_relation_graph.py` (build_relation_facts, sample_coherent_starts,
  sample_incoherent_paths) -- present
- `experiments/_seed_checkpoint.py` -- present
- 3 N-batch source scripts present at:
  - `experiments/exp_continuous_output_multi_hop_v1_n4096.py`
  - `experiments/exp_path_probability_propagation_v1_n4096.py`
  - `experiments/exp_spectral_path_identification_v1_n4096.py`

This anchor's harness REIMPLEMENTS the small per-hop kernels rather than
importing the source scripts directly (the source scripts run their own
`_instrumentation_selftest()` at module scope, which would force CPU
smoke-tests during this script's import even at production scale). The
reimplemented kernels are byte-equivalent in math but live alongside the
script-local config.

## Risk / interpretation

Best case (one specific path passes HP): the substrate has ONE robust
multi-hop mechanism. Update cap_map row to identify it.

Mid case (MIDDLE_BAND with specific M cells passing): the substrate has
M-bounded multi-hop. Update cap_map with the M ceiling.

Worst case (HARD_FAIL): the M=256 N-batch results were trivialization. The
"triple-path multi-hop rescue" claim is restricted to sub-capacity regimes.
This is a substantive de-promotion, not a refutation -- multi-hop may still
hold up to some M_max < 2048 that a follow-on can locate.

## N-suffix

`_n4096` (PROT-018). Script's production `N = 4096`. Verified via grep.
