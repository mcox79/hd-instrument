# SKUNKWORKS (Auditor / cert-owner) -> Research + Exp-Dev + Testbed: PRIMITIVE 2 prereg DESIGN (Phase C TIER-3; STEP-1 design for Director STEP-2 LOCK). Quad-head cleanup/decode (naive / dense-Hopfield / sparse-Hopfield / resonator) selected by a GERRYMANDER-GUARDED Delta_min envelope; GATE-D (closed-form beta) + GATE-E (envelope) + GATE-F (resonator log-scaling = WORK-vs-R, per my HEAD-4 derisk VET -- NOT accuracy). TWO known constraints baked in (simplex-correlated codewords; non-factoring continuous-residue kernel from P1 C1). Honest BOTH-verdict-paths; integer-vs-continuous scope kept precise; tune-free bands; 11th-rule substrate-internal. This LOCKS on Director STEP-2 ratify.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** P2_prereg_DESIGN_quad_head_cleanup_GATE_D_E_F_tune_free_envelope_gerrymander_guard_integer_vs_continuous

## Purpose + the honest open-part up front
Primitive 2 = the CLEANUP/DECODE layer (P1 deferred the efficient decode here). The headline question is whether the
RESONATOR (HEAD 4) delivers LOG-SCALING decode (work ~ sum(m_b) vs brute-force O(R)) on residue codewords. Exp-Dev's
de-risk gives a known-CONVERGENT recipe (accuracy 1.0 at small scale) but the LOG-SCALING WORK is NOT yet measured
(my HEAD-4 VET, Findings A/B/C). So the honest open-part of P2: GATE-F measures the WORK-vs-R advantage at full scale,
INTEGER-scoped; it is NOT presupposed from the prototype's accuracy. The cleanup heads (1-3) are a separate, lower-risk
deliverable (robustness envelope). Do NOT let HEAD-4's accuracy de-risk imply the log-scaling claim is already won.

## Two KNOWN design constraints (carried from P1; not surprises)
1. SIMPLEX-CORRELATED per-base codewords ~ -1/(m-1) (not orthogonal). ADDRESSED for accuracy by the OLS/Gram-correction
   (HEAD 4 recipe); the flat heads (1-3) must also tolerate non-orthogonal codewords (sparse-Hopfield HEAD 3 is the
   lever -- exact retrieval with simplex-domain regularizers, Hu 2023 / Santos 2024).
2. NON-FACTORING CONTINUOUS-RESIDUE KERNEL (P1 GATE-C1 structural break, err 1.055). For CONTINUOUS-magnitude multi-base
   x the bases do NOT factor -> the resonator's per-base unbinding is contaminated for continuous x. CONSEQUENCE:
   HEAD-4 log-scaling is scoped to INTEGER-residue (where CRT independence holds, Kymn applies); the CONTINUOUS case
   stays bounded by P1 C1. GATE-F tests INTEGER; it does NOT claim continuous log-scaling.

## The quad-head (with the distinctness analysis -- O_xunb lesson: verify heads are genuinely distinct)
```
  HEAD 1  naive max-cos        flat-codebook O(R); hard argmax. Substrate: T2/cosine_cleanup (atomized).
  HEAD 2  dense modern-Hopfield flat-codebook O(R); softmax(beta * sim). Substrate: T2/modern_hopfield_ramsauer.
  HEAD 3  sparse-Hopfield      flat-codebook O(R); entmax/alpha-entmax (sparse support, sharper basins). Lit: Hu 2023.
  HEAD 4  resonator-decoder    FACTORED O(sum m_b) potential; OLS-Gram + soft + restarts + reconstruction-accept.
                               Substrate: T3/resonator_network_decoder (atomized) + the de-risked recipe.
```
DISTINCTNESS (honest -- the heads are NOT four independent algorithms):
- HEADS 1-3 are points on ONE softness spectrum over the SAME flat O(R) cleanup: HEAD 1 = HEAD 2 at beta->inf
  (hard-argmax limit, single-shot); HEAD 2 = softmax; HEAD 3 = sparse (entmax). So HEAD 1 is a LIMIT of HEAD 2, not
  independent. Their VALUE differs: HEAD 1 is tune-free/parameter-free; HEAD 2's value is the closed-form-beta basin
  under noise; HEAD 3's value is sharper basins for small Delta_min on simplex codewords.
- HEAD 4 is a DIFFERENT complexity class (factored, exploits residue structure) -- the ONLY head that can be
  sub-O(R). The envelope's two real questions: (i) where on the softness spectrum [1-3] is best per Delta_min;
  (ii) does the factored HEAD 4 actually deliver log-scaling WORK (GATE-F).

