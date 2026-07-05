# 5x convergence drill — perception/encoder spec + brain mechanism for teacher-free grounding

**Date:** 2026-07-05
**Type:** 5x parallel convergence drill (constructive build spec, NOT vs-LLM comparison)
**Driver:** USER framing — encoder GSBC_EXPAND2X MEETS the 4 confirmed goals (native perception / 0.85 coarse cosine / ~2% sparse / algebra-survives) but DISTILLS BGE (the "one real bound": encoder <= teacher per DPI). Sharper question: brain does perception with NO external teacher network — is that an existence proof that native, non-distilled perception is achievable at target quality, and is it worth building now?
**Calibration:** lit-scan penalty applied (deflate 0.15-0.25); novel-synthesis P capped at 0.50 per [[feedback-lit-scan-calibration-penalty]].

---

## HEADLINE

**The DPI framing that motivated this drill is weaker than assumed, and the substrate already ran the decisive teacher-free experiment 13 days ago without following it up.** Five independent lit-scan angles converge on: (1) raw co-occurrence/distributional statistics genuinely carry recoverable semantic-similarity structure with zero external teacher (word2vec/GloVe are *provably* PMI-matrix factorizations — Levy & Goldberg 2014 — and the VSA-native realization of this, Random Indexing/BEAGLE, is real and well-established); (2) low-level Hebbian/sparse/predictive-coding mechanisms alone do NOT produce semantic similarity — they produce efficient/orthogonal *perceptual* codes, and the brain's bridge from perceptual to semantic is **temporal-contiguity/slowness learning** (Foldiak trace rule / Slow Feature Analysis), which converges exactly with the substrate's own prior 5x drill (2026-07-02) that put predictive-coding's earned complexity at "Spoke 2 temporal contiguity," not flat Spoke-1 concept encoding; (3) "student <= teacher" as a hard information-theoretic ceiling is an **informal folk bound, not a proven theorem** — Born-Again Networks, Noisy Student, and DINOv2-beats-CLIP are direct empirical counterexamples, and distillation is best understood as a data-efficient *bootstrap*, not an iron cap; (4) teacher-free self-supervision reliably needs corpus scale (tens to hundreds of millions of tokens) that the substrate's own already-executed test confirms it does not yet have at full semantic-separation strength; and (5) the substrate ALREADY BUILT AND RAN a native Random-Indexing/BEAGLE cell (`experiments/exp_n11_random_indexing_semantic_v1.py`, full run on text8, 17M tokens) — verdict **MIDDLE_BAND**: a real, statistically clean, teacher-free distributional-semantic signal (similar/dissimilar cosine ratio 1.20, control-null-confirmed, CV<0.001) that is nonetheless far short of BGE-class absolute separation, and it has sat un-followed-up since 2026-06-22.

**Bottom line:** teacher-dependence is a legitimate, precedented bootstrap (not a shameful crutch) and the nearer-term, cheaper, higher-EV lever is closing the *training-fidelity* gap in the existing distillation pipeline (already pre-registered, [[research_drill_sparse_distill_fidelity_lever_ladder_2026-07-04]] Lever B). Native/teacher-free grounding is a real, brain-precedented, worth-pursuing SEPARATE research thread with a realistic target well below 0.85 at current corpus scale — and the cheapest next move there is not a new build, it's re-running the existing MIDDLE_BAND result through the actual encoder-goals dual-gate (semantic-cosine-to-gold + FHRR algebra) on the substrate's own 970K-item KB instead of the generic text8 corpus.

---

## A. WHAT WE WANT — exact spec, sharpened

**Original 4 goals (USER-confirmed 2026-07-04):** native perception, 0.85 coarse cosine, ~2% sparse, algebra survives.

**Sharpened spec, informed by this drill:**

