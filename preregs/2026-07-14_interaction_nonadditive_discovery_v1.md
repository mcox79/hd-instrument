# Pre-registration: interaction_nonadditive_discovery_v1

Anchor: `interaction_nonadditive_discovery_v1`
Cell: `experiments/exp_interaction_nonadditive_discovery_v1.py`
Queue: `remote_cpu_queue` (glass-box CPU; NO GPU; NO LLM at measurement time)
Date: 2026-07-14
Author: exp_dev

## Question (two sub-questions; construction-proof != capability-win, kept distinct)

Can an INTERACTION / non-commutative composition op read out NON-ADDITIVE (parity / AND / multiplicative) and
ORDER-SENSITIVE (dominance) targets that a monotone-ADDITIVE code provably cannot -- and does a LEARNED shared-code
+ non-additive-readout DISCOVER that structure from data (extending the proven abelian/commutative-discovery to the
non-commutative case)?

- (A) CONSTRUCTION-PROOF: a matched interaction / order-aware code + readout solves a PLANTED non-additive
  conjunction (parity, AND) and an antisymmetric target (dominance) INCLUDING novel constituent combinations,
  where the monotone-additive / symmetric-bind contrast is at/below chance. Algebra-matched => construction-proof,
  NOT a capability win. Arbitrary/shuffle must-fails fire.
- (B) DISCOVERY (the prize): a LEARNED shared-code + non-additive-readout (plain SGD, NO hand-designed algebra)
  DISCOVERS the structure from data -- generalizes to novel pairs >> memorize, arbitrary at chance. If it fails
  that is an honest, valuable negative (discovery bounded).

## Prior-work check (substrate-KB concept query before authoring)
`tools/director_kb_query.py --tau 0.15 "non-commutative role binding interaction code non-additive AND-gate parity
conjunction discovery"` returned NONE at cosine > 0.15. The two converging prior threads are inlined in the cell
docstring: (1) the DISCOVERY VET (abelian/commutative discovered ~0.41; asymmetric = symmetric-readout WALL);
(2) the GENERATION cell `exp_generated_conjunction_monotone_foods_v1` (commit e7e5f1135; monotone-additive
STRUCTURALLY loses on AND=-0.018 / parity=-0.006). This cell is a genuine EXTENSION, not a rediscovery.

## Arena (planted, deterministic, glass-box)
K=4 constituents, L=4 ordinal levels, N_ENT=220 distinct combos sampled from the 256-grid, novel query split 0.45.
Five target families over the SAME X: PARITY (pure interaction, zero additive info), AND2 (conjunction; additive
gets partial), MULT (multiplicative = log-additive), DOMINANCE (antisymmetric / order-sensitive), ADD (additive
positive control). Seeds = (7, 13, 17, 23, 29). Metric = NOVEL-stratum top-1 accuracy, multi-seed mean.

## Arms
- INT_MATCH (construction): family-matched interaction readout. Parity/AND route the product through the REAL
  substrate `hdlab.binding.bsc_bind` (elementwise multiply => parity = product-of-signs, AND = product-of-
  indicators); dominance = order-aware sign(x0-x1); mult = product magnitude; add = sum. Train-fit majority map
  over the low-cardinality combo-SHARED structural feature -> generalizes to novel combos.
- MONO (contrast): monotone-additive (train-Spearman-oriented, non-negative-weighted sum, quantile thresholds).
- LEARN_INT (discovery): learnable role-keyed per-(constituent,level) embedding, ELEMENTWISE-PRODUCT (Hadamard)
  composition, linear readout, plain Adam SGD.
- LEARN_ADD (contrast): same role-keyed embedding, SUM composition. NOTE: with free per-level embeddings this is a
  FLEXIBLE additive model f0(x0)+f1(x1) -- it captures any transform-additive target (MULT via log, DOMINANCE via
  signs). Only PARITY is genuinely non-additive against it.
- LEARN_SYM (contrast): SHARED-code (no role) + PRODUCT composition = swap-SYMMETRIC / commutative bind. Provably
  fails DOMINANCE (swap-invariant readout cannot represent x0>x1). This is the non-commutative discriminator.
