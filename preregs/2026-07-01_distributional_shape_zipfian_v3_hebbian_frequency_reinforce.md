# Pre-Reg: Zipfian v3 Hebbian Frequency-Reinforcement (B.1 + B.2)

**Date:** 2026-07-01
**Author:** hdi_exp_dev
**Cell slug (B.1):** `distributional_shape_zipfian_v3_hebbian_frequency_reinforce_seed_7`
**Cell slug (B.2):** `distributional_shape_zipfian_v3_hebbian_wmatrix_canonical_seed_7`
**Trigger:** Skunkworks Batch-1 follow-up recommendation post v2 HF_PREDICTION_FAILS
**Novelty check:** substrate-KB concept-query cosine=0.2529 (top hit "Reinforcement"); well below 0.30 threshold; NOVEL.
**Prior-work check:** `notes/exp_a4.md::chunk003` (Hebbian reinforcement ratio work) is closest atom at 0.216 cosine, unrelated regime.

## Hypothesis (source: sparse-coding drill 2026-07-01)

v2 falsified sparse-coding drill's two-tier prediction for dense-Hopfield READ-REPLACE. Drill argued: reason is dense-Hopfield tape stores each item ONCE (no reinforcement mechanism). Willshaw synaptic saturation predicts head items get thicker storage under Zipf, so head recovers from noise while tail collapses.

**v3 tests two operationalizations:**
- **B.1 tape-write-scale (softmax READ-REPLACE):** K_tape[i] = eta_i * L2norm(keys[i]); V_tape[i] = eta_i * L2norm(vals[i]). eta_i = sqrt(freq_i / freq_max).
- **B.2 canonical Hebbian W-matrix:** W = sum_i eta_i * outer(vals[i], keys[i]) / N; readout = sign(q @ W.T); cleanup against vals.

