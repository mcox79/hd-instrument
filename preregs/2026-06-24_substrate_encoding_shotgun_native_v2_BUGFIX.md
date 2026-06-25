# Pre-reg: substrate_encoding_shotgun_native_v2_BUGFIX

**Authored:** 2026-06-24 by exp_dev (BUGFIX re-author per Stage 2 DISPATCH 5)
**Anchor:** `substrate_encoding_shotgun_native_v2_BUGFIX`
**Routing:** local_cpu_queue (pure numpy + rank-1 W; ~30-45 min estimated)
**Lane:** Lane 1 (substrate-native capability)
**Corpus provenance:** SYNTHETIC ONLY (no word2vec, no text8, no Pythia, no statistical-LM baseline)
**Cell file:** `experiments/exp_substrate_encoding_shotgun_native_v2_BUGFIX.py`
**Supersedes:** `substrate_encoding_shotgun_native_v1` (HARD_FAILed at NO_ENCODER_PASSES_T1; substrate-side primitive misuse)

## v1 bug diagnosis (load-bearing context)

v1 used **FFT-HRR superposition + cosine-cleanup** for T1 storage-retrieval:
```
bundle = sum_i hrr_bind(K_i, V_i)         # circular convolution; single N-dim vector
pred_i = hrr_unbind(bundle, K_i)          # circular correlation
top1_i = argmax_v cosine(pred_i, V_v)
```
HRR superposition + cosine-cleanup has **capacity ~N/8** with degraded recall above
that. At M=500, N=8192 the theoretical top-1 ceiling is ~0.83 (matches v1's
measured 0.823-0.840 across all 6 encoders). All 6 encoders giving near-
identical top1 ~0.83 is the smoking gun: not an encoder discriminator, but a
primitive capacity ceiling. v1's "HARD_FAIL substrate-side bug suspected"
framing was correct directionally -- the substrate WAS the wrong primitive
for the M=500 capacity claim.

## v2 fix

Replace storage primitive with **rank-1 Hebbian outer-product W**, per:
- `experiments/exp_substrate_k_module_heterogeneous_compose_LM_v1.py:371` `build_rank1_W_gpu`
- `experiments/exp_substrate_arm2_capacity_respecting_pair_storage_v1.py` (canonical sparse-bipolar pair-storage)
- Master sparse-bipolar checklist: amplitude scaling 1/sqrt(f) (matched-filter SNR; CERT 583)

```
W = sum_i outer(V_i, K_i) = V.T @ K       # (N, N) heteroassociative Hopfield/Kanerva
pred_q = K_q @ W.T                         # = (K_q @ K.T) @ V
top1_q = argmax_v cosine(pred_q, V_v)
```

Verified by formula-selftest: at M=20/N=1024 the rank-1 W gives top1=1.000 for
all 6 encoders by-construction (M << N capacity). At M=500/N=8192 it gives
top1=1.000 for all encoders (still below capacity), confirming primitive is
the substrate-side issue. Pre-flight sweep verified W stays at top1=1.000
through M=20000 / N=8192 (~2.5x N) for sparse+dense+kwta+hadamard arms.

## Task redesign (discriminator shifts with primitive fix)

With rank-1 W, T1 in-dist exact recall is by-construction-saturated to ~1.000
for ALL encoders. The discriminator falls on:

- **T1 STORAGE-RETRIEVAL (sanity gate)**: M=500; expect ~1.000 for all (any FAIL = primitive broken)
- **T2 COMPOSITION (HRR bind separation)**: M=300; encoder discriminates via bind+unbind preservation
- **T3 CAPACITY-AT-NOISE (sigma=2.0)**: M-sweep; encoder discriminates via noise-robustness (pre-flight: E5 raw 1/sqrt(N) Gaussian collapses; E4 kWTA marginal; sparse-amp-scaled + dense-bipolar + Hadamard robust)
- **T4 CROSSTALK (mean off-target cos at M=1600)**: finer-grained encoder discriminator

## Scope (apples-to-apples Lane 1)
- 6 encoders x 4 substrate-native tasks x 3 seeds = 72 measurement cells.
- All encoders generate hypervectors of the SAME N_DIM (8192).
- All encoders index the SAME M concept indices (synthetic int ids).
- All tasks use SAME storage primitive (rank-1 W for T1/T3/T4; HRR for T2 only).
- Encoders differ in ONE dimension each (the encoding distribution).
- Sparse arms (E1/E2) use 1/sqrt(f) amplitude scaling (matched-filter SNR).

