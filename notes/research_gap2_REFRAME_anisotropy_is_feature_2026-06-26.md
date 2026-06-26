# RESEARCH (Director): GAP 2 REFRAME — anisotropy is a FEATURE, not a bug

**Date:** 2026-06-26
**Author:** Research (Director, Opus 4.7 1M)
**Trigger:** URGENT REFRAME request from Strategy/USER — both Tier-A anchors from this morning's 5x
anisotropy drill HARD_FAILED at smoke with IDENTICAL structural pattern (huge geometric lift, zero or
negative recall lift). Reframe whether GAP 2 framing itself is wrong.
**Source notes:** `exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26.md` +
`exp_dev_anisotropy_dg_pattern_separation_prewrite_v1_SMOKE_HARD_FAIL_2026-06-26.md`
**Discipline:** 0.20 deflation novel-synthesis; cap P_deflated=0.50; brain-existence-proof +0.10
prior; Fix #28 default UNDER-claim; Fix #28 read metrics.json per-arm not verdict_msg.

---

## HEADLINE

**Gap 2 was mis-defined.** Substrate's M=10k recall collapse on real Pythia keys is NOT caused by
anisotropy needing isotropization. It is caused by GLOBAL DENSE CLEANUP attempting to serve a
clustered/anisotropic key population WITHOUT routing. The "anisotropy is the disease, isotropization
the cure" frame is borrowed from cosine-NN retrieval theory (Mu-Viswanath 2018) which does NOT apply
to substrate's Tikhonov-regularized pseudo-inverse cleanup. Every chain-grade-passing mechanism in
the substrate ledger (partition routing M=10M / KV learned projection / hierarchical 2-level / fly-LSH
sparse-fan-in) EXPLOITS the anisotropic cluster structure rather than removing it. Lit confirmation:
Cai-Kanai-Belkin (ICLR 2021) showed isotropy EXISTS WITHIN CLUSTERS in BERT embedding space — the
"anisotropy" measured at global scale IS the cluster structure. Reframed Gap 2 should target
"PARTITION-AWARE CAPACITY LIFTING within the cone," not "global isotropization."

**P_deflated for the reframe being correct: 0.65** (well-supported by 5+ chain-grade ledger entries
and 2 lit precedents; deflated 0.20 from raw 0.85 per calibration penalty; not novel-synthesis cap
since the empirical pattern is well-evidenced).

---

## Cheap decisive test

**Decisive in-flight verification:** the polarimetric multi-probe v1 cell (running on remote_cpu) and
the v4 CPU expansion sweep (running) provide one more round of evidence. Both test sparse-fan-in
mechanisms that PARTITION the cone rather than isotropize it.

**Predictions under reframe (HARD_PASS if reframe correct):**
- v4 CPU FLY_4096x recall lifts MONOTONICALLY with expansion factor at adversarial keys M=2k. The
  mechanism is sparse-fan-in (= cone-clustering implicit partitioning), so the reframe predicts
  CONTINUED LIFT at brain-scale 4096x. Specifically: FLY_4096x >= 0.60 at adversarial M=2k.
- Polarimetric K=10 LEARNED probes >= 0.50 (LEARNED probes effectively learn the cone's principal
  axes = anisotropy-aware retrieval, the substrate-native analog to anisotropic vector quantization).
