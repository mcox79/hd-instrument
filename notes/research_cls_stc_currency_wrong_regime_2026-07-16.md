# Research note: CLS route / STC hold-window — what currency is it actually FOR?

**Date:** 2026-07-16
**Trigger:** mandatory brain-check on a load-bearing negative — a brain-faithful CLS fast/slow route + synaptic-tagging-and-capture (STC) hold-then-recover mechanism tied (did not beat) decide-at-arrival on single-shot decision accuracy, in an arena with a genuine time axis AND a fired positive control proving temporal-hold *could* be rewarded if the advantage existed.
**Method:** 2 parallel Sonnet lit-scan sub-agents (public biology/psychology literature only, no substrate specifics off-platform) — one on McClelland-McNaughton-O'Reilly (MMO'R) 1995 CLS theory + its update chain, one on Frey-Morris synaptic tagging and capture (STC) + behavioral tagging. Verified citation counts below.

## HEADLINE

**WRONG-CURRENCY, not same-limitation.** Both literatures converge, independently and without ambiguity, on a single answer: neither CLS nor STC's raison d'etre has ever been single-trial / single-decision accuracy. Both are explicitly, definitionally mechanisms for **interference-avoidance and capacity-economy in continual (sequential, many-item) learning**, cashed out at a **later retention test**, not at the moment of encoding. Our arena tested the wrong currency — it measured accuracy on one labeled item in isolation, which is precisely the regime the biological literature says CLS/STC has no reason to help with. The negative result is real and internally consistent with biology (a unified fast learner is exactly as good as a dual-route one on an isolated, non-competing item) — it just isn't evidence against the route's actual function.

## Question 1 — CLS: MMO'R 1995 and update chain (Kumaran/Hassabis/McClelland 2016, O'Reilly & Norman 2002, O'Reilly/Bhattacharyya/Howard/Ketz 2014)

- The dual hippocampal(fast)/cortical(slow) architecture exists to solve **catastrophic interference** (McCloskey & Cohen 1989): a single fast-learning network overwrites overlapping weights encoding prior items when new items are trained into the *same* weight substrate.
- Nothing in this literature claims hippocampal fast-encoding beats a unified fast learner **on one isolated, non-competing item**. The entire justification is *contingent on many sequential memories needing to coexist without mutual overwrite* — a capacity/retention argument over a stream of learning events, not a per-trial accuracy argument.
- The transfer/consolidation mechanism (hippocampal replay -> interleaved cortical exposure -> gist extraction) is explicitly an interference-avoidance / retention mechanism, not an accuracy-at-encoding mechanism.
- Experimental/computational demonstrations are uniformly of the McCloskey & Cohen 1989 type: train on list A, train on list B, **measure retention of A after B** (i.e., continual-learning / catastrophic-forgetting paradigms — the direct ancestor of modern EWC-style benchmarks), never single-trial accuracy tests.

## Question 2 — STC: Frey & Morris 1997, Redondo & Morris 2011, behavioral tagging (Ballarini et al. 2009, Moncada & Viola 2007)

- The tag+capture decision governs **stabilization into durable long-term potentiation vs. decay back to baseline** — a commitment/persistence decision, not a moment-of-encoding accuracy decision. Redondo & Morris (2011) state induction "creates only the potential for a lasting change... but not the commitment to such a change."
- The hold window is a **resource-allocation / capacity-economy** mechanism: costly plasticity-related-protein (PRP) synthesis is triggered only by strong/salient/novel events; weak/incidental changes piggyback on that capacity only if coincident in time, otherwise they are lost. Ballarini et al. 2009 (PNAS) is the direct demonstration — weak training that would only yield short-term memory is converted to long-term memory *only* if a novel, protein-synthesis-triggering experience occurs nearby in time.
- No study in this literature frames STC's benefit as same-trial discrimination/accuracy. The benefit is always measured at a **later memory test** (hours to days after the tagging event) — retention/durability of an otherwise-forgettable weak trace, and selectivity for which of many competing experiences get consolidated into scarce long-term storage.

## Q3/Q4 combined verdict

