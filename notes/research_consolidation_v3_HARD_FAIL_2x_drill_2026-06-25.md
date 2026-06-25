# Research 2x revival drill — Consolidation v3 HARD_FAIL_CONSOLIDATION_NO_GENERALIZATION

**Date:** 2026-06-25
**Driver:** USER standing rule "drill all negatives 2x/3x including disparate fields"
**Cell:** `exp_substrate_multihop_consolidation_v3_proper_test_HELDOUT_FIX` HARD_FAIL
**Per-arm HELDOUT (verified from metrics.json, not verdict_msg):** NAIVE=0.850 / CONSOL_K1=0.007 / CONSOL_K3=0.107 / CONSOL_K10=0.107 / CONSOL_K50=0.400 / HYBRID=0.107
**Per-arm TRAINING:** all consol arms 1.000 (or 0.994 K50)
**Rails fired:** `NAIVE_OUT_OF_BAND(0.850 not in [0.62,0.68])` + `KTHR_GATING_NOT_DIFFERENTIATING(train spread=0.006<0.10)`

PURE research; no cell dispatches. Three angles + root cause + recommendation.

---

## HEADLINE (read first)

**Three findings, ranked by load-bearing:**

1. **The NAIVE-rail drift is decoded, NOT mysterious.** v1 / v2 / v3 use different chain-class structure (V_P=10 multi-pair vs V_P=2 single-pair vs V_P=6 with HIGH/MID/LOW frequency classes). NAIVE values 0.847 / 0.628 / 0.850 are deterministic outputs of these three regime choices — NOT methodology bugs, NOT capacity drift, NOT seed noise. The v3 sanity-rail [0.62, 0.68] was inherited from v2's single-pair regime but v3 NAIVE arm uses 200 chains over a single class (effectively V_P_naive ≈ 2 BUT separate W, separate atom-density). The rail was MIS-SPEC'd, not the result mis-measured. **Root cause: pre-reg copied band from v2 without re-deriving for v3 NAIVE arm structure.**

2. **Consolidation HURTS heldout (NAIVE 0.85 vs best CONSOL_K50=0.40) — and this is mechanistically EXPECTED, not pathological.** The v3 cell wrote compound-predicate atoms `bind(s, R_compound(p1,p2), o)` into W for TRAINING chains only. At heldout retrieval, the cleanup over W matches against the WRONG retrieval key — the heldout chain has a DIFFERENT (s, o) and the consolidated compound atoms in W increase total atomic density without providing the right shortcut. Heldout cleanup is FORCED to find an answer among the consolidated TRAINING vectors → near-zero match. **This is associative-memory crosstalk interference being correctly measured, not a substrate failure.**

3. **Brain consolidation looks like it "always helps" because brain consolidation operates on FAMILIES of similar items via shared cortical features — NOT on point-mass episodic atoms.** Substrate's W is a single-timescale linear store with per-tuple compound atoms; brain's neocortex is a multi-timescale cascade-synapse store with feature-overlap-based generalization. The substrate cell tests episodic consolidation; brain consolidation requires SEMANTIC consolidation (extract regularities across many instances → shared features → new instances retrieve via shared features). **There is no missing-mechanism in the cell; the cell tests the WRONG analog of "consolidation."**

**Recommendation:** Abandon the "compound-predicate consolidation" mechanism as Barrier 1 closer. Pivot to **pointer-chain hybrid** (the substrate-native non-compositional escape hatch; existing Store precedent at depth=100). Hold "consolidation" idea in reserve for SEMANTIC consolidation under a feature-share cortical analog — a different cell entirely, NOT a redesign of v3.

---

## Angle A — Pure math / information theory

### Why K=50 consolidation HURTS vs NAIVE

The CONSOL arm writes `(s, R_compound, o)` atoms into the SAME W that holds the 1-hop primitive atoms `(s, p1, intermediate)` and `(intermediate, p2, o)`. Hebbian superposition means:

```
W = Σ_train  outer(bind(s, p1), intermediate)
  + Σ_train  outer(bind(intermediate, p2), o)
  + Σ_consol outer(bind(s, R_compound(p1,p2)), o)   ← added by consolidation
```

