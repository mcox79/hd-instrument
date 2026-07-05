# Research: perception/encoder capability scope — state, buried win, and the highest-leverage next experiment

**Date:** 2026-07-05
**Type:** Capability-scope + existing-data scour (USER standing directive: scour before proposing new) + spec-only (no dispatch)
**Driver:** USER-flagged PRIMARY focus. Encoder is the weakest capability (MEMORY.md: "mediocre-done", GSBC_EXPAND2X tier). Task: state where native perception actually stands off-disk, identify the PROVEN blocker to 0.85, and spec the single highest-leverage next cell.
**Calibration:** lit-scan penalty applied (deflate 0.15-0.25); novel-synthesis P capped at 0.50 per [[feedback-lit-scan-calibration-penalty]].

---

## HEADLINE

**A result that already clears the 0.85 semantic-fidelity bar with algebra fully intact is sitting on disk, unpromoted, buried inside a cell whose OVERALL verdict reads HARD_FAIL.** `exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1` (FULL, 178K concepts, 5 seeds, landed) ran two paired arms at nce=0: GLOBAL/landmark-RKD (fails — algebra breaks, keyed_roundtrip@J5 mean 0.143) and **IN-BATCH-RKD-only, no landmark, no InfoNCE** (spearman-to-BGE-teacher mean **0.886**, range 0.852-0.897 across all 5 seeds; keyed_roundtrip@J5 = **1.000 in all 5 seeds**). The cell's own pre-registered bands (HARD-PASS >=0.85 / MIDDLE [0.70,0.85) / HARD-FAIL <0.70) were cleared by the in-batch arm — but the cell's verdict label is driven by the OTHER (GLOBAL) arm's algebra failure, so this win has never been separately verdicted, never carried into Step-2 (full 970K sparse-encode) or Step-3 (actual gold-verify cosine-to-right-answer, the literal USER ship metric), and has zero cap_map or git-promotion trace beyond the one code-landing commit.

