# Director BACKUP — CURRENT STATE 2026-07-04 (clean rewrite; supersedes all prior)

**Read end-to-end first. This is a clean consolidation. The prior amendment-stacked BACKUP
(`director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-03_LATE.md`) is SUPERSEDED — do not use it.**
Agents are ONLINE (the weekly rate-limit that throttled spawns earlier today has lifted).

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
replacing the retired mechanism-mirage. -> Skunkworks landed-VET for `EMPIRICAL_STORAGE_ADVANTAGE_BOUNDARY_SCALES_N_v1`
MM_STANDARD atom (in flight). (Dispatch self-healed an SH-2 naming gap: `exp_<base>_core.py` not matched by
queue_add.sh auto-SCP — Testbed durable-fix candidate.)

---

## INFRASTRUCTURE / RELIABILITY

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

## IN-FLIGHT (as of ~2026-07-04 15:00Z)

| agent | doing |
|---|---|
| R1 (a984645) + watcher | encoder global-objective MID validation (pid ~29376); DENSE-recovery number ~2h |
| Part B (a03cf07) | H-SCALE confirmation sweep (mostly moot — H-BUG already ruled out) |
| testbed (a8cfbb) | dashboard poller/duplicate fix + durable auto-restart root-cause fix |
| orchestrator (aada38) | probe_18 3-seed FULL dispatch + landing monitor |

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
