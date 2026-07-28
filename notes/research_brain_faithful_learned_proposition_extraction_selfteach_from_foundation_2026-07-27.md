# Research: brain-faithful learned proposition extraction, self-taught from the foundation (v6 scoping)

Scoping note only. No experiments dispatched, no cells edited, no atoms banked. Purpose: sharpen the v6 decision (learned extraction head vs hand-built bind readout) regardless of how in-flight v5 lands.

## HEADLINE

The brain does NOT learn thematic-role binding as a single algebraic bound vector — it decodes agent/patient identity from **reusable, role-general subregions of left mid-superior temporal cortex** (Frankland & Greene 2015) that generalize across fillers, driven by an **error/prediction-based learning signal** (Rabovsky/McClelland's Sentence-Gestalt account of the N400; St. John & McClelland 1990 showed an SRN learns thematic roles purely from next-word/role-filling feedback, no hand labels). This is good news for the substrate: it means "learn a role-bound readout from a generic error signal, not from hand-labeled semantic-role data" is exactly the brain's strategy, not a shortcut. The mapping to our foundation-as-distant-supervision design is directly analogous to **distant supervision for relation extraction** (Mintz 2009 -> Lin 2016 PCNN+ATT), and that literature's single loudest warning is the one that should gate v6: **entity-pair / lexical shortcut leakage** (Peng et al. 2020: >50% of a standard RE benchmark is solvable from entity identity alone, with zero sentence content) is structurally the same failure our own "leak-proof" discipline already worries about (mean-pool v3 gain was "distributional sample-accumulation, not comprehension" — same species of artifact). A cheap, training-free diagnostic borrowed directly from that literature can be run before committing GPU time to a full learned head.

## Cheap decisive test (recommended, pre v6 commit)

Build a **~300-500 example offline dataset**, no training required:
1. Sample foundation edges `(subject, relation, object)`, stratified across relation types, split into TRAIN-concepts / HELD-OUT-concepts (concept-level split, not edge-level — reuse the same held-out-concept slice discipline already standing for the encoder).
2. For each sampled edge, generate **2-3 distinct surface realizations** per relation type (not one fixed template) — e.g. for `/r/UsedFor`: "X is used for Y", "people use X to Y", "X helps you Y" — so a connector-string shortcut can't trivially solve it. (If real corpus sentences mentioning both concepts exist in v4/v5's source corpus, prefer those over synthetic templates — synthetic templates risk being CONSTRUCTION-DETERMINED per standing discipline.)
3. Also generate **hard-negative distractors**: same subject, but the object swapped for a DIFFERENT true object of that subject under a DIFFERENT relation (not a random unrelated concept) — this is the discriminative case that actually tests role/relation binding rather than topical co-occurrence.
4. Compute two **training-free baselines** (the deflate null, directly from Peng et al. 2020's diagnostic):
   - **B0 identity-only**: predict relation from `(subject_id, object_id)` alone via a lookup/frequency table built from the TRAIN-concept edges only (no sentence text at all).
   - **B1 mean-pool-current**: the v4 broken order-blind mean-pooled sentence vector's cosine-similarity discriminativeness on this SAME relation-classification task (data we can reuse/extend from the v4 readout probe machinery) — checks whether the existing (known order-blind) representation already saturates relation-prediction even without order-sensitivity, which would mean order-sensitivity and relation-typing are different axes worth separately building for.
5. No training run, no queue dispatch — pure data construction + two lookups. Estimated cost: well under a day, CPU-only, can be done as a direct follow-up before authoring v6.

## Falsifiable predictions

**HARD-PASS (justifies committing to the v6 learned-binding-head build):**
- B0 (identity-only, no sentence) accuracy on HELD-OUT-concept edges is **< 40%** (task is not trivially solvable by concept-identity lookup — i.e., held-out concepts genuinely lack a frequency-table shortcut), AND
- B1 (current mean-pool) discriminativeness on the hard-negative (same-subject-different-relation) slice is **< 55%** (confirms the existing order-blind representation does NOT already solve relation-typing — there is real headroom for a role-bound readout to add value), AND
- the hard-negative distractor rate is high enough that a random/majority-relation baseline scores **< 35%** (dataset is not degenerate/one-relation-dominated).

**HARD-FAIL (do not build v6 yet; the design needs rework first):**
- B0 identity-only alone exceeds **65%** on held-out concepts -> the foundation's relation distribution is skewed enough per-concept that any "win" from a learned head would be indistinguishable from frequency memorization (mirrors the v3 "distributional sample-accumulation, not comprehension" downgrade almost exactly — same failure mode recurring under a new name).
- OR the synthetic-template surface forms turn out to be the ONLY available sentence source (no real corpus sentences) AND relation-type is recoverable from connector-phrase alone with >90% accuracy by a trivial bag-of-words classifier -> the task is CONSTRUCTION-DETERMINED (per standing discipline) and any v6 result off this data would be an artifact regardless of architecture.
- OR concept-level held-out split leaks (a held-out concept's mentions still co-occur, via the foundation's own graph, with heavily-overlapping neighbor concepts seen in train, such that B0 built on 1-hop-neighbor smoothing still exceeds 65%) -> need a stricter split (hold out a whole connected subgraph region, not scattered single concepts).

## Cross-thread synthesis (3 parallel lit-scans)

**Thread 1 — brain mechanism (neuroscience/developmental).** Established: STS/lmSTC holds decodable, role-general agent/patient subregions reused across fillers (Frankland & Greene 2015, *PNAS*) — evidence for a **slot architecture**, not one bound vector per sentence. Friederici's dorsal (structure-building, pSTG<->BA44) / ventral (semantic combination, uncinate<->BA45) stream split is well-established anatomy (Friederici 2011/2012) that plausibly underlies role assignment, though no single paper gives a unified "this is the role-binding locus" answer — that synthesis is mine, flagged interpretive. The **binding code itself is a genuinely unresolved debate**: synchrony (Hummel et al. 2004) vs conjunctive/sparse coding (van der Velde & de Kamps 2006); the field's closest thing to consensus is that the brain likely uses multiple complementary mechanisms, not one. TPR (Smolensky 1990) and HRR (Plate 1995) — our own native primitive's ancestor theory — are **computational proposals, not confirmed neural mechanisms**; treat our binding-based design as an engineering analog to the brain's role-general slot code, not a claim that cortex literally does circular convolution.

On the LEARNING SIGNAL question specifically (the crux for "self-taught, not bolt-on"): the strongest, most concrete account is **Rabovsky, Hansen & McClelland (2018, *Nature Human Behaviour*)** — the Sentence Gestalt model treats the N400 as an implicit prediction-error signal during incremental comprehension, i.e. the brain's proposition-extraction is trained continuously by "how surprised was I by what came next," not by external labels. **St. John & McClelland (1990)** independently showed an SRN can learn thematic-role assignment purely from a next-role-filling prediction task — no hand-labeled semantic roles required. Developmentally, **syntactic bootstrapping (Gleitman 1990)** and **usage-based construction learning (Tomasello)** both frame role-schema acquisition as learned from distributional/statistical exposure, not innate lookup — thematic-role assignment is **substantially learned**, which directly supports (does not undercut) the charter's "earn comprehension, don't bolt on a parser" invariant: the brain's own solution to this problem IS self-supervised learning from exposure, which is what v6 should be attempting.

**Thread 2 — distant supervision / weak supervision (the fairness engine for the mapping).** Our design ("foundation triples as target, sentence-mention-of-both-concepts as input") is structurally identical to distant-supervision relation extraction (Mintz et al. 2009), inheriting its entire known failure-mode literature wholesale. Two fixes are load-bearing and should be adopted directly: (1) **multi-instance / attention-over-mentions** (Lin et al. 2016 PCNN+ATT) if a concept pair has multiple candidate sentences, rather than trusting every alignment as a true positive; (2) **non-overlapping entity/concept-pair splits between train and held-out** (Peng et al. 2020's core fix, adopted as DREB-style benchmarks in 2025) — this is precisely our own "held-out-to-NEW-concept" bar already standing, so no new discipline is needed, just explicit enforcement at the (subject, object) PAIR level, not only the single-concept level. The **single most important transferable warning**: Peng et al. (2020) found over half of a standard benchmark solvable from entity mentions alone with zero sentence context — this is the exact shape of the v3 downgrade we already caught ("gain = distributional sample-accumulation... word-scrambled text gained AS MUCH as coherent"). The cheap decisive test above is a direct re-application of their diagnostic to our own setup, run BEFORE a training commitment rather than after (matching the DESIGN GATE discipline).

No direct precedent was found for commonsense-KG-specific (ConceptNet-scale, multi-relation) distant supervision at this scope — narrower LocatedNear-only extraction work exists (Xu et al. 2018) but not a general PCNN+ATT-style analog on ConceptNet-typed relations. This is a real gap, not a refuted direction — flagged low-confidence rather than dismissed, per standing "don't dismiss adjacent methods" discipline.

**Thread 3 — learned VSA/HRR binding (the mechanism for the readout).** Two directly relevant, higher-confidence precedents: **Steinberg & Sommer (2019, arXiv:1902.09006)** learn role-filler binding via a memory-augmented network WITHOUT explicit labeled role-filler pairs, and show generalization to fillers unseen during training in a given role — this is close prior art for "learn the role assignment end-to-end," though the paper reportedly notes a live disagreement over whether learned binding generalizes to novel role-filler combinations as well as fixed algebraic binding (worth reading in full before leaning on it). **Huang, Smolensky, He, Deng, Wu (NAACL 2018, TPGN)** trained TPR-style structured representations end-to-end and found the learned representations decompose into interpretable grammatical-role components — direct precedent that "train the binding readout, structure emerges" works, at least in image-captioning. **Ganesan et al. (NeurIPS 2021, arXiv:2109.02157, "Learning with Holographic Reduced Representations")** is the most practically load-bearing citation: it is a numerical-stability fix that makes HRR bind/unbind gradient-trainable — literally applicable to our existing `hdlab/binding.py` circular-convolution primitive if v6 needs the binding operation itself inside a backprop path (vs. only using bind/unbind as a fixed post-hoc readout op on a frozen encoder). No precedent was found for the specific combination we'd be building (contrastive coherent-vs-scrambled loss anchored to a KG target, through a native HRR bind) — this appears to be a genuinely novel combination, not refuted, but not de-risked by any existing result either; treat it as the actual experimental bet, not a replication.

## Substrate-product implications

- The mapping is **charter-compliant on inspection**: the foundation's 1.24M typed edges are KNOWLEDGE (layer 2, externally-sourced is allowed), and the extraction readout itself would be a small trainable module built from the substrate's OWN encoder + OWN native binding primitive — no external parser or reader sits in the comprehension path. This satisfies invariant #2 as stated, but the note below on brain-divergence flags where the analogy is looser than it looks.
- If the cheap decisive test HARD-PASSes, v6 is a **readout-only build**: freeze (or lightly fine-tune) the existing seed-7 encoder, add a small learned bind-target module, train against foundation-triple positives + hard-negative distractors with the concept-pair-level held-out split. This is a much smaller/cheaper commitment than another full encoder retrain, and reuses assets we already have (foundation, encoder, binding primitive, v4 probe harness for order-sensitivity measurement).
- If it HARD-FAILs on the identity-only-B0 threshold specifically, the fix is **not architecture** — it's dataset construction (need denser hard-negative distractors, or a stricter graph-region-level held-out split) before any learned head is worth building. This would save a wasted training cycle exactly the way the v3->v4 STEP-0 probe saved one for the order-sensitivity axis.
- Long-run (v7+) direction suggested by Thread 1: the brain's actual learning signal is **incremental, online, prediction-error-based** (next-word/next-role surprisal), not a batch contrastive objective over pre-assembled KG-triple targets. v6 as scoped here is a reasonable, buildable engineering proxy, but a more brain-faithful v7 would move toward an incremental within-sentence prediction-error objective (closer to St. John & McClelland 1990 / Rabovsky et al. 2018) rather than a fixed target-vector contrastive loss. Flagging now so it isn't lost.

## Brain-difference check (required per standing discipline)

Where this design DIVERGES from the brain, and whether each divergence is an acceptable engineering proxy or a shortcut to avoid:

1. **Supervision source**: brain's signal is intrinsic prediction error generated continuously during ordinary comprehension (no external "answer key"); v6 as scoped uses an EXTERNALLY-SOURCED knowledge graph as the target. **Acceptable per charter** — this is layer-2 KNOWLEDGE supply, explicitly allowed, and is a reasonable stand-in for "the meanings and relations a person has already learned by the time they read a new sentence" (adults don't derive `UsedFor` relations from scratch every time either — they bring prior relational knowledge to bear). Not a comprehension-mechanism shortcut as long as the EXTRACTION itself is learned, not supplied.
2. **Binding implementation**: brain's role code is a population/slot representation with an unresolved synchrony-vs-conjunctive mechanism; our design uses algebraic circular convolution (HRR). This is a known, long-standing, and explicitly acknowledged engineering analog (Smolensky/Plate), not a novel shortcut — acceptable, but should not be oversold as "how the brain does it." Steinberg & Sommer's finding that LEARNED binding may generalize differently than FIXED algebraic binding to novel role-filler pairs is worth tracking empirically once v6 is built (does our learned-target/native-bind hybrid inherit brain-like generalization, or does it behave like fixed HRR binding?).
3. **Objective shape**: brain's account (Rabovsky/McClelland) is incremental online next-word prediction error; v6 as scoped is a batch/pairwise contrastive objective (coherent vs. scrambled/wrong, anchored to a static KG target). This is the **largest divergence** and the most likely place a v6-negative result would actually be an artifact of objective shape rather than of the "learned binding" idea itself — worth remembering if v6 comes back flat, per the standing "brain-faithful + fail => digging, not defeat" discipline. Named here explicitly so it isn't rediscovered the hard way later.

## Risks

- Same-species risk as v3: a positive signal that is actually distributional/frequency memorization, not comprehension. Directly mitigated by the B0 identity-only baseline above — do not skip it.
- Construction-determinism risk if templates are used instead of real corpus sentences. Prefer real sentences from whatever corpus v4/v5 already draw from; if none exist mentioning both concepts, treat synthetic templates as diagnostic-only, not load-bearing for a HARD-PASS claim.
- The learned-vs-fixed-binding generalization question (Steinberg & Sommer) is unresolved in the literature — a v6 negative could stem from that open question, not from the overall self-teach direction being wrong. Worth an ablation (learned bind-target vs. fixed random role vectors) inside v6 rather than treating one failure as closure.

## Citations (verified count: 12 high-confidence / 6 medium-confidence / 3 low-confidence, not independently fetched beyond search snippets)

High-confidence (verified via direct fetch or high-agreement search snippets):
1. Frankland, S.M. & Greene, J.D. (2015). *PNAS* — lmSTC encoding of agent/patient identity.
2. Friederici, A.D. (2011/2012). *Physiological Reviews* / PNAS 2008 — dorsal/ventral language streams.
3. Rabovsky, M., Hansen, S.S., McClelland, J.L. (2018). *Nature Human Behaviour* — Sentence Gestalt, N400 as prediction error.
4. St. John, M.F. & McClelland, J.L. (1990). *Artificial Intelligence* — SRN learns thematic roles from feedback.
5. Elman, J.L. (1991). *Machine Learning* — distributed representations of grammatical structure.
6. Smolensky, P. (1990). *Artificial Intelligence* — Tensor Product Representations.
7. Plate, T. (1995). *IEEE Trans. Neural Networks* — Holographic Reduced Representations.
8. Gleitman, L. (1990). *Language Acquisition* — syntactic bootstrapping.
9. Mintz, M. et al. (2009). ACL — distant supervision for relation extraction.
10. Lin, Y. et al. (2016). ACL — PCNN + selective attention (PCNN+ATT).
11. Levy, O., Seo, M., Choi, E., Zettlemoyer, L. (2017). CoNLL — zero-shot RE via reading comprehension.
12. Peng, H. et al. (2020). EMNLP — entity bias / context-vs-names in neural RE (the load-bearing leakage diagnostic).

Medium-confidence (found, not independently fetched):
13. Hummel, J.E. et al. (2004). AAAI Fall Symposium — binding-by-synchrony.
14. Riedel, Yao, McCallum (2010). ECML/PKDD — multi-instance learning, NYT-10.
15. Han, X. et al. (2018). EMNLP — FewRel; Gao et al. (2019) FewRel 2.0.
16. Steinberg, K. & Sommer, F. (2019). arXiv:1902.09006 — learned role-filler binding, memory-augmented net.
17. Huang, Q., Smolensky, P., He, X., Deng, L., Wu, D. (2018). NAACL — Tensor Product Generation Networks.
18. Ganesan, A. et al. (2021). NeurIPS, arXiv:2109.02157 — learnable/stable HRR bind-unbind.

Low-confidence (title/venue uncertain, needs direct verification before load-bearing use):
19. arXiv:2501.01349 (2025) — DREB debiased RE benchmark, author names unverified.
20. "Attention as Binding" arXiv:2512.14709 — content match unverified, flagged by sub-agent as low-confidence.
21. Xu et al. (2018) / Nguyen et al. (2020) — ConceptNet LocatedNear pattern-extraction, narrow single-relation scope only.

## Calibration

Lit-scan calibration penalty applied per standing discipline. Raw synthesis estimate that a v6 learned-binding-head, self-taught from the foundation, would show genuine held-out comprehension signal (beating the B0/B1 nulls by a wide, held-out-to-new-concept margin): ~0.55. Deflated 0.20 for uncharted-regime combination (no direct precedent for KG-distant-supervision + native-VSA-binding + coherent-vs-scrambled contrastive, per Thread 3). Novel-synthesis cap of 0.50 does not additionally bind since the deflated estimate is already below it.

**P_deflated = 0.35**

Next-drill candidate if this direction proceeds and needs deeper mechanism: Steinberg & Sommer (2019) full-paper read for the learned-vs-fixed-binding generalization question (Thread 3, risk #3) — directly load-bearing for whether v6's learned bind-target should be ablated against fixed random role vectors.
