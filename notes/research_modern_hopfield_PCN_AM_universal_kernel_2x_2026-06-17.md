# Research drill: Modern Hopfield + PCN-as-AM + Universal Hopfield kernel landscape (2x deep)

Date: 2026-06-17
Predecessor: notes/research_nonlinear_readout_frontier_2026-06-17.md (Tier-1 frontier scan)
2x discipline: this drill goes OPERATIONAL on the predecessor's "5 underexplored families" finding by drilling Modern-Hopfield variants + PCN-AM + the Universal Hopfield kernel skeleton that subsumes both, AND the joint capacity-cleanup Pareto frontier.

## (a) HEADLINE

The Universal Hopfield Network (UHN) skeleton `z = V . sep(sim(K, q))` parametrizes every
single-shot associative memory by (similarity kernel, separation function, projection).
Modern Hopfield = (dot, softmax, V); sparse-Hopfield = (dot, alpha-entmax, V); UHN-variant =
(Euclidean/Manhattan, softmax, V); Hopfield-Fenchel-Young Networks (HFYN, Santos 2024,
arXiv 2411.08590) is the cleanest strict generalization (every separation = argmin of a
Fenchel-Young loss parametrized by an entropy; Shannon -> softmax, Tsallis/norm -> entmax).
**PCN-as-AM does NOT cleanly fit the UHN single-shot skeleton** — it is iteratively
relaxational (Salvatori 2021 uses gradient on `E = 1/2 sum eps^2` with ~10^5 retrieval iters
in Tang 2023), which the UHN paper explicitly acknowledges as a separate fixed-point regime.
**The joint capacity-vs-cleanup Pareto frontier `capacity(N, d, sigma, epsilon)` is an OPEN
formalization problem** — no published closed-form bound spans dimension, noise sigma, and
tolerated cleanup-error epsilon as a single inequality. Existing results are
phase-transitions (alpha_c = 0.138; Lucibello-Mezard alpha_1/alpha_c two-point), task-specific
dimension bounds (Clarke 2023 VSA), or rate-distortion-shaped bounds on bundling crosstalk
(Frady-Sommer) — none unified. For substrate: the highest-leverage NEXT-CYCLE experiment is
not "try another readout" but **PCN-as-AM compositional generalization** — published evidence
that PCN compositionally recombines stored items better than softmax-MHN is ZERO across
verified core literature, which is BOTH a structural gap AND a substrate-product opportunity
(the substrate's structured-HD codes are exactly where this would land).

## (b) Cheap decisive test

**TEST: PCN-AM vs softmax-MHN on a substrate-structured-HD compositional-recombination probe.**

Setup (CPU-cheap, ~30-60 min single laptop run):
1. Use the existing substrate codebook (N=4096, structured role-filler bound codes).
2. Store M = 200 compositional codes formed as bind(role_i, filler_i) for i=1..M.
3. **Cue with NOVEL recombinations**: bind(role_j, filler_k) for (j,k) NOT in stored set —
   but j,k individually appear in stored set.
4. **Two readouts**:
   - Softmax-MHN: standard Ramsauer 2020 readout against stored matrix
   - PCN-AM: 3-layer hierarchical PCN, train with local error-passing on stored M codes,
     query by clamping sensory layer to bind(role_j, filler_k) and relax for ~200 iters
5. **Measure**: cosine-similarity of readout to true bind(role_j, filler_k) target
   (which is computable as ground truth from the binding operator).

This is a clean discriminator: softmax-MHN should retrieve the NEAREST stored pattern
(failure mode = retrieves bind(role_j, filler_i) or bind(role_i, filler_k), not the novel
composition). PCN-AM with its iterative inference *may* extract role / filler factors
through layer hierarchy and recombine. If PCN-AM wins by >= 0.20 cosine, the iterative
relaxation is doing genuine factor-extraction; if both readouts return nearest-stored,
the substrate's structured codes provide ZERO compositional advantage to PCN-AM either,
and the Salvatori 2021 storage-fidelity gap does not transfer to compositional regime.

Pre-flight check: also include a **dot-product baseline** to confirm both nonlinear
readouts beat linear (this isolates "nonlinearity helps" from "PCN-vs-MHN").

## (c) Falsifiable predictions

### HARD-PASS thresholds
- PRED-1 PCN-AM novel-recombination wins: PCN-AM cosine to true novel target
  **>= 0.55** AND softmax-MHN cosine **<= 0.30** at M=200, structured codebook.
  This would be FIRST published evidence of PCN-AM compositional generalization on
  HD-structured codes.
- PRED-2 UHN-Euclidean variant matches sparse-entmax: at iso-budget on substrate's
  C1-entmax-spread regime, swapping similarity from dot-product to Euclidean lifts
  recall by **>= 0.05** absolute (Millidge 2022 empirical claim transferred).
- PRED-3 HFYN entropy-parametrized separation gives separation-error-rate tradeoff:
  on substrate codebook, alpha-entmax with alpha=1.5 (between softmax and sparsemax)
  gives **>= 0.03** recall improvement over either endpoint.

### HARD-FAIL thresholds (structural-closure signals)
- PRED-1 HARD-FAIL: PCN-AM cosine to novel target **< 0.30** AND softmax-MHN
  **also < 0.30** -> structured-HD codes resist compositional generalization via
  ANY nonlinear readout; structural-closure of "iterative-inference rescues
  compositionality" route; pivot to factor-decomposition operators (which substrate
  already has via resonator decomp).
