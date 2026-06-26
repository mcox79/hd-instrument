# Research: GAP 3 -- Compositional Generalization, 5x drill

date: 2026-06-26 (filed 2026-06-25)
filed-by: research (Opus 4.7 1M)
trigger: Strategy/Skunkworks routing request -- 5x drill on GAP 3 compositional generalization (heldout 0.00 baseline)
scope: 18 candidates across 5+ fields; ranked top 5; calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]

## HEADLINE

The brain's "compositional generalization" is NOT one mechanism but a three-layer stack: (1) sparse episodic store (DG/CA3 -- substrate already has this), (2) slow consolidation that extracts INVARIANTS across episodes (CLS replay -- substrate has hdlab/predictive_coding but no replay-driven cortical extraction), (3) inference-time pattern-completion against compressed schemas (substrate has iterative_attractor but no learned schemas to complete against). The reason substrate scores 0.00 heldout despite 0.30 on training is that NO substrate primitive exists at layer 2 -- the COMPRESSION step. Five live levers, ranked by P_solve x cost: (a) LARS-VSA relational bottleneck (P=0.42; ~1 day) -- direct VSA precedent showing abstract-rule learning emerges from cross-attention-style binding in HD space; (b) Percolation/concept emergence (P=0.35; ~1 day) -- arxiv 2408.12578 establishes phase-transition model predicting WHEN compositional capability emerges from atomic-pair coverage, gives substrate a sharp falsifiable threshold; (c) Resonator-network factorization (P=0.40; ~2 days) -- iterative unbinding solves the "novel-combination" decoding problem; substrate already has codebook + iterative attractor primitives; (d) Slow cortical extraction via CLS-replay schema cells (P=0.30; ~3 days) -- substrate's continual-learning lever already validated; just needs schema-channel separate from episode-channel; (e) Tropical/max-plus attention (P=0.25; ~2 days) -- novel, untested in substrate context, but arxiv 2505.17190 shows length-generalization wins on algorithmic reasoning.

Cross-cutting insight: substrate's failure mode is "HRR crosstalk dominates at N=2048; depth-2 binding works but depth-3+ collapses." Resonator-network literature has the EXACT precedent -- factor-decomposition by iterative resonance scales superlinearly with N. Substrate should NOT hand-design schemas; it should let them EMERGE via either (a) percolation-thresholded coverage of atomic pairs or (b) resonator-network discovery of latent factors.

## Cheap decisive test