1. **Decouple "hit 0.85" (the ship metric) from "teacher-free" (a property).** These are in real tension at current data scale. Every angle of this drill agrees: BGE-class absolute cosine (~0.83-0.90 range) requires either (a) distilling an already-internet-scale-trained model, or (b) training self-supervised on an internet-scale corpus (tens-hundreds of millions of tokens) directly. The substrate's KB is ~970K items — almost certainly below the token count where word2vec/GloVe-class self-supervision saturates on hard similarity benchmarks (angle 4: word-similarity saturates ~800K tokens for coarse tasks, but analogy/fine-similarity keeps improving with scale; BabyLlama-2 evidence shows small-corpus regimes favor distillation). **0.85 is the right target for a bootstrapped (distilled) encoder. It is very likely NOT achievable via native self-supervision at the substrate's current corpus size — that's a testable, falsifiable claim (see decisive test below), not an assumption.**
2. **Native/teacher-free perception, if pursued, needs its OWN realistic target**, calibrated from literature + substrate's own measurement: Random Indexing reaches ~65-80% on TOEFL-style forced-choice synonym tests (matching/beating non-native human test-takers, matching LSA) — i.e. a real but sub-BGE ceiling. The substrate's own `n11_random_indexing_semantic_v1` full run gives ratio 1.20 (similar/dissimilar cosine separation) with HIGH ABSOLUTE cosine on both similar (0.916) and dissimilar (0.762) pairs — meaning the discriminative signal is real (control-null-confirmed) but the *absolute-cosine-to-gold* metric the 0.85 goal actually uses would not cleanly separate at this operating point without further engineering (weighting/whitening against high-frequency "hub" context words — the classic Random-Indexing hubness problem). **Native MVP target: cosine-to-gold on the goal-4 dual-gate >= 0.65 (clears the current orthographic ceiling of 0.49-0.52 by a wide, meaningful margin) while preserving FHRR bind/unbind algebra fidelity — NOT 0.85.**
3. **Goal 4 (algebra survives) is non-negotiable for ANY candidate encoder, native or distilled** — this doesn't change. Any native-grounding candidate must clear the SAME FHRR roundtrip gate GSBC_EXPAND2X clears (currently 1.0 at keyed@J5).
4. **MVP / "done" definitions, both paths:**
   - *Distilled path (current):* ret_agree10 climbs from 0.60/0.68 toward the 0.35 target region tracked by the lever-ladder (this is a RETRIEVAL metric, distinct from hi80_cos which is already close to 0.85 at 0.83-0.845) via the pre-registered soft-to-hard STE fix — no redesign needed.
   - *Native path (new):* re-evaluate existing RI/BEAGLE vectors (or a freshly-trained-on-KB variant) through the Step-3 gold-verify harness (`experiments/exp_encoder_migration_step3_gold_verify_100_queries_A_B_v1_core.py`, H1-H4 criteria) AND the FHRR algebra gate, on the substrate's OWN 970K-item KB corpus rather than text8. "Done" = clears >= 0.65 cosine-to-gold and passes algebra — a genuine, teacher-free upgrade over Step-1 orthographic, even short of 0.85.

---

## B. HOW THE BRAIN DOES IT — mechanism, concretely, as existence proof

**What does NOT, by itself, produce semantic similarity** (angle 1, converged): Hebbian/Oja's-rule (implicit online PCA), BCM, STDP (Bi & Poo 1998; Xie & Seung 2000 differential-Hebbian recast), predictive coding (Rao & Ballard 1999; local Hebbian-product weight update, no backprop, no labels — genuinely self-supervised "predict the input" objective), sparse coding (Olshausen & Field 1996 — L1-penalized reconstruction, Nature 1996, produces Gabor-like V1 filters from raw image statistics alone), dentate-gyrus sparse expansion (pattern SEPARATION/orthogonalization — decorrelates, does not cluster semantically-related items together; this is a direct correction to any assumption that "sparse expansion = semantics"), and self-organizing/competitive maps (Kohonen, von der Malsburg — topographic organization of low-level feature space). All five are real, well-established, label-free, teacher-free learning rules. All five operate on and improve PERCEPTUAL/statistical efficiency (variance capture, sparsity, orthogonality, topographic smoothness) — none of them, alone, makes "cat" and "kitten" end up close in representational space.

**The concrete brain-mechanism that DOES bridge perceptual to semantic, with zero labels and zero teacher network:** temporal-contiguity/slowness association — Foldiak's trace rule (1991) and Slow Feature Analysis (Wiskott & Sejnowski 2002) — which treats temporally-adjacent-but-perceptually-different observations as referring to "the same underlying thing," an implicit self-supervised label extracted purely from the STATISTICS OF EXPERIENCE OVER TIME, not from any external supervisor. Recent modeling work (arXiv:2602.04462, 2509.15751, 2405.05143) shows temporal-slowness self-supervision produces object representations whose similarity structure tracks real-world co-occurrence statistics far better than frame-static models — i.e., this is the brain's version of modern temporal-contrastive self-supervised learning, with TIME replacing labels.

