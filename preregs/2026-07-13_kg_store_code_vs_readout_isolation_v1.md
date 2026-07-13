# Pre-registration: CODE-vs-READOUT isolation of the native-vs-additive ORACLE-CEILING gap (2x2 factorial)

- **Cell:** `experiments/exp_kg_store_code_vs_readout_isolation_v1.py`
- **Anchor name:** `kg_store_code_vs_readout_isolation_v1`
- **Metrics path:** `data/exp_kg_store_code_vs_readout_isolation_v1/metrics.json`
- **Filed:** 2026-07-13 (exp_dev). **Target queue:** `overnight_queue` (GPU) -- see Routing deviation.
- **Source of design:** task hand-off (decompose the ~6x native-vs-additive oracle-ceiling gap into CODE QUALITY vs READOUT) +
  `notes/research_native_representational_ceiling_levers_2026-07-13.md`.

## Routing deviation (REMOTE-CPU -> GPU; load-bearing, flagged for orchestrator)
The hand-off specified `remote_cpu` on the premise "no SGD beyond the existing additive fit, which is reused/loadable."
**That premise is FALSE on disk:** `data/exp_anchor_compose_inductive_entity_cskg_v1/` retains ONLY `metrics.json` (40KB);
the fit checkpoints / X,D coords were NOT persisted (verified: no `*.pt`, no ckpt dir). The additive coords therefore must be
**re-fit** (k=24, epochs=500, n_neg=128 minibatch-SGD -- the anchor_compose FULL config VERBATIM). That is the exact
matmul-heavy SGD workload anchor_compose ran on GPU (gpu1024); on CPU it is multi-hour x2 fits x3 seeds. Per GPU-batching-
mandatory-when-speedup-available, this routes to `overnight_queue`. The NATIVE store (one-shot Hebbian) + bridge + all
direct-distance scorings run on CPU tensors within the same cell (device=auto -> cuda for the fit, cpu for the native path).

## Prior-work check (mandatory)
`bash tools/substrate_query.sh "native store code quality versus readout bilinear Hebbian additive TransE ceiling entity"`
-> top hit cosine **0.3145** (entity `native`, a wordnet/atoms lexical node, spurious); 2nd/3rd `relative quantity` 0.307
(spurious); 4th `additive identity` 0.291; 5th a MATH GSBC atom 0.284 (different arc). **Prior-work check: NONE at
cosine>0.30 relevant to this 2x2 code-vs-readout isolation.** Genuinely novel: prior cells measured the two ceilings
SEPARATELY (native 0.023 in native_bind_compose; additive 0.137 in anchor_compose) and tested the WRITE-RULE factor
(kg_store_write_rule_decorrelated_ceiling_v1 = HARD_FAIL, closed); NO prior cell CROSSES {code source} x {readout} to
attribute the gap. Not a rediscovery.

## Question
Decompose the measured ~5.9x ORACLE-ceiling gap (native 0.023083 vs additive 0.137293) into its two un-separated factors --
CODE QUALITY (random-bipolar vs learned k=24 TransE) and READOUT MATH (bilinear-Hebbian E@(W@key) vs direct-distance
-||X_h+D_r-X_t||) -- via a 2x2 factorial measuring the ORACLE ceiling under each cell. WRITE-RULE factor is CLOSED (not
varied); DIMENSION is swept separately (kg_store_dim_scaling_ceiling_v1). Outcome = a clean ATTRIBUTION (CODES / READOUT /
BOTH), each with a pre-registered rise/flat band. Not pass/fail.

## The 2x2 (all arms PAIRED on the SAME held-out QUERY edges; filtered MRR-vs-all-N; same split/arena/controls as the two source cells)
```
NN_ORACLE = native codes  x native readout   : random-bipolar E/R + bilinear-Hebbian, hold folded into W. REPRODUCE 0.023.
AN_ORACLE = additive codes x native readout   : learned ORACLE coords (Xo,Do) BRIDGED to n_dim (linear proj), as the store's
             E/R; hold folded into W; native bilinear readback.  THE NOVEL ARM.
             RISES toward 0.137 => CODES were the native limiter. FLAT ~0.02 (BF confirms codes ARE good) => READOUT caps it.
NA_ORACLE = native codes  x additive readout  : direct-distance on the SAME random-bipolar codes. RISES => READOUT was limiter;
             FLAT ~floor => CODES cap it (random codes carry no additive geometry). Predicted floor.
AA_ORACLE = additive codes x additive readout  : direct-distance on learned oracle coords (Xo,Do). REPRODUCE 0.137.
```