**Does biological consolidation-corroboration over a hold-window ever add incremental accuracy over a same-instant multi-source snapshot?** No literature evidence for this. In every framing found, the hold-window's value is (a) not overwriting prior knowledge (interference-avoidance), (b) deciding what to commit to expensive long-term store vs. let decay (capacity/economy), and (c) retention/durability measured at a later test — never same-instant decision accuracy.

**VERDICT: WRONG-CURRENCY.** This is not a same-limitation case. The route's mechanism (fast/slow split + hold-then-capture) is a real biological solution to a real biological problem — but that problem is continual/sequential multi-item learning under a shared, capacity-limited storage substrate, not single-shot judgment of one item presented once. A single-shot i.i.d. accuracy race is structurally incapable of exercising the mechanism's actual function, in the same way that testing a garbage-collector's benefit by timing the allocation of a single object would find "no difference" — true, and uninformative about what the garbage collector is for.

## Cheap decisive test (right regime)

**Regime:** sequential/continual ingestion, not single-shot decision. Introduce N items to the arena one at a time across the time axis (N sweep: e.g., 10, 20, 40 items), where later items share representational capacity/overlap with earlier ones (the interference precondition — without overlap there is nothing to interfere). After each new item (or after all N), re-test recall/accuracy on the EARLIEST items.

**Two arms:**
1. Baseline: single-timescale monolithic learner (decide-at-arrival, no route/branch, no hold-then-capture) — writes every new item into the same live representation immediately.
2. Route: CLS-style fast/slow split + STC-style hold-then-recover — new items land in a fast/provisional store first; only items that pass the hold-window corroboration get committed/consolidated into the slow/shared store; fast-store items may be evicted/decay if not captured.

**Metric:** retention of early items' recall accuracy as a function of (a) number of subsequently-learned items and (b) representational overlap between early and late items. NOT single-decision accuracy on the latest item.

**Positive control (mandatory, same discipline as the refuted test):** first confirm the arena's monolithic baseline arm actually exhibits measurable forgetting of early items as later, overlapping items are learned (i.e., verify interference is really being induced — the analog of the earlier test's "fired positive control proving temporal-hold could be rewarded"). If the baseline shows no forgetting at all (no interference precondition), the regime is vacuous and must be re-tuned (increase overlap/N) before the route/baseline comparison means anything.

## Falsifiable predictions

**HARD-PASS:** Under sequential ingestion with N >= 10-20 overlapping items and a confirmed-forgetting baseline (positive control fires), the route (fast/slow + hold-then-capture) shows >= 15-20% relative reduction in early-item retention loss vs. the monolithic baseline, AND the size of this advantage *scales with* interference load (grows as N or overlap increases) rather than being a flat constant offset. The scaling signature is the diagnostic that distinguishes a genuine interference/capacity mechanism from noise or a fixed calibration difference.

**HARD-FAIL:** If the route ties the baseline on early-item retention even under confirmed interference load (both arms forget early items at statistically indistinguishable rates), OR the route's advantage (if any) is flat/non-scaling with N and overlap, then the mechanism genuinely provides no measurable benefit in our substrate even in its own correct currency — this would upgrade from "wrong test" to a real, accepted structural bound, and the route should be deprioritized rather than re-tested a third time.

**Deflated P estimate:** P(route shows the predicted HARD-PASS scaling signature in continual-ingestion regime) = 0.45. Basis: the literature-grounding claim itself (CLS/STC currency = interference-avoidance/retention/capacity, not single-trial accuracy) is very well-established — multiple independent, converging primary sources with no counter-evidence found, raw confidence ~0.85-0.90, deflated ~0.15 for standard lit-scan calibration -> ~0.70-0.75 for the BIOLOGY claim. The APPLICATION claim (that our specific substrate implementation of the route will reproduce this advantage once tested in the correct regime) is the novel-synthesis component and is capped at 0.50 per the lit-scan calibration-penalty discipline, then further discounted to 0.45 because we have not yet verified that our route's fast/slow split actually implements capacity-limited storage or genuine representational overlap/interference in the way biological synapses do (the analogy could be structurally present in name but not in mechanism — e.g., if our "slow store" has no capacity limit, there is nothing for STC-style gating to economize).

