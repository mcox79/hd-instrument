# Research: fair-test benchmarks for a non-commutative directed-chain operator vs. degree/frequency baselines

Filed by: research (Sonnet lit-scan, single-agent cycle) | 2026-07-15
Topic statement: is there real directed-biological-network data on which a non-commutative,
order-sensitive relational operator (per-edge-type learned matrix, composition order matters:
"regulates-then-activates" != "activates-then-regulates") can show measurable value over a
plain symmetric/frequency (degree/hub) baseline, or is the field's directed-edge signal
degree-dominated as feared?

## HEADLINE

The fair-test infrastructure for exactly this question already exists in public bio-network
literature (XSwap / edge-prior framework, Zietz et al.) and is directly applicable to directed
TF-target-gene data. Independent evidence (ComHub on DREAM5) CONFIRMS the degree-dominance trap
is real and severe for at least one canonical directed-GRN task (hub/out-degree ranking rivals
sophisticated inference methods). No benchmark was found that already isolates genuine
multi-hop ORDER-SENSITIVE chain composition (A regulates-then-activates B != activates-then-regulates)
as distinct from single-hop regulator->target direction — this is a gap, not a solved case, and
matches this project's prior finding that real-data symmetric/additive baselines are hard to beat
([[project_fair_test_refute_and_scale_reframe...2026-07-15]] cross-thread, see Synthesis below).

## Cheap decisive test

Adopt the XSwap/edge-prior methodology directly:
1. Take a directed TF-target-gene network (Hetionet's `Gene>regulates>Gene` edge type, or
   DREAM5 gold-standard regulatory networks — both public and downloadable).
2. Compute the degree-only "edge prior" baseline (closed-form from source out-degree / target
   in-degree, per Zietz et al. PMC9881952).
3. Generate XSwap degree-preserving directed permutations (in/out-degree sequence held fixed,
   `allow_antiparallel` param controls whether A->B and B->A are distinguished).
4. Score any order-sensitive operator candidate against held-out edges from a DIFFERENT
   degree-distribution split (not same-network held-out — same-network held-out is exactly
   where Zietz et al. show degree alone hits AUROC >=0.9, so it's not discriminating).
5. The candidate operator only "wins" if it beats the edge-prior AUROC specifically in the
   cross-distribution / degree-preserved-permutation regime, not in the easy same-network split.

This is a CHEAP test: XSwap is a pip-installable Python package (`hetio/xswap`), DREAM5 and
Hetionet data are both public downloads, no wet-lab or novel data collection needed.

## Falsifiable predictions

**HARD-PASS** (operator shows genuine value): on the XSwap degree-preserved-permutation split
of a directed TF-target network, the order-sensitive composition operator beats the edge-prior
baseline AUROC by a margin that SURVIVES degree-preserving randomization (i.e. the win doesn't
collapse when node degrees are held fixed but edge identities are shuffled). Numeric bar:
delta-AUROC >= 0.05 over edge-prior on the degree-preserved permutation test, replicated across
>=2 independent directed networks (e.g. DREAM5 E. coli + S. cerevisiae, or Hetionet + one DREAM5
network).

**HARD-FAIL** (matches the feared trap): delta-AUROC < 0.02 over edge-prior on the degree-preserved
split, OR the operator's apparent win on a naive same-network held-out split disappears/reverses
under XSwap permutation (the classic degree-artifact signature per Zietz et al.'s cross-network
finding, where edge-prior AUROC dropped from >0.9 to ~0.5 once degree distributions were
decoupled). ComHub's finding (hub-only ranking rivaling most DREAM5 inference methods) is the
strong prior toward HARD-FAIL for single-hop regulator/target tasks specifically.

## Cross-thread synthesis

This connects directly to the active thread
[[project_fair_test_refute_and_scale_reframe_are_we_reasoning_too_far_ahead_of_grounded_data_2026-07-15]]:
the real-data yeast-epistasis linchpin already REFUTED a symmetric-vs-additive gain on readable
biological interaction data. This lit-scan adds a SECOND, independent confirmation of the same
qualitative pattern from a different corner of biology (directed GRN edges): wherever a network
task can be explained by node-level marginal properties (degree, hubness) it tends to BE
explained by them, and published benchmarks that don't explicitly control for this (same-network
held-out splits, no XSwap-style permutation) will silently overstate a fancier operator's value.
The one candidate NOT yet degree-tested — genuine multi-hop signed chain composition on SIGNOR's
signed/directed causal-chain data — is the most promising REMAINING angle precisely because it
hasn't been checked either way; it is a legitimate next-drill candidate, not a dismissed one
(per [[feedback-dont-dismiss-adjacent-methods]]).

