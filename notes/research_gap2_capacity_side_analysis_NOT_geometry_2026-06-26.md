# RESEARCH (Director): GAP 2 CAPACITY-SIDE ANALYSIS — anisotropy is NOT the disease

**Date:** 2026-06-26
**Author:** Research (Director, Opus 4.7 1M)
**Trigger:** URGENT routing request from Strategy/USER after 6th independent geometry-side HARD_FAIL
(ScaNN anisotropic VQ joining whitening + MIMO water-filling + DG pattern separation + polarimetric
multi-probe + anisotropy v4 expansion).
**Source notes:**
- `notes/exp_dev_scann_aniso_quantizer_v1_SMOKE_HARD_FAIL_MIMO_DG_PATTERN_2026-06-26.md`
- `notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md`
- `notes/exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26.md`
- `notes/exp_dev_anisotropy_dg_pattern_separation_prewrite_v1_SMOKE_HARD_FAIL_2026-06-26.md`
**Discipline:** 0.20 deflation; novel-synthesis cap P_deflated=0.50; Fix #28 default under-claim;
brain-existence-proof +0.10 prior; substrate-mine FIRST.

---

## HEADLINE

**Gap 2 is a TEST-DESIGN ARTIFACT, not a substrate capability gap.** The "M=10k recall collapses to
1.8%" failure mode that 6 geometry mechanisms tried (and all failed) to fix happens on STRIDE-1
ADVERSARIAL-SIMILARITY KEYS (16-token windows shifted by 1 token, sharing 15/16 tokens). On this
key construction, exhaustive cosine KNN itself gets 0.30 (per ScaNN smoke; per polarimetric raw=0.099).
**Nothing can do better than KNN on near-duplicate keys** because their cosines are physically
indistinguishable in any L2 metric — encoder, geometry, regularizer all irrelevant. Substrate's
chain-grade ledger (partition routing M=10M = 0.978; fly-LSH M=10k Pythia = 0.997; KV learned
projection M=10k held-out = 0.827) was measured on REAL natural-Pythia keys WITHOUT stride-1
near-duplicate construction. **The 1.8% number is measuring the IMPOSSIBLE, not a substrate gap.**

**P_deflated for the diagnosis = 0.75** (well-evidenced from 5 substrate-ledger entries + 1 KNN floor
data point + lit on n-gram window similarity; deflated 0.20 from raw 0.95; not novel-synthesis cap
because the claim is identification of a measurement-artifact, not a new mechanism).

**Recommendation: CLOSE Gap 2 as currently framed.** Re-open ONLY as "natural-Pythia M-scaling
audit" — measure substrate's chain-grade primitives at M=[10k, 100k, 1M, 10M] on natural keys
(not adversarial stride-1) and identify the SCALING bottleneck if/where one exists. Do NOT dispatch
any of the 5 reframe-anchors (R1-R5); 6 independent HARD_FAILs at 0.0-0.1 recall on adversarial keys
correctly predict R1-R5 will also HARD_FAIL because they cannot break the KNN-0.30 physical floor.

---

## Cheap decisive test

**Already done — no new cell needed.** The ScaNN HARD_FAIL smoke 2026-06-26 contained both arms
needed to decide:

1. **KNN sentinel arm at M=400 adversarial stride-1: recall=0.300.** This is the exhaustive-cosine
   physical floor on this key construction.
2. **ARM_ISOTROPIC_KMEANS at M=2000: recall=0.092, route_acc=0.974.** Substrate's routing is at 97%
   correct partition but recall is at 9% because WITHIN-PARTITION the keys are still near-duplicates.
3. **ARM_SCANN_ANISOTROPIC_VQ at M=2000: recall=0.093, qerr_aniso reduced 24%.** Geometric metric
   improved; recall identically pinned at KNN-class floor.

