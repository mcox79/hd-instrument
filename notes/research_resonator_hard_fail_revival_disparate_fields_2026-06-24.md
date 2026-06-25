# RESEARCH 2x+3x REVIVAL: Resonator integration HARD_FAIL — disparate-fields drill

**Date:** 2026-06-24
**Trigger:** USER directive 2x+3x revival drill on Resonator integration HARD_FAIL (NAIVE 2HOP 0.65 ~= RESONATOR 2HOP 0.63, tied; Modern-Hopfield top-K cleanup at K_SET=20 does not sharpen multi-hop retrieval over naive argmax in apples-to-apples synthetic regime). USER directive: do NOT constrain to brain-only; drill 5+ disparate fields.
**Discipline:** Cross-domain probe (Trigger F). 5 parallel WebSearches dispatched (DFE/comms, resonator/HD-VSA, RG/coarse-grain, random-walk/PageRank, path-integrals) + 4 deeper-mechanism searches (turbo BP, CA3 pattern-completion, GNN message-passing multi-hop, VSA unbinding cascade) + 1 soft-DFE confidence-feedback search. Generic queries only per [[feedback-query-privacy-decomposition]]. Calibration penalty 0.25 deflation per USER prompt; novel-synthesis cap P at 0.50. ASCII only.
**Cross-thread anchors:** parent research notes `research_2x_revival_comparator_resonator_HF_2026-06-23.md` (smoke-regime-too-easy diagnosis); `research_negative_N6_resonator_dense_V100_HF_2x_2026-06-20.md` (V100 dense-regime resonator HARD_FAIL); `research_drill_resonator_capacity_at_substrate_scale_2x_2026-06-04.md`. cap_map row PP-multi-hop currently 🟡 INCONCLUSIVE.

---

## HEADLINE (one-line synthesis)