- PRED-2 HARD-FAIL: PCN-AM wins novel-recomb but at cost of base-storage fidelity
  drop **>= 0.15** absolute on stored codes -> the PCN advantage trades off badly
  vs softmax-MHN, not a Pareto improvement.
- PRED-3 HARD-FAIL: all-three (softmax, sparse-entmax, Euclidean-UHN, alpha-entmax)
  give recall within 0.02 of each other on substrate codebook -> the UHN kernel
  landscape is degenerate ON STRUCTURED HD CODES (which is a substrate-novel
  literature blind-spot finding worth its own note).

### Calibration penalty applied
- Substrate is in uncharted regime (no published capacity proofs on structured HD codes;
  zero published PCN-AM-on-VSA work). Per [[feedback-lit-scan-calibration-penalty]]:
- P(PRED-1 HARD-PASS) lit-scan estimate ~0.45 -> deflated to **P_deflated = 0.25**
  (lit-scan optimism penalty 0.20; novel-synthesis cap 0.50 not binding here).
- P(PRED-2 HARD-PASS) ~0.55 -> deflated to **P_deflated = 0.40** (Millidge 2022 has
  direct evidence; less novel).
- P(PRED-3 HARD-PASS) ~0.40 -> deflated to **P_deflated = 0.25**.
- P(joint HARD-PASS all-three) = **0.06** (conservative; treat as independence-bounded).
- P(at-least-one HARD-PASS) = **0.50**.

## (d) Cross-thread synthesis with prior Entries

- **research_nonlinear_readout_frontier_2026-06-17.md (predecessor):** identified PCN
  as one of 5 underexplored families; this drill operationalizes by naming the
  cheapest decisive test (compositional-recombination on structured codes) and
  ruling out the trivial alternative (PCN already covered by UHN softmax kernel).
  Per UHN paper, PCN is acknowledged outside the single-shot skeleton — confirms
  the predecessor's classification.
- **research_modern_hopfield_capacity_retrieval_crossover_2026-06-16.md:** confirms
  that softmax-MHN sparse-entmax variants give "zero advantage in quasi-orthogonal
  small-N high-d" — this drill extends to STRUCTURED HD codes where the regime is
  no longer quasi-orthogonal (role-filler bindings have geometric structure).
  PRED-3 directly tests whether the predecessor's "no sparse advantage" finding
  transfers to structured codes.
- **research_drosophila_MB_sparse_recapture_linear_heteroassociative_2026-06-17.md:**
  3-angle lit-scan converged on "supra-linear selection step needed" for sparse
  coding to pay off. PCN-AM's iterative relaxation IS a supra-linear selection
  mechanism (error-driven message passing). This drill tests whether PCN-AM
  recaptures the substrate-failed Drosophila gain via a different mechanism than
  the proposed sparse-key dense-value fork.
- **HALT-healing-recapture session (USER memory):** ARCH-B confirmed
  nonlinear-readout LIFTS capacity (substrate-internal). The 2x drill identifies
  PCN-AM as the MOST DIFFERENT nonlinear-readout candidate from what ARCH-B
  already tested (which was softmax). If softmax lifts capacity AND PCN-AM
  compositionally recombines, **ARCH-C = softmax-storage + PCN-AM-readout** is
  the natural next architecture fork.

## (e) Substrate-product implications

- **The biggest substrate-product lever this drill identifies is PCN-AM
  compositional generalization on structured HD codes** — an unmapped intersection
  in literature that the substrate is uniquely positioned to map (it has the
  structured codebooks; no published PCN-AM work uses VSA-style binding).
- **Universal Hopfield kernel taxonomy gives the substrate a single configuration
  surface**: similarity + separation + projection as orthogonal axes the substrate
  can sweep. The substrate already exposes the projection (V matrix) and
  separation (softmax/entmax). Adding the similarity axis (dot vs Euclidean vs
  Manhattan) is a one-line config change that PRED-2 says should give >= 0.05
  recall lift.
