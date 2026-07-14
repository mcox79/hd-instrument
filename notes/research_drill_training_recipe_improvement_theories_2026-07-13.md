# Research drill: training/recipe theories to improve inductive KG relation-inference (architecture held fixed)

Scope: our additive inductive map (`hdlab/additive_map.py` / `AdditiveKGMap`, VET-confirmed FULL, held-out-entity
MRR 0.1282, HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE) uses `experiments/_kge_anchor1_fit.py::fit_kge_anchor1` as its
default coord source. Ground-truth check before drilling (per [[feedback-no-hallucinated-numbers]]): the fit
ALREADY implements self-adversarial cross-entropy loss (Sun et al. 2019), N3 regularization (Lacroix et al.
2018), reciprocal-relation augmentation, and minibatch Adam SGD. What is genuinely untuned: the specific
hyperparameter VALUES (lr=0.05, gamma=9.0, n_neg=64, adv_temp=1.0, n3_lambda=5e-4, batch=8192, epochs=500,
k=24 — all hand-picked defaults, never swept), the INITIALIZATION (`torch.randn(N,k)*0.1`, plain Gaussian,
no structural warm-start), the absence of any LR schedule, and the absence of checkpoint-averaging /
snapshot-ensembling (the existing `FitCheckpoint` is durability-only — it overwrites, retains exactly one
snapshot, not multiple). This drill does NOT re-cover architecture/capacity or grounding (covered separately
same day: `research_drillA_*_capacity_structure_2026-07-13.md`, `research_drillB_neuro_grounding_mechanism_2026-07-13.md`).

4 parallel Sonnet lit-scan sub-agents dispatched (generic public ML terms only, no substrate framing):
(A) hyperparameter-tuning lift quantification, (B) negative-sampling strategies beyond self-adversarial,
(C) curriculum / ensembling / initialization + brain-grounding, (D) loss-function / label-smoothing /
InfoNCE. All four returned quantified, citation-backed findings (no vague claims accepted).

## HEADLINE

Across 4 independent lit-scan angles, the largest, cheapest, most-composable, single-swap lever for our
additive map is **structural/spectral warm-start initialization** of the entity coordinate table X (replacing
`torch.randn(N,k)*0.1` with a cheap Laplacian-eigenmap embedding of the training graph) — the one directly
relevant paper (informed/schema-warm-started init for continual TransH) reports +9-46% task performance and
2.2-2.7x faster convergence, framed in the literature as a "free lunch" because it costs one cheap eigen-
decomposition, doesn't touch the scoring function, doesn't conflict with the self-adversarial+N3+reciprocal
recipe already in place, and directly reuses spectral-factorization machinery we ALREADY scoped in
`research_drillA_wildcard_capacity_structure_2026-07-13.md` (Trigger-C adjacency-cascade: that drill's Laplacian
eigenmap proposal for the codec problem is the SAME primitive this drill needs for the init problem).
Second-highest-value lever (snapshot-ensembling / SWA-style checkpoint averaging, ~1x compute, +9-27% Hits@10
in the one directly relevant paper) is real but currently BLOCKED by our checkpoint module being
durability-only (retains 1 snapshot, not N) — a structural prerequisite, not a training-recipe change, so it
is ranked #2 not #1 for "apply first." Full hyperparameter re-tuning (Ruffinelli et al. ICLR 2020: +8.7 to
+10.1 MRR points from full retuning, architecture-reversing) is real and well-precedented but is a SWEEP
(many runs), not a single cheap swap, so it's the natural Phase-2 follow-on once init is tested.

Deflation applied throughout per [[feedback-lit-scan-calibration-penalty]]: -0.15 to -0.25 off every literature
number below, because (a) ALL found numbers are TRANSDUCTIVE-benchmark (FB15k-237/WN18RR/YAGO3-10) or
continual-learning settings, NOT our inductive held-out-entity-compose task, and (b) our compose op
(`build_anchor_compose_codes`, a degree-invariant MEAN of per-edge tail estimates) sits downstream of the
fitted X,D and could partially wash out whatever structural signal a smarter init encodes into X — this is
exactly the mechanism the cheap test below is designed to catch or refute.

## Ranked levers (measured lift x glass-box-fit x cheap-testability on our additive map)