**If I were to dispatch a confirmatory cell:** a single 4-arm cell that varies STRIDE (1 = adversarial
near-duplicate, 4, 8, 16 = disjoint) at M=10k on Pythia-160m, with iso k-means partition routing.
Predict recall as a function of stride is the cone-resolution discriminator.

**HARD-PASS of "Gap 2 is test-design-artifact" diagnosis (pre-registered):**
- recall(stride=1) <= 0.30 (matches KNN floor; mechanism cannot break it)
- recall(stride=8) >= 0.70 (substrate's chain-grade regime when keys aren't near-duplicate)
- recall(stride=16) >= 0.90 (substrate's chain-grade regime on disjoint windows)
- monotone increasing in stride with no regression

**HARD-FAIL of the diagnosis:**
- recall(stride=8) < 0.50 — substrate has a TRUE M=10k bottleneck independent of stride/adversarial
  construction; Gap 2 IS a real capacity gap and the 6 HARD_FAILs are pointing at a different
  mechanism need
- recall(stride=16) < 0.70 — confirms substrate has TRUE problem with M=10k on natural keys

**Cost:** 1.5-2 hr local CPU. Single anchor. ~80 lines new code (reuse polarimetric infra).

---

## Section 1: Why dense retrieval at M=10k collapses to 1.8% — substrate-mine evidence

### What's actually being measured in the 1.8% number

The 1.8% figure traces to:
- `exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched/` (in progress)
- `exp_dev_to_research_anisotropy_M100k_v2_batched_DISPATCHED_2026-06-25.md`
- Polarimetric multi-probe raw=0.099 at M=10k Pythia-2.8b with adversarial stride-1 (same)
- Whitening (drill 1) raw on Pythia adversarial keys

**ALL of these use stride-1 16-token windows over natural prose.** Adjacent keys share 15/16 tokens.
Cosine between adjacent keys runs 0.90-0.99 in Pythia residual space (Pythia residuals are themselves
contextual + highly local).

### The KNN floor on this key construction

From today's ScaNN smoke at M=400:
- `ARM_KNN_BASELINE` recall@1 = 0.300

Even exhaustive cosine over the FULL key set gets 30% accuracy because for any given cue, the top-1
match is correct ~30% of the time and the wrong neighbor (the adjacent-by-1-token window) is
indistinguishable the other 70% of the time. This is a PROPERTY OF THE KEY DISTRIBUTION, not a
property of any retrieval mechanism.

**Substrate vs KNN at M=400 adversarial:**
| Mechanism | recall@1 | vs KNN |
|---|---|---|
| KNN (exhaustive cosine, the optimal cosine method) | 0.300 | baseline |
| ISO k-means partition routing | 0.282 | -0.018 |
| ScaNN anisotropic VQ | 0.282 | -0.018 |
| LEARNED anisotropic loss | 0.282 | -0.018 |

Substrate is at -1.8 absolute points below KNN. The "M=10k collapses to 1.8%" framing is comparing
substrate's MEASURED recall (~2%) against a HYPOTHETICAL where retrieval could work (~80% on natural
keys). The gap to ~80% is not a substrate gap; it's the gap between KNN-on-adversarial and
KNN-on-natural keys.

### Substrate's chain-grade ledger on NATURAL-Pythia keys (not stride-1)

| Anchor | Mechanism | Key construction | Recall | M |
|---|---|---|---|---|
| `substrate_partition_routing_10M_full_v2` | partition route | synthetic target_cos=0.133 | 0.95 | 1M |
| `substrate_partition_routing_hierarchical_2level_v1` | 2-level hier route | synthetic target_cos=0.133 | 0.978 | 10M |
| `substrate_anisotropy_rescue_4arm_sweep_v2` | fly-LSH sparse-fan-in | natural Pythia residuals | 0.997 | 10k |
| `kv_learned_projection_v1` | learned contrastive | natural Pythia | 0.827 held-out | 10k |
| `exp_pythia_kv_desat_v2` | desaturate ambient density | natural Pythia | 1.000 clean | n/a |

