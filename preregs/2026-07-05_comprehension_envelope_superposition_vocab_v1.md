# Pre-registration: comprehension_envelope_superposition_vocab_v1

Date: 2026-07-05
Cell: `experiments/exp_comprehension_envelope_superposition_vocab_v1.py`
Anchor: `comprehension_envelope_superposition_vocab_v1`
Queue (FULL): `remote_cpu_queue` (CPU; numpy matched-filter + block-argmax; no GPU)

## Why this cell (Director scope: measure the ENVELOPE of the proven comprehension mechanism)

`frame_order_recovery_hard_comprehension_v1` proved content-conditioned role-typing (selectional
restriction) recovers constituent role->block ORDER where pure occupancy energy is PROVABLY blind
(order_content=1.0 vs occupancy~chance), survives superposition, holds at scale -- but at FIXED (D, V, load)
points. This cell measures the ENVELOPE: as you superpose MORE constituents (load L=D/2 grows 1->4) and grow
the per-role vocab (V 50->1000), WHERE does type-discrimination break? Report the max (constituents x vocab)
at which order fidelity stays >= floor while occupancy stays at chance -- and the cliff, if any.

- proven single point: `data/exp_frame_order_recovery_hard_comprehension_v1:arms.content_frame` (order_content=1.0 at D=3/V=1024; FULL landed remote)  CITED
- decode hard cliff: `data/exp_generation_decoder_gsbc_native_blocklocal_v1:blocklocal_gsbc@V8192D26=0.856` (injective; superposed is harder)  CITED

## The envelope (constructive; NOT vs-LLM; synthetic clean GSBC data; NO KB referent declared)

- Superposition axis: D constituents (roles) superposed into B_OCC=2 FIXED occupied blocks, balanced L=D/2
  fillers per block. D in {2,4,6,8} -> load L in {1,2,3,4}. D=2 is the airtight anchor (one filler per block
  -> per-block energy = k EXACTLY -> occupancy STRICTLY order-blind, bias_audit proves it). D>=4 is genuine
  superposition (occupancy is content-blind: block energy is aggregate, not role-identity).
- Vocab axis: V per role in {50,125,250,500,1000}, disjoint partition per role (selectional restriction).
  Larger V -> more correlated GSBC candidates per partition -> the matched-filter argmax at a WRONG block
  grows (extreme-value of V spurious correlations) -> order confusion.
- All at N=8192, B_TOTAL=8, bs=1024. Smoke reduces the V grid to {50,250,1000}, seeds to 1, trials to 50 --
  NEVER N, NEVER B_TOTAL/bs (discriminator survives scale).

## Arms (PAIRED -- same propositions + true frames across arms)

- `content_frame` (PRIMARY): recognize occupied SET (top-B_OCC energy blocks); for each role r score
  s[r][j] = max over role-r partition of corr(cb[v], block_j); assign the L roles with highest (s[r][0]-s[r][1])
  to block 0, rest to block 1 (exact optimal balanced 2-block assignment); decode by partition-restricted argmax.
- `occupancy_baseline` (negative control, live): recognize SET, then RANDOM balanced role->block assignment
  (content-blind). Per-role order-recovery = chance 0.5 by construction.
- `decode_posctrl`: decode GIVEN true frame, full-codebook vs partition-restricted (role-typing benefit).

## Metrics (report SEPARATELY per Fix #28)

- `set_recognition`         -- P[recognized occupied SET == true SET]        (both arms; ~1.0 = easy part)
- `order_content_perrole`   -- mean_r P[content assigns role r to true block] (PRIMARY envelope; chance 0.5)
- `order_content_exact`     -- P[FULL role->block assignment == true]         (stringent; chance 1/comb(D,D/2))
- `order_occupancy_perrole` -- occupancy per-role order accuracy             (negative control ~0.5)
- `superposition_survival`  -- P[order exact AND all fillers decoded]        (FULL comprehension; the cliff)
- `decode_full / decode_part` -- decode given true frame, full-codebook vs partition-restricted (role-typing benefit)