## Bridge (autonomy; glass-box, ZERO SGD) + bridge-fidelity control (removes the confound)
FIXED random LINEAR projection `P ~ N(0, 1/n_dim)`, shape `(k, n_dim)`, deterministic per seed. `E_add = Xo @ P`,
`R_add = Do @ P` (dense real, n_dim), single global RMS scalar (rank-invariant). **LINEAR => additive translation
structure survives** (`E_add[h]+R_add[r] = (Xo[h]+Do[r])@P ~= Xo[t]@P = E_add[t]`, JL). A sign/bipolar bridge would
DESTROY additivity (sign nonlinear) and confound a FLAT AN_ORACLE. **Confound removed by a BRIDGE-FIDELITY control:**
`BF_ADD = additive_direct_scores(E_add, R_add)` MUST reproduce ~AA_ORACLE (projection preserved the geometry). If BF_ADD is
high but AN_ORACLE is flat, the native READOUT is DEFINITIVELY the limiter, not a broken bridge. KGStore is NOT modified --
E/R are overwritten on a LOCAL cell-owned instance only (same defaulted-off discipline as the write-rule cell); the
native readout / compose / controls are reused from `exp_native_bind_compose_inductive_entity_cskg_v1` VERBATIM.

## Arms
2x2 headline (NN/AN/NA/AA_ORACLE) + BF_ADD (bridge fidelity) + AA_COMPOSE (additive realized, positive control ~0.128) +
NN_COMPOSE (native realized context ~0.014) + RANDOM (native-readout null) + NATIVE_SCRAMBLE / IDENTITY_SHUFFLE (native-readout
must-fails, reused VERBATIM) + BASELINE_POP. 11 arms, all scored PAIRED per seed.

## Pre-registered attribution bands (picked BEFORE the run; primary = filtered MRR oracle cells; G = AA_ORACLE - NN_ORACLE ~= 0.114)
- **Gate POS-CONTROLS** (else `INCONCLUSIVE_POSCONTROL_OR_BRIDGE_FAILED`): `|NN_ORACLE - 0.023083| <= 0.008` AND
  `|AA_ORACLE - 0.137293| <= 0.030` AND `RANDOM <= 0.004` AND native scramble/idshuf controlled (`(scr-rnd) <= 0.20*G`,
  same idshuf) AND `BF_ADD >= 0.50*AA_ORACLE` (bridge fidelity) AND both additive fits + all W finite AND G>0.
