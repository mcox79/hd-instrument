# Pre-reg: Mammal-allometry cross-channel grounding (Track-B build #2, A-INDEPENDENT) -- grounding_mammal_allometry_xchannel_fpe_v1

Date: 2026-07-13
Author: exp_dev
Plan: notes/research_grounding_foundation_build_plan_2026-07-13.md (Phase 2, A-independent fair test)
Precursor (confounded): preregs/2026-07-13_grounding_periodic_xchannel_fpe_v1.md
Cell: experiments/exp_grounding_mammal_allometry_xchannel_fpe_v1.py

## Why this cell (the value-add test the periodic result demanded)
The periodic-table cell landed MIDDLE_BAND / GROUNDING_REDUNDANT_WITH_RELATIONAL
(A+B_FPE=0.567 vs A_alone=0.536, d=+0.031 < 0.05)
MEASURED@d:/AI/hd-instrument/data/exp_grounding_periodic_xchannel_fpe_v1/metrics.json:agg.
That could NOT answer "does grounding ADD" because the domain was CONFOUNDED: its
group/period/block graph is reverse-engineered FROM the periodic law -- group == valence-
electron count, which DIRECTLY determines electronegativity / ionization energy / radius.
So channel A already secretly CONTAINED channel B. This cell removes that confound by
choosing a domain where the relation graph is DEMONSTRABLY NOT derived from the numbers.

## A-INDEPENDENCE justification (the whole point)
Channel A = phylogenetic taxonomy: species -> (HAS_ORDER, HAS_FAMILY, HAS_CLADE).
ORDER / FAMILY / CLADE are classifications established by comparative anatomy + molecular
systematics -- established from ANCESTRY, not from any measured size/time quantity. NONE is a
function of adult body mass, body length, longevity, gestation, or litter size:
- a 0.02 kg house mouse and a 55 kg capybara are BOTH order Rodentia (mass ratio 2750x);
- a 0.008 kg shrew and a 5000 kg African elephant are BOTH placental mammals (clade);
- a 190 kg lion and a 4 kg domestic cat are BOTH family Felidae.
Mass varies up to 10^6 WITHIN a single graph cell. Contrast periodic table: group IS the
property structure. THEORETICAL: A is independent of B by the CONSTRUCTION OF THE DOMAIN, not
by assertion -- taxonomy predates and is defined orthogonally to trait measurement.
(NB A is NOT useless: body-size traits carry strong PHYLOGENETIC signal -- "phylogenetic
conservatism" -- so A_ALONE is a strong, in-band baseline. The test asks whether the measured
numeric channel B adds signal OVER that independent-but-predictive taxonomy baseline.)

## Channels
- Channel A (relational, native): species -> (order, family, clade) ingested into a REAL
  hdlab.kg_traversal.KGStore; species relational signature = sum_r R[r]*E[symbol(e,r)] from the
  store's own bipolar E/R codebooks (bind = elementwise multiply, bundle = sum).
- Channel B (measured, exterior): body_mass(kg), head-body length(cm), max longevity(yr),
  gestation(days), litter size. CITED@AnAge/PanTHERIA/Walker's-Mammals reference class
  (approximate reference values; a rank/similarity kNN readout on min-max-normalized values is
  robust to modest per-value error -- the science claim is the A-vs-A+B DELTA, not absolute
  accuracy). 64 species across 15 orders + 5 clades; ZERO NaN (all 5 traits present per species).

## Encoding (VSA wiring; REUSED verbatim from the proven periodic cell)
- FPE (FHRR): enc_k(v)=exp(1j*freqs_k*v), Gaussian base freqs. THEORETICAL@ cos-sim =
  mean_d cos(freqs*(v1-v2)) = exp(-s^2 dv^2/2). freq_std s=2.15 so kernel decays 1.0 -> ~0.1
  across normalized [0,1]. (proven: periodic decode-degradation did not bite; decay Spearman 0.999.)