## Pre-registered bands (envelope-fail-bands)

Primary envelope metric = content_frame per-role order accuracy (chance 1/B_OCC = 0.5). FLOOR = 0.75.
- HARD-PASS: content_perrole >= FLOOR across a MEANINGFUL envelope reaching D>=4 at V>=500 (HP corner (4,500)),
  while POOLED occupancy_perrole in [0.40,0.60] (near chance) and no cell > 0.72, gap at the HP corner >= 0.20,
  cv <= 0.15 there, >=3 seeds. -> comprehension HOLDS across a meaningful envelope.
- HARD-FAIL: content_perrole(D=4,V=50) <= 0.60 (mechanism collapses under MILD superposition even at easy
  vocab; does not scale past the injective point).
- MIDDLE: content works but the envelope does NOT reach D>=4 at V>=500 -> report the CLIFF location.
- Secondary FULL-comprehension envelope: superposition_survival >= FLOOR_PARSE (0.75); the cliff = cells where
  ORDER holds but full PARSE fails (comprehension degrades under load x vocab).

## BIAS audit (stressor must bite)

- Structural: at load=1 (D=2 injective), per-block occupancy energy provably INVARIANT to role-swap within a
  fixed SET (`occupancy_degenerate_for_order_load1 == True`). If not, BLOCK_DISPATCH_BIAS_DEGENERATE.
- Empirical: POOLED occupancy_perrole in [0.40,0.60] AND no cell > 0.72. If occupancy spuriously recovers
  order, BLOCK_DISPATCH_BIAS_OCC_NOT_AT_CHANCE. (Per-cell band is coarse at D=2 -> pooled + per-cell-max, not
  a tight per-cell band, to avoid false-block on the D=2 binary-per-role coarse variance.)
- Discriminator fires: easy-corner (D=2,V=50) content_perrole - occupancy_perrole >= 0.20.

## SCHEMA-VET fields

- cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_D * n_V = 3 * 4 * 5 = 60 (FULL); 1 * 4 * 3 = 12 (smoke).
- arms_differ_verified: content vs occupancy per-role order-predictions hash-distinct per (seed,D,V) unit.
- final_metrics_atomicity: tmp_replace (os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / bare except; grep-gated clean).
- crlb_n_a: per-role order chance = 1/B_OCC = 0.5; exact chance = 1/comb(D,D/2). Content ceiling at the easy
  corner is ~1.0 by self-correlation dominance (THEORETICAL). No closed-form noise floor for the balanced
  assignment argmax; decode ceiling at scale is CITED (0.856 injective; superposed harder).
- baseline_in_band: occupancy_baseline is a NEGATIVE CONTROL expected AT per-role chance 0.5 by construction;
  EXEMPT from the AG 0.05<baseline<0.95 in-band gate (HP_SCOPE) -- it carries ONLY the near-chance BIAS gate.
  The MECHANISM arm (content) is the finding, not a baseline; its across-grid behavior IS the envelope.
- discriminator survives scale: smoke runs at full N=8192 across the FULL D grid (only V grid/seeds/trials
  reduced); the order gap fires at the easy corner and the parse cliff appears at high load x high V in smoke.
- HP strictly above floor: content_perrole 0.75 >> chance 0.5; envelope must reach D>=4 at V>=500.
- HP_SCOPE: chain-grade HP gates (FLOOR/GAP_MIN/CV_MAX/envelope-reaches-corner) apply ONLY to content_frame;
  occupancy carries only the near-chance BIAS gate; decode posctrl carries the role-typing decode-benefit gate.
- calibration_check: default_ok_for_this_regime (block-local sparse-code decode; role-typed decode reproduces
  the proven-cell behavior -- dec_part 1.0->0.54 while dec_full collapses to 0.0 under superposition, verified
  in smoke).