CELL: `gap3_lars_vsa_relational_bottleneck_v1` (cell-author smoke + Fix #17 measurement)
- N=8192 (per HRR-crosstalk lesson; do NOT smoke at 2048)
- Toy compositional task: 50 "mammals" with 5 properties each (warm-blooded, has-fur, breathes-air, ...); train on 45, hold out 5 NOVEL mammals; query "is novel-mammal-X warm-blooded?" requiring schema-extraction
- Three arms:
  - ARM_BASELINE: substrate's existing predictive_coding write + iterative_attractor read (current 0.00 heldout reproduction)
  - ARM_RELBOTTLENECK: LARS-VSA-style learned-symbol values + relational cross-attention binding (values are independent embeddings, NOT input-conditioned)
  - ARM_RESONATOR: store mammal-property bindings as HRR products; at inference run resonator-network unbinding to decompose query into (category, property) factors
- Pre-registered bands per [[feedback-experiment-bias-master-checklist]]:
  - HARD_PASS: heldout accuracy >= 0.50 (10x chance 0.05) on at least one arm
  - HARD_FAIL: all three arms <= 0.10 heldout (rules out the entire mechanism family for our substrate)
  - MIDDLE_BAND [0.10, 0.50]: PARTIAL; ratify per-arm metrics, queue capacity/N sweep
- Discriminator: 3-arm spread; if all arms converge within 5%, the test is non-discriminating and we need to redesign before USER arbitration per [[feedback-encoder-picks-emerge-from-data]]
- Compute: ~1 hour CPU on N=8192 with 50x5 task. Local_cpu_queue.
- Substrate-mine FIRST per [[feedback-substrate-mine-capacity-before-extrapolating]]: there are 588 atoms; check for existing compositional-task atoms before assuming current 0.00 is universal across regimes
- Per [[feedback-clean-encoder-tests-no-contamination]]: synthetic data only; no substrate's existing 588 atoms; no name-leak

## Falsifiable predictions

### HARD PASS thresholds (one of these triggers chain-grade claim)

1. ARM_RELBOTTLENECK >= 0.50 heldout AND >= 4x ARM_BASELINE accuracy. Interpretation: relational bottleneck is sufficient; substrate needs to add a "learned symbol" channel separate from input-channel. Substrate-product implication: build hdlab/relational_bottleneck.py primitive; promote to capability-suite ARM_COMPOSITIONAL_GEN regression test
2. ARM_RESONATOR >= 0.50 heldout AND >= 4x ARM_BASELINE. Interpretation: factorization is the bottleneck; substrate has the right binding primitive (HRR) but needs the resonator-network READING side. Substrate-product implication: build hdlab/resonator_decode.py; pairs with kg_traversal for multi-hop
3. Cross-arm convergence at >= 0.50 (both RELBOTTLENECK and RESONATOR hit). Interpretation: GAP 3 is structurally solvable in substrate; pick lower-cost arm for production. Most likely outcome if literature precedent generalizes

### HARD FAIL thresholds (rules out the entire angle)

1. All three arms <= 0.10 heldout. Interpretation: at N=8192, HRR-crosstalk-style failure mode is universal across compositional mechanisms. Action: pivot to dense Hopfield (Krotov exponential capacity) or sparse-bipolar (substrate-mined 20-300x bundle lift per project_session_2026-06-23). NOT to dismiss field -- per [[feedback-dont-dismiss-adjacent-methods]]
2. ARM_BASELINE rises above 0.30 (replicating training accuracy). Interpretation: prior 0.00 measurement was confounded; re-audit harness BEFORE drilling new mechanisms. Methodology-confound per project_substrate_as_LM_test_harness_rigged_2026-06-23
3. ARM_RELBOTTLENECK and ARM_RESONATOR both fail (<=0.20) while ARM_BASELINE rises (training set leak). Interpretation: the compositional gap is not in the mechanism but in the data construction. Action: rebuild heldout split with stricter rule-rotation (Lake-Baroni SCAN-style template)

### MIDDLE BAND [0.10, 0.50]

- Partial; report per-arm metrics; cert-classify as MM-grade per [[feedback-fix28-recurring-skunkworks-correct-more-than-director]]; queue follow-up sweep over (N in [4096, 8192, 16384]) x (heldout-difficulty in [near-train, far-train, structural-novel])

## 18 Candidates with rank (top 5 marked *)

(Calibration penalty: agent P estimates deflated 0.15-0.25; novel-synthesis cap at 0.50 per [[feedback-lit-scan-calibration-penalty]])

| # | Field | Mechanism | Substrate-native mapping | Discriminator | P_solve_deflated | Cost | Novelty |
|---|---|---|---|---|---|---|---|
| *1 | ML / VSA | LARS-VSA relational bottleneck (Smolensky-Webb adapted to HD space; arxiv 2405.14436) | learned-symbol embeddings (not input-conditioned) + relational cross-attention binding in N=8192 HD space | heldout >= 0.50 on novel-mammal test | 0.42 | ~1 day | medium (VSA precedent direct) |
| *2 | ML / theoretical | Percolation model of compositional emergence (arxiv 2408.12578) | predict heldout accuracy as function of training-pair coverage; phase-transition threshold | matches predicted scaling curve within +/- 0.1 | 0.35 | ~1 day | high (NEW field for substrate) |
| *3 | Theoretical neuroscience | Resonator networks factor decomposition (Frady-Sommer arxiv 1906.11684, 2024 cleanup arxiv frai.2026) | iterative unbinding of (category, property) from HRR-bound query against existing codebook | factorization accuracy >= 0.85 on novel composites | 0.40 | ~2 days | low (resonator-network is mature; substrate has codebook + iterative_attractor primitives ready) |
| *4 | Theoretical neuroscience | CLS replay-driven schema cells (Kumaran-McClelland 2016; Tse-Morris 2011) | second "schema" channel slow-extracted from episodic channel via Hebbian replay; substrate's predictive_coding.py + replay generator | schema-channel accuracy on heldout >> episodic-channel accuracy | 0.30 | ~3 days | medium-high (substrate has Hebbian + predictive coding; lacks replay-loop integrator) |
| *5 | Pure math | Tropical / max-plus semiring attention (arxiv 2505.17190) | replace softmax cleanup with max-plus aggregation; algorithmic reasoning literature shows length-generalization win | length-generalization curve flatter than baseline | 0.25 | ~2 days | high (novel for substrate; cap at 0.50 per calibration) |
| 6 | ML | Meta-Learning for Compositionality (MLC; Lake-Baroni Nature 2023) | episodic training over many sub-tasks each requiring rule extraction; substrate's continual-learning replay | matches Nature 2023 SCAN result on substrate harness | 0.30 | ~5 days | medium |
| 7 | ML | Tensor Product Representations / Soft TPR (Smolensky + 2024 follow-ups arxiv 2412.04671) | TPR is already adjacent to HRR; soft-TPR allows epsilon-neighborhood binding | TPR-style decomposition on heldout >= 0.50 | 0.32 | ~2 days | low (TPR/HRR strongly related; substrate may already have via FHRR mode) |
| 8 | ML / interpretable | Concept bottleneck models (relational CBMs; arxiv 2308.11991) | intermediate "predicate" layer between encoder and decoder | predicate-supervision experiment | 0.20 | ~3 days | low (requires labeled predicates; doesn't match brain's unsupervised regime) |
| 9 | ML | Sparse-coding attention transformer (arxiv 2511.20194) | sparse-coding bottleneck on attention values | sparse-attention vs dense baseline on heldout | 0.20 | ~3 days | low (architecture change; not native to substrate) |
| 10 | Pure math | Group equivariant networks (Cohen-Welling; arxiv 1602.07576) | encode property-invariance group via equivariant binding | symmetry-respecting baseline beats unconstrained | 0.15 | ~3 days | low (no obvious group action on substrate's property relations) |
| 11 | Pure math | Sheaf neural networks (Hansen + 2026 follow-ups) | cellular sheaf on substrate's KG; local-to-global section composition | sheaf-Laplacian-respecting cleanup beats baseline | 0.10 | ~5 days | very high (untested in HD; high theoretical bar) |
| 12 | Pure math | Functorial / category-theoretic ML (arxiv 2408.14014 survey) | type-driven composition; learned functor between substrate-state category and answer category | functorial regularization improves heldout | 0.15 | ~5 days | very high (untested; speculative) |
| 13 | Theoretical neuroscience | Sparse Distributed Memory (Kanerva) | substrate already adjacent; add hard-locations + Hamming-distance pooling layer | SDM-pooling improves heldout vs current bipolar | 0.20 | ~2 days | low (sparse-bipolar lift already mined per project_session_2026-06-23) |
| 14 | Theoretical neuroscience | Hippocampal index theory (DG sparse separation + CA3 attractor completion) | substrate's iterative_attractor IS CA3-like; add DG-style sparse separation pre-stage | sparse-separation + attractor beats baseline | 0.25 | ~2 days | medium |
| 15 | Theoretical neuroscience | Predictive coding hierarchical Bayesian (Rao-Ballard active predictive coding; Rao 2024) | substrate has predictive_coding.py; needs HIERARCHICAL (multi-scale prediction) extension | hierarchical-PC beats flat-PC on compositional heldout | 0.25 | ~3 days | medium |
| 16 | Materials physics | Renormalization group as schema extraction (arxiv 2510.25553 + 1906.05212) | layer-wise coarse-graining of substrate states; treat schemas as RG fixed points | RG-coarsened representation predicts heldout better than raw | 0.15 | ~5 days | very high (novel synthesis; cap 0.50) |
| 17 | Materials physics | Self-assembly / Wang tiles (DNA origami) | substrate's KG edges as Wang-tile matching constraints; novel composition emerges by local-rule chaining | local-rule-driven traversal beats baseline on heldout | 0.10 | ~5 days | very high (very speculative; Tier-3 by advisor; only-if-adjacent) |
| 18 | Linguistics | Combinatory Categorial Grammar (CCG) type-driven composition | category-grammar type tags on substrate atoms; type-checking-driven traversal | type-driven traversal beats baseline | 0.15 | ~5 days | medium-high |

## Top 5 detailed treatment

### 1. LARS-VSA relational bottleneck (rank #1)

mechanism: HD vectors store object features; SEPARATE learned-symbol vectors (NOT derived from inputs) act as "values" in cross-attention; relational binding is between symbols and features via standard VSA binding. The relational-bottleneck inductive bias (Webb-Goyal-Smolensky 2024 Trends Cog Sci) restricts information flow to relations computed as inner products. Substrate already has all required primitives: binding (hdlab/binding.py), HD vectors, codebook cleanup.

substrate-native mapping: introduce a small codebook (~32-256) of "symbol" hypervectors {s_1, ..., s_K} that are LEARNED (or frozen-random for v1), separate from substrate's object atoms. At inference, query = sum over k of (similarity(input, learned_key_k) * s_k); composition step binds s_k with property hypervectors. The key novelty vs substrate's existing approach: symbols are INDEPENDENT of input content, so they act as schema-slots.

discriminator: heldout >= 0.50 on 5 novel mammals; ARM_BASELINE replicates 0.00; spread of >= 0.40 is decisive

P_deflated: 0.42 (raw lit P=0.65; -0.20 calibration; -0.03 because LARS-VSA's published results are on slightly different tasks)

decision-grade outcomes:
- HARD_PASS -> ship hdlab/relational_bottleneck.py + capability-suite regression test
- HARD_FAIL -> rules out symbol-vs-content separation; next try resonator decode
- MIDDLE_BAND -> sweep symbol-codebook-size K in [16, 64, 256, 1024]

compute budget: 1 hour local_cpu_queue at N=8192

novelty: LARS-VSA is published 2024; substrate has not tested it; medium novelty for substrate, low novelty for field

cross-cell sanity rail: if ARM_BASELINE goes >0.30 (training-set leak), abort and re-audit harness per [[feedback-fix28-verify-per-arm-metrics]]

### 2. Percolation model of compositional emergence (rank #2)

mechanism: arxiv 2408.12578 (Lubana-Tanaka et al., 2024) models compositional capability emergence as a percolation phase transition on the bipartite graph of (attribute-pair, training-pair) coverage. Predicts a sharp threshold: when fraction of attribute-pairs covered in training exceeds critical p_c, model abruptly generalizes to all novel compositions. Sub-critical = catastrophic 0% heldout; supercritical = near-100% heldout.

substrate-native mapping: substrate's 0.00 heldout vs 0.30 training is EXACTLY the sub-critical regime. Compute coverage statistic on substrate's training data; predict critical threshold; vary training-set composition to cross threshold; substrate should jump from ~0% to >50% at the predicted critical point. Substrate-physics natural since percolation is already an active research field per cap_map.

discriminator: substrate's heldout-accuracy-vs-coverage curve fits power-law with predicted exponents within +/- 0.15. If yes, GAP 3 is not a fundamental substrate limit but a data-coverage statement; if no, percolation model doesn't apply and substrate has additional bottleneck.

P_deflated: 0.35 (raw lit P=0.55; -0.20 calibration; percolation literature is well-established but transfer to HD VSA is novel)

decision-grade outcomes:
- HARD_PASS (curve fits) -> the compositional gap is solved by INCREASING TRAINING COVERAGE; concrete prescription for which atomic pairs to add; cap_map row GAP 3 reclassifies from "mechanism-missing" to "data-coverage-statement"
- HARD_FAIL (no curve) -> substrate has bottleneck beyond data coverage; pivot to mechanism candidates (#1, #3, #4)
- MIDDLE_BAND -> partial fit; identify which substrate-specific corrections to percolation model are needed

compute budget: ~1 day theory + ~1 hr CPU smoke at N=8192 with 6-8 coverage points

novelty: HIGH for substrate (percolation field is under-drilled per advisor); MEDIUM for field (percolation in ML emergence is hot 2024)

cross-cell sanity rail: must reuse same heldout split across coverage points; per [[feedback-experiment-bias-master-checklist]] guard against coverage-changes-heldout-difficulty confound

### 3. Resonator networks factor decomposition (rank #3)

mechanism: Frady-Kent-Olshausen-Sommer 2020 + 2024 follow-ups. Given a composite vector Z = X bind Y bind ..., resonator network iteratively decomposes into factors via simultaneous unbinding + cleanup against codebooks. Each factor estimate updates: x_t+1 = cleanup(unbind(Z, y_t, ...), codebook_X). Capacity scales superlinearly with N. The 2026 cleanup-rule comparison paper (Frontiers in AI) shows nonlinear cleanup beats sign() at high crosstalk. Already-deployed in neuromorphic hardware + cognitive-map work.

substrate-native mapping: substrate has codebook + iterative_attractor primitives. Add resonator wrapper: given query "is novel-mammal-X warm-blooded?", encode as bind(category_X, property_warm-blooded); iteratively decompose against (categories_codebook, properties_codebook); if factorization succeeds, lookup answer. The substrate's depth-2 binding already works -- resonator extends to depth-3+ that's currently HRR-crosstalk-limited.

discriminator: factorization accuracy >= 0.85 on novel composites at N=8192 with 50 categories x 5 properties. If <= 0.50, resonator doesn't help at this scale.

P_deflated: 0.40 (raw lit P=0.60; -0.20 calibration; resonator-network capacity is well-characterized)

decision-grade outcomes:
- HARD_PASS -> ship hdlab/resonator_decode.py; pair with multi_hop.py; chain-grade for compositional heldout
- HARD_FAIL at N=8192 -> sweep N up to 16384; if still fails, the substrate's binding fidelity is the bottleneck (cap rows on binding capacity)
- MIDDLE_BAND -> per-factor accuracy may differ; report and queue sweep

compute budget: ~2 days (1 day impl + 1 day sweep); CPU; medium

novelty: MEDIUM for substrate (resonator literature mature; substrate has not deployed); LOW for field

cross-cell sanity rail: resonator can converge to spurious fixed points; report fraction-converged vs fraction-correct separately

### 4. CLS replay-driven schema extraction (rank #4)

mechanism: Kumaran-Hassabis-McClelland 2016 update of complementary learning systems. Fast hippocampus learns specifics; slow neocortex learns generalizations via REPLAY. Schema cells in mPFC + anterior temporal lobe activate when context matches prior schema (Tse-Morris 2011 Science). Critically: replay is NOT random -- it's prioritized by uncertainty/reward, and consolidation extracts statistical regularities (Wright-Fisher selection on memory traces).

substrate-native mapping: substrate has predictive_coding.py (residual-gated Hebbian write -- correct CLS hippocampus mechanism). Add a SECOND channel: "schema" matrix W_s that gets updated via Hebbian extraction of co-activation patterns from W_h (episodic). Replay loop = sample queries, run through episodic channel, store residual-with-schema, update W_s. Inference uses W_s for unseen compositions; W_h for memorization. Has precedent in substrate's hdlab/learning.py + multi_hop.py.

discriminator: schema-channel heldout accuracy >= 2x episodic-channel heldout accuracy on heldout (separation of generalization vs memorization). If both channels equally bad, replay doesn't extract structure.

P_deflated: 0.30 (raw lit P=0.50; -0.20 calibration; replay extraction is brain-validated but substrate-specific impl risky)

decision-grade outcomes:
- HARD_PASS -> ship hdlab/cls_replay.py with two-channel architecture; major moat (continual-learning + compositional)
- HARD_FAIL -> rules out replay-extraction at this regime; next try resonator + relational-bottleneck
- MIDDLE_BAND -> sweep replay-rate, replay-prioritization, slow-channel learning rate

compute budget: ~3 days (impl heavier than #1-#3 due to two-channel coordination); CPU

novelty: MEDIUM-HIGH for substrate (CLS framework adopted in spirit but no schema-channel primitive); LOW for field

cross-cell sanity rail: per [[feedback-brain-is-existence-proof]], brain-grounded mechanism warrants P=0.60-0.75 prior; the -0.20 calibration drops to 0.30 to be conservative on impl risk, not feasibility

### 5. Tropical / max-plus semiring attention (rank #5)

mechanism: arxiv 2505.17190 (Tropical Attention, 2025). Replace softmax aggregation with max-plus semiring operation (tropical algebra). Empirically: length-generalization and value-generalization on combinatorial algorithms surpass softmax baselines. Mathematically tropical attention approximates DP-type combinatorial algorithms natively. Connects to morphological neural networks (arxiv 2505.09710 universal approximation result).

substrate-native mapping: substrate's iterative_attractor uses argmax cleanup (already a max operation). Extend to FULL max-plus by replacing softmax in cleanup steps with max-plus semiring. For compositional query, the max-plus structure naturally encodes "best path through composition tree."

discriminator: length-generalization curve on compositional task (vary depth from 2 to 6); tropical-attention flattens curve relative to softmax baseline by >= 0.2 absolute accuracy at depth 6.

P_deflated: 0.25 (raw lit P=0.45; -0.20 calibration; novel synthesis cap holds; tropical attention is 2025-new, no substrate transfer precedent)

decision-grade outcomes:
- HARD_PASS -> ship hdlab/tropical_attention.py as cleanup-rule alternative; pairs with multi_hop
- HARD_FAIL -> rules out tropical for substrate compositional; tropical may still help on combinatorial tasks separately
- MIDDLE_BAND -> compare against softmax cleanup; report length-generalization curves

compute budget: ~2 days; CPU; medium

novelty: HIGH for substrate; MEDIUM-HIGH for field (2025 paper; not widely tested)

cross-cell sanity rail: tropical attention literature focuses on algorithmic reasoning, not compositional generalization per se -- transfer is conjectural; deflated P reflects this

## Cross-thread synthesis

GAP 3 sits at the intersection of multiple substrate threads:

1. **HRR crosstalk at N=2048 (smoke HARD_FAIL precedent)**: confirms substrate's binding-fidelity bottleneck; resonator (#3) is the literature solution; LARS-VSA (#1) sidesteps by introducing symbol channel

2. **Cortex schema extraction v1 cell at N=8192 (NN=0.40, feat=0.42, comb=0.38)**: MIDDLE_BAND result for HRR-bundle of cat-prop bindings. This IS already close to the lit predictions; needs (a) replay loop (CLS, #4) or (b) resonator decode (#3) to push composition past 0.42

3. **Capability suite ARM_COMPOSITIONAL_GEN 0.00 heldout**: baseline is the "no schema layer" condition. The 0.00 (not 0.30 like training) confirms substrate's depth-2 atomic-fact retrieval works (training); the compositional inference (heldout) lacks mechanism. Maps to layer-2 of the stack -- compression/schema extraction

4. **substrate-mine result from project_session_2026-06-23**: 600K patterns at N=2048 via sparse x K x D multiplicative composition. This is a CAPACITY result, not a COMPOSITIONAL-GENERALIZATION result. They are different: capacity = "how many distinct items survive"; compositional generalization = "extract a schema from items, apply to novel items." Substrate has high capacity at low compositional. Lit consistent with this distinction

5. **predictive_coding.py + iterative_attractor.py + multi_hop.py + kg_traversal.py already in hdlab**: substrate has 4 of 7 primitives needed for full CLS-style compositional pipeline. Missing: (a) schema channel separate from episodic (#4), (b) resonator decode (#3), (c) relational-bottleneck symbol codebook (#1)

6. **Phase 3 abstraction distillation ceiling at 0.70-0.82 (testbed_to_research 2026-06-13)**: prior substrate has tried "type-atom" / "abstraction" cells. The 0.70-0.82 plateau suggests substrate's existing distillation mechanism is hitting a CAP, NOT zero floor. This is INFORMATION: the per-arm metrics differ between (a) the heldout 0.00 case (no mechanism, floor) and (b) the abstraction-distillation 0.82 ceiling (mechanism exists, hits ceiling). Different failure modes -- ranks #1 and #4 target floor; #3 targets ceiling

7. **Brain existence proof per [[feedback-brain-is-existence-proof-higher-prior]]**: layered CLS + resonator-like factorization + relational binding ALL have brain precedent. Multiple substrate-native paths likely exist; even if one fails, the field gives high prior the substrate is implementation-incomplete, not capability-blocked

8. **Per [[feedback-empowered-to-experiment-where-lit-says-dismissed]]**: literature shows HRR-style binding "doesn't scale past depth 2-3"; resonator networks (#3) DEFEAT this dismissal at higher N. Substrate should DISPATCH even where literature is pessimistic about base binding

## Substrate-product implications

- **If #1 PASSES**: substrate gains the FIRST true schema-extraction primitive. Capability-suite GAP 3 row flips from RED to GREEN. Onboarding pitch: "stores facts + extracts rules + applies rules to novel facts." Substrate-mine: pair with KG portfolio (FB15k-237 + ConceptNet + HotpotQA) for natural cross-domain validation
- **If #2 PASSES**: GAP 3 reclassifies from mechanism-deficit to data-coverage. Direct customer prescription: "increase atomic-pair coverage to X% to unlock generalization." Predictable: pricing model could differentiate "training coverage tier"
- **If #3 PASSES**: substrate gets multi-hop chain reasoning out of the box. Pairs with kg_traversal.py + multi_hop.py for chain-grade KG-completion. Combined with #1, substrate would have BOTH "extract rules" and "compose multi-hop chains" -- killer demo
- **If #4 PASSES**: substrate gains continual-learning + compositional generalization in one. Moat strengthens via "online schema updates" (no retraining)
- **If #5 PASSES**: substrate gains length-generalization on algorithmic tasks. Adjacent capability (combinatorial reasoning), not directly GAP 3, but unlocks separate value
- **If all FAIL**: pivot to dense Hopfield (Krotov exponential capacity) per cap_map modern-hopfield row; substrate's underlying-binding capacity may need rebuilding at higher capacity tier first

## Cross-rail per [[feedback-experiment-bias-master-checklist]]

- Per BIAS-13/14/15: synthetic data only; no contamination from substrate's existing 588 atoms; regime checks at N=2048, 8192, 16384 to verify finite-N vs thermodynamic
- Per Q (suspect 1.000): if any arm hits 1.0 heldout, suspect leak; per-arm metrics + heldout-construction audit mandatory
- Per N (Cramer-Rao): for percolation candidate (#2), the curve-fit must include CI bands; not just point estimate
- Per S (band-calibration regime): top-1-vs-top-5 reporting mandatory; capacity-feasible check at N=8192 (50x5=250 items >> M_c at default density)

## Citations (verified count: 18)

- [SCAN benchmark / Meta-Learning for Compositionality (Lake & Baroni)](https://www.nature.com/articles/s41586-023-06668-3)
- [Tensor Product Representation Soft-TPR 2024](https://arxiv.org/html/2412.04671v3)
- [Compositional Generalization Across Distributional Shifts (NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/file/ccfa9ba5a84d0e4c620093d27102b7c5-Paper-Conference.pdf)
- [Resonator Networks 1: Frady, Kent, Olshausen, Sommer 2020](https://par.nsf.gov/biblio/10294577)
- [Resonator Networks 2: Factorization performance (Neural Computation)](https://direct.mit.edu/neco/article/32/12/2332/95653/Resonator-Networks-2-Factorization-Performance-and)
- [A comparative study of nonlinear cleanup rules in resonator networks (Frontiers in AI 2026)](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1793314/full)
- [Sparse Distributed Memory Wikipedia](https://en.wikipedia.org/wiki/Sparse_distributed_memory)
- [Backprop as Functor / Category Theory ML survey 2024](https://arxiv.org/pdf/2408.14014)
- [Schema-Dependent Gene Activation Tse et al. Science](https://www.science.org/doi/10.1126/science.1205274)
- [Predictive Coding Review (Rao-Ballard / Friston)](https://arxiv.org/pdf/2107.12979)
- [Active Predictive Coding 2024 (Rao)](https://direct.mit.edu/neco/article/36/1/1/118264/Active-Predictive-Coding-A-Unifying-Neural-Model)
- [RG / Deep Learning Universality 2025](https://arxiv.org/html/2510.25553v1)
- [Combinatory Categorial Grammar tensor semantics](https://arxiv.org/pdf/1608.07115)
- [End-to-End Differentiable Proving (Rocktäschel)](https://arxiv.org/pdf/1705.11040)
- [Cohen & Welling Group Equivariant CNNs 2016](https://arxiv.org/pdf/1602.07576)
- [β-VAE / Understanding Disentangling](https://arxiv.org/pdf/1804.03599)
- [Sheaf Neural Networks (Hansen)](https://openreview.net/pdf?id=GgcgIJsT8HD)
- [Relational CBMs](https://arxiv.org/html/2308.11991v2)
- [Hyperdimensional Computing / LARS-VSA 2024](https://arxiv.org/html/2405.14436v1)
- [RESOLVE: VSA Relational Reasoning 2024](https://arxiv.org/pdf/2411.08290)
- [CLS Theory Updated (Kumaran, Hassabis, McClelland 2016)](https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(16)30043-2)
- [Relational Bottleneck Trends Cog Sci 2024 (Webb, Goyal, Smolensky)](https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(24)00080-9)
- [Modern Hopfield Universal framework (Millidge)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7614148/)
- [Pattern Separation CA3 DG (PMC3812781)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3812781/)
- [Percolation Model of Emergence (ICLR 2025 / arxiv 2408.12578)](https://arxiv.org/pdf/2408.12578)
- [Tropical Attention (arxiv 2505.17190)](https://arxiv.org/pdf/2505.17190)
- [Prototypical Networks (Snell et al. NeurIPS 2017)](https://www.cs.toronto.edu/~zemel/documents/prototypical_networks_nips_2017.pdf)
- [Multi-hop KG completion / compositional reasoning surveys](https://arxiv.org/pdf/2407.17396)

(Verified count: 28 cited; >= 18 candidates supported)

## Calibration sanity-check

- Top-5 P_deflated range: 0.25 - 0.42 -- all within published calibration bounds; none above 0.50 novel-synthesis cap
- HARD_FAIL thresholds explicit on every candidate
- Substrate-mine-first invoked (588 atoms, prior cells noted)
- Brain-is-existence-proof referenced but does NOT inflate Ps above ceiling
- Negative findings would not BLOCK; per [[feedback-route-negatives-to-research-2x-3x-revival-drills]], they trigger revival drills

## Next-drill candidate (post-cycle)

If experiment cycle HARD_PASSes #1 or #3: next drill is COMPOSITIONALITY-CHAIN -- "given relational bottleneck OR resonator works, does it CHAIN past depth 3?" Maps to substrate's existing depth-2 ceiling.

If HARD_FAIL on top-3: next drill is "dense Hopfield / Krotov exponential capacity as substrate substrate replacement" (modern-hopfield is fruit-bearing per advisor).

If MIDDLE_BAND across all: next drill is on PERCOLATION (#2) -- the data-coverage angle is independent of mechanism and may reframe the gap entirely.

---

end of note.