**This directly converges with the substrate's own prior work**: [[reference_5x_drill_convergence_PC_redundant_with_WTA_for_concept_encoding_Spoke1_2026-07-02]] already found PC redundant with competitive-Hebbian/WTA at the FLAT (Spoke 1) concept-encoding regime, but explicitly identified "Spoke 2 — temporal contiguity" as exactly where predictive-coding-style mechanisms earn their complexity across all 5 of ITS drill angles. This new drill's angle-1 finding (temporal-slowness is THE semantic-bridging mechanism) is independent confirmation of that prior conclusion from a completely different literature slice.

**Existence-proof status, honestly qualified (angle 2):** the brain's route from raw exposure to semantic similarity is NOT "pure statistics in total isolation" — cognitive science (Harnad 1990 "Symbol Grounding Problem"; Barsalou's Perceptual Symbol Systems) argues, and this is a live, unresolved debate, that co-occurrence statistics decoupled from any sensorimotor/referential grounding cannot constitute full meaning. Distributional statistics (Firth/Harris hypothesis) demonstrably predict a large chunk of human similarity judgment (Günther/Rinaldi/Marelli 2019) and infant statistical learning (Saffran et al. 1996) shows humans extract real structure from raw unsupervised streams from 8 months old — so "statistics-alone" is a real, evidenced, PARTIAL mechanism, not a strawman. But it is honestly not the WHOLE story biologically. Text-only distributional learning (word2vec/BERT-class, and by extension any text-only VSA/HDC native encoder) captures a genuine but partial slice of what the brain does.

---

## C. 5x CONVERGENCE — consensus and divergence

| Claim | Angles agreeing | Status |
|---|---|---|
| Raw co-occurrence stats carry real, teacher-free-recoverable semantic structure | 1 (temporal-slowness), 2 (Firth/Harris, Saffran), 3 (Random Indexing/BEAGLE numbers), 4 (word2vec = provable PMI factorization) | **CONVERGENT, strong** |
| Low-level Hebbian/sparse/predictive/DG mechanisms alone do NOT create semantic similarity — only efficient perceptual codes | 1 (explicit), 3 (FlyHash "preserves not creates" — JL/LSH theory) | **CONVERGENT** |
| Teacher-free self-supervision needs real data scale to reach dense-embedding-class quality; below that, distillation-from-a-teacher is a reliable data-efficiency win, not a crutch | 4 (BabyLlama-2, TinyBERT/DistilBERT numbers), 5 (Noisy Student/Born-Again as bootstrap-not-ceiling framing) | **CONVERGENT** |
| "student <= teacher" (DPI) is an informal folk bound in distillation, not a proven ceiling; self-supervised-from-scratch's TRUE ceiling is the raw data's own information content, independent of any specific teacher, and CAN exceed a given teacher | 5 (direct focus), corroborated by 4's framing of distillation-as-transfer-learning | **CONVERGENT — this REVISES the drill's own premise** |
| Pure statistics-without-grounding is philosophically/empirically contested as SUFFICIENT for full human-level semantics | 2 (Harnad/Barsalou vs Firth/Harris/Rogers-McClelland) | **DIVERGENT — flagged honestly, not resolved** |
| VSA-native random-projection/co-occurrence encoders (Random Indexing/BEAGLE) plateau clearly below BERT/BGE-class dense embeddings on hard similarity benchmarks | 3 (TOEFL 65-80% vs GloVe ~90%; no VSA paper found at BGE-class STS correlation), substrate's own n11 result | **CONVERGENT, and now substrate-CONFIRMED (see D/E)** |

**Net revision to the driver premise:** the DPI-bound framing ("encoder <= teacher, undercuts standalone claim") is real in a loose, practical sense but is NOT the sharp, provable ceiling the framing implied — and more importantly, per the lever-ladder note, the substrate's CURRENT distilled student is at only ~47-53% of its OWN teacher-intersected code ceiling. The binding constraint right now is training fidelity within the chosen (distilled) approach, not the theoretical existence of a teacher upstream.

---

## D. AUGMENT BEYOND BIOLOGY — legitimate vs illegitimate use of compute/teacher

