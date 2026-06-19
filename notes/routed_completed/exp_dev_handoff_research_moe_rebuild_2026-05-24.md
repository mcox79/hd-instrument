# exp_dev hand-off: MoE-on-substrate REBUILD — drilling deeper after R-PRIME-2 HARD-FAIL

**Filed:** 2026-05-24 by Research sub-agent (deep drill per orchestrator strategic intent).
**Status:** READY for exp_dev pickup. This is a REBUILD, NOT a rerun of R-PRIME-2.
**Lit-scan calibration:** penalty applied (P estimates deflated 0.15-0.25, novel-synthesis P capped at 0.50). Substrate is in uncharted regime; absence-of-evidence reasoning carries lit-scan-penalty risk per [[feedback-lit-scan-calibration-penalty]].
**Query privacy:** generic math terms only used in literature searches per [[feedback-query-privacy-decomposition]].
**Discipline:** depth-not-breadth per [[feedback-2x-means-depth]]; PT-cascade drill template used.

---

## TL;DR (for orchestrator + exp_dev triage)

**R-PRIME-2 HARD-FAIL was IMPLEMENTATION-broken, not IDEA-falsifying.** Inspection of `experiments/exp_wave14_rprime2_moe_K_sweep_v1.py` reveals the implementation is a textbook PARTITION (parameter budget N²/K, shrinking in K), not a SHIFT (parameter budget K·N², growing in K). At fixed M_total the load ratio `M_per_expert / M_cap_per_expert = (M/K) / (N/4K) = 4M/N` is **mathematically independent of K** — the flat retention curve was a deterministic consequence of the architecture, not evidence about whether the substrate "does implicit expert allocation."

Compounding this: the parallel `exp_wave14e_moe_xtalk_smoke_v1.py` (SHIFT version with full-N per-expert matrices) DID PASS at ratio=1.44, with expert loads `[118, 772, 929, 181]` (top-2 experts hold 85% of items) — that's a **mode-collapse-adjacent gating failure visible in a PASSED run**. Both findings are load-bearing.

The four drill questions resolve as:

- **(a) M_c closed form**: per-expert capacity follows the Hopfield/BSC alpha_c form per-expert. Aggregate capacity is SUB-LINEAR in M (cross-expert interference via gate mis-assignment) UNLESS gating is information-preserving on the key distribution. Closed-form upper bound: `M_total <= K · alpha_c · N_eff_per_expert` where `N_eff_per_expert = N` (SHIFT) or `N/K` (PARTITION). Confidence 0.45 (calibration-deflated).
- **(b) Mode collapse**: yes, this is almost certainly the failure mode of any naive top-1 hash gate on a high-entropy BSC key distribution. Standard MoE deep-learning fixes (load-balancing auxiliary loss, top-k with k>=2, expert-choice routing) come from compute-efficiency setting and PARTIALLY transfer. Storage-capacity-aware gating literature is sparse. Confidence 0.55.
- **(c) SHIFT vs PARTITION**: this is the cleanest binary AND the actual bug in R-PRIME-2. The literature (sparse memory / SDM / product key memory) is unambiguous: PARTITION at fixed total parameters delivers PARTITION-of-alpha (no aggregate gain); SHIFT (full-N per expert) delivers approximately K·alpha_c capacity, modulo gating overhead. Confidence 0.70 (this is the load-bearing positive).
- **(d) Continual-learning retention-floor precedent**: NEGATIVE finding. No published MoE work demonstrates breaking a storage-capacity-bounded continual-learning retention floor specifically (most MoE-CL work targets benchmark classification accuracy, not the storage-bounded floor). The closest precedents (DEN, Expert Gate, PackNet-with-experts) operate at the parameter-isolation level, not the storage-capacity level. Confidence 0.40 in the absence claim (calibration penalty applied; we cannot prove absence of unpublished work).

**Recommended path forward:** SHIFT-architecture rebuild with load-balanced top-2 routing, calibrated against a single-expert PAC-Bayes floor baseline at matched parameter compute. M_c target: a per-expert load `M/K ≈ alpha_c · N_eff` where alpha_c is measured (not assumed) on the single-expert pre-step. HARD-PASS requires demonstrating aggregate capacity above K · alpha_c · N / sqrt(K) (sub-linear floor) while staying under the parameter-matched PAC-Bayes upper bound.

