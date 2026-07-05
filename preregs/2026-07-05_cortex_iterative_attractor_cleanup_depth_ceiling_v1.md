# Pre-registration: cortex_iterative_attractor_cleanup_depth_ceiling_v1

ENVELOPE-PUSH on the proven regenerative-cleanup reasoning (v2 = CHAIN_GRADE:
single-shot argmax per-hop cleanup; regen beats analog; faith 1.0; depth-5 fidelity
~0.69-0.74). v2 measured the depth curve only to D=7, so "usable depth ~9-10 hops"
was EXTRAPOLATION. Recorded next lever: ITERATIVE / RESONATOR per-hop cleanup (run the
cleanup attractor to CONVERGENCE, CA3 recurrent-attractor analog) should push usable
depth further and raise fidelity at depth. This cell tests that lever HONESTLY and
measures the TRUE deep ceiling. Constructive build over our own memory (USER 2026-07-05);
no vs-LLM, no GPU, CPU vector algebra.

- Cell: `experiments/exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1.py`
- Anchor: `cortex_iterative_attractor_cleanup_depth_ceiling_v1`
- Predecessor (reused scaffold): `exp_cortex_regenerative_cleanup_vs_analog_accumulate_v2.py`
  FULL HARD_PASS (`data/exp_cortex_regenerative_cleanup_vs_analog_accumulate_v2/metrics.json`).
