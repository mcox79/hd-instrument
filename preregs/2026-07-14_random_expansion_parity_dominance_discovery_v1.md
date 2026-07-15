# Pre-registration: random_expansion_parity_dominance_discovery_v1

Date: 2026-07-14
Cell: experiments/exp_random_expansion_parity_dominance_discovery_v1.py
Anchor: random_expansion_parity_dominance_discovery_v1
Queue: remote_cpu_queue (FULL, 5 seeds). Smoke gate: LOCAL 2-seed (cleared).

## Question

The frontier cell (exp_interaction_nonadditive_discovery_v1) established a ROLE-KEYING <-> SYMMETRY TENSION:
a shared-code SYMMETRIC PRODUCT bind discovers swap-symmetric PARITY (~0.98 novel) but is order-blind and
CANNOT represent asymmetric DOMINANCE; a ROLE-KEYED bilinear bind discovers DOMINANCE but role-keying breaks
swap-symmetry so it FAILS parity. Neither specialized bind does BOTH.

Can a SINGLE RANDOM NONLINEAR EXPANSION + learned linear readout (mixed selectivity / reservoir; Rigotti/Fusi
2013, Rahimi/Recht 2007) -- high-dimensional enough in principle to keep BOTH structures linearly extractable --
discover BOTH parity AND dominance on NOVEL constituent combinations, where each specialized bind does only one?

## Mechanism (under test)

phi(x) = nonlinearity(R @ onehot_position_level(x) + b), R a FIXED random projection into D_exp dims (CONSTRUCT
the expansion), then a plain LEARNED LINEAR readout (closed-form ridge, lam=1.0). Input one-hot(position,level)
is ROLE-PRESERVING and retains full level identity. Primary nonlinearity = random ReLU; random Fourier reported
at D_ref as an expansion-family robustness datapoint. Expansion-dim SWEEP D_exp in {8,16,32,64,128,256,512};
HARD_PASS gates use a FIXED reference D_ref=512 (NOT best-over-sweep -> no selection-on-test); the sweep curve is
reported so the dimensionality threshold is visible.

## Arms

- RANDOM_EXP (mechanism, D_ref=512 ReLU) + RANDOM_EXP_FOUR (Fourier robustness)
- SYM_PROD = learned shared-code product (swap-symmetric): parity-YES / dominance-NO specialist
- ROLE_BILINEAR = learned role-keyed low-rank bilinear (Pa)*(Qb): dominance-YES / parity-NO specialist
- ROLE_ADD = learned role-keyed sum (additive contrast)
- FREQ_NULL = max(HOMOPHILY_COND, POP); MEMORIZE (per-combo lookup, fails novel); ORACLE (ceiling)

Headline families: PARITY, DOMINANCE. Context families (RE + baselines only): AND2, MULT, ADD.

## Pre-registered bands (fixed in-code BEFORE running: HP_GAP_CHANCE/HP_GAP_BEAT/MUSTFAIL_TOL/THRESH_GAP)

Evaluated on NOVEL stratum, top-1 accuracy, multi-seed mean; RANDOM_EXP at D_ref=512.

- parity_pass  = RE_parity >= chance_parity + 0.20  AND  (RE_parity - ROLE_BILINEAR_parity) >= 0.15
- dom_pass     = RE_dom    >= chance_dom    + 0.20  AND  (RE_dom    - SYM_PROD_dom)          >= 0.15
- mustfail_ok  = for ALL families: (RE_novel[ARBITRARY] - FREQ) <= 0.07 AND (RE_novel[SHUFFLE] - FREQ) <= 0.07
- ceiling_ok   = ORACLE >= RE for all families

Verdicts:
- HARD_PASS_BOTH: parity_pass AND dom_pass AND mustfail_ok AND ceiling_ok
  (one random-expansion mechanism UNIFIES what two specialized binds each do only half of).
