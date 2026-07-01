# Pre-registration: cross_modal_binding_4_5_modality_v1

**Author:** exp_dev 2026-07-01 (Opus 4.7 1M)
**Composes on:** cross_modal_binding_3rd_modality_v1 (3-mod single-seed HP landed 2026-07-01)
**Anchor(s):** cross_modal_binding_4_5_modality_v1_seed_{7,13,19}

## Question
Does the HRR cross-modal binding mechanism scale to 4 and 5 modalities
CROSS-SEED (cv < 10%), or does the N-way conjunctive bind lose lift vs
baseline as N-mod capacity cost compounds?

## Hypothesis
Cross-modal binding CG at 3 modalities single-seed extends to 4- and
5-modality cross-seed regime: substrate supports HRR-bindN with cross-modal
recall > 0.70 and cross-seed cv < 10% at pos-control corner
(K=10, N=8192, n_mod=5). Baseline (NO_BIND) stays at chance (~1/2048)
across sweep; mechanism arm shows band-diverse phase diagram (saturates
at low-K/high-N, cliffs at high-K/low-N, mid-band in between).

## Prior-work check (substrate-KB concept-query 2026-07-01)
Query: "cross-modal binding modality visual auditory haptic semantic scaling"
Top hits (cosine 0.32-0.38):
- Cross-modal binding note (research_substrate_llm_aggressive_eval_v1_2026-05-31)
- 2.7 Cross-Modal Binding (research_drill_fact_representation_rethink_5x_2026-06-08)
- Multimodal primitives drill (research_drill_multimodal_substrate_primitives_2x_2026-06-04)
  - Prior: SNR = sqrt(N/K) modality-agnostic; K<=196 vision, K<=100 motor safe at N=4096
- C9 cross-modal VSA binding (research_drill_embodied_revival_3x_2026-06-10)
- Prior prereg: 2026-06-05_substrate_multimodal_binding_text_kg_v1 (HP-9)

**Novelty assessment:** GENUINELY NOVEL, not rediscovery. Prior atoms cover
2-modality binding + modality-agnostic capacity SNR + text/KG 2-mod. NONE
measure 4/5-modality scaling cross-seed cv. This cell is the load-bearing
scale-extension along the modality-count axis.

## Sweep
- **K:** {10, 100, 1000} (3 pts)  -- HYPOTHESIZED spans sat/mid/cliff
- **N:** {2048, 4096, 8192} (3 pts) -- HYPOTHESIZED per SNR=sqrt(N/K)
- **n_mod:** {3, 4, 5} (3 pts) -- HYPOTHESIZED covers scaling axis
- **mechanism:** HRR_bindN (single mechanism; left-associative fold)
- **discriminator arms:** BIND_NMOD / NO_BIND
- **grid:** 27 phase points x 2 arms x 20 queries = 1080 records per seed
- **seeds:** 7, 13, 19 (chunked: 1 seed per cell file)

## Smoke corners (5)
- (K=10,   N=8192, n_mod=3)   pos-ctrl-3
- (K=10,   N=8192, n_mod=4)   pos-ctrl-4
- (K=10,   N=8192, n_mod=5)   pos-ctrl-5 (headline)
- (K=1000, N=2048, n_mod=5)   cliff regime 5-mod
- (K=100,  N=4096, n_mod=4)   mid 4-mod

## Pre-reg bands (envelope-fail)

**HARD_PASS (chain-grade scaling at 4 and 5 modalities):**
- pos-control (K=10, N=8192, n_mod=5): cross-seed recall >= 0.70 AND cv <= 0.10
- discriminating fraction (BIND - NO_BIND >= 0.30): >= 50% of 27 pts

**HARD_FAIL:**
- all bind recalls >= 0.99 (by-construction saturation)
- avg|BIND - NO_BIND| < 0.05 (mechanism not load-bearing at N-mod)

**MIDDLE_BAND:**
- disc fraction in [0.20, 0.50), OR
- pos-control short of HARD_PASS thresholds