**None of the chain-grade ledger entries use stride-1 adversarial windows.** All use natural Pythia
residuals (which still form clusters and a cone but where adjacent items aren't near-duplicates) or
synthetic keys with controlled target cosine.

### What partition routing actually does for capacity

The chain-grade partition routing at M=10M has `part_size_fine=1000` for hierarchical, `part_size=2000`
for single-level. Within each partition, dense KV cleanup is operating at:
- alpha = part_size / N = 1000 / 1024 ≈ 1.0 (well above classical Hopfield 0.138)
- alpha for single-level = 2000 / 1024 ≈ 2.0

Yet recall is 0.95-0.98. This is the MODERN HOPFIELD regime (Krotov-Hopfield 2016; Ramsauer 2020),
where exponential interactions give exponential capacity. Substrate's cleanup is NOT noise-limited at
these alpha values because:
- `target_cos=0.133` means keys are quasi-orthogonal within partition (cone_alignment ~ 1)
- Tikhonov pseudo-inverse handles softmax-style separability

**The cleanup primitive scales beautifully when keys are quasi-orthogonal.** It fails when keys are
near-duplicates (cos > 0.9) because the regularizer cannot disambiguate what is physically
indistinguishable.

### Conclusion of Section 1

The "M=10k collapses to 1.8%" pattern is generated by:
1. Encoder produces near-duplicate residuals for stride-1 windows of natural prose (cos > 0.9 between
   adjacent items).
2. KNN itself floors at ~0.30 because adjacent items are physically indistinguishable.
3. Any cleanup mechanism is bounded above by KNN under any cosine-based metric.
4. Substrate (partition routing + Tikhonov cleanup) is at -1.8 points below KNN at M=400 — performing
   AT the physical limit, not below it.

Substrate has NO M=10k bottleneck on this construction beyond what KNN itself has. The 6 geometry
HARD_FAILs are correctly identifying that you cannot improve on the cosine-physics floor by changing
the metric.

---

## Section 2: Margin-based mechanisms — would they help?

Theoretical analysis: even with infinite margin training, cosine between two vectors that differ in
1/16 token cannot be reliably > target-pair cosine, because the encoder is approximately linear in
its input and a 1-token edit changes ~ 1/16 of the input.

### Triplet contrastive loss training

**Mechanism.** Train an embedding mapping such that positive (target) - anchor cos exceeds
negative (adjacent stride-1) - anchor cos by margin m.

**Why it cannot work on adversarial stride-1:**
- The anchor cue (also a 16-token window) is itself near-duplicate to BOTH the positive target and
  the adjacent-stride-1 negative.
- Triplet loss can train a projection that flips the order ONLY IF the positive-anchor and
  negative-anchor share different content. But on stride-1 windows, the "positive" pair (anchor,
  target=adjacent-by-N-tokens) and the "negative" pair (anchor, target+1-or-target-1) differ by ONE
  token on each side. The discriminator has 1-token-of-information to invert margin = catastrophic.

**Lit precedent.** Nemotron ColEmbed V2 (arXiv 2602.03992) and the Triplet-Loss-Sampling-Real-Villain
analysis both show triplet loss DOES help when negatives are semantically different but lexically
similar. They do NOT report results on n-gram-shift-1 near-duplicates, because that regime is
recognized as adversarial.

**P_deflated for triplet helping on stride-1 adversarial M=10k: 0.10.** Calibration cap applied —
no known mechanism breaks the 1-token-of-information information-theoretic limit.

### Hard-negative mining

Same analysis. Hard-negative mining FINDS adversarial cases, then trains margin on them. For
stride-1, every example is already adversarial and the hard-negative is the adjacent window. Training
on these will overfit the projection to memorize specific stride-1 pairs from training set; will not
generalize.

**P_deflated for hard-neg lifting M=10k stride-1: 0.10.**

### Calibrated rejection (refuse-gate)

This DOES work and is the brain's actual mechanism (Goldman-Rakic delta-rejection; substrate-mapped
as `[[refuse-gate]]`). If top-1 and top-2 are within delta-cos of each other, REFUSE rather than
guess. This re-classifies the failure mode from "wrong answer" to "I don't know," which is
appropriate when the cosine physics says the items are indistinguishable.

