# Pre-registration: CONSISTENCY-AGAINST-INVARIANTS grounding (LEVER A)

- anchor_name: grounding_law_consistency_allometry_v1
- cell: experiments/exp_grounding_law_consistency_allometry_v1.py
- date: 2026-07-14
- queue: remote_cpu_queue (CPU-cheap; closed-form + a [64,64] relational Gram)
- timeout_s: 600 (measured smoke 0.55s/3seeds@n_dim=2048; FULL 5seeds@8192 est <10s; 600 = safe ceiling)
- design source: notes/research_grounding_topicB_synthesis_and_next_levers_2026-07-14.md (LEVER A)
- prior-work check (substrate KB, cosine>0.30): NONE on-topic. Top hit "DISTILLATION COST
  SCALING LAW" (0.323) is keyword-coincidence on "scaling law"; rest generic
  error-correction-code / attribution. This cell is NOVEL (first consistency-against-
  invariants grounding cell in the arc).

## Hypothesis
Grounding attribute values by requiring LAW-CONSISTENCY (a closed-form allometric scaling
law) yields two capabilities over a no-law baseline:
  (a) ERROR-CORRECTION: law-residual DETECTS + CORRECTS corrupted values.
  (b) SPARSE-TAIL IMPUTATION: law imputes MISSING attributes for the cold tail (few
      taxonomic edges) where relational inference collapses.
A WRONG / SCRAMBLED law must NOT confer these (confirms the REAL law carries the signal).
Honest caveat: a law is EXTERNAL info baked in (encodes real-world structure); this is
bake-in of a LAW, not internal-bootstrapping -- but cheaper + more general (one law
grounds many values).

## Laws (closed-form, glass-box, external biological constants)
log10(y) = slope * log10(x) + b; slope = KNOWN (baked); intercept b = per-entity LOO median (units nuisance, not the law).
- L1 mass_from_length   slope 3.00  geometric isometry (mass~volume~length^3). CITED@textbook.
                        MEASURED in dataset: OLS slope +2.80, fit R2=0.986, resid_std=0.172
                        (a VERY tight invariant) -> HEADLINE law.
                        MEASURED@d:/AI/hd-instrument (fit-check 2026-07-14, this session).
- L2 gestation_from_mass slope 0.25 quarter-power life-history. CITED@life-history-theory.
                        MEASURED OLS +0.207 R2=0.491 (looser).
- L3 lifespan_from_mass  slope 0.20 longevity allometry. CITED. MEASURED OLS +0.161 R2=0.478.
Headline verdict on L1; L2/L3 reported as a GENERALITY stratum (tight law grounds strongly,
loose laws weakly -- honest).