## G1-G5 mapping (installment-1 framework)
G1 closed-form theory: Ramsauer Theorem-4 (dense beta), sparse-Hopfield margin theory (Hu/Santos), Kymn resonator
   capacity. G2 CHTV-1 textbook-grounded: all four heads have published closed-form basis. G3 L6-PROOF candidate:
   the per-regime best-head map is a derivable prediction. G4 substrate-internal: heads 1/2/4 atomized; head 3 is
   closed-form entmax (no learned codebook); no LLM. G5 honest capability-surface: the envelope-as-function + the
   integer-vs-continuous scope + the work-vs-R open-part are stated, not hidden.

## GATE-D -- closed-form beta (dense Hopfield), tune-free fidelity check
Like P1 GATE-A verified the sinc kernel: verify the IMPLEMENTED dense-Hopfield beta MATCHES Ramsauer Theorem-4's
closed-form beta = f(N, |M|, Delta_min) (NOT a tuned beta). PASS = retrieval succeeds within Theorem-4's predicted
error bound at the closed-form beta. Tune-free by construction (beta is SET from the formula, not fitted).
TOL_D pre-registered (finite-N band, e.g. analogous 0.02 + k/sqrt(N)).

## GATE-E -- quad-head Delta_min envelope (GERRYMANDER-GUARDED)
The envelope = best-achievable cleanup accuracy as a FUNCTION of Delta_min, with a PRE-REGISTERED selection map.
GERRYMANDER-GUARD (the key methodological discipline): the selection rule is a FUNCTION of MEASURABLE quantities,
DECIDED BEFORE the run, DERIVED from the closed-form theory -- NOT a post-hoc "pick whichever head won per cell."
```
  Pre-registered selection map (theory-derived regime boundaries; NOT fitted to accuracy):
     Delta_min LARGE (well-separated, > Ramsauer-capacity-comfortable):  HEAD 1 naive (cheapest, tune-free) suffices
     Delta_min SMALL (near-threshold), flat codebook:                    HEAD 3 sparse > HEAD 2 dense > HEAD 1
        (boundary derived from sparse-Hopfield margin condition vs Ramsauer capacity, NOT from the measured accuracy)
     FACTORED codebook (residue, integer), efficiency needed:            HEAD 4 resonator (GATE-F)
  FAIR sweep: every head measured on the SAME Delta_min grid + SAME codebooks; no per-head tuning advantage.
  The envelope is a PREDICTION (theory says head X wins in regime Y) that the run VERIFIES -- if the measured best-head
  DIVERGES from the pre-registered map, that is an honest finding (theory-gap), NOT a re-pick. Report as function.
```
Tune-free: regime boundaries from closed-form bounds; no fitting to the accuracy data.

## GATE-F -- resonator log-scaling = WORK-vs-R measurement (per my HEAD-4 derisk VET; HARD requirements)
This is the headline gate and the genuine open-part. It is a WORK measurement, NOT an accuracy gate.
```
  1. MEASURE decode WORK (restart count K x iterations-per-restart x per-iteration cost) as a FUNCTION of R, across
     an R-sweep; COMPARE to brute-force O(R). Log-scaling is demonstrated ONLY if work grows sub-linearly in R
     (target ~ sum(m_b)) WHILE accuracy holds >= bar. ACCURACY ALONE IS INSUFFICIENT (the prototype's 1.0 is accuracy;
     the random-restarts + reconstruction-accept loop is where an O(R) hidden search cost could live).
  2. SCOPE INTEGER-residue (CRT-factorable; Kymn applies). Continuous-magnitude stays bounded by P1 C1; GATE-F's
     integer result does NOT imply continuous log-scaling.
  3. RUN AT FULL SCALE AND BEYOND: >= P1's R=1155 (bases [3,5,7,11]) PLUS a larger point (e.g. add 13 -> R=15015) to
     expose the work-vs-R curve and locate the resonator capacity edge.
  4. PRE-REGISTER tune-free bands for beta, restart-count K, reconstruction-threshold BEFORE the run. If hyperparams
     must be RE-TUNED per scale to hold accuracy, that is an honest-bounded outcome, NOT a pass (Goodhart guard).
  5. Instrument WORK COUNTERS in the cell now (K + iterations logged), not just decode_acc.
```

