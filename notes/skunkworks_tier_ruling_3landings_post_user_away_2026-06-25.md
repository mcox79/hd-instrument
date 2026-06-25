# Skunkworks tier ruling: 3 landings (Cell I v3 / compose v4 / unsup encoder v1)

Date: 2026-06-25 | Auditor: Skunkworks
Method: independent off-data recompute via .venv numpy on each metrics.json; cross-ref vs v2 prior ruling (Cell I) and vs v3 reference cell (compose v4); Fix #28 per-arm + N1 verify-the-referent + by-construction-saturation tiering.

---

## Cell 1: substrate_basis_layer_label_contamination_proof_v3_band_corrected

### TIER: CHAIN_GRADE_PARTIAL (upgrade from v2 MEASURED_MECHANISM)

Promote v2 MM to CHAIN_GRADE_PARTIAL. NOT full DEFINITIVE. Counts +1 toward CERT N (replaces v2 atom if already filed).

### Per-arm evidence (off-data recompute, all 5 seeds [7,13,17,23,29])

| Arm | top1 mean±std | top5 mean±std | comp top5 mean±std | within_cat_cos |
|---|---|---|---|---|
| RAND | 0.6471±0.0066 | 0.9994±0.0004 | 0.6760±0.0880 | -0.0001±0.0002 |
| LABEL_BASIS | 0.5480±0.0078 | **0.8056±0.0062** | 0.5292±0.0397 | **0.1991±0.0002** |
| EMERGENT_DW | 0.6458±0.0069 | 0.9965±0.0018 | 0.7063±0.0504 | 0.0812±0.0022 |
| EMERGENT_OLS | 0.6471±0.0066 | 0.9994±0.0004 | 0.6792±0.0369 | 0.0001±0.0001 |

LABEL-RAND retr top5 per seed: -0.184, -0.199, -0.191, -0.193, -0.201 (consistent, zero crossovers). LABEL-RAND retr top1 per seed: -0.098, -0.095, -0.098, -0.103, -0.102. DW-LABEL comp top5 per seed: +0.151, +0.245, +0.120, +0.260, +0.109 (all 5 positive, mean +0.177). OLS-LABEL comp top5: +0.198, +0.198, +0.052, +0.135, +0.167 (all positive).

### Why PARTIAL not DEFINITIVE

All PROVEN gates fired correctly; REFUTE didn't fire; within_cat_cos mechanism diagnostic hit designed 0.199 to 3 decimals across 5 seeds. Three of four c3_retrofit mitigations strong: (1) top5 discriminator visible in v2 raw before band tuning [verified: v2 metrics.json has top5=0.806 LABEL vs 0.995+ RAND/DW/OF], (2) relative-top1 gate is the literal statement of BIAS-13 (the principle predicts a relative differential, not an absolute level), (3) my META `RULE_4arm_principle_band_must_be_capacity_feasible` PRE-DATES v3 author choice.

Residual concern: **same numerics, different bands**. v2's bit-identical per-arm results re-evaluated against new bands produced PASS instead of REFUTE. The mitigation above explains why the band change is principled, not why it's prospective. A truly DEFINITIVE upgrade would require **bands set BEFORE the data exists** landing PASS. v3 is retrospective by construction. So: CHAIN_GRADE_PARTIAL.

### By-construction-saturation: NOT saturated

RAND top1=0.6471 << 0.995 Q-rail. RAND top5=0.9994 is at storage ceiling (5-of-300 = 1.7% tolerance, by-construction headroom) but LABEL_BASIS top5=0.806 is the discriminator and is NOT at ceiling. Within_cat=0.199 is the DESIGNED cone-collapse, not saturation artifact (verified: RAND and OLS within_cat=0 at same regime).

### Atomization

**Math atom (CHAIN_GRADE_PARTIAL):** `T3/EXP_substrate_basis_layer_label_contamination_proof_v3_CGP`. BIAS-13 principle supported at V=300/N=8192/M=2400/sparse_f=0.02. Mechanism: within_cat_cos=0.199 (designed) fires; cross_cat=0; RAND/OLS within_cat=0 confirms cone-collapse orthogonal to saturation. Caveat: retrospective re-banding; structural retrofit-risk remains. Supersedes v2 MM atom (net +0 if v2 filed, +1 if not).