**Predicted (drill's Willshaw signature):** at (alpha=1, sigma>=0.15, load in [0.10, 0.14]), Q1_head - Q4_tail >= 0.30.

## Pre-flight probe findings (2026-07-01, LOAD-BEARING)

**B.1 (tape-write-scale) at N=8192:** catastrophic collapse. All recall values in 0.005–0.055 range regardless of alpha, sigma, load. Q4=0 uniformly. Physics: per-row eta scaling breaks softmax scale-invariance; argmax collapses to highest-eta row (rank-1 head) regardless of query. MEASURED@d:/AI/hd-instrument/data/exp_distributional_shape_zipfian_v3_hebbian_frequency_reinforce_seed_7_smoke/metrics.json (preview arm) — post-smoke.

**B.2 (canonical Hebbian W-matrix) at N=512-1024:** REVERSE-direction gap. At (alpha=1, sigma=0.30, load=0.05, N=512): Q1=0.964, Q4=1.000, gap=-0.036 (tail-favored, opposite drill). At (alpha=1, sigma=0.30, load=0.14, N=512): Q1=0.873, Q4=0.905, gap=-0.032. Same direction across all Zipf+noise regimes probed. Physics: head items dominate W superposition → head cross-talk high → head queries pull noisy weighted-sum responses. Tail items contribute little to W but their target keys are unique + clean.

## Falsifiable predictions (verdict gates)

**B.1 cell:**

HP_TWO_TIER_HEBBIAN (drill vindicated):
- at (alpha=1.0, sigma in [0.15, 0.30], load in [0.10, 0.14]), recall_Q1 - recall_Q4 >= 0.30 at any window point in FULL run (N=8192)
- HP_SCOPE: window arms only (not control/baseline)

HF_B1_INSUFFICIENT (drill falsified, B.1 architectural):
- at (alpha=1.0, sigma=0.30, load in {0.10, 0.12, 0.14}), MAX gap < 0.10
- indicates tape-write-scale reinforcement doesn't produce drill's signature

HF_INFRA:
- BASELINE_OUT_OF_BAND: (alpha=0, sigma=0, L=0.05) < 0.85 at full
- UNIFORM_ASYMMETRY_LEAK: alpha=0 gap > 0.10 (implementation bug)
- CARDINALITY_BREACH: len(core) != 54
- META_RULE_AF: <10 distinct arm signatures

**B.2 cell:**

HP_HEBBIAN_ANY_ASYMMETRY (mechanism produces detectable asymmetry, either direction):
- at (alpha=1.0, sigma in [0.15, 0.30], load in [0.10, 0.14]), |Q1 - Q4| >= 0.10 at any window point (FULL run)

HF_HEBBIAN_ISOTROPIC (drill AND its reverse falsified):
- at same window, MAX |gap| < 0.05 → substrate shows NO Zipfian-driven asymmetry

Same infra failure modes.

## Sweep

**Both cells:** 3 alpha (0.0, 1.0, 2.0) × 3 sigma (0.0, 0.15, 0.30) × 6 load (0.05, 0.08, 0.10, 0.12, 0.14, 0.18) = 54 arms.

**Load grid** centered on classical Amit-Gutfreund wall M/N = 0.138.

## Discipline gates satisfied

- `cardinality_ok`: EXPECTED_N_UNITS = 54
- CARDINALITY_OK stamped
- ARMS-MUST-DIFFER hash-test at verdict
- ATOMIC-FINAL-METRICS-WRITE tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- CRLB: sigma_binomial = 0.0158; sigma_stratified = 0.032 THEORETICAL@binomial-CLT
- HP gap 0.30 (B.1) = 9.4 sigma_stratified (reachable)
- HP |gap| 0.10 (B.2) = 3.1 sigma_stratified (reachable)
- baseline_in_band: (alpha=0, sigma=0, L=0.05) ~ 1.000 at N=8192
- **DISCRIMINATOR-MUST-SURVIVE-SCALE**: smoke includes full-N=8192 previews (Zipf + control) for both cells
- META_RULE_L strict-band: HP thresholds strict `>=`
- META_RULE_M calibration: B.1 adaptive_with_discriminator_gate (beta=log2(M)/margin); B.2 default_ok_for_this_regime
- META_RULE_AC provenance: all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
- Chunked one-seed-per-cell architecture (§13)
- Start-marker + crash-diagnostic + heartbeat inline
- ASCII-only

## Expected result and hand-off

Given pre-flight probe evidence, **most likely outcome:**
- **B.1**: HF_B1_ARCHITECTURAL_COLLAPSE (smoke preview shows r_all < 0.1 across all arms; not "insufficient" so much as "wrong mechanism-class for softmax attention").
- **B.2**: MIDDLE_BAND_TAIL_FAVORED or HF_HEBBIAN_ISOTROPIC (probe suggests gap ~ -0.03 to -0.06, borderline).

**If either smoke fires MB/HP:** hand off to Skunkworks + Director for full dispatch to overnight_queue (via hdi_orchestrator per push-denied constraint).

**If both smoke HFs:** compile joint HALT_ATOMIZE hand-off: Willshaw-canonical Hebbian frequency-reinforcement two-tier prediction falsified across BOTH B.1 (softmax) AND B.2 (linear W-matrix) mechanism-classes at Amit-Gutfreund wall regime. Would be a stronger closure than v2 (single mechanism falsification).

## Cross-references

- Sparse-coding drill: `notes/research_sparse_coding_compressed_sensing_2026-07-01.md`
- v2 HF hand-off: `notes/exp_dev_findings/exp_distributional_shape_zipfian_v2_HF_PREDICTION_FAILS_2026-07-01.md`
- v2 cell: `experiments/exp_distributional_shape_zipfian_v2_seed_7.py`
- Willshaw 1969 CITED, Palm 2010 CITED, Amit-Gutfreund-Sompolinsky 1985 CITED, Ramsauer 2021 CITED

## Timeout estimates (per Skunkworks/PROT-019)

**B.1 FULL:** smoke_wall ~ 60s at N=1024 (54 arms). Full scaling: (8192/1024)^1.5 = 22.6. Full timeout: ceil(1.5 * 60 * 22.6) = 2034s → round to 3600s per PROT-019.
**B.2 FULL:** smoke_wall ~ 150s at N=1024 (54 arms with W-matrix build). Full scaling: matrix ops = (8192/1024)^2 = 64. Full timeout: ceil(1.5 * 150 * 64) = 14400s → 4h, at PROT-019 ceiling. Justification: B.2 requires (N x N) accumulator + argmax scan; matrix op scaling exp = 2.0 per PROT-019 guidance.
