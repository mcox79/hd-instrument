# 2x Research Drill: Encoder v2 FULL HARD_FAIL -- the ceiling is a margin/geometry trade-off, not a capacity wall (2026-07-06)

**Author:** Research (Director role).
**Trigger:** USER request to thoroughly 2x-drill the Stage-2 encoder negative
(`exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1`, canonical FULL, `run_mode=full`,
`HARD_FAIL`, `spearman_all={0.317, 0.273, 0.496}` across 3 arms) so the idle GPU gets a well-chosen next
experiment instead of a blind GPU-day. This is a 2x DEPTH drill on existing findings (own encoder history +
2 already-existing 2026-07-04 research notes), not a fresh broad lit-scan-as-verification, per
[[feedback-2x-means-depth]].
**Method:** direct on-disk re-derivation across the FULL lineage of encoder cells (v2 negative, v3
global-objective, v3b NCE-ablation diagnostic, v3c 5-seed FULL paired tie-breaker) + the two prior 2026-07-04
research drills these findings supersede, cross-checked against 2 parallel Sonnet lit-scans using generic
ML terms only (query-privacy discipline observed -- no substrate-novel vocabulary used off-platform).
**No experiments dispatched by this drill** -- decision/diagnostic memo only, per instruction; the top pick
is staged for the Director to hand to exp_dev directly (no routing file, per current session discipline).

---

## HEADLINE

**The v2 FULL negative is NOT a capacity, distill-target, or dimensional ceiling -- it is a real, now
3-way-triangulated trade-off between two things the SAME contrastive (NCE) loss term is being asked to buy at
once: graded semantic fidelity vs. discrete decodability of the block-argmax code.** Three data points on the
SAME lineage, at increasing NCE weight, draw a clean line:

| Cell | NCE weight | DENSE semantic spearman | Keyed algebra (bind-unbind decode acc@1) |
|---|---|---|---|
| v2 FULL (the negative under drill) | constant 0.5, whole run | 0.317 / 0.273 / **0.496 (best, TOPK_NAIVE)** | **1.0** (perfect, all J/blocks) |
| v3b NCE-ablation (MID scale, single seed) | 0.5 (current) vs 0 (ablated) | 0.269 (current) -> **0.734 (NCE_ZERO)**, delta +0.465 | not gated at MID |
| v3c FULL paired tie-breaker (5 seeds, NCE=0 the whole run) | **0** | **0.816-0.916** (GLOBAL 0.816-0.855; IN_BATCH 0.877-0.916, all 5 seeds clear the pre-registered HARD-PASS dense floor of 0.75 by 0.07-0.17) | **0.033-0.317** (GLOBAL keyed roundtrip J=5, all 5 seeds fail the 0.90 floor) |

Removing NCE entirely does not just "help" dense semantic fidelity -- it robustly **clears the 0.85 target in
3 of 5 seeds and comes within 0.02-0.03 in the rest**, at true 178k-concept scale, 5-seed replicated. This is
a bigger and cleaner win than either of the two prior 2026-07-04 research drills predicted
(`P_deflated(NCE-fix alone reaches 0.85)=0.20` in the cardinality drill -- beaten by the actual result).
**But the same NCE term that corrupts dense fidelity is exactly the term supplying the margin the discrete
per-block argmax code needs to survive bind -> unbind -> cleanup.** Remove it and the code's graded geometry
recovers beautifully while its decodability collapses (keyed roundtrip 0.03-0.32, need >=0.90); keep it at a
naive constant weight (v2, the run under drill) and decodability is perfect while semantic fidelity caps at
~0.32-0.50. **No arm anywhere in this lineage has demonstrated BOTH goals at once.** That is the real, newly
sharpened open question this drill surfaces -- not "is 0.85 reachable" (largely YES, already demonstrated for
semantic fidelity in isolation) but "can 0.85-class semantic fidelity coexist with the algebra requirement in
one deployable code."

**P_deflated(0.85-class dense semantic fidelity alone is reachable at full 178k scale) = 0.75** (near-certain;
already empirically demonstrated 5/5 seeds, deflated only for checkpoint-selection and seed-variance caveats
below).
**P_deflated(a sequenced NCE/margin curriculum can recover joint semantic-fidelity-AND-algebra in one code) =
0.40** (capped; well-grounded by directly-adjacent literature fetched this cycle, but no source runs this
exact combined recipe -- novel synthesis).
**P_deflated(the joint requirement is fundamentally unreachable for this student/code family, i.e. a genuine
Pareto frontier with no code on it clearing both bars) = 0.25** (real possibility per the "peak-then-decline"
pattern appearing even under NCE=0 the whole run -- see caveat below).