**Where high-energy compute legitimately exceeds slow biological learning** (per USER ground rule — brain is baseline+proof, not a ceiling): large-negative-sample contrastive pretraining (SimCLR/InfoNCE/DINOv2 - angle 5), dense-float backprop through discrete bottlenecks via soft-to-hard annealing (angle-adjacent, lever-ladder note), and internet-scale self-supervised corpora — none of these have biological energy-budget analogs and all are fully available to the substrate's build process.

**Is a big pretrained teacher (BGE) a legitimate augment/bootstrap, or a dependence to escape?** This drill concludes: **legitimate augment, well-precedented, and arguably MORE brain-analogous than "isolated self-supervision" would be.** Human language/concept acquisition is not pure isolated self-supervised learning either — children bootstrap semantics substantially from a competent LANGUAGE COMMUNITY (caregivers, culture) whose representations are themselves the product of a much larger, already-completed distributional/experiential learning process; feral-child cases show isolated sensory self-supervision without a "teacher" (community) produces severely impoverished language/concept structure. BGE-as-teacher is the substrate's analog of that community bootstrap: a compressed proxy for expensive internet-scale self-supervised training, applied to a small native corpus, exactly the pattern angle 4/5 show works well at modest data budgets (BabyLlama-2 distilled-on-10M-words beats from-scratch-on-10M-or-100M-words; Noisy Student/Born-Again show iterative self-distillation legitimately exceeding a fixed teacher over successive rounds).

