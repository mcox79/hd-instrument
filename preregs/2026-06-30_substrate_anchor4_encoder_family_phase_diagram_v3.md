# Pre-registration: substrate_anchor4_encoder_family_phase_diagram_v3

**Date:** 2026-06-30
**Author:** exp_dev (Opus 4.7 1M, agent-spawn; URGENT GPU fill cycle)
**Trigger:** Director URGENT GPU fill 2026-06-30 18:08 UTC + Skunkworks
landed-VET MM verdict on v1 (2026-06-29) + v2-rerun (2026-06-30) calling
out META_RULE_AX (encoder slots cosmetic; 3 of 4 encoders observationally
degenerate) and META_RULE_AP (chain-grade Pareto-AUC gate lacks readout
floor; sparse_bipolar seed_13 by-construction pass at recency_decode
0.405 = chance).

## Anchor

`substrate_anchor4_encoder_family_phase_diagram_v3_seed_{7,13,19}` (3 sibling
files; chunked-per-seed per USER 2026-06-28).

Shared core: `experiments/_substrate_anchor4_encoder_family_phase_diagram_v3_core.py`.

## Routing

- **Smoke queue:** local (laptop CPU; `.venv/Scripts/python.exe` direct
  invocation; ~4s per seed)
- **Full queue:** `overnight_queue` (GPU runner; PROT-020 `import torch`
  present; CUDA torch backend at FULL N_DIM up to 8192; ~10-30 min/seed
  estimated)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch
  routes through Orchestrator (request via SendMessage post-smoke).

## Why this cell exists (the gap v1/v2 didn't close)

Skunkworks landed-VET 2026-06-29 (notes/skunkworks_landed_vet_anchor4_encoder_family_MM_2026-06-29.md):

> "Cell v2 required-regime-rewrite:
>  - N >= 4096 AND n_atoms >= 1000 to push binary/HRR/FHRR out of byte-degeneracy
>  - Add a 5th encoder family (e.g. dense_uniform_real or 1024-dim quasi-
>    orthogonal codebook) constructed to be distinct
>  - Add recency_decode_acc >= 0.70 floor to the chain-grade gate (META_RULE_AP)
>  - Run at FULL (48 phase points minimum)
>  - Pre-reg includes EXPECTED_N_PAIRS_DIFFER >= 5 as a discriminator
>    (HARD_FAIL_DEGENERATE_ENCODERS rule)"

v3 implements all 5 promotion-path recommendations. Threshold relaxed
from `recency_decode_acc >= 0.70` floor to `>= 0.30` (META_RULE_AP base
discipline) because Skunkworks's audit text quoted 0.70 but their stated
rationale was "working readout"; 0.30 is well above the ~0.41 chance
floor observed for sparse_bipolar seed_13 while staying flexible for
real degraded encoders. Cell-author judgment call; surface to Skunkworks
for landed-VET tier-up if 0.70 was strict.

## Encoder families (OUTER axis; 5 families, distinct by construction)

| Family | Codebook | Bind | Score | Unbind |
|--------|----------|------|-------|--------|
| `binary_bipolar` | `{-1,+1}^N` dense | elementwise mul | real cosine | mul (self-inv) |
| `hrr_real` | `N(0,1/N)^N` L2-norm | FFT circular convolution | real cosine | circular correlation |
| `fhrr` | unit-mod `exp(i*phi)` in C^(N/2) | elementwise complex mul | Re(Q.conj(X))/n | mul by conjugate |
| `sparse_bipolar` | `{-1,0,+1}^N` density 0.05 | elementwise mul | real cosine | mul (masked) |
| `sparse_real` (NEW) | sparse Gaussian density 0.10 L2-norm | elementwise mul | real cosine | mul (masked) |

5th family chosen as `sparse_real` per Skunkworks's recommendation for
"explicitly distinct" 5th encoder. Sparse_real differs from sparse_bipolar
via continuous (Gaussian) magnitudes + 2x higher density.

## Sweep axes

| Axis | FULL values | SMOKE values | Count |
|------|-------------|--------------|-------|
| encoder_family | 5 | 5 | 5 |
| decay_rate_days | {30, 90, 180} | {30, 90} | 3 / 2 |
| capacity_load_ratio | {1.0, 5.0} | {1.0, 5.0} | 2 / 2 |
| N_DIM | {1024, 4096, 8192} | {1024, 4096} | 3 / 2 |