---

## 1. Diagnosing the ~0.5 ceiling in the v2 FULL negative (verified off-disk)

`data/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1/metrics.json`, verdict `HARD_FAIL`,
`verdict_msg: "G_A_SEMANTIC_FAIL: spearman 0.317 < 0.70"`.

**The 3 arms are `BLOCK_K128`, `BLOCK_K64`, `TOPK_NAIVE`** (config: `k_blocks_list=[128,64]`,
`sparsity_primary=0.03125`; `TOPK_NAIVE` is unconstrained global top-K selection over all 4096 dims, not
block-partitioned). Per-arm `semantic` results:

| Arm | spearman_all | ret_agree10 | keyed acc@1 (J=2..20) |
|---|---|---|---|
| BLOCK_K128 | 0.317 | 0.423 (best) | 1.0 (sbc algebra) |
| BLOCK_K64 | 0.273 | 0.348 | 1.0 (sbc algebra) |
| TOPK_NAIVE | **0.496 (best)** | 0.322 (worst) | 0.985-1.0 (fhrr algebra, slightly softer at J10/20) |

Baselines in the same run: `RANDOM_BLOCK` spearman 0.002 (calibration floor, confirms the eval is fair),
`DENSE_SIGN` (no block sparsifier) 0.439, and -- notably -- **`CHARPOS`, a non-learned character-position
hash with zero distillation, scores 0.656, beating every trained arm.** A non-learned control beating every
trained arm on pure rank-correlation is itself strong independent evidence that the training objective is
actively *destroying* signal relative to doing nothing, not merely under-delivering it.

**Where is the loss, ranked by evidence:**
- **NOT the distill target.** BGE-teacher agreement itself is not the ceiling -- v3c (below) shows the SAME
  teacher, same input pathway, same MLP student reaching 0.82-0.92 once the confound is removed.
- **NOT MLP student capacity.** The MLP (1024->2048->4096 GELU) was built specifically to fix a real, prior,
  *confirmed* linear-student capacity ceiling (~0.64, `e0fcd6ad3`, early-eval decisive). v3c proves the SAME
  MLP architecture CAN represent a >=0.85-class mapping at this scale -- capacity is not the residual problem.
- **NOT a fundamental JL/dimensional/power-law limit.** The 2026-07-04 cardinality-ceiling drill
  (`research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md`) already found, via 4
  independent lit-scans (2 directly-fetched: LIMIT sign-rank paper arXiv:2508.21038; JAIR
  Thomas/Dasgupta/Rosing 2021 HDC incoherence bound), that d=4096 has vastly more raw combinatorial capacity
  (~640 bits/item) than the ~17.4 bits needed for bare distinctness at N=177,899 -- "sheer distinctness is not
  remotely exhausted." v3c's empirical 0.82-0.92 result CONFIRMS this call and beats even that drill's own
  P=0.20 estimate for "NCE-fix alone reaches 0.85."
- **PARTIALLY the block-rigidity ("Product Quantization") tax, but secondary.** Within the SAME v2 run,
  `TOPK_NAIVE` (unconstrained top-K, escapes fixed block boundaries) beats `BLOCK_K128`/`BLOCK_K64` by
  0.18-0.22 spearman -- a real, modest, structural cost consistent with the cardinality drill's Rank-2
  "axis-misalignment tax" finding. But this gap (~0.2) is dwarfed by the NCE-removal delta (~0.47 at MID,
  and the difference between v2's ~0.3-0.5 and v3c's 0.82-0.92 at FULL) -- **the NCE/margin mechanism
  dominates the total gap by roughly 2-3x over the block-rigidity mechanism.**
- **THE DOMINANT MECHANISM: the constant-weight NCE contrastive term.** Confirmed 3-way (v2 constant-NCE ->
  poor semantic/perfect algebra; v3b MID ablation -> NCE_ZERO recovers dense +0.465 in a
  `TAIL_CORRUPTION_CONFIRMED_RECOVERED` pattern; v3c FULL NCE=0, 5 seeds -> dense 0.82-0.92 / algebra
  collapses to 0.03-0.32). This run (`v2`) had NCE ON at constant weight for the entire run
  (`train_diag.nce_last` 0.196-0.723, non-decaying) -- exactly the regime the v3b ablation and the
  alignment-uniformity literature (Wang & Isola 2020) predict actively erodes an already-forming graded
  geometry over the back half of training.

