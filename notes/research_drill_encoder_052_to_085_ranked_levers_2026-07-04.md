# Research Drill: Ranked Levers, DENSE Spearman 0.52 (MID) -> 0.85 Target (2026-07-04)

**Author:** Director (Research)
**Trigger:** USER/Director request to rank the 5x rescue-battery levers by expected gain, so the moment the
v3b batch-ratio-match + NCE-ablation MID result lands, the single best next experiment is already chosen.
**Method:** 4 parallel Sonnet lit-scans (landmark/anchor selection; objective-family choice; student
capacity; training dynamics/peak-decline), generic ML search terms only (query-privacy discipline — no
substrate-novel vocabulary used off-platform), then Director synthesis against the on-disk v3b pre-reg
(`preregs/2026-07-04_exp_encoder_migration_step1b_v3b_batch_ratio_nce_ablation_dense_recovery_diagnostic_v1.md`)
and the converged rescue-plan diagnosis (`notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md`).
**Calibration:** lit-scan penalty applied (deflate 0.15-0.25 off naive reading; novel-synthesis extrapolation
to our exact input pathway capped at 0.50). Do NOT dispatch experiments — this is a decision memo only.

---

## HEADLINE

**The single best next lever is already running inside v3b, and the literature independently predicts which
way it will break.** Three convergent 2025/2026 retrieval-distillation papers (LEAF; "Conventional
Contrastive Learning Often Falls Short"; "Beyond Hard Negatives") plus the alignment/uniformity theory
(Wang & Isola 2020) describe EXACTLY our diagnosed pattern — a relational/geometry loss that plateaus early
while a contrastive/hard-negative term keeps grinding, actively eroding the already-learned graded structure
late in training (one cited case: a relational loss literally COLLAPSED under hard-negative-only pressure,
MRR 0.006 vs 0.307 under balanced sampling). This is v3b's own NCE-ablation arm (`NCE_ZERO`, `NCE_DECAY40`
vs `NCE_CURRENT`). **Landmark selection quality and landmark-set size are NOT the bottleneck** — at ~4-8k
landmarks against an estimated ~100-dim effective semantic rank, Nystrom/leverage-score theory says we are
already well past the point where smarter (k-means/farthest-point) selection beats random, and the literature
explicitly notes uniform-random landmark sampling is "competitive with, sometimes better than" non-uniform
sampling at generous budgets. **Student capacity (2-layer MLP) is genuinely uncharted in the literature for
this exact configuration** (attention-free MLP + impoverished input pathway + fine-grained rank target over
10^5 items) — not ruled in or out, and the cheapest way to find out (train-set-vs-held-out diagnostic) costs
nothing and should run in parallel, not be guessed at.

**P_deflated(top lever, NCE-schedule fix, meaningfully improves recovery) = 0.55.**

---

## Ranked levers (highest to lowest expected gain toward 0.85)