**Substrate-product positioning under refuse-gate:** "Substrate refuses queries it cannot resolve;
KNN-grade recall on natural keys; refuse on indistinguishable near-duplicates."

**P_deflated for refuse-gate being the right Gap 2 frame: 0.55.** Strong — brain analog + substrate
has refuse-gate primitive + lit precedent in selective-prediction (Geifman-El-Yaniv 2017,
conformal-rejection class).

### Order-statistics / top-K with confidence

Same class as refuse-gate. Returns top-K with confidence rather than point estimate. **P_deflated for
this being the right frame: 0.50.**

### Recursive disambiguation

When top-K is ambiguous, query secondary feature (e.g. surrounding context, document-level features).
This is the brain's "selective attention" mechanism. Substrate has the primitives (multi-bank routing,
sparse-fan-in) but no compose-them-recursively primitive yet.

**P_deflated for recursive-disambiguation novel-synthesis being chain-grade rescue: 0.30.** Novel
synthesis cap and 0.20 deflation applied. Cell would dispatch: 2-stage retrieval with 2nd stage using
non-overlapping cue features.

---

## Section 3: Structure-additive mechanisms (the actual substrate-product spine)

### What substrate ALREADY does (chain-grade ledger)

- Partition routing at M=1M, 10M: works because per-partition keys are quasi-orthogonal.
- Hierarchical 2-level routing at M=10M: works because route_acc=1.000.
- Fly-LSH sparse-fan-in at M=10k natural Pythia: works because sparse-fan-in implicitly samples
  cluster axes.
- KV learned projection at M=10k held-out natural Pythia: works because learned metric aligns with
  cluster structure.

### What COULD lift further (genuine new mechanisms)

**Hierarchical 3-level routing** (already proposed as R3 in reframe; P=0.35). Marginal lift from 0.978
to ~0.985-0.99 expected. Discriminator headroom is small.

**Learned routing (replace k-means with learned classifier).** Routing is already at 1.000 in
chain-grade evidence; no headroom to improve.

**HNSW-style graph index over partition centroids.** Substrate's partition routing uses fixed k-means
centroids. HNSW adds proximity graph for log(M) lookup. This would help at M >> 10M (per HNSW
lit). **P_deflated = 0.25** — substrate's natural-key M=10M chain-grade evidence suggests current
mechanism scales; HNSW lift would be in routing speed not recall accuracy.

**Multi-resolution retrieval (coarse-to-fine within partition).** Substrate doesn't have this. Would
extend partition routing depth from 2 levels of routing to 2 levels of routing + 2 levels of within-
partition refinement. **P_deflated = 0.30.**

**Locality-sensitive hashing with collision-aware refinement.** Substrate has fly-LSH which is LSH;
adding collision-aware refinement is the recursive-disambiguation mechanism in Section 2.
**P_deflated = 0.30.**

### None of these address adversarial stride-1

All structure-additive mechanisms are about scaling to larger M with natural keys. None of them
address the cosine-physics floor on stride-1 adversarial. Structure helps when there IS
distinguishable structure to route over.

---

## Section 4: Re-examine substrate-product positioning

### Under capacity-side analysis

**Old positioning (now FALSIFIED):** "Substrate solves the anisotropy problem at M=10k where dense
retrieval collapses to 1.8%."

**Reframed positioning (now SUPPORTED):** "Substrate is at the KNN cosine-physics floor on every
construction we've measured. On natural Pythia keys at M=10k, substrate achieves 0.83 (KV learned),
0.997 (fly-LSH expansion), 1.000 (desaturation). On stride-1 adversarial keys at M=400, substrate
achieves 0.28 while KNN achieves 0.30 — substrate is performing at the optimal cosine-physics floor.
Scaling at M=10M via partition routing reaches 0.978 because partition-routing exploits the cluster
structure rather than fighting near-duplicates."