## Cardinality
- FULL: expected_n = 27 pts x 2 arms x 20 queries = 1080 per seed
- SMOKE: expected_n = 5 corners x 2 arms x 4 queries = 40 per seed
- `cardinality_ok: bool` set from observed_n vs expected_n (META_RULE_H)

## CRLB / capacity-feasibility (META_RULE rule 9)
- **Formula:** SNR_effective ~ 1 / sqrt(K * cross_term_count)
  For bindN of independent bipolar codes, cross-terms grow as O(2^{n_mod-1})
- **Ceiling at pos-ctrl (K=10, N=8192, n_mod=5):**
  SNR ~ 1/sqrt(10*15) ~ 0.082; top1 recall > 0.70 achievable
  since clean signal >> other-item noise at N=8192 codebook
- **discriminator_reachability: True** (verified in selftest, BIND=1.000)

## Positive-control reproducer (Gate D)
- 3-mod pos-ctrl arm reproduces 3rd-modality cell's HARD_PASS recall
  at same K=10, N=8192 (tolerance 0.10)
- If 3-mod arm < 0.60 at pos-ctrl: HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH

## Discriminating-band coverage (Gate B)
- Selftest MEASURED@2026-07-01:
  - K=10  N=8192 n_mod=3,4,5 -> BIND=1.000, saturated corner
  - K=100 N=2048 n_mod=4,5   -> BIND=0.750, mid-band
  - K=100 N=4096 n_mod=4     -> BIND=1.000, saturated
  - K=1000 N=2048/4096/8192  -> BIND=0.000, cliff/floor
- Predicted points in discriminating band [0.30, 0.70]: >= 5 of 27
- discriminating_fraction >= 0.19 (borderline); relies on cross-seed averaging
  spreading points into band

## Baseline-in-band (Gate META_RULE_AG)
- NO_BIND arm: expected 0.000 across all 27 pts (chance = 1/2048 ~ 0.0005)
- baseline_in_band: FALSE for the NO_BIND arm by design; discriminator is
  the LIFT, not baseline-absolute-in-band; declare exemption:
  `arms_differ_exempted: []` -- NO_BIND is chance-level baseline; mechanism
  arm BIND_NMOD tested vs it via lift, not vs band

## Selftest values (MEASURED@2026-07-01)
- 3-mod BIND(K=10,N=8192)=1.000
- 5-mod BIND(K=10,N=8192)=1.000
- 5-mod NO_BIND=0.000, lift=1.000
- codebook_indep=0.025 (< 0.10)
- backend=torch.cpu, elapsed=1.7s

## Meta-rule field summary
- cardinality_ok: bool from observed vs expected
- arms_differ_verified: implicit (BIND_NMOD sums bindN; NO_BIND is randn -- structurally different)
- final_metrics_atomicity: tmp_replace (see main tmp -> os.replace pattern)
- except SystemExit: raise BEFORE except Exception (verified in cell)
- crlb_floor_computed: SNR ~ 0.082 at pos-ctrl 5-mod
- crlb_formula_reference: "SNR ~ 1/sqrt(K * 2^{n_mod-1})"
- discriminator_reachability: True (selftest BIND=1.000)
- baseline_in_band: EXEMPT (NO_BIND is chance-level by design; discriminator is lift)
- calibration_check: default_ok_for_this_regime (bipolar codes, K << V=2048)
- HP_SCOPE: {BIND_NMOD: [pos_ctrl_recall, pos_ctrl_cv, disc_frac], NO_BIND: []}
- cell_chunked: true (1 seed per file: seed_7, seed_13, seed_19)
- start_marker_written: true
- crash_diagnostic_present: true (except Exception -> _write_import_crash_sentinel)
- heartbeat_present: false (cells are short; 27 pts x ~1s each ~30s)
- defensive_error_checking: passed_all_4_patterns

## Timeout
- FULL per-seed: ~30-60s CPU (27 pts x ~1s selftest scaling)
- FULL timeout with 1.5x safety + N=8192 GPU multiplier: 3600s per cell
