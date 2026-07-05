# exp_dev hand-off — research: capability-optimization priority ranking (control / comprehension / reasoning)

**Filed-by:** research sub-agent, 2026-07-05, per 5x-drill angle 1/5 (capability-optimization priorities) task.

**Trigger:** `notes/research_capability_optimization_ranking_2026-07-05.md` — ranks the not-optimized capabilities by
capability-gain x feasibility x glass-box-LLM-value and specs the top-1/top-2 next experiments. Read that note in full
first; this file names anchors + pointers only, no experiment design.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. If present, this hand-off still stands (research
dispatches are allowed while paused) — exp_dev should treat these as queued-but-gated until resume.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHOR + POINTERS only. exp_dev designs ALL of:
exact seed count, queue tier, smoke profile, FULL profile, and final HARD-PASS/HARD-FAIL bands (the research note's bands
are a starting recommendation, not binding).

**IMPORTANT — do not duplicate in-flight work:** `exp_pfc_gate_cfrpe_deeper_regime_v1` was RUNNING LOCALLY (pid observed
via `tools/inflight_monitor.py`) at the time this note was written, and its smoke is already on disk at
`data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json`. Check whether its FULL has landed before firing anchor #1
below — anchor #1 is the NEXT cell after that one, not a replacement for it.

---

## Anchor candidates (rank-ordered)