**META atom (PROPOSE):** `RULE_retrospective_band_correction_max_one_tier_lift`. T_methodology. Rule: retrospective re-banding may lift tier at most one step (MM→CGP; never directly to DEFINITIVE). Composes with `RULE_4arm_principle_band_must_be_capacity_feasible` by capping lift-rate. Witness: this cell. Rationale: principled rebands still re-evaluate same per-arm noise realizations; prospective replication eliminates structural retrofit-risk.

---

## Cell 2: substrate_compose_freq_routing_v4_hparam_sweep

### TIER: CHAIN_GRADE_PARTIAL — first Stage 2 architectural atom

ARM_FREQ_DEEPER_TRAIN at 7.1590 BPC beats: BASELINE_FAIR_HARNESS by 0.1475 (>0.10 chain-grade), V3_REPRO by 0.0506 (>0.03 tuning-null), v4 cap_broken 7.20 by 0.041.

### Per-arm evidence (off-data recompute, 3 seeds [7,17,23])

| Arm | BPC mean±std (cv) | top1 | mrr@10 | disc top1_HF |
|---|---|---|---|---|
| BASELINE | 7.3065±0.0132 (0.0018) | 0.2134 | 0.2917 | n/a |
| V3_REPRO | 7.2096±0.0016 (0.0002) | 0.2309 | 0.3310 | 0.329 |
| **DEEPER_TRAIN** | **7.1590±0.0205 (0.0029)** | **0.2459** | **0.3377** | **0.350** |
| BIGGER_RANK | 7.1966±0.0151 (0.0021) | 0.2337 | 0.3336 | 0.314 |
| SHARPER_GRADIENT | 7.1888±0.0009 (0.0001) | 0.2364 | 0.3340 | 0.335 |
| COMBINE_W_THETA | 7.3650±0.0035 (0.0005) | 0.2240 | 0.3163 | 0.319 |

DEEPER per-seed BPC: 7.1302, 7.1701, 7.1767 — all below 7.20 cap. DEEPER vs V3_REPRO paired: +0.080, +0.041, +0.031 (all positive, mean +0.051). DEEPER vs BASELINE paired: +0.189, +0.118, +0.136 (all positive, mean +0.148; strongly significant).

### Apples-to-apples + rails

All arms share N_DIM=8192, V=4000, N_TRAIN=100k, sparse_f=0.05, 3 seeds [7,17,23], word2vec encoder (n_hit=3824 identical per seed). BASELINE drift +0.0000 from fair_harness 7.3065 (exact). V3_REPRO drift +0.0000 from v3 ref 7.2096 (exact). Both sanity rails reproduce bit-identical — independent corroboration the harness is correct.

### By-construction + overfit checks

NOT saturated: top1=0.246 (far from 1.0). NOT trivial overfit: test BPC (7.13-7.18) BETTER than dev BPC (7.87-7.91), ruling out overfit-to-dev. Deeper = more iterations through same training corpus, not more data. cv=0.0029 (tighter than v3); deeper training reduces variance, not adds it. Discriminating diagnostic: high-freq top1=0.35 vs low-freq=0.00 (differential 0.35) confirms FREQ-routing mechanism does real selective-plasticity work — not "everything improved uniformly."

### Why PARTIAL not DEFINITIVE

(1) 3 seeds (vs 5 for DEFINITIVE); paired-t has df=2. (2) Deeper-training is a knob-tune in an existing architecture, not a novel primitive. Path to DEFINITIVE: 5-seed re-run at DEEPER config (cheap, CPU-bound matmul at 8192).

### Atomization

**Atom 1 (CHAIN_GRADE_PARTIAL):** `T3/EXP_substrate_compose_freq_routing_v4_DEEPER_TRAIN_CGP`. First Stage 2 architectural finding. At N_DIM=8192/V=4000/text8 N_TRAIN=100k/word2vec sparse-bipolar f=0.05 encoder, FREQ_ROUTED_K2 with n_steps=2000 hits BPC=7.159±0.021 (3 seeds, cv=0.0029), beats BASELINE by 0.148, beats v3 FREQ_ROUTED_K2 by 0.051. Cap 7.20 broken. Selective-plasticity diagnostic fires per arm.