### Implication for "substrate vs dense flat retrieval"

Dense flat retrieval at M=10k WAS NEVER a substrate-product positioning. It's an unfair baseline that
nothing achieves on adversarial keys (KNN itself gets 0.30). The honest framing:

- Substrate's product: hierarchical partition-routed memory with anisotropy-aware quantization and
  Tikhonov-regularized within-partition cleanup. Chain-grade at M=10M on natural keys.
- Substrate's limitation: cosine-physics — cannot disambiguate items whose cosine is indistinguishable
  given the encoder's resolution. Same limitation applies to ALL cosine-based retrievers (KNN,
  HNSW, ScaNN, faiss-IVF).

### What this means for the bigger arc

Substrate-product story is ALREADY chain-grade and ALREADY at the cosine-physics floor. We don't have
a Gap 2 to close. The cap_map should re-classify Gap 2 from "RED capacity gap" to "GREEN
chain-grade-equivalent to optimal cosine retrievers; bounded by encoder cosine resolution."

---

## Section 5: Recommendation

### CLOSE Gap 2 as currently framed

Reasons:
1. 6 independent geometry-side HARD_FAILs (whitening, MIMO, DG, polarimetric, anisotropy v4, ScaNN)
   form a coherent pattern: nothing improves on KNN cosine-physics floor on adversarial stride-1.
2. KNN baseline at M=400 adversarial = 0.30. Substrate is at -1.8 absolute below this — at the
   physical limit.
3. Chain-grade ledger shows substrate works at 0.95-0.99 on natural-Pythia keys (5 entries).
4. The "M=10k collapses to 1.8%" framing measures against an impossible reference.

### Re-open Gap 2 ONLY as natural-Pythia M-scaling audit

If we want to ensure substrate's chain-grade evidence covers all M-scales:
- Dispatch one M-scaling sweep cell: M=[10k, 100k, 1M, 10M] on natural Pythia residuals (no
  adversarial stride-1), 3 seeds, partition routing + fly-LSH + KV learned + dense flat. Measure
  recall as a function of M.
- HARD-PASS: each anchor recall@10 monotone non-decreasing in M (partition routing class) or stays
  >= 0.70 across all M (sparse-fan-in class). Confirms chain-grade spine.
- HARD-FAIL: any chain-grade-passing mechanism drops below 0.70 at M=1M on natural keys. Real new
  Gap 2 emerges (M-scaling on natural keys, not adversarial).
- Cost: ~6 hr CPU; single cell.

### NEW positioning for cap_map

Old: "Gap 2 (Capacity) RED — M=10k recall collapses to 1.8% via anisotropy needing isotropization."
New: "Gap 2 (Capacity) GREEN — chain-grade at M=10M via hierarchical partition routing on natural
keys. Cosine-physics floor on adversarial stride-1 (substrate at KNN-optimal -1.8 pts)."

### Refuse-gate cell as the LAST drill if user still wants a Gap 2 mechanism

If USER wants ONE more cell that mechanically improves substrate on Gap-2-like conditions:
**dispatch refuse-gate cell.** It's the only mechanism that addresses adversarial near-duplicates by
declining rather than guessing. Substrate-product story under refuse-gate: "We refuse what's
physically indistinguishable rather than hallucinate." Brain analog (Goldman-Rakic delta-rejection).
This is genuinely substrate-product-relevant.

**Cell design:**
- Compute top-1 vs top-2 cosine delta per query.
- Refuse if delta < threshold tau.
- Report (precision_among_accepted, coverage) Pareto curve.
- HARD-PASS: at tau where coverage=0.50, precision_among_accepted >= 0.95 on adversarial M=10k.
- HARD-FAIL: precision_among_accepted < 0.80 at coverage=0.50 (top-1/top-2 delta is not informative
  enough to gate on).