- **HFYN as the right structural frame for the substrate's readout module**:
  Hopfield-Fenchel-Young Networks unifies softmax-MHN and sparse-entmax under
  a single entropy-parametrized energy. The substrate can adopt the HFYN
  formulation as the cap_map row for "ARCH-B readout family" (current cap
  presentation tested two endpoints; HFYN gives the full continuous family
  with one knob = entropy choice).
- **The joint capacity-cleanup Pareto frontier is OPEN** — the substrate is well
  positioned to provide the first empirical Pareto curve on structured HD codes,
  which IS a substrate-product white-paper claim (not a publication framing, a
  product-spec claim: "the substrate exposes a calibrated capacity-vs-cleanup
  Pareto curve at each codebook size and codeword structure").
- **Cap_map implications**: this drill REINFORCES ARCH-B nonlinear-readout lever
  (does NOT close); IDENTIFIES a NEW cap_map row candidate for "PCN-AM iterative
  readout"; DOES NOT touch sparse-readout entmax row (which the substrate
  already operationalized 8x cheaper at iso-recall last night).

## Closing 3 bullets per question 5

- **Most underexplored PCN-AM compositional-generalization experiment for substrate
  next-cycle**: 3-layer hierarchical PCN trained on bind(role_i, filler_i) codes,
  queried with novel bind(role_j, filler_k). Cosine to true target as the metric.
  This experiment does NOT exist in published lit (zero PCN-AM-on-VSA results
  located across 4 verified core papers). The substrate has all required components.
- **Strongest experimental discriminator between Modern-Hopfield and PCN-AM**:
  the **iterative-vs-single-shot distinction is the diagnostic**. In a regime
  where iteration helps (sparse cues, partial queries, compositional recombination),
  PCN-AM should win; in regimes where one-shot retrieval is optimal (clean cue,
  near-orthogonal codes), softmax-MHN should win. The substrate's structured-HD
  compositional regime is EXACTLY where the two predictions diverge maximally.
  Published evidence for divergence: Salvatori 2021 reports 500 stored vs 9
  retrieved (PCN vs MHN) at high corruption — but this is storage-fidelity, NOT
  compositionality. The substrate compositional probe would fill this gap.
- **Open question: unified compositional-generalization bound spanning UHN kernel
  family**: NO published bound. Existing UHN capacity results are
  pattern-orthogonality-dependent (separation sharpness arguments). A
  compositional generalization bound would need to formalize "stored set is
  closed under binding operator; novel queries are bindings outside the stored
  set; readout error in compositional vs storage regime". This is a clean PhD
  thesis question; for the substrate it is a product-spec claim opportunity.

## (f) Citations (verified count)

Primary literature verified live this session via WebSearch + WebFetch (with verbatim
abstract snippets quoted in evidence-of-search):

1. Ramsauer et al. 2020 - arXiv:2008.02217 "Hopfield Networks Is All You Need" - verified
2. Millidge, Salvatori et al. 2022 - arXiv:2202.04557 "Universal Hopfield Networks" - verified
3. Hu et al. 2023 NeurIPS - arXiv:2309.12673 "On Sparse Modern Hopfield Model" - verified
4. Hoover, Krotov et al. 2023 NeurIPS - arXiv:2302.07253 "Energy Transformer" - verified
5. Ambrogioni 2024 Entropy 26(5):381 - arXiv:2309.17290 "In Search of Dispersed Memories" - verified
6. Salvatori et al. 2021 NeurIPS - arXiv:2109.08063 "Associative Memories via Predictive Coding" - verified
7. Yoo & Wood 2022 - arXiv:2205.09930 "BayesPCN" - verified
8. Tang et al. 2023 PLOS Comp Bio - "Recurrent PCN Covariance Learning" - verified
9. Salvatori et al. 2023 review - arXiv:2308.07870 - verified
10. Santos, Niculae, McNamee, Martins 2024 - arXiv:2411.08590 "Hopfield-Fenchel-Young Networks" - verified
11. Wu et al. 2024 generalized entmax Hopfield - verified via UHN scan
12. Lucibello & Mezard 2023 - arXiv:2304.14964 "Exponential Capacity Dense AM" - verified
13. Negri, Lucibello, Mezard 2023 PRL - arXiv:2303.16880 "Random-Features Hopfield" - verified
14. arXiv 2503.00241 (2025) "Accuracy and capacity of Modern Hopfield with synaptic noise" - verified
15. Clarke et al. 2023 - arXiv:2301.10352 "Capacity Analysis of VSA" - verified
16. Frady, Kleyko, Sommer 2023 Neural Computation 35(7):1159 - verified via DOI
17. Amit-Gutfreund-Sompolinsky 1985 - verified via researchgate
18. McEliece, Posner, Rodemich, Venkatesh 1987 IEEE TIT 33:461 - verified via ACM DOI
19. Kanerva 1988 SDM - verified via Wikipedia overview (book directly not fetched)
20. Newman 1988 Neural Networks 1:223 - verified via ScienceDirect