**Atom 2 (HARD_FAIL honest-negative):** `T3/EXP_substrate_compose_v4_COMBINE_W_THETA_HF`. Stacking freq-routing × theta two-W (4 matrices) at V=4000/N=8192 HURTS by +0.058 BPC vs BASELINE (7.365 vs 7.307); all 3 seeds hurt — not noise. The architectural composition does NOT compose at this regime. Don't re-explore without different angle.

---

## Cell 3: substrate_unsupervised_anisotropic_encoder_biology_native_v1

### TIER: SUSTAIN_CONFOUND_FAIL on DW/FOLDIAK + carve PARTIAL_MM for OLSHAUSEN

The CONFOUND_FAIL verdict is correct for DEEPWALK + FOLDIAK (sigma=0 cleanup integrity < 1.0). These need re-author. OLSHAUSEN-FIELD and KOHONEN ran clean (sigma0=1.0 across 3 seeds); OLSHAUSEN deserves a separate disposition.

### Per-arm evidence (off-data recompute, 3 seeds [7,17,23])

| Arm | BPC | sigma0 per-seed | a3 mean | cos_spread | status |
|---|---|---|---|---|---|
| RAND | 7.8652 | [1.0, 1.0, 1.0] | 0.090 | 0.011 | OK baseline |
| OLSHAUSEN | 7.8654 | [1.0, 1.0, 1.0] | 0.137 | 0.013 | OK clean |
| DEEPWALK | 7.8671 | [0.92, 0.94, 0.95] | 0.118 | 0.038 | **CONFOUND** |
| FOLDIAK | 7.9136 | [0.0, 0.0, 0.0] | 0.145 | 0.671 | **CONFOUND total** |
| KOHONEN | 7.8655 | [1.0, 1.0, 1.0] | 0.087 | 0.011 | OK null/slight-neg |

OLS-RAND BPC delta +0.0002 (tied). OLS-RAND a3 per-seed: +0.045, +0.040, +0.055 (consistent small lift).

### Provenance audit — FAILS rail

Cell-3 RAND BPC=7.8652 vs fair_harness target 7.3065 (drift +0.559). This cell did NOT match the canonical fair_harness baseline; different encoder/training pipeline. Bands `HP_FULL_BPC<=6.95` are PROVENANCE-DISCONNECTED from the 7.20-land where v4 architectural work lives. Any BPC-based disposition cannot tier-up via fair_harness ladder.

### Disposition

**SUSTAIN_CONFOUND_FAIL cell-level (re-author DW/FOLDIAK); carve PARTIAL_MM for OLSHAUSEN.**

OLSHAUSEN tied with random at BPC AND showed consistent small a3 lift (+0.047). At this regime — V=4000, N=8192, N_TRAIN=100k, this cell's provenance — Olshausen-Field 1996 forward-only sparse-coding does NOT beat random-bipolar on substrate-LM BPC. This is a HONEST_NEGATIVE-IN-REGIME (not -IN-GENERAL). The small a3 lift is real but the +0.56 BPC provenance drift from fair_harness means this isn't apples-to-apples vs the 7.20-land; a separate Olshausen-Field cell with fair_harness provenance would be a cleaner test.

### Atomization

**Atom 1 (MEASURED_MECHANISM NEGATIVE-IN-REGIME):** `T3/EXP_substrate_unsup_anisotropic_OLSHAUSEN_NULL_IN_REGIME`. Olshausen-Field at V=4000/N=8192/N_TRAIN=100k text8 → BPC=7.8654±0.0001, tied with random 7.8652 (delta +0.0002). a3 lift +0.047 (small but consistent 3 seeds). Caveat: provenance drift +0.56 vs fair_harness; NEGATIVE-IN-REGIME, not -IN-GENERAL. Counts +1 as proven boundary.