The proven blocker to 0.85 is **training-objective mismatch, not teacher-dependence, not raw MLP capacity, and not an inherent sparse-algebra tradeoff.** The evidence chain (below) rules out capacity (the ~0.52 "capacity-bound" plateau from the intermediate diagnostic is superseded — the same-size MLP hits 0.886 once the corrupting objective terms are removed) and rules out sparsity-vs-algebra as a hard tradeoff (the in-batch arm holds 1.000 roundtrip at the SAME 2%-sparse target where the GLOBAL arm's algebra collapsed) — it isolates the failure to two specific objective components: (a) InfoNCE contributes tail-corruption at full-corpus scale (v3b: zeroing nce weight recovers spearman 0.269->0.734, delta +0.465), and (b) the GLOBAL/landmark pairwise objective specifically breaks the sparse code's bind/unbind sign structure even though its raw geometry (spearman 0.777) looks fine — a textbook false-win-if-ungated case per [[feedback-smoke-gates-null-hypothesis]]-adjacent discipline.

**Is 0.85-native (teacher-free) realistic?** No — the same-day 5x convergence drill (`research_5x_drill_perception_encoder_spec_and_brain_mechanism_2026-07-05.md`, read and cross-referenced, not re-run) already established this independently: native self-supervision needs corpus scale (tens-hundreds of millions of tokens) the substrate's 970K-item KB is very likely below; the substrate's own teacher-free test (Random-Indexing/BEAGLE on text8, full run, MIDDLE_BAND, ratio 1.20, control-verified) plateaus well under BGE-class separation. Distillation-from-BGE remains the pragmatic path, and — new information this cycle — **may already be far closer to done on the ship metric than the 07-04/07-05 record assumed**, because the 07-05 drill's own situational awareness of "current distilled student ~47-53% of ceiling" was built from the lever-ladder note's block-argmax/GLOBAL numbers, not from the buried in-batch-RKD arm inventoried here.

---

## A. STATE — the numeric timeline (all verified on disk, nothing inferred)

Chain: Step1 (orthographic) -> Step1b v1 (linear distill) -> v2 (MLP distill) -> v3 (landmark/global) -> v3b (NCE ablation) -> v3c (paired RKD-only) -> Step2 (full sparse-encode) -> Step3 (gold-verify, the actual ship metric).

| Stage | Cell | Result | Key metric | Algebra (keyed_roundtrip@J5) |
|---|---|---|---|---|
| Step1 orthographic | `exp_encoder_migration_step1_train_concept_encoder_970K_KB_v1_core` | CELL_CRASHED (stale self-test, mean_nnz assertion) | independent design-correctness drill: ceiling ~0.49-0.52 cosine, P_deflated(0.85)=0.05 | n/a |
| Step1b v1 (linear) | `..._step1b_distill_concept_encoder_v1` smoke | HARD_FAIL_SPARSITY_NOT_PROTECTING (later diagnosed as a gate-design bug) | spearman(BLOCK_K128)=0.788 | 1.000 |
| Step1b v2 (MLP) smoke | `..._step1b_v2_mlp_distill..._v1` smoke | HARD_PASS | spearman(BLOCK)=0.645, DENSE=0.825 | 1.000 |
| Step1b v2 (MLP) **FULL 178K** | same, full | **HARD_FAIL G_A_SEMANTIC_FAIL** | spearman(BLOCK)=**0.311**, DENSE_SIGN=0.368 (pre-reg MIDDLE floor was 0.70 -- missed by a wide margin) | 1.000 (held) |
| capacity-ceiling diagnostic | `exp_encoder_step1b_capacity_ceiling_train_vs_held_diagnostic_v1` | "CAPACITY_BOUND" (train~held~0.52) | -- **superseded, see below** | -- |
| Step1b v3 (landmark/global) | `..._v3_global_objective_landmark_rkd..._v1` | CELL_CRASHED (CPU OOM, ~6.5GB) | no verdict | n/a |
| Step1b v3b (NCE ablation, true FULL 172,899) | `..._v3b_nce_ablation_dense_recovery_diagnostic_v1` | HARD_FAIL (batch-ratio-match not confirmed) | **load-bearing diagnostic**: nce=0.5 -> spearman 0.269; nce=0 -> spearman **0.734** (TAIL_CORRUPTION_CONFIRMED_RECOVERED, delta +0.465) | -- |
| Step1b v3c (paired GLOBAL-only vs INBATCH-only, nce=0, FULL 178K, 5 seeds) | `..._v3c_full_paired_rkd_only_dense_recovery_v1` | **cell verdict HARD_FAIL FALSE_WIN_ALGEBRA_GLOBAL** (all 5 seeds) | GLOBAL arm: spearman mean 0.777 (0.738-0.843), keyed@J5 mean **0.143** (algebra broken) — **INBATCH arm (buried in same cell): spearman mean 0.886 (0.852-0.897), keyed@J5 = 1.000 all 5 seeds** | INBATCH: 1.000 / GLOBAL: 0.143 |
| Step2 (full 970K sparse-encode) | `..._step2_sparse_encode_970K_KB_v1_core` | only smoke exists: HARD_PASS (k_mean=82.0, 0 roundtrip mismatches) | no FULL run on disk | -- |
| Step3 (gold-verify, 100 queries A/B — the literal ship metric) | `..._step3_gold_verify_100_queries_A_B_v1_core` | only smoke exists: **CELL_CRASHED** (`E_concept.pt not found` — depends on a landed step1/step1b artifact never produced) | never measured | -- |

**Capacity-ceiling superseded, explicitly:** the intermediate diagnostic concluded "need bigger student" from a ~0.52 plateau, but it ran chronologically *between* v3b and v3c — i.e., in the NCE-corrupted regime. v3c reaches 0.886 with the **same-size MLP**, once nce=0 and the landmark term is dropped in favor of simple in-batch RKD. The capacity story does not survive; it was an objective-corruption artifact.

**Git status:** `exp_encoder_migration_step1b_v3_...core.py` and `..._v3c_full_paired_rkd_only...core.py` each have exactly one commit (code landed, `6662c5717` and `94062aecc` respectively) — no follow-up commit exists that promotes, re-verdicts, or even flags the in-batch arm's win. cap_map is frozen at **v597** (2026-07-03) with no v598+ anywhere in the repo; the BGE-distillation step1b chain has never been given its own cap_map row. The only cap_map row touching "native perception" is a META row for an OLDER, different mechanism family (`META_SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE`, MM_STANDARD_5_WITNESS_GATE_1_SATISFIED, 3/5 witnesses: WTA-competitive-Hebbian CG_HONEST_NEGATIVE, VWFA-composed CG_HONEST_NEGATIVE, PPMI/SVD CG_MEASURED_BOUND_LOW_DELTA r@5=0.6791 vs char-trigram 0.7030). That row is a genuinely closed, unrelated finding about non-neural / non-distilled mechanisms losing to bag-of-words at scale — it does NOT bear on whether the BGE-distilled MLP checkpoint (step1b v2/v3c) would pass the ship metric, and should not be read as pre-judging this thread.

---

## B. IS 0.85-NATIVE (TEACHER-FREE) REALISTIC? — honest verdict

**No.** Cross-referencing `research_5x_drill_perception_encoder_spec_and_brain_mechanism_2026-07-05.md` (read in full this cycle, not re-run): the "student <= teacher" DPI bound is an informal folk bound, not a proven ceiling (Born-Again Networks, Noisy Student, DINOv2>CLIP are real empirical counterexamples) — so teacher-dependence is not a shameful design compromise. But native self-supervision needs real corpus scale (word2vec/GloVe-class quality typically needs 50-500M tokens) that the substrate's 970K-item KB is very likely well under. The substrate's own teacher-free experiment (`exp_n11_random_indexing_semantic_v1`, full run on text8/17M tokens, verdict MIDDLE_BAND, similar/dissimilar ratio 1.20, control-null-confirmed CV<0.001) is real, statistically clean, control-verified signal — and plateaus far short of BGE-class absolute separation, with an honest realistic native ceiling around 0.65-0.75 (Random-Indexing TOEFL-synonym literature: ~65-80%), not 0.85.

**Distillation-from-BGE is the pragmatic path — and per this cycle's finding, may already be much closer to the ship metric than assumed.** The recorded fallback in project memory ("Can't hit 0.85 -> distill-from-BGE; M4 defers") should be revised from "assumed-hard fallback" to "confirmed-correct AND possibly closer to landed than tracked" pending the cheap decisive test below.

---

## C. HIGHEST-LEVERAGE NEXT EXPERIMENT (spec only — no dispatch)

### Cell: `exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1`

**What it does (pure composition of already-existing infra, no new mechanism):**
1. Re-verdict the in-batch-RKD-only arm of `step1b_v3c` on its OWN pre-registered bands, independent of the GLOBAL arm's algebra failure (this is a metrics-re-read, near-zero cost — should happen regardless of whether the cell below is dispatched).
2. Take the already-trained in-batch-RKD-only checkpoint(s) (5 seeds exist; use median-seed or majority-checkpoint-ensemble — verify at pre-flight whether seed checkpoints were persisted to disk or only their metrics; if not persisted, retraining this specific arm is the cheapest arm in the whole family: no landmark pairwise term, no InfoNCE, single-pass in-batch RKD).
3. Run **Step2** (full 970K sparse-encode, currently smoke-only) using that checkpoint.
4. Run **Step3** (100-query A/B gold-verify, H1-H4 criteria, currently crashed on missing artifact) using the Step2 output — this measures the actual USER goal-2 metric (cosine to the right answer on real queries), not the held-out concept-pair spearman proxy that 0.886 is measured on.
5. Re-run the FHRR bind/unbind roundtrip gate on COMPOSED multi-atom queries from Step3 (not just isolated concept codes as in v3c's keyed@J5) — a strictly harder, more realistic version of Goal 4.

**Why this is the highest-leverage move, not a new design:** it is the cheapest possible experiment (pure infra composition, checkpoint already trained, ~1-2 hrs CPU/GPU for encode + eval) that resolves the single highest-value open ambiguity in the whole encoder program: does the spearman-0.886 representational quality (measured on an idealized held-out-pairs split from the same distillation corpus) survive contact with the actual, harder, previously-expected-lower (~0.2-0.4 per 07-04 project notes) real-query gold-verify metric? Every other candidate next-move (native RI/BEAGLE-on-KB per the 07-05 drill; Lever-B soft-to-hard STE annealing per the GSBC training-recipe memo) is either lower-EV (native ceiling is honestly ~0.65-0.75, not 0.85) or addresses a DIFFERENT, not-yet-proven-necessary problem (STE/GSBC graded-code training assumes the block-argmax/GLOBAL chain is the right one to keep pushing, when the simpler in-batch-RKD arm may have already solved the semantic-fidelity half of the problem).

**Brain-grounding:** two independent mechanisms, both with real (not just plausible) published precedent per this cycle's lit-scan:
- **Distillation-as-bootstrap is the correct frame, not a crutch to escape** — human concept/language acquisition is not isolated self-supervision either; children bootstrap semantics from a competent language community (caregivers/culture) whose representations are the product of a much larger already-completed experiential learning process (feral-child cases show isolated self-supervision alone produces impoverished concept structure). BGE-as-teacher is the substrate's analog of that community bootstrap.
- **In-batch (local, relative) relational distillation beating a global-landmark (single-reference) objective** mirrors a documented pattern in both the contrastive-learning literature (in-batch/local negatives reliably outperforming global-memory-bank references when batch statistics are representative) and population-coding theory (local relative tuning across a population, not a single grandmother-cell-style landmark reference, is how sensory cortex represents and compares stimuli). The **objective-class recommendation from this cycle's lit-scan is concrete and precedented**: relational (RKD, Park et al. 2019, arXiv:1904.05068) and contrastive (CRD, Tian et al. 2020, arXiv:1910.10699) objectives consistently beat plain pointwise/global reconstruction at preserving retrieval geometry under a hard capacity/sparsity budget — exactly what v3c's internal ablation (in-batch RKD >> global-landmark RKD) already shows empirically. The ~2%-active sparsity target itself is independently grounded in Ahmad & Hawkins' HTM/SDR theory (arXiv:1503.07469: high dimensionality + fixed ~2% sparsity is required for low false-match error, with graceful noise degradation) and in measured cortical sparsity (Olshausen & Field 1996; ~0.5-2.5% active neurons per stimulus in awake sensory cortex, PubMed 9425546) — this cycle's lit-scan found NO evidence that hybrid distillation+sparse-coding is merely biologically-plausible-but-unproven-in-practice: SPLADE (production sparse retrieval, distilled from dense teachers), "Knowledge Distillation by Sparse Representation Matching" (arXiv:2103.17012), and SparseJEPA (arXiv:2504.16140, real quantitative gains: CIFAR-100 40.0%->45.4%, object-counting R^2 59.13%->62.33%) are concrete, quantitative precedents for exactly this hybrid.

---

## CHEAP DECISIVE TEST

The spec above IS the cheap decisive test. Cost: ~1-2 hrs CPU/GPU (Step2 full-KB encode is single-pass forward through an already-trained small MLP; Step3 is a 100-query eval harness that already exists and only needs a valid input artifact). No new mechanism, no new training objective, no GPU-scale hyperparameter search — pure carry-through of a result already sitting on disk.

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL, pre-registered here)

| Prediction | HARD-PASS | HARD-FAIL | MIDDLE_BAND | If HARD-FAIL |
|---|---|---|---|---|
| In-batch-RKD checkpoint's held-pair spearman-0.886 translates to the real ship metric (Step3 gold-verify top-1 cosine-to-right-answer) | top-1 cosine-to-gold >= 0.80 AND algebra roundtrip on COMPOSED queries >= 0.95 AND ret-agreement@10 vs teacher >= 0.30 | top-1 cosine-to-gold < 0.60 (fails to clearly beat the orthographic ceiling ~0.49-0.55) OR composed-query algebra roundtrip < 0.85 | cosine-to-gold in [0.60, 0.80) | Held-pair spearman was a favorable/idealized proxy (train-corpus-adjacent split); the semantic-fidelity gain does NOT transfer to genuinely novel real-query composition; re-open the training-fidelity lever ladder (Lever B soft-to-hard STE per the GSBC training-recipe memo) as the next move instead of shipping this checkpoint |
| The in-batch-RKD objective (no landmark, no InfoNCE) generalizes to the FULL 970K KB (not just the 178K teacher-cache subset used in v3c) without re-corrupting | Step2 full-KB sparsity/roundtrip metrics match the smoke's HARD_PASS profile (k_mean ~82, near-zero roundtrip mismatches) at the larger scale | roundtrip mismatches appear at >5% of items, or k_mean drifts outside [72,92] (10% band around target) | -- | Scale-dependent degradation exists in the encoder itself (not just the training objective); would need a scale-matched retrain, not just a bigger encode pass |
| Algebra survives under REALISTIC composed (multi-atom bound) queries, not just isolated concept-code roundtrip | composed-query FHRR bind/unbind roundtrip >= 0.95, matching the isolated-code keyed@J5=1.000 | composed-query roundtrip < 0.85 despite isolated-code roundtrip being 1.000 | roundtrip in [0.85, 0.95) | Binding composition (not the code itself) is where fidelity is lost — the false-win-algebra pattern seen in the GLOBAL arm may recur under composition even for the in-batch arm's clean isolated code; would need a binding-aware regularizer (Lever 4 in the GSBC training-recipe memo, previously deferred as "don't pre-pay for insurance the format may not need") |

**P_deflated = 0.42** for the headline HARD-PASS band (cosine-to-gold >= 0.80 on real queries). Reasoning: raw prior from the strength of the held-pair evidence (0.886 spearman, 5/5 seeds, intact algebra) would support ~0.55-0.65, but this is deflated per the lit-scan calibration penalty (0.15-0.25) because (a) there is no published precedent for GSBC block-sparse distillation reaching production dense-embedding retrieval quality specifically, and (b) held-out-concept-pair spearman on a train-adjacent split is a structurally easier eval than open real-query gold-verify (project notes' own prior expectation for the orthographic reality-check was ~0.2-0.4, and while this checkpoint is a different, better mechanism, the SAME structural gap between "pairwise similarity on curated concepts" and "answer the actual query" applies). Capped within the 0.50 novel-synthesis ceiling per [[feedback-lit-scan-calibration-penalty]].

---

## CROSS-THREAD SYNTHESIS

This drill directly extends and corrects `research_5x_drill_perception_encoder_spec_and_brain_mechanism_2026-07-05.md` (same day, earlier): that drill correctly answered the NATIVE-vs-DISTILLED framing question (teacher-dependence is a legitimate, brain-precedented bootstrap; native ceiling is honestly ~0.65-0.75) but its situational read of "where the DISTILLED pipeline currently stands" was built from the lever-ladder note's block-argmax/GLOBAL-chain numbers (ret_agree10 0.60/0.68, hi80_cos 0.83-0.845, "student at ~47-53% of its own ceiling") — it did not have visibility into the buried in-batch-RKD arm inventoried here, which is a DIFFERENT, simpler, better-performing training objective within the SAME distillation family. The two notes are complementary, not contradictory: this note narrows the "close the training-fidelity gap" recommendation from "try the GSBC graded-code + Lever-B STE annealing program" (a genuinely novel-synthesis, uncharted-precedent path per the training-recipe memo's own P_deflated=0.44) to "first verify whether the gap is ALREADY closed by an existing, cheaper, better-precedented objective that was landed but never carried through to the ship metric." If the cheap decisive test HARD-PASSes, the GSBC graded-code training-recipe program (Lever 1-4, `research_drill_graded_global_topk_gsbc_training_recipe_2026-07-04.md`) becomes lower priority — it was solving a problem (cashing a higher CEILING via graded codes) that may not be the binding constraint if simple in-batch RKD on the existing block-argmax format already clears the bar. If it HARD-FAILs, the GSBC graded-code program remains the correct next lever, now with an added, cheaply-falsified data point about where exactly the proxy-to-real-metric gap lives.

This also closes a `[[feedback-negativity-bias]]` / `[[feedback-2x-drill-negatives-before-capability-closure]]` gap of the SAME shape the 07-05 drill flagged for the n11 Random-Indexing result (a real result sitting 13 days unfollowed-up): the v3c in-batch-RKD win has been sitting unfollowed-up since its landing (single commit, no verdict-promotion, no cap_map entry) because the cell's aggregate verdict label (HARD_FAIL, driven by the co-located GLOBAL arm) masked it. Per [[feedback-research-every-finding-middle-negative-for-mechanism-and-envelope-push]]: tier is not the finding — a HARD_FAIL cell can contain a HARD_PASS-caliber result in one of its arms, and per-arm metrics (not the summary verdict string) are the load-bearing signal, directly reinforcing [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]].

---

## SUBSTRATE-PRODUCT IMPLICATIONS

- **If the carry-through cell HARD-PASSes:** the encoder's semantic-fidelity blocker to 0.85 is effectively CLOSED with an already-trained, already-cheap checkpoint — no new training run needed, only the (near-zero-cost) Step2/Step3 pipeline execution. This would unblock M4 (consolidation/attention) far sooner than the 07-04 record assumed, and would mean the "can't hit 0.85 -> distill-from-BGE" fallback is not just correct but nearly SHIPPED, pending real-query verification.
- **If it HARD-FAILs or lands MIDDLE:** it cheaply and concretely localizes the proxy-to-real-metric gap (train-adjacent-pairs vs genuine open queries, or isolated-code vs composed-query algebra) — either finding is directly actionable and both are cheaper to have than not knowing, per the USER standing directive to research every finding (middle/negative especially) for mechanism and envelope-push.
- **Either way:** the buried-win-in-a-failed-cell pattern is a process gap worth hardening structurally (per-arm metrics review as a standing check on any paired/multi-arm cell before its aggregate verdict is treated as final), independent of this specific cell's outcome.
- **Product framing, honestly stated:** "own our perception, natively" should be read (as the 07-05 drill already concluded) as "own the algebra and the memory mechanism; bootstrap the perception front-end from a teacher the way distillation research and human language acquisition both do" — and this cycle adds: that bootstrap may already be working, pending the cheap verification below.

---

## CITATIONS

**Verified this cycle — external (16, via 2 parallel Sonnet lit-scan sub-agents, generic-terms-only per query-privacy discipline):**
1. "Decoding Dense Embeddings: Sparse Autoencoders for Interpreting and Discretizing Dense Retrieval" — arXiv:2506.00041 (k-sparse SAE distillation of SimLM: MRR@10 0.343 @ k=32 vs dense 0.411, ~83% recovery; 0.368 @ k=128, ~89.5%)
2. SPLADE learned-sparse retrieval — near-parity with dense (MRR@10 0.322 vs ANCE 0.330); sbert.net sparse-encoder distillation docs
3. Dense retrieval distillation survey — arXiv:2211.14876 (capacity-gap effectiveness decay)
4. "Geometric Limits of Knowledge Distillation: A Minimum-Width Theorem" — arXiv:2604.04037
5. RKD (distance-wise + angle-wise) — Park et al. 2019, arXiv:1904.05068
6. CRD (Contrastive Representation Distillation) — Tian et al. 2020, arXiv:1910.10699
7. CSR "Beyond Matryoshka" — Wen et al., ICML 2025, arXiv:2503.01776
8. Olshausen & Field 1996, sparse coding of natural images (V1) — PubMed 9425546, Nature 381:607-609
9. Super-sparse V1 population codes (awake monkey, ~0.5% active) — bioRxiv 10.1101/252940
10. Rao & Ballard 1999, hierarchical predictive coding — homes.cs.washington.edu/~rao/predcoding2011.pdf
11. Millidge et al., PC-vs-backprop representation-quality gap in self-supervised settings — arXiv:2106.13082, arXiv:2506.06332
12. Ahmad & Hawkins 2015, HTM sparse distributed representations (dimensionality + ~2% sparsity -> low false-match, graceful noise degradation) — arXiv:1503.07469
13. HTM Spatial Pooler — Frontiers Comp. Neurosci. 2017, PMC5712570
14. Population codes in visual cortex (readout framework) — PMC3688279
15. "Knowledge Distillation by Sparse Representation Matching" — arXiv:2103.17012
16. SparseJEPA — arXiv:2504.16140 (CIFAR-100 40.0%->45.4%, object-counting R^2 59.13%->62.33%)

**Cross-referenced (verified in a prior session, not re-verified this cycle) via `research_5x_drill_perception_encoder_spec_and_brain_mechanism_2026-07-05.md`:** 26 external citations covering DPI/distillation-ceiling counterexamples (Born-Again Networks, Noisy Student, DINOv2), temporal-slowness/Foldiak/SFA, Random Indexing/BEAGLE (Kanerva, Sahlgren, Jones & Mewhort), word2vec-as-PMI-factorization (Levy & Goldberg 2014) — see that note for the full list; not duplicated here.

**Internal, freshly verified on disk this cycle (12 artifacts):**
1. `data/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1/metrics.json` (FULL)
2. `data/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1_smoke/metrics.json`
3. `data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1/metrics.json`
4. `data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_{7,13,23,29,31}/metrics.json` (5 files)
5. `data/exp_encoder_step1b_capacity_ceiling_train_vs_held_diagnostic_v1/metrics.json`
6. `data/exp_encoder_migration_step2_sparse_encode_970K_KB_v1_core*/metrics.json` (smoke only)
7. Step3 gold-verify metrics dir (smoke only, crashed)
8. `preregs/2026-07-04_exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1.md`
9. `notes/substrate_capability_map.md` v597 (META row, `MM_STANDARD_5_WITNESS_GATE_1_SATISFIED`)
10. `notes/research_5x_drill_perception_encoder_spec_and_brain_mechanism_2026-07-05.md`
11. `notes/research_drill_graded_global_topk_gsbc_training_recipe_2026-07-04.md`
12. git log (`6662c5717` step1b v3 core, `94062aecc` step1b v3c core — both code-landed, no verdict-promotion commit)