## Encoders (E1..E6) -- unchanged from v1
- **E1 sparse-bipolar f=0.02** (amplitude-scaled): ternary +/-7.07 or 0
- **E2 sparse-bipolar f=0.05** (amplitude-scaled): ternary +/-4.47 or 0
- **E3 dense bipolar**: +/-1 over all N coords
- **E4 k-WTA-VQ**: random Gaussian -> keep top-k=0.05*N abs, sign-quantize
- **E5 dense Gaussian**: continuous N(0, 1/N) projection (no amplitude scaling -- raw)
- **E6 Hadamard**: random sign-permuted Hadamard rows

## Tasks (T1..T4)
- **T1 STORAGE-RETRIEVAL** (sanity gate): build W=V.T@K from M=500 pairs; query with exact K_i; top-1 over V codebook. **Metric:** top-1 recall@1.
- **T2 COMPOSITION**: bundle bind(S,O) over M=300 pairs (HRR); unbind by S_q to recover O_q; compare cosine(unbound, O_q) to cosine(unbound, O_k) where k != q for non-stored pairs. **Metric:** (in_mean - out_mean) / (in_std + out_std).
- **T3 CAPACITY-AT-NOISE**: sweep M in {500, 1000, 2000, 4000, 8000, 16000}; build W; query with K + Gaussian noise (sigma=2.0); find capacity M* = largest M with noise-top1 >= 0.95. **Metric:** M* (integer).
- **T4 CROSSTALK**: at saturation M=1600, query with K_i, measure mean |cos(pred, V_j)| for j != i. **Metric:** mean off-target cosine (lower=better).

## HARD bands (pre-registered, sacrosanct both directions)

**Per-encoder, per-task:**
- **T1 PASS:** top1_recall >= 0.95 (sanity gate; expected ~1.000)
- **T2 PASS:** normalized_separation >= 0.30
- **T3 PASS:** capacity_M_star >= 1000
- **T4 PASS:** off_target_cosine <= 0.05

**Cell-level (across the 6x4 matrix):**
- **HARD_FAIL:** no encoder PASSes T1 (rank-1 W primitive broken; substrate-side bug; re-author needed)
- **HARD_PASS:** at least one encoder achieves PASS on ALL 4 tasks
- **MIDDLE_BAND:** each task has a clear winner, no single encoder dominates (encoder choice is task-dependent)

## By-construction-saturation note (per Skunkworks discipline)

T1 PASS at top1=1.000 across all encoders is **expected by construction** for
rank-1 W at M << encoder-effective-rank. This is NOT chain-grade evidence
that all encoders are equally good -- it's a sanity gate that confirms the
primitive isn't broken. The discriminating tier-deciders are T2 (HRR bind
preserves O signal) + T3 (noise capacity) + T4 (crosstalk magnitude).

Skunkworks A5 owns the chain-grade tiering call; this pre-reg defaults to
**MIDDLE_BAND classification** for any verdict that comes back with T1=1.000
PASS for all encoders but no encoder dominating T2/T3/T4. Only an encoder
that PASSes all 4 with discriminating margin on T2/T3/T4 earns the
HARD_PASS framing -- and even then, Skunkworks owns the cert-grade tier.

## DISCRIMINATOR

Encoder rankings should differ across tasks (Spearman rho across task-rank
columns < 0.7 expected if encoder choice IS task-dependent; >= 0.7 supports
"one optimal encoder"). Descriptive, not a gate.

Pre-flight sigma=2.0 noise sweep observation: E5 raw 1/sqrt(N) Gaussian
collapses to top1 ~0.01 (signal-dominated by noise; raw amplitude too small).
E4 kWTA-VQ marginal at sigma=4.0 (drops to 0.520 at M=6400). E1/E2 amplitude-
scaled sparse + E3 dense-bipolar + E6 Hadamard all robust at sigma=2.0
through M=6400. **This pre-flight informs the bands**: T3 PASS=1000 is
discriminating because E5 will FAIL it definitively; if NO encoder PASSes T3,
the noise sigma is too high (re-author).

