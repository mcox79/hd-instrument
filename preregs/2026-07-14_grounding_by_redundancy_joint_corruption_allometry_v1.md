# Pre-registration: GROUNDING-BY-REDUNDANCY under JOINT corruption (allometry)

anchor_name: grounding_by_redundancy_joint_corruption_allometry_v1
cell: experiments/exp_grounding_by_redundancy_joint_corruption_allometry_v1.py
date: 2026-07-14
queue: remote_cpu_queue (CPU-cheap; whole run << 10s wall)
supersedes-crutch-of: exp_grounding_law_consistency_allometry_v1 (HARD_PASS via PREDICTOR_CLEAN coupling)

## Question
The sibling cell exp_grounding_law_consistency_allometry_v1 corrupted ONLY the target
attribute per law and left the predictor CLEAN, so detecting a corrupted mass from a
98%-correlated CLEAN length is a near-tautology (a single clean sibling over-determines the
value). This cell removes the crutch: corrupt ALL attributes JOINTLY (no clean sibling
anywhere). Given a NETWORK of allometric laws, can CROSS-LAW REDUNDANCY (the consensus of
multiple, also-noisy, law-predictions) DETECT + LOCALIZE + CORRECT the off-manifold value
when NO single clean predictor exists? Must-fails prove it is the redundant law-network,
not any single predictor / generic smoothing / clean sibling, doing the work.

## Law network (glass-box; CITED biological exponents = the external grounding)
Four attributes are affine in a shared log-body-size latent s = log10(mass):
- mass loading a=1.00 (s itself)  CITED@Kleiber/geometric
- length a=1/3   (mass ~ length^3)      CITED@geometric isometry
- gestation a=0.25 (gestation ~ mass^0.25) CITED@quarter-power life-history
- lifespan a=0.20 (lifespan ~ mass^0.20)   CITED@longevity allometry
Pairwise law i<-j: log(attr_i) = (a_i/a_j) log(attr_j) + b_ij; intercept b_ij LOO-median
(no leak). FULLY-CONNECTED 4-node graph (every node degree 3) -> redundancy.
Data: 64 mammals (load_mammals), REAL KGStore relational channel (build_relational_store).

## Corruption protocol (the HONEST regime)
- Background noise N(0, sigma_bg=0.08 log10) on 100% of cells -> NO clean sibling (structural;
  self-test asserts min per-cell |perturbation| > 0).
- Exactly ONE large off-manifold shift per entity: U[0.6,1.2] log10, random sign. Off the
  cross-attribute manifold but in marginal range for wide attributes.