1. **`exp_pfc_gate_branching_depth_entropy_grid_v1`** (TOP PRIORITY — cheapest, most decisive, directly reframes CONTROL)
   - Anchor pointer: `notes/research_capability_optimization_ranking_2026-07-05.md`, section "#1 CONTROL" + "Cheap
     decisive test".
   - Substrate-product reading: the in-flight `..._deeper_regime_v1` cell's OWN smoke already falsifies its headline
     hypothesis (SR-horizon/gamma extension: gonogo is bit-identical across gamma at both tested branching levels) and
     confirms a different one wired in only as a side "fairness lever" (branching factor n_ops 4->2 at fixed depth=6
     triples closure). This anchor formalizes that into a proper `n_ops={2,3,4} x depth={4,5,6,7,8}` grid at FIXED
     gamma=0.85 (drop gamma as an axis, it's empirically inert), fitting closure/gonogo_lift against depth-alone vs
     n_ops-alone vs `log2(n_ops)*depth` (Hick's-law-generalized decision-entropy). Reuses the existing anchor's
     trainer/harness — no new architecture.
   - Tier hint: CPU/GPU-plausible at the existing anchor's scale (N=8192) — same cost class as `pfc_gate_cfrpe_
     trained_v2`'s FULL (elapsed_s ~1685 on that run). exp_dev's call on queue tier.
   - Why now: the smoke evidence is already collected and clean (3x effect, exact gamma-tie); this is confirmatory-
     grid-building, not speculative.
   - Recommended bands (exp_dev may adjust): HARD-PASS entropy-product model beats depth-alone by >=0.15 Spearman-rho
     margin, >=3 seeds, anti-tautology `reach_tcos_corr` gate held (reuse v2's own discipline). HARD-FAIL depth-alone
     matches/beats the entropy model (op2_d8 does not beat op4_d5).
   - P_deflated = 0.50 (capped, novel-synthesis rule; raw prior ~0.70 given the pre-existing smoke signal).

2. **`exp_pfc_gate_hierarchical_options_v1`** (follow-on brain-component build, gated on #1's HARD-PASS)
   - Anchor pointer: same research note, "On HARD-PASS, the natural follow-on build" paragraph.
   - Substrate-product reading: a genuinely NEW brain-component (not an analysis cell) — a two-level Go/NoGo gate,
     top-level selects among <=4 subgoals/macro-ops, each realized by a depth<=4 low-level gate (matching the already-
     PROVEN-at-depth-4 envelope from `pfc_gate_cfrpe_trained_v2`). Brain-grounded: Sutton-Precup-Singh options (1999),
     Botvinick-Niv-Barto HRL (2009), Frank-Badre corticostriatal HRL. This is the "missing hierarchy" analog to the
     "missing training signal" thesis that already worked once this session (the cfrpe-RPE Go/NoGo gate moved
     CONTROL from HARD_FAIL to PROVEN-at-depth-4) — same BRAIN-COMPONENT-DRIVEN pattern, next installment.
   - Tier hint: likely GPU (two-level trainer, more moving parts than #1). exp_dev's call.
   - Why now: only fire AFTER #1 confirms branching-factor is the real driver — if #1 HARD-FAILs, this follow-on's
     premise (hierarchy fixes depth by reducing branching-per-gate) needs re-deriving, don't fire blind.
   - Recommended bands: HARD-PASS hierarchical depth-8 closure >= 80% of native depth-4 closure (target derived from
     V1200_d4's 0.661 -> >=0.53 at hierarchical depth-8). HARD-FAIL hierarchical depth-8 closure <= flat single-level
     gate's own depth-8 closure (hierarchy adds nothing).
   - P_deflated: not yet assigned (gated on #1's outcome; the research note treats this as conditional, not a
     standalone pre-registered P).

3. **COMPREHENSION shared/overlapping-vocabulary retest** (co-equal priority with #1 by the research note's ranking,
   but not yet cell-authored — a spec, not an anchor name)
   - Anchor pointer: same research note, "#2 COMPREHENSION" section + its "Falsifiable predictions" entry.
   - Substrate-product reading: `exp_comprehension_envelope_superposition_vocab_v1`'s banked HARD_PASS (17/20
     full-parse) was measured under a `V_per_role_disjoint_partition` design (each role's candidate fillers are a
     private, non-overlapping vocabulary slice). An independent psycholinguistics lit-scan found this structurally
     avoids the dominant, well-replicated driver of real comprehension difficulty (similarity-based cue-overload /
     fan-effect interference among competing fillers — Van Dyke & McElree 2006; Jäger, Engelmann & Vasishth 2017;
     Anderson's fan effect). Real language has shared/overlapping vocabulary across roles; the current envelope may
     be measuring an easier-than-real regime. exp_dev should design a new cell (reusing the existing envelope cell's
     GSBC pool/harness) that draws role-fillers from a SHARED pool with controlled competitor-count/cue-overlap,
     re-measuring where the D/V cliff actually sits.
   - Tier hint: reuses existing harness (same GSBC_EXPAND2X pool, same classifier shape) — likely CPU-plausible at
     smoke, same cost class as the original envelope cell (elapsed_s=12.0 at FULL for that cell — cheap).
   - Why now: co-equal to #1 in the research note's ranking (a MUST-HAVE validity question, not polish) but has no
     pre-existing smoke/partial data the way #1 does — pure new-cell design work, hence ranked #3 by immediate
     buildability even though the research note ranks it #2 by importance.
   - Recommended bands: HARD-FAIL-of-current-tier (i.e., disjoint-vocab design didn't matter) = full-parse still
     holds >=15/20 cells under shared vocab with matched competitor count. HARD-PASS-of-hypothesis (i.e., found a
     real, bigger gap) = full-parse envelope shrinks to <12/20 cells once fillers share a pool — an honest negative
     on the previously-banked comprehension tier, valuable either way.
   - P_deflated: not yet assigned (no cell exists yet; exp_dev's pre-flight should set this per its own read of the
     lit-scan evidence in the research note).

---

## Context pointers (pointers, not summaries)

- `notes/research_capability_optimization_ranking_2026-07-05.md` — this cycle's full ranking + brain-mechanism
  grounding (read this first, in full).
- `data/exp_pfc_gate_cfrpe_trained_v2/metrics.json` — the depth-4-proven CONTROL FULL (fair regimes: V1200_d4,
  V2400_d4 only; degrades to closure=0.073 at V2400_d6, unfair-baseline).
- `data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json` — the in-flight cell's smoke (gamma-tie + n_ops-effect,
  the direct evidence base for anchor #1). CHECK WHETHER ITS FULL HAS LANDED before firing #1.
- `experiments/exp_pfc_gate_cfrpe_deeper_regime_v1.py` — source cell to adapt/extend for anchor #1 (its docstring
  already contains the gamma/SR-horizon hypothesis derivation and the n_ops fairness-lever rationale; reuse its
  trainer, drop gamma as a swept axis).
- `data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json` — REASONING's MIDDLE_BAND (ranked #3, not gated here).
- `data/exp_comprehension_envelope_superposition_vocab_v1/metrics.json` + `experiments/exp_comprehension_envelope_
  superposition_vocab_v1.py` — the existing comprehension envelope cell to adapt for the shared-vocab retest (anchor
  #3 above); its docstring's `vocab_axis` field is the exact line to change.
- `notes/research_5x_drill_reasoning_spec_and_brain_mechanism_2026-07-05.md` — prior brain-mechanism drill for
  REASONING, reused not re-derived by this cycle's note.
- `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md` — honest scoreboard this ranking corrects two
  stale premises against (PERCEPTION and INTEGRATION are CLOSED, not open candidates — do not dispatch anything for
  them from this hand-off).
- Pause state line: check `data/orchestrator_paused.flag` at dispatch time.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke (starting bands
  recommended above; exp_dev owns final numbers).
- Smoke gate exercises the SAME code path as FULL per [[feedback-smoke-code-path-must-exercise-same-branches]].
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance (>=3 seeds minimum, matching the existing anchors' convention).
- Anti-tautology gate (`reach_tcos_corr`) carried forward for anchor #1/#2 per the existing CONTROL cells' own
  discipline — do not drop it just because this is billed as a "grid" cell.
- Queue routing per Tier A/B/C in `agents/exp_dev.md` Section 0.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code.
- status_log entry with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: whether the in-flight `..._deeper_regime_v1` FULL needs to land first (check before firing
anchor #1), exact seed count, queue tier, ETA, smoke profile, FULL profile, and final HARD-PASS/HARD-FAIL/MIDDLE bands
for all three anchors (the research note's bands are starting recommendations, not binding). If exp_dev's own
pre-flight check finds the gamma-tie or branching-effect claims don't hold up under direct re-read of the smoke
metrics.json (independent verification is expected, not optional), that supersedes this hand-off's framing — report
the discrepancy rather than proceeding on a stale premise. Anchor #3 (comprehension) has no cell yet; exp_dev owns
the full cell design, not just the parameters.
