# Pre-reg: dg_style_expansion_layer_smoke_v1 (substrate-native dentate-gyrus analog)

**Date:** 2026-06-23
**Anchor:** dg_style_expansion_layer_smoke_v1
**Cell:** experiments/exp_dg_style_expansion_layer_smoke_v1.py
**Queue:** local_cpu_queue (numpy-only; smoke wall ~10min)
**Run-mode:** smoke (smoke gate first per Exp-Dev contract)
**Author:** Exp-Dev (cell author + dispatch)
**Pre-reg source-of-truth:** USER 2026-06-23 directional pushback on top-enabler concern 1.1 -- "why don't we have an equivalent expansion layer?"

## Question

Does sparse expansion projection (N_input=4096 -> N_expanded=16384, K=5 nonzero per row, +/- 1 bipolar) orthogonalize similar inputs the way brain dentate gyrus (DG) does, lifting substrate cleanup recall at high noise (sigma=1.5)?

Brain DG: 200k entorhinal-cortex (EC) neurons project to ~1M DG granule cells (5x expansion); each DG granule cell receives ~5 mossy-fiber inputs (K_sparse=5); only ~2-3% of DG cells fire for any cue (sparse output). Net effect: similar EC inputs decorrelate in DG via random sparse projection + sparse output -- the canonical "pattern separation" circuit (Cayco-Gajic 2017; Litwin-Kumar 2017; Marr 1971).

## Information-decisive design

- **HARD_PASS:** substrate CAN host a brain-style expansion layer; sparse expansion is the missing primitive; ship hdlab/dg_expansion.py + queue capacity-sweep replication on real corpora.
- **HARD_FAIL:** substrate bottleneck is NOT dimensionality; sparse expansion to 16384 doesn't lift recall at high noise; pivot away from expansion-as-primary-lever.
- **MIDDLE_BAND:** partial mechanism (e.g. sparse lift helps but +kWTA doesn't, or one arm hits floor but not target).

## Arms (4)

1. **ARM_FLAT_N4096** -- baseline; argmax in N=4096 (current substrate); reproduces Shannon-floor at sigma=1.5.
2. **ARM_DENSE_LIFT_N16384** -- lift via DENSE random gaussian projection W_dense [16384, 4096] (JL-scaled 1/sqrt(4096)); argmax in lifted 16384 space.
3. **ARM_DG_SPARSE_LIFT_N16384** -- lift via SPARSE random projection W_DG [16384, 4096]; each row has K=5 nonzero bipolar entries at random positions (cerebellar/DG fan-in regime per Litwin-Kumar 2017); argmax in lifted 16384 space.
4. **ARM_DG_SPARSE_LIFT_PLUS_KWTA** -- sparse K=5 lift + k-WTA top-2% output (full DG-style: sparse projection AND sparse output, keep top 327 of 16384 entries per encoded atom).

## Config (smoke)

- N_INPUT = 4096
- N_EXPANDED = 16384
- K_SPARSE = 5 (nonzero entries per row of W_DG)
- M = 200 (real WordSim353 word vocabulary via word2vec)
- KWTA_FRAC = 0.02 (top 2% of 16384 = 327 entries kept)
- Encoder = word2vec-google-news-300 (300d -> 4096d via per-seed gaussian projection; banked clean-external-data approach)
- N_EVAL = 50
- Seeds = [7]
- SIGMA_SWEEP = [0.0, 0.5, 1.0, 1.5, 2.0]
- DISCRIMINATOR_SIGMA = 1.5

## Metrics

### (A) Cleanup recall@1 per (arm, sigma) -- N_EVAL queries; argmax in arm's representation space.

### (B) Pairwise orthogonality of encoded atom representations -- mean abs cosine across all unique atom pairs (lower = more orthogonal = better pattern separation).

### (C) Effective dimensionality (participation ratio of singular value spectrum): `(sum s_i)^2 / sum(s_i^2)`. Higher = atoms span more of the available dimensions.

## Pre-reg HARD bands

### HARD_PASS (DG expansion lifts substrate at high noise; chain-grade-eligible substrate-native pattern separation)

BOTH must hold:
- ARM_DG_SPARSE_LIFT_PLUS_KWTA `recall@sigma=1.5 >= 0.20` (substantial lift over ARM_FLAT_N4096 baseline expected ~0.02).
- ARM_DG_SPARSE_LIFT_PLUS_KWTA `mean_abs_cosine` reduced by `>= 30%` vs ARM_FLAT_N4096 (orthogonality improvement).

### HARD_FAIL (expansion doesn't help; substrate bottleneck isn't dimensionality)

- ARM_DG_SPARSE_LIFT_N16384 AND ARM_DG_SPARSE_LIFT_PLUS_KWTA both have `recall@sigma=1.5 <= ARM_FLAT_N4096 + 0.02` (no measurable lift; expansion null).

### MIDDLE_BAND

- Partial: one DG arm clears recall threshold but orthogonality fails, or orthogonality lifts but recall doesn't move (mechanism partial; refine before chain-grade claim).

## Sanity self-tests (must hold for ALL arms; BLOCKS dispatch on FAIL)

- `sigma=0.0` endpoint: ALL arms `recall@1 == 1.000` (clean cue, perfect cleanup by construction).
- Identical-input duplicates: arms produce identical hashes for identical inputs (deterministic encoding given fixed seed).
- `W_DG.shape == (16384, 4096)`; each row has exactly K=5 nonzero entries; nonzero entries in {-1, +1}.

## Pre-flight discipline applied

- Clean external word2vec data (no substrate-self contamination; per banked methodology).
- Name-leak not applicable (real WordSim353 words encoded, not atom IDs that would leak labels).
- Fresh substrate state per arm (no shared W_DG across arms).
- Self-test BEFORE dispatch (selftest gated; runs on cell import).

## Substrate-only

n_llm_calls = 0; numpy + gensim downloader (open-weight bundle; word2vec-google-news-300 cached locally).

## Status_log

event_kind="experiment_ship" importance=HIGH (USER directional pushback test; pattern-separation primitive missing from substrate).

## Cites

- USER 2026-06-23 directional pushback on top-enabler concern 1.1: "why don't we have an equivalent expansion layer?"
- Cayco-Gajic et al. 2017 ("Sparse synaptic connectivity is required for decorrelation and pattern separation in feedforward networks"); Litwin-Kumar et al. 2017 ("Optimal Degrees of Synaptic Connectivity"); Marr 1971 (DG/CA3 theory).
- experiments/exp_sparse_engram_allocation_smoke_v1.py (sibling cell; sparse representations at INPUT, not expansion).
- experiments/exp_encoder_word2vec_substrate_bind_v1.py (word2vec loader pattern reused).
- Shannon-floor META reference (sigma=1.5 ~0.020 floor).