## CONFOUND audit
- f parameter held identical for E1 vs E2 except f (clean delta).
- All encoders see the same random key/value pair indices per seed.
- Codebook seed = primary seed; encoder draws inside that.
- Sparse-bipolar arms amplitude-scaled per master checklist (NOT confounded with HRR-cosine-cleanup as v1 was).
- All encoders see SAME noise sigma in T3 (no per-encoder noise tuning).
- chance = 1/M for T1/T3 (reported in verdict_msg).

## Smoke gate
Smoke variant: M_smoke=100, seeds=[7], encoders=ALL 6, tasks=T1+T2 only (per v1 convention).
Smoke must:
- Produce valid per_seed metrics with all 6 encoders measured on T1+T2.
- **Show ALL 6 encoders achieve T1 top1 >= 0.99 at M=100** (rank-1 W sanity gate; substrate-mining floor at M << capacity).
- Run end-to-end in <= 180s on CPU.

If smoke shows any encoder with T1 < 0.99 at M=100, BUGFIX itself has a bug;
do NOT dispatch full.

## REQUIRED_FIELDS in metrics.json
`verdict`, `verdict_msg`, `elapsed_s`, `summary`, `run_mode`, `n_seeds`,
`config_version`, `per_seed` (list of dicts with seed + matrix), `aggregate`
(with matrix mean per (encoder, task)), `storage_primitive`,
`amplitude_scaling`, `v1_bug_diagnosis`.

## Self-test (formula-selftest discipline per Fix #28)
Mechanism check at TINY config; pre-computes expected values BEFORE assertion:
- Phase 1: shape + sparsity per encoder (E1/E2 ~f density, E3/E5/E6 dense, E4 ~0.05).
- Phase 2: rank-1 W at M=20/N=1024 -> expected top1=1.000 for all 6 encoders (asserted).
- Phase 3: rank-1 W at M=100/N=8192 for E2 -> expected top1=1.000 (would have caught v1 bug).
- Phase 4: HRR bind+unbind round-trip at M=5 -> argmax should be index 0 (asserted).

## Risk
Primary risk: chosen noise sigma=2.0 + T3 PASS threshold 1000 may be too
aggressive for some encoders given N=8192 + amplitude differences. Pre-flight
sweep informs the bands honestly (E5 will fail T3 at this sigma; if MIDDLE_BAND
is verdict the encoder picture is task-dependent -- which IS the substrate-
product answer per USER "use what the substrate prefers per task").

Secondary risk: T2 HRR composition is the only encoder discriminator on a
binding op. If T2 also saturates (all encoders ~equal separation), then T4
crosstalk becomes the sole magnitude discriminator. Acceptable; still
informative for the encoding-shotgun question.

No PASS-by-construction risk for the cell-level verdict: HARD_PASS requires
encoder PASS on ALL 4 tasks; T2/T3 are not by-construction-saturated.

## Verdict text policy
verdict_msg will:
- List PASS/FAIL per (encoder, task) cell (24 entries).
- Identify best encoder per task (4 entries).
- Identify any encoder in top-2 across ALL 4 tasks.
- Report cell-level verdict.
- NOT claim "winning encoder" if no encoder PASSes all 4 -- MIDDLE_BAND.
- Explicitly note T1 sanity-gate semantics (top1=1.000 is BY CONSTRUCTION at M=500/N=8192 with rank-1 W; NOT a chain-grade claim).

## Dispatch
- queue: local_cpu_queue
- timeout: 3600s (60 min; per Fix #14 floor for N>=4096 cells per PROT-019)
- ASCII-only.
- single primary metric per task.
- per-seed checkpoint via experiments/_seed_checkpoint.

## Cites
- v1 metrics: `data/exp_substrate_encoding_shotgun_native_v1/metrics.json` (HARD_FAIL; 0.83 across all encoders confirms primitive-not-encoder issue)
- arm2 reference: `experiments/exp_substrate_arm2_capacity_respecting_pair_storage_v1.py` (canonical sparse-bipolar pair-storage; in_dist=1.000 by construction at M=20/N=8192)
- K-module reference: `experiments/exp_substrate_k_module_heterogeneous_compose_LM_v1.py:371` `build_rank1_W_gpu` (rank-1 outer-product Hebbian write)
- CERT 583 sparse-bipolar amplitude scaling (matched-filter receiver SNR; -17dB penalty without 1/sqrt(f))
- Master discipline: feedback_substrate_mine_capacity_before_extrapolating_2026-06-22; by-construction-saturation tiering (Skunkworks 2026-06-22)
- Stage 2 DISPATCH 5 brief (this BUGFIX re-author task)