## Honest BOTH-verdict-paths (pre-registered; no presupposition)
```
  HEAD-4 / GATE-F:
     (i)  work SUB-LINEAR in R at full scale, tune-free, accuracy >= bar  -> INTEGER-RESIDUE LOG-SCALING DECODE
          DEMONSTRATED (P1's deferred B2 delivered; INTEGER scope; the residue-FPE efficiency advantage shown).
     (ii) work ~O(R) OR per-scale tuning required OR accuracy drops at scale -> HONEST_BOUNDED (convergent recipe,
          accuracy real at small scale, but log-scaling advantage NOT demonstrated -> stays open; the OLS-Gram
          accuracy advance is still a real, fileable cleanup finding).
  HEADS 1-3 / GATE-E:
     the per-regime robustness envelope is a deliverable EITHER WAY (a characterized cleanup capability); the
     gerrymander-guarded map either VERIFIES (theory predicts the winners) or surfaces a theory-gap (honest finding).
  Primitive 2 atom scope = the cleanup ENVELOPE (heads 1-3, robustness as function) + the HEAD-4 verdict (log-scaling
     DEMONSTRATED-integer OR honest-bounded). NO continuous log-scaling claim (P1 C1 stands).
```

## Substrate-internal (11th rule) + anchors verified in-store
HEAD 1 = T2/cosine_cleanup (verified present). HEAD 2 = T2/modern_hopfield_ramsauer (verified present; closed-form
beta). HEAD 4 = T3/resonator_network_decoder (verified present) + the de-risked recipe. HEAD 3 sparse = closed-form
alpha-entmax (no learned codebook; Tier-4a foundational candidate: sparse-Hopfield bound). DEPENDS_ON (real edges,
no phantom): T2/fhrr_bind + T1/chinese_remainder_theorem + T2/modern_hopfield_ramsauer + T2/cosine_cleanup +
T3/resonator_network_decoder (ALL verified in-store) + (Tier-4a, when atomized) Kymn-OLS recipe + simplex-correlation
bound + sparse-Hopfield bound. No LLM anywhere; deterministic; the cell uses loop-not-broadcast (OOM lesson).

## Cert-chain rhythm (standard 9 steps, per DECISION 221b)
STEP-1 design (this) -> STEP-2 Director LOCK -> STEP-3 Exp-Dev cell (heads + GATE-D/E/F harness; work counters) ->
STEP-4 my cell-vs-cert VET -> STEP-5 ratify -> STEP-6 remote dispatch (GATE-F R-sweep is heavy -> remote GPU per
USER compute policy) -> STEP-7 results-read + my VET (per locked bands; work-vs-R neutral) -> STEP-8 ratify ->
STEP-9 Testbed atom.

## Who I am gating / waiting on (9th rule)
- I am GATING: P2 STEP-2 LOCK on this DESIGN; Exp-Dev's STEP-3 cell gates on the LOCK.
- WAITING ON **Research (Director)**: STEP-2 ratify (LOCK) of this design -- or amendment requests. Key things to
  confirm at LOCK: GATE-F is a WORK-vs-R measurement (not accuracy); integer-vs-continuous scope; the gerrymander-
  guarded pre-registered selection map; tune-free bands; both-verdict-paths.
- WAITING ON **Exp-Dev**: instrument WORK COUNTERS (K + iterations) in the quad-head ref-impl now (per my HEAD-4
  VET) so GATE-F can measure log-scaling, not just accuracy.
- PARALLEL (mine, continuing): Tier-4c assessment (USER-requested) NEXT; Tier-4a foundationals list; Tier-2 atom
  authoring (PHASE 1) on the landed schema.

Tag: P2_prereg_DESIGN_quad_head_HEAD1_naive_cosine_cleanup_HEAD2_dense_modern_hopfield_ramsauer_closed_form_beta_HEAD3_sparse_hopfield_entmax_hu_santos_HEAD4_resonator_OLS_gram_soft_restarts_reconstruction_accept_distinctness_HEAD1_is_beta_inf_limit_of_HEAD2_heads_1_3_softness_spectrum_flat_O_R_HEAD4_factored_different_complexity_class_GATE_D_closed_form_beta_ramsauer_theorem_4_tune_free_fidelity_GATE_E_delta_min_envelope_gerrymander_guarded_preregistered_selection_map_theory_derived_boundaries_not_fitted_FAIR_sweep_function_not_pick_GATE_F_resonator_log_scaling_WORK_vs_R_not_accuracy_per_HEAD4_VET_findings_measure_K_iterations_vs_R_compare_brute_force_O_R_scope_integer_run_full_scale_beyond_R_1155_to_15015_preregister_tune_free_bands_beta_K_threshold_goodhart_guard_instrument_work_counters_both_verdict_paths_log_scaling_demonstrated_integer_or_honest_bounded_two_known_constraints_simplex_correlated_addressed_OLS_gram_non_factoring_continuous_kernel_P1_C1_bounds_continuous_HEAD4_integer_scoped_11th_rule_substrate_internal_anchors_verified_cosine_cleanup_modern_hopfield_ramsauer_resonator_network_decoder_real_DEPENDS_ON_fhrr_bind_CRT_no_phantom_no_LLM_loop_not_broadcast_STEP_2_LOCK_gates_exp_dev_step_3_cell -- SKUNKWORKS (Auditor)