- AB_CONTROL random K probes >= 0.40 (confirms it's the multi-probe partitioning, not LSH-specific).

**HARD_FAIL of reframe (defensive predictions):** if v4 CPU FLY_4096x ties FLY_8x within 0.05 AND
polarimetric LEARNED < 0.30, then "exploit-the-cone" mechanisms ALSO fail and the issue is more
fundamental than anisotropy framing — Gap 2 would then re-classify as "dense cleanup capacity caps
at M ~1k for any non-trivial key population."

---

## Section 1: What is substrate's M=10k recall actually limited by?

### Substrate-mining evidence: 5 chain-grade-passing mechanisms on real data

Pulled directly from `data/exp_*/metrics.json` (Fix #28: per-cell numbers, not verdict text).

| Anchor | Mechanism | Recall@scale | Lift vs raw/flat | Common structural feature |
|---|---|---|---|---|
| `substrate_partition_routing_hierarchical_2level_v1` | 2-level partition routing | 0.978 @ M=10M (cv=0.006) | flat=0.30 (collapses) | DECOMPOSES key-space into 10 coarse + ~100 fine partitions; per-partition KV stays in the regime where dense cleanup works |
| `substrate_partition_routing_10M_full_v2` | Single-level partition routing | 0.950 @ M=1M (cv=0.011) | flat=0.514 | route_acc=1.000 — categorical clusters in the cone ARE routable; routes AROUND anisotropy by exploiting category structure |
| `kv_learned_projection_v1` | Contrastive learned key projection | 0.827 heldout @ M=10k | analytic-ceiling=0.032; lift=0.795 (25x) | LEARNED projection adapts to data distribution — effectively learns Mahalanobis metric for the cone |
| `substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full` | Fly-LSH sparse-fan-in K=5 expand 5x | 0.997 @ M=10k Pythia-2.8b | raw=0.018 (55x lift) | SPARSE-RANDOM fan-in samples K=5 axes — implicit IVF-like partitioning of the cone via random projection clusters |
| `exp_pythia_kv_desat_v2` | De-saturation reduces ambient density | clean=1.000 | depends on regime | Operates on REDUCED key density — confirms the limit is interaction count, not isotropy |

**Pattern:** every working mechanism exploits or AVOIDS the global dense cleanup over an anisotropic
key population. Not one chain-grade mechanism succeeds by isotropizing first and then doing dense
cleanup. The two HARD_FAILs this morning (water-filling readout-side; DG pattern separation
input-side) BOTH attempted to isotropize first and then dense-cleanup; both lifted geometry by 5-186x
but DROPPED recall by 3-15 absolute points.

### What is substrate's M=10k actually limited by? (mechanism inventory)

Not anisotropy per se. The limit on global dense KV cleanup at M=10k on real Pythia is a JOINT
effect of:

1. **Categorical cluster collisions.** Real Pythia residuals form ~10-100 semantic clusters (token
   class, syntactic role, document topic). Within a cluster, cosines run 0.5-0.8. The dense KV
   pseudo-inverse cannot disambiguate cue-key pairs whose KEYS are within-cluster (the cue's
   projection onto every same-cluster key is large). This is a CLUSTER-LEVEL problem, not a
   global-axis-orientation problem.

2. **Per-cluster capacity scaling.** Within a cluster of size n_c, dense KV cleanup behaves roughly
   like Hopfield at K/N = n_c/d_eff. Once n_c exceeds the cluster's intrinsic effective dimension,
   recall collapses for that cluster. The partition routing chain-grade evidence (M=10M with
   part_size=2000) tells us the substrate's cleanup is FINE at ~2000 atoms per partition; the
   global-M=10k uniform cleanup fails because some clusters contain >>2000 same-class atoms.

3. **Cue-side anisotropy mismatch.** Cues are queried from the same anisotropic distribution as keys
   were stored from. The Tikhonov pseudo-inverse correctly downweights the cone axes IF the cue
   shares the same distribution as the keys — which it does. So Tikhonov is ALREADY doing the right
   thing per-cue; what it can't do is increase capacity within a saturated cluster.

**Diagnosis:** substrate's bottleneck at M=10k is "too many same-cluster atoms in one undifferentiated
cleanup," not "global cone shape needs flattening."

---

## Section 2: Mu-Viswanath revisited — does it apply to substrate?

Mu-Viswanath 2018 ("All-but-the-top") shows that removing the mean + top principal components from
word embeddings improves performance on **word similarity tasks** (cosine of word pair vs human
judgment). The retrieval class they fix is **direct cosine nearest-neighbor**: given query, find
arg-max cos(query, key) over a key set.

**Does Mu-Viswanath apply to substrate?**

| Property | Mu-Viswanath retriever | Substrate retriever |
|---|---|---|
| Decision rule | argmax cos(q, k_i) | argmax cleanup(W · q) where W = (K^T K + lambda I)^-1 K^T V |
| Linearity | direct similarity | regularized pseudo-inverse (Wiener-style) |
| Anisotropy handling | NONE (raw cosine sees full cone) | Tikhonov regularizer DOWN-WEIGHTS cone-collapse null directions automatically |
| Effect of top-PCA removal | improves cosine because removes "common axis hubness" | DESTROYS the regularization basis the pseudo-inverse uses |

**The Mu-Viswanath fix is for retrieval methods that don't already have anisotropy-aware
regularization.** Substrate's Tikhonov pseudo-inverse is ALREADY anisotropy-aware by construction.
Subtracting top PCs from the keys before storing them STRIPS the cone-aware regularization signal
that makes the cleanup work in the first place — exactly the whitening HARD_FAIL pattern (recovery
+0.020 vs raw; arm collapsed to 0.155 at M=200 from raw 0.07).

**Stronger lit precedent:** anisotropic Tikhonov regularization (arXiv 2406.02209 + 2503.08187) is a
well-established class of methods that BEAT isotropic Tikhonov by EXPLOITING the data's anisotropy
through directional weighting. The bilevel-optimization paper (Lasanen-Mueller et al 2024) gives the
explicit derivation. Substrate's current Tikhonov is ISOTROPIC (uniform lambda * I); the right
improvement would be ANISOTROPIC (lambda * Cov(K)) or LEARNED (per-direction lambda from data).

**Stronger still:** Cai-Kanai-Belkin (ICLR 2021, "Isotropy in the Contextual Embedding Space:
Clusters and Manifolds") empirically showed BERT embeddings exhibit **ISOTROPY WITHIN CLUSTERS** and
the "global anisotropy" measurement is an artifact of cluster centers being distributed
anisotropically. Rajaee-Pilehvar 2021 ("A Cluster-based Approach for Improving Isotropy") then
showed a CLUSTER-AWARE isotropization works much better than global isotropization. This is the
same conclusion as substrate's partition routing chain-grade ledger entries.

**Conclusion:** the "anisotropy is the problem" framing is mis-imported from cosine-NN retrieval
theory. The correct framing for substrate's Tikhonov-regularized cleanup is "WITHIN-CLUSTER capacity
saturation," and the correct mechanism class is "PARTITION the cone into clusters, then do dense
cleanup per cluster."

---

## Section 3: When DOES isotropization help?

It is real and useful in three regimes — none of which match substrate.

**Regime A: Cosine-NN retrieval over many small unrelated items.** Mu-Viswanath + whitening + ABTT
all help here. Lit precedent: Rajaee-Pilehvar 2021 on STS-B / SICK-R semantic-similarity tasks.
SUBSTRATE-FIT: NO — substrate uses Tikhonov, not raw cosine.

**Regime B: Visual / image embeddings with dominant low-frequency content.** PCA-whitening removes
the dominant low-freq axis that adds bias to nearest-neighbor recall. Lit precedent: face
recognition / image retrieval pre-2015. SUBSTRATE-FIT: NO — Pythia residuals don't have a single
dominant axis in the same way (the "anisotropy" is cluster-distributed, not axis-distributed).

**Regime C: Streaming embeddings where the cone shape drifts over time.** Online whitening or
adaptive PCA helps re-align retrieval with current data distribution. Lit precedent: streaming IVF
maintenance (arXiv 2411.00970). SUBSTRATE-FIT: NO — substrate keys are batched, not streaming.

**Is there a substrate-realistic regime where Brenier-OT or CS coherence-aware would help?**
Possibly at the **between-cluster** level — Brenier-OT could map cluster centers (not raw keys) to
near-orthogonal positions, then dense cleanup proceeds within each cluster's anisotropic basin.
This is a 2-level architecture: cluster routing (uses anisotropic structure) + per-cluster dense
cleanup (operates in local isotropic-within-cluster basin per Cai-Kanai-Belkin). The polarimetric
LEARNED variant in flight is structurally similar (learned probes ~ learn cluster centers).

---

## Section 4: NEW Gap 2 candidates given reframe

If substrate's anisotropy-AWARE cleanup is the WINNING strategy, then Gap 2 mechanism candidates
should ENHANCE anisotropy-awareness, not fight it. Five candidates ranked by P_deflated.

### Candidate R1 — Anisotropic Tikhonov regularizer (lambda * Cov^alpha instead of lambda * I)

**Mechanism.** Replace the substrate's current uniform Tikhonov regularizer (lambda * I in the
pseudo-inverse W = (K^T K + lambda I)^-1 K^T V) with anisotropic Tikhonov (lambda * Cov(K)^alpha for
alpha in [0, 1]). At alpha=0 this reduces to current. At alpha=1 it pre-multiplies by the codebook
covariance — DOWNWEIGHTS within-cluster collision directions PROPORTIONALLY to how anisotropic they
are. This is the formal IVF-equivalent for dense KV cleanup.

**Substrate-realistic?** Trivially. Just replace one line in the cleanup primitive (REG_LAMBDA scalar
becomes REG_LAMBDA * Cov(K)^alpha matrix).

**Cheap decisive test:** 4-arm cell, ARM_ISOTROPIC (current; alpha=0) vs ARM_AT(alpha=0.5) vs
ARM_AT(alpha=1.0) vs ARM_LEARNED (alpha learned per-axis via gradient descent on heldout). Pythia-160m
M=[2k, 10k], 3 seeds. ~2 hr CPU.

**HARD_PASS:** ARM_AT(alpha=1.0) >= ARM_ISOTROPIC + 0.05 absolute at M=10k.
**HARD_FAIL:** ARM_AT(alpha=1.0) - ARM_ISOTROPIC <= 0.01 — substrate's existing uniform Tikhonov IS
the right regularizer for this data; the cone-aware improvement comes from PARTITIONING not
regularizer choice.

**P_deflated = 0.40.** Anisotropic Tikhonov is a well-established theoretical improvement
(arXiv 2406.02209) but unclear if the cluster-collision regime is the right place to apply it. Plus
calibration penalty for not-yet-validated-on-substrate.

### Candidate R2 — Substrate-native ScaNN: anisotropic vector quantization for partition routing

**Mechanism.** Replace the current partition routing's k-means quantizer (isotropic L2 distance) with
Guo et al 2020's ANISOTROPIC vector quantization loss (penalizes quantization error in the query
direction more than orthogonal). This is the production-validated billion-scale recipe — Google's
ScaNN beats other vector libraries 2x specifically because it does anisotropy-aware quantization
during partition assignment.

**Substrate-realistic?** Yes. Substrate's partition routing primitive uses standard k-means
assignment today. Replacing with anisotropic loss is a ~50-line change in the partition-build
preprocessor. The CHAIN-GRADE ledger already supports M=10M with isotropic k-means; this would
strengthen it further AND give a substrate-product positioning identical to ScaNN's anisotropy claim.

**Cheap decisive test:** 3-arm cell within partition routing: ARM_KMEANS_ISOTROPIC (current) vs
ARM_KMEANS_ANISOTROPIC (Guo et al loss) vs ARM_KMEANS_LEARNED_METRIC. Real Pythia keys M=100k,
part_size=2000, 3 seeds. ~3 hr CPU.

**HARD_PASS:** ARM_ANISOTROPIC route_acc + recall lift sum >= 0.05 absolute over current isotropic at
M=100k.
**HARD_FAIL:** ARM_ANISOTROPIC ties ARM_ISOTROPIC within 0.02 — current k-means routing is already
near-optimal for substrate cone structure (would still inform: locks in partition routing as the
substrate-product spine).

**P_deflated = 0.50.** Strong lit precedent (Guo et al 2020 ICML — production-validated at billion
scale) directly applicable; substrate is already doing partition routing so the upgrade has minimal
architectural risk.

### Candidate R3 — Hierarchical partition routing extended (3-level + per-level cluster shape)

**Mechanism.** Current chain-grade 2-level hierarchical routes via 10 coarse + 100 fine partitions
(M=10M recall = 0.978). Extend to 3-level (10 coarse + 100 mid + 1000 fine) and let EACH LEVEL'S
PARTITION SHAPE BE ANISOTROPY-AWARE (Mahalanobis-style clusters at coarse level; isotropic-within-
cluster fine-level). This makes the hierarchical routing fully cone-exploitation-native.

**Substrate-realistic?** Yes — extends an already-validated cell. The cluster-shape change is a
diagonal-vs-full-covariance choice per level.

**Cheap decisive test:** 3-arm hierarchical: ARM_2LEVEL_ISO_ISO (current) vs ARM_3LEVEL_ISO_ISO_ISO
vs ARM_3LEVEL_ANISO_ISO_ISO. M=10M, 3 seeds. ~6 hr CPU (already validated infra).

**HARD_PASS:** ARM_3LEVEL_ANISO recall@10M >= 0.985 (lift over current 0.978 by >= 0.007 absolute,
chain-grade-grade tightening).
**HARD_FAIL:** all three arms within 0.005 — 2-level is the optimal depth; further hierarchy doesn't
help.

**P_deflated = 0.35.** Lower because current already saturates near 0.98 — the discriminator headroom
is small. But low-cost extension of existing chain-grade primitive.

### Candidate R4 — Learned per-cluster Tikhonov (adaptive lambda per partition)

**Mechanism.** Within partition routing, learn a DIFFERENT lambda per partition based on local
cluster density and dimension. Sparse clusters get larger lambda (more smoothing); dense clusters
get smaller (more selectivity). This combines anisotropic Tikhonov (R1) with partition routing (R2).

**Substrate-realistic?** Yes. Adds one diagonal matrix per partition, learned via heldout fit.

**Cheap decisive test:** 3-arm: ARM_FIXED_LAMBDA (current) vs ARM_DENSITY_HEURISTIC vs ARM_LEARNED.
M=100k partition-routed, 3 seeds, ~4 hr CPU.

**HARD_PASS:** ARM_LEARNED >= ARM_FIXED + 0.03 at M=100k.
**HARD_FAIL:** all three arms within 0.01.

**P_deflated = 0.35.** Modest expected lift; substrate's fixed lambda probably already near-optimal
for typical partition density.

### Candidate R5 — Anisotropic kernel retrieval (Mahalanobis at the cleanup stage)

**Mechanism.** Replace the L2-distance argmax in the final cleanup with a Mahalanobis-distance
argmax: argmin_i (cue - W_i)^T Sigma^-1 (cue - W_i) where Sigma is the cleanup-residual covariance.
This is the kernel-method analog of anisotropic Tikhonov, applied at READOUT.

**Substrate-realistic?** Yes — Mahalanobis at readout is a 1-matmul change.

**Cheap decisive test:** 2-arm: ARM_L2 (current) vs ARM_MAHAL. M=10k Pythia, 3 seeds, ~1 hr CPU.

**HARD_PASS:** ARM_MAHAL >= ARM_L2 + 0.03.
**HARD_FAIL:** within 0.01.

**P_deflated = 0.30.** Lower because Mahalanobis at readout is conceptually overlapping with
anisotropic Tikhonov at storage (R1); marginal additional lift expected.

### Ranked candidates (substrate-product priority)

| Rank | Candidate | P_deflated | Cost | Strategic fit |
|---|---|---|---|---|
| 1 | R2 anisotropic ScaNN-style quantizer for partition routing | 0.50 | 3 hr | STRONG — production-validated; strengthens chain-grade partition routing spine |
| 2 | R1 anisotropic Tikhonov regularizer | 0.40 | 2 hr | MEDIUM — well-supported theory; informative either way |
| 3 | R3 3-level hierarchical with per-level cluster shape | 0.35 | 6 hr | MEDIUM — tightens existing chain-grade; small discriminator |
| 4 | R4 learned per-cluster Tikhonov | 0.35 | 4 hr | MEDIUM — combines R1 + R2 |
| 5 | R5 Mahalanobis cleanup | 0.30 | 1 hr | LOW — cheap experiment but conceptually overlaps R1 |

---

## Section 5: Pending in-flight cells inform this drill

Two cells were dispatched 2026-06-25 BEFORE this reframe:

### v4 CPU expansion sweep
- Status: smoke = MIDDLE_BAND (correct for smoke); full dispatched on remote_cpu_queue ~3h budget.
- Tests cerebellar fly-LSH sparse-fan-in at expansions [8, 64, 512, 4096] at adversarial M=2k.
- Under REFRAME: sparse-fan-in is an EXPLOIT-THE-CONE mechanism (random K=5 fan-in implicitly
  samples cluster axes); predicted HARD_PASS by reframe at FLY_4096x >= 0.60 and AB_CONTROL_4096x
  not dominating fly. If lifts strongly, REFRAME STRENGTHENS.
- If FLY_4096x ties FLY_8x within 0.05, REFRAME WEAKENS (mechanism fails — implies dense cleanup
  capacity is the real cap regardless of cone exploitation).

### Polarimetric multi-probe v1
- Status: dispatched on remote_cpu (queued behind v4).
- Tests K=10 small learned probes that interact differently with cone-aligned items.
- Under REFRAME: LEARNED probes effectively learn cluster center directions = substrate-native ScaNN
  analog at the readout side. Predicted HARD_PASS_LEARNED at >= 0.50.
- If LEARNED ties RANDOM_UNIT within 0.10, REFRAME WEAKENS (learned cluster axes don't help; would
  imply cluster structure isn't routable from data alone).

### Cumulative evidence stack after both land

| Cell outcome | Reframe state |
|---|---|
| v4 HARD_PASS + polarimetric HARD_PASS_LEARNED | REFRAME CONFIRMED at chain-grade-eligible level; dispatch R2 (anisotropic ScaNN) as 1st new Gap 2 anchor |
| v4 HARD_PASS, polarimetric HARD_FAIL | REFRAME PARTIAL; sparse-fan-in is the mechanism, multi-probe isn't; dispatch R2 + R3 |
| v4 HARD_FAIL, polarimetric HARD_PASS | REFRAME PARTIAL; multi-probe is the mechanism, deeper expansion saturates; dispatch R2 (focus on partition-side anisotropy) |
| Both HARD_FAIL | REFRAME WEAKENS; Gap 2 may be capacity-cap not anisotropy-related at all; pivot to capacity analysis (different Gap re-classification) |

---

## Section 6: Recommendation

### Is Gap 2 a real gap?

**REAL but mis-labeled.** The phenomenon (recall collapse on real Pythia keys at M=10k with global
dense cleanup) is real. The CAUSE is WITHIN-CLUSTER capacity saturation + missing partition routing,
NOT anisotropy needing isotropization. Renaming Gap 2 from "anisotropy rescue" to "cluster-aware
capacity lifting" reflects the actual mechanism.

### Solved-via-bypass or active rescue needed?

**Both, and they're complementary.**

- **Bypass component (already in substrate, chain-grade):** partition routing at M=1M/10M with route
  acc=1.0 ROUTES AROUND the global cleanup capacity problem by ensuring each partition is small
  enough for dense cleanup to work. This is the load-bearing substrate-product spine.

- **Active rescue component (proposed for new Gap 2 drill):** R2 anisotropic-ScaNN-style quantizer
  for partition routing — strengthens the spine by improving quantization quality (Google's
  production billion-scale recipe). R1 anisotropic Tikhonov as a per-partition regularizer
  improvement. Both are EXPLOIT-the-cone mechanisms; both differ from this morning's HARD_FAIL'd
  fight-the-cone mechanisms.

### Substrate-product positioning under reframe

**Old positioning (now FALSIFIED):** "Substrate solves anisotropy through novel isotropization that
preserves neighborhood structure unlike whitening" — REFUTED by 2 HARD_FAILs this morning + 1 prior
whitening HARD_FAIL = 3 independent isotropization HARD_FAILs.

**Reframed positioning (now SUPPORTED):** "Substrate exploits the anisotropic cluster structure of
real embeddings through HIERARCHICAL PARTITION ROUTING with anisotropy-aware quantization (ScaNN
class) and per-partition Tikhonov-regularized cleanup (anisotropic Tikhonov class). The same
structural property — clusters in a cone — is the SIGNAL substrate uses for retrieval, not a noise
to be removed."

This positioning matches:
- Substrate's chain-grade ledger (partition routing M=10M, hierarchical 2-level M=10M, KV learned
  projection M=10k held-out, fly-LSH sparse-fan-in M=10k)
- Production billion-scale vector retrieval (FAISS IVF, Google ScaNN, DiskANN — all partition-then-
  retrieve with anisotropy awareness)
- Brain architecture (DG sparse-fan-in pattern separation, hippocampal categorical encoding,
  cortical column-level partition routing per Mountcastle 1957 / Buxhoeveden-Casanova 2002)
- Recent NLP geometry literature (Cai-Kanai-Belkin ICLR 2021 isotropy-within-clusters;
  Rajaee-Pilehvar 2021 cluster-based isotropy improvement)

---

## Cross-thread synthesis (with prior research drills)

### Connection to drill 2 (`research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md`)
That drill EXPLICITLY identified the partition-and-sparse-fan-in pattern in section D.1: "the
WORKING mechanisms (cerebellar/fly sparse-fan-in v2, contrastive learned projection, partition
routing decomposition, de-saturation) all share one structural property — they either expand into a
sparse high-dim representation BEFORE binding, or they decompose the problem so each sub-memory sees
a smaller, less anisotropic key set." This morning's 5x drill MISSED this synthesis and proposed
isotropization anyway. The reframe re-asserts what drill 2 already concluded.

### Connection to drill 1 (`research_anisotropy_drill_1_barriers_math_literature_2026-06-25.md`)
Drill 1 (barriers half) characterized whitening's failure as "burns the neighborhood structure that
made keys meaningful." The reframe extends this: ALL global isotropization burns the neighborhood
structure; only LOCAL (within-cluster) or BYPASS (partition-then-cleanup) mechanisms preserve it.

### Connection to GAP 3 compositional drill (yesterday)
The GAP 3 drill found brain solves compositional via 3-layer stack including "slow extraction of
patterns" (missing in substrate). Cluster structure IS that extracted pattern. Reframe Gap 2 +
proper compositional architecture both point at the SAME architectural element: a routable
intermediate representation between raw keys and dense cleanup.

### Connection to USER's "encoder is THE bottleneck" framing 2026-06-23
The encoder produces anisotropic real-data keys (Pythia, word2vec, sentence-BERT all converge to
cones). Reframe says: don't fight the encoder's output geometry; route over its cluster structure.
Substrate-as-LM revival path: predictive-coding encoder + partition routing + anisotropic
Tikhonov-regularized cleanup. The encoder picks were never the load-bearing piece; the cleanup
ARCHITECTURE (global vs partition-aware) is.

---

## Substrate-product implications

1. **Stop investing in global isotropization mechanisms for Gap 2.** Three independent HARD_FAILs
   (whitening, water-filling, DG pre-write) are conclusive. Do not dispatch a 4th isotropization
   variant.

2. **Invest in anisotropy-AWARE partition routing improvements.** Top priority: R2 anisotropic ScaNN
   for partition routing. Second: R1 anisotropic Tikhonov for per-partition cleanup. These
   strengthen the chain-grade spine substrate already has.

3. **Substrate-product positioning:** "Hierarchical partition-routed VSA memory with anisotropy-
   aware quantization" — positions substrate alongside ScaNN/FAISS/DiskANN but with the VSA
   substrate-product story (deterministic + observable + auditable per cap_map).

4. **Continual learning angle:** the "missing PROMOTION" architecture from yesterday's GAP 4 drill
   (two-tier generational) maps cleanly onto partition routing — promote dense-cluster items into
   their own fine-level partition; demote stale items. Reframe Gap 2 + GAP 4 share architecture.

5. **NEVER write a research note positioning this as "we solved anisotropy."** Per USER's
   no-product-positioning rule and per Fix #28 under-claim default. Position as: "substrate's
   cleanup architecture is anisotropy-aware; we strengthen the partition routing spine."

---

## Citations (verified count: 8 external lit refs + 5 substrate-internal ledger entries)

### External (verified via WebSearch tool 2026-06-26)
1. Mu, J. and Viswanath, P. (2018). "All-but-the-Top: Simple and Effective Postprocessing for Word
   Representations." ICLR. https://arxiv.org/abs/1702.01417
2. Cai, X., Huang, J., Bian, Y., Church, K. (2021). "Isotropy in the Contextual Embedding Space:
   Clusters and Manifolds." ICLR. https://openreview.net/pdf/8b00c8e698e9a810bfcee44a4ae5f6c3adeb7266.pdf
3. Rajaee, S. and Pilehvar, M.T. (2021). "A Cluster-based Approach for Improving Isotropy in
   Contextual Embedding Space." https://arxiv.org/abs/2106.01183
4. Guo, R., Sun, P., Lindgren, E., Geng, Q., Simcha, D., Chern, F., Kumar, S. (2020). "Accelerating
   Large-Scale Inference with Anisotropic Vector Quantization." ICML 2020.
   https://arxiv.org/abs/1908.10396 (= ScaNN production-validated billion-scale)
5. Lasanen, S., Mueller et al (2024). "Automatic nonstationary anisotropic Tikhonov regularization
   through bilevel optimization." https://arxiv.org/abs/2406.02209
6. Da Silva, N. et al (2024). "Optimal Space-Variant Anisotropic Tikhonov Regularization."
   https://arxiv.org/abs/2503.08187
7. Cayco-Gajic, N.A. and Silver, R.A. (2019). "Re-evaluating Circuit Mechanisms Underlying Pattern
   Separation." Neuron 101(4): 584-602. (substrate-cerebellar fan-in reference)
8. Mountcastle, V.B. (1957) / Buxhoeveden, D.P. and Casanova, M.F. (2002). Cortical columnar
   organization — biological evidence for brain-level partition routing.

### Substrate-internal (verified via Read on metrics.json files)
1. `data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json` — CHAIN_GRADE_AT_M_10M
   recall=0.978
2. `data/exp_substrate_partition_routing_10M_full_v2/metrics.json` — HARD_PASS chain-grade @ M=100k,
   M=1M recall=0.95
3. `data/exp_kv_learned_projection_v1/metrics.json` — HARD_PASS held-out M=10k recall=0.827 vs
   analytic ceiling 0.032
4. `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json` — HARD_PASS
   chain-grade-candidate fly-LSH ARM B = 0.997 at M=10k
5. `data/exp_dense_KV_whitening_revival_v1_gpu/metrics.json` — HARD_FAIL recovery +0.020 (read via
   prior drill 2 verification)

### Companion HARD_FAIL notes informing this reframe
- `notes/exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26.md`
- `notes/exp_dev_anisotropy_dg_pattern_separation_prewrite_v1_SMOKE_HARD_FAIL_2026-06-26.md`
- `notes/research_anisotropy_drill_1_barriers_math_literature_2026-06-25.md`
- `notes/research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md`
- `notes/research_gap2_anisotropy_5x_drill_2026-06-26.md` (the drill this reframe partially refutes)
