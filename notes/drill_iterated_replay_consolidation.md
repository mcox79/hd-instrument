# Drill: iterated interleaved replay consolidation — wiring design (2026-07-29)

Research/design drill (Director, main thread). NOT built/dispatched/banked. Row 9 of
`notes/component_brain_fidelity_ledger.md` (CONSOLIDATION/sleep, status UNFAITHFUL, faithful
version ISLANDED). This drill is a RE-DISPATCH of the same task after an overnight process exit
lost the prior run's output; it reconciles with and extends the pre-existing
`notes/consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md` (found already on disk,
same day-before drill, same root gap) rather than re-deriving from scratch. Where that note
already answers a sub-question, this note cites it and adds the WIRING-level detail (function
signatures, call sites, can-fail bands) needed to actually build the swap.

**HONEST PRIORITY (stated up front, per task instruction):** consolidation is NOT the current
bottleneck. Per `notes/component_brain_fidelity_ledger.md` EXECUTION SEQUENCE, rows 4/5
(readout/comprehension) are FIRST and row 6 (working memory, ABSENT) is SECOND; consolidation
(row 9) is FOURTH, explicitly "on-deck (not current bottleneck)." This drill is scoped
READY-TO-BUILD, not queued for immediate dispatch — it should be picked up once readout/WM work
lands or frees up capacity, per the sequencing note both this doc and the 07-28 predecessor agree
on.

## 1. Biology vs our mechanism — the four axes of difference (restated, tightened)

Sources: McClelland/O'Reilly 1995 CLS; Marr 1971 (hippocampal one-shot binding);
Wilson & McNaughton 1994, Buzsaki 1989/2015 (SWR replay); Diba & Buzsaki 2007 (reverse replay);
Tse/Morris 2007/2011 (schema-gating, the "PRE" paradigm); Frey & Morris 1997 (synaptic
tagging-and-capture). These are recalled landmarks, NOT re-verified this drill (no fresh web
fan-out run) — treat as reasoning aids per the lit-scan calibration discipline, same caveat the
07-28 predecessor applied.

1. **ONCE vs ITERATED.** Brain: cortex is written only via OFFLINE REPLAY, many small repeated
   exposures per item, spread across a sleep/rest phase. Us (all versions v1/v2 plain-average,
   precision-Kalman, CA3-single-shot-denoise, v4/v5 fast-episodic softmax blend): exactly ONE
   update per concept per sleep cycle, whatever the store's mentions currently look like.
2. **AVERAGE-ALL vs SELECTIVE-REPLAY.** Brain: one sampled/cued episode reactivated and
   Hebbian-written at a time, via CA3 pattern-completion from a partial SWR cue. Us: ALL
   accumulated mentions for a concept folded together in a single mean/Kalman-fold/softmax-blend
   operation — mathematically `sum(w_i * x_i)` computed once, regardless of whether weights are
   uniform, precision-derived, or similarity-derived (v4/v5's softmax blend is still this same
   operation-class, just "one level removed" per the 07-28 note's mechanistic argument in section
   2 row 111-127 — a specific fact never dominates because it's never treated differently from a
   routine repeat in the SAME timestep).
3. **UNGATED vs SCHEMA-GATED.** Brain: schema-CONSISTENT information assimilates fast (can be
   near one-shot, Tse et al.); schema-INCONSISTENT information takes the slow hippocampal-
   dependent route or is rejected/deferred. Us: gate on internal coverage/coherence of a
   concept's OWN mentions (`new_conf >= override_min`), never on fit to the concept's EXISTING
   relational neighborhood in the foundation graph — the wrong gating signal (agreement among new
   evidence, not fit to prior knowledge).
4. **UNIFORM vs PE-BUDGETED.** Brain: replay priority and encoding strength scale with
   surprise/prediction-error/salience (novelty-gated dopaminergic/noradrenergic plasticity);
   well-predicted repeats get little further consolidation resource. Us: every mention
   participates in the fold/blend with equal or purely similarity-derived weight — no
   surprise-based prioritization anywhere in the pipeline.

