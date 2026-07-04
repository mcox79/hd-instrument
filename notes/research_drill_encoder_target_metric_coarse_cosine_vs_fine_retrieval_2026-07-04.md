# Research Drill: What Metric IS the 0.85 Goal, and Is the Gap Coarse or Fine? (2026-07-04)

**Author:** Director (Research)
**Trigger:** LOAD-BEARING metric-definition question. First honest measurement (in-batch-RKD-only,
NCE-off, FINAL step, TEST set, no best-ckpt cherry-pick) landed `hi80_cos=0.832` (near 0.85) but
`ret_agree10=0.21` (weak). Need to resolve: which metric IS the stated 0.85 goal, what gates quality
for retrieval vs composition vs cortex-2 atom-consultation, and whether the fine-retrieval gap is a
K=128 code-resolution ceiling or a training/objective gap.
**Method:** internal archaeology only (grep/read of notes, PROGRESS.md, memory index, git-adjacent
on-disk metrics.json; NO internet this cycle per explicit instruction) + off-disk direct read of the
metrics.json artifacts that produced the numbers in the trigger, plus conceptual synthesis against
the USER-locked runtime-phase-diagram-regime-switching directive.
**Calibration:** archaeology findings below are DIRECTLY VERIFIED on-disk facts (not extrapolated) —
confidence is high, not lit-scan-deflated. The Part 3 dual-attribution and the Part 2 architecture
recommendation ARE novel synthesis and are P-capped/deflated per [[feedback-lit-scan-calibration-penalty]]
even though no external lit was searched this cycle (same discipline applied to internal novel-synthesis
claims). Do NOT dispatch experiments (per instruction) — this is a definitional/diagnostic memo.

---

## HEADLINE

**The literal 0.85 target IS a coarse cosine-to-gold metric, and that goal is nearly closed
(hi80_cos 0.832, best-checkpoint 0.857) — but a second, never-formally-targeted fine-retrieval metric
(ret_agree10) is wide open at 0.21, and an on-disk zero-training diagnostic proves this is NOT purely
a K=128 resolution ceiling: the code itself could support ret_agree10 up to ~0.48 at K=128 (measured,
full 177,899-concept cache) even with a PERFECT untrained linear map, meaning the trained student's
actual 0.21 leaves more than half of the currently-available code capacity on the table. Widening to
K=256 raises that ceiling further to ~0.58 (measured) — a real but second-order ~0.10 gain, not a fix.
The dominant, larger share of the ret_agree10 gap is student/objective-bound (same root cause already
diagnosed for the DENSE collapse); K=128->K=256 is a legitimate follow-on lever, not the first one to
pull.**

P_deflated(archaeology: hi80_cos is the literal operationalization of the stated 0.85 goal) = **0.90**
(directly sourced from 3 independent on-disk artifacts, not extrapolated).
P_deflated(dual-attribution: ret_agree10 gap is majority student/objective-bound, minority-but-real
code-capacity-bound) = **0.65** (measured via 2 independent bypass-diagnostic runs at different scales,
consistent direction, but capped: n_test=800 on the full-cache run, no production-scale-n_test
confirmation yet).
P_deflated(regime-switching / two-tier retrieval architecture is the right next design move rather
than forcing one code to serve both) = **0.50** (capped; novel-synthesis strategic recommendation,
consistent with existing ANN literature already surfaced in this thread but not itself tested here).

---

## Part 1 — ARCHAEOLOGY: how was "0.54 -> 0.85" originally defined?

Three independent on-disk sources converge on the same answer, and a fourth (the v3e cell's own
docstring, written by exp_dev/Skunkworks the SAME day) makes the mapping explicit and authoritative:

