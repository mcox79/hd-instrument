# Research drill: POS Brown -> PTB cross-domain transfer (3rd-appearance candidate, capability-class tail-shape rule)

Date: 2026-06-12
Drill type: 1x scoped literature drill (4-6 generic queries; lit-scan calibration penalty applied)
Topic: Pre-register transfer-shape prediction for 3rd-appearance test of meta::RULE_cross_domain_transfer_tail_shape_is_capability_class_dependent_open_vocab_persists_closed_feature_converges

## Drill spec

Cross-domain rule has 2 prior appearances:
- Sentiment (closed-feature single-label classification): CONVERGING tail. Substrate lift positive low-data, neutral at high data.
- NER (open-vocab sequence-labeling): NON-CONVERGING TAIL. Lift persists through high data fractions.

3rd-appearance candidate: POS tagging Brown -> PTB.

Question: which side does POS fall on? POS is sequence-labeling (NER-like structurally) but uses universal tagset (closed in label-space, sentiment-like).

## Findings (compact)

F1. OOV rate is the dominant cross-domain failure mode for POS taggers.
- WSJ in-domain OOV ~2.3%
- Cross-domain OOV jumps to 6.8-11% (clinical, Twitter, biomedical)
- UWT (unknown-word-tag) rate jumps 0.61% (WSJ) -> 2.91-3.47% (answers, emails)
[Source: clinical-narratives POS adaptation; Cross-Domain Evaluation WSJ -> Fandom Wiki, arXiv:2304.13989]

F2. Unknown-token accuracy degrades sharply under domain shift.
- Stanford tagger unknown-token accuracy: 90.37% in-domain -> 78.37% cross-domain (-12pp)
- Bilty tagger unknown-token accuracy: 87.84% -> 80.41% (-7pp)
- Known-token accuracy is "almost as good as in-domain" cross-domain
[Source: Plank et al. domain-adaptation noisy-text studies; aNT NaCTeM POS adaptation page]

F3. Transfer-benefit decay shape: cross-domain transfer helps MOST at low target data, DIMINISHES with more target data, but does NOT fully vanish.
- PTB -> Genia: 83% zero-target-labels, 92% with only 0.001 labels (huge low-data lift)
- "Effects of improved transfer diminish when a substantial number of target domain examples are acquired for fine-tuning"
- Diminish, not vanish: the persistent OOV gap (F2) keeps a residual non-zero tail
[Source: Chen et al. 2019, Transfer Learning for Sequence Labeling Using Source Model and Target Data; Yang et al. CMU/ICLR 2017]

F4. Universal POS tagset (Petrov et al. 2012) closes the LABEL-space but does NOT close the INPUT-vocabulary, which is the driver of the cross-domain gap. Coarse tags help cross-lingual / cross-domain comparison but the unknown-word problem remains structural.
[Source: Petrov, Das, McDonald 2012 universal tagset arXiv:1104.2086]

F5. Suffix / orthographic / cluster features (substrate-aux) partially close the OOV gap. Per substrate-aux-features-shrink-with-data memory: at scale lexical features subsume the aux lift. But cross-domain low-data is exactly the regime where aux features dominate.

F6. Structured-perceptron POS taggers with SCL adaptation reported small absolute lifts (87.9 -> 88.9, +1pp) on Brown / biomedical targets. Modest in absolute terms because in-domain ceiling is already ~97%; the RATIO lift at low target data is the load-bearing measurement.

## Synthesis: predicted transfer shape for POS Brown -> PTB

POS is HYBRID:
- Label space: closed (~17 universal tags or ~45 PTB tags). Sentiment-like.
- Input space: open vocabulary. NER-like.
- Decision boundary: structurally a sequence-labeling problem (transitions + emissions), NER-like.