**Best arm and why:** `TOPK_NAIVE` (0.496) -- not because its objective differs (NCE was on, constant, same
as the other two arms) but because its unconstrained top-K selection avoids part of the block-rigidity tax
that `BLOCK_K128`/`BLOCK_K64` pay. It is still far from 0.85 because the dominant NCE-corruption mechanism
applies equally to all three arms in this cell.

---

## 2. Scouring the encoder history -- was NCE on or off in the best arm, and what is "raw-cardinality ceiling"

**NCE was ON (constant weight ~0.5) in ALL THREE arms of the v2 FULL negative.** Per the cron's framing,
killing NCE is indeed "the obvious next lever" -- and it has ALREADY BEEN TRIED, at full scale, 5-seed
replicated, in the v3c cell (`67311a73b` lineage: `6662c5717` v3 global-objective build ->
`20b4c6fbb`/`84044e6f3` v3b NCE-ablation diagnostic MID -> `94062aecc`/`4fdf72dae` v3c FULL 5-seed paired
tie-breaker). Result: **NCE-off dramatically fixes semantic fidelity (0.82-0.92) but breaks algebra
decodability (0.03-0.32 keyed roundtrip, need >=0.90)** -- confirmed via direct read of
`experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py` lines 588-629:
the FULL-mode verdict logic gates on `keyed_global["acc_at1"] < 0.90` (`FALSE_WIN_ALGEBRA_GLOBAL`) **before**
even checking the dense-recovery floor (`HP_DENSE_FLOOR=0.75`), specifically to prevent claiming a semantic
win on a non-composable code. **All 5 seeds cleared the dense floor by 0.07-0.17 points -- the dense-recovery
hypothesis is empirically CONFIRMED and exceeds the pre-registered HARD-PASS bar -- but the cell's overall
verdict is HARD_FAIL because the newly-surfaced algebra-decodability requirement fails.** This is a
genuinely useful negative: half the hypothesis landed spectacularly, and the failure pinpoints exactly the
untested joint requirement.

Caveat on scope: the FULL verdict logic short-circuits on the `GLOBAL_BLOCK` arm's keyed acc@1 first; the
`INBATCH_BLOCK` arm's keyed acc@1 was never reached/reported in the 5 landed verdict messages (only its DENSE
and coarse BLOCK-spearman numbers are). Given `IN_BATCH` consistently has even higher DENSE than `GLOBAL`
(0.877-0.916 vs 0.816-0.855) -- i.e. even LESS margin-inducing pressure survived training -- it is very
likely (not directly confirmed) that `INBATCH_BLOCK` keyed acc@1 is equally or more degraded. Flag as
inference, not an on-disk-verified number.

**"Raw-cardinality ceiling"** (named in the dispatch cron) refers to the hypothesis raised by
`research_drill_2x_batch_ratio_match_negative_understanding_2026-07-04.md`: DENSE fell from 0.825 at
smoke-scale (V~3,000) to 0.36-0.47 at MID (V=39,515) even at generous batch ratios, a drop attributed
partly to raw vocabulary size itself (generalized-neural-collapse-for-many-classes theory, sign-rank/LIMIT
theory). **This was directly re-examined and substantially REFRAMED by the very next same-day drill**
(`research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md`, 4 lit-scans, 9
directly-fetched sources): it is real but NOT a hard N-vs-d information-theoretic wall -- it is better
explained by (a) the block-code's axis-misalignment ("Product Quantization") tax and (b) a reconstruction-MSE
loss that doesn't specifically preserve ranking-relevant structure (ScaNN-style anisotropic-loss analogy,
arXiv:1908.10396, directly fetched). **v3c's empirical result (0.82-0.92 dense, NCE=0, full scale) now
substantially confirms the OPTIMISTIC reframe**: whatever cardinality-driven cost exists, it did not prevent
the SAME code/student/scale from reaching near-target fidelity once NCE was removed. So "raw-cardinality
ceiling" is real as a secondary, structural, largely-fixable cost (the TOPK_NAIVE-vs-BLOCK gap, ~0.2, is its
visible fingerprint in the v2 negative) -- it is NOT the primary explanation for the v2 FULL's ~0.3-0.5
ceiling, which is dominantly the NCE/margin mechanism.