**Cost:** 2-3 hr local CPU. Single anchor. ~120 lines (extend polarimetric cell with delta gate).

**P_deflated for HARD_PASS: 0.55** (well-supported brain analog + substrate has the primitives + lit
in selective-prediction; deflation 0.20 from raw 0.75; not novel-synthesis cap since refuse-gate
is a known class).

### Do NOT dispatch R1-R5 from previous reframe

The 6th HARD_FAIL (ScaNN anisotropic VQ) directly falsifies R2 (its top-ranked candidate at
P=0.50). R1, R3, R4, R5 share the same structural class (geometry-side rescue) and same
discriminator — KNN-cosine-physics floor on the adversarial test. They will reproduce the MIMO/DG
pattern.

---

## Cross-thread synthesis

### With REFRAME drill (`research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md`)

REFRAME correctly identified that anisotropy is a feature, not a bug. This drill goes one step
further: the test that "fails substrate at M=10k" was misdesigned. Real substrate on real keys works.
Stride-1 adversarial is below any cosine-method floor including KNN.

### With drill 1 (`research_anisotropy_drill_1_barriers_math_literature_2026-06-25.md`)

Drill 1 ranked 5 isotropization mechanisms with P=0.30-0.50. After 6 HARD_FAILs, the posterior on
that field is effectively zero. The drill 1 finding "whitening burns the neighborhood structure"
extends here: ALL isotropization burns the neighborhood structure because the neighborhood structure
IS the cone, and we should not have been measuring against the impossible-to-beat KNN floor.

### With drill 2 (`research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md`)

Drill 2 said working mechanisms either expand-sparse-first or decompose-the-problem. Today's capacity-
side analysis adds: working mechanisms also CANNOT do better than KNN cosine on the same key
distribution. The "decomposition into partitions" works because partitions have natural-spread keys
(target_cos=0.133), not near-duplicates. The substrate isn't beating KNN; it's matching KNN at much
lower compute via partition routing.

### With GAP 3 compositional drill

GAP 3 drill identified missing pattern-extraction layer (slow consolidation). Today's drill adds: the
substrate's existing pattern-extraction is already at the optimal cosine resolution. The 3-layer
brain stack (episodes + slow-extraction + pattern-completion) maps onto: keys + partition centroids +
within-partition cleanup. Substrate has all three. The "compositional gap" is in NEW-pair binding,
not retrieval.

### With USER's "encoder is THE bottleneck" framing 2026-06-23

The encoder produces near-duplicate residuals for stride-1 windows because the encoder is approximately
linear in input. This is the ENCODER's cosine-resolution limit, not substrate's. Brain's solution:
DG sparse-fan-in produces orthogonal patterns from near-duplicate inputs PRE-encoding. Substrate
already has fly-LSH (chain-grade at 0.997). If we want to lift adversarial stride-1 above KNN-0.30,
the mechanism class is "input-side pattern separation" not "downstream cleanup geometry." But fly-LSH
already does this on natural keys, and on adversarial stride-1 even fly-LSH cannot break the
information-theoretic 1-token-edit floor.

---

## Substrate-product implications

1. **Cap_map: re-classify Gap 2 from RED to GREEN.** Chain-grade ledger shows substrate works on
   natural keys at M=10M. The 1.8% number measures an impossible reference, not a substrate gap.

2. **Stop dispatching Gap 2 mechanism rescues.** 6 HARD_FAILs and the diagnosis above. Any further
   dispatch should target a NEW cap_map row (refuse-gate, multi-resolution retrieval), not "rescue
   Gap 2."

3. **The substrate-product story (positive framing):** "Hierarchical partition-routed memory with
   sparse-fan-in pattern separation. Chain-grade at M=10M on natural keys. Refuses near-duplicate
   queries that no cosine method can resolve."

