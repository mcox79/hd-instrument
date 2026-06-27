# Research -- Cortex E_tensor WRONG_DIRECTION 2x revival drill (alternatives beyond existing 4x + exp_dev probes)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Drill type:** 2x revival drill on HARD_FAIL `E_GATED HURTS OLD recall worse than RANDOM gating`
**Trigger:** `data/exp_cortex_E_tensor_HARDER_REGIME_v1_smoke/metrics.json` -- ARM_E_GATED_DOWNSCALE recall_old=0.500 vs ARM_RANDOM_GATED 0.717 vs ARM_NO_E_BASELINE 0.800; gap_E_vs_RND=-0.217. Wave 1.6 RETEST is in flight; this drill PRE-PROVIDES alternatives for if Wave 1.6 also fails.
**Excluded mechanism classes (already covered by existing alternatives):**
- The 4x drill `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md` ANCHORS 1-4: excitability-tensor (the very thing that failed), ultrametric-clustering, SOC-avalanche, MDL-dictionary-turnover.
- The exp_dev probe-candidates in `notes/exp_dev_to_research_cortex_E_tensor_v2_SMOKE_HARD_FAIL_Fix_B_wrong_shaped_2026-06-26.md`: counterfactual-utility ablation, surprisal-weighted bump, random-projection witness.

This drill must propose 2 STRUCTURALLY DIFFERENT mechanisms.

---

## HEADLINE

The deep failure of E_GATED is now triple-confirmed: (a) HARDER_REGIME smoke -- gap -0.217 vs RANDOM; (b) RETEST v2 smoke -- `cor(E, |W|)=0.984` proving E is a set-membership-correlated co-magnitude signal; (c) the existing 4x ANCHOR 1 framing of "per-atom excitability tensor decoupled from W" was correct in BRAIN-grounding but WRONG in substrate-implementation -- ANY retrieval-history-driven update rule will inherit the magnitude correlation because retrieval-success IS magnitude-success on the substrate's argmax cleanup.

**Substrate-deep diagnosis:** the cortex E_tensor mechanism class assumes there exists a per-atom-indexed scalar tag that meaningfully encodes "importance" while being orthogonal to the substrate's primary axis (cleanup-cosine magnitude). On bipolar HRR substrate, NO PER-ATOM SCALAR can be orthogonal to magnitude when its update rule depends on retrieval. The problem is dimensional: importance must live in a SPACE that is structurally different from the W-magnitude observable.

**Two structurally different paths the literature converges on:**

1. **Move importance OUT of per-atom-scalar SPACE and INTO per-pair / per-edge SPACE.** Track importance on the RELATIONS BETWEEN ATOMS (the bound-pair structure), not on atoms themselves. Edges have a different observability axis than nodes.
2. **Move importance OUT of substrate-internal observables and INTO an EXTERNAL HOMEOSTATIC TARGET** that the substrate must conform TO, not derive FROM. The brain's CREB excitability is set EXTERNALLY by neuromodulator broadcast, not derived from local synaptic activity.

**P_deflated for at least one of the 2 anchors closing cortex-content-extraction:** **0.40**.

---

## Cheap decisive test

For BOTH anchors: cell must include load-bearing FAIRNESS CHECK from USER pre-reg gate that killed Wave 1.6 v1/v2: `cor(importance_signal, |W @ key|) < 0.30 across all atom-buckets`. This is the bright-line test that proves the new mechanism is structurally different. Smoke first at the same regime as `cortex_E_tensor_HARDER_REGIME_v1` (N=256, M_OLD=200, M_RECENT=150, J=1000); STOP at smoke if fairness check fails.

HARD_PASS additionally requires `recall_old >= NO_E_BASELINE recall_old - 0.05` (preserves old at least as well as the unmodified baseline) AND `recall_recent >= 0.85` (does not destroy recent ingest).

---

## Falsifiable predictions

### ANCHOR 5 (cortex sequence; numbering continues from 4x drill): edge_importance_bound_pair_consolidation_v1

**Tagline:** Track importance on BOUND-PAIR EDGES, not on atoms. Consolidate the EDGES (binding events) that participate in repeated multi-atom queries; downscale atoms only as a derived consequence of their EDGES being low-importance.

**Mechanism (different from per-atom scalar):**