Predicted shape: PARTIAL CONVERGENCE.
- Low-data regime (5-10% target): substrate-classical (structured perceptron + Viterbi + tag-bigram + suffix/cluster aux) shows LARGE lift vs target-only baseline. Sentiment-like magnitude but NER-like mechanism (OOV-bridging).
- High-data regime (100% target): substrate lift COMPRESSES toward but does NOT collapse to zero. Residual tail driven by F2 unknown-token accuracy gap (12pp absolute on Stanford-class taggers) which target-only training cannot eliminate because OOV words remain OOV in the held-out test set.
- Expected tail magnitude: SMALLER than NER's non-converging tail (because closed label space reduces structured-prediction ambiguity that helps known-tokens too), LARGER than sentiment's near-zero convergence (because OOV is real and persistent).

Mechanism statement: substrate-classical POS does well cross-domain because (a) structured-perceptron transitions are tagset-coupled not vocabulary-coupled (universal across domains); (b) suffix/orthographic features generalize OOV->tag at zero corpus cost; (c) Viterbi enforces tag-bigram coherence that masks per-token uncertainty.

Per literature-is-not-oracle: literature predicts SHRINKAGE not VANISHING. Substrate prediction REFINES literature with explicit non-zero asymptote driven by OOV-tag mapping primitive.

## Confirming-vs-falsifying test framing