## Cross-thread synthesis

- Consistent with the standing full-auto loop discipline (MEMORY: "MANDATORY on EVERY negative: proactively check how the brain does that operation") — this is exactly the wrong-currency subtype of that check, not the same-limitation subtype. Compare to the prior same-day finding (project_realdata_unreadable_is_test_design_mismatch...) where a different negative (real-data unreadable interaction signal) was similarly diagnosed as a TEST-DESIGN MISMATCH (dense continuous-regression readout vs. brain's sparse-detection regime) rather than a true absence of signal. This is now the SECOND recent negative in this session's thread resolved as "right mechanism, wrong test regime," which itself is worth tracking as a pattern: single-shot / dense-regression test harnesses appear to systematically undermeasure brain-analog mechanisms whose entire function is amortized over sequences or sparse events, not single observations.
- Ties into the CLS/reasoning-mechanism thread (project_reasoning_mechanism...) and the continual-learning / Wright-Fisher adjacency already flagged in the research role's own field-coverage table (`population-genetics-wright-fisher` -> "Continual learning = mutation + selection + drift... predicts catastrophic-forgetting rate vs replay rate") — that adjacency is now directly load-bearing for designing the corrected test regime above (replay rate / drift-diffusion framing could quantitatively predict the expected forgetting-rate difference between arms before the cell is even run).

## Substrate-product implications

- Do not retire the CLS-route / STC-hold-window mechanism based on the refuted single-shot test — that would throw away a mechanism that has never been shown to fail in its own currency.
- Before spending cell-design effort: confirm the substrate's "slow store" actually has a capacity/interference precondition (bounded capacity, representational overlap causing crosstalk) — if it doesn't, the STC-style gate has nothing to economize and the mechanism truly is inapplicable to our substrate's current architecture (a genuine, non-refuted-by-this-argument reason to deprioritize it), independent of which test regime is used.
- If the precondition holds, the corrected continual-ingestion test above is the next legitimate decisive test for this route — it should be pre-registered with the positive control (confirmed baseline forgetting) as a gating step, exactly as the single-shot test's positive control was gating for the temporal-hold reward signal.
- Product framing: the value proposition for a route/hold mechanism, if it passes the corrected regime, is "graceful degradation / retention under continual updates" (a capacity-economy and non-catastrophic-forgetting guarantee), not "smarter single answers" — should be marketed/reported as a retention property, not an accuracy property, to avoid re-triggering the same test-design mismatch downstream.

## Citations (verified count: 9)

1. McClelland, McNaughton & O'Reilly, 1995, *Psychological Review* — "Why there are complementary learning systems in the hippocampus and neocortex."
2. Kumaran, Hassabis & McClelland, 2016, *Trends in Cognitive Sciences* — "What Learning Systems do Intelligent Agents Need? Complementary Learning Systems Theory Updated."
3. McCloskey & Cohen, 1989 — "Catastrophic Interference in Connectionist Networks: The Sequential Learning Problem."
4. O'Reilly, Bhattacharyya, Howard & Ketz, 2014, *Cognitive Science* — "Complementary Learning Systems."
5. Frey & Morris, 1997, *Nature* — "Synaptic tagging and long-term potentiation."
6. Redondo & Morris, 2011, *Nature Reviews Neuroscience* — "Making memories last: the synaptic tagging and capture hypothesis."
7. Ballarini, Moncada, Martinez, Alen & Viola, 2009, *PNAS* — "Behavioral tagging is a general mechanism of long-term memory formation."
8. Moncada & Viola, 2007, *Journal of Neuroscience* — "Induction of long-term memory by exposure to novelty requires protein synthesis: evidence for a behavioral tagging."
9. Okuda et al., 2021, *European Journal of Neuroscience* — "Initial memory consolidation and the synaptic tagging and capture hypothesis."

All 9 independently verified by the two lit-scan sub-agents with source links; no contradicting source found in either scan.