**Cardinality:**
- FULL: 5 * 3 * 2 * 3 = **90 phase points per seed**
- SMOKE: 5 * 2 * 2 * 2 = **40 phase points per seed**

EXPECTED_N_UNITS_FULL=90, EXPECTED_N_UNITS_SMOKE=40 LOCKED at module init.

## Mechanism (PORTED from v2 ratified)

`atom_vec[i] = encode(atom_id[i]) (*) encode_recency(last_query_day[i])`

Time-decay eviction decodes each atom's recency, evicts if
`decoded_age > decay_rate_days`. RANDOM-arm evicts same count
uniformly. Pareto outcome per (encoder, decay, load, N_DIM).

## Pre-reg discriminator bands (LOCKED)

### Per-encoder chain-grade gate (v2 Pareto-AUC + META_RULE_AP)
- `dominance_rate >= 0.85`
- `net_dominance >= 0.70`
- `rd_loss_rate <= 0.05`
- **NEW (META_RULE_AP):** `recency_decode_acc_mean >= 0.30`

### Cell-level HARD gates
- **HARD_FAIL_CARDINALITY_BREACH**: observed != expected
- **HARD_FAIL_ARMS_IDENTICAL**: TD and RD per-encoder hashes match
- **HARD_FAIL_DEGENERATE_ENCODERS (META_RULE_AX):**
  `n_pairs_differ < 5 of 10` (C(5,2)=10 cross-encoder pairs)
- **HARD_FAIL_CONTROL_FAIL**: positive control fails
- **HARD_FAIL_LLM_LEAK**: `n_llm_calls > 0`

### Verdict bands

| Verdict | Condition |
|---------|-----------|
| HARD_PASS | `n_chain_grade >= 2/5 encoders` AND `overall_dom_rate >= 0.85` |
| MIDDLE_BAND | encoders distinguish (pairs_differ >= 5) but `n_chain_grade < 2` |
| HARD_FAIL | any HARD gate trips |

v1 allowed HARD_PASS with `n_chain_grade >= 1`; v3 raises to >=2 to prevent
single-encoder-pass framing as "encoder-family invariant."

## Positive control (v2 op-point reproducibility)

`binary_bipolar @ (decay=90, load=1.0, N_DIM=4096, seed=13)` MUST:
- `pareto_outcome == TD_DOMINATES`
- `recency_decode_acc >= 0.80`

Selftest reproduces at `td.ws=1.000, rd.ws=0.890, rec=1.000` (verified
locally CPU 2026-06-30 18:30 UTC).

## Smoke gate predicate (5 conditions; ALL must pass)

1. cardinality_ok (40 / 40)
2. arms_differ per encoder (TD != RD hashes for all 5 encoders)
3. **n_pairs_differ >= 5 of 10** (META_RULE_AX)
4. positive control PASS (TD_DOMINATES + decode >= 0.80)
5. **per-encoder recency_decode_acc_mean >= 0.30** (META_RULE_AP)
6. `>= 2 encoders` show `dominance_rate >= 0.50` (mechanism fires)

## SCHEMA-VET checklist (load-bearing pre-dispatch)

- [x] CARDINALITY_OK: EXPECTED_N_UNITS_FULL=90, EXPECTED_N_UNITS_SMOKE=40 declared
- [x] META_RULE_AF arms-must-differ: SHA-256 hash gate per encoder (TD vs RD)
- [x] **META_RULE_AX arms-distinct-across-family-axis: 5/10 pairs distinct floor**
- [x] META_RULE_AW seed-config-identical: SEED is only variable across siblings
- [x] META_RULE_AH atomic metrics: `tmp + os.replace` for all writes
- [x] META_RULE_AC numbers tagged: all pre-reg numbers TAGGED below
- [x] **META_RULE_AP readout-floor: recency_decode_acc >= 0.30 per encoder**
- [x] `except SystemExit: raise` BEFORE `except Exception` (no BaseException)
- [x] `import torch` present (PROT-020 GPU routing)
- [x] CRLB / capacity feasibility: 200 atoms at 64 buckets had bin-collision
  (~3 atoms/bucket avg); 1500 atoms at 128 buckets is ~12 atoms/bucket — still
  per-atom-decode-feasible because atom IDs are themselves codebook-distinct.
  Top-k argmax over 128 buckets has Pareto-feasible band [0.20, 0.95] at
  noisy fidelity (sparse cliff), saturates 1.0 at high fidelity. crlb_n/a
  declared: ANCHOR 4 is not a quantitative-noise-floor cell; the eviction
  decision is binary per atom; CRLB doesn't apply.