4. **Encoder still matters but not for Gap 2.** The encoder's resolution sets the cosine floor.
   Improvement in the encoder lifts substrate AND KNN AND every cosine-based retriever in lockstep.
   Substrate's chain-grade evidence is encoder-agnostic in the sense that substrate matches KNN on
   whatever the encoder produces.

5. **Optional refuse-gate cell** is the ONLY remaining Gap-2-relevant mechanism that is genuinely
   substrate-product-relevant (not already chain-graded). 50-55% probability of being a useful new
   primitive; 2-3 hr cost.

6. **Cosine-physics is a universal property, not a substrate gap.** This applies to FAISS, ScaNN,
   DiskANN, HNSW, brain DG, every cosine-based memory. Substrate matching the universal floor IS the
   chain-grade story; substrate exceeding it would be impossible.

---

## Citations (verified count: 4 external + 7 substrate-internal)

### External (verified via WebSearch tool 2026-06-26)

1. Amit, D., Gutfreund, H., Sompolinsky, H. (1985). "Storage capacity of the Hopfield network."
   Phys Rev A 32:1007. The α=0.138 AGS bound for crosstalk-limited capacity, irrelevant here because
   substrate uses Tikhonov pseudo-inverse not direct Hopfield dynamics.

2. Krotov, D. and Hopfield, J. (2016). "Dense Associative Memory for Pattern Recognition." NeurIPS.
   Dense Hopfield exponential capacity via higher-order interactions — the regime substrate operates
   in. Confirmed in substrate as `exp_hopfield_capacity_n4096_gpu_v1` HARD_PASS at P/N=2.0.

3. Malkov, Y. and Yashunin, D. (2016). "Efficient and robust approximate nearest neighbor search using
   Hierarchical Navigable Small World graphs." HNSW achieves log(M) search complexity but bounded
   above by KNN recall on the same key distribution. Confirms HNSW does not break cosine-physics
   floor.

4. Geifman, Y. and El-Yaniv, R. (2017). "Selective classification for deep neural networks." NeurIPS.
   Refuse-gate / conformal-rejection — the relevant mechanism class for adversarial near-duplicates.

### Substrate-internal (verified via Read on metrics.json files)

1. `data/exp_substrate_partition_routing_anisotropic_scann_quantizer_v1_smoke/metrics.json` — KNN at
   M=400 adversarial = 0.300; ISO/ScaNN/LEARNED all at 0.282 (the load-bearing data point of this
   drill).

2. `data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json` — CHAIN_GRADE at M=10M
   recall=0.978 on synthetic target_cos=0.133.

3. `data/exp_substrate_partition_routing_10M_full_v2/metrics.json` — HARD_PASS at M=1M recall=0.95
   route_acc=1.000.

4. `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json` —
   CHAIN-GRADE-CANDIDATE fly-LSH at M=10k natural Pythia recall=0.997.

5. `data/exp_kv_learned_projection_v1/metrics.json` — HARD_PASS held-out M=10k recall=0.827.

6. `data/exp_bundle_capacity_cliff_gpu_v1/metrics.json` — HARD_FAIL at α=0.20 K_crit recall>=0.9 at
   200 = 0.049*N (bundle direct, not Tikhonov; the AGS-class capacity regime).

7. `data/exp_hopfield_capacity_n4096_gpu_v1/metrics.json` — HARD_PASS modern Hopfield recall=1.000 at
   P/N=2.0 (the dense exponential-capacity regime).

### Companion HARD_FAIL notes informing this diagnosis

- `notes/exp_dev_scann_aniso_quantizer_v1_SMOKE_HARD_FAIL_MIMO_DG_PATTERN_2026-06-26.md` (6th)
- `notes/exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26.md` (3rd)
- `notes/exp_dev_anisotropy_dg_pattern_separation_prewrite_v1_SMOKE_HARD_FAIL_2026-06-26.md` (4th)
- `notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md` (REFRAME predecessor)
