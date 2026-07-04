# Director BACKUP — CURRENT STATE 2026-07-04 (clean rewrite; supersedes all prior)

**Read end-to-end first. This is a clean consolidation. The prior amendment-stacked BACKUP
(`director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-03_LATE.md`) is SUPERSEDED — do not use it.**
Agents are ONLINE (the weekly rate-limit that throttled spawns earlier today has lifted).

## >>> LATEST STATE ~21:05Z (read first) <<<

- **>>> OBJECTIVE-SWAP DEAD (VET-verified HF, both seeds). Retrieval is a CODE/QUANTIZATION bound, NOT a training-objective bound. STRATEGY FORK. <<<** KL-RANK ret_agree10 = 0.223/0.219 vs MSE 0.211/0.211 -> delta +0.010 (~9x smaller than K256's verified +0.093). KL-RANK FIXED the dense "decline" (plateau 0.78 vs MSE 0.65) and retrieval STILL didn't move -> proves it's not the loss family (atomized HF_STRUCTURAL_BOUND, commit 7f116800d; +1 HF). KL "looked" better on coarse cosine only by OVERSHOOTING the teacher (calib_err 0.096 vs MSE 0.006 -- worse calibration, not a win). **=> the elegant 'fix retrieval AND keep sparsity via a better loss' path is CLOSED.**
- **THE FORK (retrieval is the real goal ~0.21, target 0.35; two lever families):** (A) SPARSITY-PRESERVING = OPQ-style LEARNED ROTATION before the block quantizer (align variance with code axes -> less quantization loss at SAME ~3% sparse; cardinality-drill #2 lever; the LAST sparsity-preserving shot). **DISPATCHED (exp_dev a8c105) -- watch: a rotation must NOT break SBC algebra.** (B) TRADE SPARSITY = K256 (+0.09 verified, 6.25% active) or bigger. **DIRECTOR CALL (full-auto): try OPQ (A) first -- it violates no goal. IF OPQ ALSO FAILS, retrieval-at-2% is likely unreachable and the 2%-sparsity-vs-retrieval tradeoff becomes a USER decision (trade sparsity / regime-switch dense-retrieval+sparse-composition / hold sparsity+weaker retrieval). Do NOT unilaterally trade the USER-confirmed 2% goal -- flag it.**
- **NOTE:** the "2% sparse" framing is loose -- K=128 = 3.125% active (K256 = 6.25%). Full bypass (aa97d4, code-capacity ceiling K128 vs K256 for retrieval) landing -- refines whether OPQ has headroom (code-utilization gap) or retrieval is truly code-bound (must trade sparsity).

## >>> LATEST STATE ~20:25Z <<<

- **>>> ENCODER: two big reframes from a0ff3e's 3-cell landing (VET a746e1 in flight -- hold loosely). <<<**
  - **(1) The "DECLINE" WAS A METRIC ARTIFACT.** v3e's DECLINE_CONTINUES (which drove "needs objective-family change") was measured on the DENSE proxy. On the REAL goal metric (ret_agree10), there is NO decline over 6000 steps (v4 convergence cell, a92ae8a46 + bugfix e845cf831 -- exp_dev found+fixed its own Gate-D VAL-vs-TEST bug, recomputed offline bit-exact). => the objective-swap's CONVERGENCE motivation is moot; its RETRIEVAL motivation (rank-aware loss directly targets ranking) STANDS. Plateau-hold LR gives a small +0.02-0.03 ret_agree10 lift (free).
  - **(2) K=256 LIFTS RETRIEVAL +0.09 (2-seed HARD_PASS, v5, 75326999a): ret_agree10 0.21 -> ~0.30** (delta +0.093/+0.097, no calib regression, bypass-ceiling prediction survived training). **BUT K=256 = 6.25% active -- 3x the ~2% SPARSITY goal (#3). Real SPARSITY-vs-RETRIEVAL tradeoff.**
  - **STRATEGY (Director call, full-auto):** the SPARSITY-PRESERVING retrieval path = the OBJECTIVE-SWAP (rank-aware/KL loss at K=128/2%, addc94 building) -- try it FIRST; if it lifts ret_agree10 toward 0.35 at 2% sparse, that's the win. K=256 (6.25%) is the FALLBACK (trade sparsity for retrieval). RUNTIME REGIME-SWITCHING is the release valve (dense-retrieval regime + sparse-composition regime) if we can't get both in one static code. v6 (K256+plateau, running) tests if the levers stack. SURFACE the 2%-vs-retrieval tradeoff to USER.
- **IN-FLIGHT (multiple, ~20:25Z):** GPU: v6 k256+plateau (running). CPU: bypass-fix full-scale K128-vs-K256 retrieval-ceiling (aa97d4). Building: objective-swap KL/rank-aware (addc94, the sparsity-preserving retrieval path). VET: v4/v5 (a746e1). Testbed: dispatch-on-idle AUTO-REFILL daemon (aef5c7, durable "multiple-in-flight-at-all-times" fix).

## >>> LATEST STATE ~19:00Z <<<

- **>>> v3c FULL RUN: "BREAKTHROUGH" REFUTED by Skunkworks VET (a1ac04, both seeds off-disk). ENCODER NOT SOLVED. <<<** Paired global-RKD-only vs in_batch-RKD-only, 2 seeds (7,13), NCE OFF, full 178k. The reported in_batch BLOCK(best) 0.897/0.887 / DENSE 0.877/0.895 / keyed@J5 1.000 was a FALSE breakthrough -- **VET refuted the "hits 0.85" claim on all 4 rigor checks:** (1) BEST-CKPT INFLATION -- in_batch trajectory DECLINES (pearson(step,dense) -0.88/-0.81 seed7); final-step ~13-14% BELOW the cherry-picked best; the cell's peak-detector even counts the untrained step-0 spike (~0.956) so its HARD_PASS is structurally unreachable; (2) NOT REPRODUCIBLE -- v3b's identical-config final was 0.7336 vs v3c's 0.6514 (11% gap between "identical" reruns); (3) 0.368->0.89 CONFOUNDED -- steps 40k->1.8k + batch512->128 + best-of-13 selection ALL moved; in_batch already declining within 1800 steps (as consistent with "still collapses given more steps" as with "NCE fixed it"); (4) WRONG METRIC -- goal is COSINE-TO-GOLD (~0.54->0.85); we measured SPEARMAN over 400k mostly-random pairs (only ~0.05% gold-similar); the closer metric ret_agree10 is UNSTABLE 0.15-0.67 across seeds. **WHAT SURVIVES (real): (a) LANDMARK-DROP CONFIRMED (MM_STANDARD, +cert) -- global block algebra genuinely broken (keyed 0.13/0.32, ret_agree10 near-chance 0.015/0.026) -> DROP the landmark objective for good; (b) in_batch block algebra roundtrip survives (goal #4 "algebra survives" is real).** **HONEST STATE: NOT "remove NCE fixes in-batch" -- that is CONFOUNDED/UNPROVEN.** Net cert this VET: MM +3 (landmark-droppable MM_STANDARD, in_batch-bounded-characterization MM, ckpt-inflation+metric methodology MM_TENTATIVE), commit in `data/substrate_index/`. **NEXT (honest, VET-recommended, routed to ad1710): the DECLINE-vs-PLATEAU diagnostic** -- in-batch-RKD-only at v3c config but LONGER (4000-6000 steps, dense-eval every ~50 steps), reporting FINAL-step ALWAYS + ret_agree10 + COSINE-TO-GOLD (the real goal metric) as co-equal headlines. Decides whether "remove NCE" plateaus at a usable level or just slows the collapse toward v2's 0.368 floor. **METHODOLOGY LOCKED: report final-step not just best-ckpt; use the metric the goal is stated in (cosine-to-gold), not spearman over random pairs.**
- **>>> v3e DECLINE-vs-PLATEAU LANDED (seed_7; honest measurement -- final-step, disjoint VAL/TEST split, step-0 excluded): the encoder is COARSE-GOOD / FINE-WEAK. <<<** cell `experiments/exp_encoder_v3e_decline_vs_plateau_v1_core.py` (commit `200e1421a`). **cosine-to-gold on genuinely-similar pairs hi80_cos = 0.832 (calib_err 0.006 -- NEAR the 0.85 goal, honestly measured from 0.54 baseline)**, BUT **ret_agree10 (retrieval@10) = 0.21 (WEAK)**; verdict DECLINE_CONTINUES (still sliding, doesn't cleanly converge; final_block spearman 0.9187 on TEST but that spearman-over-mostly-random is the misleading metric). So: preserves COARSE "are these similar" nearly to target, SCRAMBLES fine near-neighbor ranking (what retrieval needs). **BYPASS diagnostic (code-capacity, smoke): K=128 caps ~0.80, K=256 ~0.89 (+0.09) -> the fine-retrieval weakness is likely CODE RESOLUTION (K=128 too coarse); K=256 is the candidate lever.** (full bypass pending GPU; seed_13 running.) **METRIC VERDICT (research af8384, ANSWERED):** the stated "0.85 semantic" is a COARSE cosine question (hi80_cos: does our code agree when the teacher says two concepts are similar) -- traced to PROGRESS.md + goals memory + v3e docstring -- and it is **essentially MET (0.832 final, 0.857 earlier ckpt).** BUT the metric that matches the USER's ACTUAL need ("return the RIGHT memory, not a vague neighbor") is RETRIEVAL (ret_agree10: do our top-10 NN match the true top-10) -- it had NO target and is WEAK at 0.21. **This is the real goal now (Director call, full-auto): scoreboard ret_agree10 HARD-PASS >=0.35, HARD-FAIL <=0.25.** KEY: the K=128 code supports ret_agree10 ~0.48 (K=256 ~0.58); the trained encoder at 0.21 is NOT EVEN HALF its available K=128 ceiling -> **the retrieval gap is a TRAINING problem (convergence/objective), NOT code-size. K=256 is a SECONDARY lever.** => the convergence experiment (a0ff3e) is the right priority. Algebra healthy (1.000).
- **QUEUE BEHIND (USER discipline "always have a queue behind"):** ad1710 redirected to build (design+smoke+HOLD) the ROBUSTNESS-CONFIRMATION of in_batch-NCE-off (3-5 seeds, full bind/unbind/bundle algebra suite, held-out test, full trajectory to kill the early-ckpt-spike risk -> CG promotion if it holds) + the teacher-through-sparsifier BYPASS diagnostic (code-capacity ceiling). Ready to fire the instant VET clears.
- **CARDINALITY research (aad2a0) done:** no hard info-theoretic wall below 0.85 (d=4096 oversized for N=178k); block-WTA pays a Product-Quantization axis-misalignment tax + trains on MSE not rank-aware loss -> levers IF we need to push past 0.89: (1) rank-aware loss reweight, (2) OPQ-style learned rotation before block-argmax; widen-code is Rank 3. (Note: research assumed we were stuck at 0.734; v3c's in_batch 0.89 already beats its P=0.20 "NCE-fix-alone-sufficient" prior.)
- **BCT (a246) done + running:** compatibility loss WORKS -- restores cross-version retrieval 0.00 -> 0.89 at 0.989 quality-retention (essentially free); local full-preview HARD_PASS; full confirmation running on remote_cpu_queue (VET on landing). Encoder updates can be made non-breaking (de-risks the continual-improvement vision).

## >>> LATEST STATE ~18:15Z <<<

- **>>> ENCODER PIVOT (v3b landed, decisive): the lever is KILLING THE CONTRASTIVE (NCE) TERM, not the landmark objective. <<<** v3b (`data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1/metrics.json`): PRIMARY batch-sweep HARD_FAIL (landmark-vs-inbatch unresolved at MID -- in_batch didn't degrade, global was worse; likely CONFOUNDED because both arms carried the harmful NCE term -- Skunkworks VETting). **SECONDARY = the win: NCE-ablation TAIL_CORRUPTION_CONFIRMED_RECOVERED -- NCE_ZERO (RKD-only) DENSE 0.734 vs NCE_CURRENT(0.5) 0.269, delta +0.465.** The constant contrastive tail corrupts the distilled geometry; zeroing it recovers to ~0.73. **SCALE (corrected -- important): v3b actually ran at FULL 178k** (teacher_n_concepts=177899, n_train=172899, n_held=5000; NOT the 43.9k R1 used), so **NCE-off DENSE 0.734 is a FULL-SCALE number** -- from v2's full-scale collapse 0.368 to 0.734 just by killing the contrastive term. That is the headline. Still short of 0.85 (and BLOCK/sparse will be a touch lower), so more levers may be needed. **Skunkworks VET:** primary batch-sweep = CONFOUNDED category(c) (all 8 arms carried NCE=0.5 -> not a clean landmark negative; landmark stays ALIVE); NCE-off atomized MM_STANDARD (**+2 cert: MM + a compound-loss-ablation-completeness meta rule**, commit `5a0895383`; single-seed caveat). **2x-drill:** landmark = CONDITIONAL DROP (settled by ONE untested arm: in_batch+NCE_ON->OFF at 178k); flags a possible RAW-CARDINALITY CEILING (0.734 < 0.825-at-tiny-vocab) that no batch/objective trick fixes -> even NCE-off may land short of 0.85. **CAPACITY diagnostic** (train-vs-held on R1 ckpts): mechanically "capacity_bound" (both gaps ~0, values ~0.52) BUT that's the POST-DECLINE checkpoint -- since NCE-off reaches 0.734, the student is NOT the ceiling; the 0.52 was NCE corruption. **NEXT (dispatched, exp_dev ade3960): NCE-off FULL run** = paired global-RKD-only vs in_batch-RKD-only at 178k (does RKD-only hold 0.73+ toward 0.85 at scale, AND does landmark finally beat in_batch at FULL where in_batch collapses). Once-per-stage GPU FULL. **SOP running: Skunkworks landed-VET (a1921) + research 2x-drill of the batch-sweep negative (a857).** Methodology banked: save mid-training checkpoints so capacity can be re-measured pre-decline; coverage-ratio-match-at-MID did NOT substitute for a FULL test (why: distinct-near-neighbors-seen-over-training >> per-batch coverage). **Latent bug flagged: checkpoint-resume ByteTensor crash L364 gen.set_state (exp_dev item).**
- **PARALLEL (idle resources in use):** BCT compatibility experiment (exp_dev a246) on remote_cpu_queue -- can a compatibility loss restore cross-version retrieval (compat probe MEASURED an encoder swap collapses retrieval to ~1%, HARD_FAIL, so encoder updates silently break stored vectors -- real, need BCT loss before any version change).

## >>> LATEST STATE ~16:20Z <<<

- **R1 encoder MID validation: GLOBAL arm FINISHED (~15:59Z); in_batch baseline arm still training (~15-20 min left)** (pid 29376, local CPU). The run does global-arm THEN in_batch-baseline (2x1800 units) then evals both -> full metrics.json at the very end. **DENSE-recovery number = THE signal** (does DENSE recover to ~0.8 with the global/landmark objective = objective fix confirmed). Do not read the training loss; use the eval spearman.
- **EARLY-READ RESULT (~16:35Z, exp_dev a00368, setup cross-checked vs the live run log):** GLOBAL arm, full held set n=4390 (teacher bge_large_v2_name_43905, 43.9k concepts), 400k pairs: **DENSE spearman = 0.521, BLOCK_K128 = 0.511.** Verdict = **PARTIAL** (target ~0.8; run's own pre-reg pass floor 0.64; both missed) BUT +0.15 over v2's full-scale collapse (0.368). **KEY FINDING = PEAK-THEN-DEGRADE:** in-training quick-eval (1500-held/60k subsample) logged 0.740@step1200, 0.716@step1500, then final full-eval@step1800 = 0.521 -- a DOWNWARD trend on the consistent metric + rkd(geometry) plateaued ~0.22 from step ~700 while nce(contrastive) kept falling 0.51->0.456. Hypothesis: the CONTRASTIVE term over-optimizes in the tail and corrupts the RKD-built geometry => training-SCHEDULE problem, not an objective ceiling (cheap fix: early-stop / down-weight-NCE). Secondary possibility: 1500-subsample quick-eval over-reads vs full 4390 eval (variance). **BLOCK ~= DENSE (0.51 vs 0.52) confirms SPARSITY IS NOT THE BOTTLENECK** (sparse-frontier finding holds) -- the whole gap is the dense objective/schedule. CAVEAT: single arm, MID scale (43.9k not full 178k), 0.74 was a lighter eval. **The paired GLOBAL-vs-IN_BATCH verdict (cell's `_verdict_mid`) is the real discriminator -- in_batch arm ~10 min out.** **DIAGNOSTIC DISPATCHED (exp_dev a4dc45, design+smoke local, HOLD FULL):** full-held eval every ckpt + NCE-ablation (RKD-only / anneal) + best-ckpt-select, to settle degradation-vs-variance and recover the peak.
- **R1 MID RUN DIED mid-eval ~16:42Z (recoverable, NOT a loss):** BOTH arms trained to step=1800 (global + in_batch checkpoints on disk at `data/substrate_concept_encoder_v1b_v3global_mid/_ckpt_block_{global,in_batch}.pt`); eval reached unit 4/9 (INBATCH_DENSE) then the LOCAL process (pid 29376) was hard-killed BEFORE writing metrics.json -- no crash-metrics file = OS/resource kill, not a caught exception. Cause: LOCAL laptop resource pressure (WinError 1450 family the testbed also hit), memory-heavy eval running concurrent with testbed work (local laptop -- unrelated to the remote BOINC kill). RECOVERY: reconstruct the paired verdict by evaluating BOTH checkpoints with the early-eval script (exp_dev a00368 resumed: global already 0.521/0.511; in_batch eval running -> gives recovery_delta). **LESSON: do NOT run heavy MID eval on local-CPU concurrent with other heavy local work; route MID diagnostic + FULL to the (now-free) GPU.**
- **>>> R1 PAIRED VERDICT (recovered ~17:00Z) = NOT VALIDATED at MID, but the TEST was UNDERPOWERED (not a real negative):** in_batch DENSE 0.5677 / BLOCK 0.5240 vs global 0.5209 / 0.5110 -> **recovery_delta_dense = -0.047, delta_block = -0.013 (NEGATIVE).** Landmark objective did NOT beat in-batch at MID. **ROOT CAUSE (key methodology insight):** the in-batch-RKD failure the landmark objective fixes is SCALE-DEPENDENT and barely fires at MID. FULL train ~160k, batch 512 -> ~0.3% sampled -> graded near-neighbors ~never co-occur in a batch -> in-batch collapse (that's the 178k failure). MID train ~39.5k, batch 512 -> ~1.3% (~7x more co-occurrence) -> pathology gentle -> both arms ~0.52-0.57, nothing to rescue. The +0.15 over v2 (0.368) is a SCALE artifact, NOT an objective effect. **=> MID-as-run CANNOT discriminate the objective. Do NOT GPU-FULL the global objective on MID strength.** **FIX TO THE TEST (decisive, cheap):** reproduce FULL's near-neighbor co-occurrence at MID by MATCHING batch/N RATIO -> batch ~128 (=512*39515/160000), NOT absolute-N. At batch~128 in-batch should collapse while global (landmark-supervised = batch-size-independent) holds -> measurable delta at MID cost. Batch-sweep 512/256/128/64 as the discriminator axis = the proof + cheap scale stand-in. **Folded into exp_dev a4dc45's cell** (same run: batch-sweep + full-held eval every ckpt for BOTH arms + NCE-ablation + best-ckpt). Smoke local, then GPU (free). **NOTE: peak-then-degrade (0.74->0.52) still open -- may be objective-independent schedule artifact (both arms); the a4dc45 full-held trajectory settles it.**
- **CONTINUAL/SELF-IMPROVING ENCODER drill landed (research aa9840, memo `notes/research_drill_brain_grounded_continual_self_improving_encoder_2026-07-04.md`):** R1's FIXED-LANDMARK objective ALREADY IS the backward-compatible-representation mechanism (Shen 2020) that lets an encoder keep improving WITHOUT invalidating stored vectors -- brain's "stable readout despite drift" needs periodic RE-ALIGNMENT, not passive freeze. NOW = nothing new to build; NEXT = one cheap decisive test (cross-checkpoint retrieval-compatibility probe reusing the saved R1 checkpoints; HARD-FAIL if <50% same-ckpt retrieval); R3/R4 self-teacher LATER (60-250x corpus wall unchanged). P_deflated 0.45. Directly answers USER's "should the encoder self-improve over time" (YES; mechanism already in place).
- **GUI LAUNCHED for USER (~16:50Z):** `tools/dash_gui.py` running (venv pythonw re-execs to system interpreter -> may show 1-2 pythonw procs but ONE window; do NOT kill to "dedup" -- that killed the real one once). Final commit `7a5ff16f1`. Nit: GPU util shows the smoothed EMA (lags at transitions; util_pct/mem/temp are the truth) -- show instantaneous as primary on next testbed touch.
- **[superseded early-read plan] (exp_dev a00368, ~16:20Z):** the finished global-arm checkpoint is **`data/substrate_concept_encoder_v1b_v3global_mid/_ckpt_block_global.pt`** (126MB, final, written 15:59Z; dict key `"student"` holds the state_dict). NOTE: that is the ARTIFACT dir `substrate_concept_encoder_v1b_v3global_mid/`, NOT the `..._v1_mid/` heartbeat/output dir. Early-eval = load ckpt into `_make_student("mlp", X.shape[1], N_DIM_DEFAULT, ...)`, replicate the MID seeded split EXACTLY (`np.random.default_rng(7)`, perm, `n_he=min(round(V*HELD_FRAC), MID_HELD_CAP)`, `he_idx=perm[n_tr:n_tr+n_he]`), teacher via `_resolve_teacher_cache(None)`+`_load_teacher`, then `_semantic_unit(arm, c, c, Xhe, Xhe, 0, MID_PAIR_SAMPLE, seed+3)` for `GLOBAL_DENSE` (`_dense_sign_codes`) and `GLOBAL_BLOCK_K128` (`_encode_hard_block`). Gives DENSE-recovery WITHOUT waiting for the baseline arm. Gate: DENSE ~0.8 = fix WORKS -> sparsify + GPU FULL; 0.5-0.8 = partial -> fallbacks (bigger landmark set, k-means/farthest-point landmark SELECTION, KL objective, Partial-FC negatives); ~0.37 (v2-like) = objective still broken -> escalate R3/R4. **The cell ALSO prints a DENSE-spearman trajectory to stdout every 300 steps** (`_dense_spearman_quick` on a 1500-held subset) if that stdout log can be found.
- **RESEARCH VERDICTS (5 drills done, memos in `notes/research_drill_*_2026-07-04.md`):**
  - **Sparse-fidelity-frontier (LOAD-BEARING):** ~2%-active is NOT the binding constraint on 0.85. Feasibility is gated on the DENSE OBJECTIVE (R1) reaching ~0.88, NOT the sparsity level (4x-expansion SAE clears 0.85-equiv at 0.78% active). => **focus 100% on R1/the objective; R5 K=256 diagnostic is now LOW priority.** P_deflated 0.55.
  - **Distillation methods (4 lit-scans):** R1's fixed-teacher-landmark approach VALIDATED on every axis - it IS what SEED/CompRess do (frozen teacher = ZERO drift, the key advantage); landmark-MDS/Nystrom theory says 8k/180k landmarks is likely OVERSAMPLED for global reconstruction (risk = teacher spectral decay, not the L/N ratio); landmark distillation is the LOWEST code-collision risk (proxy losses collapse -> hash collisions; Anti-Collapse Loss confirms); fixed real-item landmarks best for REPRODUCING a teacher's geometry (vs learned proxies = separability). **Fallbacks if R1 falls short: (a) bigger landmark set, (b) k-means/farthest-point landmark SELECTION (not random), (c) KL-distribution objective (CompRess) instead of MSE-RKD, (d) Partial-FC negative-subsample.**
  - **Teacher-free (R3):** NOT viable now - needs 60-250x corpus density (1.6 -> ~100-400 atoms/entity). D1-now (keep BGE teacher) / R3-later. 2-stage milestone ladder.
- **USER DIRECTIVE (new, memory-saved):** RUNTIME PHASE-DIAGRAM REGIME-SWITCHING - the substrate can MOVE around the phase diagram during operation (experimentally supported); operate in one optimal regime per operation, shift for others. RELEASES the "one code optimal for everything at once" over-constraint - the encoder need not be globally optimal (semantic-optimal for retrieval, shift for composition). See `feedback_runtime_phase_diagram_regime_switching_per_operation_USER_2026-07-04`.
- **DASHBOARD FIXED + VERIFIED** (testbed `5b3e6d1b3`): the earlier "dead poller" was a DIRECTOR CHECKER ERROR (grepped `gpu_util` but `/api/system` used `util_pct`; freshness on `/api/health`). Dashboard was live all along; now aliased + verified (gpu 100%, encoder visible, 1 supervisor+1 worker). USER can hard-reload. **LOCAL GUI BUILT (USER request, replaces the web dashboard as primary monitor):** `tools/dash_gui.py` + `tools/dash_gui.bat` (commit `6d536b154`) -- single-file Tkinter window, imports `build_state()` from `tools/inflight_monitor.py` (no reimplemented polling), no web server / port / supervisor / poller-thread / browser. Non-blocking inline poll (7s), degrade-safe render, ALERTS banner + GPU + LOCAL experiments + queues/verdicts + runners. Testbed follow-up in flight: direct nvidia-smi SSH GPU fallback (removes the last soft dependency on the old dashboard's localhost poller) + 3 presentation optimizations (progress/phase, GPU ours-vs-BOINC, short names). Launch: `.venv/Scripts/python.exe tools/dash_gui.py` or double-click the .bat. Durable auto-restart root-cause fixed (broken scheduled-task launch pattern + \r\r\n wmic duplicate-detection no-op bug). ONE elevation-gated follow-up: `schtasks /change /tn hd_dashboard /tr "cmd.exe /c ...dashboard_launcher.bat"` (USER runs once elevated, for reboot-persistence).
- **RESEARCH-INGESTION (USER q):** we do NOT ingest research into the substrate - deliberately (a) substrate KNOWS NOTHING principle + (b) ingestion quality is gated on the very encoder we're fixing. Once the encoder works, distilling our own research IN is the "substrate as Director-KB dogfood" vision. Research currently lives in notes/ + Director memory.

---

## STEP 0 — first actions on pickup

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp
python d:/AI/hd-instrument/tools/inflight_monitor.py            # accurate live status (GPU, queues, runners, alerts)
grep -cE "2026-07-04" d:/AI/hd-instrument/data/substrate_index/{math,meta}/atoms.jsonl
cat d:/AI/hd-instrument/data/latest_landings.md | tail -20
```
Then read this file, then `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (the encoder plan).

---

## PRIMARY FOCUS: the concept encoder (USER load-bearing #1)

**Goal (USER-confirmed 4):** native perception — turn a concept into the substrate's own vector.
(1) OWN it (not borrowed BGE), (2) ~0.85 semantic cosine (from ~0.54 baseline), (3) ~2% sparse
(brain-like), (4) ALGEBRA must survive (bind/unbind/bundle stay clean).

**WHERE WE ARE — the distillation approach FAILED at full scale (real, verified negative):**
- v2 MLP FULL (177,899 concepts): BLOCK_K128 semantic spearman **0.31**, DENSE_SIGN 0.368,
  CHARPOS orthographic baseline **0.656** (baseline BEAT the trained arms). Keyed algebra 1.00 (fine).
- Eval verified FAIR (Skunkworks/exp_dev); teacher normalized on both caches -> bug ruled out.
- **Root cause (locked):** the RKD objective is IN-BATCH (512x512 over 160k concepts) -> graded
  near-neighbor geometry is never supervised at scale; the map learns bulk near-orthogonality only.
  Proof it's the OBJECTIVE not the sparsifier: DENSE (no sparsifier) collapsed too; rkd converged
  to a 2.4x-higher floor with lr fully decayed (not under-training).
- **Brain drill (USER "how does the brain do it"):** brain has NO external teacher (self-distills
  via hippocampal replay) and builds rich geometry FIRST, sparsifies AFTER (competitive k-WTA) —
  we did the opposite on both. Our external BGE teacher also violates the substrate-standalone anchor.

**THE FIX UNDER TEST — R1 global/landmark objective** (`notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md`):
- Anchor every concept to a FIXED ~4-8k landmark frame each step so global geometry IS supervised.
- Cell `experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`
  (commit `6662c5717`). MID-scale validation RUNNING locally (pid ~29376); watcher re-invokes on landing.
- **VALIDATION GATE: does DENSE recover to ~0.8 at intermediate scale?** If yes -> objective fixed ->
  then sparsify brain-style -> then GPU FULL. If no -> escalate to R3/R4 (brain-grounded self-teacher).
- **5x rescue battery** (sequenced, R1 first): R1 global-obj (running); R2 brain dense-first-then-sparsify;
  R3 internal self-teacher (wean off BGE); R4 predictive/temporal-contiguity over relation graph;
  R5 K=256 diagnostic (is 0.85-at-2% capacity-bound — a USER strategy call if so).
- **DEFINE SUCCESS:** DENSE recovers ~0.8 at scale (fix confirmed) -> BLOCK sparse code reaches ~0.85
  with algebra roundtrip intact. Honest caveat: 0.85 AT exactly 2% may be capacity-bound.
- **Discipline (Fix#28):** I over-framed the SMOKE's 0.82 as "capacity confirmed"; it was an easy
  3k-subset and did NOT scale. No capability claim before the FULL number.

---

## SECONDARY: physics-map (phase diagram) — honest + advancing

**Mechanism-moderation cross-term family CLOSED 4/4 as measurement artifacts** (Skunkworks `bf4408f2e` + `99a8228ef`):
P1 STORAGE x CLEANUP (was CG_META, DEMOTED), P8 (demoted), P6v2/P7v2 (paired range EXACTLY 0.0000).
Root: mechanisms are argmax-readout-DEGENERATE (bit-identical accuracy on identical inputs) -> cross-term
PROVABLY absent. **Any cell comparing cleanup mechanisms on argmax readout finds 0 by construction.**
**META-ATOM (durable):** unpaired max/range arm-comparison discriminators manufacture phantom cross-terms;
PAIRED trials (shared items/salts) OR a data-driven binomial null are MANDATORY. See memory
`feedback_paired_trials_mandatory_for_arm_comparison_discriminators_2026-07-04`.

**SURVIVED (real):** STORAGE main effect (0.93 gap), SCALE_FREE / TOPOLOGY_FREE / M-scaling / ALGEBRA_SCALES
laws, P9 N x L additive composition. **The parked M-sweep is a TRAP** (its axis is the degenerate mechanism
comparison) — do NOT run as written.

**GENUINE next experiment LANDED: probe_18** storage-advantage boundary, PAIRED SHARDED-vs-BUNDLED across
the cliff where SHARDED can actually move (its size/scaling were never measured — SHARDED was always
ceiling-pinned). SMOKE HARD_PASS (`b09826cd5`); **3-seed FULL all HARD_PASS**: STORAGE-advantage boundary
SCALES WITH N (delta_scales_with_N ~0.101 all 3 seeds, cv=1% -> MM_STANDARD by 14x margin; boundary rises
N512~0.866 -> N2048~0.934 -> N8192~0.967), F-axis scale-free (null). First genuine paired measurement
replacing the retired mechanism-mirage. **MM_STANDARD FILED** (Skunkworks `4a93d3496`, reproduced EXACTLY
off-disk cv~1% = 14-17x margin, N-axis 18-21x over null). **PRECISION (Skunkworks fix):** BUNDLED = 0.000
at ALL in-band cells (M=4800 >> Plate bound) -> delta == acc_SHARDED; the finding IS "the SHARDED
corruption-cliff LOCATION moves to higher tolerable corr as N grows; BUNDLED contributes nothing; the
storage advantage is TOTAL." Do NOT narrate as a gap between two moving arms. (Dispatch self-healed an SH-2 naming gap: `exp_<base>_core.py` not matched by
queue_add.sh auto-SCP — Testbed durable-fix candidate.)

---

## INFRASTRUCTURE / RELIABILITY

- **BOINC STOPPED on remote GPU (marsh@home) 2026-07-04 ~16:45Z (USER-authorized).** Was NOT a service -- autostarted via two HKLM\...\CurrentVersion\Run entries (boincmgr, boinctray); killed the process tree (incl PrimeGrid genefer22g GPU app) + removed both Run-key entries -> stays down across reboot, reversible, no data deleted. GPU freed: 100%util/1200MiB -> 0%util/742MiB(desktop residual), 59C->42C. Our runners untouched. **RE-ENABLE (run on that box or via SSH):** `powershell -Command "reg add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' /v boincmgr /t REG_SZ /d '\"C:\Program Files\BOINC\boincmgr.exe\" /a /s' /f; reg add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' /v boinctray /t REG_SZ /d '\"C:\Program Files\BOINC\boinctray.exe\"' /f; Start-Process 'C:\Program Files\BOINC\boincmgr.exe' -ArgumentList '/a','/s'"` (the two reg-adds alone restore autostart-on-logon; the Start-Process line also relaunches immediately). Implication: remote GPU now reads GENUINELY idle when we're idle -- the whole GPU is ours for R1 FULL + the diagnostic.


- **Reliable status tool: `python tools/inflight_monitor.py`** (never-silent alerts; reads fresh cache).
  Prefer it over the web dashboard.
- **Dashboard being fixed** (testbed in flight): dead GPU poller + duplicate supervisors/workers +
  structural blindness to direct-subprocess work (agent-launched runs bypass the queue -> showed "idle").
- **DURABLE ROOT CAUSE FOUND (the recurring reliability bug):** scheduled-task launch pattern
  (`cmd /c start /b launcher.bat` -> synchronous pythonw grand-orphan killed by the job object) + a
  buggy taskkill singleton loop (wrong wmic-csv delimiter) -> processes silently die AND stale copies
  accumulate. That accumulation caused the OS resource spike (WinError 1450) + the USER's recycle-bin
  corruption. Fix = match the working emitter launcher pattern (`start /B pythonw ...; exit /b 0`).
- **Machine cleaned:** killed 4 waste procs (a 68-CPU-hr hung infinite-loop debug script + superseded
  runs, ~2.8GB freed). Remote emitter/watchdog restored (cache fresh, GPU util flows).

---

## IN-FLIGHT (post session-restart ~2026-07-04 ~18:00Z; agent IDs are THIS session)

| agent | doing |
|---|---|
| orchestrator (a960d6) | dispatching the v3b batch-sweep cell (commit `20b4c6fbb`) to the FREE remote GPU via `queue_add.sh` (SCP, no origin push); SH-2 SCP-verify cell + `_seed_checkpoint.py`; arm landing monitor. **THE decisive encoder run.** |
| exp_dev (a56336) | cross-checkpoint retrieval-compatibility probe (reuse saved R1 checkpoints; continual-learning Q; HARD-FAIL <50%). Local, light. |
| research (ab6b80) | RANK the encoder 0.52->0.85 levers (landmark-selection / objective KL-vs-MSE / student-capacity / schedule) -> ordered fallback ladder + single top bet. |
| testbed (a0fb47) | hard-bound `build_state()`/inflight_monitor (>2min hang after restart -- likely SSH fallback or dead-feed socket w/o timeout); protects Director tool + GUI refresh. |

**DONE this session:** R1 paired verdict recovered (underpowered, not a real negative -- see LATEST STATE); BOINC killed (GPU free); local GUI built+launched (`dash_gui.py` commit `7a5ff16f1`); v3b decisive cell built+smoked+committed (`20b4c6fbb`, HARD_PASS). **probe_18** LANDED 3-seed HARD_PASS (MM_STANDARD filed).

**DISPATCH FACT (current setup):** remote GPU/CPU dispatch via `tools/orchestrator/queue_add.sh` is SCP-based -- it SCPs the cell+prereg+siblings to marsh@home and the runner executes the SCP'd file, so a LOCAL commit is sufficient and NO origin/main push is needed (sidesteps the harness default-branch-push gate). `dispatch_request.sh` is the OTHER path that DOES require origin/main. See memory `reference_remote_dispatch_queue_add_is_scp_based_no_origin_push_needed_2026-07-04`.

---

## USER-LOCKED CONSTRAINTS (standing — obey)

- **Encoder = load-bearing PRIMARY** (4 goals above).
- **NEVER STAND** (USER emphatic 2026-07-04): while priority runs, dispatch parallel work / own research
  lane; "standing by / monitoring / nothing needs you" is a FORBIDDEN turn-ending state.
- **PAIRED trials mandatory** for arm-comparison discriminators (or data-driven binomial null).
- **Verify off-disk before propagating** (Fix#28); no capability claim before the FULL number.
- **SMOKE only local_cpu**; GPU FULL once-per-stage; heavy remote via Orchestrator (proper queue/runner,
  NOT raw ssh — raw ssh children die on disconnect).
- **Substrate stands alone** (no external LLM long-term); substrate KNOWS NOTHING (CG = mechanism proof).
- **Intuitive summary at END** (no jargon, with importance/implications/position). **Full-auto = make the call.**
- **Brain = best-in-class reference**; higher prior for brain-grounded mechanisms.
- Full memory index: `C:/Users/marsh/.claude/projects/d--AI/memory/MEMORY.md`.

---

## KEY FILES + COMMITS

- Encoder rescue plan: `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md`
- Brain drill: `notes/research_drill_brain_grounded_concept_encoding_how_does_brain_do_it_2026-07-04.md`
- Phase-diagram roadmap: `notes/research_phase_diagram_genuine_open_questions_post_cross_term_collapse_2026-07-04.md`
- Encoder v3 (R1): `experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py` (`6662c5717`)
- probe_18: `experiments/exp_stage1_regime_probe_18_storage_advantage_boundary_paired_v1_core.py` (`b09826cd5`)
- Monitor: `tools/inflight_monitor.py`

---

## CERT / SESSION STATE (2026-07-04)

~16 math + ~7 meta atoms today. Net cert this session: **CG -1** (Probe 1 cross-term demote), **MM +several**
(P1 storage-survivor, family-closure, paired-trials meta, probe atoms). The demotion is a real integrity
correction (a wrong top-tier claim retired with airtight evidence), not a loss.

---

## LONGER-TERM FOUNDATIONAL (in parallel where sensible)

1. **Wean off the external teacher (BGE)** -> internal self-supervised learning (brain-grounded; honors
   substrate-standalone). This is R3/R4 AND a foundational bet.
2. **Enrich the substrate's own knowledge** (KB is thin ~1.6 atoms/entity) -> makes teacher-free learning viable.
3. **Cortex layer** (substrate acts on its own findings; atoms become active guardrails) — the prior primary
   focus (cortex-2 arc); resumes once the encoder is solid.

---

## THE INTUITIVE VERSION

We're building the substrate's own sense of meaning — the foundation everything else sits on. The obvious
approach (copy a strong outside model's meaning into a sparse code) worked small but failed at full scale,
worse than a spelling baseline. We diagnosed exactly why (the training only ever compared a handful of
concepts at a time, so it never learned the big-picture map) and proved it's a real failure, not a bug. The
brain confirmed our mistake: it has no outside teacher and builds the rich map first, then sparsifies. The
fix — give every concept fixed landmarks to orient against — is validating now; the make-or-break number
lands in ~2 hours. Alongside, we made the physics map honest (retired a 4-experiment statistical mirage,
started a genuine replacement) and found the root bug behind the recurring machine-reliability problems.
The parts we got right (sparse code + algebra) work perfectly; the broken part is the training method, which
is the changeable part. Confident but not certain until the number lands.