| Rank | Lever | Mechanism | Cheapest test | Expected gain | Cost | Gated on v3b? | P_deflated |
|---|---|---|---|---|---|---|---|
| **1** | **NCE/contrastive-term weight SCHEDULE** (anneal-to-zero or drop once relational term plateaus) | Alignment-uniformity antagonism (Wang & Isola 2020, ICML): once the relational/geometry loss stops improving, continued contrastive/hard-negative optimization keeps pushing uniformity, actively eroding the graded structure already learned. Matches our own diagnostic exactly: rkd loss plateaued ~0.22 from step~700 while nce loss kept falling 0.51->0.456 through the tail, DENSE 0.740@1200 -> 0.716@1500 -> 0.521 full-eval. | **Already running**: v3b's `NCE_ZERO`/`NCE_DECAY40` ablation arms at the decisive batch=128. Zero marginal cost. | HIGH. Retrieval-scale analogs show pure-relational beats combined objective by 5-7 points (LEAF), and a MarginMSE-style relational loss recovered from near-total collapse (0.006->0.307 MRR) purely by fixing negative-sampling balance/weight. | ~zero (in flight) | **This IS v3b's secondary tier — answered directly by v3b, no new dispatch needed to test it.** | 0.55 |
| **2** | **Objective FAMILY upgrade**: distribution/KL-style relational loss (PKT/CompRess-style softmax-normalize-then-KL) in place of raw cosine-MSE relational loss | Softmax-normalization is scale-invariant and concentrates weight on near neighbors; PKT/CompRess/DIST literature supports this recovers finer graded rank than raw MSE-on-cosine. Caution: DIST also shows over-strict KL-matching can hurt under a large teacher-student capacity gap (correlation-matching sometimes beats exact KL). Independent of the contrastive-term antagonism — a genuine loss-family change layered under the anchor/landmark mechanism already in place. | Swap the RKD-MSE term for a PKT-style softmax+temperature+KL term at the SAME batch/landmark config v3b already validates; retrain one MID arm reusing all v3b infra (same landmarks, split, student). | MEDIUM. Best evidence closest to our regime (LEAF) says pure relational already wins without needing this wrapper — so likely a smaller, second-order gain layered on top of Rank 1, not a standalone fix. | LOW (one new MID arm, reuses v3b infra) | Independent — can run in parallel; priority DROPS if Rank 1 alone clears bar. | 0.45 |
| **3** | **Cheap diagnostic: in-sample (training-set) vs held-out relational error**, to separate capacity-bound from objective/generalization-bound failure | Standard ML diagnostic (Harutyunyan et al. 2023 confirms the field lacks a turnkey distillation-specific version, but the general logic transfers): poor fit on the TRAINING set itself = real capacity ceiling; good train fit + held-out gap = objective/generalization problem (matches everything else this drill found). | Reuse ALREADY-SAVED v3b checkpoints (best-by-full-held per arm); evaluate the same relational/spearman metric on a training-set sample instead of the held set. No new training, no GPU time. | Not a fix by itself — a DISCRIMINATOR that prevents wasting a capacity-upgrade experiment if the ceiling is actually objective-bound (which all current evidence favors). High information value per dollar. | ~zero (eval pass only) | Independent — run in parallel with v3b interpretation, using v3b's own checkpoints the moment they land. | N/A (diagnostic, not a claim) |
| **4** | **Landmark SELECTION method** (k-means / farthest-point vs random) + **landmark SET SIZE** | At ~4-8k landmarks against an estimated ~100-dim effective semantic rank, Nystrom leverage-score theory (Musco & Musco 2017; Kumar/Mohri/Talwalkar 2012) implies near-optimal accuracy needs only ~d_eff*log(d_eff) ~ 460-1000 landmarks — we are already well INSIDE the "generous budget" regime where Kumar/Mohri/Talwalkar's own controlled study found uniform-random sampling "competitive with, sometimes better than" smarter non-uniform sampling. The fixed-external-anchor mechanism ITSELF (vs in-batch) is the well-supported, convergent fix (MoCo/CompRess/SEED lineage) — that part is already right; refining WHICH points are landmarks is second-order at this budget. | If pursued anyway: swap random landmark selection for k-means/farthest-point at the same count, retrain at MID, compare. Literature predicts near-zero delta. | LOW. Confirms the earlier "8k likely oversampled" suspicion — it is oversampled relative to the spectral-rank bound, not undersampled. Growing L further is unlikely to help either. | LOW (cheap swap) but low expected payoff | Independent, but deprioritize — do not spend a cycle here before Ranks 1-3. | 0.15-0.20 |
| **5** | **Student capacity/architecture** (width / depth / attention) | Universal approximation says a 2-layer MLP CAN represent the mapping in principle; nothing in the literature says it DOES reliably at practical width for a fine-grained RELATIONAL target fed by an impoverished/lossy input pathway (this exact combination — attention-free MLP, lossy input, large-vocabulary graded-rank target — is a genuine absence-of-evidence in the literature, not a confirmed ceiling). Capacity-gap literature (Cho & Hariharan 2019; TAKD/DGKD) is CNN-classifier-and-coarse-label work and increasingly reinterpreted as objective/optimization-bound, not architecture-bound, so it only weakly transfers here. | Gate this on Rank 3's diagnostic. If in-sample fit is ALSO poor, retrain a wider/deeper variant at MID with everything else held fixed and compare. | Could be large IF capacity is really the ceiling, but current evidence (peak-then-decline, not a flat low ceiling; lr fully decayed = converged, not undertrained; 128 teacher-draws/concept at full vs 9.6 at smoke yet WORSE held generalization) argues AGAINST a simple capacity story and FOR an objective-side explanation. | MEDIUM (new architecture variant, retrain at MID) | Gated on Rank 3's diagnostic firing capacity-bound — do not preempt. | 0.25 (capped; unconfirmed without Rank 3) |
| **6** | **Structural**: block-STE gradient bias, temperature, normalization in the sparsifier | Already effectively closed by the prior sparse-fidelity-frontier drill (2% comfortably above the fidelity knee; DENSE~0.52 vs BLOCK~0.51, nearly equal) — sparsity is not implicated. This lit-scan additionally found NO literature on STE-gradient-bias interacting with contrastive losses to cause peak-then-degrade dynamics. Mechanically, the diagnosed DENSE_SIGN collapse (0.825->0.368) happened with the sparsifier NOT engaged (pre-sparsifier readout), so STE bias cannot be the primary failure's cause. | N/A — only revisit if Ranks 1-3 all fail to move the needle. | LOW / near-closed. | — | Independent, deprioritized. | 0.10 |

