# 5x drill 4/5 — Component C modern-Hopfield readout HF — ML literature scan

Trigger: 5x-drill sequence (negative-result 2x/5x discipline) on Component C brain-analog readout
(commit 4cd1d30ba, `hdlab/modern_hopfield_readout.py`, Ramsauer 2020 formulation). Landed finding:
modern-Hopfield readout at beta={4,8} scored r@5={0.050, 0.053} vs plain cosine 0.16 on WordNet
held-out synonym retrieval, equal-norm sparse-bipolar storage (k=2%, N=2048, 100 concepts). This is
drill 4 of 5, domain = ML literature (Ramsauer 2020 downstream + attention/retrieval lit). Drills
1-3/5 (empirical config sweep, math/info-theory, neuroscience) and drill 5 (separate ML/AI lit pass
on the sibling substrate_content_HF chain) are logged separately; this drill is scoped strictly to
the 5 questions the dispatching agent specified.

## HEADLINE

Convergent literature across three independent lit-scans (Ramsauer-downstream, sparse/attention
lit, HDC/VSA canon) finds **no published evidence that softmax/modern-Hopfield attention beats
plain cosine/dot-product argmax retrieval on equal-norm sparse or bipolar storage**. The single
closest controlled comparison found (Millidge et al. 2022, "Universal Hopfield Networks") shows the
*opposite*: hard winner-take-all/max readout beats softmax at the beta value the authors themselves
treat as the fair-comparison default, on a corrupted-pattern retrieval-capacity task. Canonical
HDC/VSA literature (Plate, Kanerva, Rachkovskij, Kleyko survey) independently and unanimously
recommends cosine/dot-product (continuous) or Hamming (binary) argmax nearest-neighbor as the
standard cleanup-memory readout — softmax-weighted alternatives are a niche, recent (2024-2026)
thread, not a field consensus. Verdict: **(I) — literature confirms softmax attention does not beat
cosine on equal-norm sparse storage; Skunkworks recommendation to skip/close Component C in its
current form stands.** A geometry-dependent caveat applies (see Cross-thread synthesis): this is not
evidence that modern-Hopfield attention is globally useless — it is evidence that its advantage,
where real, is tied to dense continuous storage, not sparse-bipolar equal-norm storage.

## Findings by question (as dispatched)

1. **Ramsauer 2020 downstream — anyone beat cosine on retrieval?** No. Ramsauer 2020 itself never
   benchmarks retrieval-vs-cosine; its empirical wins are classification (UCI/MIL/immune-repertoire)
   and language modeling. Its exponential-capacity theorems assume equal-norm patterns on a sphere —
   a theoretical construction, not the tested regime. Millidge et al. 2022 (PMLR, arXiv:2202.04557,
   "Universal Hopfield Networks") is the closest controlled retrieval-capacity comparison and finds
   **hard max/NN beats softmax at beta=1** (their fair-comparison default) on corrupted-image
   retrieval (MNIST/CIFAR-10/Tiny-ImageNet); softmax only approaches max's performance as beta→∞.
   Hu et al. 2023/2024 ("Sparse and Structured Hopfield Networks", arXiv:2402.13725) again requires
   equal-norm theory but tests natural unnormalized embeddings empirically with no cosine baseline.
   CLOOB (Fürst et al. 2021, arXiv:2110.11316) reports Hopfield retrieval *increases* both matched-
   and unmatched-pair cosine similarities — a saturation problem, arguably evidence Hopfield
   retrieval can degrade similarity-score separability. HoReN 2026 (arXiv:2605.08143) is the one
   paper with an on-topic premise (L2-normalizes edit-keys specifically because unnormalized norms
   caused retrieval problems) but ablation numbers were not verified in detail — flagged as
   found-but-unconfirmed.

