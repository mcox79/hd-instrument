# PRE-REG: interaction_bilinear_wall_break_v1

Filed: 2026-07-15 (pre-reg BEFORE run). Cell: `experiments/exp_interaction_bilinear_wall_break_v1.py`.
Anchor: `interaction_bilinear_wall_break_v1`. Metrics: `data/exp_interaction_bilinear_wall_break_v1/metrics.json`.

## Question
Does a MINIMAL learnable upgrade of the elementwise/symmetric bind -- a per-role LOW-RANK BILINEAR projection
`P_i = I + U_i V_i^T` (rank R; `U_i,V_i` ZERO-init so at init `P_i=I` and the op is EXACTLY the elementwise /
symmetric-product special case) on a SHARED learnable code, folded by product -- discover BOTH a SYMMETRIC
non-additive structure (PARITY) AND an ANTISYMMETRIC / order-sensitive structure (DOMINANCE) on NOVEL combos,
each within tolerance of the RESPECTIVE specialist, WITHOUT the role-keying<->symmetry tension? A yes would BREAK
the commutativity wall with a single enriched operator (cheaper than the joint-code + two-head design that landed
MIDDLE with over-tolerance interference).

## Why this is the pre-scoped frontier (inlined; no re-hunt)
- `exp_interaction_nonadditive_discovery_v1` (commit 59056b6d4): localized the ROLE-KEYING<->SYMMETRY TENSION.
  Symmetric-product bind discovers PARITY (~0.98) but fails DOMINANCE; role-keyed bind does DOMINANCE but fails
  PARITY on novel. NO single FIXED op does both. Its `LEARN_BILINEAR` arm was FULL-rank D*D per-role (init
  identity + noise, no rank constraint, no zero-init) -> behaved as just-another-role-keyed arm. This cell is the
  GENUINE rank-1 low-rank test it was not.
- `exp_joint_dual_channel_readout_v1` (commit 947d8c913): landed `MIDDLE_BOTH_DISCOVERED_HEADDISC_CLEAN_
  INTERFERENCE_OVER_TOL` -- a joint code + TWO heads discovers both (PARITY JD_CONFIG=0.816 vs SYM_PROD
  specialist 0.976; DOMINANCE JD_ORDER=1.0 vs ROLE_KEY 0.998) but pays cross-channel interference over tolerance.
  MEASURED@data/exp_joint_dual_channel_readout_v1/metrics.json:verdict_msg. This cell tests whether ONE learned
  op is enough (no two heads).
- brain-nonadditive drill (a48d3739): ranked LEARNED LOW-RANK BILINEAR / gated-multiplicative bind
  `z=(P a)(*)(Q b)` #1 (Kim et al. 2016 low-rank bilinear pooling; parietal gain-field). Our elementwise bind is
  the P=Q=I special case; learning P,Q is a minimal learnable upgrade. CITED@notes/drill_brain_nonadditive_
  interaction_relational_coding_bestinclass_2026-07-14.md.