---

## Decision table — what to dispatch the moment v3b lands

v3b reports three things: the **primary tier** (batch-ratio-match: does the fixed-landmark/global objective
beat in-batch as batch shrinks toward FULL's true coverage ratio?), the **secondary tier** (NCE ablation at
the decisive batch=128: does `NCE_ZERO`/`NCE_DECAY40` recover the peak?), and the **H1-vs-H2 diagnostic**
(is the peak-then-decline real on the full-held eval, or was it quick-eval subsample noise?).

| v3b primary tier | v3b secondary (NCE ablation) tier | Single best next dispatch |
|---|---|---|
| HARD_PASS (global beats in_batch) | CONFIRMED_RECOVERED (best NCE arm >=0.70, delta>=0.15) | **Dispatch FULL-scale GPU run**: winning objective (global) + winning NCE schedule (`NCE_ZERO` or `NCE_DECAY40`, whichever recovered further) + best-by-full-held checkpoint selection (not final-checkpoint). This is the combined Rank-1-validated fix at true scale. Run Rank 3's diagnostic in parallel on the MID checkpoints as a free cross-check before committing GPU hours. |
| HARD_PASS | PARTIAL_RECOVERY or NOT_CONFIRMED | Objective/coverage mechanism confirmed but the tail-corruption story is not (fully) the cause of the residual gap. Run Rank 3 (in-sample-vs-held diagnostic) on the winning MID checkpoint BEFORE any FULL dispatch — decide capacity-bound (-> Rank 5) vs still-objective-bound (-> Rank 2, KL/PKT-style family swap) with real evidence rather than guessing. |
| MIDDLE_BAND / HARD_FAIL | CONFIRMED_RECOVERED or PARTIAL_RECOVERY | The coverage/landmark mechanism did not clearly confirm at MID, but the NCE-schedule fix independently recovers quality. **Apply the winning NCE schedule to whichever objective performed best in absolute terms at MID (global or in_batch)** and retest — the schedule fix may be orthogonal to and independent of the landmark/coverage story; do not assume the landmark mechanism must be right just because it is running. |
| MIDDLE_BAND / HARD_FAIL | NOT_CONFIRMED | Neither hypothesized mechanism confirmed. Do NOT preempt with a capacity or architecture change. Run Rank 3's diagnostic first (near-zero cost, uses existing checkpoints) to learn whether ANY MID arm shows good in-sample fit; if none do, escalate to a fresh look at whether the "objective can reach ~0.8 at scale at all" premise itself needs revisiting (a genuinely new research drill, not a rank-5/6 guess). |

**Single top bet across the most probable branch:** given the diagnostic evidence already in hand — training
converged (lr fully decayed), MORE teacher-draws-per-concept at full than at smoke yet WORSE held
generalization, and the loss telemetry showing exactly the relational-plateau/contrastive-still-falling
signature the literature independently flags as a known collapse mode — the most probable v3b outcome is
**secondary tier fires (NCE ablation shows real recovery), regardless of exactly how strongly the primary
coverage-ratio tier confirms.** Bet on Rank 1's fix being the one that moves the number, and pre-stage the
FULL-scale dispatch plan (winning objective + winning NCE schedule + best-checkpoint selection) so it can go
out within the same cycle v3b lands, per the ONCE-per-stage GPU-dispatch rule.

---

## Cheap decisive test

Two tests, both free, both usable the moment checkpoints exist (no new training):

1. **v3b's own secondary tier IS the decisive test for Rank 1** — no separate action needed, just read the
   `TAIL_CORRUPTION_CONFIRMED_RECOVERED` / `PARTIAL_RECOVERY` / `NOT_CONFIRMED` verdict already pre-registered
   in the v3b prereg.