**Cell-level:** SUSTAIN_CONFOUND_FAIL on DW/FOLDIAK/KOHONEN. FOLDIAK cos_spread=0.671 + sigma0=0 = encoder collapsed to near-rank-1 (likely unscaled lateral-weight update). DEEPWALK sigma0=0.94 = sparse-bipolarize losing cleanup integrity on graph-walk codes (likely needs sparse_f=0.04 or pre-norm). KOHONEN clean but null/slight-neg a3 (0.087 < random 0.090) — drop unless Research wants HONEST_NEGATIVE-IN-REGIME atom.

---

## CERT N delta summary

- Cell I v3: +1 CGP (replaces v2 MM if filed → net +0; else +1)
- Cell I META retrospective-band: +0 (T_methodology)
- Cell 2 v4 DEEPER_TRAIN: +1 CGP (first Stage 2 architectural)
- Cell 2 v4 COMBINE_W_THETA: +1 HARD_FAIL (honest-negative)
- Cell 3 OLSHAUSEN: +1 MM-NEGATIVE-IN-REGIME
- Cell 3 DW/FOLDIAK: +0 (CONFOUND_FAIL pending re-author)

**Net CERT N change: +3 to +4.** Director: file via .venv `tools/a5_atomize_cert.py` with atomic-write + verify-load + integrity-check; commit by-path; ledger increment per-atom.

---

## META atoms to land (2)

1. **`RULE_retrospective_band_correction_max_one_tier_lift`** (per Cell 1 ruling). Caps retrospective-rebanding upgrades at one tier.

2. **`RULE_sigma0_cleanup_integrity_gate_per_arm`**. Every multi-arm encoder cell must verify sigma0_recall >= 0.99 per-arm before any other claim is trusted; an arm with sigma0 < 0.99 cannot contribute evidence FOR or AGAINST its arm-hypothesis until cleanup-integrity is fixed. Witness: Cell 3 FOLDIAK (sigma0=0) + DEEPWALK (sigma0=0.94). Cell-level CONFOUND_FAIL fires correctly; rule formalizes "cleanup is the first gate, mechanism claims are gated on cleanup-pass."

---

## Discipline self-checks (Fix #28 + N1 + Q + symmetric anti-negativity)

- **Fix #28 (per-arm metrics.json):** done for all 3 cells. Independent .venv recompute reproduces every cited number to 4 decimals.
- **N1 verify-the-referent:** Cell 2 V3_REPRO drift +0.0000 vs v3 ref 7.2096 (canonical comparator reproduces exact); Cell 2 BASELINE drift +0.0000 vs fair_harness 7.3065 (rail bit-exact); Cell I v3 within_cat_cos std=0.0002 (deterministic same as v2); Cell 3 provenance check FAILED (drift +0.56) — disqualifies Cell 3 from 7.20-land cert ladder.
- **Q-suspect:** Cell I v3 RAND top5=0.9994 near 0.995 Q-rail BUT it's top5 with 1.7% tolerance (by-construction headroom) and discriminator is the GAP (0.19 absolute), not absolute level; secondary metrics also fire (relative top1 -0.099 + within_cat_cos diagnostic). Three independent discriminators agree. Q does not invalidate.
- **By-construction-saturation:** Cell I v3 NOT saturated (RAND top1=0.65 << 1.0); Cell 2 NOT saturated (top1=0.25); Cell 3 NOT saturated on trustworthy arms (BPC=7.87 barely above unigram 7.74 — under-saturated, not over-).
- **Symmetric anti-negativity:** UPWARD: promoted Cell I v3 from MM to CGP despite same-numerics concern, carved PARTIAL_MM for OLSHAUSEN despite cell-level CONFOUND_FAIL. DOWNWARD: withheld DEFINITIVE on Cell I v3 (retrofit-risk) and Cell 2 v4 (n=3 seeds + knob-tune not novel primitive); declined to promote DW/FOLDIAK arms in Cell 3 (cleanup-confound disqualifies). Same rigor both directions.
- **Skunkworks vs Director calibration:** Director's framings on Cell I v3 (principle-proof) and Cell 2 v4 (first Stage 2 win) are directionally correct; I'm seconding at PARTIAL not DEFINITIVE in both cases. These are calibration-tightening, not overrides.

End ruling.
