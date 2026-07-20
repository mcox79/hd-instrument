# Pre-reg: reasoning-readout LENGTH-GENERALIZATION chain-grade (CLUTRR-style kinship) v1

ANCHOR_NAME: reasoning_readout_length_generalization_clutrr_cg_v1
DATE: 2026-07-19
AUTHOR: exp_dev (task from Director hdi_research NIGHT-3 reoriented chain-grade)
QUEUE: LOCAL-ONLY (foreground, numpy/BLAS, wall < ~90s full). needs_orchestrator_store_sync=True.
NO push, NO remote-persist, NO git add -A. Route to skunkworks landed-VET on landing.

## PRIOR-WORK CHECK (mandatory)
substrate_query "CLUTRR kinship chain length generalization multi-hop VSA compositional reasoner":
top hits at cosine>0.30 = all about COMPOSITIONAL GENERALIZATION (wave14e_hierarchical_composition
0.391; skunkworks_correction_reasoning_IS_coverage 0.349; substrate_compositional_generalization_CLEAN
0.347 MIDDLE_BAND; stage2_vsa_cell2 0.334). These target composition-over-clean-structure, which
atom 29363 proved is FREE/construction-determined. This cell is DISTINCT: it targets
LENGTH-GENERALIZATION (train short chains 2-4, test long 2-10) where the free geometry BREAKS, on a
task whose ceiling is honestly < 1.000. NOT a rediscovery -- it is the reoriented non-free target.

## CLAIM (genuine, non-construction-determined)
A native-VSA iterative multi-hop reasoner LEARNS relational-composition rules from SHORT chains
(length 2-4) and LENGTH-GENERALIZES to LONG chains (up to 10) -- degrading gracefully -- better than a
PARAM-MATCHED FLAT/single-hop baseline that provably cannot chain beyond its hop budget, on a
CLUTRR-style kinship-chain task whose ceiling is honestly < 1.000.

## DATA
CLUTRR-style kinship-chain reasoning, GENERATED (faithful equivalent). Rationale for synthetic over
real-CLUTRR-repo: (1) real CLUTRR delivers difficulty via TEXT (entity/coref extraction) which the
substrate cannot read (Stage-3 rule: substrate does not read text), and its usable SYMBOLIC form IS a
relation-sequence + kinship answer -- exactly what we generate; (2) synthetic lets us TUNE the
irreducible ambiguity so the construction-determined GUARD provably passes (oracle_len10 < 0.90) and
lets us prove the flat must-fail mechanism. Network IS reachable (git ls-remote succeeded) but the
symbolic content would be identical and the text confound is undesirable. Data = a "relational monoid
with ambiguous composition": m named kinship-style relations; a fixed per-seed pairwise composition
kernel comp_dist[a,b,:] (distribution over results); a fraction `ambiguity_rate` of pairs map to a
MIXTURE (irreducible gender/context underdetermination -> the honest sub-1.0 ceiling), the rest
deterministic. Chains = iid base-relation sequences; answer = generative left-fold (sampling each hop);
the model observes ONLY (sequence, final answer), never intermediate states.

## ARMS (ONE variable = the compositional reasoner; same data/codes/position-family/param budget)
- ARM_A (native-VSA multi-hop reasoner): FHRR relation codes; iterative FOLD with inter-hop CLEANUP
  (sharded discipline). Composition memory W (Hebbian heteroassociative, [N,N] complex) LEARNED from
  length-2 training pairs (direct pairwise observations); key(a,b) = bind(rhoL,a)+bind(rhoR,b) with
  rhoL,rhoR = MONOTONIC/ordered fractional-power position codes (the encoding lever: order carried by
  ordered content codes + COMMUTATIVE bind, no non-commutative operator). Inference: fold W over the
  chain, cleanup to a clean relation code each hop -> iterates to ANY length.
- ARM_B (param-matched FLAT/single-hop, provably cannot chain): encodes the WHOLE chain as ONE bundle
  sum_i bind(rho_pos[i], code[r_i]) (same monotonic position family), ONE heteroassociative readout U
  ([N,N] complex, SAME shape/dtype as W) trained on length-2,3,4. No iteration. Provably fails at
  length > training budget (4): position codes rho_5..rho_10 never trained; single bundle blends k
  terms U never mapped -> chance/majority at k>=6. (ARM_B is HANDED MORE usable data (all of 2-4);
  ARM_A uses only length-2 for its pairwise memory -- CONSERVATIVE for ARM_A, strengthens the result.)

## PRIMARY MEASUREMENT
Length-generalization curve: accuracy vs chain length k=2..10 (trained only on 2-4), per arm, plus the
Bayes ORACLE (handed the true comp kernel, exact marginal fold). Headline discriminator =
long_gap_clean = mean_{k in 6..10}(ARM_A - ARM_B).