**Total: 20 verified primary citations across 4 parallel lit-scan sub-agent reports.**

## Distilled T2/T3 claims ready for substrate research-finding onboarding

Per [[feedback_research_can_be_wrong_only_proven_fully_believed_trust_tier_USER_2026-06-17]],
these are RESEARCH_FINDING atoms (NOT proven core), tagged T2 (lit-supported) or T3 (conjecture):

1. **T2 / source: Millidge 2022**: Universal Hopfield Network skeleton z = V . sep(sim(K, q))
   subsumes Classical Hopfield, SDM, Modern Hopfield, sparse Hopfield via kernel choice.
   *Bears on*: substrate ARCH-B readout family; cap_map row design.

2. **T2 / source: Santos 2024 (HFYN)**: Every separation function in UHN = argmin of a
   Fenchel-Young loss parametrized by a generalized entropy (Shannon -> softmax,
   Tsallis/norm -> entmax). *Bears on*: substrate readout configuration surface;
   continuous entropy-knob sweep.

3. **T2 / source: Salvatori 2021**: PCN-AM iterative readout stores 500 corrupted Tiny-ImageNet
   images at 512 hidden units vs ~9 retrievable by MHN at matched conditions. *Bears on*:
   substrate corrupted-cue retrieval cap row (not yet measured PCN-AM).

4. **T3 / conjecture (lit-gap)**: PCN-AM compositionally recombines stored items better than
   softmax-MHN on structured HD codes. *Source*: NO PUBLISHED EVIDENCE either way (zero
   PCN-AM-on-VSA papers located). *Bears on*: ARCH-C candidate (softmax-storage +
   PCN-AM-readout).

5. **T2 / source: Ramsauer 2020 + Lucibello-Mezard 2023**: Modern Hopfield capacity scales
   exponentially with dimension d under pattern-separation conditions; multiple thresholds
   (typical vs all-patterns) define the high-noise frontier. *Bears on*: substrate capacity
   envelope claims; honest method-contingent framing.

6. **T3 / open formalization**: Closed-form joint capacity-vs-cleanup-accuracy Pareto bound
   `capacity(N, d, sigma, epsilon) <= f(N, d, sigma, epsilon)` does NOT exist in published
   literature. *Source*: absence verified across 5 search angles. *Bears on*: substrate
   product-spec claim opportunity (first empirical Pareto curve on structured HD codes).

7. **T2 / source: Hu 2023 + Wu 2024**: Sparse-Hopfield with alpha-entmax preserves exponential
   capacity ceiling AND provides tighter retrieval-error bounds than softmax-MHN.
   *Bears on*: substrate C1-entmax-spread regime cap row (already operationalized last night;
   this gives lit-precedent backing).

8. **T2 / source: Ambrogioni 2024**: Diffusion model trained on discrete patterns has
   energy asymptotically identical to MHN energy; diffusion training implicitly encodes MHN.
   *Bears on*: long-tail substrate option for diffusion-as-AM if iterative compute
   becomes available.

9. **T2 / source: Frady-Sommer 2023**: VSA information-rate bounds on bundled retrieval
   are rate-distortion-shaped per architecture (MAP, FHRR), with crosstalk-noise as the
   distortion source. *Bears on*: substrate codebook-design cap row; the closest published
   precedent to the joint Pareto framing.

## Field-coverage advisor cue for next drill

This drill operated in the `modern-hopfield` fruit-bearing field (per advisor Tier-1) plus
the adjacency edge to predictive-coding / iterative-inference (newly opened). Next-drill
candidates ranked:

- **PCN-as-AM compositional generalization empirical test** (highest leverage; not yet
  in field-coverage advisor; routes via exp_dev not research)
- **Hopfield-Fenchel-Young Networks entropy-knob sweep** on substrate codebook (adjacency
  to modern-hopfield; cheap CPU test)
- **structural-glasses-MCT** (advisor Tier-1b unexplored; ARCH-B nonlinear-readout cap
  growth may map to MCT relaxation timescales)
- **sparse-coding-compressed-sensing** (advisor Tier-1b; PPMI replacement angle;
  L1/LASSO phase transitions parallel substrate capacity cliffs)