## Arms
- Detection/correction: LAW, MARGINAL (|robust z| within the attribute's own dist),
  RELATIONAL (deviation from taxonomic-neighbor median via a REAL KGStore), WRONG_EXP
  (slope=1.0), SCRAMBLE (true slope, predictor shuffled across entities).
- Imputation: LAW, RELATIONAL (kNN in the real relational geometry), MEAN, RANDOM
  (relational kNN with random codes = floor), WRONG_EXP, SCRAMBLE.
- Fair no-law comparator = BEST of {MARGINAL, RELATIONAL} (beat the strongest baseline).

## Corruption regime (calibration_check: adaptive_with_justification)
- corruption_rate = 0.25 (25% of target values corrupted; 75% clean -> robust intercept).
- shift = sign * U[0.8, 1.5] in log10 (6x-32x multiplicative). Designed to keep the
  corrupted value IN the marginal range but OFF the cross-attribute manifold, so MARGINAL
  detection is genuinely weak (a mouse-mass corrupted to rat-mass is normal marginally but
  wildly off the mass-length line -- only the LAW catches it). Verified: MARGINAL AUC 0.599,
  RELATIONAL AUC 0.681 (NOT saturated) vs LAW 0.999.
- Detection uses oracle-K flagging (K = n_corrupt, same for all arms) -> NO per-arm
  detection-threshold tuning (p-hack-free). Correction scored as all-cell log-MAE reduction
  (penalizes wrongly correcting clean cells).
- SCOPE: predictor attribute assumed CLEAN (corrupt target only). Joint-corruption is a
  documented follow-up.

## Pre-registered bands (headline law L1; strictly-above-floor per META_RULE_L)
HARD_PASS (all must hold):
  (a) LAW detection AUC >= 0.85 AND (LAW - best-no-law) >= 0.10
      LAW correction gain >= 0.30 AND (LAW - best-no-law) >= 0.10
  (b) LAW imputation R2 (cold tail) >= 0.50 AND (LAW - RELATIONAL) >= 0.15
      AND degree-invariance: LAW R2 cold >= LAW R2 interior - 0.15
  must-fail collapse (two-pronged):
      SCRAMBLE (pure no-law): scr_auc <= best-no-law+0.05 AND scr_corr <= 0.10 AND scr_imp <= 0.15
      WRONG_EXP (right exponent value load-bearing): (LAW-WRONG) margins >= {AUC 0.15,
        corr 0.20, imp 0.20} AND wrong_auc <= best-no-law+0.05
  encoding: L1 true-data fit R2 >= 0.80 (info-ceiling; imputation cannot exceed this).
MIDDLE_BAND: encoding_ok AND must-fail-collapses AND exactly one of (a)/(b) fires.
HARD_FAIL: encoding broken (data off manifold) OR must-fail does NOT collapse (wrong/scramble
  also helps = generic regularizer not the law) OR neither (a) nor (b) fires.

Rationale for "best-no-law+margin" rather than chance-0.5 must-fail ceiling: additive-in-log
corruption inflates ANY y-residual, so wrong/scramble detection AUC floors near the no-law
baseline (~0.68), not at 0.5. SCRAMBLE breaks entity-pairing (pure no-law); WRONG_EXP retains
partial signal because length<->mass correlate at any positive slope, so the discriminating
claim is "the RIGHT exponent VALUE beats the wrong one by a large margin".

### Discriminator preview (self-test, 3 seeds, real data, n_dim=2048; MEASURED this session)
LAW_AUC=0.999 best-no-law=0.681 (d=+0.318) | LAW_corr=+0.858 no-law=-0.527 (d=+1.385)
| LAW_imp_cold=+0.978 REL=-1.724 MEAN=-0.393 (d=+2.702) | interior LAW=0.976 (degree-invariant)
| must-fail: wrong(auc=0.702 corr=-0.475 imp=+0.466) scramble(auc=0.633 corr=-2.524 imp=-1.383)
collapse=True | L1_fit_R2=0.981 | verdict=HARD_PASS.
(Only the REAL law corrects -- no-law/wrong/scramble corrections are NEGATIVE i.e. HURT.
Relational imputation COLLAPSES on the cold tail (R2=-1.724 < mean) -> the LAW's degree-
invariance is exactly the sparse-tail win. WRONG_EXP imputes R2=0.466 (< LAW 0.978) because a
wrong-but-positive slope still captures the length-mass correlation -- beaten by margin.)

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_laws = 5*3 = 15 (FULL); verdict HARD_FAILs on breach.
- arms_differ_verified: true (META_RULE_AF hash-test at self-test; detection-score vectors).
- final_metrics_atomicity: tmp_replace (META_RULE_AH).
- except-ordering: SystemExit/KeyboardInterrupt re-raised before except Exception (no BaseException/bare).
- crlb_n/a: "rank-AUC + R2-skill cell; no argmax capacity floor. Info-ceiling = law fit R2 (0.981);
  HARD_PASS imputation bar 0.50 << ceiling."
- baseline_in_band: MARGINAL/RELATIONAL AUC 0.599/0.681 (0.05 < x < 0.95); asserted no-law < 0.95.
- discriminator_survives_scale: self-test runs the REAL mechanism on the REAL data (n_dim=2048,
  3 seeds); FULL n_dim=8192 differs ONLY in relational-code dimension (laws are dimension-free);
  discriminator (LAW>>no-law, must-fail collapse) fires at preview.
- real_code_path_exercised: [KGStore, ingest_triples, build_relational_store] (F.1, self-test constructs REAL store).
- substrate_signature_checked: [KGStore] with BASE/portable kwargs {n_ent,n_rel,n_dim,generator} (F.2/F.3).
- guard_baseline_validated: N/A -- this cell has NO control-beats-baseline break-guard. (RELATIONAL
  imputation lands BELOW the RANDOM floor on the cold tail; that collapse IS the finding, not a
  guard input. Declaring F.4 here would mis-apply it.)
- HP_SCOPE: {LAW: [all HARD_PASS gates], MARGINAL/RELATIONAL: [no-law comparator only],
  WRONG_EXP/SCRAMBLE: [must-fail only], MEAN/RANDOM: [imputation floor reference only]}.
- progress_logging: print_flush_true (timeout << 1800; per-seed progress line).

## Compute architecture
- class: (b) sequential-CPU with justification. 64 entities; closed-form laws are dimension-free;
  the only n_dim-dependent op is a [64,64] relational-similarity Gram from a REAL KGStore.
  Per-seed wall << 2s; whole cell << 10s (measured smoke 0.55s/3seeds). Not a GPU-batching
  candidate (wall-time sanity < 10s).
- storage: no_composition (relational baseline uses sharded KGStore E/R codes; no bundled
  multi-item composition). No sequential dependency across seeds.

## §15 gates
- effective_vs_nominal (A): no parameter sweep; single regime. sweep_alignment_verdict: N/A.
- bracket_includes_discriminating_band (B): N/A (no sweep). Corruption band verified discriminating
  (LAW 0.999 vs no-law 0.681; both must-fail arms near no-law floor).
- signal_shape_compatibility (C): laws are closed-form scalar maps; no primitive->primitive edge.
- reproduce_prior_chain_grade (D): reuses build_relational_store from the sibling allometry cell
  (same KGStore relational path); no new chain-grade primitive composed.
- functional_requirements (E): (1) detect off-manifold values -> law residual; (2) correct ->
  project onto law; (3) impute sparse tail -> closed-form law (degree-invariant). Each mapped.