---

## 3. Literature grounding for the next lever (2 parallel Sonnet lit-scans, generic terms only)

Two focused scans (not a fresh broad scan, per 2x-depth discipline) targeted the specific new question this
drill surfaces: does removing a margin-inducing loss trade decodability for geometry, and is there a known
way to sequence the two to get both?

**Scan A (margin needed for exact discrete-code decodability):** Deep-hashing literature explicitly
distinguishes "graded similarity preservation" objectives (regression/cosine-matching) from "hard-decision
margin" objectives (contrastive/triplet/margin loss), and adds the latter specifically because regression
alone leaves ambiguous, near-threshold decision boundaries (quantization-margin-loss papers,
arXiv:2603.02738, arXiv:2012.03820, arXiv:1602.06697 -- snippet-tier). VQ-VAE commitment-loss literature
confirms the analogous trade-off: weakening the discreteness-inducing commitment term improves continuous
fidelity but degrades reliable codebook-entry selection (`Huh, Cheung, Agrawal, Isola`, "Straightening Out the
Straight-Through Estimator," ICML 2023, arXiv:2305.08842). **Directly on point:** "Mitigating Premature
Discretization with Progressive Quantization for Robust Vector Tokenization" (arXiv:2603.22304, fetched in
full) frames this exact tension as a CURRICULUM problem -- continuous-first, then cosine-annealed
discretization -- and reports that *premature* discretization causes "grid mapping" collapse toward random
codebook init, degrading both reconstruction and code diversity; their curriculum resolves the trade-off
rather than accepting it. No source found the exact "tail corruption" (late-training erosion of previously-good
graded geometry by an overlong repulsion phase) framing by name -- flagged as **novel synthesis, not directly
evidenced**, though Wang & Isola's alignment-uniformity decomposition (ICML 2020, arXiv:2005.10242) is the
right lens for it.

**Scan B (curriculum sequencing of continuous-then-discrete objectives):** Gumbel-Softmax/concrete-relaxation
literature is unanimous: anneal temperature HIGH-to-LOW ("soft-then-hard"), never the reverse -- starting hard
collapses gradients to near-rank-one and starves most units of learning signal (Jang et al., ICLR 2017,
arXiv:1611.01144). **Directly on point:** "Continuous First, Discrete Later: VQ-VAEs Without Dimensional
Collapse" (arXiv:2605.06870, fetched in full) shows JOINT VQ-VAE training causes dimensional collapse
(effective codebook dimension only 3-5), while a continuous-autoencoder warm-up BEFORE introducing
quantization raises effective dimension to 17-19 and improves downstream quality 11-35% at equal budget --
almost exactly the shape of our own finding (train the continuous/relational objective to convergence first;
only then impose discreteness). Quantization-aware-fine-tuning (QAT) literature for network WEIGHTS (not
embeddings, an analogy not a direct hit) shows a SHORT post-hoc fine-tune with the discretization mechanism
active, using a reduced learning rate specifically to avoid "catastrophic disruption of pre-trained
representations," closes most of the accuracy gap (Jacob et al., CVPR 2018; Krishnamoorthi 2018,
arXiv:1806.08342). No source runs the exact combined recipe (RKD+InfoNCE distillation into a hard top-k/WTA
code with a specifically SHORT terminal margin-locking phase) -- **cap confidence ~0.4-0.5, novel synthesis
borrowing well-evidenced sub-patterns.**

**Both scans converge on the same actionable shape: geometry-first, discreteness-last, and SHORT is the
operative word for the discreteness phase.** This is a well-grounded, not speculative, next test.

---

## 4. Ranked next-lever recommendation