- Prior-work check (substrate concept-query "iterative resonator cleanup regenerative
  deep reasoning chain per-hop attractor convergence depth ceiling"): top hit
  cosine=0.3682 "Resonator / iterative decoding" (`notes/wave14e_hierarchical_composition_research.md`
  sec 6.3) -- a HYPOTHESIS that resonator iterative decode "could improve recovery 5-10%"
  in the HIERARCHICAL bundle-chunking regime, NOT the deep sequential-CHAIN reasoning
  regime here. Second hit cosine=0.3301 resonator-generative (different application).
  Genuinely novel for the chain-reasoning regime; NOT a rediscovery.

## Two deliverables (the second SURVIVES the predicted tie)
1. PRIMARY (load-bearing): usable_depth(ITERATIVE attractor cleanup) vs usable_depth
   (SINGLE-SHOT argmax cleanup), PAIRED on identical chains+store+seed, DEEPER than
   v2 (D_MAX=14 vs 7). Does iterating the cleanup to convergence EXTEND usable depth?
2. FIRST-CLASS (survives the tie): the CAPACITY LAW -- single-shot usable-depth vs
   store-capacity (N_TEST) -- the true deep ceiling v2 never measured, and its
   N-independence (the collision-limited ceiling should be ~flat in N).

## PRE-FLIGHT (MEASURED before finalizing; exp_dev 2026-07-05) -- axis correction
Direct simulation reusing v2's primitives (efficient indices store), N=8192, V=512, P=8:
- FALSIFIED the naive "crosstalk sets the depth ceiling" model. At M/N=3, collision-free
  (N_TEST=6): single-shot is PERFECT to depth 8+. THEORETICAL: background argmax
  separation z = target_proj / distractor_noise ~ N / sqrt(M) ~ 8192/157 ~ 52 sigma;
  breaking argmax by background crosstalk needs M ~ (N/3.5)^2 ~ 5.5e6 (M/N ~ 668),
  absurd. So background M/N is NOT the limiter. MEASURED (pre-flight).
- The GENUINE limiter is chain-key COLLISION (store key-capacity): N_TEST chains store
  N_TEST*D_MAX (source,rel)->object edges over only V_CHAIN*P_REL = 256*8 = 2048 distinct
  key slots; higher fill -> ambiguous keys carrying multiple objects -> degraded
  retrieval, INDEPENDENT of N. MEASURED @ N=8192, M/N=1.0: N_TEST 10/25/50 -> usable_ss
  14/8/5. So M/N is FIXED (1.0) and N_TEST is SWEPT as the store-capacity difficulty.
- CORRECTLY-TUNED modern-Hopfield attractor cleanup (beta {20,40,80}, T=5): depth curve
  BIT-IDENTICAL to single-shot argmax (max_abs_gap=0.000 at N_TEST 10/25/50). MEASURED.
- THEORY (THEORETICAL@modern-Hopfield/Ramsauer 2020; CITED@Kent-Frady 2020 resonator):
  for a near-orthogonal random bipolar codebook, softmax re-weighting preserves the
  projection RANKING, so the attractor converges to the argmax MAP decoder; single
  argmax is already Bayes-optimal for "nearest stored atom." A collided key is a genuine
  superposition of >=2 stored objects -- NO cleanup (single-shot or iterative) can pick
  the "right" one, because both are legitimately stored. A first attractor impl at beta=8
  COLLAPSED (softmax could not concentrate vs V=512 -> uniform fixed point) -- a
  parameter artifact; corrected to beta=12 with self-test T_attr asserting attractor@
  beta=60 == argmax (correct generalization).
=> PREDICTION: HARD_FAIL on the extension hypothesis (iterative TIES single-shot). The
   contract's explicitly-anticipated valid outcome ("the one-shot snap was already
   optimal"). CLOSES the "iterate the cleanup" lever; the real levers for deeper chains
   are MORE KEY SLOTS (richer relation/node vocabulary V_CHAIN*P) and sharded storage,
   NOT iteration and NOT bigger N (collision is N-independent).

## SMOKE (MEASURED, this cell, N=8192, N_TEST=25, D=12, fill=0.15)
- seed7: usable_ss=10 usable_it=10 delta=0 (d1=0.84, in band); ctl=0; faith=1.000;
  max_abs_gap=0.040 -> HARD_FAIL (tie). seed17: usable_ss=7 usable_it=7 delta=0
  (d1=0.96); ctl=0; faith=1.000; max_abs_gap=0.000 (bit-identical) -> HARD_FAIL (tie).
  MEASURED@data/exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1_smoke/metrics.json.
  Single-shot IN BAND (degrading through 0.5), control at chance, iterative TIES -> the
  discriminator FIRES and the tie is decisive at a fair, non-vacuous operating point.

## Arms (3; paired on same chains + same store + same seed; META_RULE_AF)
- ARM_SINGLE_SHOT (baseline): x_{k+1} = E[argmax_v <E[v], yhat_k>] (v2 regen; MAP; T=1).
- ARM_ITERATIVE (mechanism, best fair shot): modern-Hopfield / CA3 recurrent attractor
  cleanup, z_{t+1} = softmax(beta*cos(z,E)) @ E (renormalized), T=6 iters at beta=12,
  then snap. FIXED principled beta/T (self-test asserts attractor@beta=60 == argmax).
- ARM_SHUFFLED_CTL (discriminator-fires / broken rail): iterative attractor over SAME
  edges with objects label-shuffled -> fidelity ~ chance (1/V), usable_depth ~ 0.

## Config
- N_LIST full = [8192, 16384] (N-independence check; 32768 dropped -- ~16 min/unit and
  the collision-limited ceiling is N-independent, so it adds cost not signal); smoke = [8192].
- V=512, P=8, V_CHAIN=256, KEY_SLOTS = V_CHAIN*P = 2048.
- MOVERN_FIXED = 1.0 (background is NOT the limiter; held constant).
- DIFFICULTY axis NTEST_TARGETS full = [15, 25, 40] (fill 10%/17%/27% -> ud ~12/8/5,
  single-shot IN BAND with headroom); smoke = [25]; self_test = [6, 12].
- D_MAX full = 14 (DEEPER than v2's 7); smoke = 12; DEPTHS = 1..D_MAX.
- BETA_ITER = 12.0, T_ITER = 6 (FIXED). BETA_HIGH = 60.0 (self-test only).
- Seeds full = [7,17,23,31,41]; smoke = [7,17,23].
- USABLE_FLOOR = 0.50 (contract); secondary 0.30. usable_depth(arm) = largest d s.t.
  fidelity(1..d) ALL >= FLOOR (contiguous-from-1; robust to a lucky deep point).
- Chain-key fill = N_TEST*D_MAX / KEY_SLOTS (the store-capacity difficulty knob).

## Bands (PASS band + FAIL band pre-registered)
FAIR op-point (per N,seed) = a swept N_TEST where single_shot IN BAND: usable_ss in
[SS_BAND_LO=2, D_MAX-1] AND d1 sanity (ss_d1 >= 0.80 AND it_d1 >= 0.80). disc point =
fair point maximizing delta_usable = usable_it - usable_ss.
- HARD_PASS (ALL): delta_usable >= 2 (real >=2-hop extension); mean per-depth gap over
  crossover band (ss in [0.30,0.70]) >= 0.05; control usable_depth <= 1; iterative
  faithfulness >= 0.95; single_shot IN BAND; arms_differ; isolation_clean. AND cross-seed
  stable: ALL seeds at that N agree delta_usable >= 2.
- HARD_FAIL: at a fair op-point delta_usable <= 0 (iterative TIES or LOSES single-shot);
  OR the CENSORED-TIE case (single_shot deep/never-collapsed within D_MAX but iterative
  bit-identical, max_abs_gap < 0.05). [PREDICTED.]
- HARD_FAIL_CTL: control usable_depth > 1 (broken rail recovers structure).
- ITERATE_REGIME: no fair op-point AND not a censored-tie (needs higher N_TEST / deeper D).
- MIDDLE_BAND: 0 < delta_usable < 2, OR extends but cross-seed unstable, OR all-N ITERATE.
REPORTED (first-class, survives the tie): CAPACITY LAW (usable-depth vs N_TEST, aggregated
over seeds+N), usable-depth-vs-N (N-independence), full per-depth curves all arms, gap
curve, decisive_tie_audit (global max_abs_gap, max_delta_usable), faith, secondary floor.

Aggregate: cell HARD_PASS iff >=1 N-tier majority-HARD_PASS AND all seeds extend AND no
HARD_FAIL_CTL. Cell HARD_FAIL iff MAJORITY of N-tiers HARD_FAIL (tie everywhere = lever
CLOSED; first-class result = the capacity law + N-independence). All-N ITERATE -> MIDDLE.

## Falsifiable predictions
- HARD_FAIL (expected): at every N a fair op-point (single_shot in band) exists and
  iterative TIES it (delta_usable <= 0; global max_abs_gap < 0.05). Capacity law:
  usable-depth DECREASES with N_TEST (more collision); ~N-independent across {8192,16384}.
- HARD_PASS (would surprise the theory): iterative extends usable depth by >=2 hops,
  cross-seed stable, control at chance -- reported loudly if it happens.
- Report asks regardless: (a) the capacity law (usable-depth vs N_TEST); (b) is the
  ceiling N-independent? (c) control at chance; (d) faith ~1.0.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds * len(N_LIST) * len(NTEST_TARGETS)
  (full = 5*2*3 = 30); verdict counts units, emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- arms_differ_verified: True (sha256 of 3 arms' D_MAX preds; self-test T3). NOTE +
  arms_differ_exempted: single_shot vs iterative MAY be bit-identical at an exact tie
  (attractor converges to argmax; smoke seed17 max_abs_gap=0.000) -- the SCIENTIFIC
  RESULT, not a bug; control always differs (walk verified live) and self-test T_attr
  proves distinct code paths. HARD_FAIL (tie) does NOT require arms_differ; only HARD_PASS.
  Exempted pair: (ARM_SINGLE_SHOT, ARM_ITERATIVE) when delta_usable<=0.
- final_metrics_atomicity: tmp_replace (metrics.json.tmp -> os.replace).
- except-ordering: `except SystemExit: raise` / `except KeyboardInterrupt: raise` BEFORE
  `except Exception` (no BaseException, no bare except; grep-gate clean).
- crlb / discriminator_reachability: True. Discriminator = delta_usable (integer hops).
  Reachable: single_shot depth curve MEASURED spans ~0.96 -> chance as N_TEST grows
  (ud 14/8/5 at N_TEST 10/25/50) so the discriminating band [0.30,0.70] is richly
  populated and iterative has full headroom. crlb_formula_reference: chain-key fill =
  N_TEST*D_MAX/KEY_SLOTS sets the ambiguous-key fraction; cleanup method cannot resolve a
  genuinely-collided key, so the HARD_FAIL is the physics-predicted outcome.
- baseline_in_band (META_RULE_AG): the disc op-point REQUIRES single_shot usable_depth in
  [2, D_MAX-1] AND ss_d1>=0.80. N_TEST=25 is the MEASURED in-band point (smoke ud 7-10).
- calibration_check: default_ok_for_this_regime. Attractor beta=12/T=6 FIXED principled
  (soft best-shot), NOT tuned-for-PASS; self-test T_attr asserts attractor@beta=60==argmax.
- progress_logging: line_buffered_stdout + print(flush=True) per line (timeout_s >= 1800).
- defensive_error_checking: passed_all_4_patterns (start_marker + crash_diagnostic
  CELL_CRASHED metrics + heartbeat _heartbeat.jsonl + no silent except).
- cell_chunked: false (seeds looped with per-seed write_partial + resumable_seeds).
- HP_SCOPE: {ARM_ITERATIVE: [delta_usable>=2, mean_gap_cross>=0.05, faith>=0.95];
  ARM_SHUFFLED_CTL: [usable_ctl<=1]; ARM_SINGLE_SHOT (baseline): [in-band usable_ss in
  [2,D_MAX-1], d1>=0.80]}. Extension gates apply ONLY to iterative vs paired single_shot.

## Gate A-E (sweep/composition; per exp_dev.md section 15)
- A effective-vs-nominal: swept param = N_TEST. effective difficulty each primitive sees
  = chain-key fill = N_TEST*D_MAX/KEY_SLOTS (monotone in N_TEST, not constant).
  sweep_alignment_verdict: ALIGNED.
- B discriminating-band: single_shot ud spans 14/8/5 across N_TEST 10/25/50 (pre-flight);
  the swept fill {0.10,0.17,0.27} brackets ud {~12,8,5}, all in the discriminating band
  (single_shot degrading through 0.5). discriminating_fraction ~1.0 (>=0.30).
- C shape-compat: single primitive (retrieve + cleanup) self-composed across depth (atom
  -> atom, shape-preserved). composition_edges: SHAPE_MATCH (self-composition).
- D positive-control (reproduce prior CG at test regime): ARM_SINGLE_SHOT at N=8192, V=512,
  P=8 (v2's regime) reproduces v2's regenerative depth behavior: ss_d1>=0.80 (smoke 0.84-0.96),
  graceful decay, mean ss_d5 in [0.40,0.95]. cited_prior_metric: v2 regen_d5 ~0.69-0.74
  CITED@data/exp_cortex_regenerative_cleanup_vs_analog_accumulate_v2/metrics.json. Reported in
  metrics.extra.positive_control_v2_reproduce. regime_extension_audit: SAME V=512/P=8; D_MAX
  7->14, N_TEST/collision-controlled -- documented drift (qualitative repro, not bit-repro).
- E functional-requirements:
  * "retrieve one relational hop from a bundled store" -> associative retrieve (Hebbian).
  * "keep a chain accurate across depth despite store-capacity pressure" -> per-hop
    regenerative cleanup; single-shot argmax (MAP) vs iterative attractor (run-to-convergence).
  * "prove the answer is mechanically traceable" -> faithfulness replay (>=0.95 gate).
  * "confirm the discriminator is not an artifact" -> shuffled-object control (chance floor).

## Dispatch
- Smoke: LOCAL only (USER-LOCKED smoke-only-local). N=8192, N_TEST=25, 3 seeds, in-band.
  Wall MEASURED 127s (fits the queue_add 180s default gate cap; no override needed).
- FULL: remote_cpu_queue (CPU; SEQUENCE-DEPENDENT + substrate-primitive exemptions).
  Wall est ~45-90 min (N=16384 x N_TEST=40 tier dominates). Timeout: 10800 s (3 h;
  PROT-019 n>=4096 -> timeout>=3600 satisfied). exp_dev CANNOT push -> Director routes to
  hdi_orchestrator for queue_add. POST-SHIP REMOTE VERIFY.

Author: exp_dev, 2026-07-05.