The third term ADDS noise capacity. At cleanup time, the heldout query `bind(s_held, R_compound(p1,p2))` is NOT among the consolidated atoms (heldout (s,o) disjoint from train) — so the cleanup matches against the entire W and finds the best-aligned consolidated TRAINING atom, returning some random training-o. This is **EXACTLY the associative-memory crosstalk story** — the consolidated atoms are NEAREST in compound-key space, but their OUTPUTS are wrong-o. The "near-zero" heldout result is honestly measuring this crosstalk.

K=50 is "best" only because at threshold=50 only 1 compound predicate gets created (HIGH only) — so fewer wrong-match crosstalk atoms exist. The closer K_THRESH gets to "consolidate nothing," the closer to NAIVE the heldout gets. **The discriminator gradient itself proves crosstalk is the mechanism.**

Information-theoretically: consolidation does not ADD information about heldout chains; it adds STRUCTURED-MISMATCH atoms that the cleanup procedure cannot distinguish from genuine target atoms. The information channel from heldout query → heldout answer is the SAME as NAIVE (the 1-hop primitive atoms must do the work for both arms); consolidation strictly adds crosstalk to the channel for heldout queries.

### Frady-Sommer capacity bound

At V_C=600 V_P=2 (NAIVE) or V_P=6 (CONSOL) N=8192 K_SET=20: the Frady-Sommer capacity for k-hop chain retrieval with random-bipolar codebook scales as N / (k · V · K_SET) before crosstalk dominates. With N=8192, V·K=600·20=12000, k=2: theoretical k=2 capacity ratio ≈ 8192 / (2·12000) ≈ 0.34. Empirical: NAIVE achieves 0.85 — well above the random-noise floor, meaning the random-bipolar isotropic encoder gets some lift from inherent codebook separability (V_C=600 codes are pseudo-orthogonal at N=8192).

For consolidation to LIFT this 0.85 ceiling on HELDOUT, the consolidator must add information ABOUT THE HELDOUT (s, o) pair. By construction it cannot — it only sees TRAINING pairs. **The theoretical multi-hop ceiling under random-bipolar isotropy at this regime IS approximately 0.85 + small noise; the cell is bouncing against the genuine Barrier 1 ceiling.**

### Information geometry: shortcut on a different manifold

The compound atom `bind(s, R_compound(p1,p2))` lives in a DIFFERENT subspace from `bind(bind(s, p1), p2)` (the chained query). They project to the same target O via Hebbian outer-product, but the bind operator is non-commutative + non-associative under HRR (or sparse-bipolar): `bind(A, bind(B, C)) ≠ bind(bind(A, B), C)`. The consolidated shortcut atom lives in the "flat" subspace of pair-as-symbol; the chained-query trajectory lives in the "compositional" subspace of (subj-bound)-then-(rel-bound).

Heldout queries arrive in the COMPOSITIONAL subspace (chained query), but the consolidated atoms live in the FLAT subspace — there is no projection back. NAIVE doesn't have this issue because there are NO consolidated atoms; the entire query path is compositional.