| Rank | Lever | GPU-worthy or cheap-local-first? | Expected lift | P_deflated |
|---|---|---|---|---|
| **1 (top pick)** | **Sequenced/curriculum NCE schedule**: reuse the 5 already-trained v3c NCE=0 checkpoints (zero retrain cost for the geometry phase); add a SHORT terminal fine-tune (~5-10% of full steps) with NCE turned back on (or a dedicated margin/commitment-style loss on just the block-argmax choice), monitoring BOTH dense-spearman and keyed-roundtrip acc@1 continuously so the terminal phase stops the instant decodability clears 0.90 -- before "tail corruption" can re-erode the geometry. | **Cheap local/short-GPU smoke first**, 1-2 seeds, reusing existing checkpoints -- this is explicitly NOT a fresh full GPU-day. Only escalate to a full 5-seed FULL dispatch if the smoke shows the terminal-lock-in mechanism actually recovers keyed acc@1 >=0.90 while dense stays materially above the v2 baseline (>=0.70). | Plausible joint result: dense ~0.75-0.85 (some erosion from the 0.82-0.92 peak expected but literature-motivated to be small if the phase is short and late) AND keyed roundtrip >=0.90 -- the first arm anywhere in this lineage to jointly clear both bars. | 0.40 (capped; two directly-on-point fetched sources support the mechanism class, none run this exact recipe) |
| **2** | **Rank-aware/anisotropic loss reweighting** (ScaNN-style, cardinality drill's own Rank-1, arXiv:1908.10396 directly fetched) layered under lever 1 -- reweight the RKD regression term toward ranking-relevant directions instead of raw cosine-MSE. | Cheap (loss-function swap only, no architecture/width change), complementary not competing -- stack with lever 1 rather than sequence before it. | Could raise the nce=0 geometry ceiling itself (currently 0.82-0.92) and/or make the terminal margin phase easier to satisfy without eroding geometry as much, since resolving power would already concentrate where the block-argmax decision matters. | 0.45-0.50 (per cardinality drill, re-affirmed here) |
| **3** | **"Raw-cardinality ceiling" as an independent hard wall** (accept the ~0.2 block-vs-topk gap as unfixable, or pursue OPQ-style rotation before block-argmax) | Cheap if pursued (rotation-only variant) | Largely REFUTED as the dominant story this cycle -- real but secondary (visible only as the ~0.2 TOPK_NAIVE-vs-BLOCK gap), and v3c's 0.82-0.92 result shows the SAME block-rigid code, once NCE is removed, is not far off 0.85 on its own. Worth a cheap OPQ-rotation try only AFTER lever 1 is tested, not before. | 0.30-0.45 (per cardinality drill Rank-2, downgraded in priority here) |
| **4 (fallback, not manufactured optimism)** | **Accept the trade-off; defer the JOINT requirement to M4; ship v2-class (NCE-on, algebra-perfect, semantic-capped) as production; treat nce=0 checkpoints as a separate semantic-similarity-only side-channel, not for compositional binding.** | N/A -- this is a strategy decision, not a dispatch. | Honest bound if lever 1 fails: 0.85-class semantic fidelity IS reachable in isolation (proven); 0.85-with-algebra is not proven reachable in this code/objective family, and the "peak-then-decline" pattern reproducing even under NCE=0 the whole run (v3c: `global_peak_decline=True` / `inbatch_peak_decline=True` in ALL 5 seeds, despite no NCE at all) hints at an intrinsic late-training instability beyond just the NCE mechanism -- a real residual risk that lever 1's "stop early" mitigation targets directly but may not fully solve. | 0.25 that lever 1 cannot close the joint gap at all (see HEADLINE) |

**Is 0.85 plausibly reachable? Two different answers for two different questions, and this drill is careful
not to conflate them (per the "no manufactured optimism" instruction):**
- **Semantic fidelity alone, ignoring the algebra requirement: YES, effectively already reached** (0.82-0.92,
  5/5 seeds, full 178k scale, no new build needed -- this closes what the two 2026-07-04 drills left as an
  open, calibrated-uncertain question, and beats their own point estimates).
- **Semantic fidelity AND algebra decodability jointly, in one deployable code (the actual product
  requirement -- "sparse algebra" is one of the 4 stated encoder goals): UNPROVEN.** No arm in this lineage
  has cleared both bars simultaneously. Lever 1 (sequenced NCE curriculum) is the best-motivated, cheapest
  next test to find out -- not a guaranteed fix. If it fails even after tuning phase length/strength, the
  honest, non-optimistic call is that this specific code/objective family cannot deliver both at once, and
  the joint requirement -- not the semantic-fidelity requirement -- is what should defer to M4 or a
  differently-scoped code family (additive quantization / free top-k / OPQ-rotation rebuild).

---

## Cheap decisive test

**Reuse existing v3c checkpoints; run a short terminal fine-tune with NCE re-enabled on 1-2 seeds; track
dense-spearman and keyed-roundtrip acc@1 every ~50-100 steps of the terminal phase.**
- Zero new training for the geometry phase (5 NCE=0 checkpoints already exist and are landed).
- Terminal phase budget: ~5-10% of the original 40,000-step schedule (~2,000-4,000 steps), cheap on GPU,
  cheaper than any of the FULL 5-seed dispatches already run in this lineage.
- Early-stop the instant keyed acc@1 (J=5) clears 0.90, and report dense-spearman AT THAT STEP (not at the
  end of the terminal phase) -- this directly operationalizes "short and monitored" rather than "run the old
  constant-NCE recipe again and hope."

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

Framed against the recommended lever-1 smoke (short terminal NCE-relock fine-tune on top of a converged
NCE=0 checkpoint):

**HARD-PASS** (the joint requirement is solvable via sequencing; proceed to a full 5-seed FULL dispatch of
the sequenced recipe, then treat as the new production encoder objective):
- Keyed roundtrip acc@1 (J=5) clears >=0.90 within the terminal phase, AND
- dense-spearman at the SAME step is >=0.70 (a real, usable improvement over the v2 baseline's best arm of
  0.496, even if short of the full 0.82-0.92 peak), AND
- the recovery is stable for at least ~500 steps past the 0.90 crossing (not an instantaneous spike
  immediately followed by re-collapse -- guards against the same peak-then-decline pathology already observed
  in this lineage).

**HARD-FAIL** (sequencing does not solve the joint requirement; escalate to lever 2 stacked with lever 1, or
accept the fallback strategy call in Rank 4):
- Keyed roundtrip acc@1 stays <0.70 even after a terminal phase equal in length to 25% of the original
  schedule (i.e. NCE needs to run so long to re-establish margin that it is no longer a "short, monitored"
  intervention -- this would reproduce the same corruption dynamic the whole recipe was designed to avoid), OR
- dense-spearman collapses below 0.60 (worse than the v2 negative's own best arm) by the time keyed acc@1
  clears 0.90 -- i.e. the trade-off is not softenable by sequencing at all, just relocated in time.

**MIDDLE BAND:** keyed acc@1 in [0.70, 0.90) at an acceptable dense-spearman (>=0.65) -- partial recovery;
worth layering lever 2 (rank-aware loss) before concluding the sequencing approach is insufficient.

---

## Cross-thread synthesis

- **`research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md`**: ranked the NCE-schedule fix as the top
  lever (Rank 1, P=0.55) BEFORE the v3c FULL result existed. That drill's HARD-PASS band (FULL-scale DENSE
  with the winning NCE schedule >=0.75, no further late-training decline) is **now confirmed on the DENSE
  metric alone** by v3c (0.82-0.92 clears 0.75 easily) -- but that drill did not anticipate the algebra-gate
  failure, because its falsifiable predictions were framed purely in terms of DENSE recovery, not joint
  decodability. This drill's contribution is identifying that the SAME mechanism (NCE) that drill correctly
  bet on for dense recovery is also the mechanism supplying algebra margin -- an interaction that drill's
  scope did not cover.
- **`research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md`**: proposed a cheap
  "bypass-the-student" diagnostic (teacher embeddings straight through the sparsifier, no training) to
  separate code-capacity-bound from student/training-artifact explanations. **That diagnostic was never run**
  (confirmed by grep across `experiments/` and `notes/` -- no `teacher_direct`/`bypass_student` cell exists),
  but its information value has been **superseded by v3c's actual trained-student result**: since a real
  trained student (not a bypass) already reaches 0.82-0.92, the code/sparsifier is empirically NOT the
  capacity bottleneck for dense fidelity, making the bypass diagnostic no longer necessary to resolve that
  specific question. It could still be useful for isolating a PURE code-structure ceiling independent of the
  algebra question, but that is now a lower-priority follow-up, not a blocker.
- **`encoder_rescue_plan_converged_diagnosis_2026-07-04.md`** (the R1-R5 rescue battery this entire lineage
  implements): R1 (global/landmark RKD objective) is validated -- dense geometry recovers as hypothesized.
  **This drill's lever-1 recommendation IS exactly R2** ("brain dense-first-then-sparsify sequencing,
  post-R1") from that same plan, now sharpened with (a) hard evidence that R1's dense payoff is real and
  large (not hypothetical), (b) a concrete mechanism for WHY R2 is needed (algebra decodability requires
  margin, which dense-only RKD does not supply), and (c) fresh, directly-fetched external literature
  (arXiv:2605.06870, arXiv:2603.22304) that did not exist in the plan's original citation set, independently
  recommending exactly this "continuous-first, discretize-last, keep it short" pattern.
- **`research_drill_2x_batch_ratio_match_negative_understanding_2026-07-04.md`**: raised "raw-cardinality
  ceiling" as a candidate explanation for the smoke-to-MID drop. This drill's finding (v3c reaches 0.82-0.92
  at FULL scale, full cardinality, with the SAME block-rigid code) further downgrades that hypothesis as the
  PRIMARY driver -- consistent with, and extending, the cardinality-ceiling drill's own reframe from "hard
  wall" to "structural, largely-fixable tax."