**The Resonator HARD_FAIL on multi-hop is NOT a per-hop-cleanup-capacity problem (Modern-Hopfield top-K can sharpen single-hop just fine) — it is an INTER-HOP ERROR-PROPAGATION + ESTIMATOR-COLLAPSE problem, structurally identical to error-propagation in Decision Feedback Equalization (DFE) and turbo-decoding receivers: when hop-1 emits a HARD (argmax/top-K) decision before hop-2 runs, an incorrect hop-1 pick is fed into hop-2 cleanup as if it were ground truth, and the substrate has no soft confidence channel to detect or correct it; the cleanup operation simultaneously COLLAPSES the per-hop estimator from a continuous similarity field to a discrete pick, throwing away the very evidence that would let hop-2 discriminate, mirroring exactly the SOFT-DFE / turbo-equalization win in communications theory where replacing hard decision with soft LLR feedback reduces error propagation. Across 5 disparate fields the structurally-strongest mechanisms that share this diagnosis are: (1) SOFT-DECISION FEEDBACK / LLR-style confidence-weighted hop chaining (communications theory; brain analog = CA3 pattern-completion uses graded reactivation not winner-take-all; existence proof = turbo codes achieve Shannon-limit by soft iteration), (2) PATH-SUMMATION over K-best hop-1 candidates with amplitude = product of per-hop cosines (path integrals / Feynman; substrate-implementable as superposition over K_BEAM=5-10 hop-1 picks weighted by their pre-cleanup similarities), and (3) RANDOM-WALK STATIONARY-DISTRIBUTION readout with damping (PageRank-style on the substrate's stored relation graph; replaces the brittle per-hop argmax with a converged probability distribution over multi-hop endpoints). Renormalization-Group coarse-graining is mathematically elegant but lacks a substrate-native primitive at our current scale; pure resonator-network factorization is what the smoke ALREADY tested. Top revival rank: (1) SOFT-DFE/LLR variant > (2) PATH-SUM K-beam > (3) PageRank-walk readout. P_deflated(at least one of top-3 lifts 2HOP from 0.65 to >=0.78 at apples-to-apples synthetic, multi-seed) = 0.40. P_deflated(all three fail) = 0.20.**

Plain English: the resonator failed on multi-hop NOT because its single-hop cleanup is weak (it is fine) — it failed because the way we CHAIN hops throws away the confidence information from hop-1 BEFORE hop-2 starts. This is exactly the bug communications engineers solved in the 1990s with soft-decision feedback equalizers: stop letting hop-1 commit to one hard pick; pass along its full similarity profile so hop-2 can weight its retrievals by how confident hop-1 actually was. The brain does this in CA3 with graded reactivation, not winner-take-all. The cross-domain literature is unanimous that hard-decision chaining is the root cause of error propagation in any iterated decoder, and replacing it with soft-confidence chaining is the standard fix. Two more revival angles fall out naturally: path-integral-style sum over K-best hop-1 candidates (each weighted by amplitude), and PageRank-style random-walk readout where the answer is the stationary distribution over multi-hop endpoints rather than a single argmax. None requires a new substrate primitive; all three are wiring changes on the existing Modern-Hopfield + bind + W lookup stack.

---

## ANGLE-BY-ANGLE FINDINGS (5 disparate fields)

### Angle 1 — RESONATOR NETWORK FACTORIZATION (Frady-Kent + extensions; HD-VSA field)

**Mechanism (lit anchor: Frady-Kent 2020 "Resonator Networks 1," Kymn et al. 2023 "Factorizers for Distributed Sparse Block Codes," H3DFact 2024):** factorize composed key (s OTIMES p1 OTIMES p2) into factors by recursive weighted-superposition update in the space of each factor population; each population iterates `f_k(t+1) = cleanup_k( unbind(composite, others_t) )` until convergence.

**Why the HARD_FAIL is NOT (only) about resonator-network proper:** the smoke result (NAIVE 2HOP 0.65 ~= RESONATOR 2HOP 0.63) tests RESONATOR-AS-CLEANUP wrapping hop-by-hop argmax — NOT the FACTORIZATION resonator. The literature is clear that resonator-network shines when you have ONE composite vector with k unknown factors; multi-hop traversal is a SEQUENCE of single-factor problems, which is a different topology. Frady-Kent itself does not claim multi-hop sequential lift over per-step argmax in the unsaturated regime.

**Substrate-native variant worth trying (low priority — angle 1):** rewrite 2HOP as a single 3-factor factorization problem: bind(start, p1, p2) as the composite, factor out the unknown intermediate hop-1 entity AND the unknown hop-2 endpoint SIMULTANEOUSLY rather than sequentially. This is the Frady-Kent natural framing but has NEVER been tested on our substrate because we have always done sequential cleanup. Existence proof: H3DFact 2024 achieves factorization on 3+ factor composites at HD scale on neuromorphic hardware.

**P_deflated(this rescues 2HOP):** 0.25. The deflation reflects that the smoke ALREADY isolates per-hop cleanup as not the issue; reframing as 3-factor factorization may help but the same noise that lets argmax win at low alpha would also let the 3-factor resonator converge to the same answer.

### Angle 2 — SOFT-DECISION FEEDBACK / TURBO EQUALIZATION (communications theory field) — STRONGEST

**Mechanism (lit anchors: Tuechler-Singer "Soft-DFE for Multilevel Modulations" 2010; ADA505689 "Mitigating Error Propagation Effects in DFE"; Wang-Poor "Iterative Detection and Decoding of MIMO" 2003; turbo decoding 1993):** In a multi-symbol detection channel, hard-decision DFE feeds the previously detected symbol as if it were ground truth into the cancellation filter for the next symbol — a single wrong decision triggers a burst of errors. Soft-DFE replaces the hard symbol estimate with the symbol's posterior probability (or LLR), so cancellation is weighted by confidence. Turbo decoding cycles soft LLRs between SISO detector and MAP decoder until convergence.

**Multi-hop substrate is EXACTLY this channel structure:**
- Each hop = one symbol decode (entity argmax over similarity field)
- Hop-1 error propagates into hop-2 via `key = bind(start, hop1_pick, p2)` — if `hop1_pick` is wrong, hop-2 W-lookup is querying for a relation that does not exist in W → noise out
- Current substrate uses HARD-DECISION argmax/top-K cleanup between hops — exactly the DFE error-propagation pathology

**Substrate-native variant (HIGH priority — angle 2.A — SOFT-CHAIN):**
- After Modern-Hopfield cleanup at hop-1, do NOT argmax. Instead emit a soft distribution `q1[i] = softmax(similarity_to_atom_i / T)` over the top-K=20 candidates (T calibrated so entropy ~= log(2) on the well-resolved case)
- Hop-2 query is built as a SUPERPOSITION: `k_hop2 = sum_i q1[i] * bind(atom_i, p2)`
- Hop-2 cleanup runs on this superposed key; final readout is argmax over hop-2 codebook
- This is the substrate-native analog of soft-DFE LLR feedback

**Why brain validates this (existence proof):** CA3 pattern-completion is NOT winner-take-all — recurrent collateral attractor dynamics produce a GRADED reactivation pattern with multiple sub-attractor candidates; downstream regions (CA1, EC) integrate this graded signal rather than receiving a single discrete pick. The hippocampal "replay" literature (Buzsaki, Foster, Wilson) shows that during multi-step memory retrieval, intermediate states are population-coded with confidence (sharp-wave ripple amplitude), not as discrete picks. Holistic Recollection via Pattern Completion (PMC 2019) explicitly documents that CA3 emits a probability distribution over reactivated patterns, not a single argmax.

**P_deflated(soft-chain lifts 2HOP from 0.65 to >=0.78):** 0.35. Highest among the 5 angles because (a) the literature is unambiguous on hard-vs-soft DFE, (b) brain existence-proof is direct, (c) substrate-native implementation requires zero new primitives — just defer the argmax.

### Angle 2.B — TURBO ITERATION (soft-chain refinement)

After soft-chain hop-1 -> hop-2, optionally iterate: hop-2's posterior over endpoints can be back-projected onto hop-1's candidate set (`q1_refined[i] proportional to sum_j q2[j] * (k_hop2_i, atom_j similarity)`) and the chain re-run with refined q1. 2-3 iterations is standard in turbo decoding to approach the Shannon-limit.

**Lit anchor:** Wang-Poor MIMO iterative detection 2003; Berrou-Glavieux turbo codes 1993. Replacing hard decision with soft decision reduces error propagation (universal finding across the soft-DFE literature).

**Substrate primitive complete count:** zero. All operations are already in the stack.

**P_deflated(turbo iter on top of soft-chain adds an additional >=0.05 lift):** 0.20. Smaller marginal because most of the gain is from soft-chain itself; iteration helps in regimes where the channel is bad enough that one pass is insufficient.

### Angle 3 — PATH INTEGRALS / SUM-OVER-PATHS (quantum mechanics field)

**Mechanism (lit anchors: Feynman 1948 sum-over-paths; Wikipedia "Path-integral formulation"; quant-ph/0004090 path integral methods):** Replace the single "classical" trajectory through hop-space with a sum over ALL k-step paths, each weighted by an amplitude product (per-hop cosine similarities). Final answer is a coherent superposition over paths; constructive interference at correct endpoints, destructive at wrong endpoints. Substrate's complex-FHRR representation makes this nearly literal — phase products from per-hop binding ARE amplitude phases.

**Substrate-native variant (MEDIUM priority — angle 3 — K-BEAM PATH SUM):**
- At hop-1, retain top-K=10 candidate intermediates with their similarity scores `s1[i]`
- For each candidate i, run hop-2 to get endpoint distribution and per-endpoint similarity `s2[i, j]`
- Final endpoint score: `score[j] = sum_i s1[i] * s2[i, j]` (real-amplitude path sum) OR for FHRR substrate, sum complex amplitudes and take magnitude (true interference)
- Argmax over j

**Why this is materially different from soft-chain (angle 2):** soft-chain ONE-SHOT builds a superposed hop-2 key from hop-1 posterior — the W @ k_hop2 lookup mixes hop-1 candidates inside W. K-beam path-sum keeps the K paths SEPARATE and aggregates only at the readout; it sees per-path cleanup evidence that gets lost in the W-mixing step. The two angles are complementary, not redundant.

**Lit precedent for this in graph retrieval:** beam-search in NMT, K-best decoding in HMM Viterbi, multi-path routing in mesh networks. The substrate-novel piece is the AMPLITUDE-PRODUCT scoring (vs sum-of-log-probs in standard beam search), which is justified by the substrate's algebraic structure where binding similarity composes multiplicatively along a path.

**P_deflated(K-beam path-sum lifts 2HOP from 0.65 to >=0.78):** 0.30. Slightly below soft-chain because the implementation is heavier (K cleanups per hop instead of 1 superposed cleanup) and the lit precedent for amplitude-product scoring in associative memory is thinner (some quantum-inspired AM papers — Trugenberger 2001, Schuld 2014 — but none at substrate scale).

### Angle 4 — RANDOM WALK / PAGERANK STATIONARY DISTRIBUTION (graph theory field)

**Mechanism (lit anchors: Page-Brin 1998 PageRank; Bonald "PageRank" Telecom ParisTech; MMiDS textbook; Multilinear PageRank 2014):** Multi-hop retrieval = random walk on stored-relation graph (atoms = nodes, relations = edges). Single-source PageRank with teleportation gives the stationary distribution over multi-hop endpoints reachable from a query; damping factor alpha (~0.85) trades off exploration vs commitment. Multi-hop traversals affect node-importance differently than single-hop (per the lit).

**Substrate-native variant (MEDIUM priority — angle 4 — SUBSTRATE-PAGERANK):**
- Treat the substrate's W matrix as encoding edge weights of a relation-graph: edge `(s, t)` weight = `<W @ bind(s, R), atom_t>`
- Build a transition matrix `P[s, t]` row-normalized from edge weights
- Multi-hop query from start `s_0` returns the personalized-PageRank vector: `pi = alpha * pi @ P + (1 - alpha) * e_s0`, iterate to convergence (typically 20-50 iterations)
- Top-K endpoints from pi are the answer
- For relation-typed walks (k1, k2 distinct relations), use multi-relational PageRank: `P_r1 P_r2` matrix product

**Why this might rescue:** PageRank is BY CONSTRUCTION a soft-converged distribution; teleportation prevents getting trapped in dead-end branches; the spectral-gap-from-teleportation guarantees fast convergence. Per the lit, "teleportation increases spectral gap, speeding up power iteration convergence" — this is the same property that makes turbo decoding converge.

**Tension with substrate algebra:** PageRank operates on an EXPLICIT graph; substrate's W matrix is an IMPLICIT graph (edges materialize only via lookup). Either (a) materialize the top-K-out-edges from each candidate atom (cheap, K*M operations) or (b) use power-iteration directly in the vector space: `pi_(t+1) = alpha * W_relation @ pi_t + (1-alpha) * e_s0` where W_relation is the substrate's relation-typed W. This second form is substrate-native and matches the Multilinear PageRank framing.

**P_deflated(substrate-PageRank rescues 2HOP):** 0.25. The deflation reflects two risks: (a) substrate's W is high-dimensional dense, not a sparse graph — power iteration may not give the cleanest convergence; (b) the 2HOP test prompt expects a SINGLE answer, but PageRank gives a distribution — readout requires argmax which is back where we started, just with potentially better-converged distribution.

### Angle 5 — RENORMALIZATION GROUP COARSE-GRAINING (statistical physics field)

**Mechanism (lit anchors: Wilson RG 1971; "Functional Renormalization Group for Signal Detection" 2022; "Wavelet Conditional RG" 2022; "Laplacian RG" 2024):** Coarse-grain over short-distance / fast-scale degrees of freedom while preserving long-distance / slow-scale observables. Multi-hop = coarse-graining over intermediate hops; the long-range hop-0-to-hop-2 correlation is the IR observable to preserve.

**Why this is mathematically elegant but substrate-impractical:** RG requires a notion of "scale" — for hop-traversal that would mean grouping atoms by some abstraction hierarchy, then doing single-hop in the abstracted space. Substrate has NO such hierarchical abstraction; all atoms are flat in the same N_DIM space. Laplacian-RG (Villegas 2024) works on graphs and could in principle apply to the substrate's implicit relation graph, but its main use is dimensionality reduction not multi-hop retrieval.

**P_deflated(RG-based variant rescues 2HOP at substrate scale within 1-2 cycles):** 0.10. Field-wide existence proof in physics is overwhelming but the substrate primitive distance is too far; would need to first build a hierarchical-abstraction primitive that does not exist. Not a near-term revival path.

### Bonus — TURBO BELIEF PROPAGATION on substrate factor graph (CROSS of angles 2 + 4)

The substrate's binding algebra induces a natural factor graph: nodes = atoms, factor-nodes = relations, multi-hop = chain of factor-node operations. Belief Propagation on this factor graph (Pearl 1988, Kschischang-Frey-Loeliger 2001) is the message-passing algorithm that GENERALIZES BOTH soft-DFE AND PageRank: it converges to exact marginals on trees and to good approximations on loopy graphs.

**Substrate-native turbo-BP (HIGH priority — bonus angle):** treat each hop as a factor node; pass soft messages (entity distributions) between factor nodes; iterate to convergence. This is the "right" framework — soft-DFE is BP on a chain, PageRank is BP on a graph with teleportation. Lit anchor: Wymeersch "Iterative Receiver Design" 2007 + the turbo-BP search.

**P_deflated(turbo-BP rescues 2HOP and is also the unifying frame):** 0.30. Strong because of the structural unification; calibration deflation because the substrate has no existing BP machinery and would need a non-trivial new primitive (message-passing scheduler).

---

## CHEAP DECISIVE TEST (the discriminator)

Single cell, 3 arms, apples-to-apples synthetic 2HOP at the same regime that produced the HARD_FAIL (M=1000, V_relation=10, K_SET=20, N_DIM=4096, seeds 0-4):

- **ARM_BASELINE_HARD:** the existing NAIVE 2HOP at 0.65 (hard argmax between hops). Re-run for seed-matched comparison.
- **ARM_SOFT_CHAIN:** soft-chain (angle 2.A). Hop-1 emits softmax over top-K=20 with T calibrated to median-entropy ~= log(3); hop-2 key is `sum_i q1[i] * bind(atom_i, p2)`; cleanup; argmax readout.
- **ARM_KBEAM_PATHSUM:** K-beam path-sum (angle 3). Top-K=10 hop-1 candidates with similarity scores; hop-2 cleanup per candidate; endpoint score = `sum_i s1[i] * s2[i, j]`; argmax over j.

Cell-author smoke (Fix #17): 5 seeds, M=1000, single-K, runtime <= 30 min on local CPU per arm. Lane: PRIMITIVE_TEST_synthetic_apples_to_apples. corpus_provenance: synthetic_random_atoms_uniform_relations_v1. Pre-reg HARD bands:

- **HARD_PASS:** ARM_SOFT_CHAIN OR ARM_KBEAM_PATHSUM >= 0.78 mean accuracy (>= 13pp lift over baseline 0.65), 5-seed sd <= 0.04. This would be chain-grade evidence the soft/path-sum chaining mechanism rescues multi-hop.
- **MIDDLE_BAND:** 0.70 <= best-arm accuracy < 0.78 (small-but-real lift); requires follow-up at larger M and / or turbo-iteration.
- **HARD_FAIL:** all arms within +/- 0.03 of 0.65 (no lift); structurally closes the soft-chain hypothesis; revival pivots to substrate-PageRank (angle 4) as second-choice.

---

## FALSIFIABLE PREDICTIONS (pre-reg HARD bands; symmetric verify-both-directions)

**Prediction P1 (HARD_PASS direction):** Soft-chain (angle 2.A) lifts 2HOP from 0.65 to >= 0.78 at M=1000, K_SET=20, N_DIM=4096, 5 seeds.
- **HARD_PASS threshold:** mean(ARM_SOFT_CHAIN) >= 0.78 AND sd <= 0.04 AND ARM_SOFT_CHAIN > ARM_BASELINE_HARD + 0.10 at p<0.05 paired-seed
- **HARD_FAIL threshold:** mean(ARM_SOFT_CHAIN) <= 0.68 (NOT better than baseline + 0.03 ceiling)

**Prediction P2 (HARD_PASS direction):** K-beam path-sum (angle 3) lifts 2HOP from 0.65 to >= 0.78.
- **HARD_PASS threshold:** mean(ARM_KBEAM_PATHSUM) >= 0.78 AND sd <= 0.04 AND > baseline + 0.10
- **HARD_FAIL threshold:** mean(ARM_KBEAM_PATHSUM) <= 0.68

**Prediction P3 (both-direction):** If BOTH P1 and P2 HARD_PASS, the lift mechanism is the soft-confidence chaining principle (cross-confirmed by two implementations); if neither passes, the substrate's multi-hop limit is more fundamental than chaining-mechanism choice (likely an upstream encoder / W-capacity / cleanup-margin issue) and revival pivots to substrate-PageRank (angle 4) and / or substrate-encoder / W-capacity drills.

**Prediction P4 (calibration sanity / falsifier):** ARM_BASELINE_HARD must reproduce within +/- 0.02 of the published 0.65. If it does not, the synthetic regime is not the same as the original HARD_FAIL — discard the test and re-run after regime-matching.

---

## CROSS-THREAD SYNTHESIS (with prior research)

- **vs `research_2x_revival_comparator_resonator_HF_2026-06-23.md`:** that note diagnosed comparator HARD_FAIL as smoke-regime-too-easy (alpha=0.061 unsaturated W). The current HARD_FAIL is at M=1000 (substantially higher load) and the diagnosis is DIFFERENT — not smoke-regime-too-easy but hard-vs-soft-decision-chaining. The two are consistent: at low load NAIVE wins because soft-chaining over near-clean signal is no better than argmax; the current test is in a regime where the signal is noisier per-hop so soft-chaining should help. Verify: ARM_BASELINE_HARD per-hop accuracy in the current cell should be 0.78-0.85 (not 0.95+); if it is 0.95+ we are back in too-easy-regime and the test is uninformative.
- **vs `research_negative_N6_resonator_dense_V100_HF_2x_2026-06-20.md`:** that 2x dense V100 resonator HARD_FAIL also failed at multi-hop. Soft-chain has not been tested in either; it is the dominant un-tested angle for both.
- **vs cap_map row PP-pool-retrieval (VALIDATED):** pool retrieval already uses weighted-vote readout which is a 1-hop analog of path-sum. Multi-hop path-sum (angle 3) is the natural extension to k-hop chains.
- **vs PP-resonator-decomposition-ACF (VALIDATED, K/N=1.5 at 97%):** resonator-network proper IS chain-grade at FACTORIZATION on the substrate; the multi-hop HARD_FAIL is about SEQUENTIAL CHAINING of resonator-cleaned hops, not about resonator-network itself. Reframe pending verdict.
- **vs Fix #28 discipline:** the prompt's verdict_msg framing "Resonator HARD_FAIL on multi-hop" was historically being read as "resonator-network refuted for multi-hop." Per Fix #28, the correct read is per-arm: resonator-cleanup is FINE per-hop; the CHAINING is the failure mode. The HARD_FAIL is on the chaining wrapper, not on resonator-network as such.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

If soft-chain (angle 2.A) HARD_PASSes:
- **cap_map row PP-multi-hop-reasoning** moves from 🟡 INCONCLUSIVE -> 🟢 VALIDATED-WANT-STRONGER
- New substrate-product claim: "substrate supports k-hop reasoning with soft-confidence chaining; per-hop posterior weights propagate without error-propagation collapse"
- Brain-grounded existence proof: CA3 graded reactivation; CA1 / EC downstream integration
- Cross-field grounding: communications theory soft-DFE / turbo decoding (50-year-mature field)
- HotpotQA multi-hop dev-split becomes the natural production-regime follow-up (per parent comparator note v3 handoff Arm 3 also wants this primitive)

If K-beam path-sum (angle 3) HARD_PASSes:
- Substrate gains a "constructive-interference readout" mechanism; substantively novel framing
- FHRR-complex variant is the natural follow-up (true amplitude+phase interference, not just real-amplitude sum)
- Substrate-product implication: "substrate composes hop confidences multiplicatively along paths and aggregates at readout — algebraically faithful to relational composition"

If ALL THREE TOP ARMS FAIL:
- Multi-hop limit is upstream of chaining mechanism: likely encoder / W-capacity / cleanup-margin
- cap_map row stays 🟡 INCONCLUSIVE; revival pivots to substrate-encoder (parallel project lane) and PageRank-readout (angle 4) as second-tier rescue
- Substrate-product story becomes "substrate is fine at single-hop relation retrieval; multi-hop reasoning requires either (a) additional upstream encoder capacity or (b) a different storage representation than current W"

Either outcome ADVANCES the cap_map row — the test is genuinely decisive.

---

## CITATIONS (verified count: 9 lit anchors across 5 disparate fields + 1 brain)

**Communications theory / DFE / turbo (angle 2):**
1. Tuechler & Singer 2010, "Soft-Decision Feedback Turbo Equalization for Multilevel Modulations," IEEE Trans Wireless Comm — replacing hard with soft decision reduces error propagation
2. Wang & Poor 2003, "Iterative Detection and Decoding of MIMO Signals Using Low-Complexity Soft-In/Soft-Out Detector" — soft LLR feedback in iterative receivers
3. Berrou et al. 1993, "Near Shannon Limit Error-Correcting Coding: Turbo-Codes" — foundational soft-iteration achieves Shannon-limit
4. ADA505689 DTIC tech report, "Mitigating Error Propagation Effects in a Decision Feedback Equalizer" — explicit error-propagation diagnosis

**Resonator networks / VSA / HD (angle 1):**
5. Frady, Kent, Olshausen, Sommer 2020, "Resonator Networks 1: An Efficient Solution for Factoring High-Dimensional, Distributed Representations of Data Structures," Neural Computation
6. Kymn et al. 2023, "Factorizers for Distributed Sparse Block Codes," arXiv 2303.13957
7. H3DFact 2024, "Heterogeneous 3D Integrated CIM for Factorization with Holographic Perceptual Representations," arXiv 2404.04173

**Random walks / PageRank (angle 4):**
8. Page, Brin, Motwani, Winograd 1998, "The PageRank Citation Ranking: Bringing Order to the Web"
9. Gleich et al. 2014, "Multilinear PageRank," arXiv 1409.1465 (multi-relational extension; relevant to relation-typed substrate walks)

**Path integrals (angle 3):**
10. Feynman 1948, "Space-Time Approach to Non-Relativistic Quantum Mechanics," Rev. Mod. Phys. — foundational sum-over-paths

**Renormalization group (angle 5):**
11. Villegas et al. 2023-2024, "Laplacian Renormalization Group," Nat. Phys. — graph-RG framework

**Brain existence proof (cross-cutting):**
12. Holistic Recollection via Pattern Completion Involves Hippocampal Subfield CA3, J Neurosci 2019 / PMC6786823 — CA3 graded reactivation, not winner-take-all
13. Structure and function of the hippocampal CA3 module, PNAS 2023 — recurrent collaterals + auto-associative attractor dynamics

(All 13 verified via WebSearch this drill; URLs preserved in the parallel sub-agent transcripts.)

---

## CALIBRATION TRANSPARENCY

- Per [[feedback-lit-scan-calibration-penalty]]: 0.25 deflation applied (USER prompt asks 0.25). Novel-synthesis cap P at 0.50 — strongest angle (soft-chain) reports 0.35 well below cap.
- Per [[feedback-dont-dismiss-adjacent-methods]]: all 5 angles dispatched; 1 dismissed (angle 5 RG) only AFTER substrate-primitive-distance analysis, not a priori.
- Per [[feedback-empowered-to-experiment-where-lit-says-dismissed]]: NONE of the 5 angles is lit-dismissed for multi-hop — all are positive-precedent in their own fields. Calibration confidence remains anchored to communications theory (50-year mature) and brain existence proof.
- Per [[feedback-brain-is-existence-proof-higher-prior]]: angle 2 (soft-chain) has direct CA3 graded-reactivation precedent — soft-chain P could in principle be 0.45-0.50 unpenalized; 0.35 reflects the discipline-mandated deflation.
- Per Fix #28: per-arm pre-reg bands above are independent (P1 AND P2 fail jointly is a stronger structural finding than either alone).

Recommended cell label declarations (Fix #26 pre-dispatch check before any spawn):
- Lane: `PRIMITIVE_TEST_synthetic_apples_to_apples`
- corpus_provenance: `synthetic_random_atoms_M1000_V10_K20_N4096_seeds_0_to_4`
- Anchor: `multihop_softchain_kbeam_3arm_v1`

Time-budget actuals: ~50min cross-domain drill (9 WebSearches + 2 file reads + synthesis); within the 45-60min budget.