- Prior-work substrate-KB concept-query ("learned low-rank bilinear bind commutativity non-additive interaction
  discovery"): top hits below cosine 0.30 (max 0.2861 'commutative'; 0.2754 'ghrr_noncommutative_bind') -> GENUINELY
  NOVEL, not a rediscovery. GHRR matrix-vector bind is a cheaper non-commutative precedent (acknowledged).

## Arena (SAME as the VET-clean discovery arena, unchanged)
K=4 constituents, L=4 ordinal levels, N_ENT=220 sampled distinct combos (space L^K=256), QUERY_FRAC=0.45,
novel-split (novel = query combos never seen in train). Families: PARITY (symmetric non-additive, ZERO additive
info), DOMINANCE (antisymmetric x0>x1), AND2/MULT (transform-additive diagnostics), ADD (additive control).
Regimes: CLEAN + ARBITRARY + SHUFFLE (must-fail controls). All strata reported; NOVEL is the honest stratum.

## Arms (head-to-head)
- HERO: `LEARN_BILINEAR_RANK1` = shared learnable code + per-role rank-1 `P_i=I+u_i v_i^T` (u,v zero-init) + product.
- `LEARN_BILINEAR_RANK4` = rank-4 diagnostic (rank effect; REPORTED, NOT gated).
- `LEARN_SYM` = shared code + product (ELEMENTWISE P=Q=I baseline = PARITY specialist; HERO must MATCH on parity).
- `LEARN_INT` / `LEARN_ADD` = role-keyed product / sum (role-keyed; `max` = DOMINANCE specialist; HERO must MATCH on dom).
- INT_MATCH (algebra-matched construction; REAL FHRR bind), MONO (additive contrast).
- FREQ_NULL=max(HOMOPHILY_COND,POP), MEMORIZE, POP, ORACLE (ceiling).
- (joint-dual = REFERENCE only, cited from its landed metrics; NOT re-run here -- compute-proportionality.)

Fixed hyperparams (a priori, MATCH the prior VET-clean cell to avoid design-to-pass): EMB_D=48, EPOCHS=500,
LR=0.05, RANK1=1, RANK4=4, BIL_REG=1e-3 (modest weight-decay on the low-rank factors -> Occam bias toward the
P=I elementwise special case unless the data demands asymmetry).

## HARD-PASS / HARD-FAIL bands (fixed BEFORE run; all on NOVEL CLEAN, multi-seed mean; strict per META_RULE_L)
Let HERO=LEARN_BILINEAR_RANK1, SYM=LEARN_SYM, role_spec_dom=max(LEARN_INT,LEARN_ADD), FREQ=FREQ_NULL. TOL_SPEC=0.10.
- `parity_ok`    = HERO_par >= SYM_par - 0.10 AND HERO_par >= chance_p + 0.20 AND HERO_par - LADD_par >= 0.15
                   AND HERO_par - FREQ_par >= 0.15
- `dominance_ok` = HERO_dom >= role_spec_dom - 0.10 AND HERO_dom - FREQ_dom >= 0.10 AND HERO_dom - SYM_dom >= 0.15
- **HARD_PASS** `HARD_PASS_WALL_BROKEN_ONE_LEARNED_OP_DOES_BOTH` = parity_ok AND dominance_ok AND hero_mustfails_fire
  AND ceiling_ok. => a single learned low-rank bilinear op discovers BOTH -> commutativity wall broken.
- **HARD_FAIL** `HARD_FAIL_BILINEAR_IS_ANOTHER_SPECIALIST_{PARITY_ONLY|DOMINANCE_ONLY}` = exactly ONE of
  {parity_ok, dominance_ok}. The wall holds; the op is still a specialist.
- **HARD_FAIL** `HARD_FAIL_BILINEAR_TIES_ELEMENTWISE_NO_GAIN` = neither solved AND |HERO_dom - SYM_dom| < 0.05
  (no gain over elementwise -> the joint-code two-head design remains necessary).
- **HARD_FAIL** `HARD_FAIL_MUSTFAIL_BREACH_HERO_FITS_NOISE` = HERO beats FREQ_NULL by > 0.10 on ARBITRARY/SHUFFLE
  (fitting noise; invalidates all claims).
- **REFUTE** `REFUTE_IMPL_MATCHED_OP_CANNOT_SOLVE_ARENA` = INT_MATCH < 0.90 on parity or dominance (arena/impl broken).
- **MIDDLE_BAND** `MIDDLE_BAND_INCONCLUSIVE` = anything else (e.g. both fail but not a clean elementwise tie ->
  under-trained / inconclusive; needs regime nudge, not a wall verdict).

Honest note: the parity+dominance bars are demanding (HERO must roughly MATCH each specialist). That IS the
"breaks the wall" definition. The tension theory predicts HARD_FAIL (specialist-or-tie); a genuine minimal-upgrade
win predicts HARD_PASS. Both outcomes are informative; neither is assumed.

## Compute architecture
Class **(b) sequential-CPU with justification**. Each learned arm is a tiny Adam SGD fit (EMB_D=48, 500 epochs,
~120 train samples); the cell IS the substrate composition-op being validated (glass-box, bit-reproducible on CPU).
Per-fit wall << 10s; FULL = 5 seeds x 5 families x 3 regimes x 5 learned arms (~375 fits) estimated ~5-10 min total.
GPU transfer overhead would dominate at this scale; no batching benefit. Storage strategy: **no_storage /
no_composition** (no KGStore / bundling; a learned-readout arena). REAL substrate primitive exercised: `hdlab.binding.bind`
(FHRR complex elementwise, INT_MATCH construction + self-test homomorphism), long-stable signature `bind(a,b)`.

## SCHEMA-VET fields
- `arms_differ_verified`: smoke asserts MONO/LEARN_INT/LEARN_ADD/LEARN_SYM/HERO_R1/HERO_R4/HOM bit-distinct (7 sigs).
- `final_metrics_atomicity`: **tmp_replace** (metrics.json.tmp -> os.replace).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException; no bare except). Verified by static grep (NONE).
- `crlb_n/a`: "accuracy discriminator is a learned-SGD generalization gap, not a noise-floor estimation problem; no
  Cramer-Rao floor applies. Feasibility instead governed by specialist reproduction: SYM reaches parity ~0.98 and
  role-keyed reaches dominance ~1.0 at this arena (MEASURED@prior cells), so both PASS bars are physically attainable."