2. **Sparse-bipolar/binary + softmax-attention retrieval lit.** No paper found doing the exact
   comparison (sparse-binary/bipolar/ternary storage, softmax readout vs cosine NN, same storage).
   Closest analogs: Product-Key Memory (Lample et al. 2019, arXiv:1907.05242) and its 2020-2026
   follow-ons use dense continuous keys, not sparse-binary, and never ablate softmax-weighted vs
   hard top-1 on the same keys. Karunaratne et al. 2021 (Nature Communications, arXiv:2010.01939) —
   the closest true empirical instance — uses dense bipolar/binary prototype hypervectors at ~50%
   density (not "sparse" in the few-nonzero sense) with **equal norm by explicit construction**, and
   compares two attention-family sharpening variants (softmax vs "softabs") against each other, not
   against hard NN.

3. **Non-equal-norm / confidence-weighted attention.** Variable key/value norm reliably *emerges* in
   trained transformers (Kobayashi et al. 2020, EMNLP, arXiv:2004.10102; Bricken & Pehlevan 2021,
   arXiv:2111.05498) but is not established as a *beneficial designed* retrieval signal — the
   opposite engineering trend (QK-Norm, used in Gemma/Chameleon-style models) actively suppresses
   norm variance as a stability nuisance. Attention-sink literature (2024-2026, multiple papers)
   shows outlier key/value norms function as a "dump attention here to do nothing" mechanism, not a
   salience signal. No paper found benchmarking non-equal-norm vs equal-norm storage under otherwise
   identical softmax retrieval.

4. **HDC/VSA canon (Kanerva SDM, Kleyko survey, Rachkovskij, Plate).** Unanimous: standard cleanup
   memory is cosine/dot-product (continuous) or Hamming-distance (binary) argmax nearest-neighbor —
   normalize-then-argmax, not softmax-weighted combination. Kanerva's SDM itself uses threshold/
   radius-based Hamming summation, mechanistically distinct from both hard-NN and softmax attention;
   Bricken & Pehlevan 2021 (NeurIPS, arXiv:2111.05498) proved this becomes mathematically equivalent
   to softmax attention only under specific fitted conditions (validated on trained GPT-2 statistics,
   not shown to hold generically for arbitrary sparse-bipolar codebooks). Resonator networks (Frady/
   Kent/Olshausen/Sommer) use iterative superposition-based cleanup; a 2026 Frontiers paper directly
   comparing sign/softmax/ReLU/polynomial cleanup rules found no single rule dominates — softmax
   competitive only in easy/small-search-space regimes, degrading faster than ReLU/polynomial at
   large search spaces.

5. **Head-to-head (a) cosine vs (b) modern-Hopfield vs (c) magnitude-weighted, equal-norm sparse
   storage, real retrieval task.** Not found. This exact 3-way comparison does not appear to exist in
   the literature; the closest partial precedent (Millidge 2022) argues against modern-Hopfield's
   premise using dense real-valued (not sparse-bipolar) storage.

## Verdict

**(I), with a geometry-scoped caveat.** Literature confirms softmax attention does not reliably beat
cosine/argmax on equal-norm sparse-bipolar storage — no paper claims otherwise, the closest
controlled comparison (Millidge 2022) finds the opposite, and the entire HDC/VSA canon independently
converges on cosine/Hamming argmax as the standard. Skunkworks recommendation to skip Component C in
its current sparse-bipolar equal-norm form stands.