1. **`PROGRESS.md` line 7** (current-phase framing, USER-locked):
   > "Currently borrows BGE-large (0.54 semantic cosine on USER test query); native concept encoder
   > targets 0.85+."
   This is a raw **cosine-to-gold on a specific query/answer pair** — not a Spearman, not a
   retrieval@k, not a macro-F1. "0.54" = the cosine between the borrowed BGE-large encoding of the
   USER's test query and the encoding of the right answer, observed directly by the USER; "0.85" is
   the aspirational bar for a NATIVE encoder to match or beat that same kind of measurement.

2. **Memory file `project_encoder_goals_native_perception_085_sparse_algebra_USER_CONFIRMED_2026-07-04.md`**
   (USER-confirmed "those goals sound perfect"), goal #2 verbatim:
   > "Semantic accuracy: hit 0.85. USER test query is ~0.54 cosine to the right answer today; target
   > 0.85+. The returned memory should BE the right one, not a vague neighbor."
   Same framing: cosine-to-gold on a right-answer pair. Goal #4 (algebra survive) is stated as a
   SEPARATE, non-negotiable gate ("Every eval passes TWO gates at once: (a) semantic fidelity
   [cosine to gold] AND (b) algebraic fidelity [FHRR bind/unbind roundtrip]") — confirming from the
   very first statement of the goal that semantic-cosine and algebra were always meant to be two
   independently-gated axes, not one number.

3. **`research_drill_concept_encoder_design_correctness_2026-07-04.md`** (same-day design-correctness
   drill, P_deflated=0.05 for the pre-distillation design): uses `cat_kitten_cos` (a single-pair
   cosine, same family) as its own operational stand-in for the 0.85 target throughout, citing
   "the 0.54 semantic signal it is trying to beat" — same metric family, independently corroborating.

4. **`experiments/exp_encoder_v3e_decline_vs_plateau_v1_core.py` docstring (lines 27-64)** — written
   by exp_dev under a Skunkworks/VET verdict the SAME day as the trigger measurement — makes the
   metric question EXPLICIT and resolves the ambiguity that had crept into the lineage:
   > "WRONG METRIC for the actual 0.85 goal: v3c's per_unit gate metric is Spearman rank-correlation
   > over 400k mostly-RANDOM held pairs (most random concept pairs have near-zero teacher cosine -- a
   > rank correlation over a mostly-uninformative-pair sample is not the same question as 'is a
   > genuinely similar pair's code-cosine close to its teacher-cosine', which is what the 0.85 target
   > is actually about)."
   > "...The cosine-to-gold metric reuses v3's existing `_semantic_unit` hi80_cos/hi80_teacher_mean/
   > hi80_calib_err fields (mean code-pair cosine restricted to pairs whose TEACHER cosine is itself
   > >= 0.80 -- i.e. 'genuinely gold-similar pairs', exactly the regime the 0.85 target is stated in)
   > -- these already existed in every prior cell in this lineage but were never promoted out of
   > per_unit."

**Ground-truth code** (`experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py:718-757`, function `_semantic_unit`) confirms exactly what each number computes:
- `spearman_all` (the lineage's long-running "DENSE/BLOCK spearman" headline, e.g. the "0.52 MID"
  number in `research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md`): Spearman rank
  correlation between code-cosine and teacher-cosine over `n_pairs` UNIFORM-RANDOM held pairs. Since
  most random concept pairs have near-zero teacher cosine, this is dominated by the easy "most things
  are unrelated" bulk structure. **This is the metric the VET flagged as wrong for the 0.85 question.**
- `hi80_cos`: mean CODE cosine restricted to the subset of those sampled pairs whose TEACHER cosine
  is >= 0.80 ("genuinely gold-similar"), paired with `hi80_teacher_mean` (mean teacher cosine on that
  same subset) and `hi80_calib_err = |hi80_cos - hi80_teacher_mean|` (absolute calibration error, not
  correlation). **This is the literal, direct formalization of "USER test query ~0.54 cosine to the
  right answer -> target 0.85."**
- `ret_agree10`: retrieval-agreement@10 — for each held row, overlap (|intersection|/10) between the
  TRUE top-10 nearest neighbors (via teacher cosine) and the CODE-predicted top-10 nearest neighbors
  (via code cosine), averaged over rows. **This metric was never named in the original 0.54->0.85
  goal statement.** It first appears as a per_unit field early in the lineage but was only promoted to
  headline status the same day as the trigger measurement, explicitly because the VET judged it "the
  closer analog" to what a real retrieval/cleanup operation needs.

**Conclusion of Part 1:** the 0.85 target, as literally stated by the USER and confirmed in the goals
memory, is a **coarse cosine-to-gold calibration metric on genuinely-similar pairs** — which `hi80_cos`
now formalizes exactly. `ret_agree10` is a DIFFERENT, newly-surfaced, operationally-motivated metric
that nobody ever set an explicit numeric target for — it was flagged as important only once the
lineage noticed the old headline (`spearman_all`) was measuring the wrong thing. This is not a case of
"the goalposts moved" — it is a case of "the original goal was under-specified for what happens AFTER
you hit it" (see Part 2).

---

## Part 2 — CONCEPTUAL: which metric gates which downstream use, and can the encoder regime-switch?

Composing with the USER-locked directive
`feedback_runtime_phase_diagram_regime_switching_per_operation_USER_2026-07-04` ("the substrate can
MOVE AROUND the phase diagram DURING operation... operate in one optimal regime for one operation,
then SHIFT to an alternate optimal regime for other operations... releases the 'one code/config
optimal for everything at once' over-constraint... can be semantic-optimal for retrieval and shift to
algebra-optimal for composition"):

| Downstream use | What it actually needs | Metric that gates it | Current status (this run) |
|---|---|---|---|
| **Retrieval / cleanup** (return THE right memory, not a vague neighbor) | Fine near-neighbor discrimination: among the handful of items closest to a query, get the RANKING right, not just the bulk "these are broadly similar" structure | `ret_agree10` (or a stronger downstream analog: recall@1/MRR against the true right answer) | **WEAK.** 0.21 trained; CHARPOS/random floor ~0.07-0.19; code's own zero-training ceiling at true full cardinality ~0.48 (K=128) / ~0.58 (K=256) — see Part 3. |
| **Composition / algebra** (bind/unbind survives; codes compose predictably) | Coarse geometric sanity (similar concepts land in a roughly-consistent algebraic neighborhood) + EXACT bind/unbind roundtrip fidelity — does NOT need to distinguish the 3rd-nearest from the 7th-nearest neighbor | (a) `hi80_cos`/`hi80_calib_err` for coarse sanity, (b) `keyed_roundtrip` J=5 accuracy for the algebra gate | **SOLID.** hi80_cos=0.832 (near target); `keyed_J5_last=1.000` in the very same run — the non-negotiable algebra gate (goal #4) is fully passing right now. |
| **Cortex-2 atom-consultation** (match current context against a ~100-atom learned-law store, gate/constrain) | Per its own same-day drill (`research_drill_cortex_2_atoms_as_active_constraints_M3_v2_2026-07-04.md`): a small-N (~99 atoms) cosine/tag-match-then-rerank problem where the design risk is FALSE-POSITIVE firing, not fine ranking. At N~100, the order-statistics crowding effect that punishes `ret_agree10` at N=177,899 barely applies — near-neighbors are far apart at this scale | Coarse threshold/calibration, i.e. the `hi80_cos`/`hi80_calib_err` regime, not fine retrieval-agreement | Not separately measured this cycle, but structurally closer to the ALREADY-STRONG coarse axis than to the weak fine axis. |

**Is it legitimate that the encoder is coarse-optimal for composition/cortex-consultation and needs a
DIFFERENT regime/mechanism for fine retrieval, or must one code serve both?**

Per the USER-locked regime-switching directive, this is explicitly licensed, not a compromise: the
directive names EXACTLY this shape of split ("semantic-optimal for retrieval... shift to
algebra-optimal for composition") as the intended way to release the "one code must do everything"
over-constraint. Concretely, this points toward a **two-tier retrieval architecture** rather than
demanding the single stored K=128 sparse/algebra code carry fine-grained rank order globally:

1. **Tier 1 (coarse, current code, already near-target):** use the existing sparse/algebra-preserving
   K=128 code for ALL composition/binding operations and for coarse candidate-set narrowing during
   retrieval (hi80_cos-style thresholding — "is this in the right neighborhood at all"). This is the
   code's proven strength today.
2. **Tier 2 (fine, a different mechanism, on a small shortlisted candidate set only):** once retrieval
   has narrowed to a small coarse-similar shortlist (via Tier 1), rerank that SHORTLIST with a
   finer-grained signal — e.g. the pre-quantization dense vector kept alongside the sparse code, or a
   wider auxiliary K=256 code, or a direct comparison against cached teacher vectors for just the
   shortlisted items (cheap, because it is no longer an all-177,899-item operation).

This is not a new idea invented for this drill — it composes directly with the existing
literature-anchored Ranks 1-2 in `research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md`
(anisotropic/rank-aware quantization loss; OPQ-style rotation before block-selection), both of which
are exactly the "preserve fine ranking on top of a coarse code" pattern the ANN/PQ literature already
solved (ScaNN, OPQ). The regime-switching directive gives USER-level permission to NOT insist the
single static sparse code solve the fine-ranking problem by itself.

---

## Part 3 — VERDICT: where do we honestly stand, and is the fine-retrieval gap K=128-resolution-bound?

**The metric(s) the encoder must hit:**
- `hi80_cos >= 0.85` (coarse semantic calibration on genuinely-gold-similar pairs) — THE literal
  stated goal. **Nearly closed**: final-step 0.832, best-val-checkpoint 0.857 (already above target at
  an earlier checkpoint in the SAME run) — this holds up across at least two checkpoints, not a single
  lucky read.
- `keyed_roundtrip` algebra gate — THE non-negotiable goal #4. **Currently passing** (1.000 in this run).
- `ret_agree10` at a level sufficient for reliable retrieval/cleanup — a metric that EXISTS on-disk in
  every prior cell in this lineage but has no formally-stated numeric target from the USER. **Wide
  open**: 0.21 trained, far below what the code can currently support (below).

**Is the remaining gap (a) coarse semantic quality, (b) fine retrieval, or both?**
**Both, but asymmetrically: (a) is nearly closed, (b) is wide open and is the one that should now
become the tracked headline**, since hi80_cos is close enough to target that further chasing it
(e.g. via a KL/PKT-style objective swap) is lower marginal value than fixing what actually gates
whether the substrate returns the RIGHT memory.

**Is the fine-retrieval weakness attributable to K=128 code resolution ("widen to K=256 is the
lever")?** On-disk MEASURED evidence (`experiments/exp_encoder_teacher_sparsifier_bypass_v1_core.py`,
zero-training-error, real teacher cache) gives a nuanced, decisive answer:

| Cache used | n_test | `ortho_k128_ret_agree10` (zero-train ceiling) | `ortho_k256_ret_agree10` | `charpos_ret_agree10` (floor) |
|---|---|---|---|---|
| 43,905-concept (local) | full-held | 0.596 | 0.669 | 0.189 |
| **177,899-concept (true full cardinality)** | 800 | **0.478** | **0.580** | 0.139 |

Compare to the trained student's actual `ret_agree10 = 0.211` (v3e, full 177,899 corpus, final step,
no cherry-pick).

- **K=128 DOES impose a genuine, real ceiling well below 1.0** (~0.48 at true full cardinality, even
  with a mathematically PERFECT zero-error linear map before quantization) — this is a real,
  structural, N-dependent cost, consistent with the order-statistics argument in
  `research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md` (bigger N packs
  true near-neighbors tighter, so even lossless-before-quantization information gets scrambled by the
  hard block-argmax discretization). **So "K=128 resolution contributes to the fine-retrieval
  weakness" is TRUE.**
- **Widening to K=256 is a real but SECOND-ORDER lever**: ceiling rises from ~0.48 to ~0.58 (+~0.10
  absolute, ~+21% relative) — a genuine, measured gain, not nothing, but nowhere near closing the gap
  to 1.0, and nowhere near the dominant factor.
- **The bigger, more urgent share of the gap is NOT code-resolution at all**: the trained student's
  actual 0.211 sits at LESS THAN HALF of the CURRENT K=128 code's own zero-training ceiling (0.478).
  A student that fully exploited the code it already has (no widening needed) could in principle more
  than DOUBLE today's ret_agree10 before K=256 becomes relevant. This gap has the same root cause
  already diagnosed for the DENSE collapse in `encoder_rescue_plan_converged_diagnosis_2026-07-04.md`
  (in-batch coverage collapse at scale; R1's global/landmark objective fix targets exactly this).

**Bottom line:** BOTH ARE TRUE, in this order of priority — (1) the objective/training-side gap (0.21
observed vs 0.48 achievable at the SAME K=128) is the larger, more urgent, already-being-worked lever
(R1); (2) K=128->K=256 widening is a legitimate, measured, but second-order follow-on lever (+~0.10
ceiling) that should be staged AFTER the objective fix lands, not instead of it, consistent with the
Rank ordering already established in `research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md`
and `research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md`. Caveat: the
177,899-cache ceiling reading used n_test=800 (a modest sample); a production-scale re-run of this same
zero-training diagnostic (already-authored cell, already dispatchable, not proposed here as new work)
would tighten the confidence interval on the exact ~0.48/0.58 numbers.

---

## Cheap decisive test

No new cell is proposed (per instruction). The single highest-value NEXT READ, once the in-flight
R1 global-objective fix lands (already tracked elsewhere in this session, "DENSE-recovery number
~2h"), is: **read `hi80_cos` AND `ret_agree10` together off that run's metrics.json, not `spearman_all`
alone.** If R1 lifts `ret_agree10` meaningfully above 0.211 (toward the ~0.48 K=128 ceiling) without
any code-width change, that CONFIRMS the objective was the dominant lever (as this drill concludes);
if R1 lifts `hi80_cos`/`spearman_all` but leaves `ret_agree10` roughly flat near 0.21, that would argue
the objective fix repairs coarse geometry but not fine rank, and K=256 (or the Rank-1/2 anisotropic-loss
/ OPQ-rotation levers from the cardinality drill) should be escalated sooner than currently planned.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

Framed against the NEXT landed checkpoint of the R1 global/landmark-objective fix (already in flight),
read on the SAME dual-metric standard this drill establishes:

**HARD-PASS** (objective fix is confirmed as the dominant lever; K=256 widening can wait):
- `hi80_cos >= 0.85` sustained (not merely a single early-checkpoint spike) AND
- `ret_agree10 >= 0.35` (materially closes at least half the gap from 0.21 toward the current K=128
  zero-training ceiling of ~0.48, without any code-width change).

**HARD-FAIL** (objective fix alone is insufficient; escalate K=256 widening / Rank-1-2 loss-family
levers from the cardinality drill sooner than planned):
- `ret_agree10 stays <= 0.25` (no material movement from today's 0.211) despite `hi80_cos`/coarse
  metrics recovering to target — this would show the coarse and fine axes are cleanly decoupled and
  the objective fix only touches the coarse one.

**MIDDLE BAND:** `ret_agree10` in `[0.25, 0.35)` — real but partial movement; re-run the
zero-training bypass diagnostic at production n_test scale before deciding whether to escalate K=256
next or keep tuning the objective.

---

## Cross-thread synthesis

- **`research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md`**: ranked the NCE-schedule/
  objective fix as the top lever toward "0.85" when the tracked headline was still `spearman_all`
  (the "0.52 MID" number). This drill does not overturn that ranking — it REFRAMES what "0.85" means
  (hi80_cos, already close) and adds a SECOND target (ret_agree10) that ranked drill's lever list did
  not explicitly gate on, because ret_agree10 had not yet been promoted to headline status when it was
  written.
- **`research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md`**: proposed
  the "teacher-to-sparsifier-direct bypass" as the cheap decisive test for whether the code or the
  student is the bottleneck. THAT test has since been RUN (`exp_encoder_teacher_sparsifier_bypass_v1`,
  smoke-scale on both the 43,905 and 177,899 caches) — this drill is the first to read its ret_agree10
  fields specifically (the prior drill's own falsifiable bands were framed on `spearman_all`/quantization
  ceiling, not ret_agree10) and finds the SAME qualitative answer (student-bound gap dominates, code
  ceiling real but second-order) generalizes from the "wrong" metric to the "right" one.
- **`encoder_rescue_plan_converged_diagnosis_2026-07-04.md`**: this drill's "student/objective-bound"
  conclusion for ret_agree10 is the SAME root-cause mechanism (in-batch coverage collapse at scale)
  already diagnosed there for the DENSE spearman collapse, and R1 (already in flight) is aimed
  correctly at fixing it — this drill's contribution is confirming the fix, if it works, should show up
  in ret_agree10 too, and giving an explicit numeric band to check that against.
- **`feedback_runtime_phase_diagram_regime_switching_per_operation_USER_2026-07-04`**: the two-tier
  retrieval architecture recommendation in Part 2 is a direct, first application of this USER-locked
  directive to the encoder's own downstream-use split (composition/cortex-consultation vs retrieval).

---

## Substrate-product implications

- **No architecture change is required to close the LITERAL 0.85 goal** — hi80_cos is already at or
  above target at the best checkpoint in the very run that triggered this question. The USER-facing
  claim "the returned memory should BE the right one" is NOT yet supported by that number alone, though
  — that claim is a `ret_agree10`/recall-style claim, and should not be conflated with hi80_cos when
  reporting progress to the USER going forward.
- **`ret_agree10` should be promoted to an explicit, USER-visible tracked target** alongside hi80_cos,
  since it is the metric that actually answers "does the substrate return the right memory," which is
  the plain-language framing of goal #2. No numeric target for it currently exists; this drill proposes
  the HARD-PASS/HARD-FAIL bands above as a starting point, subject to USER/Director revision.
- **The composition/algebra goal (#4) is NOT at risk** — it is passing cleanly (1.000) in the same run
  that shows the retrieval weakness, so the two axes are empirically independent right now, which is
  exactly what licenses treating them as separate regimes per the phase-diagram directive rather than
  as one entangled number.
- **K=256 widening is a legitimate, already-measured, second-order roadmap item** (~+0.10 ceiling gain)
  worth sequencing AFTER the R1 objective fix lands and is read against the new ret_agree10 band above
  — not a reason to pause or redirect the in-flight R1 work.
- **No exp_dev hand-off file is filed this cycle.** This drill is interpretive/definitional — it
  sharpens how to READ the already-in-flight R1 result (per the same precedent set by the two sibling
  same-day drills in this thread, both of which also withheld a hand-off pending a trigger condition
  that had not yet confirmed). If R1 lands in the HARD-FAIL band above, that IS the trigger for a
  fresh hand-off (K=256 widening and/or the Rank-1/2 anisotropic-loss and OPQ-rotation levers already
  ranked in the cardinality drill), at which point Strategy/Director should route it directly, not via
  this note.

---

## Citations (verified count)

**Zero external web sources this cycle (internal archaeology only, per explicit instruction).**
Internal provenance — every number and quote above was independently re-read off disk this cycle, not
carried forward from memory:

- `d:/AI/hd-instrument/PROGRESS.md` (line 7, direct read)
- `C:\Users\marsh\.claude\projects\d--AI\memory\project_encoder_goals_native_perception_085_sparse_algebra_USER_CONFIRMED_2026-07-04.md` (direct read)
- `C:\Users\marsh\.claude\projects\d--AI\memory\feedback_runtime_phase_diagram_regime_switching_per_operation_USER_2026-07-04.md` (direct read)
- `C:\Users\marsh\.claude\projects\d--AI\memory\project_phase_diagram_action_data_survives_phase_transformations_USER_2026-06-22.md` (direct read)
- `d:/AI/hd-instrument/notes/research_drill_concept_encoder_design_correctness_2026-07-04.md` (direct read, full)
- `d:/AI/hd-instrument/notes/research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md` (direct read, full)
- `d:/AI/hd-instrument/notes/research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md` (direct read, full)
- `d:/AI/hd-instrument/notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (direct read, full)
- `d:/AI/hd-instrument/notes/research_drill_cortex_2_atoms_as_active_constraints_M3_v2_2026-07-04.md` (partial read, headline)
- `d:/AI/hd-instrument/experiments/exp_encoder_v3e_decline_vs_plateau_v1_core.py` (docstring lines 1-134
  + verdict logic lines 280-400, direct read)
- `d:/AI/hd-instrument/experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`
  (`_semantic_unit` function, lines 708-758, direct read)
- `d:/AI/hd-instrument/experiments/exp_encoder_teacher_sparsifier_bypass_v1_core.py` (docstring +
  computation lines, direct read)
- `d:/AI/hd-instrument/data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/metrics.json` (direct
  Python-parsed read: verdict, verdict_msg, recovery dict incl. full dense_traj_val)
- `d:/AI/hd-instrument/data/exp_encoder_teacher_sparsifier_bypass_v1_smoke_selftest/metrics.json`
  (direct Python-parsed read: recovery dict, 43,905-concept cache)
- `d:/AI/hd-instrument/data/exp_encoder_teacher_sparsifier_bypass_v1_selftest/metrics.json` (direct
  Python-parsed read: recovery dict, TRUE 177,899-concept cache, n_test=800)

**14 distinct on-disk artifacts directly read/parsed this cycle** (not reported from memory).

---

## Intuitive summary (plain language, 6-10 lines)

The 0.85 target was always about one specific, simple question: "when the teacher says two concepts
are genuinely similar, does our own code agree by how much?" That question (`hi80_cos`) is basically
answered already — 0.83, and 0.86 at an earlier checkpoint in the same run, both right around target.
A second question nobody ever put a number on turned out to matter more for what the USER actually
wants ("the returned memory should BE the right one"): "if I ask for the 10 closest matches, how many
of the TRUE 10 closest matches do I actually get back?" That number is only 0.21 today — weak. We
tested, with zero training at all (a perfect, cheat-mode mapping straight into the same code), how good
that second number COULD be, and found the code itself caps out around 0.48 at its current resolution,
rising to about 0.58 if we doubled the code's width. So there IS a real, physical ceiling from the
code's resolution, and widening it would help a little — but the trained encoder today (0.21) isn't
even close to that ceiling (0.48) yet, so the bigger, more urgent problem is how it's being TRAINED, not
how big the code is. Good news: the fix already in flight for the training problem is the same fix
already diagnosed as the top lever for everything else in this arc, so no new work is being proposed
here — just a clearer scoreboard to read the result against.

**Why it matters:** without this, we'd have declared victory on 0.85 (the coarse number) while the
USER's actual complaint ("returns a vague neighbor, not the right one") stayed silently unsolved,
because nobody had put a number or a target on the metric that measures THAT.
**Near-term decision:** when the in-flight training fix lands, read `hi80_cos` AND `ret_agree10`
together (bands above) — not the old headline number alone — before deciding whether to widen the
code (K=256) or declare the encoder ready to move on.

ASCII-only. No emojis. No em dashes.
