# Pre-reg: Course-C ORACLE capacity ladder -- what MINIMUM fit/readout capacity fires the transductive ORACLE at full CSKG scale?

- anchor_name: `course_c_oracle_capacity_ladder_v1`
- cell: `experiments/exp_course_c_oracle_capacity_ladder_v1.py`
- metrics: `data/exp_course_c_oracle_capacity_ladder_v1/metrics.json`
- date: 2026-07-11
- queue: **remote_cpu_queue** (CPU-safe default; no memory limit; single seed = memory FLAT by construction).
  LOCAL = NEVER (USER-locked: no local experiment execution; all validation is a remote job).
- seed: 7 (single seed; this is a capacity DIAGNOSTIC, not a multi-seed verdict)
- upstream INCONCLUSIVE: `data/exp_course_c_map_builder_cskg_l2_genuine_v1/metrics.json`
  (verdict INCONCLUSIVE_GEOMETRY_READOUT_UNDERFIT: oracle=0.0231 vs random=0.0002 at full 25752-entity core,
  k=24/dim=4096/600ep full-batch margin fit -> oracle collapsed from ~1.0 at the 3000-node smoke / grid).
- handoff: `notes/exp_dev_handoff_research_reasoning_realization_gap_closure_prep_2026-07-11.md` (Anchor 1-2)
- Anchor-1 fit module (new): `experiments/_kge_anchor1_fit.py`
- reused apparatus (identical code path as the decisive run): `experiments/exp_course_c_map_builder_cskg_l2_genuine_v1.py`
  (geom_scores / filtered_hits / pop_hits / extract_l2_genuine / stratify), operator
  `experiments/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1.py` (make_fpe_basis / fit_transe_coords),
  CSKG `experiments/exp_cskg_dense_core_headroom_acceptance_v1.py`, symbolic `exp_gt_induction_fb15k237_dense_v1.py`.

## Question
The transductive ORACLE (coords fit WITH the held-out edges folded in, then recovered via the readout) is the
PRECONDITION gate: if the fit+readout cannot even recover edges it was trained on out of 25752 candidates, the
reasoning question (does geometry beat frequency on genuinely-held-out L2 edges) is not ASKABLE. The decisive
FULL run under-fit (oracle=0.023). This cell LOCATES the minimum capacity that fires the oracle BEFORE a full
3-seed re-run, and DISENTANGLES the two candidate bottlenecks so we scale the right axis.

## Two bottlenecks, disentangled per ladder point
- **FIT capacity**: original `fit_transe_coords` is FULL-BATCH margin-rank -> `epochs` gradient steps TOTAL
  (600) with the margin loss only pushing gold above 10 random negatives. At 485k edges this is under-trained
  + weak ranking pressure. Levers: more epochs, MINIBATCH SGD, Anchor-1 (CE self-adversarial + N3 + reciprocal).
- **READOUT capacity**: the FPE bounded-kernel readout (dim) may not resolve gold out of 25752 even given a good
  fit. Lever: readout dim.
Per point we fit the transductive ORACLE and measure filtered hits@10 under BOTH readouts:
  `oracle_fpe` = FPE bounded-kernel (the MANDATED readout; the gate) ; `oracle_direct` = rank by
  -||x_hat - X_c|| on the SAME standardized coords (fit-limited reference). If direct FIRES but fpe does NOT ->
  READOUT is the wall (raise dim). If NEITHER fires -> FIT is the wall (epochs/objective axis).

## Ladder (ordered cheap -> expensive; the CHEAPEST point clearing ORACLE_FIRE is the re-run capacity)
| label | fit_kind | k | fpe_dim | epochs | batch | purpose |
|---|---|---|---|---|---|---|
| L0_margin_fb_ep600 | margin_fb | 24 | 4096 | 600 | full | CONTROL: reproduce the 0.023 collapse (ladder calibrated to the failing regime) |
| L1_margin_fb_ep2400 | margin_fb | 24 | 4096 | 2400 | full | pure more-epochs with the current objective |
| L2_margin_mb_ep60 | margin_mb (minibatch CE, no N3/recip) | 24 | 4096 | 60 | 8192 | minibatch vs full-batch, same-ish objective |
| L3_anchor1_ep60 | anchor1 | 24 | 4096 | 60 | 8192 | Anchor-1 recipe, moderate |
| L4_anchor1_ep150 | anchor1 | 24 | 4096 | 150 | 8192 | Anchor-1 recipe, more |
| L5_anchor1_k32_d8192 | anchor1 | 32 | 8192 | 150 | 8192 | + coord/readout resolution axis |

## Primary metric + pre-registered bands
- `oracle_fpe_h10` (filtered hits@10 of the ORACLE held-out sample under FPE readout). **ORACLE_FIRE = 0.90**
  (the reasoning question becomes askable). `oracle_direct_h10` the fit-limited reference under direct-distance.
- N_ORACLE_HOLD = 500 random test edges (memorization-capacity probe; L2-genuineness irrelevant to the ORACLE).
- FPE_ELL = 0.55 (pre-registered; coords z-scaled so ell is data-independent). Anchor-1 defaults (pre-registered,
  held fixed while the ladder sweeps epochs/k/dim): lr=0.05, gamma=9.0, n_neg=64, adv_temp=1.0, n3_lambda=5e-4,
  batch=8192, reciprocal=True.