- `baseline_in_band`: FREQ_NULL not saturated (self-test asserts freq_p <= 0.75; chance_p ~0.52, chance_d ~0.63).
- `discriminator_survives_scale`: smoke runs at FULL arena params (K/L/N_ENT identical; option A), 2 seeds. Arena is
  small so smoke == full-scale discriminator. The wall-break gate is telemetry-sensitive: forcing P=I collapses HERO
  to SYM (fails dominance) -> gate moves.
- `discriminator_fires`: COMPETITION/discovery class -- must-fails (ARBITRARY/SHUFFLE) fire (HERO gap<=0.10);
  specialists behave (SYM discovers parity, role discovers dominance, SYM fails dominance) asserted in self-test.
- `cardinality_ok`: EXPECTED_N_UNITS/seed = 5 families x 3 regimes = 15; verdict counts n_units == 15*n_seeds.
- `calibration_check`: **default_ok_for_this_regime** (all hyperparams inherited a-priori from the VET-clean prior
  cell; BIL_REG fixed, not tuned-for-PASS).
- `deterministic_seeding`: true (FAM_IDX/REG_IDX integer-index seeds; torch manual_seed from int mode-keys; NO
  built-in-hash seeding; NO list(set()) ordering). Static scan CLEAN (queue_add PROT-023 auto-scan).
- `positive_control_arms`: INT_MATCH reproduces the algebra-matched construction AT THIS REGIME (>=0.90 gate =
  REFUTE_IMPL if it cannot) -- the arena-solvability positive control.
- `run_mode`: cell DEFAULTS to full on no-flag (runner invokes `python -u <script>`); metrics run_mode="full".
- `progress_logging`: **print_flush_true** (line_buffered stdout + per-seed flush log). timeout target < 1800s.

## Dispatch
Target queue: **remote_cpu_queue** (CPU cell, no GPU benefit; ALL COMPUTE REMOTE per USER lock). Timeout 1800s
(generous vs ~5-10 min estimate). Remote `--self-test` is the gate (asserts construction + machinery + arms-differ
+ must-fail fires; does NOT assert the open wall-break hypothesis). exp_dev authored + committed + static-verified;
orchestrator ships + owns post-ship REMOTE VERIFY.