## Substrate-product implications

- Before spending build effort on a non-commutative per-edge-type composition operator, run the
  cheap XSpwap-style fair test above on a small public directed dataset FIRST. This is a data-only,
  no-GPU-cell task — could be done as a lightweight local analysis, not a queue dispatch.
- If HARD-FAIL replicates (most likely per ComHub prior), the product framing should shift:
  the operator's value proposition is NOT "beats degree on a real directed regulatory network,"
  it's whatever the operator's win looks like on a genuinely non-degree-dominated regime
  (e.g. synthetic conjunctive-chain data, or the SIGNOR-signed-chain angle if that gap gets
  filled and shows real signal).
- If HARD-PASS, this becomes a strong, citable, real-data validation asset for the reasoning
  architecture (additive_map improvement / native-bind work), directly answering the
  "is this just synthetic-data theater" pushback with public GRN/DREAM5 data.

## Citations (verified count: 8)

1. Zietz et al., "The probability of edge existence due to node degree: a baseline for
   network-based predictions" — PMC9881952 / manuscript at greenelab.github.io/xswap-manuscript.
   Directly builds the directed-network-capable degree-only edge-prior baseline; quantifies
   AUROC >=0.95 (17/20 networks) same-network held-out, collapsing to ~0.5 cross-distribution.
2. `hetio/xswap` (GitHub) — degree-preserving randomization tool, `allow_loops`/`allow_antiparallel`
   params for directed networks. Public, pip-installable.
3. Studený & Sonnhammer et al., "ComHub: Community predictions of hubs in gene regulatory
   networks" — BMC Bioinformatics 2021 / PMC7871572. Hub/out-degree-only ranking rivals most
   individual DREAM5 GRN inference methods — direct empirical confirmation of the degree trap.
4. "Bayesian Copula Directional Dependence is Cross-Network Robust for Gene-Regulatory Pair
   Direction: A Benchmark Study on DREAM5" — arXiv:2606.29402 (2026). Directly targets
   regulator/target direction prediction with cross-network generalization testing; explicit
   degree-baseline comparison NOT confirmed from available extract — flagged UNVERIFIED,
   needs direct read of results tables before relying on it.
5. Chevalley et al., "A large-scale benchmark for network inference from single-cell
   perturbation data" (CausalBench) — Communications Biology, 2025. Real interventional
   ground truth; no degree-baseline ablation found in available text — flagged as
   promising-but-unverified.
6. SIGNOR 3.0 — Nucleic Acids Research 2023 (PMC9825604 / academic.oup.com/nar/article/51/D1/D631).
   Public signed+directed causal-chain data (~8400 entities), path-tracing tool. No degree-preserving
   baseline benchmark found against it — an OPPORTUNITY GAP, not a tested-and-failed case.
7. dGPredictor / MetaQSAR metabolic-reaction-direction literature (PLOS Comp Bio;
   PMC8512547; PMC3102224). Reaction direction is thermodynamics/structure-driven, not a
   chain-composition-order problem — DEPRIORITIZED as a poor mathematical match for this
   question, not because it's degree-capped but because it doesn't test order-sensitivity.
8. DREAM5 challenge gold-standard data (in silico, E. coli, S. aureus, S. cerevisiae) — public,
   used as the substrate for candidates #3 and #4 above.

P_deflated = 0.30 (lit-scan calibration penalty applied; this is a single-Sonnet-agent cycle,
not a multi-agent breadth dispatch, so confidence in the ranked-list completeness is further
discounted below the standard 0.15-0.25 deflation band). The HARD-FAIL prior (degree dominates)
is assessed as more likely than HARD-PASS based on the ComHub evidence, but this has NOT been
run as the cheap decisive test yet — it is a recommendation, not a result.

## Next-drill candidate

SIGNOR signed/directed causal-chain data + an XSwap-style directed degree-preserving permutation,
specifically targeting multi-hop ORDER-SENSITIVE composition (not just single-hop direction) —
this is the one angle in the ranked list that is genuinely untested either way, per the
dont-dismiss-adjacent-methods discipline.