---

## Substrate-product implications

- **No new cell needed for the top pick.** Lever 1 is a config/sequencing change on the ALREADY-BUILT v3c
  core module (`exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py`): load an
  existing best-checkpoint, continue training with NCE re-enabled for a short schedule, evaluate both metrics
  along the way. This is the cheapest possible next experiment in this lineage -- reuses 5 already-landed
  checkpoints, no new data, no new architecture.
- **The "raw-cardinality ceiling" framing from the cron should be retired as the leading hypothesis.** It is
  real but secondary (visible as the ~0.2 TOPK_NAIVE-vs-BLOCK gap) and should not gate further investment
  ahead of the NCE/margin-sequencing lever, which the evidence now shows dominates the total gap by 2-3x.
- **The product-relevant framing for the USER strategy decision**: "0.85 native perception" (encoder goal) is
  effectively DE-RISKED for semantic fidelity alone -- the open risk is narrower and sharper than before:
  whether the SAME code can also satisfy "sparse algebra" (the other stated encoder goal) at that fidelity
  level. This is a better-defined, cheaper-to-resolve question than the one the cron posed, and should be
  framed to the USER as such rather than as a re-run of the same 0.85-reachability uncertainty.
- **If lever 1 HARD-FAILs**, that is a genuine, well-evidenced (not manufactured) decision point: ship the
  current v2-class encoder (algebra-perfect, semantic ~0.32-0.50) as the production compositional encoder,
  and treat the nce=0 checkpoint's 0.82-0.92 semantic fidelity as a separate, non-compositional
  similarity-search capability for M4 to pick up on its own terms -- not as evidence that 0.85-with-algebra
  is close.

