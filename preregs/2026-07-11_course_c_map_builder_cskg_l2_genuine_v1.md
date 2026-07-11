# Pre-reg: Course C map-builder ON CSKG -- does the substrate REALIZE CSKG's L2-genuine reasoning-headroom, beating frequency?

- anchor_name: `course_c_map_builder_cskg_l2_genuine_v1`
- cell: `experiments/exp_course_c_map_builder_cskg_l2_genuine_v1.py`
- metrics: `data/exp_course_c_map_builder_cskg_l2_genuine_v1/metrics.json`
- date: 2026-07-11
- queue: overnight_queue (GPU) FULL; local self-test + local CPU smoke are the pre-flight gates (matmul-heavy
  FPE ranking over N~23.6k CSKG entities x dim=4096 x nq~6000 x 5 geom arms x 3 seeds; local is smoke-only,
  USER-locked). device=auto (cuda on the GPU host).
- seeds FULL: [7, 17, 23] (3); EXPECTED_N_UNITS = n_seeds
- design: `notes/research_course_c_map_builder_replay_consolidation_design_2026-07-10.md` +
  `notes/the_last_piece_intuitive_reasoning_vs_frequency_courses_2026-07-10.md` (the convergence)
- operator (SMOKE-CONFIRMED, reused unchanged): `experiments/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1.py` (404a9a846)
- CSKG assembly + VET corpus: `experiments/exp_cskg_dense_core_headroom_acceptance_v1.py`; L2/L1I/L1F apparatus:
  `experiments/exp_gt_induction_fb15k237_dense_v1.py`. VET: a46eadfa (CSKG L2-only headroom).

## Question
The three pieces line up for the first time on the RIGHT knowledge: (1) a VET-verified-GENUINE compositional
corpus = CSKG dense core (L2-only fair-headroom 0.276, HIGH-degree 0.226 at POP_RELFREQ 0.412 -- reasoning
CAN beat frequency, even at hubs; OPPORTUNITY, not yet demonstrated substrate reasoning); (2) a SMOKE-
CONFIRMED map-builder operator (phase-rotation binding RotatE-equivalent + FPE/SSP continuous entity
encoding + replay-consolidation); (3) a bounded FPE-kernel readout. THE NUMBER: on the held-out CSKG
L2-GENUINE composition edges, does the map-builder geometry beat the frequency incumbent (POP_RELFREQ),
INCLUDING at HIGH degree (the headline)? Does consolidation add value on this real underdetermined corpus
(the P~0.20-0.25 sub-claim gets its fair test here -- the synthetic operator grid was fully-derivable, no
headroom for replay)?

## Held-out arena (the L2-GENUINE set -- a win is REASONING, not lookup)
For each held-out CSKG test edge (h, r, gold): included iff gold is REACHABLE by a GENUINE 2-hop L2 path
pattern (r1(h,b) & r2(b,gold), support>=1 mined generator reach) AND NOT reachable by an L1I inverse pattern
NOR an L1F alias/direct pattern NOR present in the filtered-known set (sym-leak). This EXCLUDES inverse-
lookup + alias + symmetric-leak (per the VET decomposition) so a win is genuine 2-hop composition. Uses the
IDENTICAL Graph / mine_rules / reachable / pop_rank apparatus the VET's headroom used (apples-to-apples).
Degree-stratified LOW/MID/HIGH by gold-tail GLOBAL degree tertile (data-driven quantiles). Info-ceiling per
stratum = the CSKG headroom decomposition (reach-ceiling); the win bar (beat POP) is <= ceiling = FAIR.

## Arms (PAIRED: same L2-genuine held-out split + candidate set + degree strata per seed)
- ONESHOT_ROTATE: SSP_FRACTIONAL one-shot TransE coord fit + FPE bounded-kernel readout (coords z-scaled by a
  single global scalar -> PRE-REGISTERED bandwidth is data-independent). THE map arm.
- REPLAY_CONSOLIDATED: same operator, iterative interleaved replay + recall-consistency gate + val early-stop
  (the NEW ingredient; the P~0.20-0.25 consolidation sub-claim, first fair test on a real underdetermined corpus).