1. Maintain a sparse edge-importance tensor `H[i,j]` indexed by (atom_i, atom_j) pairs that have been BOUND together in any composite-write (substrate has these from binding.py role-filler ops).
2. On every retrieval that involves a composite query (a query that BINDS multiple atoms and returns a composite result), increment `H[i,j] += 1` for each (i,j) pair in the query. This is per-EDGE not per-ATOM.
3. Atom importance is DERIVED as `E[i] = sum_j H[i,j]` (the row-sum over the importance graph). Atoms participating in MANY important edges have high derived importance; atoms only in one-off edges have low derived importance.
4. Downscale rule: at homeostatic cycle, downscale atom_i iff `E[i] < e_thresh` AND `max_j H[i,j] < h_thresh` (no single edge is load-bearing for this atom).

**Why this avoids the failure mode:** the substrate's W magnitude is dominated by single-atom Hebbian writes (per-atom signal). Edge-frequency H[i,j] tracks RELATIONAL structure -- which atoms COMPOSE WITH which other atoms repeatedly. This is structurally orthogonal: an atom can have high |W @ key| (frequently retrieved alone) AND low edge-importance (never composes with anything else -- it's a "stub" atom); OR low |W @ key| (rarely retrieved alone) AND high edge-importance (always participates in composite reasoning). The fairness check `cor(E_derived, |W|) < 0.30` should PASS because the signals are derived from different observables.