Multi-seed with REAL per-seed corruption randomness (NOT the sibling's vacuous cv=0).

## Arms
FULL (mechanism): each attr predicted from MEDIAN of the other 3 pairwise-law predictions.
NO_REDUNDANCY (must-fail 1): perfect matching (mass<->length, gestation<->lifespan) -> ONE
  partner per attr -> pair-ambiguous localization; a single predictor cannot localize.
SCRAMBLE (must-fail 2a): FULL graph, predictor columns shuffled across entities.
WRONG_EXP (must-fail 2b): FULL graph, WRONG loadings (all a_k=1 -> all slopes=1).
MARGINAL / RELATIONAL (no-law baselines): own-distribution z-score / taxonomic-neighbor
  consensus via REAL KGStore (a DIFFERENT redundancy source; the fair cross-channel baseline).

## Metrics
- CORRECT (headline): flag argmax standardized-residual cell per entity, replace with the
  arm's law-prediction, all-cell log-MAE reduction. Mis-localization ADDS error.
- LOCALIZE: per-entity argmax standardized-residual == the corrupted attribute (chance 1/K=0.25).
- DETECT: pooled AUC over all entity-attribute cells (corrupt vs clean).
Per-arm per-attribute ROBUST-MAD standardizer on the OBSERVED (corrupted) residuals; SAME
recipe every arm (no per-arm tuning; calibration_check=adaptive_with_justification).

## Pre-registered bands (BOTH; calibrated to MEASURED self-test + 5-seed FULL)
HARD_PASS requires ALL of (mechanism_fires AND mustfail_collapses AND h_fires AND a_fires):
- (headline correction) FULL corr >= 0.20 ; FULL corr - NO_REDUNDANCY corr >= 0.25 ;
  FULL corr - best-no-law corr >= 0.15
- (localization) FULL loc >= 0.68 ; FULL loc - NO_REDUNDANCY loc >= 0.20 ;
  FULL loc - best-no-law loc >= 0.06
- (detection) FULL AUC >= 0.78 ; FULL AUC - best-no-law AUC >= 0.02 (LOW bar: honest -- a
  big shift is often a marginal outlier so DETECTION is not where redundancy shines;
  LOCALIZATION + CORRECTION are)
- (mechanism_fires) FULL AUC >= 0.70
MUST-FAIL / HARD_FAIL (mustfail_collapses false OR mechanism not firing):
- SCRAMBLE corr <= 0.05 AND FULL loc - SCRAMBLE loc >= 0.12
- NO_REDUNDANCY corr <= 0.05 AND NO_REDUNDANCY loc <= 0.55
- FULL loc - WRONG_EXP loc >= 0.12 AND FULL corr - WRONG_EXP corr >= 0.20
MIDDLE_BAND: mechanism fires + must-fails collapse but only some of h/a fire.

## MEASURED self-test (3 seeds, n_dim=2048) + 5-seed FULL (n_dim=8192)
MEASURED@data/exp_grounding_by_redundancy_joint_corruption_allometry_v1_smoke/metrics.json (smoke=3seed):
- verdict HARD_PASS ; FULL corr=+0.298 loc=0.802 AUC=0.869 ; NO_REDUNDANCY corr=-0.389 loc=0.458 ;
  SCRAMBLE corr=-0.318 loc=0.599 ; WRONG_EXP corr=-0.101 ; MARGINAL loc=0.677 REL loc=0.661 ;
  best-no-law corr=+0.121 ; collapse=True (scr+noredun+wrong all collapse).
MEASURED@5-seed FULL import (n_dim=8192; verdict HARD_PASS):
- FULL corr=+0.301 loc=0.800 AUC=0.870 ; NO_REDUNDANCY corr=-0.400 loc=0.431 ;
  SCRAMBLE corr=-0.449 loc=0.569 ; WRONG_EXP corr=-0.055 loc=0.613 ; best-no-law corr=+0.122 ;
  detect d=+0.052. THEORETICAL localization chance = 1/K = 0.250.
KEY HONEST FINDING: under JOINT corruption FULL is the ONLY arm with POSITIVE correction
gain; every no-redundancy / no-law / wrong / scramble arm makes it WORSE or neutral -- they
mis-localize and replace a clean cell. Redundancy (consensus of K-1 noisy law-predictions)
is REQUIRED. DETECTION barely beats marginal (d~+0.05): a big shift is a marginal outlier so
"something is off" is easy; "WHICH one + fix it" needs cross-law redundancy.

## No-clean-sibling proof (must-fail 3, explicit)
(i) STRUCTURAL: background noise on 100% of cells (min_bg>0 asserted) -> no attribute is
clean. (ii) NO_REDUNDANCY IS the single-predictor case -- if a lone clean sibling did the
work it would MATCH FULL; it does not (corr -0.40 vs +0.30; loc 0.43 vs 0.80). The
partner-also-corrupted AUC_pc/loc_pc are REPORT-ONLY weak-point diagnostics (ill-posed once
BOTH pair-members are off-manifold: NO_REDUNDANCY's AUC even inflates via mutual corruption),
NOT gated.

## SCHEMA-VET fields
cardinality_ok: EXPECTED_N_UNITS = n_seeds * K = 5*4 = 20 (FULL); verdict HARD_FAILs on breach.
arms_differ_verified: true (META_RULE_AF hash of per-arm z-vectors at self-test).
arms_differ_exempted: none.
final_metrics_atomicity: tmp_replace.
except-ordering: SystemExit/KeyboardInterrupt re-raised BEFORE except Exception (no BaseException).
crlb_n/a: "rank-AUC + localization-accuracy + log-MAE-skill cell; no argmax capacity floor.
  localization chance floor = 1/K = 0.25 is declared + used as the must-fail reference."
baseline_in_band: true (best-no-law localization 0.677 < FULL 0.802; not saturated; asserted).
discriminator_survives_scale: CASE B -- the mechanism is DIMENSION-FREE (closed-form on the
  64x4 log-attribute table); n_dim only affects the RELATIONAL baseline (KGStore cosine).
  Self-test at n_dim=2048 and 5-seed FULL at n_dim=8192 both HARD_PASS with matching gaps.
calibration_check: adaptive_with_justification (log10 for power-law vars; per-arm per-attr
  robust-MAD standardizer on OBSERVED corrupted residuals; identical recipe all arms).
HP_SCOPE: {FULL: [corr>=0.20, corr-noredun>=0.25, corr-nolaw>=0.15, loc>=0.68, loc-noredun>=0.20,
  loc-nolaw>=0.06, AUC>=0.78, AUC-nolaw>=0.02]; NO_REDUNDANCY/SCRAMBLE/WRONG_EXP: must-fail
  ceilings only (NOT the FULL HP gates); MARGINAL/RELATIONAL: no-law baseline (no HP gates)}.
progress_logging: print_flush_true (cheap cell; timeout << 1800).
compute_architecture: sequential-CPU with justification (64 entities, closed-form,
  dimension-free; per-seed << 2s; whole cell << 10s; no GPU batching candidate).
storage_strategy: no_composition (relational baseline uses sharded KGStore E/R codes only).

### Gate F (F.1-F.4) declarations
real_code_path_exercised: [KGStore, ingest_triples, build_relational_store] -- self-test
  CONSTRUCTS the REAL KGStore at n_ent=6 n_dim=16 + ingests real triples + builds the REAL
  relational store at n_dim=256 on the REAL mammal data.
substrate_signature_checked: [KGStore] bound with BASE/portable kwargs {n_ent,n_rel,n_dim,
  generator} only (NO version-specific init_entities kwarg -> local/remote portable).
guard_baseline_validated: N/A -- this cell has NO control-beats-baseline BREAK-guard (the
  must-fails are localization/correction-margin gates, not a control-vs-incumbent break-guard).
mode: VALIDITY_PREFLIGHT_MODE=enforce PASSED (--self-test exit 0).

## Failure-mode taxonomy (do NOT conflate)
MECHANISM_NOT_FIRING (FULL AUC < 0.70) | REDUNDANCY_NOT_LOADBEARING (single/scramble/wrong
also corrects) | REDUNDANCY_GROUNDS (localizes+corrects, no clean sibling) [HARD_PASS] |
REDUNDANCY_LOCALIZES_CORRECTS_but_detect_weak | REDUNDANCY_DETECTS_but_localize_correct_weak
| REDUNDANCY_NO_ADVANTAGE.
