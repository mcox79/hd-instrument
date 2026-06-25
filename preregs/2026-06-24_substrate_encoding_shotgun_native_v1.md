# Pre-reg: substrate_encoding_shotgun_native_v1

**Authored:** 2026-06-24 by exp_dev
**Anchor:** `substrate_encoding_shotgun_native_v1`
**Routing:** local_cpu_queue (pure numpy + FFT-HRR; ~30-45 min estimated)
**Lane:** Lane 1 (substrate-native capability)
**Corpus provenance:** SYNTHETIC ONLY (no word2vec, no text8, no Pythia, no statistical-LM baseline)
**Cell file:** `experiments/exp_substrate_encoding_shotgun_native_v1.py`

## Why
USER directive: "we choose the optimal encoding - that we start on the right track."
Today's encoder-leakage finding (path_c FAIR_HARNESS) showed the current default
(sparse-bipolar f=0.05 with word2vec init) is biased by the source semantic encoder.
A clean substrate-native comparison on substrate-native tasks (NO external semantic
encoder, NO corpus statistics) is needed to identify the Stage-1 foundational encoder
for all Stage 2/3 work.

## Scope (apples-to-apples Lane 1)
- 6 encoders x 4 substrate-native tasks x 3 seeds = 72 measurement cells.
- All encoders generate hypervectors of the SAME N_DIM (8192).
- All encoders index the SAME M concept indices (synthetic int ids).
- All tasks use SAME HRR substrate machinery (FFT bind/unbind + cosine retrieval).
- Encoders differ in ONE dimension each (the encoding distribution); everything
  else (N_DIM, M, seed, task pipeline) is held constant per task. INTRA_LANE_DELTA = encoder.

## Encoders (E1..E6)
- **E1 sparse-bipolar f=0.02**: ternary +/-/0, density 0.02 (capacity-optimal per substrate-mining drill).
- **E2 sparse-bipolar f=0.05**: ternary +/-/0, density 0.05 (current default; for comparison).
- **E3 dense bipolar**: +/-1 sign (Bernoulli) over all N coordinates.
- **E4 k-WTA-VQ**: random Gaussian -> keep top-k absolute values, sign-quantize, others zero (k = round(0.05*N)).
- **E5 dense Gaussian**: continuous N(0, 1/N) projection (no quantization).
- **E6 Hadamard**: orthogonal-by-construction (random sign-permuted rows of a Hadamard matrix; N=8192 = 2^13 so exact).

All encoders are L2-normalized at the vector level before binding (per the HRR convention).

## Tasks (T1..T4)
- **T1 STORAGE-RETRIEVAL**: store M=500 (key, value) pairs via sum-of-binds; query a key, recover value by unbind + cosine cleanup over the value codebook; **metric:** top-1 recall@1.
- **T2 COMPOSITION**: store M=300 (subj, obj) bound-pairs; for each (subj_q, obj_q) probe, ask "is (subj_q, obj_q) in the set?" by unbind probe with subj_q and check cosine to obj_q's atom; **metric:** unbind-cosine separation (in-set mean - out-set mean), normalized.
- **T3 CAPACITY-AT-SCALE**: sweep M in {100, 200, 400, 800, 1600, 3200, 6400}; T1 protocol per M; find capacity M* = largest M with recall@1 >= 0.95; **metric:** M* (integer).
- **T4 CROSSTALK**: at the saturation M=1600, measure mean cosine of an unbound value to all NON-target codebook atoms; **metric:** mean off-target cosine (lower=better).

## HARD bands (pre-registered)
Per-encoder, per-task:
- **T1 PASS:** top1_recall >= 0.95
- **T2 PASS:** normalized_separation >= 0.30
- **T3 PASS:** capacity_M_star >= 1000
- **T4 PASS:** off_target_cosine <= 0.05

Cell-level (across the 6x4 matrix):
- **HARD_PASS:** at least one encoder achieves PASS on ALL 4 tasks.
- **MIDDLE_BAND:** each task has a clear winner, but no single encoder dominates; suggests task-specific or hybrid encoding required.
- **HARD_FAIL:** no encoder PASSes T1 (storage-retrieval is the foundational task; failure here means substrate-side bug in this cell, not an encoder choice).

## DISCRIMINATOR
Encoder rankings should differ across tasks (Spearman rho across task-rank columns < 0.7 expected if the choice IS task-dependent; >= 0.7 supports "one optimal encoder"). This is descriptive, not a gate.

## CONFOUND audit
- f parameter held identical for E1 vs E2 except f (clean delta).
- All encoders see the same random key/value pair indices per seed.
- Codebook seed = primary seed; encoder draws inside that.
- Vocab/concept-id space size held constant per task.
- No corpus, no statistical model -- chance = 1/M for T1/T3 (reported in verdict_msg).

## Smoke gate
Smoke variant: M_smoke=100, seeds=[7], encoders=ALL 6, tasks=T1+T2 only.
Smoke must:
- Produce valid per_seed metrics with all 6 encoders measured on T1+T2.
- Show E2 (the current default) achieves top1_recall >= 0.5 on T1 at M=100 (sanity: known good encoder works at smoke scale).
- Run end-to-end in <= 180s on CPU.

## REQUIRED_FIELDS in metrics.json
verdict, verdict_msg, elapsed_s, summary, run_mode, n_seeds, config_version,
per_seed (list of dicts with seed + matrix), aggregate (with matrix mean per (encoder, task)).

## Self-test
1-second mechanism check: each encoder produces N-dim vectors with the right distribution (sparsity / boundedness); HRR bind+unbind round-trips approximately at M=10.

## Risk
This cell's primary risk is the WRONG cell-level threshold: T3 capacity threshold 1000 may be too aggressive for some encoders given N=8192. We will accept MIDDLE_BAND verdict and let Skunkworks adjudicate. There is NO PASS-by-construction risk: all 4 tasks involve seed-randomized atoms with no closed-form perfect answer; T1/T3 are crosstalk-limited and T4 measures crosstalk directly.

## Verdict text policy
verdict_msg will:
- List PASS/FAIL per (encoder, task) cell (24 entries).
- Identify best encoder per task (4 entries).
- Identify any encoder in top-2 across ALL 4 tasks.
- Report cell-level verdict.
- NOT claim "winning encoder" if no encoder PASSes all 4 -- MIDDLE_BAND in that case.

## Dispatch
- queue: local_cpu_queue
- timeout: 2700s (45 min; well above 30-min estimate).
- ASCII-only.
- single primary metric per task.