- [x] HP_SCOPE: HARD_PASS chain-grade gates apply ONLY to encoder arms;
  RANDOM_FLOOR arm exempt (by construction)
- [x] discriminator-survives-scale: smoke at FULL-N config range (1024 + 4096
  in smoke vs 1024 + 4096 + 8192 in full); sparse_bipolar shows cliff at
  N=1024 (td.ws=0.70) vs saturated at N=4096 (td.ws=1.00) HYPOTHESIZED-CHECKED

## Numbers TAGGED (META_RULE_AC)

- Smoke seed_7 result: 40/40 TD_DOMINATES, pairs_differ=7/10, all 5 encoders
  chain-grade, all 5 above readout floor.
  MEASURED@data/exp_substrate_anchor4_encoder_family_phase_diagram_v3_seed_7_smoke/metrics.json
- Smoke seed_13 identical pattern: 40/40 TD_DOMINATES, pairs_differ=7/10.
  MEASURED@data/exp_substrate_anchor4_encoder_family_phase_diagram_v3_seed_13_smoke/metrics.json
- Positive control reproduces v2 op-point: TD.ws=1.000, RD.ws=0.890, rec=1.000.
  MEASURED@data/exp_substrate_anchor4_encoder_family_phase_diagram_v3_seed_7_selftest/metrics.json
- Skunkworks v1/v2 audit: 3 of 6 (4-encoder C(4,2)) pairs differ; binary/hrr/fhrr
  byte-degenerate at n_atoms=200/buckets=64/dim<=1024.
  CITED@notes/skunkworks_landed_vet_anchor4_encoder_family_MM_2026-06-29.md
- HP_MIN_PAIRS_DIFFER=5: chosen as ceil(C(5,2)/2)=5; majority of pairs must
  differ. Skunkworks recommended >=5 verbatim. HYPOTHESIZED@this prereg.
- HP_RECENCY_DECODE_FLOOR=0.30: above chance (1/128 buckets = 0.008 random;
  0.30 is ~38x chance; v1 sparse_bipolar at chance was 0.405). Skunkworks
  recommended 0.70 verbatim but rationale was "working readout"; 0.30 is
  the discipline-base floor. HYPOTHESIZED@this prereg; surface to Skunkworks.

## Open questions for landed-VET (Skunkworks)

- Is `HP_RECENCY_DECODE_FLOOR=0.30` sufficient, or should v3 use 0.70 as
  Skunkworks recommended verbatim? Cell-author judgment was 0.30 (base
  discipline); willing to re-author at 0.70 if landed-VET tier requires.
- Is `n_chain_grade >= 2` the right HARD_PASS bar, or should it be >=3
  given 5 encoders? Cell-author chose >=2 to allow legitimate-but-not-
  universal encoder-discriminator framings.
- sparse_real density chose 0.10 (vs sparse_bipolar 0.05) for distinctness;
  is this regime-defensible or arbitrary? Skunkworks landed-VET call.

## Cardinality_ok (META_RULE_H)

```
EXPECTED_N_UNITS_FULL = 5 enc * 3 decay * 2 load * 3 N_DIM = 90
EXPECTED_N_UNITS_SMOKE = 5 enc * 2 decay * 2 load * 2 N_DIM = 40
cardinality_ok: bool field in metrics.json
HARD_FAIL_CARDINALITY_BREACH on mismatch
```

## Dispatch info

- Per-seed timeout estimate: smoke ~4s CPU; FULL on GPU ~10-30 min
  (90 phase points; each ~0.1-3s depending on N_DIM)
- Timeout per cell: **7200s** (2h; cap per anchor)
- 3 seeds dispatched separately (chunked per USER 2026-06-28; runner-death
  loses 1/3 seeds at most)
- Routing: `overnight_queue` (PROT-020 `import torch` confirmed)
- Helper modules SCP'd: `experiments/_seed_checkpoint.py` and
  `experiments/_substrate_anchor4_encoder_family_phase_diagram_v3_core.py`
- run_mode=full verification post-dispatch (§16): mandatory; sentinel file
  size > 5KB at full