| Rank | Lever | Measured lift (source) | Composability | Cost to test on our map | Deflated verdict |
|---|---|---|---|---|---|
| 1 | **Structural/spectral init warm-start of X** | +9-46% task perf, 2.2-2.7x faster convergence (informed TransH continual-learning init study) | Full — no scoring-fn change, no conflict w/ self-adv+N3+reciprocal | 1 clean re-fit, reuse existing Laplacian-eigenmap primitive from wildcard drill | P=0.40 (deflated from ~0.55-0.65); expect **+3 to +15% relative MRR** (0.1282 -> ~0.132-0.147), NOT the full 46% |
| 2 | Snapshot-ensembling / SWA checkpoint averaging | Hits@10 +9.4% (TransE), +26.9% (RotatE), ~1x compute vs 5-7x for independent-seed ensembles (SnapE, 2024) | Full in principle, BUT blocked — our `FitCheckpoint` overwrites (1 snapshot retained, not N) | Needs a small infra change first (retain-N-checkpoints mode) before it's a recipe-only lever | P=0.30; real but gated on a prerequisite, not "apply first" |
| 3 | Full hyperparameter re-tuning sweep (lr, gamma, n3_lambda, batch, epochs, k jointly) | +8.7 to +10.1 MRR points, architecture-reversing (Ruffinelli et al. ICLR 2020) | Full — same recipe family we already use (CE self-adversarial is their dominant lever and we already have it) | Moderate — needs a small grid/random search (10-20 runs), not a single swap | P=0.35; well-precedented but priced as Phase-2, sequenced AFTER init test |
| 4 | DURA regularizer (replace N3) | +0.5-1.7 MRR pts for CP/ComplEx (our scoring family); up to +10 pts only for RESCAL where N3 doesn't apply | Full — drop-in swap of the regularization term only | Trivial (change one loss term) | P=0.30; low-modest expected lift for our specific scoring family, cheap enough to bundle into the Phase-2 sweep |
| 5 | Label smoothing (eps~0.1 on gold target) | ~0.008 Hits@10 one direction; "significant" but unquantified other direction (ConvE vs HypER disagree) | Full — orthogonal axis, layers on top of existing recipe at ~zero cost | Trivial | P=0.20; free to try, don't expect much |
| 6 | Structure-aware negative sampling (SANS: sample negatives from k-hop neighborhood) | +2-6 MRR points, additive on top of self-adversarial | Full — self-adversarial softmax still applies on top of the restricted pool | Moderate (need k-hop neighborhood sampler) | P=0.30; solid but not "first" — implementation cost above init/DURA/label-smoothing |
| 7 | Curriculum / easy-to-hard edge ordering | ~1-4% MRR on static KGE (the one 25% number is temporal-KG-specific, does not transfer) | Full | Cheap (reorder training edges by degree/confidence) | P=0.20; modest, deflate the one large number as non-transferable |
| 8 | n_neg increase beyond current 64 | "Negligible impact" beyond ~8-16 negatives (2025 PyKEEN-extension sweep) | N/A | N/A | We are ALREADY past the saturation point at n_neg=64 — this is a CLOSED lever, not worth touching |
| 9 | NSCaching (cache-based hard negatives) | Neutral-to-positive on dense benchmarks vs self-adversarial; big win only on sparse/large ontology-scale graphs (+150% MRR in one setting) | Additive in principle (untested as hybrid) | Moderate (cache data structure + refresh schedule) | P=0.25; flag as secondary given our graph is moderately sparse (~485k edges / ~25.7k entities, avg degree ~19) |
| 10 | Independent multi-seed ensembling | Real gains, but 5-7x compute, inconsistent across models | N/A | High | RULED OUT — snapshot-ensembling (rank 2) strictly dominates on a cost-adjusted basis |
| 11 | GAN-based adversarial negative samplers (KBGAN/IGAN) | Underperforms self-adversarial by ~0.02 MRR while costing more (adversarial training instability) | Replace, not additive | N/A | RULED OUT — proven worse than what we already have |
| 12 | InfoNCE/contrastive full redesign (SimKGC-style) | Largest raw numbers anywhere (+19-22% MRR) | NOT composable — requires a PLM/text-encoder architecture change, confounds with scoring-function redesign | High (architecture change) | RULED OUT for a "recipe-only, architecture-fixed" drill — inspirational ceiling only, out of scope per the user's explicit "without changing the architecture" constraint |
| — | LR schedule (warmup/cosine/cyclical decay) | **Literature gap** — no paper isolates the schedule contribution for simple-scoring-function KGE | Full — orthogonal, trivial to add | Trivial | Unscored (no citable number); flag as an open, cheap, untested bet worth a side-channel A/B, not a ranked claim |

## Cheap decisive test (rank-1 lever: spectral init warm-start)

1. Compute a k=24-dim spectral embedding of the training-edge graph via the top-k eigenvectors of the
   normalized graph Laplacian (cheap CPU `eigsh`/Lanczos on the existing ~485k-edge / ~25.7k-entity graph —
   the SAME graph object already used for the wildcard-drill Laplacian-eigenmap proposal, no new data needed).