- **CODES_ARE_THE_LIMITER**: `(AN_ORACLE - NN_ORACLE) >= 0.50*G` (native readout carries the additive magnitude given good
  codes -> CODES were the native path's dominant limiter; glass-box code-family is the next lever).
- **READOUT_IS_THE_LIMITER**: `(AN_ORACLE - NN_ORACLE) <= 0.20*G` with BF_ADD proving the codes ARE good -> the bilinear-
  Hebbian READOUT FORMAT caps it (nativize needs a readout change). `_NA_CONFIRMS` variant if NA_ORACLE also rises.
- **BOTH_CODES_AND_READOUT_CONTRIBUTE**: `0.20*G < (AN_ORACLE - NN_ORACLE) < 0.50*G` (30%-of-G dead-band), OR NA_ORACLE rises
  (`(NA_ORACLE - RANDOM) > 0.20*G` -> the readout swap alone lifts even native codes).
- **NA read-out** (reported): predicted `(NA_ORACLE - RANDOM) <= 0.20*G` (direct-distance alone does NOT rescue random codes
  -> the additive advantage is a CO-DESIGNED codes+readout package, not a bolt-on readout).

MEASURED / CITED anchors:
- NN_ORACLE target 0.023083  MEASURED@data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_FOLDIN
- AA_ORACLE target 0.137293  MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_ADDITIVE
- AA_COMPOSE target 0.12821  MEASURED@ same anchor_compose path :ANCHOR_COMPOSE ; NN_COMPOSE 0.013969 MEASURED@ native path

## Compute architecture
class (c) MIXED. Additive fits (Xa/Da + Xo/Do oracle) = minibatch SGD (k=24, epochs=500, n_neg=128) -> GPU-batched
(overnight_queue). Native store (one-shot Hebbian ingest, bilinear readout) + linear bridge + direct-distance scorings +
split/POP = CPU tensors (cheap; the base cell's own CPU path). 2 fits/seed x 3 seeds. No mutation of KGStore / persisted
store; fit checkpoints cell-owned + resumable (`_fit_ckpts/`). Wall estimate < ~90min on GPU.
storage_strategy: no_composition (matrix store + geometric coords; no bundled-vs-sharded axis; E/R untouched).

## SCHEMA-VET fields
- `arms_differ_verified: true` (11 arms produce >=5 distinct sigs/seed asserted; self-test n_distinct_sigs=11; META_RULE_AF)
- `final_metrics_atomicity: "tmp_replace"` (write_metrics + os.replace)
- `cardinality_ok: true`; `EXPECTED_N_UNITS = n_seeds = 3`; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if short
- `crlb_n/a: "primary is a FRACTION-OF-THE-MEASURED-GAP attribution (AN-NN)/(AA-NN); bands are fractions of the in-run measured gap G, not absolute thresholds"`
- `discriminator_reachability: true` (bands scale to whatever G the FULL measures; NN+AA positive controls must reproduce landed)
- `baseline_in_band: true` (NN reproduces 0.023 AND AA reproduces 0.137 as positive controls; RANDOM near 1/N floor; BF proves bridge before AN interpreted)
- `calibration_check: "default_ok_for_this_regime"` (all fracs/tols pre-registered, NOT tuned on real data; additive config copied VERBATIM from confirmed anchor_compose FULL)
- `discriminator_survives_scale: analytical + self-test` (the FULL runs at the EXACT regimes that MEASURED 0.023 and 0.137;
  the self-test native code-sensitivity probe fires at the INTERFERENCE load M=2n -- matching real N>>n_dim -- rand-code oracle 1.0 vs correlated-code oracle 0.726, margin 0.274)
- `positive_control_arms:` NN_ORACLE reproduces 0.023083+-0.008 AND AA_ORACLE reproduces 0.137293+-0.030 at FULL config; BF_ADD reproduces ~AA_ORACLE (bridge)
- `effective_vs_nominal_parameter_audit: ALIGNED` (no swept axis; fixed n_dim=1024/k=24; the 2x2 is a code/readout crossing, not a parameter sweep)
- `bracket_includes_discriminating_band: n/a` (attribution, not a sweep; the two novel cells AN/NA land between the measured NN=0.023 and AA=0.137 endpoints by construction)
- `composition_edges:` bridge edge Xo(k) -> E_add(n_dim) = LINEAR projection SHAPE_MATCH (additivity-preserving; BF control verifies)
- `per_unit_failure_class: true` (no bare except; per-seed failure_class recorded)
- `start_marker_written / crash_diagnostic_present / heartbeat_present: true`; `cell_chunked: false` (3 seeds in one cell, per-seed write_partial; GPU SGD cell)
- `progress_logging: "print_flush_true"` (line-buffered stdout + per-seed/per-fit flush prints + heartbeat + fit ckpt progress; timeout >= 1800)
- `run_mode_default: full` (argparse default run-mode=full; --self-test explicit; post-dispatch RUN_MODE verification required)
- `functional_requirements:` (1) attribute the 6x gap to CODES vs READOUT -> the 2x2 crossing; (2) keep the bridge honest ->
  linear projection + BF-fidelity control removes the additive->multiplicative confound; (3) reproduce both endpoints ->
  NN=0.023 + AA=0.137 positive-control gates; (4) not regress CERT-584/585 -> KGStore untouched, E/R overwritten on a local instance only.

## Four validity-preflight checks (declared in the self-test)
1. positive_control_passes: additive readout recovers planted TransE (learned>>random) AND native ORACLE recovers the planted native arena.
2. metric_moves: the four 2x2 oracle cells MOVE across the synthetic arenas.
3. negative_control_margin: RANDOM + native-codes-under-additive-readout + native-scramble sit below the learned-additive arm by margin (>=3 controls).
4. full_gates_exercised: the attribution verdict fires every gate at self-test scale.

## Self-test result (MEASURED, local .venv, run_mode=self_test, n_dim=256 / k=8 / epochs=150)
- native planted arena: ORACLE 0.763 fires vs RANDOM 0.051; native 0.266 - scramble 0.095 = 0.171 and native - idshuf 0.217 = 0.049 (must-fails FIRE >= 0.03).
- native code-sensitivity (interference load M=2n): random-code oracle 1.0 vs correlated-code oracle 0.726 (margin 0.274 >= 0.02 -> native readout RESPONDS to code quality; apparatus not frozen).
- planted TransE arena: AA(learned)=0.465 >> RANDOM; BF(bridge fidelity)=0.489 ~= AA (linear bridge preserved additive geometry); NA(random codes, additive readout)=0.0186 at floor; AN(bridged codes, native readout)=0.169; n_distinct_sigs=11; fits finite.
- `SELFTEST_PASS`, validity_preflight_ok=True (3.4s).

## Dispatch (hand to orchestrator; exp_dev cannot SCP/push -- overnight_queue is SCP+SSH to marsh@home, GPU)
`bash tools/orchestrator/queue_add.sh overnight_queue kg_store_code_vs_readout_isolation_v1 experiments/exp_kg_store_code_vs_readout_isolation_v1.py preregs/2026-07-13_kg_store_code_vs_readout_isolation_v1.md 10800`

## Post-ship REMOTE VERIFY (orchestrator)
Confirm `data/exp_kg_store_code_vs_readout_isolation_v1/metrics.json` lands with `run_mode == "full"` (NOT self_test -- a
sibling cell recently mis-completed as selftest), `n_seeds == 3`, size >> 5KB, and `gates.oracle_2x2_mrr` populated.