## Decision (pre-registered, before running)
- **LADDER_ORACLE_FIRES** = at least one ladder point clears `oracle_fpe_h10 >= 0.90`. Report the CHEAPEST such
  point as `firing_config` -> that capacity is handed to the decisive 3-seed re-run. Also report the single-seed
  reasoning PREVIEW at that point (refit INDUCTIVELY, extract L2-genuine, ONESHOT geometry vs POP degree-strat).
- **LADDER_READOUT_LIMITED** = best point has `oracle_direct_h10 >= 0.90` but `oracle_fpe_h10 < 0.90` -> the FPE
  readout is the wall; raise readout dim / change readout before the re-run.
- **LADDER_FIT_LIMITED** = no point fires either readout -> fit capacity is the wall; escalate beyond the ladder.

## Discriminator-fires / not-vacuous
L0 is the CONTROL that must REPRODUCE the collapse (oracle_fpe ~ 0.02-0.05) -- proves the ladder is calibrated to
the failing regime, not a trivially-saturating setup. A point "fires" only by clearing 0.90 (a hard gap above the
~0.02 collapse floor). The preview is REPORTED (single seed), never a verdict -- the decisive verdict is the
3-seed re-run.

## Compute architecture
class: (c) MIXED. CSKG assembly + L2-genuine extraction (preview only) = symbolic graph traversal (sequential-CPU
correct, same as the VET apparatus). Coord fit = minibatch SGD; readout = batched matmul (FPE kernel + cdist),
query-chunked (chunk=256) so no (nq, N) map is materialized whole. SINGLE seed + SINGLE CSKG assembly reused
across all ladder points -> memory FLAT (the multi-seed accumulation OOM driver is absent by construction; no
subprocess isolation needed). device=cpu on remote_cpu_queue.

## SCHEMA-VET fields
- cardinality_ok: N/A single-seed diagnostic; EXPECTED ladder rows = len(FULL_LADDER)=6, each row emitted with
  measured oracle_fpe/oracle_direct.
- arms_differ_verified: N/A (ladder points are capacities of the same ORACLE arm, not competing arms); the
  contrast is capacity, and L0 (collapse) vs firing point must DIFFER by >= 0.85 for a FIRES verdict.
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
- crlb: filtered hits@10 chance floor ~ 10/25752 ~ 4e-4 (THEORETICAL); ORACLE_FIRE=0.90 is far above chance and
  is the memorization-recovery bar (transductive fit SEES the answers), reachable iff fit+readout capacity
  suffices -- exactly what the ladder measures. discriminator_reachability: the grid/3k-smoke oracle already hit
  ~1.0 at low N, so 0.90 IS reachable given capacity; the open question is the minimum capacity at N=25752.
- baseline_in_band: L0 control reproduces the ~0.02 collapse (measured at run time); firing points must clear 0.90.
- discriminator_survives_scale: the whole point IS scale -- the ladder runs at the FULL 25752-entity core (not a
  reduced slice), so the firing capacity it locates is the capacity the re-run needs at full scale.
- HP_SCOPE: ORACLE_FIRE gate applies to oracle_fpe_h10 per point; oracle_direct is the fit-vs-readout diagnostic.
- positive_control (Gate D): the grid/3k-smoke oracle=1.0 (CITED@prior smoke/grid) is the prior that 0.90 is
  reachable; the ladder reproduces the failing full-scale regime (L0) and searches for the capacity that recovers
  it. regime_extension: same corpus, same readout, only capacity varies -> SHAPE_MATCH.
- effective_vs_nominal: the ladder axis (fit_kind x epochs x k x dim) is exactly the capacity the ORACLE fit +
  FPE readout experience at full N; sweep_alignment_verdict: ALIGNED.
- functional_requirements: (1) the transductive oracle must recover trained edges out of 25752 candidates ->
  fit+readout capacity; (2) locate the MINIMUM such capacity -> cheap-to-expensive ladder; (3) attribute the wall
  to FIT vs READOUT -> dual readout per point.
- calibration_check: default_ok_for_this_regime (FPE_ELL pre-registered + data-independent via z-scaling;
  Anchor-1 hyperparams are literature-standard RotatE self-adversarial / Lacroix N3 defaults, held fixed).
- progress_logging: print_flush_true (per-ladder-point + per-fit flush; line-buffered stdout; heartbeat jsonl).
- cell_chunked: False (single seed by design -> no cross-seed accumulation; memory-safe without subprocess).
- start_marker_written: True; crash_diagnostic_present: True (Exception -> CELL_CRASHED metrics + traceback);
  heartbeat_present: _heartbeat.jsonl per ladder point; defensive_error_checking: passed (single-seed diagnostic,
  preview wrapped in specific-Exception guard that records preview_error class without killing the ladder).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except) -- grep-verified clean.
- HYPOTHESIZED vs MEASURED: upstream oracle=0.0231 MEASURED@data/exp_course_c_map_builder_cskg_l2_genuine_v1/
  metrics.json:gates.reach_hits_at_k.ORACLE_TRANSDUCTIVE; grid oracle=1.0 CITED@prior smoke; all ladder numbers
  are MEASURED@this metrics.json at run time (none pre-baked).

## Dispatch (handed to orchestrator; exp_dev does NOT SCP)
remote_cpu_queue, single seed, full core. No local smoke (USER-locked). This ladder IS the pre-FULL remote
validation. queue_add command in the completion report.