- LEARN_BILINEAR (discovery, brain-grounded upgrade per drill_brain_nonadditive_interaction_..._2026-07-14):
  FIXED shared level-code, LEARNED per-role projection P_i initialized at IDENTITY (so it STARTS as the Hadamard
  special case, then learns cross-dim mixing). Kim et al. 2016 low-rank bilinear pooling; parietal gain-field
  brain analog (Zipser-Andersen 1988). The best-in-class learned interaction arm.
- Baselines: FREQ_NULL = max(HOMOPHILY_COND, POP) ; MEMORIZE ; POP ; ORACLE (ceiling).
Best-in-class learned-interaction score = max(LEARN_INT, LEARN_BILINEAR) per family.

## Compute architecture
Class (b) sequential-CPU with justification: numpy data + torch CPU. Per-fit tensors are tiny (N~120 train, D=48,
K=4); 5 families x 5 seeds x 4 learned arms x 500 epochs full-batch Adam. Wall < 4 min local (2-seed smoke = 80s).
No matmul-in-python-loop scaling concern (D=48, no large-N). Storage: no_storage / no_composition of stored items
(this is a readout-representability + SGD-discovery experiment, not a memory-capacity sweep). GPU batching not
required (sub-4-min CPU; below the 10s/phase-point batching-candidate threshold per arm-fit).

## Pre-registered bands (fixed BEFORE the canonical 5-seed run)
Chance = majority-class rate per family (imbalanced targets). Thresholds:
- HP_A_INT_FLOOR = 0.90 ; HP_A_MONO_MARGIN = 0.07 ; HP_A_INT_MONO_GAP = 0.30 ; HP_A_SYM_MARGIN = 0.10
- HP_B_INT_ADD_GAP = 0.15 ; HP_B_INT_MEMO_GAP = 0.15 ; HP_B_INT_CHANCE = 0.20 ; HP_B_DOM_SYM_GAP = 0.15
- REFUTE_A_MARGIN = 0.15 ; REFUTE_B_GAP = 0.05 ; MUSTFAIL_TOL = 0.07

### (A) construction
- HARD_PASS_A: PARITY INT_MATCH_novel >= 0.90 AND MONO_novel <= chance+0.07 AND (INT-MONO) >= 0.30 ; DOMINANCE
  INT_MATCH_novel >= 0.90 AND LEARN_SYM_novel <= chance+0.10 ; INT_MATCH arbitrary+shuffle must-fails fire
  (gap <= 0.07) on the interaction-CLAIM families {PARITY, AND2, MULT, DOMINANCE} ; oracle ceiling ok.
- REFUTE_A: INT_MATCH_novel < chance+0.15 on parity OR dominance (matched op cannot represent -> impl bug).

### (B) discovery -- THREE principled sub-verdicts (one per structure class)
- B1 disc_noncommutative (DOMINANCE; the clean extension): best(LEARN_INT,LEARN_BILINEAR) - LEARN_SYM >= 0.15
  AND - MEMORIZE >= 0.15 AND leak ok. Contrast is the SYMMETRIC bind (dominance is additively-separable-with-
  signs, so the flexible learned-additive arm also solves it -- the interaction op's advantage here is SYMMETRY-
  BREAKING, not non-additivity).
- B2 disc_nonadditive (PARITY; the genuine non-additive test): best(LEARN_INT,LEARN_BILINEAR) - LEARN_ADD >= 0.15
  AND - MEMORIZE >= 0.15 AND >= chance+0.20. (MULT/DOMINANCE excluded as non-additive tests: they are transform-
  additive and the flexible learned-additive arm solves them; PARITY is the only target with no additive-izing
  transform.) parity_refute if best - LEARN_ADD <= 0.05.
- Combined verdict_B: HARD_PASS if B1 AND B2 ; PARTIAL_..._NONCOMMUTATIVE if B1 only ; PARTIAL_..._NONADDITIVE if
  B2 only ; REFUTE if neither.
