# Pre-reg: TRANSITION_OP vs commutative additive_map on REAL CSKG 2-hop irreducible order-reversal composition

Anchor: `transition_op_cskg_2hop_order_reversal_v1`
Cell: `experiments/exp_transition_op_cskg_2hop_order_reversal_v1.py`
Filed: 2026-07-15 (exp_dev)
Design source: `notes/research_transition_op_real_data_test_target_2026-07-15.md` (candidate #1, BEST/ready-to-build)
Prior-work check (substrate-KB concept-query, cosine>0.30 top hits): "Multiplicative vs additive composition" (0.399,
  note), "Composition primitive" (0.368, prereg exp3 family), "Multiplicative composition" (0.357, note). NONE is a
  prior real-data ORDER-REVERSAL / non-commutative-transition-operator test on CSKG multi-hop. This cell is genuinely
  NOVEL (first real-data transfer of the VET'd TRANSITION_OP vs the live additive_map's commutative composition);
  the composition-primitive hits are the abelian-additive-map family it is designed to BEAT, not a rediscovery.

## Question
Does a non-commutative per-relation matrix-chain operator (TRANSITION_OP, VET'd CHAIN_GRADE on the synthetic dominance
arena) improve REAL directed multi-hop relational reasoning on a FREQUENCY-CAP-IMMUNE task, specifically beating the
live `additive_map`'s PROVABLY COMMUTATIVE translation-vector composition (`X_h + D_r1 + D_r2 = X_h + D_r2 + D_r1`) --
the exact order-blind flaw TRANSITION_OP fixes?

## Construction-level motivation (load-bearing; this is why the discriminator survives scale, option B)
`additive_map` scores `score(t) = -||X_h + D_r - X_t||` (TransE); 2-hop composition = `X_h + D_r1 + D_r2`, which is
IDENTICAL under order swap for ANY trained D. On an eval set of ORDER-SENSITIVE queries (where gold(h,r1,r2) !=
gold(h,r2,r1)), the commutative arm assigns IDENTICAL scores to both orders -> it is structurally capped at getting at
most one of each reversed pair right, REGARDLESS of fit quality or scale. TRANSITION_OP composes as
`X_h M_r1^T M_r2^T` with `M_r1^T M_r2^T != M_r2^T M_r1^T` in general -> can represent order. The discriminator gap
is therefore an ARCHITECTURAL bound, not an empirical hope: it cannot vanish at scale. (DISCRIMINATOR-MUST-SURVIVE-
SCALE: satisfied by analytical option B + a full-N-behavior self-test on a planted non-commutative arena.)

## Data / arena
CSKG typed/asymmetric-relation directed subset (excludes the 68.6% near-symmetric lexical relations RelatedTo/Synonym/
etc. that the sibling reachability-audit drill root-caused as homophily-driving). Typed relations kept (exact `/r/<Name>`
suffix match, directed head->tail preserved): IsA, PartOf, HasA, MadeOf, Causes, CausesDesire, HasPrerequisite,
HasSubevent, HasFirstSubevent, HasLastSubevent, MotivatedByGoal, UsedFor, ReceivesAction, CapableOf, AtLocation,
LocatedNear, Entails, CreatedBy. Entity budget capped by a degree floor + max_nodes to keep the multi-fit tractable
(FULL: max_nodes<=20000). All numbers below the loader are MEASURED@ the cell's provenance block at run time.

## Arms (all rank candidate tails for held-out irreducible 2-hop query (h, r1, r2); MRR + Hits@10, FILTERED)
- TRANSITION_OP            per-relation matrix M_r [k,k] (RESCAL/TEM form); 2-hop pred = X_h M_r1^T M_r2^T. NEW candidate.
- ADDITIVE_MAP_COMMUTATIVE the LIVE baseline: real `fit_kge_anchor1` (additive_map's exact coord source);
                           2-hop pred = X_h + D_r1 + D_r2. Order-blind by construction. (F.1 real_code_path arm.)
- TRANSITION_OP_SHUFFLED   SAME trained M_r, hops composed in reversed order at TEST only (X_h M_r2^T M_r1^T).
                           Order-attribution diagnostic (the synthetic cell's SHUFFLED_ORDER ablation, transferred).
- FREQ_COMPOSED            per-hop marginal-tail-frequency composition (train-order stats only). Honest must-beat null.
- DEGREE                   degree/popularity tail ranking (Akrami-style degree floor). Honest must-beat null.
- CHANCE                   uniform-random tail rank (sanity floor).
- MEMORIZE                 exact-chain lookup from train; POP fallback. ~CHANCE on held-out irreducible (leak sentinel).

Fit fairness: TRANSITION and ADDITIVE trained with the SAME objective family (CE self-adversarial + N3 + reciprocal +
minibatch SGD), SAME constants (A1_LR/A1_GAMMA/A1_N_NEG/A1_ADV_TEMP/A1_N3_LAMBDA/A1_BATCH imported from
`experiments/_kge_anchor1_fit`), SAME epochs, SAME k. ADDITIVE calls the live recipe verbatim; TRANSITION mirrors it
with matrix ops + a Lacroix inverse-relation block (forward readout uses M[:n_rel] only). arms_differ: exempt pair
(TRANSITION_OP, TRANSITION_OP_SHUFFLED) [same model; equality IS the null diagnostic].

## Splits (fairness-critical)
1. IRREDUCIBILITY FILTER (Gregucci et al. 2025): drop any 2-hop query (h,r1,r2)->t where a direct 1-hop edge h --r--> t
   exists for ANY r (a one-hop shortcut), OR t is in the 1-hop neighborhood of h. Only irreducible chains are evaluated.
2. ORDER-REVERSAL HELD-OUT SPLIT: partition ordered relation-pairs into TRAIN-ORDER and TEST-ORDER so each TEST-ORDER
   pair (r1,r2) has its REVERSE (r2,r1) present in TRAIN-ORDER. Operators fit on ALL single-hop edges; the FREQ/DEGREE
   nulls are estimated from TRAIN-ORDER composition stats ONLY (cannot memorize the test-order answer distribution).
3. ORDER-SENSITIVE MATCHED SUBSET (reported sharpener, not primary gate): held-out queries where BOTH orders exist
   with different gold tails -> the sharpest exposure of the commutative cap. Reported separately; may be small/empty
   (reported n; if n < 30 the sharpener is annotated LOW_POWER and not interpreted).
Determinism: all splits/RNG from FIXED integer seeds + sorted(set()) canonical dedupe. NO built-in hash()/list(set())
(F.5 static scan enforced by queue_add).

## Compute architecture
Class (c) mixed-with-justification. Fits are torch minibatch SGD (matmul-heavy) but small (n_rel~18, k=32, ~<=20k
entities); GPU optional (cell defaults device='cpu', runner does not pass argv). Genuinely sequential dependency: the
2-hop compose chains hop N on hop N-1 (SHARDED per-entity codes; NO bundled storage -- each entity its own coord row).
Storage strategy: sharded (entity coords X [N,k], per-relation ops). Wall estimate FULL: 4 fits (add/trans, and their
scramble-refits) x 3 seeds, ~150 epochs each on <=20k ents ~= 1-3h CPU -> REMOTE (remote_cpu_queue). memsmoke slice
(150k lines, small node cap, 20 epochs, 1 seed) is the remote gate; NOT run locally (USER no-local-compute lock).

## Pre-registered bands (FIXED before running)
Primary metric = MRR on the IRREDUCIBLE, ORDER-REVERSAL-HELD-OUT 2-hop test set, NOVEL (test-order) stratum, mean over
seeds. NULL = max(FREQ_COMPOSED, DEGREE) MRR (the honest floor). MARGIN = 0.15 (deflated first-cross-domain transfer
per scout; module-registry standard is 0.15-0.30). Strictly-above-floor per META_RULE_L: report clears band by >=5% width.

- HARD_PASS = TRANSITION_OP_MRR - ADDITIVE_MRR >= 0.05 (STRICTLY beats the commutative baseline)
              AND TRANSITION_OP_MRR - NULL_MRR >= 0.15 (beats the degree/freq floor by the pre-reg margin)
              AND order_attribution_confirmed: (TRANSITION_OP_MRR - TRANSITION_OP_SHUFFLED_MRR) >= 0.10 on the test set
              AND scramble_gate_ok (arena is NOT homophily-carried; see below).
- HARD_FAIL = TRANSITION_OP_MRR - ADDITIVE_MRR <= 0.02 (ties the commutative baseline; order does not help on real
              directed data) OR TRANSITION_OP_MRR - NULL_MRR <= 0.05 (degree/freq-dominated -- the dense-cell lesson)
              OR NOT order_attribution_confirmed (SHUFFLED does not degrade -> the "order" signal is not load-bearing;
              claim void even if raw MRR looks high) OR NOT scramble_gate_ok (no fair test was actually run).
- MIDDLE_BAND = beats ADDITIVE and NULL but by a sub-threshold margin (0.02 < add_gap < 0.05 OR 0.05 < null_gap < 0.15),
              OR clears margins on the aggregate set but the order-sensitive matched subset (if adequately powered)
              does not confirm, OR partial SHUFFLED degradation (0.05 <= order_gap < 0.10). Reported per-condition,
              NOT averaged into one global number.
- REFUTE_IMPL = the 2-hop arena/impl is degenerate (fewer than MIN_IRREDUCIBLE held-out test queries, or ORACLE-tail
              reachability < floor) -> cannot run a fair test; re-spec, do not interpret arms.

SCRAMBLE_REFIT gate (arena-sanity, reused from sibling v3): refit BOTH ops with relation labels permuted; scramble_gate_ok
= the beyond-null MRR margin of the CLEAN TRANSITION_OP is retained by at most `rel_specific_frac <= 0.70` after shuffle
(i.e. >=30% of the margin is relation-specific, not homophily-carried). If a label shuffle keeps most of the margin, the
signal is degree/homophily, not directed composition -> HARD_FAIL_ARENA_HOMOPHILY.

## Honest odds
P_deflated(HARD_PASS) ~ 0.30 (carried from scout). MIDDLE_BAND is the single most-likely outcome (real KG multi-hop
carries substantial-but-not-total beyond-frequency signal; Safavi/Koutra, Akrami). A clean HARD_FAIL (order doesn't
help on real data OR degree-dominated) is a genuinely useful scoping refute, same value class as this week's real-data
refutes -- designed to REFUTE cleanly.

## SCHEMA-VET / cell-template mandate fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds (3 FULL) x n_arm_fits; verdict counts per-seed results, HARD_FAIL_
  CARDINALITY_BREACH if < expected.
- arms_differ_verified: true (hash-test at self-test; exempt pair (TRANSITION_OP, TRANSITION_OP_SHUFFLED) declared).
- final_metrics_atomicity: "tmp_replace" (metrics.json.tmp -> os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException). Grep-clean of bare except.
- crlb_n/a: "ranking-MRR task; no Gaussian noise floor. Feasibility instead governed by the construction-level
  commutative cap (ADDITIVE_MRR order-sensitive-subset <= 0.5 ceiling) + the reported ORACLE-reachability upper bound;
  HARD_PASS margins verified reachable below ORACLE at self-test."
- discriminator_reachability: true (ORACLE upper bound reported; HARD_PASS thresholds below it; commutative cap is the
  analytical headroom guarantee).
- baseline_in_band: verified at self-test (ADDITIVE and NULL MRR strictly between CHANCE floor and ORACLE ceiling; not
  saturated >0.95, not at chance).
- calibration_check: "default_ok_for_this_regime" -- fit constants inherited verbatim from the live additive_map recipe
  (A1_*), the exact regime the baseline is defined on; TRANSITION uses the identical constants. Evidence: self-test
  reproduces additive commutativity property + both fits converge (loss decreases) at tiny scale.
- HP_SCOPE: {TRANSITION_OP: [beats_additive, beats_null, order_attribution, scramble]; ADDITIVE_MAP_COMMUTATIVE: [];
  TRANSITION_OP_SHUFFLED: []; FREQ_COMPOSED: []; DEGREE: []; CHANCE: []; MEMORIZE: [leak_sentinel_below_null]}.
- per-unit failure-class instrumentation: specific except classes; failure_class per failed seed; no bare except.
- cell_chunked: false (single cell; per-seed loop with per-seed checkpoint of partial results + heartbeat; a fit crash
  records failure_class and FAILs loud, does not silently continue).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics + traceback).
- heartbeat_present: true (per-seed + per-fit-epoch-block _heartbeat.jsonl). defensive_error_checking:
  "passed_all_4_patterns".
- progress_logging: true (flush=True + stdout line_buffering; per-epoch-block progress; timeout_s FULL >= 1800).

### Test-design gates (section 15)
- effective_vs_nominal_parameter_audit: no swept scalar axis (fixed k/epochs); sweep_alignment_verdict: ALIGNED (n/a).
- bracket_includes_discriminating_band: the discriminating axis is arm-vs-arm, not a scalar sweep; ADDITIVE order-
  sensitive-subset MRR is analytically capped ~<=0.5 while TRANSITION is uncapped -> the gap band is discriminating by
  construction. Self-test verifies ADDITIVE order_gap ~ 0 and TRANSITION order_gap > 0.
- signal_shape_compatibility_audit: composition_edges: X_h (k,) --M_r (k,k)--> tail-pred (k,) [SHAPE_MATCH];
  D_r (k,) additive --> tail-pred (k,) [SHAPE_MATCH]. No SHAPE_MISMATCH.
- reproduce_prior_chain_grade_result_as_positive_control: ADDITIVE_MAP_COMMUTATIVE arm calls the REAL live
  `fit_kge_anchor1` at the TEST regime (its own recipe). Additionally the self-test asserts the additive arm's
  commutativity property (its defining prior property) reproduces exactly. regime_extension_audit: SHAPE_DRIFT
  (synthetic-dominance -> real-CSKG-multi-hop) declared; risk = real 2-hop may lack order-dependence (-> HARD_FAIL via
  SHUFFLED null, which is the designed refute).
- functional_requirement_decomposition_present: yes (see Arms). FR1 order-sensitive composition -> TRANSITION_OP
  (matrix chain); FR2 frequency-immune eval -> irreducibility filter + order-reversal split; FR3 honest floor ->
  FREQ_COMPOSED + DEGREE; FR4 attribution -> SHUFFLED + SCRAMBLE_REFIT.
- real_code_path_and_signature_preflight (F.1-F.5): self-test constructs the REAL fit (`fit_kge_anchor1`) at N~24 +
  binds its signature; F.5 static scan (no hash()/list(set)) enforced by queue_add. Declared checks: real_code_path
  (exercised_entrypoints includes fit_kge_anchor1), substrate_signature (fit_kge_anchor1 base kwargs), guard_baseline_
  valid (n/a: no control-beats-POP break-guard; MEMORIZE leak sentinel compared to NULL not used as a break-guard).

## Positive/negative controls summary
- Positive: ADDITIVE arm = live recipe reproduces at test regime; ORACLE-reachability reported as ceiling.
- Negative/must-fail: SCRAMBLE_REFIT (label shuffle must destroy >=30% of margin); TRANSITION_OP_SHUFFLED (order
  permute must degrade); MEMORIZE (must be <= NULL on held-out irreducible = no leak); CHANCE floor.