## PRE-REGISTERED BANDS (both directions)
HARD_PASS (headline, clean condition) requires ALL:
- H1: long_gap_clean >= 0.20            (A meaningfully beats flat on long chains)
- H2: ARM_B[k=10] <= max(chance, majority_class_10) + 0.10   (flat collapses; must-fail 1)
- H3: ARM_A_short(k=2,3,4) >= 0.60 * oracle_short AND ARM_A_short >= 3 * chance  (A learned the rules)
GUARD (construction-determined; if any fails -> GUARD_FAIL_CONSTRUCTION_DETERMINED, whole cell flagged):
- G1: oracle_len10 < 0.90               (handed rules do NOT solve length-10 for free)
- G2: oracle_len2 - oracle_len10 >= 0.10  (ceiling genuinely degrades with length)
- G3: oracle_len10 > 2 * chance         (task is above-chance / non-degenerate)
CONTROL (scramble = non-compositional per-sequence answers; must-fail 2):
- C1: long_gap_scramble <= 0.08         (A's length-gen advantage COLLAPSES with no learnable rule)
POSITIVE CONTROL (learned-not-handed sanity):
- P1: |ARM_A[k=2, clean] - oracle[k=2]| <= 0.12  (A reproduces the pairwise rules it learned)
HARD_FAIL if: long_gap_clean <= 0.05  OR  G1 fails (rigged)  OR  C1 fails (leakage/memorization).
MIDDLE_BAND: 0.05 < long_gap_clean < 0.20 with guards+control passing.

## CEILING CHECK
oracle_len10 reported and REQUIRED < 0.90 (target tune ~0.40-0.80). Success = beating flat on the
length slope on data with sub-1.0 ceiling, NOT hitting 1.000.

## DISCRIMINATOR-MUST-SURVIVE-SCALE
Smoke KEEPS the full length range (2..10) at reduced N/m so the long-chain discriminator FIRES at
smoke: require smoke long_gap_clean >= 0.15 AND ARM_B[k=max] <= 0.35 AND oracle_len10 in (2*chance,0.90)
BEFORE full. Full is also run foreground-to-completion (measured, not preview).

## COMPUTE ARCHITECTURE
Class (b) sequential-CPU, BATCHED across chains (fold hops = batched [n_test,N]@[N,N] complex matmul).
Tiny FHRR reference computation; wall < ~90s full, < ~10s smoke, < ~5s self-test. No GPU (sub-100s).
LOCAL-ONLY foreground; not dispatched to a zombie-prone runner. Storage strategy: SHARDED (each
relation its own code; inter-hop cleanup) -- ARM_A; ARM_B's single bundle IS the bundled must-fail.

## SCHEMA-VET / CELL-TEMPLATE FIELDS
- arms_differ_verified: True (hash ARM_A vs ARM_B predictions; must differ)
- final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: "discriminator is an accuracy GAP, not a noise-floor-limited estimate; chance floor=1/m
  documented; capacity feasibility N>m^2 (heteroassoc memory over m^2 pairwise keys) verified: full
  N=1024>324, smoke N=512>100, selftest N=256>36"
- discriminator_reachability: True (0.20 gap reachable; oracle<0.90 leaves ARM_A headroom above ARM_B)
- baseline_in_band: True gate -> require 0.10 < ARM_A_long < 0.90 AND oracle_len10 < 0.90 (not saturated)
- HARD_PASS strictly above floor (0.20 gap, band [0.05,~0.50]); MIDDLE_BAND = 0.05..0.20
- HP_SCOPE: {ARM_A_vs_ARM_B: [H1,H2,H3], oracle: [G1,G2,G3,P1], scramble: [C1]}
- cardinality_ok: True; EXPECTED_N_UNITS = n_seeds * n_conditions(2) * n_lengths(9); verdict counts.
- per-unit failure-class instrumentation: no bare except; per-seed try records failure_class
- calibration_check: default_ok_for_this_regime (ambiguity_rate fixed; oracle-in-band VERIFIED at
  smoke before full; iterate-regime if out of band)
- gate A effective_vs_nominal: ALIGNED (sweep=chain length; each hop experiences same fold depth op)
- gate B bracket_includes_discriminating_band: >=3 of 9 lengths predicted gap in [0.15,0.9] (k=6..10)
- gate C signal_shape: SHAPE_MATCH (fold: relation-code -> key -> W -> cleanup -> relation-code)
- gate D reproduce_prior_CG: N/A (fresh mechanism, no external prior-atom primitive invoked);
  internal positive control P1 = ARM_A reproduces oracle at length-2
- gate E functional_requirements: (1) learn pairwise composition from data -> Hebbian assoc memory W;
  (2) iterate composition to unseen lengths -> fold+cleanup; (3) represent relation-order asymmetry ->
  monotonic ordered position codes + commutative bind; (4) provably-can't-chain baseline -> flat bundle+U
- gate F.1/F.2/F.3/F.4: N/A (no KGStore / fit-module / store-helper / control-beats-POP guard)
- gate F.5 deterministic_seeding: True (np.random.default_rng + fixed int seeds + hashlib for scramble;
  NO builtin hash(), NO list(set()); self-test calls assert_no_nondeterministic_seeding on own source)
- progress_logging: print_flush_true (also timeout < 1800 so not strictly mandated)
- cell_chunked: False (single-process foreground local <90s; runner-zombie risk N/A; all seeds in-proc)
- start_marker_written: True; crash_diagnostic_present: True; heartbeat: exempt (foreground <90s)

## CONFIGS
- self-test: N=256, m=6, ambiguity_rate=0.35, p_major=0.60, train 400/len, test 120/len, seed 7, len 2..8
- smoke:     N=512, m=10, ambiguity_rate=0.35, p_major=0.60, train 1500/len, test 300/len, seed 7, len 2..10
- full:      N=1024, m=18, ambiguity_rate=0.35, p_major=0.60, train 4000/len, test 600/len, seeds 7,13,19, len 2..10
