# Director BACKUP — CURRENT STATE 2026-07-04 (clean rewrite; supersedes all prior)

**Read end-to-end first. This is a clean consolidation. The prior amendment-stacked BACKUP
(`director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-03_LATE.md`) is SUPERSEDED — do not use it.**
Agents are ONLINE (the weekly rate-limit that throttled spawns earlier today has lifted).

## >>> LATEST STATE ~16:20Z (read first) <<<

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

## IN-FLIGHT (as of ~2026-07-04 16:30Z; agent IDs are THIS session)

| agent | doing |
|---|---|
| R1 run (pid 29376) | encoder global-objective MID validation; GLOBAL arm DONE, in_batch baseline at ~1400/1800 -> full metrics.json ~10-12 min out |
| exp_dev (a00368) | R1 EARLY-READ: DENSE+BLOCK spearman off the finished global-arm checkpoint (beats the full run) |
| testbed (a0fb47) | local GUI monitor (`tools/dash_gui.py`, commit `6d536b154`) -- adding direct nvidia-smi SSH GPU fallback (kill the last web-dashboard dependency) + 3 Director presentation optimizations (progress/phase on local experiments; GPU ours-vs-BOINC disambiguation; short anchor names). Director launches on its return. |

**probe_18 (phase-diagram) LANDED** 3-seed FULL all HARD_PASS (see SECONDARY section); MM_STANDARD filed. No longer in flight.

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