- LEVEL (fallback, arXiv:2412.00488): spherical interp normalize(cos(t)*v_lo+sin(t)*v_hi), t=v*pi/2.
- CLEANUP: CSim-style resonator (iterative interference subtraction) decoder, first-class arm.
- calibration_check: adaptive_with_justification -- LOG10 transform on the four power-law-
  distributed size/time vars (mass, length, lifespan, gestation) BEFORE min-max, because
  allometric scaling is LINEAR IN LOG SPACE (Kleiber's law; life-history theory). Litter size
  (range 1-8) stays linear. Skill (R^2) is scored in the SAME log/linear space used to encode.

## Oracle + readout
Allometric coupling. Leave-one-out kNN in the consolidated geometry: predict a held-out
species' (normalized) property from a similarity-weighted average of all OTHER species' values
(no self, no leakage; the held-out target property is EXCLUDED from Channel B's bundle).
Skill = R^2 vs the mean baseline, averaged over the 5 target properties.

## Arms (8)
- MEAN: global-mean predictor (skill == 0 by construction).
- DEGREE: query-agnostic graph-degree-weighted predictor (relational popularity floor).
- RANDOM: random-hypervector similarity (must-fail floor).
- A_ALONE: taxonomy similarity only (Channel A; lam=0). THE ablation baseline.
- B_ALONE: FPE numeric similarity only (lam=inf) -- does B ground AT ALL, independent of A.
- A_PLUS_B_FPE: taxonomy fused with FPE attribute similarity (lam=1). HEADLINE.
- A_PLUS_B_LEVEL: taxonomy fused with level-code attribute similarity.
- RAW_FEATURE_KNN: kNN on RAW normalized other-features (grounding-is-winnable reference).

## Diagnostics (fairness + weak-point localization, first-class per MEMORY 2026-07-10)
- PER-PROPERTY skill breakdown for A_ALONE / B_ALONE / A_PLUS_B_FPE over the 5 targets:
  localizes WHERE B adds vs where taxonomy already suffices (even if the 5-property MEAN washes).
- LAM-FUSION SWEEP lam in {0,0.25,0.5,1,2,4}: does B add over A under ANY reasonable weight
  (upper-bound on the fusion's value), not just the headline lam=1.0. Reporting-only; headline
  verdict stays at lam=1.0 for periodic-comparability.
- boundary/interior strata: boundary = bottom-tertile graph degree (taxonomically isolated
  species; A has few same-order/family/clade neighbors) -> tests whether B helps MOST where the
  graph is sparse (degree invariance / weak-point localization).

## Compute architecture
Class (b) sequential-CPU with justification: 64-species domain; all ops are 64x64 similarity
matrices + a 257-point decode grid; total wall << 30s at n_dim=8192 x 5 seeds (periodic FULL
same shape = 21.5s MEASURED). No GPU benefit (matmuls tiny). Routes to remote_cpu_queue.
Storage strategy: no_composition (single-hop kNN readout, not chained retrieval).

## Multi-seed + stratification
- FULL: n_dim=8192, seeds=[7,13,19,23,29]. Self-test/smoke: n_dim=2048, seeds=[7,13].
- Randomness (seed): FPE base freqs, level endpoints, roles, KGStore E/R codes, RANDOM arm.
  The mammal DATA + the leave-one-out split are DETERMINISTIC (no random split -> no
  PYTHONHASHSEED split-identity hazard; no list(set()) dedupe on any split-defining set).

## Pre-registered bands (BOTH pre-reg'd before running)
HARD_PASS = GROUNDING_ADDS (ALL required; strictly above floor per META_RULE_L):
1. A_PLUS_B_FPE skill - A_ALONE skill >= 0.05 (Channel B load-bearing OVER independent A)
2. A_PLUS_B_FPE skill - RANDOM skill >= 0.10 AND A_PLUS_B_FPE > MEAN (== 0)
3. B_ALONE skill - MEAN >= 0.10 (numeric channel grounds on its own)
4. fpe_decay_spearman >= 0.90 (encoding does real metric work)
5. boundary_fpe >= interior_fpe - 0.15 AND boundary_fpe > 0 (degree/boundary invariant)
6. cleanup decode median rel-err <= 0.20 (numeric info recoverable after bundle size 5)
AND machinery valid (synth ablation gap >= 0.30).

FAIL / non-PASS classes (classified separately; do NOT conflate):
- ENCODING_BROKEN (HARD_FAIL): fpe_decay_spearman < 0.50 (wiring broken, not a grounding result).
- ABLATION_MACHINERY_INSENSITIVE (HARD_FAIL): synth A+B-A gap < 0.30 (test can't detect a
  load-bearing exogenous channel even when injected).
- GROUNDING_NEGATIVE_B_CARRIES_NOTHING (HARD_FAIL): B_ALONE - MEAN < 0.10 (numeric channel
  carries no exogenous info even alone).
- ORACLE_LEAK_VIA_SMOOTHNESS (HARD_FAIL): interior_fpe > 0 but boundary_fpe <= 0.
- GROUNDING_REDUNDANT_WITH_RELATIONAL (MIDDLE_BAND): machinery + encoding valid, B grounds
  alone, but A+B does NOT beat A by >= 0.05 -> B is redundant with the (independent) taxonomy on
  this domain. A pre-registered, scientifically-informative outcome distinct from periodic's
  redundancy: here redundancy is via genuine phylogenetic conservatism, NOT construction-confound.
- DECODE (independent of grounding verdict): raw decode median rel-err > 0.50 at bundle size 5
  => DECODE_DEGRADATION; if cleanup rel-err <= 0.20 => cleanup recovers (report, not a grounding failure).

## HP_SCOPE
- A_PLUS_B_FPE: [b_beats_a, b_beats_floor, encoding_ok, degree_invariant, cleanup_fixes].
- A_ALONE: baseline only (no HP gates; must be above RANDOM floor per F.4).
- B_ALONE: grounding-alone gate (B_ALONE - MEAN >= 0.10) only.
- MEAN/DEGREE/RANDOM: floor arms (no HP gates). RAW_FEATURE_KNN: winnability reference.

## SCHEMA-VET gate fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds * sum_t (n species with property t known)
  = n_seeds * 5 * 64 (zero NaN). MEASURED smoke: got 640 == expected 640 (2 seeds).
- effective_vs_nominal: no swept confounded param (lam ablation 0 vs 1; both experienced fully;
  the lam-sweep diagnostic experiences each lam fully). sweep_alignment_verdict: ALIGNED.
- discriminating_fraction: N/A (ablation cell, not a bracket sweep); A_ALONE pre-verified in band.
- composition_edges: relational-sig (bind/bundle) -> cosine; FPE (bind role, bundle) -> cosine;
  fusion = additive at similarity/readout level. verdict: SHAPE_MATCH (all cosine-space).
- positive_control_arms: (a) SYNTH exogenous channel (A+B must beat A by >= 0.30 -> machinery
  fires); (b) RAW_FEATURE_KNN (grounding-is-winnable reference). MEASURED smoke: synth gap 1.285.
- functional_requirements: (1) encode a measured scalar as a composable hypervector -> FPE/level;
  (2) fuse with native relational algebra -> KGStore E/R bind/bundle + additive sim fusion;
  (3) infer a held-out measured value -> LOO kNN oracle; (4) recover the scalar after bundling
  -> resonator cleanup decoder.
- real_code_path_exercised: [KGStore, ingest_triples] (self-test constructs + ingests REAL store).
- substrate_signature_checked: [KGStore] with BASE/portable kwargs {n_ent,n_rel,n_dim,generator};
  NO version-specific init_entities (F.3 drift discipline).
- guard_baseline_validated: [ablation_needs_nonfloor_A] (A_ALONE validated above RANDOM floor).
- baseline_in_band: A_ALONE checked 0.05 < skill < 0.95 at self-test (MEASURED smoke 0.595, in band).
- crlb_n/a: "regression-skill (R^2) cell; no argmax capacity / Cramer-Rao noise floor applies."
- arms_differ_verified: true (per-arm concatenated prediction hashes; META_RULE_AF).
- final_metrics_atomicity: tmp_replace (META_RULE_AH).
- cell_chunked: false (single-file multi-seed; 5 seeds x seconds each, runner-death risk minimal).
- start_marker_written: true. crash_diagnostic_present: true. heartbeat_present: false
  (per-seed [progress] print_flush lines; total wall << 60s so a jsonl heartbeat is unnecessary).
- defensive_error_checking: "print_flush per-seed progress + start-marker + crash-diagnostic;
  heartbeat exempt (sub-minute wall)".
- progress_logging: print_flush_true.

## Validity-preflight (VALIDITY_PREFLIGHT_MODE=enforce)
F.1 real_code_path, F.2/F.3 substrate_signature, F.4 guard_baseline_valid (ENFORCE) + the
original 4 (positive_control, metric_moves, full_gates_exercised, negative_control_margin) all
DECLARED and exercised in the self-test. Ship gate = machinery fires (synth gap >= 0.30) AND B
grounds alone (B_ALONE - MEAN >= 0.10) AND A_ALONE in band -- NOT the real "B beats A" (that IS
the FULL science question this cell exists to answer; gating ship on it would refuse to run it).
MEASURED self-test @n_dim=2048: PASS all gates.

## Smoke result (MEASURED, pre-ship; n_dim=2048, seeds [7,13])
MEASURED@d:/AI/hd-instrument/data/exp_grounding_mammal_allometry_xchannel_fpe_v1/metrics.json:
verdict=MIDDLE_BAND, failure_mode=GROUNDING_REDUNDANT_WITH_RELATIONAL.
A+B_FPE=0.593, A_alone=0.595 (d=-0.002), B_alone=0.447, RANDOM=-0.493, MEAN=0.
machinery synth gap=1.285; decay=0.999; decode raw=0.008 clean=0.002. cardinality 640==640.
PER-PROPERTY (A_ALONE -> A+B_FPE): mass 0.614->0.596, length 0.635->0.605, lifespan 0.579->0.642,
gestation 0.802->0.723, litter 0.347->0.401. B adds for {lifespan, litter}; A+B_best_lam=0.617.
=> HEADLINE hint: taxonomy is a strong INDEPENDENT baseline (phylogenetic signal); B adds real
signal only for the residual-variation traits (lifespan, litter), not the pure-size traits.
FULL (n_dim=8192, 5 seeds) confirms/refines at scale; landed verdict is authoritative.

## Scope / honest deflation
Proves/refutes the GROUNDING-ADDS claim in a small clean A-INDEPENDENT domain with a lawful
oracle; transfer to the messy 222k-triple KB is a separate later step. This is passive-exterior
(ingested measurements, layer-2), NOT active-intervention (layer-3) grounding. The A-independence
is the domain's structural property (taxonomy != trait), verified by construction, not asserted.
P_deflated(HARD_PASS GROUNDING_ADDS on 5-property mean) = 0.25 (smoke shows redundancy on the
mean; B adds only on 2/5 residual-variation properties). Most likely landed = MIDDLE_BAND /
GROUNDING_REDUNDANT with per-property localization (lifespan+litter add), which is itself the
informative, honest, unconfounded answer the periodic cell could not give.