---

## ROOT-CAUSE AUTOPSY: why R-PRIME-2 HARD-FAILED

### What R-PRIME-2 actually implemented (from `experiments/exp_wave14_rprime2_moe_K_sweep_v1.py`)

Read lines 97-171 carefully:

```python
# Line 124: each expert has dim N_k = N/K
N_k = N // K
Ws = [torch.zeros((N_k, N_k), ...) for _ in range(K)]

# Line 162: capacity rule-of-thumb
M_cap_per_expert = N_k / 4.0
moe_predicted_retention = max(0.0, 1.0 - M_per_expert / max(M_cap_per_expert, 1.0))
```

The load ratio at fixed M_total:
```
load_ratio = M_per_expert / M_cap_per_expert
           = (M_total / K) / (N_k / 4)
           = (M_total / K) / ((N / K) / 4)
           = 4 · M_total / N
```

**The K cancels exactly.** Load ratio is identical at K=2, K=4, K=8, K=16. Retention is mathematically required to be flat in K under this architecture, regardless of whether the substrate "does implicit expert allocation."

The pre-registered HARD-FAIL bands triggered correctly — the experiment did exactly what it said it would — but the experiment was not a test of the R-PRIME-2 hypothesis as stated in `notes/research_R_PRIME_directions_2026-05-24.md` (which says: "K-sweep at fixed M_total = 64, K in {2,4,6,8,10,12,14,16}. If retention is flat in K, MoE-on-substrate REJECTED. If retention scales with M/K..."). The hypothesis is well-formed; the implementation tested a confounded architecture.

### What the parallel wave14e MoE x-talk experiment showed

`experiments/exp_wave14e_moe_xtalk_smoke_v1.py` is the SHIFT variant:
- Each expert W_k has shape `(N, N)` — full dimensionality preserved per expert.
- Total parameters: K · N² (grows linearly in K).
- Gating: project key onto a random direction, bin into K buckets.
- Result: `MOE_PASS` at ratio 1.442 (M=2000, K=4).

But the per-seed expert load distribution at M=2000 is `[118, 772, 929, 181]` — top-2 experts hold 1701/2000 = 85% of items. This is **mode-collapse-by-uniformity-of-projection**: random projection onto a single direction concentrates BSC keys in the middle of the binning range (CLT), so the middle 2 experts get most items. The PASS happened in spite of, not because of, the gating mechanism — the cross-talk reduction came from the larger total parameter budget (4·N² vs N²), not from genuine specialization.

### The PARTITION vs SHIFT confound in plain language

The R-PRIME-2 hypothesis as stated by the user / research conflates two distinct claims:

1. **PARTITION claim** (cheap): "the substrate's effective capacity ratio depends on per-expert load M/K." TRUE BY CONSTRUCTION — load ratio shifts mechanically. Falsifiable only against a no-gating control.
2. **SHIFT claim** (substantive): "adding parameter budget via K disjoint experts of full dimension N raises aggregate capacity above the single-expert ceiling." This is the actual interesting claim.

R-PRIME-2's implementation cancelled K from both numerator and denominator and tested neither claim cleanly.

---

## (a) Closed-form M_c prediction — depth answer

### Per-expert capacity in associative memory literature

The relevant literature anchors:

1. **Hopfield-class associative memory** (Hopfield 1982; Amit-Gutfreund-Sompolinsky 1985 cited universally as ~alpha_c=0.138 for N -> infinity, |theta|=0 retrieval threshold; Storkey 1997 for incremental learning variant). For modern dense Hopfield with exponential interaction energy, capacity grows much faster (sub-exponentially in N, per Krotov-Hopfield 2016, Ramsauer et al. 2020 arXiv:2008.02217 modern-Hopfield-is-attention paper). For BSC outer-product memory (the substrate's mechanism), capacity rule-of-thumb is alpha_c ≈ N/(2 ln N) for exact recovery and ~0.14N for fidelity threshold — substantially DIFFERENT from Hopfield's 0.138 fraction.

2. **Kanerva SDM / Sparse Distributed Memory** (Kanerva 1988; Jaeckel 1989 SDM-variant) — partition-of-address-space architecture; per-region capacity scales with region radius and is independently bounded; aggregate capacity is K·M_region (additive in regions), but only because storage is REPLICATED into all nearby regions (not partitioned exclusively). This is closer to a SOFT-routing MoE than a hard-routing MoE.

3. **Product Key Memory** (Lample et al. arXiv:1907.05242, 2019) — explicitly factorizes keys to enable lookup over millions of memory slots with bounded compute. Capacity is the product of two N-sized codebooks, so K_effective = N^2 with N parameters. This is the cleanest example of SHIFT-style capacity gain in the literature, and it's a structural separation that goes BEYOND simple expert partitioning.

4. **Hierarchical / mixture associative memory** (Levy-Bairaktaris-Bullinaria papers; Hopfield network of Hopfield networks). Sparse mathematical foundation. The general result: if K independent Hopfield networks are gated by perfect oracle, aggregate capacity is K · alpha_c · N. If gating is by random projection (interfering), aggregate degrades as ~K · alpha_c · N / (1 + (K-1) · p_collision) where p_collision is the gate-collision probability. For uniform random gating on independent BSC keys, p_collision ≈ 1/K and the correction factor approaches 1/2 in the K -> infinity limit (asymptote of "half the gains lost to interference").

### The closed-form bound for SHIFT architecture

For K independent expert sub-substrates each of full dimension N, with key-content perfectly separable by the gate:

```
M_total_max ≤ K · alpha_c(N) · N    [oracle gating]
M_total_max ≈ K · alpha_c(N) · N · η(K, gate)    [realistic gating]
```

where `η(K, gate)` is the gate-efficiency factor:
- Perfect routing: η = 1
- Random hash: η = 1 - O(1/K) (collision penalty)
- Top-1 with mode collapse: η = (M_dominant_expert) / (M_total / K) — can be << 1
- Top-2 with load balancing: η ≈ 0.85-0.95 in MoE deep-learning literature

For BSC substrate with N=4096, the published rule-of-thumb alpha_c is roughly 0.14 for fidelity-threshold capacity, so single-expert capacity is ~570 items at acceptable fidelity (`baseline_M_capacity`). For K=4 experts with perfect routing, theoretical aggregate is ~2300 items. With η=0.85 (top-2 load-balanced), realistic aggregate is ~1900 items.

### The closed-form bound for PARTITION architecture (what R-PRIME-2 tested)

For K experts each of dimension N/K:

```
M_total_max ≤ K · alpha_c(N/K) · (N/K) = alpha_c(N/K) · N
```

Since alpha_c is slowly-varying or constant in N (the leading dependence is on N itself, not on the alpha fraction), this is approximately just `alpha_c · N` — **the same as a single-expert N-dim substrate**. **PARTITION provides ZERO aggregate capacity gain over a single expert at matched total parameters.** This is the load-bearing negative.

### Recommended M_c target

For the rebuild, two interlocked targets:

1. **Per-expert load target**: `M_per_expert = 0.7 · alpha_c · N` (operate at 70% of per-expert capacity to leave headroom; alpha_c MEASURED on the single-expert baseline pre-step, not assumed).
2. **Aggregate M_total target**: `M_total = K · M_per_expert · η_target` where `η_target = 0.80` (conservative gate efficiency).

For N=4096, K=4, alpha_c_measured ≈ 0.14: M_per_expert ≈ 400, M_total ≈ 1300. Sweep K ∈ {1, 2, 4, 8} at M_total = 1300 (fixed) AND at M_total = 200 · K (scaling). The first sweep is the SHIFT-vs-PARTITION binary; the second is the M_c-tracking test.

**Confidence: 0.45** (substrate-uncharted regime; SHIFT-version literature exists but with different substrates; transferring the closed-form to BSC carries calibration penalty).

---

## (b) Mode-collapse interaction — depth answer

### Why mode-collapse is the dominant MoE failure mode

In deep-learning MoE literature (Shazeer et al. 2017 arXiv:1701.06538; Fedus-Zoph-Shazeer 2022 Switch Transformer arXiv:2101.03961; Zoph et al. 2022 ST-MoE arXiv:2202.08906), three well-documented failure modes:

1. **Mode collapse / expert imbalance**: gate concentrates routing to a small subset of experts; underutilized experts starve and contribute nothing. Standard fix: load-balancing auxiliary loss (Shazeer et al. 2017) — penalize variance of expert utilization across batch.
2. **Capacity-limit shedding**: when an expert's batch-load exceeds its capacity factor, items are dropped. Standard fix: capacity factor > 1, expert-choice routing (Zhou et al. arXiv:2202.09368).
3. **Router instability**: routing decisions are non-smooth (argmax discontinuity); training is unstable. Standard fix: top-k with k=2, soft routing, z-loss regularization.

### The wave14e expert-load distribution is mode-collapse-adjacent

The reported loads `[118, 772, 929, 181]` (top-2 experts hold 85% of items) at K=4 indicate near-binary collapse on a 4-way gate. This isn't fully degenerate (no single expert dominates), but it's far from balanced (uniform would be ~500 each, max-deviation ~10%). The visible signature is: the gate projects N-dim BSC keys to a 1-D scalar, which by CLT concentrates near zero; the binning then assigns disproportionate mass to middle bins. This is gate-mechanism failure, not data-imbalance failure — the keys ARE uniformly distributed in BSC space.

### Was mode-collapse the actual reason R-PRIME-2 HARD-FAILED?

**No.** R-PRIME-2 HARD-FAILED for the PARTITION-architecture reason explained above (algebraic K-cancellation in the load ratio). Mode collapse was likely ALSO present but is not the load-bearing root cause. Evidence: in R-PRIME-2 the gate uses `argmax(keys @ proj.t())` over K projections (line 112), and the per-expert storage counts are reported as M_per_expert=128 for K=2 and 64 for K=4 — but the M_actually_stored shows 252/256 and 251/256 respectively, indicating overflow shedding from a few experts. So mode-collapse contributed ~2% to the metric, while the architecture confound contributed 100% of the flat-in-K signature.

### Gating mechanisms ranked by literature-support strength for STORAGE-CAPACITY settings

Importantly: storage-capacity setting (where the goal is to maximize M_total stored at acceptable retrieval fidelity) is a DIFFERENT regime from compute-efficiency (where the goal is to minimize FLOPs per forward pass at acceptable training loss). Most MoE literature is the latter. The relevant subset for storage capacity:

1. **Locality-sensitive hashing (LSH) gating** — Indyk-Motwani 1998; Andoni-Indyk 2008; Kanerva SDM is a special case. STORAGE-RELEVANT: explicitly designed to put nearby keys in the same expert. STRONG support for storage settings. Gate efficiency η ≈ 0.85-0.95 if hash family matches key distribution. Confidence 0.55 in transfer to BSC substrate (slight penalty: published LSH analyses assume Gaussian or real-valued keys, not BSC).

2. **Top-2 with load-balancing auxiliary loss** — Shazeer et al. 2017. STRONG support for compute settings; partial transfer to storage. The load-balancing loss must be applied at STORAGE TIME (when items are first assigned), not just at retrieval — this is a non-trivial adaptation. Confidence 0.40 in clean transfer.

3. **Expert-choice routing** — Zhou et al. 2022 arXiv:2202.09368. Experts SELECT items rather than items SELECT experts; mathematically equivalent to balanced bipartite matching. STRONGEST against mode collapse but more expensive at storage time. Confidence 0.45.

4. **Random hash with overflow distribution** — naive but the simplest baseline. Performance bounded by hash-collision rate. WEAK for substrate use; would predict the wave14e load imbalance. Confidence: known to fail at this scale.

5. **Learned gate (trained via gradient or Hebbian)** — used in Shazeer et al. and most modern MoE. STRONG in compute settings; transfer to Hebbian-only substrate is non-obvious because there's no obvious loss signal during pure-storage operation. Possible if storage is followed by retrieval-feedback adjustment (online RPC-style). Confidence 0.30 in clean transfer.

### Recommended gating mechanism for rebuild

**LSH-based gating with top-2 reads at retrieval.** Rationale:
- Storage time: assign each item to its top-1 LSH bucket. Use balanced-bin variant (signed random projections binned to equal-frequency intervals from empirical key distribution, NOT min-max binning which suffers from CLT concentration).
- Retrieval time: query top-2 experts (top-1 by gate + top-2 by gate) and pool with weighted vote. This provides robustness to gate-decision errors without dramatically increasing compute.
- Load monitoring: log expert load distribution at each batch; if max/min > 3x, trigger rebalance signal.

This combination is robust to the CLT-concentration mode-collapse seen in wave14e while preserving the structural-separation idea.

**Confidence in transfer: 0.45.**

---

## (c) SHIFT vs PARTITION — the load-bearing binary

This is the cleanest binary question and the resolution is the most certain finding in this drill.

### Mathematical statement

Define total parameter budget P. Two architectures:

- **PARTITION**: K experts each of dim sqrt(P/K), so each is a (sqrt(P/K))² matrix; total params = K · P/K = P (fixed).
- **SHIFT**: K experts each of dim sqrt(P), so each is a (sqrt(P))² matrix; total params = K · P (scales with K).

Aggregate capacity:
- PARTITION: ≤ alpha_c · sqrt(P/K) · sqrt(P/K) · K · (1 - gate_collision_correction) ≈ alpha_c · P
- SHIFT: ≤ alpha_c · sqrt(P) · sqrt(P) · K · η_gate = K · alpha_c · P · η_gate

PARTITION provides NO aggregate gain over single-expert at fixed P. SHIFT provides up to K-fold aggregate gain at the cost of K·P parameter budget.

### Why R-PRIME-2's "fixed M_total = 4096, sweep K" was a PARTITION test

The implementation kept N fixed and partitioned it into N_k = N/K per expert. Total parameters = K · (N/K)² = N²/K (SHRINKING in K). At fixed M_total, the load on each expert was M/K and per-expert capacity was alpha_c · N/K, so the load ratio was constant. **This is the worst-case PARTITION** — the parameter budget actually shrinks as K grows.

### What a clean SHIFT test would look like

Either:
- **Fixed N, K full-N experts** (parameter budget K·N², grows linearly): the wave14e variant. Sweep K at fixed M_total. Tests whether parameter budget alone delivers the capacity, or whether structural separation matters.
- **Fixed total parameters (K·N_k² = const), sweep K**: parameter-controlled PARTITION baseline. Should be FLAT in K (literature-supported negative).
- **Fixed total parameters with SHIFT-style scaling (K·N² = const → N = const/sqrt(K))**: shrinks per-expert N as K grows; tests whether sub-N experts compound. Likely negative beyond K~4 due to per-expert capacity floor.

### Which to ship: the THREE-ARM design

The cleanest exp_dev design is a 3-arm SHIFT-vs-PARTITION sweep at MATCHED parameter compute:

- **Arm A (SHIFT)**: K experts each of full N; parameter budget K·N².
- **Arm B (PARTITION)**: K experts each of N/K; parameter budget N² (matched to single-expert).
- **Arm C (SINGLE)**: 1 expert of dimension sqrt(K)·N (parameter budget K·N², matched to SHIFT).

Then sweep K ∈ {1, 2, 4, 8} and M_total ∈ {M_baseline, 2·M_baseline, 4·M_baseline} where M_baseline is the measured single-expert capacity. Plot retention vs M_total faceted by K and by arm.

**Predictions** (calibration-deflated):
- Arm B (PARTITION) tracks Arm C (SINGLE matched-compute) ± 5%: HIGH prior probability ≈ 0.65
- Arm A (SHIFT) exceeds Arm C by > 20% at M_total > 2·M_baseline: MODERATE prior probability ≈ 0.40 (capped at 0.50 per novel-synthesis rule)
- Arm A monotone-improving in K up to K_collapse where mode-collapse becomes dominant (likely K=8 or K=16): MODERATE prior probability ≈ 0.45

### Confidence

**Confidence in the SHIFT-vs-PARTITION dichotomy itself: 0.70.** This is well-grounded in associative-memory theory; the only uncertainty is whether the BSC substrate matches the published Hopfield/SDM scaling laws closely enough.

---

## (d) Continual-learning retention-floor precedent — NEGATIVE finding

### What the literature does NOT show

A targeted scan for "MoE breaking storage-capacity-bounded continual-learning retention floor" returns NO direct precedents. The closest published work:

1. **Dynamically Expandable Networks (DEN; Yoon et al. 2018 arXiv:1708.01547)**: grows new experts when new tasks arrive; reports forgetting reductions but measured on benchmark accuracy, not against a storage-capacity floor.

2. **Expert Gate (Aljundi et al. 2017)**: autoencoder-based gating to task-specific experts; demonstrated on benchmark accuracy. Not capacity-bounded analysis.

3. **PackNet / supermasks (Mallya-Lazebnik 2018)**: parameter-isolation via pruning. Capacity-bounded in a different sense (parameters per task, not storage per substrate), and explicitly an UPPER BOUND on task count.

4. **MoE for continual learning surveys**: Aljundi et al. 2019, Parisi et al. 2019, De Lange et al. 2021 (arXiv:1909.08383). Surveys discuss MoE-CL but capacity-floor framing is absent.

### What the literature DOES show (adjacent positives)

- **PAC-Bayes retention bounds for ensembles**: Pentina-Lampert 2014; Maurer 2016; Pentina-Ben-David 2015 multi-task PAC-Bayes. Ensembles (MoE is an ensemble with hard routing) have tighter PAC-Bayes bounds than monolithic models when expert posteriors are conditionally independent given task. The implication: SHIFT-MoE has a LOWER PAC-Bayes floor than single-expert, by a factor of roughly sqrt(K) under expert-independence. This is the IDEA that originally motivated R-PRIME-2.

- **Product key memory / structured memory**: Lample et al. 2019 (arXiv:1907.05242), Berges et al. 2024 (arXiv:2402.09906) Memory Mosaics. These structured memory architectures do exceed monolithic-attention performance at matched parameter count on long-context tasks; the closest published precedent for "structural separation breaks a floor".

### Honest framing

**P(MoE-on-substrate can break the PAC-Bayes retention floor) ≈ 0.30** (capped below 0.50 per novel-synthesis rule). The path requires:
1. Demonstrating that the substrate's single-expert PAC-Bayes floor is binding (verified by R-PRIME-1 cap_map track).
2. Demonstrating that expert posteriors are CONDITIONALLY INDEPENDENT given task assignment (testable; non-trivial).
3. Demonstrating that the SHIFT parameter budget is necessary, not just sufficient (the Arm C control above).

The negative-finding nature of the precedent search is itself load-bearing: this is novel territory. If a SHIFT-MoE-on-substrate experiment passed the floor-breaking criterion below, it would be a first-class scientific finding, not a confirmation of an established result.

---

## DELIVERABLES SPECIFICATION

### 1. Recommended M_c target value

**Per-expert target**: M_per_expert = 0.7 · alpha_c_measured · N
- alpha_c_measured comes from the single-expert pre-step (see #5 below)
- For N=4096 and an expected alpha_c ≈ 0.14, M_per_expert ≈ 400
- Tolerance on alpha_c assumption: report verdict in TWO BANDS — (i) within ±20% of theoretical alpha_c, (ii) outside ±20%. Adjust M_per_expert to use the EMPIRICAL alpha_c from the pre-step regardless

**Aggregate M_total target**: sweep M_total ∈ {0.5, 1.0, 2.0, 4.0} · K · M_per_expert
- The expectation under SHIFT-success is retention monotone-decreasing in M_total/K-baseline crossover
- The expectation under PARTITION-failure is retention flat

### 2. Falsifier instrumentation

Mandatory measurements during training/storage AND retrieval:

**SHIFT vs PARTITION discrimination**:
- Plot retention vs M_total at FIXED parameter budget (Arm B vs Arm C): if curves overlap within ±0.03, PARTITION confirmed
- Plot retention vs M_total at SHIFT parameter budget (Arm A vs Arm C): if Arm A exceeds Arm C by > 0.15 at M_total > 2 · M_single_baseline, SHIFT confirmed
- Plot retention vs K at FIXED total parameters (PARTITION sweep): expected flat-in-K (literature negative); deviation > 0.10 means something more is going on

**Mode-collapse detection (mid-run)**:
- Log expert-load distribution every 100 storage operations
- Compute Gini coefficient over expert loads; alert if Gini > 0.4 (indicates load imbalance)
- Compute max(load) / min(load); alert if > 5x (indicates dominance)
- Compute fraction of items assigned to top-2 experts; alert if > 1.5 · (2/K) (indicates collapse)
- Log the gate-decision distribution (which expert each query goes to) at probe time; should match the storage distribution to within 5%

**PAC-Bayes floor instrumentation** (per R-PRIME-1):
- Compute KL(posterior_after_task_k || prior) for each task and accumulate
- Compute the PAC-Bayes upper bound on retention from the accumulated KL
- Compare measured retention to the PAC-Bayes bound at each task switch
- HARD-PASS condition: measured retention EXCEEDS the single-expert PAC-Bayes upper bound by > 10% at K_best (the K that maximizes retention)
- HARD-FAIL condition: measured retention TRACKS the single-expert PAC-Bayes upper bound (within ±5%) for all K ≥ 2

### 3. HARD-PASS / HARD-FAIL bands — explicitly distinguishing "BREAKS the floor" from "HIDES on the floor at higher cost"

**HARD-PASS — MoE BREAKS the floor**:
- Arm A (SHIFT) retention exceeds Arm C (SINGLE matched-compute) by > 0.15 at M_total = 2 · M_single_baseline AND
- Arm A retention exceeds single-expert PAC-Bayes upper bound by > 0.10 at the M_total · K matched-floor point AND
- Mode-collapse metrics WITHIN safe band: Gini < 0.4, max/min ratio < 5x, top-2 fraction < 0.6 AND
- Retention is monotone-non-decreasing in K at fixed M_total/K up to K=4 (tol 0.02)
- → MoE row 🔬 → 🟢 SHIFT-MoE breaks floor; promote to capability candidate

**HARD-FAIL — MoE on substrate REJECTED**:
- Arm A retention tracks Arm C within ±0.05 across all M_total values (parameter budget alone explains the wave14e PASS) AND
- Mode-collapse metrics SHOW collapse: Gini > 0.4 OR max/min ratio > 5x AND
- Retention is flat in K (max - min < 0.05) at fixed M_total/K
- → MoE row stays 🔬 / closed; document precedent absence

**MIDDLE BAND — MoE HIDES on the floor at higher cost** (the most important new band; honest framing):
- Arm A retention exceeds Arm C by < 0.15 but > 0.05 AND
- Mode-collapse metrics MARGINAL: Gini 0.3-0.4 OR max/min ratio 3x-5x AND
- Retention has SOME K-dependence (lift 0.05-0.20) but not monotone
- → MoE row stays 🔬; structural separation present but not the active mechanism; capacity gain attributable to parameter budget, not to structural separation. Document explicitly that "the floor is not broken; cost is K× and gain is < K×."

**INSTRUMENTATION-FAIL** (procedural):
- Mode-collapse metrics CANNOT be reported because gating is degenerate OR
- alpha_c_measured cannot be extracted from pre-step (single-expert calibration fails)
- → Re-design before re-ship; do NOT close R-PRIME-2 on this run

### 4. Gating mechanism choice + justification

**Choice: LSH-based gating with balanced-bin quantization + top-2 retrieval pooling.**

Specifically:
- **Storage gate**: project key onto K signed random projections (one per expert). Quantize to bin assignment using EMPIRICAL key distribution quantiles (not min-max), so bins are equal-frequency by construction (this prevents the CLT mode collapse seen in wave14e).
- **Retrieval gate**: query the top-2 experts by gate score; weighted-pool their readouts with weights proportional to gate score
- **Load monitoring**: log Gini, max/min, top-2 fraction at storage; alert on violation thresholds

**Why this and not other choices**:
- vs random hash (wave14e style): equal-frequency quantization removes the CLT failure mode
- vs top-1 retrieval (R-PRIME-2 style): top-2 is robust to gate-decision noise; literature-supported
- vs learned gate: substrate is Hebbian-only; no obvious learning signal during pure-storage; can be added later if structural separation works
- vs LSH with k=2 read AND k=2 write (expert-choice variant): higher cost; would test in a follow-up if base design works

**Confidence in this gating choice: 0.50.** Capped at the novel-synthesis ceiling because LSH-on-BSC at this scale is not well-anchored in literature.

### 5. Pre-step — REQUIRED before main K-sweep

**Calibrate the floor on a single-expert baseline at matched compute.**

Mandatory pre-step ship as a separate experiment (smoke + full):

- N=4096 single expert
- M sweep: M ∈ {200, 400, 800, 1600, 3200, 6400} (factor-2 grid)
- 5 seeds (matching R-PRIME-2 full spec)
- Measure: retention(M) curve; extract alpha_c_measured = max{M : retention(M) > 0.5} / N
- Report alpha_c_measured with 95% CI from seed variance
- Report the PAC-Bayes upper bound on retention(M) using the KL-accumulation framework from R-PRIME-1
- Compare measured retention to the bound; report whether the floor is BINDING (measured tracks bound within 10%) or LOOSE (measured exceeds bound)

**Why required**: without this, every downstream verdict is ambiguous. The HARD-PASS conditions reference both alpha_c_measured AND the PAC-Bayes upper bound, both of which must be quantified from the single-expert run. Ship the pre-step BEFORE the main K-sweep; do not parallelize.

ETA estimate (exp_dev decides): pre-step single-expert at 5 seeds × 6 M-values ≈ 30 GPU-min. Main K-sweep 4 arms × 4 K-values × 4 M-values × 5 seeds ≈ several GPU-hours; queue assignment is exp_dev's call.

---

## CONTEXT POINTERS

- `experiments/exp_wave14_rprime2_moe_K_sweep_v1.py` — broken implementation analyzed in this drill (PARTITION confound)
- `experiments/exp_wave14e_moe_xtalk_smoke_v1.py` — SHIFT-style implementation with passing result; expert-load distribution shows mode-collapse-adjacent imbalance
- `data/exp_wave14_rprime2_moe_K_sweep_v1_smoke/metrics.json` — verdict MOE_KSWEEP_HARD_FAIL_REJECTED
- `data/exp_wave14e_moe_xtalk_smoke_v1_smoke/metrics.json` — verdict MOE_PASS, expert_loads [118, 772, 929, 181]
- `notes/research_R_PRIME_directions_2026-05-24.md` — original R-PRIME-2 spec
- `notes/research_pt_cascade_drill_2026-05-24.md` — template used for this drill's depth discipline
- `notes/exp_dev_handoff_rprime1_posterior_over_W_KL_derivation_2026-05-24.md` — R-PRIME-1 PAC-Bayes derivation work (the floor that this experiment tries to break)

---

## DISCIPLINE CITATIONS

- per [[feedback-rehabilitation-after-rejection]] — R-PRIME-2 HARD-FAIL was implementation-broken; this is the rehab, not a re-run
- per [[feedback-no-experiment-design-in-prompts]] — this handoff names task SHAPE (3-arm SHIFT/PARTITION/SINGLE design, mandatory pre-step, gating mechanism justification) but exp_dev decides all numerical sweep grids, seeds-per-cell, queue placement, ETA
- per [[feedback-verify-implementations]] — autopsy of R-PRIME-2's implementation done against the cited theory; gating choice justified vs cited LSH / MoE literature
- per [[feedback-envelope-expansion-fail-bands]] — HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL bands pre-registered with explicit numerical thresholds
- per [[feedback-lit-scan-calibration-penalty]] — confidence values deflated 0.15-0.25 across the four drill questions; novel-synthesis P (Arm A exceeds Arm C) capped at 0.50
- per [[feedback-2x-means-depth]] — drill goes deeper into the R-PRIME-2 failure mechanism, not a re-verification of its result
- per [[feedback-strategy-spec-formula-selftests]] — closed-form load-ratio derivation `4·M_total/N` provided with explicit cancellation step; exp_dev should verify the M_per_expert / M_cap_per_expert formula on a small synthetic example before coding
- per [[feedback-composition-classification]] — this is a HANDOFF-level composition (PAC-Bayes-floor + MoE-structural-separation); not a SCORE composition

---

## AUTONOMY DECLARATION

exp_dev decides:
- Exact K-sweep grid points (recommend including K=1 as control)
- Seeds-per-cell (recommend 5 minimum per [[project-research-playbook]])
- Queue placement (GPU for full; recommend GPU per [[feedback-gpu-first-for-depth-probes]] given seeds × cells > 50)
- ETA estimate
- Smoke-scale parameters
- Order: pre-step first, smoke for main, then full
- Code structure (one script or three)

exp_dev does NOT decide:
- The 3-arm structure (SHIFT / PARTITION / SINGLE matched-compute) — that is the testable design
- The pre-step single-expert calibration of alpha_c — REQUIRED
- The HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL band thresholds — pre-registered above
- The gating choice (LSH balanced-bin + top-2 retrieval) — chosen with explicit justification
- The mode-collapse instrumentation (Gini, max/min, top-2 fraction) — pre-registered above

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