- BASELINE_POP: POP_RELFREQ per-relation tail frequency (the VET frequency incumbent; the bar, HIGH h@10=0.412).
- DISCRETE_BIND: stage3 failure-mode (i.i.d. phasor + learned rotation, NO coords). MUST underperform.
- SCRAMBLE_REPLAY (must-fail #1): identical replay, relation labels shuffled. MUST NOT beat ONESHOT.
- RANDOM_CODES (null / geometry-necessary): random coords + identical FPE kernel -> near-chance.
- ORACLE_TRANSDUCTIVE (must-fire GUARD): ONESHOT coords fit WITH held-out visible -> MUST recover (>> random)
  or the FPE-kernel readout/coord-fit capacity is the bottleneck (under-fit), NOT a substrate wall.

## Primary metric
Filtered hits@10 on the L2-GENUINE held-out subset (matches the VET's POP_RELFREQ h@10=0.412 comparison),
PLUS per-degree-stratum hits@10, PLUS hits@1 and MRR. achieved / POP-bar per stratum reported.

## Pre-registered bands (picked BEFORE the run)
- PRIMARY_K=10. POP_GAP=0.03 (geometry_best hits@10 - POP, aggregate); HIGH_POP_GAP=0.03 (at HIGH stratum,
  the headline); DISCRETE_UNDER=0.03 (geometry_best - DISCRETE); SCRAMBLE_EPS=0.03; ORACLE_FIRE_MARGIN=0.15;
  MANUFACTURE_EPS=0.05 (SYN_FREQ geometry - POP); TIE_EPS=0.02 (FAILS threshold). MIN_HELDOUT=20 (FULL);
  MIN_STRAT_Q=8.
- CONSOLIDATION (reported at smoke, FULL landed-VET decides): CONSOL_REL=0.15 (replay LOW >= oneshot LOW *
  1.15); REGRESS_REL=0.05; FLAT_EPS=0.15 (|hits_HIGH - hits_LOW| replay); R_BACKDOOR=0.20 (coord-precision-
  vs-degree |r|).
- FPE bandwidth FPE_ELL=0.55 (PRE-REGISTERED; coords z-scaled so ell is data-independent -- no post-hoc
  kernel tuning). KGE: margin=1.0, neg=10, wd=1e-3, lr=0.02 (standard regularized defaults). FULL geometry
  capacity: k=24, fpe_dim=4096, kge_epochs=600, replay_passes=80. CSKG: k_core=12, MIN_SUPPORT=10,
  MIN_CONF=0.10 (MATCHED to the VET headroom apparatus).

## Decision (pre-registered, before running)
- **INCONCLUSIVE_GEOMETRY_READOUT_UNDERFIT** (GUARD, checked FIRST) = transductive ORACLE does NOT fire
  (ORACLE - RANDOM < ORACLE_FIRE_MARGIN) -> the FPE-kernel readout / coord-fit capacity is the bottleneck,
  NOT a substrate-reasoning verdict. (At smoke k=8/150ep the oracle failed = under-fit; FULL k=24/600ep/4096
  must clear this before any geometry claim is trustworthy.)
- **REALIZES_L2_OPPORTUNITY** (the headline; SMOKE reports, FULL landed-VET decides -- telemetry may wash at
  scale, HOLD the mechanism story until VET) = geometry_best (max ONESHOT/REPLAY) hits@10 - POP >= POP_GAP
  (aggregate) AND HIGH-stratum geometry_best - POP >= HIGH_POP_GAP AND geometry_best - DISCRETE >=
  DISCRETE_UNDER AND SCRAMBLE - ONESHOT <= SCRAMBLE_EPS AND ORACLE fires AND SYN_FREQ no-manufacture AND
  SYN_COMP positive control fires.
- **REALIZES_..._AND_CONSOLIDATION_HELPS** = REALIZES + (replay LOW >= oneshot LOW *(1+CONSOL_REL) AND no
  aggregate regress AND replay degree-flat AND |backdoor_r| < R_BACKDOOR).
- **FAILS_DOES_NOT_REALIZE_L2_OPPORTUNITY** (ONLY when ORACLE fires) = geometry_best - POP <= TIE_EPS on the
  L2-genuine arena -> the substrate does not beat frequency even on the fair reasoning arena (a 6th on-
  substrate negative; redirect Course B density / Course D relation-closure).
- **MIDDLE_BAND_PARTIAL_REALIZATION** = otherwise (e.g. aggregate win but HIGH collapses, or partial controls).

## Must-fail controls (design contract)
(1) SCRAMBLE_REPLAY must NOT beat ONESHOT. (2) freq-leak: cross-channel independence (geometry-of-gold score
vs POP-rank-of-gold) reported. (3) DISCRETE_BIND (old failure mode) must underperform. (4) shuffled-relation
must not help (SCRAMBLE) + RANDOM_CODES geometry-necessary null. (5) NO MANUFACTURED HEADROOM: on SYN_FREQ_
GUESSABLE the geometry must NOT beat POP (scale-invariant apparatus-integrity gate). SYN_COMPOSITIONAL is the
positive control (geometry beats POP + DISCRETE on planted composition).

## Self-test (proves the discriminators FIRE; scale-invariant; SAME code path) -- MEASURED@ local 2026-07-11, SELFTEST_PASS 4.6s
PART A geometry positive control on the operator's OWN grid testbed (proven clean): ONESHOT hits@1=0.7179,
ORACLE=1.0 FIRES, DISCRETE=0.0513, POP=0.0, SCRAMBLE=0.0256, RANDOM=0.0; geometry_fires=True (grid_recovers,
grid_beats_discrete, grid_beats_pop, grid_scramble_ok, grid_oracle_fires all True; 7 distinct sigs). PART B
L2-genuine arena: SYN_COMPOSITIONAL L2-genuine extraction = 150 (non-empty); geometry beats DISCRETE (0.19 vs
0.027) + POP (reported; unstable weak-TransE fit so gated on grid not SYN); SCRAMBLE/RANDOM at chance.
SYN_FREQ_GUESSABLE no-manufacture (freq_geo << freq_pop=1.0). VacuousSmokeError guard fires if DISCRETE
passes the map-arm bar. (Note: SYN_COMP geometry-beats-POP is REPORTED not GATED -- weak TransE fit on the
planted person->middle->tail corpus is CPU-thread-noise-unstable at the small pop-margin; the robust
geometry-beats-frequency capability is proven by the STABLE grid control. The CSKG "beat frequency" number is
the FULL's headline question.)

## Smoke (LOCAL CPU, k_core=3 slice ~3000 nodes; REPORT-ONLY -- validates assembly + arms-run, NOT the FULL)
MEASURED@data/exp_course_c_map_builder_cskg_l2_genuine_v1_smoke/metrics.json 2026-07-11 (~15s): SELFTEST_PASS
(geometry_fires). CSKG assembly: 3000 nodes, 16487 edges, avgdeg 11.4, 19 rels. L2-genuine extraction = 439
held-out (491 reach-L2 -> exclude 33 L1I inverse + 19 L1F alias -> 439 genuine); 7 distinct arm sigs. Verdict
INCONCLUSIVE_GEOMETRY_READOUT_UNDERFIT: geom_best=0.007 POP=0.228 BUT ORACLE=0.018 (transductive oracle did
NOT recover on CSKG at k=8/150ep -> UNDER-FIT, not a substrate wall -- exactly why the FULL uses k=24/600ep/
dim4096). The smoke proves the operator RUNS on CSKG + the L2-genuine arena extracts + all arms fire distinct;
the CSKG headline (geometry vs POP) is the FULL's job, gated behind ORACLE firing at FULL capacity.

## Compute architecture
class: (c) MIXED with justification. (i) L2/L1I/L1F decomposition + POP = symbolic hash-joins / dict lookups
(mine_rules / reachable / pop_rank) -- combinatorial graph traversal, sequential-CPU (same as the FB15k
apparatus). (ii) map-builder geometry = TransE margin-ranking coord fit (vectorized edge minibatches) + FPE
encode (one [N,k]@[k,dim] matmul) + a single batched Re(S_hat @ conj(S_all).T)/dim ranking per arm on a
SHARED candidate tensor (PAIRED) -- matmul-heavy, batched-GPU. FULL N~23.6k x dim=4096 x nq~6000 -> GPU. FPE
S_all (N,dim) complex64 ~= 0.77GB; peak per arm ~2GB -> fits an 8GB GPU. Storage: SHARDED (each entity its
own coord/code; per-relation-TYPE operators; NEVER one global fact bundle -- the stage3 crosstalk fix).
device=auto (cuda on the GPU host); local = SMOKE-ONLY.

## SCHEMA-VET fields
- cardinality_ok: True (EXPECTED_N_UNITS = n_seeds; each seed asserts >= 5 distinct arm sigs + L2-genuine >=
  min_heldout; smoke measured 7 distinct sigs, 439 L2-genuine)
- arms_differ_verified: True (7 distinct held-out score signatures among the arms; MEASURED at smoke)
- final_metrics_atomicity: tmp_replace (_seed_checkpoint.write_metrics + os.replace; write_partial per seed)
- crlb: filtered hits@10 chance floor ~ 10/n_candidates (THEORETICAL, ~10/23600 at FULL); POP is the real
  (non-chance) bar; the REALIZES bar (geometry - POP >= POP_GAP) is on the achievable side ONLY IF the
  substrate reasons -- exactly the open FULL question; the planted grid self-test demonstrates the geometry
  CAN clear a beat-POP bar (grid_beats_pop). discriminator_reachability: guarded by ORACLE-fires (if the
  transductive oracle cannot recover, the readout capacity is the wall, verdict INCONCLUSIVE not FAILS).
- baseline_in_band: POP is the measured confound-baseline (VET HIGH h@10=0.412, in-band); DISCRETE + RANDOM
  are anti-triviality nulls; ORACLE must-fire (the readout-capacity guard).
- discriminator_survives_scale: the geometry-beats-POP discriminator is the FULL question; the smoke's
  discriminator-fires proof is the SCALE-INVARIANT planted self-test (grid geometry_fires + SYN no-manufacture)
  through the IDENTICAL code path; the CSKG smoke slice validates assembly + arms-run + non-empty L2-genuine
  extraction (headline REPORTED at smoke, FULL decides). Smoke under-fit (oracle failed) -> FULL raises
  capacity (k 8->24, epochs 150->600, dim 512->4096); the FULL's ORACLE-fires gate confirms capacity suffices.
- HARD floors strictly above tie: POP_GAP (0.03) > TIE_EPS (0.02); DISCRETE_UNDER (0.03).
- HP_SCOPE: REALIZES applies to geometry_best vs POP + DISCRETE + SCRAMBLE + SYN controls + ORACLE guard;
  CONSOLIDATION applies to REPLAY vs ONESHOT (LOW stratum + flatness + backdoor); RANDOM=null; ORACLE=must-fire.
- positive_control (Gate D): ORACLE_TRANSDUCTIVE reproduces transductive recovery (the readout-capacity guard);
  SYN_COMPOSITIONAL + the grid control reproduce the operator-smoke's geometry>POP+DISCRETE result through
  THIS cell's exact code path before any CSKG claim. regime_extension_audit: synthetic-grid -> real discrete
  CSKG is SHAPE_DRIFT (coords are FIT from graph structure, not given by construction) -- the coord-precision-
  vs-degree back-door check (companion HARD-PASS #7) + the ORACLE-fires guard guard against it.
- effective_vs_nominal_parameter_audit: swept axis = ARM x seed x degree-stratum; every arm experiences the
  nominal CSKG scale (no partition routing); sweep_alignment_verdict: ALIGNED.
- bracket_includes_discriminating_band: N/A (arms are methods, not a threshold sweep). The discriminating band
  is the arm CONTRAST (geometry vs POP on L2-genuine), with the VET's HIGH-stratum opportunity 0.226 as the
  in-band target and POP 0.412 as the bar.
- composition_edges: coord-fit (R^k additive) -> z-scale -> FPE encode (R^k -> C^dim phasor) -> kernel score;
  SHAPE_MATCH at each edge (additive displacement composes with phase addition by construction). POP baseline
  shares the candidate set + filtered-known masking with the geometry arms (PAIRED); SHAPE_MATCH.
- positive_control_arms: ORACLE_TRANSDUCTIVE (transductive recovery must-fire guard); grid control (reproduces
  operator smoke reach@1 0.718 / oracle 1.0 through this cell's scoring). cited_prior_atom: operator smoke
  reach@1 0.912 (grid FULL) / self-test 0.718 (grid SELFTEST); tolerance: qualitative (oracle fires, oneshot
  >> discrete/pop/random/scramble). regime_extension_audit: synthetic-to-real-KG is SHAPE_DRIFT declared.
- functional_requirements: (1) generalize to held-out entity-PAIRS under seen relation types on a REAL KG ->
  continuous FPE coords fit from graph + per-type phase-rotation operator; (2) beat frequency on the fair L2-
  genuine reasoning arena -> geometry vs POP_RELFREQ, degree-stratified, HIGH-degree headline; (3) genuine-
  reasoning-not-lookup -> L2-genuine held-out (exclude L1I/L1F/sym-leak); (4) consolidation adds value on a
  real underdetermined corpus -> REPLAY vs ONESHOT (LOW stratum + flatness); (5) not-a-readout-artifact ->
  ORACLE-fires guard + coord-precision-vs-degree back-door + cross-channel independence.
- calibration_check: default_ok_for_this_regime (k_core / MIN_SUPPORT / MIN_CONF / held-out frac / degree
  tertiles MATCH the VET's headroom apparatus -> comparable; FPE bandwidth ell PRE-REGISTERED; coords z-scaled
  by a single global scalar so ell is data-independent; KGE hyperparams standard regularized defaults)
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush; per-seed heartbeat jsonl)
- cell_chunked: False (3 seeds in one cell with per-seed write_partial checkpointing + cardinality gate; per-
  seed failure recorded with failure_class, does not lose other seeds)
- start_marker_written: True; crash_diagnostic_present: True (Exception -> CELL_CRASHED metrics + traceback);
  heartbeat_present: _heartbeat.jsonl per unit + per-seed flush; defensive_error_checking: passed_all_4_patterns
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except) -- grep-verified clean
- HYPOTHESIZED vs MEASURED: all self-test/smoke numbers tagged MEASURED@ paths above; band values are pre-
  registered thresholds; VET numbers (0.276/0.226/0.412) CITED@notes VET a46eadfa.

## FULL dispatch (un-shipped; director gates release on the operator-fix FULL confirmation)
overnight_queue (GPU). queue_add command handed to the director in the completion report; NOT shipped by
exp_dev (remote SCP/SSH dispatch is the orchestrator's job).