- B_leak (must-fail): best learned interaction arbitrary+shuffle gap <= 0.07 on {PARITY, AND2, MULT, DOMINANCE}.

MULT-vs-flexible-additive and the ADD-control arbitrary leak (high-cardinality raw-sum feature, mild finite-sample
positive gap) are REPORTED diagnostics (`gates.b_mult_bestlint_add_gap`, `gates.add_control_leak`), NOT PASS gates.

## SCHEMA-VET / discipline compliance
- cell_chunked: false (single-cell multi-seed sweep, wall < 4 min; not a runner-zombie risk)
- start_marker: n/a (short cell) ; crash_diagnostic_present: true (except Exception -> CELL_CRASHED metrics + tb)
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except) -- grep-gate PASS
- final_metrics_atomicity: tmp_replace (os.replace) ; run_mode default = full (runner calls `python -u <script>`)
- arms_differ_verified: true (self-test asserts MONO/LEARN_INT/LEARN_ADD/LEARN_SYM/LEARN_BILINEAR/HOM mutually
  distinct; INT_MATCH/ORACLE exempted -- legitimately coincide on a perfectly-solved family)
- baseline_in_band: MONO parity ~0.51 (chance), FREQ_NULL ~0.47 (not saturated), oracle=1.0 -> in-band
- crlb_n/a: no quantitative noise-floor primitive; discriminator is accuracy dissociation, reachability shown by
  self-test (INT solves at 1.0; symmetric/additive contrasts at chance)
- calibration_check: default_ok_for_this_regime (planted synthetic arena; no substrate-distribution calibration)
- discriminator survives scale: smoke run at FULL family/arm config (2 of 5 seeds) fires all discriminators
  (INT-MONO=0.48, INT-LSYM=0.54, disc_noncommutative=True)
- real_code_path: self-test EXERCISES the real substrate bind -- `hd_bind` (FHRR homomorphism (i+j)mod L) and
  `bsc_bind` (parity=product-of-signs, AND=product-of-indicators) verified vs numpy ground truth
- progress_logging: print_flush_true (line-buffered stdout + per-seed flush logs) ; timeout 1200s

## Predictions (HYPOTHESIZED -- to be confirmed by the canonical 5-seed remote run)
From the 2-seed local smoke (HYPOTHESIZED@this prereg, NOT the canonical result):
- (A) HARD_PASS: PARITY INT=1.00 MONO=0.52 (gap 0.48); DOMINANCE INT=1.00 LSYM=0.46; must-fails fire.
- (B) PARTIAL: disc_noncommutative TRUE (DOMINANCE best-learned=1.00 vs LEARN_SYM=0.46); disc_nonadditive FALSE
  (PARITY best-learned ~0.43 < chance+0.20; neither Hadamard nor bilinear discovers parity -> honest negative,
  consistent with parity-SGD-hardness). MULT LEARN_ADD=1.00 (log-additive; not a non-additivity discriminator).
Expected canonical verdict: `HARD_PASS_A_INTERACTION_CONSTRUCTION_PROVEN | PARTIAL_B_DISCOVERS_NONCOMMUTATIVE_BUT_
NONADDITIVE_PARITY_BOUNDED`. The 5-seed run is the canonical result (canon != preview).

## Fairness + weak-point localization
- Info-ceiling: ORACLE arm per family (1.0 by construction on CLEAN; must dominate INT_MATCH).
- Fair baselines: FREQ_NULL (marginal/homophily), MEMORIZE (combo lookup), POP (majority).
- Must-fails fire: ARBITRARY (random-per-combo) + SHUFFLE (label permutation) both drive mechanism arms to freq.
- Confound: MEMORIZE isolates combo-lookup leakage; novel stratum = combos never in train.
- Metric-can-move: demonstrated (INT 1.00 vs MONO 0.52 vs freq 0.47 all distinct within one arena).
- Weak-point localization: per-family x per-regime x per-seed novel table persisted
  (`per_family_regime_novel`) -> pinpoints exactly which structure class each arm breaks on.