2. **In-sample-vs-held-out relational error (Rank 3)** on the winning MID checkpoint(s): evaluate the same
   spearman/relational metric on a training-set sample instead of the held set. This is the single cheapest
   action that discriminates "the map genuinely cannot represent this function" (capacity-bound, escalate to
   Rank 5) from "the map fits what it saw but does not generalize" (objective-bound, stay on Ranks 1-2). It
   costs one extra eval pass and should be run regardless of which v3b branch fires, in parallel with
   interpreting the primary/secondary tiers.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

Framed against the NEXT dispatch this drill recommends (FULL-scale run combining the winning objective +
winning NCE schedule + best-checkpoint selection), conditional on v3b's secondary tier confirming per the
decision table above:

**HARD-PASS** (validates Rank-1-as-primary-lever thesis; proceed to production sequencing — R2 sparsify,
R3/R4 self-teacher roadmap unchanged):
- FULL-scale DENSE spearman with the winning NCE schedule >= 0.75 (recovers at least to the MID-observed
  peak, ideally beyond it since FULL has more data), AND
- the full-held eval trajectory shows NO further late-training decline beyond the best checkpoint (confirms
  the schedule fix, not just checkpoint-picking, actually removed the degradation), AND
- best-by-full-held checkpoint is at or near the FINAL checkpoint (not far earlier) — i.e., the fix moved the
  peak forward/sustained it, rather than merely making early-stopping the only way to capture it.