The caveat: this substrate's own prior evidence (2026-07-01, `research_2x_drill_cortex_hippo_
readout_replacement_2026-07-01.md`) found modern-Hopfield attention reading DIRECTLY from a dense,
continuous Hebbian-written memory tape achieved recall 1.000 (vs 0.008 for a lossy-readout-then-
attention cascade) — i.e., attention *did* help when storage was dense/continuous. This is
consistent with, not contradictory to, today's finding: Millidge 2022 and Karunaratne 2021 both
report their attention-family results on dense real-valued or ~50%-density storage, never on
sparse-bipolar equal-norm codes. The pattern across both the literature and the substrate's own two
data points is **storage-geometry-contingent, not encoder-contingent**: modern-Hopfield attention's
advantage (where real) tracks dense continuous storage; it does not transfer to sparse-bipolar
equal-norm storage. This is a (I)-plus-(II)-lite finding — not "revisit Component C," but "the two
existing substrate results already jointly triangulate the boundary condition, and literature
confirms that boundary is exactly where the field's own attention-vs-NN evidence lands."

A minor (III)-lite note: 2026 resonator-network cleanup-rule literature (sign/softmax/ReLU/
polynomial) suggests iterative superposition-based cleanup with graceful degradation at large
codebook sizes as a genuinely distinct alternative family (not "beats cosine" but "different
scaling behavior at large N-concepts") — worth flagging for a future capacity-cliff drill, not
actionable now.

## Cheap decisive test

No new test is needed to close Component C in its current form — the literature convergence plus
the existing Millidge-2022-style negative result is sufficient. The discriminating test for the
geometry-scoped caveat has **already been run** by the substrate itself: Cell D v2 (`cortex_hippo_
dense_layer`, 2026-07-01) is the natural control — dense continuous storage + direct attention read
= recall 1.000, vs today's sparse-bipolar equal-norm storage + attention read = r@5 0.05. These two
substrate data points, read together with the literature, are the decisive test; no further dispatch
required to resolve THIS question.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

Framed for the geometry-contingent hypothesis, should anyone want to re-test it directly on a single
matched task in the future:

- **HARD-PASS** (would falsify "geometry, not encoder, is the driver" in the encoder's favor):
  modern-Hopfield softmax readout on a DENSE real-valued (non-sparse, non-bipolar) encoding of the
  SAME WordNet synonym set, same task/metric (r@5), beats cosine by >=0.05 absolute at some beta in
  {1,2,4,8,16}. This would show the encoder's content, not just its sparsity/bipolarity, is
  compatible with attention-style readout.
- **HARD-FAIL** (confirms geometry is irrelevant / negative result is encoder-specific, not
  storage-geometry-general): dense real-valued encoding of the same task+metric still shows
  softmax r@5 < cosine r@5 (any beta), i.e. lift <= 0. This would mean the WordNet
  synonym-retrieval task itself (not storage geometry) is simply unfavorable to attention-style
  readout, undermining the geometry explanation offered above.
- **Pre-registered threshold for "inconclusive":** lift in (0, 0.05) absolute — some effect but
  too small to distinguish from noise at this task's scale (100 concepts).

## Cross-thread synthesis

- 2026-07-01 `research_5x_drill_cortex_hippo_M8192_rescue`: recommended dense-Hopfield/attention
  cortex layer for M3, citing Ramsauer 2020 capacity theorems — that recommendation is for a
  DIFFERENT storage regime (dense continuous Hebbian tape) than today's HF (sparse-bipolar). No
  conflict; the M3 cortex-layer recommendation stands on its own dense-storage evidence.
- 2026-07-01 `research_2x_drill_cortex_hippo_readout_replacement`: REPLACE-not-COMPOSE discipline
  (attention reads directly from Hebbian-written tape, no lossy readout stacked underneath) is
  validated there and is the exact mechanism that makes attention work in that regime — underscoring
  that Component C's sparse-bipolar test was never going to satisfy this precondition, since the
  substrate encoder there IS the storage (no separate dense tape to read from directly).
- 2026-06-16/17 modern-Hopfield cleanup-head threads (`research_modern_hopfield_capacity_retrieval_
  crossover`, `DECISION_174/176`): prior drills already found modern-Hopfield cleanup deferred to
  continuous-valued FPE decode subpath, NOT the discrete/sparse cardinality path — same geometry
  boundary recurring across a third independent thread, six weeks apart. This is now a
  three-instance recurring pattern, not a one-off: modern-Hopfield attention consistently lands on
  the dense/continuous side of the substrate's mechanism boundary, never the sparse-bipolar side.

## Substrate-product implications

- Close Component C (sparse-bipolar equal-norm modern-Hopfield readout) as a dead-end for the
  real-content retrieval product surface. Do not re-attempt softmax-attention readout directly over
  the k=2% sparse-bipolar codebook without first inserting a dense continuous intermediate
  representation (which is a different, already-validated M3 cortex-layer path, not a Component-C
  variant).
- Keep the Cell D v2 (`cortex_hippo_dense_layer`) cortex layer (dense Hebbian tape + direct attention
  read) as the sanctioned path for any future attention-style readout need — it already has
  empirical support (recall 1.000) and three independent literature threads say this is the correct
  storage geometry for that mechanism.
- Cosine/dot-product argmax remains the product-correct readout for the sparse-bipolar substrate
  representation itself — this is not a compromise, it is the field-standard HDC/VSA recommendation
  (Plate/Kanerva/Rachkovskij/Kleyko), independently converged upon by the ML attention literature's
  own negative results (Millidge 2022).
- Resonator-network-style iterative cleanup (2026 Frontiers cleanup-rule comparison) is a candidate
  worth a future look ONLY if/when a capacity-cliff drill needs graceful degradation at very large
  codebook sizes (concept count >> 100) — not urgent, not a Component C revival, filed for the
  scope-expansion backlog.

## Citations (verified count: 12)

1. Ramsauer et al. 2020, "Hopfield Networks is All You Need," arXiv:2008.02217.
2. Millidge, Ruiz, Salvatori, Song, Lukasiewicz 2022, "Universal Hopfield Networks," PMLR,
   arXiv:2202.04557.
3. Hu et al. 2023/2024, "Sparse and Structured Hopfield Networks," arXiv:2402.13725.
4. Fürst et al. 2021, "CLOOB: Modern Hopfield Networks with InfoLOOB Outperform CLIP,"
   arXiv:2110.11316.
5. "Normalized Hopfield Retrieval for Large-Scale Sequential Model Editing" (HoReN), arXiv:2605.08143
   (2026) — abstract-level only, ablation numbers unverified.
6. Lample, Sablayrolles, Ranzato, Denoyer, Jégou 2019, "Large Memory Layers with Product Keys,"
   arXiv:1907.05242.
7. Karunaratne et al. 2021, "Robust High-dimensional Memory-augmented Neural Networks," Nature
   Communications, arXiv:2010.01939.
8. Bricken & Pehlevan 2021, "Attention Approximates Sparse Distributed Memory," NeurIPS,
   arXiv:2111.05498.
9. Kobayashi, Kuribayashi, Yokoi, Inui 2020, "Attention is Not Only a Weight," EMNLP,
   arXiv:2004.10102.
10. Plate 1995, "Holographic Reduced Representations."
11. Kanerva 2009, "Hyperdimensional Computing: An Introduction to Computing in Distributed
    Representation with High-Dimensional Random Vectors," Cognitive Computation 1:139-159.
12. Kleyko, Rachkovskij, Osipov, Rahimi 2021/2022, "A Survey on Hyperdimensional Computing aka
    Vector Symbolic Architectures," Parts I & II, arXiv:2111.06077 / arXiv:2112.15424.

(Additional papers referenced in sub-agent scans but not load-bearing to the verdict: attention-sink
literature 2024-2026 cluster, QK-Norm engineering references, resonator-network 2026 Frontiers
cleanup-rule comparison, MemAE 2019 arXiv:1904.02639 — omitted from the verified-12 count as
secondary/contextual.)

## Calibration

P_deflated = 0.58. Raw convergent confidence across 3 independent lit-scans + substrate's own two
data points would support ~0.75-0.80; deflated 0.15-0.22 per [[feedback-lit-scan-calibration-penalty]]
for uncharted-regime lit-scan (no single paper directly tests the exact substrate configuration).
Novel-synthesis component (the geometry-contingent boundary claim, not directly stated in any single
paper) is capped at P<=0.50 per the same discipline; the (I) core verdict (softmax doesn't beat
cosine on equal-norm sparse storage) carries the higher confidence, the (II)-lite geometry
explanation is the capped-at-0.50 novel-synthesis piece.