- progress_logging: line_buffered_stdout (sys.stdout.reconfigure line_buffering) + per-unit heartbeat + _say.
- defensive_error_checking: start_marker + crash_diagnostic + heartbeat + atomic write (all 4).
- kb_referent_declared: FALSE (synthetic clean GSBC data only; no `# KB_REFERENT:` line -> PROT-022 not
  triggered). The GSBC pool npz is an untracked DATA DEPENDENCY (not a referent) -- must exist on remote
  before FULL dispatch.
- gate A (effective vs nominal): D and V are the swept params; each primitive experiences them directly
  (load L=D/2 per block; V candidates per partition). sweep_alignment_verdict: ALIGNED.
- gate B (discriminating band): smoke shows superposition_survival spans 1.0 (D<=6 low V) down to 0.52 (D=8
  V=1000) -> >=30% of cells in the discriminating band; the parse envelope is not saturated.
- gate C (composition edges): recognize_set -> content_order_2block -> partition-restricted decode; all numpy
  correlation shapes match (V x bs codebook, bs-segment blocks). SHAPE_MATCH.
- gate D (positive control reproduce): D=2 load=1 reproduces the proven injective point (content_perrole=1.0,
  dec_full=1.0). Under superposition dec_full collapses (0.0) while dec_part holds -> the role-typing benefit
  is the mechanism, reproduced from the proven cell's selectional-restriction decode.
- gate E (functional requirements): (1) recover which constituents co-locate + their block -> content matched
  filter; (2) decode each superposed filler -> partition-restricted argmax (selectional restriction); (3) prove
  the win is type-discrimination not occupancy -> occupancy_baseline negative control at chance.

## Compute architecture

- Class: (b) sequential-CPU with justification. Reuses the proven CPU numpy matched-filter + block-argmax
  primitive (bit-identical to the cited comprehension cell); each (D,V) phase point is an independent fast
  numpy matmul. The single matmul-heavy step (the JL projection building cb_max, ~67 GFLOP) is done ONCE per
  seed and all grid cells are cheap slices of it. Estimated FULL wall: ~2-4 min (3 seeds x cb_max build + 60
  cheap cells). Batching to GPU would require porting the whole matched-filter and risks divergence from the
  proven CPU reference; wall time is well under any batching threshold.
- storage strategy: no_storage (compose -> read within a trial; no persisted item store; not a chain/retrieval cell).

## Smoke result (MEASURED @ data/exp_comprehension_envelope_superposition_vocab_v1/metrics.json)

- SELFTEST PASS 0.4s; SMOKE HARD_PASS (SMOKE_MACHINERY_OK) 6.8s compute.
- BIAS occupancy_degenerate_for_order_load1=True; occupancy POOLED per-role=0.503 (chance 0.5), no cell > 0.72.
- Easy corner (D=2,V=50): content_perrole=1.000 vs occupancy=0.480, gap=0.520 (discriminator fires).
- ORDER envelope: content_perrole holds >= 0.75 at 12/12 cells (min 0.975 at D=8) -> order recovery is
  remarkably robust; max_constituents@V>=500=8, max_V@D>=4=1000.
- FULL-PARSE envelope: superposition_survival holds >= 0.75 at 11/12 cells; CLIFF at D8_V1000
  (sup_survival=0.520). parse_max_constituents@V>=500=6.
- decode: dec_full=1.0 at load=1 but 0.0 at load>=2 (role-blind decode cannot resolve co-located fillers);
  dec_part (role-typed) holds 1.0 -> 0.54 -> selectional restriction is NECESSARY, not merely helpful.

## Dispatch

- FULL -> remote_cpu_queue, timeout 1800s (fast numpy; generous; no _n suffix -> no PROT-019 floor). 3 seeds (7,13,19).
- PREREQ: SCP `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` to remote (untracked data dependency;
  queue_add does NOT ship it). NOT declared as a KB_REFERENT (PROT-022 avoided per Director scope).