2. Rescale the spectral vectors to match the current init's norm statistics (so the comparison isolates
   STRUCTURE, not just a different scale), and use as `X_init` in place of `torch.randn(N,k)*0.1` in
   `fit_kge_anchor1` line 82. Leave D's init, loss, N3, reciprocal, self-adversarial weighting, lr, gamma,
   batch size, epochs, and seed BIT-IDENTICAL to the confirmed run that produced MRR=0.1282.
3. Re-run the SAME held-out-entity split through the SAME acceptance-gate pipeline
   (`experiments/exp_additive_map_acceptance_gate_v1.py`) at two checkpoints: (a) full epoch budget (500,
   asymptotic-performance test) and (b) a reduced budget (~100 epochs, 20% of full — convergence-speed test,
   since the literature's headline claim is FASTER convergence, not just a better asymptote).
4. Must-fail control (fairness discipline): a SCRAMBLED-spectral-init arm — same eigenvector magnitudes/norms,
   but randomly permuted assignment across entities (destroys structure, preserves scale statistics). If the
   scrambled arm gets the same lift as the correctly-assigned spectral arm, the lift is a scale/norm artifact,
   not real structural transfer — this isolates the mechanism per [[feedback-fairness-plus-weak-point-localization]].

## Falsifiable predictions

**HARD-PASS** (either condition, both arms measured against a second seed to bound noise):
- Full-epoch MRR >= 0.1282 x 1.05 (>=5% relative lift, deflated hard floor well below the literature's raw
  double-digit numbers), AND scrambled-init control does NOT match this lift (structure, not scale, is doing
  the work); OR
- Reduced-epoch (~100/500) MRR >= the confirmed full-epoch baseline of 0.1282 (i.e., convergence-speed win:
  reaches current asymptotic performance in <=20% of the training budget), with full-epoch MRR not regressing
  below 0.1282 x 0.97 (no asymptotic cost for the speed gain).

**HARD-FAIL:**
- Full-epoch MRR <= 0.1282 x 1.02 (within noise band across 2 seeds) AND reduced-epoch MRR shows no
  convergence-speed advantage over the current random-init arm at the same reduced budget. This would mean
  the degree-invariant MEAN compose op downstream of X,D washes out whatever structural signal the spectral
  init encodes — a genuine, informative negative (localizes the wall to the COMPOSE stage, not the FIT stage,
  which is itself a useful finding worth carrying into the compose-op design).
- If the scrambled-init control matches or beats the correctly-assigned spectral arm: the entire lever is a
  scale-normalization artifact, not structural transfer — report and do not pursue further scale-matched
  structural inits.

## Cross-thread synthesis

- **Adjacency-cascade (Trigger C) hit**: `research_drillA_wildcard_capacity_structure_2026-07-13.md` proposed
  Laplacian-eigenmap spectral factorization of the same 190k-edge graph as a capacity/codec lever (frequency +
  usage-graph spectral basis). This drill independently arrives at the SAME primitive (graph Laplacian
  eigenvectors) for a completely different purpose (init warm-start rather than codebook design) — two
  independent research threads converging on one shared cheap CPU artifact (a spectral decomposition of the
  entity graph) that, once computed, serves BOTH the capacity drill's codec test AND this drill's init test.
  Recommend computing it once, reusing twice.
- **Brain-grounding**: (a) developmental/scaffolded curriculum learning (shaping paradigms, easy-to-hard
  exposure) is the soft biological analog for curriculum edge-ordering (rank 7) — real but modest, matches the
  ~1-4% static-KGE number, not the 25% temporal-KG outlier; (b) hippocampal replay / systems consolidation
  under Complementary Learning Systems theory (Kumaran/McClelland/O'Reilly) is the direct analog for
  snapshot-ensembling / checkpoint-averaging (rank 2) — the brain does not retrain from scratch, it replays
  and integrates multiple experience-snapshots into one stable long-term representation, structurally
  identical to averaging multiple training-trajectory checkpoints into one better estimator; (c) synaptic
  scaling / homeostatic plasticity is the loose analog for structural/informed initialization (rank 1) — the
  nervous system does not start from an arbitrary baseline, it maintains a structured homeostatic starting
  point that measurably accelerates and improves subsequent learning, mirroring why literature-reported
  structural init beats naive Gaussian init by a wide margin.
- **Does NOT re-litigate** capacity (arbitrary-label no-free-lunch, closed per same-day quantum/bio/wildcard
  drills) or grounding (forward-model/prediction-error mechanism, same-day neuro drill) — this drill is
  strictly the training-recipe axis holding architecture and the capacity/grounding conclusions fixed.

## Substrate-product implications

This is a glass-box, same-scoring-function improvement path — no architecture change, no new interpretability
debt. Concretely actionable for the next exp_dev cycle on `AdditiveKGMap` / `fit_kge_anchor1`:

1. **First anchor candidate**: spectral-init warm-start test (rank 1 above). Pointer: modify
   `experiments/_kge_anchor1_fit.py` line 82 (`X = (torch.randn(N, k, generator=g) * 0.1)...`) behind a new
   `init_mode` kwarg (`"gaussian"` default = bit-identical current behavior, `"spectral"` = new path), so the
   confirmed 0.1282 baseline stays reproducible and the new arm is purely additive. Acceptance-gate pipeline:
   `experiments/exp_additive_map_acceptance_gate_v1.py`. Held-out-entity split: same as the VET-confirmed run.
   Tier hint: this is a recipe-only change to an already-HARD_PASS anchor, so it's a low-risk, high-precedent
   refinement cell, not a novel-mechanism cell — should smoke-gate easily.
2. **Second anchor candidate (sequenced after #1, or in parallel if capacity allows)**: retain-N-checkpoints
   mode for `experiments/_fit_checkpoint.py::FitCheckpoint` (currently durability-only, overwrites) as the
   structural prerequisite for snapshot-ensembling (rank 2) — this is an infra change, not a recipe change,
   file it as a `hdi_testbed` task rather than an `exp_dev` cell.
3. **Third anchor candidate (Phase-2 sweep, lower urgency)**: small hyperparameter grid over
   (lr, gamma, n3_lambda, batch_size) x (DURA vs N3) x (label_smoothing on/off) on top of whichever init wins
   from #1 — bundle DURA-swap and label-smoothing into this sweep since both are trivial one-line changes.
4. Ruled-out-for-now, do not spend cycles: independent multi-seed ensembling (dominated by #2 on cost),
   GAN-based negative samplers (proven worse than what we have), InfoNCE/contrastive full redesign
   (architecture-confounded, out of scope for "hold architecture fixed").

## Citations (verified count: 13 distinct sources cited by name/year/venue across the 4 sub-agent scans)

1. Ruffinelli, Broscheit, Gemulla, "You CAN Teach an Old Dog New Tricks!", ICLR 2020.
2. Sun, Deng, Nie, Tang, "RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space", ICLR 2019 (self-adversarial negative sampling).
3. Lacroix, Usunier, Obozinski, "Canonical Tensor Decomposition for Knowledge Base Completion", ICML 2018 (N3 + reciprocal).
4. Zhang, Cai, Wang, "Duality-Induced Regularizer for Tensor Factorization Based Knowledge Graph Completion", NeurIPS 2020 (DURA).
5. Zhang, Yao et al., "NSCaching: Simple and Efficient Negative Sampling for Knowledge Graph Embedding", ICDE 2019.
6. Ahrabian et al., "Structure Aware Negative Sampling in Knowledge Graphs" (SANS), EMNLP 2020, arXiv:2009.11355.
7. Cai, Wang, "KBGAN: Adversarial Learning for Knowledge Graph Embeddings", NAACL 2018, arXiv:1711.04071.
8. PyKEEN-extension n_neg sweep, arXiv:2508.05587 (2025).
9. Dettmers, Minervini, Stenetorp, Riedel, "ConvE" (1-vs-all / KvsAll scoring, label smoothing ablation), AAAI 2018.
10. Balazevic, Allen, Hospedales, "TuckER" and "HypER", 2018-2019 (label smoothing use / disagreement w/ ConvE).
11. Wang et al., "SimKGC: Simple Contrastive Knowledge Graph Completion with Pre-trained Language Models", ACL 2022.
12. SnapE (snapshot ensemble via cyclical LR for KGE), arXiv:2408.02707 (2024).
13. Informed/schema-warm-started initialization for continual TransH, arXiv:2511.11118 / ScienceDirect S0925231226014438 (2025-2026).
Plus: Kumaran/McClelland/O'Reilly Complementary Learning Systems theory (general neuroscience framing, not a single paper) for the brain-grounding paragraph.

All numbers above were extracted directly by the sub-agents from primary-source abstracts/tables/PDFs, not
inferred; every lift figure in the ranked table carries its source. P_deflated = 0.15-0.25 applied throughout;
novel-synthesis claims (the wildcard-drill Laplacian-eigenmap reuse, the compose-op-washout hard-fail
mechanism) capped at P<=0.50.
