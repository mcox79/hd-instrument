# Spoke 1 PC-earning-complexity investigation

**Filed:** 2026-07-02 evening
**Trigger:** USER directive "we get this right" — pause FULL dispatch on
`substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2`
until mechanism clarity established.
**Load-bearing under:** brain-best-in-class strategic anchor (USER-LOCKED 2026-07-02).
**Cell smoke reference:**
`data/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2_smoke/metrics.json`.

## TL;DR — top-line finding

**Q1: Does predictive coding earn its complexity in the current v2 HYBRID
composition?** — **NO**, in EVERY tested composition. Diagnostic sweep
(5 seeds × 6 configs at N=2048, spc=40) shows:
- **Variant A (pre-mask compose, current v2):** monotone-degrades within-cluster
  consolidation. At W_ALPHA={0.10, 0.5, 1.0}, Δintra_mean = {-0.038, -0.173, -0.238}
  vs COMPETITIVE_ONLY. Seed CV amplifies 5x (0.083 → 0.44). The gap metric
  "improves" only by pushing unrelated concepts apart (Goodhart's Law on `gap`),
  not by pulling related concepts together.
- **Variant B (post-mask sign modulation):** null intervention. Δintra = -0.002
  at W_ALPHA={0.5, 1.0}. PC's sign contribution never flips a top-K dim's sign
  because raw acc magnitude dominates on those dims by construction.

The v2 HP HARD_PASS is a **coincidence of the `gap` summary metric** — the
underlying mechanism is worse than COMPETITIVE_ONLY at the brain-analog target
(within-cluster similarity).

**Recommended v3:** **V3-D — drop PC from Spoke 1** (P_CG = 0.50, capped).
Reframe as competitive-Hebbian sparse coding (Foldiak/Kohonen tradition) — a
legitimate brain-analog concept encoder in its own right. PC belongs in Spoke 2+
(temporal contiguity / one-shot indexing) where hierarchy makes sense.

**Under brain-best-in-class discipline, DO NOT ship v2 FULL as-is.** The HP
would pass, but the mechanism underneath is not what the pre-reg claims.

## 1. Prior-work check (substrate-KB concept-query, mandatory)

Three substrate queries, top-3 filtered:

**Query 1:** `predictive coding hierarchy composition Hebbian sparse coding brain`
- `B8. Predictive coding hierarchy` — cosine=0.499 (research_drill_substrate_integration_5x_2026-06-10)
- `B10. Predictive coding hierarchies` — 0.418 (research_drill_realtime_multimodal_5x_2026-06-10)
- `2.8 Predictive Coding` — 0.387 (research_drill_fact_representation_rethink_5x_2026-06-08)

**Query 2:** `Foldiak Kohonen competitive Hebbian coding invariance`
- Highest match cosine=0.303 (WordNet `competitive` entry — dictionary hit, not substantive).
- No prior Foldiak/Kohonen atoms in Store. **NEW LITERATURE THREAD to add.**

**Query 3:** `hyperdimensional predictive coding capacity limit`
- `4.2 Predictive Coding` — 0.364 (research_drill_continuous_truth_biology_3x_2026-06-09)
- `Predictive coding -> predictive substrate engine analogue` — 0.321 (atoms)
- `predictive_coding.py` — 0.321 (memory + notes; substrate module)

**Prior-work overlap check:**
- Substrate has `hdlab/predictive_coding.py` (Rao-Ballard threshold-gated Hebbian outer product on
  shared W). Confirmed in atoms.
- Prior substrate research atoms cite Rao-Ballard 1999, Friston FEP, Millidge-Salvatori-Buckley
  2021 review — all HIERARCHICAL PC; substrate's implementation is flat (single W).
- `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` lists PC as
  "Mechanism E" (top-down generative model) — pairs it with cortex-schema completion, NOT
  with competitive WTA allocation. **Composition of PC + competitive-WTA is NEW territory.**
- `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md`: L1.3 Predictive coding
  hierarchy (Rao-Ballard/Friston/Bastos/Caucheteux-Goyal 2022). Notes that Caucheteux showed
  brain ROI activations correlate with up-to-8-token future predictions — HIERARCHICAL
  substrate PC is unexplored.
- Confirms: this specific composition (flat PC + per-concept competitive WTA in a hybrid
  concept encoder, HD substrate) is NOVEL. No prior work under this exact configuration.
- Prior 2026-06-23 falsification: `sparse_engram_allocation_smoke_v1` — the ARM_NAIVE_WTA_SAMPLING
  baseline. Confirmed falsified as a candidate encoder. HYBRID beating it is the CORRECT
  falsification frame (v2 HP #3).

**Foldiak/Kohonen lit (from generalist knowledge, unindexed):**
Foldiak 1990 "Forming sparse representations by local anti-Hebbian learning" — competitive
Hebbian + anti-Hebbian lateral inhibition yields sparse-distributed codes. Kohonen SOM 1982 —
competitive winner update. These are the CANONICAL brain-analog competitive-Hebbian
mechanisms. `ARM_COMPETITIVE_ONLY` in the v2 cell already implements the sparse-Hebbian core
(no anti-Hebbian yet); it IS a legitimate brain-analog concept encoder on its own.

## 2. Q1 — Diagnostic sweep results

**Sweep design:** N=2048, spc=40, 5 seeds. Varying W_ALPHA (composition weight),
PC residual threshold, npass (PC training passes), and one architectural variant B
(post-mask sign modulation vs pre-mask compose).

**Focused sweep configs (`scratchpad/spoke1_pc_focused_sweep.py`):**
- A_walpha_0.0 (sanity: variant A with W_ALPHA=0 must equal COMPETITIVE_ONLY)
- A_walpha_0.10 (small PC influence)
- A_walpha_0.5 (v2 baseline)
- A_walpha_1.0 (larger PC influence)
- B_walpha_0.5 (variant B post-mask; PC influences sign only, mask stays raw)
- B_walpha_1.0 (variant B post-mask, larger PC influence)

### 2.1 The smoke masked pathology — off-disk metric re-read

Before sweeping, direct read of the v2 smoke metrics:

| Arm | cat_kitten (mean, cv) | cat_airplane (mean, cv) | gap (mean, cv) |
|---|---|---|---|
| COMPETITIVE_ONLY | +0.522 (cv=0.076) | +0.015 (cv=1.33) | +0.507 (cv=0.083) |
| PREDICTIVE_ONLY (dense) | +0.512 (cv=0.078) | -0.054 (cv=1.37) | +0.566 (cv=0.123) |
| **FULL_HYBRID** | **+0.220 (cv=0.66)** | **-0.298 (cv=0.76)** | +0.517 (cv=0.38) |

**Mechanism read:**
- HYBRID cat_kitten similarity is 42% of COMPETITIVE_ONLY (0.220 vs 0.522).
  The composition **degrades** within-cluster consolidation by 0.30.
- HYBRID cat_airplane is much more negative than COMPETITIVE_ONLY (-0.298 vs +0.015).
  The composition adds cross-corpus **anti-similarity** pressure.
- Net gap looks similar because pull-together loss (~0.30) roughly matches
  push-apart gain (~0.31). Same summary number, opposite mechanism.
- Seed CV amplified 5x (from 0.08 to 0.38) — the composition is FRAGILE where
  single mechanisms are STABLE.

Under a brain-best-in-class reference standard, within-cluster consolidation
(cat/kitten similar) is the **primary target** of a concept encoder — not
absolute discrimination distance. HYBRID as constructed regresses the primary
target.

**intra_cluster_cos_mean** (all 25 clusters, not just cat/kitten):

| Arm | intra_mean | intra_std |
|---|---|---|
| COMPETITIVE_ONLY | 0.474 | 0.006 |
| PREDICTIVE_ONLY | 0.532 | 0.019 |
| **FULL_HYBRID** | **0.306** | **0.040** |

Confirms the pattern generalizes across all 25 clusters. HYBRID cross-cluster
consolidation is **65% of COMPETITIVE_ONLY** and **58% of PREDICTIVE_ONLY**.
The composition is anti-composing.

### 2.2 Diagnostic sweep — configs and results

Sweep configs (15 total):
- **Variant A** (pre-mask compose, current v2 architecture):
  - W_ALPHA ∈ {0.0, 0.10, 0.25, 0.50, 1.0, 2.0} at threshold=0.30, npass=1
  - Threshold ∈ {0.10, 0.20, 0.40, 0.50} at W_ALPHA=0.5, npass=1
  - Npass ∈ {3, 5} at W_ALPHA=0.5, threshold=0.30
- **Variant B** (post-mask sign modulation):
  - W_ALPHA ∈ {0.5, 1.0, 2.0} at threshold=0.30, npass=1

### 2.3 Aggregate sweep results (5 seeds each, N=2048 spc=40)

**COMPETITIVE_ONLY reference (mean over 5 seeds):**
- cat_kitten = 0.522 ± 0.040
- gap = 0.507 ± 0.042 (cv 0.083)
- **intra_cluster_cos_mean = 0.474 ± 0.006** (very stable)

**Aggregate sweep table** (Δ = HYBRID mean − COMPETITIVE_ONLY mean):

| Config | gap (mean, cv) | intra_mean | Δgap | Δck | **Δintra** |
|---|---|---|---|---|---|
| A_walpha_0.0 (sanity) | 0.507 (0.083) | 0.474 | 0.000 | 0.000 | **0.000** ✅ sanity confirmed |
| A_walpha_0.10 | 0.463 (0.137) | 0.436 | -0.044 | -0.054 | **-0.038** ↓ |
| A_walpha_0.5 (v2 baseline) | 0.566 (0.403) | 0.301 | +0.059 | -0.273 | **-0.173** ↓↓ Goodhart |
| A_walpha_1.0 | 0.678 (0.444) | 0.236 | +0.171 | -0.283 | **-0.238** ↓↓↓ extreme Goodhart |
| B_walpha_0.5 (post-mask) | 0.507 (0.083) | 0.472 | 0.000 | 0.000 | **-0.002** null |
| B_walpha_1.0 (post-mask) | 0.507 (0.083) | 0.472 | 0.000 | 0.000 | **-0.002** null |

**Key readings:**
1. **A_walpha_0.0 sanity passes** — all Δ = 0.000, confirming variant A at zero-weight collapses to COMPETITIVE_ONLY. No implementation bug.
2. **Variant A monotone-degrades intra_mean.** At W_ALPHA = 0.10, Δintra = -0.038; at 0.5, -0.173; at 1.0, -0.238. No W_ALPHA rescues consolidation.
3. **The "gap improvement" at W_ALPHA ≥ 0.5 is Goodhart.** Gap goes UP (+0.059 to +0.171) while ck goes DOWN (-0.273 to -0.283) and intra_mean crashes (-0.173 to -0.238). The gap gain comes entirely from cross-corpus anti-correlation pressure (ca goes strongly negative), NOT from within-cluster consolidation.
4. **Seed CV amplifies 5x under variant A** (0.083 → 0.403 → 0.444). The composition is architecturally fragile where the single mechanism is architecturally stable.
5. **Variant B (post-mask) is a null intervention.** Δintra = -0.002 for both W_ALPHA = 0.5 and 1.0. PC's sign contribution never flips a top-K dim's sign because raw acc magnitude dominates on those dims by construction.

**None of the 5 non-sanity configs meets the "PC earns complexity" criterion**
(Δintra ≥ +0.05 with cv ≤ 0.20). PC is either useless (variant B) or actively
harmful (variant A). The v2 HP HARD_PASS on `gap` is Goodhart, verified.

### 2.4 Mechanism interpretation

The sweep confirms three predictions from the seed-29 mechanism analysis:

1. **A_walpha_0.0 sanity:** deltas are exactly 0. Confirms variant A at
   W_ALPHA=0 collapses to COMPETITIVE_ONLY. No implementation bug.
2. **Variant A W_ALPHA monotone-degrades within-cluster consolidation.**
   Even at W_ALPHA=0.10, d_ck ~= -0.03 to -0.05; d_intra ~= -0.03 to -0.04.
   No W_ALPHA rescues consolidation — the composition is architecturally
   anti-composing.
3. **Variant B (post-mask) is a null intervention.** At W_ALPHA={0.5, 1.0},
   d_intra ~ 0.000 for most seeds. The mask stays raw-competitive-driven, and
   the sign is dominated by the raw accumulator on top-K dims (which have
   large |acc_raw| by construction; W's addition doesn't flip signs there).

4. **The "gap" metric is misleading.** At larger W_ALPHA in variant A, gap
   often **increases** (seed 17 A_walpha_1.0: d_gap = +0.098) while d_ck
   drops -0.488 and d_intra drops -0.181. This is Goodhart's Law on the
   discrimination gap: increased cross-corpus anti-correlation looks like
   "better" but the underlying representation is worse.

**Conclusion — Q1 answer:** No config in the diagnostic sweep meets the
"PC earns complexity" criterion (mean d_intra >= +0.10 AND cv < 0.20 in gap).
Variant A degrades. Variant B is null. PC as currently composed with sparse-WTA
in Spoke 1 does NOT contribute to the brain-analog target.

## 3. Q2 — Seed-29 pathology root cause

Seed 29 in the v2 smoke:
- COMPETITIVE_ONLY: cat/kitten=0.488, cat/airplane=0.000 → gap=0.488
- PREDICTIVE_ONLY: cat/kitten=0.438, cat/airplane=-0.150 → gap=0.589
- **HYBRID: cat/kitten=0.000, cat/airplane=-0.659 → gap=0.659**

HYBRID annihilates cat/kitten similarity (BOTH single arms produce ~0.45; the
composition drops it to 0). The gap looks great because cat/airplane became
extremely negative.

### 3.1 Off-disk reproducer (isolated seed 29 diagnostic)

Reproducer: `scratchpad/seed29_pathology.py`. Trains PC once for seed 29 at
N=2048 spc=40, then dissects top-K masks / W projection profile / sentence
residual log.

**Top-K mask analysis (K=41, target 2% sparse):**

| Metric | COMPETITIVE_ONLY | HYBRID (pre-mask) |
|---|---|---|
| Jaccard(cat, kitten mask) | **0.323** | **0.038** |
| Jaccard(cat, airplane mask) | 0.025 | **0.439** |
| Mask intersection popcount (cat, kitten) | ~20 | **3** |
| cos(cat_hd, kitten_hd) | 0.488 | 0.073 |
| cos(cat_hd, airplane_hd) | 0.000 | -0.610 |

**Under COMPETITIVE_ONLY, cat and kitten share ~1/3 of their top-K dims** (the
per-cluster consistent axes). **Under HYBRID with W_ALPHA=0.5, they share only
3 dims** — one order of magnitude less. And cat now overlaps ~44% with airplane's
dims (with opposite sign, producing strong anti-correlation).

**Root cause — W projection asymmetry:**

The W matrix acts asymmetrically on different concept-means at this seed:

| Vector | \|\|input\|\| | \|\|W @ input\|\| | ratio |
|---|---|---|---|
| cat_mean | 10.36 | 35.03 | **3.38x** |
| kitten_mean | ~10 | ~12 | **1.21x** |

**For cat, the composed vector `x + 0.5 * W @ x` is dominated by the W term
(3.4x amplification).** For kitten, the composed vector is barely different from
raw x (1.2x). The two concepts' composed representations diverge in top-K
selection because W amplifies one but not the other.

**Which dims does composition select vs raw?**

- cat top-K raw vs composed overlap: **1/40** (essentially disjoint — W hijacks the mask entirely)
- kitten top-K raw vs composed overlap: **28/40** (mostly preserves the raw mask)
- cat/kitten top-K raw overlap: 19/40 (near ~48%)
- **cat/kitten top-K composed overlap: 3/40** (near-orthogonal)

The composition drops cat/kitten shared dims from 19→3 because cat's mask flips
entirely while kitten's mask barely moves.

**Why the asymmetry? PC writes per cluster:**
- cat/kitten cluster: 31.2% write rate (below-median)
- airplane/jet cluster: 38.8% write rate (above-median)

The airplane cluster gets **more residual writes** during training — W's
airplane-space is denser than its cat-space. When we then compute W @ x_cat,
W happens to project cat into airplane-space rather than into cat's own dims
(because W's dominant learned directions come from the concepts it wrote most
about).

**Mechanism:** flat unsupervised PC converges toward W ~ (input covariance
dominant eigendirections). Under shuffled-order writes with residual-gated
Hebbian outer products, whichever concepts hit the threshold first accumulate
W-mass. Their directions become dominant. Subsequently other concepts get
PROJECTED INTO those dominant directions via `W @ x`. This is a runaway
positive-feedback pathology on training order.

**Confirmation this is not a bug:** COMPETITIVE_ONLY and PREDICTIVE_ONLY at
seed 29 both work fine (0.488 and 0.438 respectively). The pathology is
strictly in the COMPOSITION, and specifically in the top-K selection being
hijacked by W-projection magnitude.

**This is order-dependent and not seed-specific.** The same mechanism would
appear at any seed whose shuffle happens to write W-mass to concepts other
than cat/kitten early. Seed 29's HYBRID pathology is one instance of a class
of failure modes intrinsic to the composition.

## 4. Q3 — Recommended v3 mechanism variants

Under brain-best-in-class reference standard, three v3 options:

### V3-A — Composition-weight tuning (minimum change; FALSIFIED by sweep)

**Change:** would have been W_ALPHA tuning.
**Sweep result:** NO W_ALPHA in {0.0, 0.10, 0.5, 1.0} yields Δintra ≥ 0 vs COMPETITIVE_ONLY.
The only W_ALPHA that doesn't degrade is 0 (which is COMPETITIVE_ONLY exactly).
**Mechanism issue:** flat PC's W develops asymmetric amplification (seed 29 evidence);
top-K selection gets hijacked toward W-dominant directions regardless of weight.
**Verdict:** falsified. Not a viable v3 path.

### V3-B — Post-mask sign modulation (FALSIFIED by sweep as tested)

**Change tested:** COMPETITIVE_ONLY selects the mask (within-concept salience);
PC contributes to the SIGN within selected dims via `sign(acc_raw + W_ALPHA * W @ acc_raw)` on mask.
**Sweep result:** NULL intervention. Δintra = -0.002 at W_ALPHA={0.5, 1.0}.
**Mechanism issue:** on top-K dims, |acc_raw| is by construction large; adding
W_ALPHA * (W @ acc_raw) never flips signs there. PC's sign contribution is
architecturally invisible in this formulation.
**Verdict:** falsified as tested. See V3-B' below for speculative variant.

### V3-B' — Post-mask sign flip-only on ambiguous dims (SPECULATIVE, untested)

**Change:** apply PC sign flip ONLY on top-K dims where |acc_raw| is
below-median within the mask (i.e., ambiguous dims that WTA barely retained).
Idea: PC contributes only where the raw signal is weak; leaves confident-sign
dims alone.
**Mechanism:** decouples PC contribution to the sub-region of the mask where
raw acc doesn't dominate. Might inject useful sign structure in low-signal dims.
**Brain-analog fidelity:** SPECULATIVE. Not a documented microcircuit; a
substrate design choice.
**Effort:** low (~50 lines).

### V3-C — Hierarchical PC (proper Rao-Ballard)

**Change:** two-layer PC where layer L2 predicts layer L1 activity, not input.
Layer L1 provides the residual up to L2; L2 sends back predictions; W learns
top-down. Composed with competitive WTA at L1 output.
**Mechanism:** matches Rao-Ballard 1999 / Bastos 2012 canonical cortical microcircuit.
Flat PC on same-space is a degenerate case that converges toward PCA-of-input,
which fights competitive-WTA's per-concept discrimination.
**Brain-analog fidelity:** HIGH. Direct cortical analog.
**Effort:** medium-high (~200-400 lines new; needs an L2 latent space and its own
Hebbian rule for W_top-down).

### V3-D — Honest reframe: Spoke 1 = COMPETITIVE + Hebbian only

**Change:** drop PC from Spoke 1 entirely. Extract Spoke 1 = char+positional + competitive
WTA + Hebbian sign accumulation. Add anti-Hebbian lateral inhibition (Foldiak 1990) as an
enhancement.
**Mechanism:** classic Foldiak/Kohonen sparse-distributed competitive coding.
**Brain-analog fidelity:** HIGH. This IS a documented cortical mechanism
(primary sensory cortex + local competitive circuits).
**Where PC lives:** in Spoke 2+ (temporal contiguity) where SEQUENCE prediction
makes sense; not on single-hop concept discrimination where competitive-WTA already
solves the problem cleanly.
**Effort:** trivial (remove PC from cell).

### P_CG estimates (deflated per lit-scan calibration penalty)

Estimation basis: brain-analog fidelity + prior-work evidence + mechanism
robustness under seed order variance. Novel-synthesis cap 0.50 per protocol.
Lit-scan deflation 0.15-0.25 applied.

| Variant | Raw P | Deflated P_CG | Rationale (updated with sweep) |
|---|---|---|---|
| V3-A W_ALPHA tuning | 0.15 | **0.05** | Sweep shows Δintra ≤ 0 at all tested W_ALPHA; doesn't fix mechanism |
| V3-B post-mask sign (as tested) | 0.15 | **0.05** | Sweep confirms null intervention (Δintra = -0.002 at W_ALPHA={0.5, 1.0}) |
| V3-B' post-mask sign — flip-only | 0.35 | **0.20** | Untested: only apply PC where raw acc magnitude is small (below-median top-K). Might contribute at ambiguous dims. Speculative rescue of V3-B. |
| V3-C hierarchical PC | 0.55 | **0.30** | Right analog but 3+ new mechanisms; higher engineering risk. Belongs in Spoke 2+ anyway. |
| V3-D drop PC (Foldiak) | 0.65 | **0.50** (capped) | Well-understood single-mechanism, seed-stable, honest brain analog. |

Recommended sequencing:
1. **V3-D first** (trivial cost, highest P_CG, honest reframe). Cell = char+positional + competitive WTA + Hebbian sign accumulation + optional Foldiak anti-Hebbian lateral inhibition. If passes CG cleanly, that's Spoke 1 done — extract to hdlab.
2. **Defer V3-A** — sweep confirms it doesn't work at any W_ALPHA. Papering over the mechanism issue is not brain-best-in-class.
3. **Defer V3-B / V3-B'** — the sweep-tested V3-B is a null intervention. V3-B' (flip-only on ambiguous dims) is a speculative rescue; not worth a probe unless V3-D leaves clear room for PC contribution.
4. **Defer V3-C to Spoke 2+** — hierarchical PC across cortical-layer analogs is the right home. Composing at Spoke 1 (single-hop concept discrimination) is a category error.

## 5. Honest brain-best-in-class read

**The v2 HYBRID HARD_PASS is a metric-coincidence, not a mechanism victory.**
Under brain-best-in-class discipline, the primary target of a concept encoder is
within-cluster consolidation (similar concepts share representational features).
Discrimination against unrelated concepts is a *derivative* target — it comes for
free from sparse-random assignment. The metric that matters is `intra_cluster_cos_mean`:
"do cat and kitten share features?" HYBRID at 0.306 fails this against
COMPETITIVE_ONLY at 0.474 and PREDICTIVE_ONLY at 0.532.

**Flat unsupervised PC is degenerate against per-concept sparse-WTA.**
The mechanism analysis at seed 29 shows W develops an ASYMMETRIC amplification
profile: whichever concepts hit the residual threshold first (order-dependent)
accumulate W-mass. Subsequent concepts get their `W @ x` dominated by *those*
directions, not their own. This is a runaway positive-feedback pathology on
training order. The seed CV amplification (0.08 → 0.38) is the fingerprint of
this pathology at population scale.

**The brain doesn't compose flat PC with WTA in a single layer.**
- Rao-Ballard 1999 canonical PC is HIERARCHICAL: L_top predicts L_bottom;
  the residual (not the composed value) is what propagates up.
- Bastos 2012 canonical microcircuit: superficial layers carry prediction
  errors, deep layers carry predictions. They are ANATOMICALLY separated.
- Foldiak 1990 anti-Hebbian sparse coding: this IS a documented single-layer
  competitive-Hebbian mechanism that produces sparse-distributed codes.

**The honest reframe under brain-best-in-class:**
Spoke 1 = char+positional (V1 analog) + competitive WTA + Hebbian sign
accumulation. This is Foldiak/Kohonen/Olshausen tradition — a legitimate
brain-analog concept encoder in its own right. PC's role in the brain is
top-down expectation-signaling across cortical hierarchy levels. Composing
flat PC with sparse-WTA at the SAME hierarchy level was our design mistake,
not a mechanism failure.

**Where PC belongs:**
- **Spoke 2 (temporal contiguity):** sequence prediction is inherently
  hierarchical (predict-next-token requires temporal-history model). PC's
  Rao-Ballard analog fits here.
- **Spoke 3 (one-shot hippocampal indexing):** episode-vs-schema decision is
  a two-layer prediction problem (schema-cortex predicts, episode-hippocampus
  fills residual). PC is the natural mechanism.
- **NOT Spoke 1** (single-hop concept discrimination): competitive-WTA already
  solves this cleanly.

**Recommended pivot:**
File Spoke 1 v3 as V3-D (drop PC, char+positional + WTA + Hebbian). Optionally
add V3-B as a "does PC contribute anything?" ablation in parallel. If both pass
CG cleanly with clean-mechanism attribution, Spoke 1 is a real brain-analog
concept encoder — just simpler than we designed.

**What NOT to do:**
- Do NOT ship v2 as-is even though HP HARD_PASS. The HP measures the wrong
  metric (gap, not intra_mean), and the mechanism underneath is worse than
  simpler alternatives.
- Do NOT chase W_ALPHA tuning as the fix. It papers over the mechanism issue.
- Do NOT rush to Spoke 2. Get Spoke 1 mechanism-clean first.

## 6. Deliverable summary

**Q1 answer:** PC does NOT earn complexity in the v2 HYBRID composition.
The HP HARD_PASS is a coincidence of the `gap` metric hiding a within-cluster
regression (0.474 → 0.306 intra_mean). Ratio of PC-added lift to added seed
variance (cv 0.08 → 0.38) is architecturally unfavorable.

**Q2 answer:** Seed 29 pathology is a specific instance of an order-dependent
W-projection asymmetry — flat PC's W accumulates mass on early-written concepts,
then hijacks later concepts' top-K masks via `W @ x` amplification. Not
seed-specific — the failure mode class is intrinsic to the composition.

**Q3 answer:** Recommended v3 = V3-D (drop PC from Spoke 1). Reframe as
competitive-Hebbian sparse coding (Foldiak/Kohonen tradition). PC lives in
Spoke 2+ where hierarchy makes sense. P_CG = 0.50 (capped novel-synthesis).
V3-B as parallel ablation at P_CG = 0.35.

**Load-bearing implication:** the entire Stage 2 concept encoder arc depends
on getting Spoke 1 mechanism-clean. Dispatching v2 FULL right now would land
a HARD_PASS that we would later have to reframe — worse than filing an honest
mechanism reframe now.

## References

- Rao & Ballard 1999. "Predictive coding in the visual cortex." Nat Neurosci 2:79-87.
- Friston 2005. "A theory of cortical responses." Phil Trans R Soc B.
- Bastos et al. 2012. "Canonical microcircuits for predictive coding." Neuron.
- Millidge, Salvatori, Buckley 2021. "Predictive Coding: a Theoretical and Experimental Review." arXiv:2107.12979.
- Foldiak 1990. "Forming sparse representations by local anti-Hebbian learning." Biol Cybern 64:165-170.
- Kohonen 1982. "Self-organized formation of topologically correct feature maps." Biol Cybern 43.
- Caucheteux & King 2022. "Brains and algorithms partially converge in natural language processing." arXiv:2111.14232.
- Substrate arc 2026-06-23: `sparse_engram_allocation_smoke_v1` (falsified; = ARM_NAIVE_WTA_SAMPLING v2 baseline).
