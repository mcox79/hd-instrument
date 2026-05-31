# Pre-registration: reasoning_storage_scheme_b_smoke_v1_n16384

Date: 2026-05-31
Anchor: reasoning_storage_scheme_b_smoke_v1_n16384
Script: experiments/exp_reasoning_storage_scheme_b_smoke_v1_n16384.py
Queue: remote_cpu_queue
PROT-018: _n16384 binds N = 16384

## Context

2x deep research synthesis (notes/research_substrate_reasoning_storage_2x_synthesis_v1_2026-05-31.md)
surfaced a SHARP operational picture:
- Scheme B three-way bipolar binding gives exact audit decomposition (algebraic).
- Path D's validated 32N envelope may NOT transfer to structured-key corpora.
- 6 operational gaps including: substrate is retrieval primitive, not reasoning primitive.

This experiment tests the empirical performance under structured-key conditions.

## Scientific question

Does structured-key reuse (5 inference-rule codewords shared across 500 reasoning
chains at N=16384) produce measurable per-step retrieval accuracy degradation vs
a matched random-key baseline? Does conclusion re-encoding mitigation restore the
random-key envelope?

## Configuration

- N = 16384 (PROT-018 binding)
- BSC bipolar codebook: 5 rule + 200 entity + 20 relation codewords
- Structured corpus: 500 chains, depth 3-5 (avg ~4 steps), M_steps ~ 2000
- Random-key corpus: same M_steps, same conclusion assignment, i.i.d. BSC keys
- Mitigation arm: conclusion re-encoding via rho permutation (Steinberg-Sompolinsky 2022)
- 3 seeds: [7, 17, 23]
- Device: CPU (remote_cpu_queue)

## N-suffix

`_n16384` -> production N = 16384 (PROT-018 binding).

## Pre-registered bands

### Arm A: Scheme B encoding audit

Metric: cosine confidence of three-way unbinding to nearest-neighbor in codebook.
For bipolar k_step = r * k1 * k2: unbinding r_rec = k_step * k1 * k2 = r (exact).
Confidence = <r_rec, r> / N = 1.0 exactly for stored codewords.

- HARD-PASS: all 3 components (r_type, k_premise1, k_premise2) have frac_above_hp > 0.95
  for frac of checked steps with confidence > 0.95. (95% of steps pass @ > 0.95 conf.)
- HARD-FAIL: any component has frac_below_hf >= 0.05 for confidence <= 0.70.
- MIDDLE-BAND: between HARD-PASS and HARD-FAIL.

### Arm B: Structured-key Path D differential

Metric: mean per-step retrieval accuracy.
Query: k_step -> W -> argmax over entity codebook -> target = conclusion_idx.

- HARD-PASS: struct_acc >= 0.95 * rand_acc (within 5% of random; shared keys don't hurt).
- HARD-FAIL: struct_acc <= 0.85 * rand_acc (> 15% degradation).
- MIDDLE-BAND: 0.85 < ratio < 0.95.

### Arm C: Conclusion re-encoding mitigation

Metric: mean per-step retrieval accuracy for mitigated corpus.
Mitigation: rho(i) = (i * 47) % 200 permutation applied to conclusion vectors.

- HARD-PASS: mitig_acc >= 0.95 * rand_acc (mitigation restores envelope).
- HARD-FAIL: delta = mitig_acc - struct_acc < 0.02 (mitigation provides no benefit).
- MIDDLE-BAND: partial restoration.

### Overall verdict

- RSB_HARD_PASS: all 3 arms HARD-PASS.
- RSB_HARD_FAIL: 2 or more arms HARD-FAIL.
- RSB_PARTIAL: 1 arm HARD-FAIL + 1+ HARD-PASS.
- RSB_MIDDLE_BAND: otherwise.

## Timeout estimate

- Smoke wall: 1.07s (N=512, 1 seed, 3 corpora, all ops)
- FULL N=16384 vs smoke N=512: dim ratio = 32. W build is O(M * N^2).
  M scales from 81 to ~2000 (~25x). N^2 scales 1024x. But empirical W build
  benchmarks: N=512: 0.016s, N=1024: 0.113s, N=2048: 0.719s. Exponent ~2.7.
  Extrapolated N=16384: ~130s per build. 3 corpora x 3 seeds x 130s = 1170s.
  Other ops (audit, retrieval, SVD@7.8s each): ~3 seeds x 3 x 8s = 72s.
  Total estimate: ~1242s. With 1.5x safety: ~1863s.
- PROT-019 floor: 14400s (well accommodated).
- timeout_s = 14400

## Dependencies

- BSC codebook construction: self-contained (no external files required).
- _seed_checkpoint.py: present at d:/AI/hd-instrument/experiments/_seed_checkpoint.py.
- No external data files required (all generated from seed).

## Walk-back assessment

Smoke effect size: struct_acc = 1.000, rand_acc = 1.000. At N=512 with M=81 steps
(M/N = 0.158), both corpora are sub-capacity -- no degradation expected at smoke scale.
The FULL run at N=16384 with M~2000 steps (M/N = 0.122) is still sub-capacity, so
we expect both to show high accuracy. The differential will be small -- the interesting
result is whether structured keys cause ANY measurable degradation. Walk-back not
triggered (effect size at smoke is degenerate: both = 1.0 due to trivial sub-capacity).