Pre-registered candidate: Brown corpus (source) -> PTB-WSJ (target) at substrate-classical baseline.
Metric: substrate vs target-only-baseline accuracy LIFT, measured at training fractions {5%, 25%, 50%, 100%} of target.
Tail metric: lift_5pct / lift_100pct ratio (the "tail-shape signature").
- NER pattern (prior appearance #2): tail ratio approximately 1.0-1.5 (non-converging; lift persists).
- Sentiment pattern (prior appearance #1): tail ratio approximately 5-20+ (low-data dominates; high-data lift collapses near zero).
- Partial-convergence prediction for POS: tail ratio approximately 2-4.

What confirms the rule:
- POS in 2-4 range (PARTIAL CONVERGENCE) -> rule CONFIRMED with refinement: tail-shape is a CONTINUUM indexed by input-vocabulary openness, not a binary toggle.
- POS in 5-20 range (sentiment-like) -> rule CONFIRMED in its binary form: label-space closure dominates input-vocab openness for tail shape.
- POS in 1.0-1.5 range (NER-like) -> rule CONFIRMED with sharpening: sequence-labeling structure dominates, label-space closure is irrelevant for tail shape.
- POS in 0.5-1.0 range (INVERTED, lift grows with data) -> rule FALSIFIED. Substrate becomes a feature-engineering crutch the LLM-side calibrated baseline subsumes at scale.

## Pre-registered HARD-PASS / MIDDLE / HARD-FAIL bands

These are bands on the 3rd-appearance cell, where lift = substrate_classical_acc - target_only_baseline_acc, measured on PTB-WSJ test split.

HARD-PASS (capability-class tail-shape rule confirmed at 3rd appearance):
- lift @ 5% target train: >= +0.030 absolute
- lift @ 100% target train: >= +0.005 absolute (non-trivially > 0; tail does NOT vanish)
- tail ratio (lift_5 / lift_100): in [1.5, 6.0] (partial-convergence band consistent with hybrid capability-class)
- substrate OOV-token accuracy at 100% target train: >= +0.04 absolute over target-only baseline on cross-domain-flavored OOV subset

MIDDLE-BAND (rule needs 4th appearance to decide):
- lift @ 5%: in [+0.010, +0.030)
- lift @ 100%: in [+0.001, +0.005)
- tail ratio: in [6.0, 12.0] (drifting toward sentiment convergence) OR [1.0, 1.5] (drifting toward NER non-convergence)
- Outcome: log 3rd appearance as PARTIAL; do not yet promote rule to "confirmed across 3 capability classes"

HARD-FAIL (rule falsified at 3rd appearance):
- lift @ 5%: < +0.010 absolute (low-data lift fails to materialize for sequence labeling open-vocab case)
- OR lift @ 100%: < 0 (substrate HURTS at high data, indicating spurious low-data win)
- OR tail ratio: < 1.0 (lift GROWS with data, contradicting both prior appearances)
- Action on HARD-FAIL: file capability-class-tail-shape rule as REFUTED; rewrite rule to scope to (sentiment OR NER) without generalization.

## Cross-thread synthesis

- Substrate POS standalone is already Tier-A (0.957 in-domain per substrate_small_llm_per_token_structural_unscoreable memory). Cross-domain is the unmeasured axis.
- Substrate-aux-features-shrink-with-data memory predicts: aux features dominate low-data, lexical features dominate high-data. This is the SAME shape as the cross-domain rule's tail prediction. The two memories are TWO VIEWS of the same OOV-feature-coverage phenomenon.
- Substrate-classical wins on POS because of structured-perceptron + Viterbi + suffix cascade. All three are domain-robust by design.
- 3rd-appearance result (whatever shape) will refine RULE_cross_domain_transfer_tail_shape... from "capability-class binary" to "input-vocab-openness continuum" if POS lands in the partial band.

## Substrate-product implications

- If HARD-PASS: substrate-product gains a 3-class generalization claim ("substrate's cross-domain low-data lift extends across sentiment + NER + POS, with tail shape predictable from capability class"). This is a marketable structural-cognition claim — "substrate is robust across domain shift in 3 distinct NLP capability classes, with predictable shape".
- If MIDDLE: substrate-product claim narrows to "2.5 classes" — still useful, but the universal-claim is not yet earned.
- If HARD-FAIL: substrate-product cross-domain claim stays scoped to 2 capability classes (sentiment + NER). No false generalization shipped.
- Either way: this drill produces a CALIBRATED pre-registered band against which Exp-Dev measures honestly. This is structural-cognition-meets-empirical-rigor positioning.

## Scope: MODERATE

- STRONG: F1, F2, F3 are well-cited; OOV / unknown-token degradation in POS is textbook.
- MODERATE: F4 universal-tagset effect on tail shape specifically is inferred not directly measured in lit.
- SPECULATIVE: numeric band edges (tail-ratio 1.5-6.0 HARD-PASS) are reasoned from F2/F3 magnitudes, not directly extracted from a single source. Calibration penalty applied: deflated from initial 0.65 to P_deflated = 0.48 that partial-convergence band is the correct prediction.

## Citations (verified count: 8 directly relevant)

1. Brants 2000, TnT statistical POS tagger (arXiv:cs/0003055) — learning curve methodology.
2. Petrov, Das, McDonald 2012, A Universal Part-of-Speech Tagset (arXiv:1104.2086) — closed-tagset framework.
3. Chen et al. 2019, Transfer Learning for Sequence Labeling Using Source Model and Target Data (arXiv:1902.05309) — low-data transfer diminishing returns.
4. Yang, Salakhutdinov, Cohen 2017, Transfer Learning for Sequence Tagging with Hierarchical Recurrent Networks (ICLR) — cross-domain sequence-tagging gains.
5. Plank et al. 2019, Domain adaptation for POS tagging of noisy user-generated text (arXiv:1905.08920) — Bilty/Stanford unknown-token degradation numbers.
6. Cross-Domain Evaluation of POS Taggers: WSJ to Fandom Wiki (arXiv:2304.13989) — OOV rate 2.3% -> 6.8-11%.
7. Ferraro et al., POS adaptation on clinical narratives, PMC3756264 — SCL +1pp baseline numbers.
8. aNT NaCTeM domain adaptation of POS taggers — averaged-perceptron cross-domain scaling note.

P_deflated for partial-convergence prediction: 0.48 (capped per novel-synthesis ceiling 0.50; deflated from raw 0.65).

Next-drill candidate field: nonequilibrium-stat-mech adjacency to thermodynamics (Tier-1b scope-expansion; Jarzynski / NESS framing for retention dynamics across cap rows).