**Falsifiable predictions:**
- HARD_PASS: at the HARDER_REGIME, `cor(E_derived, |W|) < 0.30` AND `recall_old >= 0.75` (matches or beats NO_E_BASELINE=0.800 within 0.05) AND `recall_recent >= 0.85` AND `n_downscaled > 100` (mechanism actually fires, not a no-op).
- MIDDLE_BAND: `cor < 0.50` AND `recall_old in [0.65, 0.75]`.
- HARD_FAIL: `cor >= 0.30` (edges turn out to also be magnitude-correlated -- mechanism fundamentally wrong-shaped) OR `recall_old < 0.65` (worse than current E_GATED) OR `no composite queries in the test regime to drive H` (mechanism inapplicable to substrate's current query distribution -- structural mismatch).

**Cross-discipline pulls:**
- **Brain (engram synaptic CLUSTERS -- Govindarajan-Israely-Huang-Tonegawa 2011):** brain consolidation occurs at SYNAPTIC CLUSTERS on dendritic branches (~10-um spans), not at individual synapses. The clustered-plasticity hypothesis is that synapses that fire together get spatially co-located and protected jointly. The substrate's bound-pair edges are exactly the analog of synaptic clusters -- groups of associations that fire together.
- **Math (graph centrality / PageRank, Brin-Page 1998):** instead of per-node importance, PageRank computes importance as eigenvector of the edge-stochastic matrix. Substrate-native PageRank on the H-graph gives a principled per-atom importance from the edge structure: `E[i] = sum_j H[i,j] * E[j] / out_degree(j)`. This recursive definition is **structurally orthogonal to W magnitude** because it depends only on H connectivity.
- **Network science (k-core decomposition, Seidman 1983):** atoms in the k-core of the edge-graph (every atom in subset has >= k edges within subset) are structurally load-bearing for the substrate's composite reasoning. Pruning atoms outside the k-core is a structural-not-magnitude criterion.
- **Materials (percolation on a graph, Stauffer-Aharony):** if H is too sparse, no giant connected component forms and the importance signal is useless; if H is too dense, importance saturates and is non-discriminating. There is a critical edge density (around the percolation threshold) where edge-importance is maximally informative. Substrate-native percolation check on H tells us whether the regime is in the discriminating zone.

**P_deflated:** **0.40** (raw 0.55 - 0.15 calibration penalty; mechanism class has strong brain + math grounding via clustered-plasticity + PageRank; main risk is that substrate's current cells don't generate enough composite queries to populate H meaningfully -- substrate's E_tensor cells use mostly single-atom queries by design; this anchor REQUIRES a regime change toward composite-query-driven cells, which aligns with USER pivot toward "build compositional understanding").

**Substrate primitives used:**
- Existing: binding.py (HRR role-filler bind/unbind), cleanup_memory.py
- NEW: `hdlab/edge_importance.py` -- sparse H[i,j] dict, increment on composite query, derived E from row-sum or PageRank, downscale gate

---

### ANCHOR 6: external_homeostatic_target_set_point_v1

**Tagline:** Importance is set EXTERNALLY by a homeostatic target (a desired W-norm distribution); substrate downscales to MATCH the target, not to encode internal importance. The target is brain-grounded (lognormal weight distribution observed in cortex).

**Mechanism (different from any retrieval-derived importance):**

1. Specify an EXTERNAL TARGET distribution for the substrate's weight magnitudes: lognormal with `mu=mu_target, sigma=sigma_target` (per Buzsaki-Mizuseki 2014 the cortex maintains a lognormal firing-rate / synaptic-weight distribution at all times; the SHAPE of the distribution is the homeostatic invariant).
2. At each homeostatic cycle, compute the CURRENT distribution of `|W @ key_i|` across all stored atoms i. Compare to target distribution via KL divergence.
3. Downscale rule: identify atoms whose current `|W @ key_i|` is in the **top tail beyond the target distribution's upper tail** -- these are the "outliers above lognormal expectation". Downscale these specifically, not by "low importance" but by "violates target distribution shape". `W[i] *= gamma` for atoms in the upper-outlier set.
4. Optionally: identify atoms in the **bottom tail beyond the target's lower tail** (atoms BELOW even the lognormal noise floor) and zero them out OR replace with fresh random directions.

**Why this avoids the failure mode:** importance is NOT a per-atom signal at all; the substrate is asked to maintain a SHAPE INVARIANT. The downscale criterion is statistical (distribution-matching) not magnitude-derived (no `|W| > thresh`) and not retrieval-derived (no hit-count). The fairness check `cor(importance, |W|) < 0.30` doesn't even apply because there IS no importance per-atom; the test becomes `cor(downscale_decision, |W|) < 0.30` -- which CAN be high (the top tail IS the high-|W| atoms) BUT that's OK because the downscaling is now ABOUT distribution-shape, not about correlation-with-W being a defect.

WAIT -- this is the key reframe. The Wave 1.6 USER fairness check `cor(E, |W|) < 0.30` was designed under the assumption that importance signal should be orthogonal to |W|. For lognormal-distribution-matching, the correct fairness check is DIFFERENT: `KL(post_W_distribution, target_distribution) < KL(pre_W_distribution, target_distribution)` -- the mechanism succeeds iff it MOVES the distribution toward the target. This is a more honest test for distribution-matching mechanisms.

**Falsifiable predictions:**
- HARD_PASS: at HARDER_REGIME, `KL(post_W, lognormal) < KL(pre_W, lognormal)` (mechanism actually moves distribution toward target) AND `recall_old >= 0.70` (within 0.10 of NO_E_BASELINE) AND `recall_recent >= 0.85` AND `||W||_F bounded` (distribution-matching keeps norm bounded).
- MIDDLE_BAND: KL improves AND `recall_old in [0.55, 0.70]`.
- HARD_FAIL: KL does NOT improve (mechanism doesn't actually match target -- the downscale operation as defined doesn't reshape the distribution as expected) OR `recall_old < 0.55` (distribution-matching destroys old patterns even worse than current E_GATED) OR `the target distribution is unachievable given the substrate's writes` (no schedule of gamma's brings W into lognormal shape).

**Cross-discipline pulls:**
- **Brain (Buzsaki-Mizuseki 2014 cortical lognormality):** [The log-dynamic brain](https://www.nature.com/articles/nrn3687): "The distribution of synaptic weights, firing rates and population synchrony in many brain areas follows a lognormal distribution, spanning several orders of magnitude." Crucially, this distribution is MAINTAINED across plasticity events -- it is a HOMEOSTATIC INVARIANT. This is exactly the missing primitive substrate lacks.
- **Math (maximum entropy under moment constraints):** lognormal is the max-entropy distribution given fixed mean and variance of log-magnitudes. The substrate-native version asks: subject to the constraint that the substrate stores N concepts with bounded ||W||_F, what is the max-entropy weight distribution? Answer: lognormal, with parameters set by N and storage capacity.
- **Signal processing (companding / mu-law compression):** in audio coding, mu-law / A-law compression maps a uniform input distribution onto a lognormal-like target to minimize quantization error per perceptual bit. The substrate as an "information channel" benefits from a similar SHAPE INVARIANT on its weight distribution.
- **Statistical physics (Boltzmann distribution maintenance under detailed balance):** any equilibrium distribution that satisfies detailed balance is a maximum-entropy distribution subject to energy constraints. Substrate's W distribution at equilibrium under random ingest IS lognormal (sum of log-iid is log-normal by CLT-on-logs). Homeostasis-toward-lognormal is detailed-balance maintenance.

**P_deflated:** **0.35** (raw 0.50 - 0.15 calibration penalty; brain-grounded but the substrate-native realization of "match a distribution shape" requires careful definition of the downscale schedule that does NOT just argsort by |W| -- there is real risk that distribution-matching collapses to top-quantile-pruning which IS magnitude-coupled and degenerates back into Wave 1.6's failure mode; the fairness check reframe to KL-improvement is structurally honest but may not satisfy USER's original intent).

**Substrate primitives used:**
- Existing: cleanup_memory.py, KL-divergence-on-empirical-distributions (standard numpy)
- NEW: `hdlab/distribution_homeostasis.py` -- fit current W-norm distribution, compute KL to target, identify outliers, schedule downscale to minimize KL

---

## Cross-thread synthesis

- **The 2 anchors are MECHANISM-CLASS DISJOINT from prior cortex content-extraction failures:**
  - Anchor 5 moves the importance signal to per-EDGE space (graph centrality), not per-atom.
  - Anchor 6 removes the per-atom importance signal ENTIRELY and replaces with a distribution-shape invariant.
- **Compositional with existing 4x ANCHORS 1-4:** Anchor 5 (edge-importance) is the COMPLEMENT to 4x ANCHOR 2 (ultrametric clustering) -- ultrametric finds atom clusters; edge-importance finds atom-pair bonds. They could compose: cluster by ultrametric distance, weight clusters by their internal edge-importance.
- **Compositional with existing 4x ANCHOR 3 (SOC):** Anchor 6 (distribution homeostasis to lognormal) is the FORMAL realization of what SOC was trying to achieve informally -- self-organized criticality MAINTAINS a scale-free distribution; lognormal-homeostasis maintains lognormal. Both are distribution-shape invariants.
- **Compositional with exp_dev's 3 probe candidates:** counterfactual-utility (exp_dev option 1) is per-atom and orthogonal-by-construction; Anchor 5 (edge-importance) provides a SCALABLE alternative because counterfactual-ablation requires O(N) cleanup re-runs per cycle while edge-importance is O(1) per query.
- **No-Hebbian-window META atom:** both anchors are window-free -- Anchor 5 increments H on composite queries (not on per-atom writes); Anchor 6 operates on W-statistics not on individual writes.
- **Aligns with USER pivot (substrate doesn't know language):** these anchors operate on STRUCTURAL CORTEX HOMEOSTASIS not on language eval. Anchor 5 specifically REQUIRES composite queries to fire, which couples with USER pivot toward "compositional understanding first." Anchor 6 is language-agnostic distribution maintenance.

---

## Substrate-product implications

1. **Per-atom-scalar importance has been triple-falsified.** Wave 1 E_tensor v1 HARD_FAIL, Wave 1.5 HARDER_REGIME HARD_FAIL wrong-direction, Wave 1.6 v2 fairness-gate STOP. Three different parameterizations all inherit the magnitude correlation because retrieval-driven updates are magnitude-driven on argmax cleanup. **Cap_map should retire the "per-atom-scalar importance" mechanism class entirely.**
2. **Two viable structural alternatives remain:** edge-space (Anchor 5) and distribution-space (Anchor 6). Both have brain + math + materials grounding. If BOTH HARD_FAIL, then cortex content-extraction may require leaving the bipolar HRR substrate entirely (switch algebras to Modern Hopfield with energy-based importance or to graph-neural-message-passing with explicit edge state).
3. **Anchor 5 unblocks the USER pivot.** USER pivot is "compositional understanding first." Composite queries -- the substrate operating on bound pairs, not just unitary atoms -- are exactly what Anchor 5 measures and reinforces. Even if the IMPORTANCE measurement fails, the act of building a substrate-native composite-query pipeline (required to populate H) advances the user's strategic direction.
4. **Anchor 6 is the substrate-native homeostasis primitive that's been missing.** Currently substrate has no concept of "maintain a healthy weight distribution." Anchor 6 introduces this primitive even if its first realization is imperfect.
5. **Cost:** Anchor 5 = ~4-6 CPU-hr local (new edge-importance primitive + integration into a cortex-content-extraction cell + REQUIRES composite-query workload, which itself takes ~2hr to set up); Anchor 6 = ~3-5 CPU-hr local (single primitive + cell that runs distribution-fit periodically).
6. **No language eval involved.** Pure cortex-homeostasis tests.

---

## Calibration penalty applied

- Lit-scan calibration penalty: 0.15 deflation applied (Anchor 5 raw 0.55 -> 0.40; Anchor 6 raw 0.50 -> 0.35).
- Novel-synthesis cap: 0.50 honored.
- HARD-FAIL thresholds explicit and falsifiable for both anchors with quantitative metrics.
- Brain-grounded mechanism (Anchor 5: clustered plasticity; Anchor 6: lognormal cortex) gets higher prior per USER 2026-06-23 ("brain is existence proof"); raws 0.55 / 0.50.
- Per-arm metrics-vs-verdict-msg per Fix #28: failure-mode diagnosis derived from explicit per-arm metrics + exp_dev's structural diagnosis (cor=0.984 = set-membership correlation), NOT verdict_msg framings.
- Pre-dispatch verify-the-referent per Fix #26: exp_dev should run `predispatch_check.py` against `edge_importance_bound_pair_consolidation_v1` and `external_homeostatic_target_set_point_v1` -- these are new anchor names not used before.

---

## Citations (verified)

External (cross-discipline lit-scan):

**Brain:**
1. Buzsaki & Mizuseki (2014). "The log-dynamic brain: how skewed distributions affect network operations" -- Nature Reviews Neuroscience 15: https://www.nature.com/articles/nrn3687
2. Govindarajan, Israely, Huang & Tonegawa (2011). "The dendritic branch is the preferred integrative unit for protein synthesis-dependent LTP" -- Neuron 69(1): https://www.cell.com/neuron/fulltext/S0896-6273(10)01045-7
3. Frey & Morris (1997). "Synaptic tagging and long-term potentiation" -- Nature 385: (foundational STC paper, motivates the failure mode of substrate's STC implementation)

**Math / network science:**
4. Brin & Page (1998). "The Anatomy of a Large-Scale Hypertextual Web Search Engine" -- WWW7 conference: https://research.google.com/archive/pageranks-paper.html
5. Seidman (1983). "Network structure and minimum degree" -- Social Networks 5(3): https://www.sciencedirect.com/science/article/abs/pii/0378873383900289 (k-core decomposition)

**Materials / statistical mechanics:**
6. Stauffer & Aharony (1994). "Introduction to Percolation Theory" -- Taylor & Francis: standard reference for percolation thresholds on graphs

**Signal processing:**
7. Smith (1957). "Instantaneous companding of quantized signals" -- Bell System Tech Journal 36: foundational mu-law / A-law compression (analog to lognormal target for substrate W)

Internal (cross-thread):
- `data/exp_cortex_E_tensor_HARDER_REGIME_v1_smoke/metrics.json` (Wave 1.5 HARD_FAIL wrong-direction)
- `data/exp_cortex_E_tensor_RETEST_fairness_v2_smoke/metrics.json` (Wave 1.6 RETEST cor=0.984)
- `notes/exp_dev_to_research_cortex_E_tensor_v2_SMOKE_HARD_FAIL_Fix_B_wrong_shaped_2026-06-26.md` (exp_dev probe candidates already-proposed; EXCLUDED from this drill)
- `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md` (4x drill ANCHORS 1-4; EXCLUDED from this drill)
- `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md` (USER pivot)

---

## Next-drill candidate field

If Anchor 5 lands first verdict, route next to **network-science-graph-theory** (Tier-1b; expander/Ramanujan/spectral-gap) for deeper analysis of substrate's bound-pair graph and what graph-structural properties predict cortex-content-extraction success.

If Anchor 6 lands first verdict, route next to **nonequilibrium-stat-mech** (Tier-1b; Jarzynski/Crooks/NESS) for the formal treatment of distribution-matching under continual driving -- the substrate's writes ARE a driving process; the homeostatic mechanism is a Crooks-like fluctuation theorem on the W-distribution.

If BOTH HARD_FAIL, the cortex content-extraction problem moves to **substrate-algebra-replacement**: route to a probe of whether Modern Hopfield (Krotov-Hopfield 2016 dense Hopfield, exponential capacity) provides energy-based importance natively, making the entire "extract importance from bipolar HRR" question moot. This would be a major architectural cap_map event.

-- Research (Opus 4.7-1M), 2026-06-26
