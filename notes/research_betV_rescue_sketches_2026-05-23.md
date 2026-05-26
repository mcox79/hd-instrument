# Research: Bet V self-reflective memory -- 5 axis-combination rescue sketches

**Date**: 2026-05-23
**Trigger**: `notes/strategy_request_to_research_betT_betV_rescue_sketches_2026-05-23.md` (Strategy cycle 178, v158); back-fills PROT-004/006 rehab discipline for 🟡 PARTIAL Bet V (54 cap_map versions stale since cycle 102-103 v102-v103 gap=0.424 at largeN).
**Drill type**: axis-combination rehabilitation per [[feedback-rehabilitation-after-rejection]] (5 sketches before any closure call).
**Method**: 1 broad Sonnet-equivalent WebSearch pass over generic-math literature (VSA/HDC binding, metacognition + confidence-conditioned retrieval, HRR iterative inversion, modern dense AM at large N) per [[feedback-query-privacy-decomposition]]; Opus synthesis with calibrated P estimates and explicit hard-fail thresholds.
**Calibration**: deflated P by 0.20-0.25 per [[feedback-lit-scan-calibration-penalty]] (substrate operating regime -- N=524K-1M envelope confirmed (v148/v150), substrate is intermediate hybrid regime per cycle 103 v103 -- has no direct published precedent for second-order meta-bindings at this scale). Novel-synthesis cap P=0.50 enforced.

---

## (a) HEADLINE

**Top-ranked rescue path**: Sketch 3 -- confidence-conditioned cleanup (Bet G TEMPSCALE thresholding on meta-queries) -- `P_deflated = 0.45`. Cheap decisive test ~5-10 min CPU. The current Bet V gap (0.285 at smallN -> 0.424 at largeN; meta-retrieval is ~30-42% worse than first-order retrieval) is most plausibly a readout-threshold problem: meta-information has a NARROWER margin than first-order facts because it's a derived/second-order binding, but the cleanup operator uses the same beta threshold for both. Confidence-conditioned cleanup gates meta-queries through a higher-confidence threshold so that low-confidence meta-hits are rejected (returned as "unknown") rather than misclassified, lifting effective accuracy without retraining the substrate.

**One-sentence form**: Bet V's gap=0.424 is a "we are returning low-confidence guesses as answers" problem, not a "we cannot store meta-info" problem -- the substrate stores meta-bindings but the readout aggregates them at a margin where they are below the noise floor of first-order facts.

**Top-5 vetted ranking** (after deflation; novel-synthesis cap enforced):

| Rank | Sketch (axis combination) | P (deflated) | Cheap test cost | Why ranked here |
|---|---|---|---|---|
| 1 | #3 Confidence-conditioned cleanup (Bet G TEMPSCALE meta-gate) | 0.45 | ~5-10 min CPU | Smallest intervention; reuses existing TEMPSCALE infrastructure; metacognition lit (Koriat 1997, signal-detection framework) supports confidence-gating as primary metamem mechanism |
| 2 | #4 Provenance chain encoding (source_id (x) update_step (x) confidence triple) | 0.40 | ~15-20 min CPU | Composes with Lane D 4-primitive demo (cycle 168 v143); HRR/VSA binding lit supports triple-binding tractability; substrate-product wedge (provenance is a customer ask) |
| 3 | #1 Meta-binding hierarchy (separate meta_W bound to first-order via cross-tag) | 0.35 | ~30-45 min CPU | Architecturally cleanest; but doubles substrate state; deflated further because adding a second W introduces new capacity/calibration questions |
| 4 | #2 N=65536 scaling re-test with proper cleanup operator | 0.30 | ~20-30 min CPU on cluster | Cycle 102-103 gap scaled positively with N (0.285 -> 0.424); needs the v100 beta=c/N calibration applied at largeN; possibility of negative scaling at very-largeN is plausible per v148 N=524K + v150 N=1M envelope |
| 5 | #5 HRR iterative meta-refinement (Plate-style inversion of meta-bindings) | 0.30 | ~20-30 min CPU | HRR iterative unbinding is published (Kanerva 2009, Plate 1995); substrate has the primitive; but iterative refinement on second-order bindings is not directly precedented |