- PARTIAL_PARITY_ONLY / PARTIAL_DOMINANCE_ONLY: exactly one headline family passes (random expansion inherits
  ONE specialist's limitation -- informative partial).
- REFUTE_RANDOM_EXPANSION_DISCOVERS_NEITHER_ON_NOVEL: neither passes (honest, valuable negative).
- INVALID_MUSTFAIL_EXPANSION_MEMORIZED: a must-fail did not fire (mustfail_ok False) -> the expansion memorized;
  the cell is NOT measuring generalization -> HAND BACK, do not tier. (LOAD-BEARING: a high-D random expansion +
  linear readout can trivially memorize; NOVEL-combo generalization + arbitrary-at-chance are the real test.)

## SCHEMA-VET fields

- cardinality_ok: true. EXPECTED_N_UNITS = 5 families x 3 regimes x 5 seeds = 75 score units.
- arms_differ_verified: true (self-test: RANDOM_EXP/SYM_PROD/ROLE_BILINEAR/ROLE_ADD/HOM = 5 distinct sha256 sigs).
- final_metrics_atomicity: tmp_replace (os.replace on metrics.json.tmp).
- except-ordering: SystemExit + KeyboardInterrupt raised before except Exception; no bare/BaseException (grep-clean).
- crlb_n/a: accuracy target has no Cramer-Rao noise floor; chance = majority-class rate is the honest per-family floor.
- discriminator_reachability: true. Arena is FIXED tiny (K=4,L=4,N=220); SMOKE == full-scale on the discriminator
  (only #seeds grows full vs smoke), so the discriminator that fires in smoke fires at full.
- baseline_in_band (META_RULE_AG): FREQ_NULL on PARITY CLEAN = 0.47, on DOMINANCE CLEAN = 0.86 (both 0.05<b<0.95).
  Self-test asserts freq_not_saturated_parity (<=0.75).
- calibration_check: default_ok_for_this_regime (ridge lam=1.0 fixed; expansion R random-fixed; no per-run tuning).
- discriminating_band: RE dominance curve spans 0.81->1.0 across the sweep (threshold visible); RE parity spans
  0.25-0.45 (clearly sub-chance, does not discover) -> both headline questions land in a measurable/discriminating
  regime, neither saturates trivially.
- real_code_path_exercised: [_expand, _ridge_fit_predict, _train_learned, arm_random_expand] -- self_test() calls
  the ACTUAL mechanism functions the FULL run uses (no synthetic-only branch); machine-checked via exercised set.
- substrate_signature: n/a (self-contained numpy/torch cell; no KGStore / external substrate object constructed).
- guard_baseline_valid: the must-fail guard compares RE vs FREQ_NULL (= majority-class rate, meaningfully above the
  1/nclass random floor), not a structural-zero baseline -> guard cannot mis-fire at floor.
- defensive_error_checking: passed_all_4_patterns (start_marker + heartbeat.jsonl + crash-metrics + no-silent-except).
- cell_chunked: false (single script, seed loop with per-seed heartbeat + flushed progress; arena tiny, ~90s total).
- progress_logging: true (stdout line_buffering + flushed per-seed _log + _heartbeat.jsonl per seed).
- compute_architecture: sequential-CPU, justified (wall < a couple minutes total; ridge = single lstsq per unit,
  learned arms = 500-epoch Adam on 48-dim over ~120 rows; no matmul-in-Python-loop scaling; tiny fixed arena).

## Smoke result (LOCAL 2-seed, cleared 2026-07-14; MEASURED@data/exp_.../metrics.json)

verdict = PARTIAL_DOMINANCE_ONLY_RANDOM_EXPANSION.
PARITY(ch=0.52): RE=0.313 (four=0.409) SYM=0.980 BIL=0.429 MEMO=0.470 FREQ=0.470 ORC=1.0; RE-BIL=-0.116; thr=None.
DOMINANCE(ch=0.62): RE=1.0 (four=0.960) SYM=0.465 BIL=1.0 MEMO=0.667 FREQ=0.859 ORC=1.0; RE-SYM=0.535; thr=D=16.
context RE: AND2=1.0 MULT=1.0 ADD=0.485. spec_confirmed=True. mustfails ok=True (parity_arb=0.0505, dom_arb=-0.0404).
Interpretation (HELD until landed-VET): random expansion is a DOMINANCE-specialist (mirror of role-keyed bilinear);
it discovers order/asymmetric + low-order conjunctions (dominance/AND2/MULT) but FAILS to generalize high-order
swap-symmetric PARITY/XOR to novel combos even at D=512, across BOTH ReLU and Fourier expansions. FULL (5 seeds)
confirms whether this holds; an honest PARTIAL/REFUTE is the expected and valuable outcome.