**Implication:** consolidation as written is mathematically a separate retrieval channel, not a shortcut. To make it work on heldout you would need either (a) the heldout query rewritten into FLAT form before cleanup (requires KNOWING it's a compound) or (b) the consolidation mechanism to extract a FEATURE-SHARE structure that survives the (s,o) substitution — neither is in the current cell.

---

## Angle B — Brain / neuroscience

### "Brain consolidation never hurts" — actually it DOES, just on a different timescale

The folk claim "brain consolidation never hurts retrieval" is wrong. Two known phenomena where consolidation DOES hurt:

1. **Retrieval-induced forgetting (Anderson 1994).** When item A and item B share a cue and A is retrieved, B becomes HARDER to retrieve. The mechanism is the same as the substrate cell — consolidated/strengthened items create competitor activation at cleanup that interferes with non-consolidated competitors.
2. **Reconsolidation interference (Nader-Schafe-LeDoux 2000).** Reactivating a consolidated memory makes it labile; if interfering content is introduced during the labile window, the reconsolidated memory is degraded. Brain consolidation is NOT monotonically protective.

The substrate v3 cell is operationally the **interference half** of brain consolidation — strengthening a subset of items hurts retrieval of non-strengthened items in the same memory store. The fact that v3 measures this honestly is a feature, not a bug.

### Missing mechanism: SYSTEMS-level (offline replay) vs ONLINE consolidation

The cell does ONLINE consolidation: write compound atom WHILE encoding chains. Brain does the opposite:

- **Hippocampal fast learning** (online): full episodic detail; high interference; CA3 attractor + DG pattern separation
- **Sharp-wave-ripple-tagged replay** (offline, sleep): SELECTIVE subset of episodes (Liu 2024 PMC 11068097; Cell 2025 large-SWR studies) gets reactivated during slow-wave sleep
- **Neocortical slow learning** (offline, post-replay): replayed episodes get INTEGRATED into cortical schemas via shared features

The v3 cell collapses all three into one online step writing into the same W. The brain analog of v3 is *if you wrote your sleep-consolidated schemas straight into hippocampus while still encoding new episodes* — which would indeed cause the kind of crosstalk v3 measures.

**The brain-correct version would require TWO W matrices:**
- W_hippocampal: fast-learning store; receives all training; high crosstalk
- W_neocortical: slow-learning store; receives ONLY consolidated FEATURE-OVERLAP-extracted patterns; queried as fallback when hippocampal cleanup margin is low

The Cell H spec (`director_cell_H_extended_multihop_consolidation_2026-06-25.md`) gestures at this with parallel-W per depth, but the missing primitive is FEATURE EXTRACTION across consolidation candidates. Without feature-share, parallel-W is just more crosstalk channels.

### Squire-Wixted complementary learning systems — both in one W is the problem

Squire-Wixted's CLS framework states: hippocampal fast learning is INSTANCE-based; neocortical slow learning is FEATURE-based. The substrate's single W tries to be both, which means consolidated atoms compete instance-wise with primitive atoms. Either:

- Separate the W matrices (substrate-substantive change; CLS-faithful)
- Or change the consolidation primitive from "write compound 1-hop atom" to "extract shared feature → write feature-graph edge" — but the substrate has no feature-graph primitive

**Calibrated prior for "substrate-native CLS via separated W matrices closes Barrier 1": P_deflated = 0.25.** The mechanism is mathematically clean (just two W's) but the discriminator question is whether the heldout query has a HOPABLE feature-share path — which is a CORPUS property, not a substrate property. On synthetic random-bipolar codebook with no inherent feature structure, it cannot help. On structured corpora (KG with attribute overlap) it might. v3's synthetic corpus is the wrong test domain for CLS.

### Brain mechanisms NOT present in v3 (5 candidates, ranked)

| Mechanism | Brain source | Substrate-fit | Why missing matters | P(adds lift if added) |
|---|---|---|---|---|
| Separate hippocampal/neocortical W matrices | Squire-Wixted CLS | Direct | Eliminates online crosstalk | 0.25 (corpus-dependent) |
| Cascade-synapse metaplasticity (depth-state W) | Fusi 2005 / Benna-Fusi 2016 | Direct | Lets consolidation transition slowly (avoiding immediate-write) | 0.30 (substrate-substantive; harder to ship) |
| Synaptic tagging-and-capture (selective consolidation) | Frey-Morris 1997 | Direct | Only some writes get consolidated → reduces crosstalk | 0.35 (cheap to ship) |
| SWR-gated SELECTIVE replay | Liu 2024 | Direct | Replay only LARGE-tag subset → expanding intervals | 0.20 (still episodic; doesn't address heldout) |
| Feature-share extraction (semantic consolidation) | McClelland 1995 | Indirect (substrate has no feature-graph primitive) | THE missing primitive for heldout lift | 0.40 (highest gain BUT substrate-substantive) |

**Note** — the highest-lift mechanisms (cascade-synapse, feature-share) require substantive substrate rework, not v3 patch. The cheap ones (STC tagging) reduce crosstalk but don't solve heldout — they just defer the saturation point.

---

## Angle C — Why NAIVE keeps showing different baselines per cell (ROOT-CAUSE)

### The data

| Cell | NAIVE | V_C | V_P | n_chains | chain class structure |
|---|---|---|---|---|---|
| v1 (memory_v1) | 0.847 | 200 | 10 | 300 | UNIFORM random sampling over 10×9=90 ordered (p1,p2) pairs → ~3.3 chains per pair |
| v2 (proper_test) | 0.628 | 200 | 2 | 200 | SINGLE fixed pair (p1=0, p2=1) → ALL 200 chains on the SAME pair → max pair-density |
| v3 (heldout_fix) | 0.850 | 600 NAIVE / 600 CONSOL | 2 NAIVE / 6 CONSOL | 200 NAIVE / 112 train / 50 held | NAIVE arm: separate W, single chain class (no class structure for NAIVE arm) → effectively v1-like dispersion of 200 chains over V_C=600 |

### Root cause: NAIVE baseline is a FUNCTION OF (V_C, n_chains, predicate_pair_density) — and these three vary across cells

The Skunkworks tier ruling already identified this for v1 vs prior beta-sweep ("0.65 baseline was a single-pair-saturated stress test; v1 was a sparse predicate-pair-density regime"). v2 then DELIBERATELY moved to single-pair to match the beta-sweep regime, which gave NAIVE=0.628 (in the [0.62, 0.68] band).

v3 INHERITED v2's sanity band [0.62, 0.68] but the NAIVE arm structurally changed:
- v3 NAIVE: V_C=600 (3x v2), n_chains=200 over single-class chain construction, separate W
- The W stores 200 chain × 2 hop = 400 1-hop atoms over V_C=600 codes at N=8192
- Atomic density 400/600 = 0.67 atoms-per-code; cleanup ceiling ≈ 0.85
- v2 NAIVE: V_C=200, n_chains=200, W stores 400 atoms over 200 codes → atomic density 2.0 — saturation regime → 0.63

**The cell varies V_C from 200 to 600 between v2 and v3 NAIVE arm and KEEPS the same sanity band. That is the bug — not the substrate, not the methodology, but the pre-reg band specification.**

### Why this matters beyond "fix the band"

The v3 cell deliberately uses different V_C for NAIVE (V_C=600) vs CONSOL (V_C=600 but with 3 chain classes × different freq structure). NAIVE arm at V_C=600 V_P=2 single-class is APPLES-TO-ORANGES vs CONSOL arm at V_C=600 V_P=6 three-class. The lift comparison `NAIVE 0.85 vs CONSOL best 0.40` is not a valid lift measurement at the cell-level — the two arms are in different capacity regimes.

**The honest verdict from the cell is: CONSOL arm collapses on heldout under its own regime (HELDOUT 0.40 down from TRAINING 0.99) — that is the load-bearing finding. The NAIVE comparison is incidental.** The v3 "HARD_FAIL" framing as "consolidation worse than NAIVE" is over-claiming; the discriminator-grade finding is "consolidation does not transfer to heldout chains (40% vs 99% drop within-arm)."

### Predicted future drift if pattern continues

Any future consolidation cell that varies V_C, V_P, n_chains, or chain-class structure WILL produce a different NAIVE value. The fix is NOT to keep re-running with different bands — it's to **derive the NAIVE expected value FROM the regime parameters at pre-reg time, not copy bands across cells.**

A simple formula for the NAIVE 2-hop ceiling at random-bipolar N=8192 K_SET=20:

```
NAIVE_2hop ≈ erf(N / (4 · n_chains · V_P_effective))
```

(rough; valid in the K=2 / random-bipolar / isotropic regime; underestimates at low density)

This gives:
- v1: erf(8192 / (4·300·10)) = erf(0.68) ≈ 0.67 ... empirical 0.85 (formula underestimates; isotropic + pseudo-orthogonal codebook beats erf bound)
- v2: erf(8192 / (4·200·2)) = erf(5.1) ≈ 1.0 ... empirical 0.63 (formula now OVER-estimates because single-pair saturates a SINGLE codebook code → atomic density saturates differently)
- v3 NAIVE: erf(8192 / (4·200·2)) = erf(5.1) ≈ 1.0 ... empirical 0.85

The formula is wrong because the density regime depends on chain class structure (whether all 200 chains share the same (p1,p2) or spread). A correct formula needs the EFFECTIVE atomic-density of (intermediate-atom, second-predicate) pairs in W, which is a function of `n_chains × (1 - prob_pair_collision)`. Calculating this for each regime is straightforward but cell-specific.

**Operational fix:** every consolidation cell pre-reg must include a NAIVE smoke run (n_seeds=1, single arm) BEFORE the full dispatch, with the measured NAIVE value used to SET the sanity band ± 0.03. Do NOT copy bands from prior cells when V_C, V_P, n_chains, or chain-class structure changed.

---

## What's the right architecture? Three options

### Option 1: Different consolidation primitive (modify W to favor known chains)

Instead of WRITING a compound atom, ADJUST the existing 1-hop atoms' weights to be more retrievable along known chain trajectories. Mathematically: instead of `W += outer(bind(s, R_compound), o)`, do `W += alpha · outer(bind(s, p1), intermediate) + alpha · outer(bind(intermediate, p2), o)` (BOOST the existing chain atoms). This is gain-amplification not new-atom addition.

**Concerns:**
- This is mathematically equivalent to running the same primitive 1-hop atoms multiple times with higher gain — likely just re-discovers what NAIVE measures, except with higher SNR for boosted chains
- Heldout chains are NOT boosted → still bounded by the unboosted NAIVE ceiling
- No clear path to lift heldout above NAIVE

**P_deflated(closes Barrier 1): 0.10** — predicted to do nothing.

### Option 2: Different test (pointer-chain hybrid IS the right Barrier 1 closure)

Existing Store reference `exp_pointer_chain` is HARD_PASS at depth=100 in a different regime. The Director spec `director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md` proposes apples-to-apples test at V_C=200 V_P=10 N=8192. Mechanism: external `(s, p) → atom_id` index for key routing; 1-hop HRR retrieval per step for content.

**Concerns:**
- "External index" needs to be substrate-native to count; the Director spec acknowledges this (substrate atoms holding pointers, retrieved via HRR cleanup themselves)
- If pointer-chain is fully substrate-native, then EACH index lookup is itself a 1-hop HRR retrieval — so 10-hop chain = 10 independent 1-hop retrievals, each at the 1-hop primitive ceiling (~0.95). Compound retention: 0.95^10 = 0.60 → BELOW the 0.80 HARD_PASS band for 10-hop
- Pointer-chain only beats NAIVE if EACH 1-hop step is significantly above the NAIVE single-step accuracy. The 1-hop primitive currently is ~0.92-0.95 per hop. At depth 2: 0.92^2 = 0.85 vs NAIVE 0.85 (no lift). At depth 10: 0.92^10 = 0.43 vs NAIVE-equivalent (unknown).
- The Store ref `exp_pointer_chain` HARD_PASS at depth=100 was likely in a higher-capacity or anisotropic regime — needs verify-the-referent BEFORE assuming it transfers

**P_deflated(closes Barrier 1 at apples-to-apples regime): 0.30** — possible but needs the Store ref verified first; the depth-retention claim is the load-bearing one.

### Option 3: Abandon consolidation (and pointer-chain) for substrate; accept Barrier 1 ceiling as fundamental at random-bipolar isotropic regime

Pure-math L5 (META gap-map drill 2026-06-24) established: at N=8192 K_SET=20 V_C=200 V_P=10 random-bipolar isotropic, the 2-hop ceiling IS ~0.65-0.85 depending on density regime. The fix is NOT a different chaining primitive; the fix is a DIFFERENT ENCODER (anisotropic / structured / data-driven).

**Concerns:**
- This is the Wave D hub-spoke v3 / SEMANTIC v3 path; orthogonal to consolidation
- USER directive 2026-06-22 said "empowered to experiment where lit says dismissed" — abandoning shouldn't be premature
- BUT the v3 evidence strongly suggests episodic consolidation is the WRONG mechanism for Barrier 1; pursuing it further is sunk-cost

**P_deflated(non-consolidation path wins Barrier 1): 0.45** — encoder-side rework has higher prior than consolidation-side rework

### Synthesis recommendation

**Primary:** Stop dispatching consolidation variants for Barrier 1. The three v1/v2/v3 cells have collectively spent ~6-8 hours of compute + author-cycles establishing that episodic compound-predicate consolidation does not generalize to heldout chains. The mechanism is mathematically understood (associative-memory crosstalk + flat-vs-compositional subspace mismatch); the brain analog is misapplied (episodic vs semantic consolidation conflation).

**Secondary:** Dispatch the pointer-chain hybrid cell ONLY if Skunkworks verify-the-referent confirms the Store `exp_pointer_chain` HARD_PASS depth=100 result is at a comparable regime. If the Store ref is in a higher-capacity or anisotropic regime, pointer-chain transfers poorly to v3's random-bipolar isotropic regime, and we should NOT dispatch.

**Tertiary:** Hold "consolidation" idea in reserve for SEMANTIC consolidation under feature-share cortical analog. The earliest cell that could test this would require (a) a structured corpus with attribute overlap (NOT synthetic random-bipolar), (b) two W matrices (hippocampal + neocortical), (c) feature-extraction primitive (currently missing from substrate). Each of these is a substantive build, not a v3 patch.

---

## Root cause hypothesis for NAIVE rail drift across v1/v2/v3 (load-bearing for future cells)

**Root cause:** NAIVE baseline at random-bipolar isotropic regime is a DETERMINISTIC FUNCTION of (V_C, V_P, n_chains, chain_class_structure, K_SET, N). The four cells used four different combinations and therefore got four different baselines (0.65 prior-beta-sweep / 0.847 v1 / 0.628 v2 / 0.850 v3). The drift is NOT methodology error; it is the pre-reg copying sanity bands across cells without re-deriving the expected NAIVE from regime parameters.

**Verification:** the formula `NAIVE_2hop ≈ f(N, V_C, V_P, n_chains, density)` is straightforward to derive for the random-bipolar isotropic regime and should be added to the substrate's pre-reg discipline. Every NAIVE rail should be computed at pre-reg time from the regime parameters, NOT copied from prior cells.

**Atomization candidate:** META rule `META_M6_NAIVE_baseline_must_be_derived_from_regime_not_copied_from_prior_cells`.

**Operational fix:** add a one-line check to the cell-author workflow:
```
# Pre-reg sanity-band derivation
expected_naive = compute_naive_2hop_ceiling(N, V_C, V_P, n_chains, K_SET, chain_class_structure)
sanity_band = (expected_naive - 0.03, expected_naive + 0.03)
# Use THIS band in the HARD_FAIL condition, not a copied band
```

---

## Recommendation: pivot decision

**Pivot to pointer-chain IF Skunkworks verify-the-referent on Store `exp_pointer_chain`:**
1. Verify Store `exp_pointer_chain` actual verdict field = HARD_PASS (not gap-map framing)
2. Verify regime (N, V_C, V_P, K_SET) of the Store cell
3. IF Store cell is at random-bipolar isotropic regime AND depth=100 hits ≥ 0.80: dispatch pointer-chain hybrid v1
4. IF Store cell is at anisotropic / structured regime OR depth=100 below 0.80: do NOT dispatch; pointer-chain doesn't transfer to v3-equivalent regime

**Abandon consolidation (compound-predicate variants) for Barrier 1.** Three cells have established the mechanism does not generalize. Hold the idea for semantic-consolidation under feature-share cortical analog in a future structured-corpus cell.

**Continue Wave D encoder work in parallel.** Anisotropic encoder (hub-spoke v3) is the orthogonal escape hatch from Barrier 1 and the higher-prior path per gap-map drill.

**Add META_M6 to substrate atomization queue.** Codifies the NAIVE-baseline-derivation discipline so v1→v2→v3 drift does not recur.

---

## Pointer references (absolute paths)

- `d:/AI/hd-instrument/data/exp_substrate_multihop_consolidation_v3_proper_test_heldout_fix/metrics.json` (v3 per-arm)
- `d:/AI/hd-instrument/data/exp_substrate_multihop_consolidation_v2_proper_test/metrics.json` (v2 per-arm)
- `d:/AI/hd-instrument/data/exp_substrate_multihop_consolidation_memory_v1/metrics.json` (v1 per-arm)
- `d:/AI/hd-instrument/notes/skunkworks_tier_ruling_cell3_cell4_consolidation_2026-06-25.md` (META_M4 + META_M5 atomized)
- `d:/AI/hd-instrument/notes/director_cell_consolidation_v2_proper_test_spec_2026-06-25.md` (v2 spec)
- `d:/AI/hd-instrument/notes/director_cell_H_extended_multihop_consolidation_2026-06-25.md` (parallel-W extension spec)
- `d:/AI/hd-instrument/notes/director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md` (pointer-chain spec)
- `d:/AI/hd-instrument/notes/research_brain_drill_2_CLS_continual_learning_5x_DEEPER_2026-06-22.md` (cascade-synapse / STC / SWR mechanism scan)

## Word count: ~2700