**HARD-FAIL** (Rank-1 fix insufficient at true FULL scale; escalate to Rank 2 objective-family swap AND run
Rank 3's diagnostic before considering Rank 5):
- FULL-scale DENSE spearman with the winning NCE schedule stays < 0.60 (materially below the MID peak of
  0.740, i.e. the fix that worked at MID does not transfer to FULL scale), OR
- the peak-then-decline pattern reproduces even with `NCE_ZERO`/`NCE_DECAY40` at FULL scale (the antagonism
  has a different/additional driver beyond contrastive-term weight — reconsider the relational-loss FORM
  itself, i.e. jump straight to Rank 2's KL/PKT-style swap rather than re-tuning the NCE schedule further).

**MIDDLE BAND**: FULL-scale DENSE spearman in [0.60, 0.75) — real recovery, short of the ~0.8 objective-fix
target used to gate the sparsify-next decision; treat as partial and re-run Rank 3's diagnostic before
deciding whether to invest further in objective tuning (Rank 2) or accept a lower dense ceiling and revisit
the USER strategy call on whether 0.85 is achievable at all under this input pathway (a decision this drill
does NOT make — see prior design-correctness drill, P(current unsupervised-if-it-had-shipped) = 0.05, now
superseded by the distillation redesign but the underlying "orthography+sparse-triples input pathway may not
carry 0.85 of teacher semantics regardless of objective" caution from that drill still applies as an outer
bound on ALL of these levers).

---

## Cross-thread synthesis

- **research_drill_sparse_code_semantic_fidelity_frontier_2026-07-04.md**: established sparsity is not the
  bottleneck (Rank 6 here is deprioritized consistently with that drill's verdict — 2% vs 3.1% landed
  DENSE~0.52 vs BLOCK~0.51, no material gap). This drill's Rank 6 treatment is a direct extension, not a
  new question.
- **research_drill_concept_encoder_design_correctness_2026-07-04.md**: established the ORIGINAL no-teacher
  unsupervised design could not reach 0.85 (P=0.05) and recommended BGE distillation — the redesign this
  entire rescue battery (R1-R5) implements. This drill's ranking operates entirely WITHIN that redesign; it
  does not reopen whether distillation is the right macro-direction (settled), only which micro-lever inside
  distillation to pull next.
- **research_drill_brain_grounded_continual_self_improving_encoder_2026-07-04.md**: independently validated
  the fixed-landmark/anchor MECHANISM itself (Shen et al. 2020 BCT) as structurally sound and convergent with
  a totally different literature (production embedding-compatibility engineering). THIS drill adds: the
  landmark SELECTION/SIZE question within that mechanism is second-order (Rank 4), so no further landmark
  engineering is warranted before the objective-schedule question (Rank 1-2) is resolved.
- **encoder_rescue_plan_converged_diagnosis_2026-07-04.md** (the rescue battery this drill ranks): confirms
  R1 (Rank 1/2 territory) is correctly sequenced as the lead; this drill sharpens WHICH part of R1's own
  v3b diagnostic experiment carries the most expected information (the NCE ablation, not the batch-ratio
  sweep alone) and adds Rank 3 (a free diagnostic) and Rank 5 (student capacity) as items the rescue plan's
  R1-R5 numbering did not explicitly separate — R5 in the rescue plan was a K=256 capacity-BOUND-on-sparsity
  diagnostic (already deprioritized by the fidelity-frontier drill); this drill's Rank 5 is a DIFFERENT
  question (2-layer-MLP student ARCHITECTURE capacity, independent of sparsity level) that the rescue plan's
  numbering does not currently cover — flagging this as a genuinely new candidate item, not a duplicate.

---

## Substrate-product implications

- **Zero new infrastructure needed for the top bet.** The literature-predicted highest-value lever (NCE
  weight schedule) is already instrumented inside v3b; if it confirms, the FULL-scale dispatch is a
  straightforward config choice (which NCE schedule, which checkpoint), not a new build.
- **The cheap in-sample-vs-held diagnostic (Rank 3) should become a standing practice** for this encoder
  lineage going forward — it is a near-zero-cost way to avoid ever guessing "maybe the architecture is too
  small" without evidence, which the literature explicitly flags as an easy, common misdiagnosis (Cho &
  Hariharan's own capacity-gap literature is itself now being reinterpreted as objective-bound in a
  non-trivial fraction of cases).
- **Landmark engineering (selection method, set size) is validated as NOT worth further investment** at the
  current budget — this closes a plausible rabbit hole (re-deriving landmark count/selection) before it
  opens, freeing cycles for the objective-side work that the evidence actually points to.
- **If Rank 1+2 both fail at FULL scale (the HARD-FAIL branch), that is itself a decision point for the USER**
  on whether the orthography+sparse-triples input pathway can EVER carry 0.85 of BGE semantics regardless of
  objective — the design-correctness drill's outer-bound caution (P=0.05 for the pre-distillation design)
  reapplies as a residual risk even after a correct distillation objective, and should be surfaced explicitly
  rather than silently re-tuning forever.

---

## Per-claim P_deflated (summary)

| Claim | P_deflated | Basis |
|---|---|---|
| NCE/contrastive-schedule fix (Rank 1) meaningfully improves recovery | **0.55** | 3 convergent 2025/2026 retrieval-distillation papers + alignment/uniformity theory; matches our own loss-telemetry signature closely. Lit-anchored, not novel synthesis, but extrapolated to our regime so not raised above 0.55-0.60. |
| Objective-family (KL/PKT) swap (Rank 2) adds further gain beyond Rank 1 | **0.45** | Supportive but the closest single analog (LEAF) suggests pure relational alone already wins without this wrapper — treat as secondary, not required. |
| Landmark selection method (k-means/FPS) meaningfully improves recovery (Rank 4) | **0.15-0.20** | Deflated hard; Kumar/Mohri/Talwalkar's own finding is uniform-random is competitive at generous budgets, and Nystrom leverage-score theory puts our budget well past the point of diminishing returns. |
| Student-capacity (2-layer MLP) is the ceiling (Rank 5) | **0.25** | Capped; genuine literature gap (no direct precedent for this exact configuration) argues against high confidence either way; current training-dynamics evidence (converged, not undertrained; peak-then-decline shape) argues against a simple flat-capacity-ceiling story specifically. |
| Structural/STE sparsifier gradient bias is implicated (Rank 6) | **0.10** | Near-closed by the prior sparse-fidelity drill (sparsity not the bottleneck) plus this drill's own null literature search on STE-contrastive interaction, plus the mechanical fact that the diagnosed collapse occurred pre-sparsifier. |

---

## Citations (verified count)

**~35+ distinct works surfaced across 4 parallel Sonnet lit-scan sub-agents** (each searched/fetched web
sources directly via WebSearch/WebFetch; citations were not independently re-fetched by the synthesizing
agent this cycle — apply the standing lit-scan calibration discipline). Load-bearing citations:

- **Landmark/anchor:** Kumar, Mohri, Talwalkar, "Sampling Methods for the Nystrom Method," JMLR 2012 (uniform
  sampling competitive with non-uniform); Musco & Musco, "Recursive Sampling for the Nystrom Method," NeurIPS
  2017, arXiv:1605.07583 (ridge-leverage effective-dimension bound); Liu, He, Chang, AnchorGraph, ICML 2010;
  He et al., MoCo, CVPR 2020; Koohpayegani et al., CompRess, NeurIPS 2020, arXiv:2010.14713; Fang et al.,
  SEED, ICLR 2021, arXiv:2101.04731.
- **Objective/schedule:** Park et al., Relational Knowledge Distillation, CVPR 2019, arXiv:1904.05068; Tian
  et al., CRD, ICLR 2020, arXiv:1910.10699; Passalis & Tefas, PKT, ECCV 2018; Huang et al., DIST, NeurIPS
  2022, arXiv:2205.10536; "LEAF" text-embedding distillation, arXiv:2509.12539 (pure-relational beats
  combined objective by 5-7 pts); "Conventional Contrastive Learning Often Falls Short," arXiv:2505.19274
  (contrastive addition degrades retrieval NDCG); "Beyond Hard Negatives," arXiv:2604.04734 (relational loss
  collapse under hard-negative-only mining, MRR 0.006 vs 0.307); Chen et al., GradNorm, arXiv:1711.02257;
  Kendall & Gal, uncertainty weighting, CVPR 2018, arXiv:1705.07115.
- **Student capacity:** Cho & Hariharan, "On the Efficacy of Knowledge Distillation," ICCV 2019,
  arXiv:1910.01348; Mirzadeh et al., TAKD, AAAI 2020; Son et al., DGKD, ICCV 2021, arXiv:2009.08825;
  Harutyunyan et al., "Supervision Complexity," NeurIPS 2023, arXiv:2301.12245; Kusupati et al., Matryoshka
  Representation Learning, NeurIPS 2022, arXiv:2205.13147.
- **Training dynamics / collapse:** Jing et al., "Understanding Dimensional Collapse in Contrastive
  Self-supervised Learning," ICLR 2022, arXiv:2110.09348; Wang & Isola, "Alignment and Uniformity," ICML
  2020, arXiv:2005.10242; "Unveiling Key Aspects of Fine-Tuning in Sentence Embeddings: A Representation Rank
  Analysis," arXiv:2405.11297 (correlation-with-quality sign flip +0.85 -> -0.81 across training phases —
  load-bearing analog for our peak-then-decline signature); Chuang et al., Debiased Contrastive Learning,
  NeurIPS 2020, arXiv:2007.00224; Robinson et al., "Contrastive Learning with Hard Negative Samples," ICLR
  2021, arXiv:2010.04592.