**Keep native (Random-Indexing/BEAGLE-class) self-supervision as the honest, teacher-free FALLBACK BASELINE** — real mechanism, brain-precedented, cheap to run (already built), useful for reporting a genuinely-standalone number and as a long-horizon research bet if/when the KB corpus scales up substantially (word2vec/GloVe-quality typically needs 50-500M tokens; a 970K-item KB is very likely well under that, though item length matters and hasn't been tokencount-verified in this drill — flagged as an open question, not asserted).

---

## E. SUBSTRATE FIT + FIRST BUILD — is the encoder done, and what's the decisive next move

**The substrate already ran the closest thing to a teacher-free perception experiment it has.** `experiments/exp_n11_random_indexing_semantic_v1.py` (full run, `data/exp_n11_random_indexing_semantic_v1/metrics.json`, verdict **MIDDLE_BAND**, filed under the 2026-06-22 drill `notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md`) tested exactly this hypothesis on text8 (17M tokens, real corpus, not synthetic):

- RANDOM_INDEXING_ALONE: similar-pair cosine 0.916, dissimilar-pair cosine 0.762, ratio **1.20**, CV 0.0005 (near-zero — tight, reproducible signal)
- RI_PLUS_BEAGLE_ORDER (adds HRR circular-convolution order-binding): ratio 1.214, similar 0.884 — comparable, order-binding doesn't add much here
- RI_HUB_SPOKE_KGSTORE (composed with substrate's orthographic char-trigram encoder): ratio 1.183, but absolute cosines collapse (0.468/0.396) — **composing with the orthographic spoke actively hurts**, contrary to the cell's own ATL hub-spoke hypothesis
- CONTROL_RANDOM_PERMUTE (position-shuffled corpus, destroys distributional structure): ratio 1.001 — **confirms the RI signal is real, not an artifact** (control is cleanly null)

**Honest read of this result:** the distributional/co-occurrence signal is genuinely present and statistically airtight (control-verified, near-zero CV across seeds) — this is substrate-level, on-disk CONFIRMATION of the angle-3/angle-4 literature convergence. But it is NOT yet in the form the 0.85 goal needs: (a) it used a raw similar-vs-dissimilar RATIO metric on handcrafted category probes, not the goal's absolute cosine-to-gold-answer metric or the algebra-survival gate; (b) both similar AND dissimilar absolute cosines are high (0.92 / 0.76) — the classic Random-Indexing "hubness" problem (common context words dominate raw bag-of-context vectors) — meaning a naive port to an absolute-threshold metric like the 0.85 goal would likely under-discriminate without weighting/whitening (PPMI-style down-weighting of high-frequency contexts, which is precisely what real Random Indexing implementations use and this cell's docstring doesn't mention adding); (c) it never went through the FHRR bind/unbind algebra gate; (d) it ran on text8 (generic word2vec benchmark corpus), not the substrate's own 970K-item KB — so it doesn't tell us what native grounding on the SUBSTRATE'S OWN DATA would look like; and (e) this MIDDLE_BAND landed 13 days ago and was never followed up (no cap_map row references it, no lever iteration filed) — a clean case of "negative/partial result parked instead of 2x-drilled," per [[feedback-negativity-bias]] and [[feedback-2x-drill-negatives-before-capability-closure]].

**Is the (distilled) encoder done?** For the SHIP metric: essentially yes on coarse cosine (hi80_cos 0.83-0.845 is already near the 0.85 target), and the retrieval-fidelity shortfall (ret_agree10 0.60/0.68) has an already-pre-registered, cheap (~few-hour CPU), high-EV fix in flight (Lever B: soft-to-hard STE annealing, P_deflated~0.25-0.33, [[research_drill_sparse_distill_fidelity_lever_ladder_2026-07-04]]). That is the correct near-term move — NOT a redesign, NOT chasing native-grounding as a 0.85 substitute.

**The single most decisive next experiment for the native-grounding thread (separate track, not gating):** re-run the EXISTING RI/BEAGLE mechanism (`hdlab/random_indexing.py` per the n11 cell) trained on the substrate's own 970K-item KB corpus (not text8) with PPMI-style context-weighting added (to address the hubness problem observed), then evaluate through the SAME Step-3 gold-verify harness (`exp_encoder_migration_step3_gold_verify_100_queries_A_B_v1_core.py`, H1-H4) plus the FHRR bind/unbind algebra gate used for goal 4. This is cheap (CPU-only, single-pass co-occurrence accumulation, the RI infra already exists) and directly answers, on the substrate's own data and the substrate's own success metric, whether native grounding is a viable near-term upgrade over the orthographic Step-1 baseline (0.49-0.52) — independent of whether it ever reaches 0.85.

---

## CHEAP DECISIVE TEST

**Cell:** `exp_n11b_random_indexing_kb_native_dualgate_v1` (new — adapts existing `hdlab/random_indexing.py` + Step-3 gold-verify harness; no new mechanism, re-composition of existing chain-grade infra)

- Train Random Indexing (with PPMI/entropy-style context down-weighting added, addressing the observed hubness collapse) on the substrate's own 970K-item KB text (same corpus Step 1/1b use), at the SAME sparsity target (~2%, N matched to GSBC_EXPAND2X's N=4096/k~82-92 config) and SAME dimensionality family.
- Evaluate via the Step-3 100-query gold-verify harness (top-1/top-10 cosine-to-gold, H1-H4 criteria) AND the FHRR bind/unbind roundtrip algebra gate.
- Arms: RI_ALONE, RI_PLUS_BEAGLE_ORDER (both already implemented), plus RI_PPMI_WEIGHTED (new — the hubness fix); CONTROL_RANDOM_PERMUTE carried forward as the null-signal check.

**Pre-registered HARD bands:**

- **HARD-PASS:** best arm reaches cosine-to-gold (Step-3 top-1, H1 delta over bag-word) >= 0.65 absolute AND clears the FHRR algebra roundtrip gate at parity with GSBC_EXPAND2X (>= 0.95 roundtrip fidelity) AND beats the orthographic Step-1 ceiling (0.49-0.52) by >= 0.10 absolute AND CONTROL stays null (ratio <= 1.1) -> native grounding is a credible, teacher-free upgrade path; fund it as a genuine parallel research thread (not a 0.85 replacement, an honest ~0.65-0.75-class alternative with a real "no external teacher" claim).
- **HARD-FAIL:** best arm cosine-to-gold < 0.55 (fails to clearly beat orthographic ceiling) OR algebra gate fails OR CONTROL loses its null property (signal is an artifact) -> native self-supervised-from-scratch is NOT viable at the substrate's current corpus scale (970K items too small / too different in structure from text8); teacher-dependence (BGE distillation) is CONFIRMED as the correct near-term bootstrap; shelve native-from-scratch until KB ingest scales materially (candidate re-trigger: >=10x corpus growth, i.e. ~10M+ items or equivalent token count — needs an actual token-count check, not asserted here).
- **MIDDLE_BAND:** cosine-to-gold in [0.55, 0.65) -> partial signal (consistent with the ALREADY-OBSERVED text8 MIDDLE_BAND); route to HYBRID — use RI/BEAGLE co-occurrence vectors as an auxiliary feature channel INTO the existing BGE-distillation training (e.g. concatenated input or auxiliary self-supervised regularizer), not a standalone replacement.

**Cost:** ~1-2 hrs CPU (co-occurrence accumulation is single-pass, no GPU needed; the RI infra and gold-verify harness both already exist — this is composition, not new-mechanism engineering). Smoke at 1K-entity KB slice first, matching the Step-1/2/3 smoke convention already in place.

---

## FALSIFIABLE PREDICTIONS

| Prediction | HARD-PASS | HARD-FAIL | If HARD-FAIL |
|---|---|---|---|
| Native RI/BEAGLE on substrate's own KB beats orthographic Step-1 ceiling meaningfully | cosine-to-gold >= 0.65 | cosine-to-gold < 0.55 | Native-from-scratch shelved; corpus too small; distillation confirmed as correct bootstrap |
| PPMI-weighting fixes the observed hubness collapse (both-high-absolute-cosine problem seen in text8 run) | RI_PPMI_WEIGHTED shows dissimilar-pair absolute cosine drops >= 0.15 vs RI_ALONE while similar-pair holds | dissimilar cosine stays within 0.05 of RI_ALONE | Hubness is structural to bag-of-context accumulation at this scale, not a weighting artifact; would need a different native mechanism (e.g. BEAGLE-order-only, or contrastive re-weighting) |
| Algebra survives on a native (non-distilled) code | FHRR roundtrip >= 0.95, matching GSBC_EXPAND2X's 1.0 | roundtrip degrades below 0.85 | Native RI encoding is incompatible with the compositional-algebra requirement even if semantically adequate; would need a structurally different sparsification scheme for RI vectors |
| Distillation is (still) the right near-term bootstrap regardless of native-path outcome | Lever B (soft-to-hard STE) delivers ret_agree10 >= 0.26-0.30 @ K128 per its own pre-registered test | Lever B fails to move ret_agree10 by >= 0.03 | Training-fidelity gap is NOT estimator-driven; re-open capacity (Lever A) or schedule (Lever C) per the lever-ladder ranking |

---

## SUBSTRATE-PRODUCT IMPLICATIONS

- **If native RI/BEAGLE HARD-PASSes on KB data:** substrate gains an honest, fully-standalone ("zero external teacher, zero external model weights") perception path at a real (if sub-0.85) quality level — valuable for any product narrative that requires provable independence from a third-party embedding model (e.g. licensing, air-gapped deployment, "substrate owns its own semantics end-to-end"). It does NOT replace the distilled encoder for the 0.85 ship target; it becomes a second, complementary encoder family.
- **If HARD-FAIL (more likely per this drill's calibration):** definitively closes native-from-scratch as a near-term option, redirects the "own our perception" narrative honestly toward "own the ALGEBRA and the MEMORY MECHANISM (bind/unbind, sparse storage, retrieval) — bootstrap the PERCEPTION FRONT-END from a teacher the way distillation research and (arguably) human language acquisition both do." This is a more defensible, more honest product story than claiming full perceptual independence prematurely.
- **Either way:** the Lever-B STE fix on the existing distillation pipeline should ship first and independently — it's cheaper, already pre-registered, targets a measured (not assumed) gap, and its outcome doesn't depend on the native-path result.
- **Process note:** this drill surfaces a real process gap — a full-scale, control-verified, MIDDLE_BAND result (`n11_random_indexing_semantic_v1`) sat for 13 days with no cap_map entry and no follow-up lever. Recommend: any MIDDLE_BAND/PARTIAL verdict on a cell touching the encoder-goals thread gets a cap_map annotation and a 2x-drill trigger at landing time, not only on HARD_FAIL.

---

## CITATIONS (verified count: 26 external + 8 internal)

**External:**
1. Oja 1982, Oja's rule -> online PCA — scholarpedia.org/article/Oja_learning_rule
2. Bienenstock, Cooper & Munro 1982, BCM theory — en.wikipedia.org/wiki/BCM_theory
3. Bi & Poo 1998 / Xie & Seung 2000, STDP as differential Hebbian — scholarpedia.org/article/Spike-timing_dependent_plasticity
4. Rao & Ballard 1999, predictive coding, Nat. Neurosci. 2:79-87; arXiv:2107.00140; PMC5467749
5. Olshausen & Field 1996, sparse coding, Nature 381:607-609
6. Dentate gyrus pattern separation — PMC2829853; J. Neurosci. 2016 (36:29:7569)
7. Foldiak 1991 trace rule; Wiskott & Sejnowski 2002 Slow Feature Analysis — Frontiers Comp Neurosci 2012 (10.3389/fncom.2012.00037)
8. Temporal-slowness self-supervision modeling — arXiv:2602.04462, 2509.15751, 2405.05143; PMC8335547
9. Harris 1954 distributional structure; Firth 1957 — ACL Wiki Distributional Hypothesis; arXiv:2205.07750
10. Saffran, Aslin & Newport 1996, Science 274:5294 — infant statistical learning
11. Harnad 1990, Symbol Grounding Problem — cs.ox.ac.uk/activities/ieg/e-library/sources/harnad90_sgproblem.pdf; scholarpedia.org/article/Symbol_grounding_problem
12. Barsalou 2003, Perceptual Symbol Systems — barsaloulab.org/Online_Articles/2003-Barsalou-PTRSL-BS-abstraction.pdf
13. Rogers & McClelland 2004, Semantic Cognition PDP — Cambridge BBS precis; Nature Reviews Neuroscience
14. Günther, Rinaldi & Marelli 2019, vector-space models cognitive perspective — journals.sagepub.com/doi/abs/10.1177/1745691619861372
15. Kanerva, Kristoferson & Holst 2000, Random Indexing; Sahlgren 2005/2006 thesis — diva-portal.org/smash/get/diva2:1041127
16. Karlgren & Sahlgren 2001, TOEFL synonym test results (72.5% RI vs 64.4% LSA)
17. Jones & Mewhort 2007, BEAGLE, Psychological Review 114:1-37
18. Recchia, Sahlgren, Kanerva & Jones 2015, order-info encoding replication — PMC4405220
19. Dasgupta, Stevens & Navlakhe 2017, FlyHash, Science; arXiv:1812.01844
20. Ryali et al. 2020, BioHash — arXiv:2001.04907
21. Kleyko, Rachkovskij, Osipov & Rahimi 2021-2023, HDC surveys — arXiv:2111.06077, arXiv:2112.15424
22. Mikolov et al. 2013, word2vec — arXiv:1310.4546; Pennington, Socher & Manning 2014, GloVe
23. Levy & Goldberg 2014, skip-gram = implicit PMI matrix factorization — NIPS 2014
24. van den Oord et al. 2018, InfoNCE/CPC — arXiv:1807.03748; Poole et al. 2019 — arXiv:1905.06922; McAllester & Stratos MI-estimation impossibility — arXiv:1811.04251
25. Furlanello et al. 2018, Born-Again Networks — arXiv:1805.04770; Xie et al. 2020, Noisy Student — arXiv:1911.04252; Oquab et al. 2023, DINOv2 — arXiv:2304.07193
26. Stanton, Izmailov et al. 2021, "Does Knowledge Distillation Really Work?" NeurIPS; "Towards the Law of Capacity Gap" 2023 — arXiv:2311.07052; BabyLlama-2 — alphaxiv.org/overview/2603.29552v1

**Internal substrate provenance (verified on disk this session):**
1. `data/exp_n11_random_indexing_semantic_v1/metrics.json` — MIDDLE_BAND, RI_ALONE ratio 1.2016 (CV 0.0005), control null 1.0008
2. `experiments/exp_n11_random_indexing_semantic_v1.py` — cell source, existing RI+BEAGLE+hub-spoke infra
3. `notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md` — origin drill for n11
4. `notes/research_drill_sparse_distill_fidelity_lever_ladder_2026-07-04.md` — lever-ladder for the distilled-pipeline training-fidelity gap; Lever B top bet
5. `notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md` — prior brain-mechanism drill (multi-modular capacity, adjacent not overlapping)
6. `notes/wave14d_self_supervised_concepts_research.md` — prior self-supervised concept-DISCOVERY (post-encoder concept layer) drill, distinct problem from raw perceptual grounding
7. `/c/Users/marsh/.claude/projects/d--AI/memory/reference_5x_drill_convergence_PC_redundant_with_WTA_for_concept_encoding_Spoke1_2026-07-02.md` — prior 5x drill converging PC->Spoke2-temporal-contiguity; independently confirmed by this drill's angle 1
8. `/c/Users/marsh/.claude/projects/d--AI/memory/project_encoder_goals_native_perception_085_sparse_algebra_USER_CONFIRMED_2026-07-04.md` — the 4 confirmed goals + orthographic-ceiling finding this drill sharpens
9. `experiments/exp_encoder_migration_step3_gold_verify_100_queries_A_B_v1_core.py` — existing dual-gate eval harness, target for the decisive test's re-use