Sketch #2 and #5 are deferred unless #1-#3 fail; #4 is a strong candidate that composes immediately with the existing Lane D wedge.

---

## (b) Cheap decisive test (top-ranked path)

**Test name**: `wave14_betV_confidence_gated_cleanup_v1`

**Action**: Re-analyze the cycle 102-103 FULL Bet V data already on disk. For each (meta-query, ground-truth) pair, compute the cleanup operator's confidence margin (top-1 softmax probability at the substrate's current beta). Sweep a confidence threshold tau in {0.50, 0.60, 0.70, 0.80, 0.90} and for each threshold report (i) `acc_above_tau` = accuracy on items where confidence >= tau; (ii) `coverage` = fraction of items above threshold; (iii) effective `gap = first_order_acc - meta_acc_above_tau`.

The hypothesis: at a threshold tau*, `acc_above_tau` >= 0.85 on meta-queries while coverage stays >= 0.50 (i.e., we can answer at least half of meta-queries with high confidence and >85% accuracy). If this holds, the gap collapses to within noise of first-order accuracy on the high-confidence subset, and Bet V is rescued as a "high-confidence subset retrieval" capability.

**No new substrate change**. Confidence-conditioned cleanup is a readout-side wrapper. Cost: <10 min CPU including all 5 threshold cells; pure post-hoc on existing cycle 102-103 measurements (the substrate's TEMPSCALE logits are persisted per v100 calibration infrastructure).

**If mechanism #3 fails the cheap test** (no threshold tau achieves both acc_above_tau >= 0.85 AND coverage >= 0.50): fall through to mechanism #4 (provenance chain) at ~15-20 min CPU. The provenance chain test reuses the Lane D 4-primitive composition pipeline from cycle 168 v143 (S+T+U+X primitives) with a 5th primitive (provenance) added.

**If mechanisms #3 and #4 both fail**: fall through to #1 (meta-binding hierarchy). Cost ~30-45 min CPU + substrate-side build of a second `meta_W` matrix. This is the largest single rescue build.

---

## (c) Falsifiable predictions with HARD PASS / HARD FAIL

### Prediction Sketch #3 (confidence-conditioned cleanup; P_deflated=0.45)

- **HARD PASS**: There exists a threshold tau* in [0.60, 0.80] such that on the cycle 102-103 FULL meta-query set, `acc_above_tau* >= 0.85` AND `coverage(tau*) >= 0.50` across 3 seeds. Equivalently, the substrate can answer at least half of meta-queries with >=85% accuracy.
- **HARD FAIL**: If for ALL tau in {0.50,...,0.90} either `acc_above_tau < 0.75` (no useful subset exists even at the strictest threshold) OR `coverage(tau) < 0.20 when acc_above_tau >= 0.85` (the high-accuracy subset is too small to be useful), mechanism #3 is REFUTED.
- **Pre-registered margin**: 0.85 is 0.42 above current 0.43 = (1 - gap_at_largeN) approximation; this is a substantial lift, deliberate so that PASS demonstrates real product value not just statistical noise.

### Prediction Sketch #4 (provenance chain encoding; P_deflated=0.40)

- **HARD PASS**: Provenance triple `source_id (x) update_step (x) confidence` retrieved with traceback accuracy >= 0.90 at chain depth <= 3 across 3 seeds, AND first-order accuracy is NOT degraded by more than 0.05 from the baseline (i.e., adding the provenance binding does not bleed retrieval quality from first-order facts).
- **HARD FAIL**: Traceback accuracy < 0.65 at depth=3 (substrate cannot carry the triple binding across multi-step provenance chains), OR first-order accuracy drops by >0.10 (provenance binding interferes destructively with first-order retrieval).

### Prediction Sketch #1 (meta-binding hierarchy meta_W; P_deflated=0.35)

- **HARD PASS**: With a separate `meta_W` (same N=4096 dim, independent storage) bound to first-order via cross-tag, `gap <= 0.20 at largeN` across 3 seeds at N=16384. (Half-or-better closure of current 0.424 gap.)
- **HARD FAIL**: `gap > 0.40 at largeN` (no improvement; current gap is 0.424 so this is essentially no movement), OR meta_W storage doubles substrate memory footprint without lifting capability above what mechanism #3 already provides at zero new storage.

### Prediction Sketch #2 (N=65536 scaling with beta=c/N calibrated cleanup; P_deflated=0.30)

- **HARD PASS**: At N=65536 with cycle 100 calibrated beta=0.5 (NOT beta=32 used at cycle 102-103), `gap monotone decreasing past N=32768` AND `gap(N=65536) <= 0.30` (significant improvement on the 0.424 at smallN trajectory).
- **HARD FAIL**: `gap > 0.50 at N=65536` (positive scaling continues), OR substrate OOMs at N=65536 in the Bet V protocol (relevant given cycle 174-175-176 OOM history at Bet A continual edits).
- **Note**: This is the only sketch with notable hardware risk; sweeps A/B from v155 show N=65536 protocols frequently hit the 8GB VRAM budget. Mechanism #2's cheap test should run at N=32768 first to validate the scaling direction before committing to N=65536.

### Prediction Sketch #5 (HRR iterative meta-refinement; P_deflated=0.30)

- **HARD PASS**: 5 iterations of HRR-style inverse-unbind on meta-bindings reduce gap by >=50% (i.e., 0.424 -> 0.21 or better) across 3 seeds without inducing convergence to spurious states.
- **HARD FAIL**: Gap reduction < 10% over 5 iterations (iteration does not help), OR substrate converges to a spurious state (iterated meta-refinement amplifies noise rather than reducing it; check via 28-element ENDPOINT_COLLAPSED basin test from cycle 137-148 -- if final state is in the 28-element basin set, that's fine; if not, that's spurious).

---

## (d) Cross-thread synthesis with prior Entries

### Connection to Bet G TEMPSCALE (cycle 86-90) and v100 beta=c/N

The same calibration insight that drives mechanism #2 in the Bet T note also applies here. Cycle 100 v100 measured beta=c/N with c=32768; at N=4096 (cycle 102-103 small-N) optimal beta=8, at N=16384 (cycle 102-103 largeN) optimal beta=2. The cycle 102-103 measurement was done at the (now-known mis-calibrated) beta=32 -- which is 4x too large at small-N and 16x too large at large-N. The fact that the gap WORSENED with N (0.285 -> 0.424) is exactly what one would expect from a beta that drifts further from optimal as N grows. Mechanism #2 directly addresses this; mechanism #3 (confidence threshold) sidesteps it by gating the readout. Both should be on the table; #3 is ranked first because it's a smaller intervention.

### Connection to Lane D 4-primitive composition (cycle 168 v143)

The Lane D wedge demonstrates 4 primitives composing at FULL: Bet S, T, U, X. Adding Bet V (or its provenance-chain extension under mechanism #4) makes it a 5-primitive demo and directly composes with the existing customer-facing narrative ("substrate carries its own self-knowledge -- you can query why it knows what it knows"). Mechanism #4 is therefore a substrate-product priority even though its P=0.40 is slightly below #3's 0.45.

### Connection to Bet Y V2.D drop (cycle 106)

Bet Y V2.D was originally meant to extend Bet V at N=65536 via modern-dense-AM cleanup; cycle 106 simplification DROPPED that aspect. The substrate has since demonstrated FULL at N=131K (v143), N=262K (v145), N=524K (v148), N=1M (v150) -- all FAR past the original Bet V V2.D scope. So the N-scaling test (mechanism #2) is now empirically viable at much higher N than originally proposed, IF the calibrated beta is applied. The v148/v150 N-envelope confirms the substrate operates at very-largeN; the open question is whether Bet V's gap closes there.

### Connection to v149 ORDER_PARAM and v150 ORDER_PARAM_SUB_REGION_STABLE

v149 found that the Parisi-like q_overlap order parameter is REFUTED globally but v150 found it STABLE in sub-regions (multi-component q-structure). This is structurally relevant to mechanism #1 (meta-binding hierarchy): the substrate has multiple coexisting "phases" in q-overlap space, and meta_W could be designed to live in a DIFFERENT q-region than first-order W (interference reduction by phase separation). This is a refined version of #1 that may justify lifting its P estimate; recorded as a free hypothesis for the Strategy → Exp Dev pickup.

### Connection to v153 COSET_UNIFORM_NONLINEAR + v152 anti-RM(1,16)

Provenance chain encoding (mechanism #4) requires triple-binding source_id (x) update_step (x) confidence. Each component should be drawn from the substrate's preferred nonlinear coset structure (per v153) rather than RM(1,16) linear codes (per v152 refutation). This is a non-trivial design constraint but the substrate's COSET_UNIFORM_NONLINEAR preference is already known, so the codeword selection is unambiguous.

### Connection to PROT-009 + Bet V smoke-FULL divergence

Bet V was the second of the 5-anchored smoke-not-predictive divergences (cycle 102 smoke 0.358/0.386 KILLED -> FULL PARTIAL gap=0.285 at smallN, then 0.424 at largeN). The smoke and FULL went in OPPOSITE directions: smoke said "no signal" (gap indistinguishable from chance), FULL said "real signal but with a gap." This is the most extreme smoke-FULL pattern in the substrate's history. It argues that Bet V's substrate signal is at a margin where smoke noise drowns it. The cheap test for mechanism #3 -- which extracts the high-confidence subset -- exploits exactly this: at the high-confidence subset, the signal is well above noise and smoke would have agreed.

---

## (e) Substrate-product implications

If mechanism #3 PASSES at HARD PASS threshold (acc_above_tau* >= 0.85 at coverage >= 0.50):

- **Cap 14 Self-Reflective Memory** becomes a fresh ✅ row with a product caveat: "substrate provides high-confidence meta-information retrieval over 50%+ of queries with >85% accuracy; low-confidence meta-queries return 'unknown' rather than guesses." This is product-honest and is a fresh capability lift from 🟡 PARTIAL after 54 stagnant versions.
- Composes with Cap 1 Crooks (forensic erase): per-fact meta-information includes confidence + provenance + update history; customers can audit "what does the substrate know about X, and how sure is it, and when did it last update?" -- a real wedge over vector DB baselines.
- Composes with Lane D 4-primitive demo (cycle 168 v143): becomes 5-primitive demo, strengthening the cognitive architecture narrative.
- Composes with Bet T rescue (if both pass): per-hypothesis confidence + meta-information per hypothesis gives "substrate carries N competing hypotheses each with its own confidence-gated self-knowledge" -- a strong differentiator.

If mechanism #3 FAILS but mechanism #4 (provenance chain) PASSES:

- Cap 14 becomes a ✅ row with the provenance-chain framing: "substrate provides full provenance traceback at depth <=3 with >=90% accuracy, with first-order retrieval preserved." Slightly weaker than #3 but still product-useful; specifically pairs with Cap 1 forensic erase (per-fact provenance + per-fact erase certificate is a coherent compliance/audit story).

If all 5 sketches FAIL their HARD PASS thresholds:

- File PROT-004/006 ❌ closure (provisional) on Bet V at the next Strategy cycle. Substrate-product impact: Cap portfolio loses the self-reflective memory differentiator; remaining 12 capabilities still hold. Lane D 4-primitive demo continues to work but does NOT extend to 5 primitives via Bet V. The substrate cannot claim "auditable self-knowledge" -- a real product cost.

### Combined Bet T + Bet V substrate-product implication (if both pan out)

Both pan out gives substrate two NEW Cap rows (13 + 14) lifting portfolio from 12 to 14 demonstrated capabilities, both connecting to the existing Cap 1 forensic erase + Lane D wedge. The combined narrative becomes: "substrate maintains K_hyp parallel hypotheses, each with calibrated per-hypothesis confidence AND per-hypothesis provenance + meta-information retrievable above a configurable confidence threshold." This is a coherent product story that distinguishes substrate from (i) vector DBs (no calibrated confidence, no per-hyp provenance) and (ii) LLM-only systems (no auditable per-fact erase + no decoupled hypothesis tracking). Both rescues hit "auditable third memory type" framing from the AI memory subsystem direction (locked 2026-05-22 per MEMORY index).

Per [[feedback-no-papers-product-only]]: every framing above is substrate-product. Per [[feedback-value-creation-not-competition]]: the wedge is enabling K_hyp + per-hyp provenance, not winning a benchmark.

---

## (f) Verified citations

1. Plate, T. "Holographic Reduced Representations: Distributed Representation for Cognitive Structures." CSLI 2003. (HRR binding/unbinding, circular convolution.)
2. Plate, T. "Encoding Structure in HRR." 1994 / IEEE TNN 1995. (Iterative inversion; bidirectional recall.)
3. Kanerva, P. "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors." Cognitive Computation 2009. (VSA primitive availability, including iterative refinement.)
4. Kleyko, D. et al. "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I." CSUR 2022. (Modern survey; binding/bundling/permutation operations.)
5. Schlegel, K. et al. "A Comparison of VSAs." Neural Computing & Applications 2022. (Operator choice across VSAs.)
6. Ramsauer, H. et al. "Hopfield Networks is All You Need." ICLR 2021. (Modern dense AM exponential capacity; relevant to mechanism #2 N-scaling.)
7. Lucibello, C., Mezard, M. "Exponential Capacity of Dense Associative Memories." PRL 2024. (beta=O(1/N) scaling; substrate-relevant per cycle 93 + v100.)
8. Koriat, A. "Monitoring One's Own Knowledge During Study: A Cue-Utilization Approach to Judgments of Learning." JEP:G 1997. (Metacognitive monitoring; confidence-cue framework.)
9. Pleskac, T.J. & Busemeyer, J. "Two-stage dynamic signal detection: A theory of choice, decision time, and confidence." Psych Review 2010. (Signal-detection framework for confidence-gated retrieval.)
10. Hebart, M.N. et al. (and broader metacognition lit search returned PMC7901934, Nature Sci Rep 2024 41598-024-76208-0). (Confidence-conditioned metamemory accuracy; gap between item and meta accuracy.)

Plus internal hd-instrument references: cycle 75 v75 (Bet V spec), cycle 86-90 (Bet G TEMPSCALE), cycle 100 v100 (beta=c/N calibration), cycle 102-103 v102-v103 (Bet V FULL PARTIAL gap=0.285 -> 0.424), cycle 106 (V2.D drop), cycle 137-148 (28-element ENDPOINT_COLLAPSED), cycle 145 v145 (N=524K smoke), cycle 148 v148 (N=524K FULL), cycle 150 v150 (N=1M FULL + ORDER_PARAM_SUB_REGION_STABLE), cycle 152 v152 (RM(1,16) REFUTED), cycle 153 v153 (Cap 1 commercial wedge + COSET_UNIFORM_NONLINEAR), cycle 168 v143 (Lane D 4-primitive demo).

Verified count: 10 external + 13 internal = 23.

---

## Summary one-liner

Top-ranked Bet V rescue: confidence-conditioned cleanup with TEMPSCALE-gated meta-queries (Bet G extension); P=0.45 deflated; cheap test = post-hoc tau-sweep on cycle 102-103 FULL data, <10 min CPU; HARD PASS = exists tau* in [0.60,0.80] with acc_above_tau* >= 0.85 AND coverage >= 0.50; HARD FAIL = acc_above_tau < 0.75 for all tau OR (acc>=0.85 only at coverage <0.20).