None of these were spot-verified against source PDF/HTML directly by the synthesizing (Director) agent this
cycle — all are as reported by the 4 sub-agents (title/venue/arXiv-id level confidence, not table-level
re-verification). Apply the standard discount for that tier of citation confidence.

---

## Intuitive summary (plain language, 6-10 lines)

The training run's own numbers already look exactly like a known, well-documented failure pattern from
outside literature: one part of the lesson plan (teaching the overall shape of meaning) finished improving
early, while a second part (telling apart close-but-different concepts) kept grinding harder and harder —
and that second part, once the first part stopped moving, started actively UNDOING the good shape it had
already learned. Three recent, independent studies of very similar systems found the same thing and the same
fix: once the "big picture" part of training plateaus, dial down or turn off the "nitpicking" part rather
than letting it run at full strength for the rest of training. The good news: our OWN in-flight experiment
(v3b) already tests exactly this fix, so no new build is needed to find out if it's right — we just read the
result. Two things this drill rules OUT as likely explanations: the "reference points" used to teach the
whole map (the landmark set) are already generous, not scarce, so making them smarter won't move the needle;
and the small student network is not obviously too small, since the training pattern looks like a coaching
problem, not a "not enough brain cells" problem — though we don't yet have hard proof either way, and this
drill flags a free, one-line check (compare how well the student fits what it was SHOWN vs what it's tested
on) that would settle that for free the moment we want it. Bottom line: bet on the coaching fix, watch it
land inside v3b, and have the "train it for real, at full scale, with the fixed coaching schedule" plan ready
to fire the same cycle.

**Why it matters:** this converts "try five things and see" into "one validated fix, already in flight, plus
a free tie-breaker test on standby" — the highest-leverage next action needs zero new infrastructure.
**Near-term decision:** the moment v3b lands, if the NCE-ablation arm shows recovery (likely, per this
drill's calibrated read of the evidence), dispatch a single FULL-scale run combining the winning objective,
the winning NCE schedule, and best-checkpoint selection — do not wait to also test landmark selection or
architecture changes first, since both are independently deprioritized by this drill.

ASCII-only. No emojis. No em dashes.