A fifth, second-order axis (not this drill's build target, sequenced after #1-4): synaptic
tagging-and-capture — a novel trace is flagged and only durably committed once CAPTURED by a
later, separate consolidation event, i.e. commitment is delayed and cross-phase, not immediate.

## 2. Prior-work inventory (cite + reuse, do not rebuild)

- **`hdlab.hippocampal_encoder.cls_discrete_budget_consolidate`** (read on disk, lines 337-419):
  CERTIFIED HARD_PASS / CHAIN_GRADE-eligible primitive from `exp_cls_ca3complete_consolidation_v1`
  (commit 92e01cf3f; `math::CHAIN_GRADE_cls_ca3complete_consolidation_v1_INTEGRATE_NEW_KNOWLEDGE
  _WITHOUT_FORGETTING`; measured gap ~0.913 old-retention, FULL vs NAIVE, all seeds, at
  `data/exp_cls_ca3complete_consolidation_v1/metrics.json`). Signature:
  `(fast_store[D,D], replay_keys[m,D], concept_codebook[V,D], slow_store[D,D], *, budget:int,
  cue_rho=0.70, ca3_complete=True, ca3_temp=4.0, ca3_alpha=0.5, ca3_max_steps=6, rng=None,
  seed=0) -> dict{slow_store, n_replayed, budget, budget_respected, ca3_complete}`. Mechanism:
  fixed discrete per-phase budget B (first min(m,B) replay_keys), SWR partial-cue
  (`cue = rho*key + sqrt(1-rho^2)*noise`), readout = `cue @ fast_store.T`, optional
  `iterative_cleanup` (the same CA3-completer as the certified cell) against `concept_codebook`,
  write into `slow_store` via `value.T @ keys`. This directly answers axes 1 and 2 above (offline,
  discrete-budget, per-item replay instead of fold-all-at-once) — it is EXACTLY the certified
  ISLANDED primitive the ledger's row 9 names. It composes `iterative_cleanup` from
  `hdlab.iterative_attractor` — already imported in `hippocampal_encoder.py`, no new dependency.
- **`hdlab.continual.replay_cycle` / `nrem_replay_decorator`** (read on disk): a DIFFERENT,
  earlier NREM-replay primitive — "PARTIAL MITIGATOR of continual-write drift, NOT a chain-grade
  SOLVER" (module docstring line 132-133). Replays a UNIFORM RANDOM `replay_frac` (default 0.2,
  cell-validated at replay_every=100) of a trace buffer via re-Hebbing; validated bound:
  drift_reduction +0.57 absolute (0.88 -> 0.31 final_forget) at N=4096, 2500 continual-write
  cycles (`math::T3/EXP_substrate_continual_NREM_replay_v1_proven_bound_replay_reduces_drift
  _0p57_abs`). Distinct from `cls_discrete_budget_consolidate`: no discrete fixed budget (a
  FRACTION not a count), no CA3-completion, no schema-gating, uniform-random selection (axis 4
  still ungated). Module comment (line 205-206) already flags "NREM replay + selective REM
  downscale composition is the path to chain-grade" as an open follow-up — i.e. this primitive is
  itself explicitly PARTIAL and was never claimed to solve schema/surprise-gating. Relevant as a
  SECOND, cheaper reference point (drift-reduction bound) but `cls_discrete_budget_consolidate` is
  the more complete, more certified, and more directly applicable primitive for THIS wiring (it
  already has the old-vs-new retention framing the brain metric below needs, whereas
  `replay_cycle`'s bound is drift-reduction on a single trace type, not old-vs-new interleaving).
- **`exp_unified_self_learning_loop_v4.py` / `v5.py`** (read on disk): the self-learning loop's
  current consolidation call sites — `_sleep_consolidate_v5` (line 458), dispatching to
  `_consolidate_candidate_v5` per mode (`plain`, `precision`, `fast_episodic`), and
  `_fast_episodic_read` (line 361) + `_sparse_keys` (line 340) — the DG-analog sparse key
  construction (fixed random Gaussian expansion + k-WTA, common-mode-centered per v5's fix,
  STEP-0 measured raw cross-concept cos 0.9444 -> -0.0645 centered). This key space and the
  `BIND_HRR_position` per-mention readout are SETTLED per the 07-28 predecessor and this drill
  does not re-open them (see 3.2 below).
- **`notes/consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md`**: same-topic drill from
  the day before (found already on disk at drill start — this is a genuine duplicate-topic
  situation, not a KB-check miss, since it was written the same session/day this ledger row was
  scoped). It already contains a materially complete design (section 3, candidate menu #1-5;
  section 5, a full v6 experiment sketch: `unified_self_learning_loop_v6_replay_consolidation`).
  This drill AGREES with that design and does not contradict it; the added value here is (a)
  reconciling `continual.py`'s replay_cycle as an explicit second prior-art primitive (asked for
  in this drill's dispatch, not covered in the predecessor), (b) sharpening the can-fail bands
  into concrete numeric thresholds relative to the certified cell's own bar, and (c) the honest
  priority framing. Where the two disagree on nothing, defer to the predecessor for prose detail.

## 3. Wiring design (integration, not invention)

**Composition: #1 (discrete-budget replay) + #2 (schema-gate) + #3 (surprise-order), matching the
07-28 predecessor's "cheapest defensible next build."**

### 3.1 Data flow (new `replay_schema_gated` mode inside `_sleep_consolidate_v5`)

1. Each concept's accumulated per-mention traces already live in the fast episodic store, keyed
   by `_sparse_keys` (reuse verbatim — brain-faithful DG pattern separation, already centered).
2. At each sleep phase, for each concept `ci` with new mentions since the last phase:
   - Compute `surprise_i = 1 - cos(mention_rep_i, slow_store[ci])` for each pending mention (axis
     4 fix) — this needs `slow_store[ci]` from the PREVIOUS phase, already available (it's the
     concept's current committed rep).
   - Sort `replay_keys` for this phase by `surprise_i` descending (high-surprise first;
     "surprise-ordering actually reorders" is one of the new self-tests, see 3.3).
   - Call `cls_discrete_budget_consolidate(fast_store, replay_keys=<surprise-ordered keys>,
     concept_codebook=<train-side foundation reps, the SAME leak-proof `base_clean` array
     `_ca3_complete` already uses>, slow_store, budget=B, ca3_complete=True, seed=<phase seed>)`
     with a small fixed `budget` (start B=3-5 per concept per phase, matching the certified cell's
     validated regime) — this is axis 1/2's fix: offline, discrete, per-item, not fold-all.
3. **Schema-consistency gate (axis 3 fix), applied to the completion OUTPUT before commit:**
   compute a consistency score between the CA3-completed value and the concept's existing
   TRAIN-side relational neighborhood in the foundation graph (reuse whatever adjacency
   `relational_eval` already loads — same object, train-side only, never the held-out scored
   edges — this is the SAME leak-proofness invariant the v2 pre-reg and 07-28 predecessor both
   enforce). If consistent: commit to `slow_store` immediately (fast-track, matches Tse et al.'s
   near-one-shot schema-consistent assimilation). If inconsistent: do NOT commit this phase;
   leave the item in the fast store with elevated future-replay-priority (tag), to be replayed
   again next phase — UNLESS a patience counter (e.g. 3 consecutive inconsistent phases) is
   exceeded, in which case force-commit anyway (avoids permanent starvation of genuinely novel
   facts with no existing schema neighbors, an edge case the predecessor's section 3.1 item 2
   also names).
4. Interleaving old+new: because `cls_discrete_budget_consolidate`'s budget is shared across
   BOTH previously-committed concepts up for re-consolidation and brand-new concepts (not one
   dedicated budget per concept, entirely separate from other concepts' updates the way v1-v5's
   per-concept fold is), this is where axis-1's "interleaved" property actually enters — the
   certified cell's own HARD_PASS claim (0.913 gap) is specifically about retaining OLD material
   while acquiring NEW under one shared discrete budget, which is the exact continual-learning
   signature current arms cannot even express.

### 3.2 What stays fixed (do not re-litigate — settled by v5, confirmed again this drill)

- v5's `BIND_HRR_position` per-mention encoding (order-sensitive, no bolt-on reader) stays the
  input representation the new consolidation mode consumes. Do not reintroduce pooled centroids
  anywhere in this pipeline.
- v5's centered `_sparse_keys` DG key space stays the cue/key space fed to
  `cls_discrete_budget_consolidate`'s `replay_keys` argument.
- Leak-proofness: schema-consistency lookups and `concept_codebook` are TRAIN-side only.

### 3.3 New self-tests this wiring specifically requires (mechanism-correctness, not capability)

1. Schema-consistency score is measurably HIGHER for coherent than scrambled mentions on
   synthetic toy data (if this fails, the gate cannot be trusted downstream — check BEFORE
   trusting any capability-level result).
2. Surprise-ordering actually reorders: a high-surprise synthetic mention is replayed before a
   low-surprise one within the same budget-limited phase (direct unit check on the sort).
3. Discrete-budget-respected still holds when driven by loop-supplied keys/codebook rather than
   the certified cell's own synthetic ones (re-verify `budget_respected` field from
   `cls_discrete_budget_consolidate`'s return dict is True across a phase).

## 4. Own metric + can-fail bands (vs the current averaging baseline)

**Brain metric (per ledger row 9): interleaved OLD-vs-NEW retention — integrate new WITHOUT
catastrophic forgetting. NOT a downstream task-win.** Averaging-based consolidation (v1-v5) has
no shared replay budget and no old/new interleaving concept, so it cannot even be scored on this
metric in a meaningful way except as the naive/no-consolidation-discipline comparison point.

**Discriminator design (three arms, readout+encoder held fixed across all, same frozen ckpt +
BIND_HRR_position per the 07-28 predecessor's fairness design, section 4):**
- `plain` (v1/v2 baseline) — sanity-check arm, expected to reproduce the KNOWN negative.
- `fast_episodic` (v4/v5 current-best softmax-blend) — must be BEATEN, not merely matched, or
  the new mechanism (more moving parts: budget, surprise-order, schema-gate) has not earned its
  complexity.
- `replay_schema_gated` (this design) — candidate under test.

**PASS band (own-metric, brain-faithful gate):**
- Old-retention gap (retained-old-AUC under `replay_schema_gated` MINUS retained-old-AUC under a
  NAIVE-no-consolidation-discipline control, analogous to the certified cell's 0.913 own bar) must
  be POSITIVE and non-trivial — propose >= 0.15 absolute as a first can-fail floor (much lower
  than the certified cell's synthetic 0.913 because this drill's setting is noisier/real corpus,
  not synthetic; treat 0.913 as a ceiling reference, not the bar to hit here).
- SIMULTANEOUSLY, new-concept LOW-slice comprehension-specific gain must beat `fast_episodic`'s
  current bar (LOW gain > `fast_episodic`'s LOW gain, matching v4/v5's own HP_GAIN_MARGIN=0.02
  convention) — both must hold together (retention AND acquisition), not either alone; that
  simultaneity IS the brain's actual signature capability and the sharper bar than AUC-gain alone.
- Schema-consistency scores must differ coherent > scrambled (self-test 3.3.1) BEFORE the above is
  trusted — this is a discriminant-validity precondition per the predecessor's DEFLATE-null
  discipline (section on "DEFLATE null" in 07-28 note): a positive that ties this precondition is
  not a real positive.

**FAIL band (honest negative, do not spin as ceiling):** `replay_schema_gated` ties or loses
`fast_episodic` on EITHER retention or acquisition even though the schema-gate and surprise-order
self-tests (3.3.1, 3.3.2) pass mechanistically. Per the 07-28 predecessor's DEFLATE-null section,
the honest read in that case is NOT "consolidation solved/unsolvable" but one of: (i) insufficient
replay dosage at available data density (check n_mentions/concept LOW-slice median before
concluding), (ii) the AUC+cloze metric under-detects real acquisition (ledger row 11's own
GATING caveat), or (iii) the 0.73 coherent-vs-scrambled bind-readout separation is real but too
weak a signal-to-noise ratio for a mean-field metric — not a consolidation-mechanism failure.

**MIDDLE/SATURATION check:** if ALL THREE arms (plain, fast_episodic, replay_schema_gated) show
near-identical retention AND near-identical LOW-slice gain, that is a saturation/no-discriminator
signal (the harness itself isn't sensitive to consolidation-mechanism differences) — re-run the
`plain` sanity arm specifically to confirm it still reproduces its OWN known negative before
trusting any of the three numbers.

## 5. Build sizing (for when this is picked up off-deck)

Per the 07-28 predecessor's naming: `unified_self_learning_loop_v6_replay_consolidation`,
reusing v5's cell wholesale (frozen ckpt, `BIND_HRR_position`, centered `_sparse_keys`, 7-arm
LOW-MID-HIGH-ALL exposure design, leak-proof `relational_eval`) and swapping ONLY the
consolidation mode per section 3 above. Estimated build cost: wiring + ~30-60 new lines around an
existing call (surprise-sort + schema-consistency check), zero new certified primitives required
(both `cls_discrete_budget_consolidate` and `iterative_cleanup` already exist and are certified).
This is genuinely cheap relative to the readout/WM work ahead of it in the execution sequence —
the reason to defer is queue priority (rows 4/5/6 ahead of row 9 on the ledger), not build cost.

## 6. Summary for the ledger

Row 9 status stays UNFAITHFUL/ISLANDED until this wiring actually lands (nothing built/dispatched
this drill). "FORMALIZE next" entry unchanged: wire the certified replay engine + surprise-budget
+ schema-gate — this note supplies the concrete function-level plan for that wiring plus numeric
can-fail bands, so the next pickup can go straight to cell-authoring without a fresh design pass.