---

## Per-claim P_deflated (summary)

| Claim | P_deflated | Basis |
|---|---|---|
| 0.85-class dense semantic fidelity alone is reachable at full scale | **0.75** | Already empirically demonstrated, 5/5 seeds, real trained MLP student, full 178k concepts; deflated only for checkpoint-selection-not-final-checkpoint and per-seed variance (0.816-0.916 range). |
| Sequenced NCE/margin curriculum recovers BOTH semantic fidelity and algebra decodability jointly | **0.40** | Capped; two directly-fetched, closely-adjacent papers (arXiv:2605.06870, arXiv:2603.22304) support the mechanism class; no source runs this exact recipe -- novel synthesis. |
| Rank-aware/anisotropic loss reweighting adds further gain, stacked with the NCE fix | **0.45-0.50** | Re-affirms the cardinality drill's own Rank-1 (ScaNN analogy, directly fetched), now layered under a stronger evidence base. |
| "Raw-cardinality ceiling" is the dominant/primary driver of the v2 negative | **0.15** (downgraded from the cron's implicit framing) | v3c's 0.82-0.92 result at full cardinality, same block-rigid code, refutes cardinality-as-primary; the NCE mechanism dominates by 2-3x. |
| The joint requirement (semantic AND algebra) is fundamentally unreachable for this code/objective family | **0.25** | Real risk flagged by `peak_decline=True` reproducing even under NCE=0 the whole run in all 5 v3c seeds -- an instability not fully explained by NCE alone. |

---

## Citations (verified count)

**2 parallel Sonnet lit-scan sub-agents this cycle, ~30 tool-uses total (WebSearch/WebFetch), targeting the
specific new question this drill raises (margin-for-decodability; continuous-then-discrete curriculum
sequencing).** Plus re-use (not re-fetch) of the two 2026-07-04 sibling drills' own citation sets for the
capacity/cardinality/objective-schedule background (their own verified-fetch tallies: ~9 directly-fetched of
~45 total in the cardinality drill; ~35 total across 4 lit-scans in the ranked-levers drill -- see those notes
for full lists, not re-verified again by this drill).

**Directly fetched this cycle (highest confidence):**
- "Mitigating Premature Discretization with Progressive Quantization for Robust Vector Tokenization,"
  arXiv:2603.22304 (2026) -- fetched in full; load-bearing for lever 1.
- "Continuous First, Discrete Later: VQ-VAEs Without Dimensional Collapse," arXiv:2605.06870 -- fetched in
  full; load-bearing for lever 1 (dimensional-collapse-under-joint-training mechanism, quantitative gains from
  continuous-first warm-up).
- Jang, Gu, Poole, "Categorical Reparameterization with Gumbel-Softmax," ICLR 2017, arXiv:1611.01144 --
  reported at snippet-level by the sub-agent but is a standard, canonical result (soft-then-hard annealing
  direction).
- Huh, Cheung, Agrawal, Isola, "Straightening Out the Straight-Through Estimator," ICML 2023, arXiv:2305.08842
  -- abstract/search-snippet verified; full-PDF fetch attempt failed (binary parse error), treat as
  snippet-tier.

**Snippet-tier (not independently fetched this cycle, standard/canonical or secondary-source confidence):**
Wang & Isola, "Alignment and Uniformity," ICML 2020, arXiv:2005.10242; Jacob et al., CVPR 2018 (QAT);
Krishnamoorthi, arXiv:1806.08342 (QAT whitepaper); "Cosine Annealing Weights in Knowledge Distillation"
(CAW-KD), ACM 2025; "Improving Discrete Optimisation via Decoupled Straight-Through Gumbel-Softmax,"
arXiv:2410.13331; assorted deep-hashing margin-loss papers (arXiv:2603.02738, arXiv:2012.03820,
arXiv:1602.06697) -- snippet-only, engineering-paper tier, supportive but not load-bearing on their own.

Apply the standing lit-scan calibration discipline: none of the snippet-tier citations were independently
re-verified a third time by the synthesizing agent this cycle.

---

## Intuitive summary (plain language)

The encoder's semantic-similarity training and its "must decode back to an exact answer after algebra"
training are pulling in opposite directions, and we now have clean, repeated proof of it: turn off the
"tell-close-things-apart-harder" part of training and the encoder gets almost perfect at ranking things by
meaning (arguably good enough on its own) but loses the ability to reliably decode which exact answer it
picked after a bind/unbind operation; leave that part on (the setup that just failed) and decoding is
perfect but meaning-ranking caps out around a third to a half of where it needs to be. This is not a wall we
ran into by accident and not something more GPU time alone fixes -- it is a genuine trade-off the current
recipe asks one loss term to resolve on its own. Outside research on very similar systems (image/audio
codebooks, quantized neural networks) has a well-tested playbook for exactly this shape of problem: teach the
rich, graded meaning FIRST until it settles, then apply the "must decode exactly" pressure only briefly at
the very end, just long enough to lock in a reliable decision boundary, and stop before it has a chance to
undo the meaning it just learned. We already have the trained "meaning" checkpoints sitting on disk from a
prior run, so testing this costs a short fine-tune, not a fresh GPU-day.

**Why it matters:** this reframes the encoder's blocking negative from "we don't know if 0.85 is possible"
(the cron's framing) to a sharper, more actionable question: "0.85-class meaning-fidelity is basically already
proven possible; the real open question is whether it can coexist with exact decodability in one code, and
there's a cheap, literature-grounded test for that specific question, not a guess."
**Near-term decision:** dispatch the short terminal-NCE-relock smoke (1-2 seeds, reusing the 5 landed v3c
checkpoints) as the next encoder experiment -- NOT a fresh full-scale GPU-day, and NOT a re-run of any lever
already tried in this lineage. If it clears the HARD-PASS band above, escalate to a 5-seed FULL of the
sequenced recipe. If it HARD-FAILs, that is real, non-manufactured evidence to ship the current
algebra-perfect v2-class encoder for compositional use and treat 0.85-with-algebra as an M4-deferred,
differently-scoped problem.

ASCII-only. No emojis. No em dashes.
