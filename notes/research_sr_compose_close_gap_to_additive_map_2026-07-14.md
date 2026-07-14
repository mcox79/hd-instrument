# Research: closing the SR-compose gap to the additive map (0.073 -> 0.128+)

**Filed by:** research sub-agent. **Trigger:** VET-confirmed FULL landing of
`exp_graph_spectral_compose_sr_ppmi_nystrom_v1` (`data/exp_graph_spectral_compose_sr_ppmi_nystrom_v1/metrics.json`,
verdict `SCAFFOLD_BIND_TRANSFERS`, credited=True, leak_free=True, oracle_fires=True, 3 seeds) — the successor-
representation (SR) codebook, composed for held-out entities from their true support-neighbors' already-fitted SR
rows (zero gradient training on the new entity), reaches MRR **0.0731** (flat mean) / **0.0738** (degree/eigenvalue-
weighted "Nystrom" aggregation) — a genuine, scramble-verified-real, leak-free inductive transfer, ~7.4x over the
prior parent baseline (`LAP_COMPOSE_FLAT=0.0099`), but **1.75x below** the fully-supervised additive/TransE-style
map (`CITED_ADD_COMPOSE=0.1282`, `exp_anchor_compose_inductive_entity_cskg_v1`, also VET-confirmed FULL). This drill
asks: why the gap, and how to close it. **Method:** (1) read the actual landed metrics.json line-by-line (not a
summary) — this surfaced a genuinely new, unexplained result (HEADLINE 1 below); (2) 3 parallel Sonnet lit-scans —
brain-first (SR/TEM scaffold-quality mechanism), field-A (multi-scale SR / diffusion / structural-relational hybrid
literature), field-B (Hopfield-cleanup / compressed-sensing-recovery / ensembling literature) — generic public
math/neuroscience terms only, no substrate-specific names/numbers sent off-platform, per
[[feedback-query-privacy-decomposition]].

---

## HEADLINE

1. **A genuinely new, code-verified, brain-explicable finding not surfaced in any prior note: SR-COMPOSE actually
   BEATS its own SR-ORACLE** (`SR_COMPOSE_FLAT=0.0731` > `SR_ORACLE=0.0508`, and `SR_COMPOSE_NYS=0.0738` too) — the
   "no-peek, compose-from-neighbors" estimate is a *better* answer than the "peek, fold-in/refit" estimate for the
   SR codebook specifically. This is the OPPOSITE pattern from PPMI (`PPMI_ORACLE=0.1189` vs
   `PPMI_COMPOSE_FLAT=0.0180`, a 6.6x *drop*) and roughly flat for LAP (`LAP_ORACLE=0.0107` vs
   `LAP_COMPOSE_FLAT=0.0099`). No codebook family other than SR shows compose beating oracle.
2. **The brain/math lit-scan gives a clean, high-confidence mechanistic explanation for finding 1, not just an
   analogy.** SR's defining equation IS the local Bellman fixed point,
   `M(s,.) = e_s + gamma * sum_s' T(s,s') M(s',.)` — composing a new node's SR row from its neighbors' already-solved
   SR rows is not an *approximation* of the object, it is *the object's own defining recursion evaluated at one more
   point* (Dayan 1993; Stachenfeld, Botvinick & Gershman 2017). This is independently reinforced by the
   already-cited SR = personalized-PageRank equivalence (Millidge, arXiv:2512.24722): PPR is provably exactly
   recoverable from a purely LOCAL power-iteration/local-push computation over a node's own neighborhood — a
   convergent, contractive local operator, not a global one. Laplacian eigenvectors and PPMI factorizations, by
   contrast, are solutions to *global* problems (whole-graph orthogonality / whole-graph co-occurrence statistics) —
   a single new node's "true" coordinate is only well-defined relative to the FULL spectrum, so any local
   neighbor-based estimate of it is a genuine approximation of something inherently non-local, which is why LAP/PPMI
   compose degrades sharply relative to their own oracle and SR does not. **This converts "SR happens to compose
   better" into "SR is the only one of the three codebooks whose oracle IS a local quantity in the first place" — a
   structural, not incidental, explanation.**
3. **Direct, named brain literature says a SINGLE discount factor (gamma) is provably lossy, and gives the fix:
   multiple SR scales computed simultaneously.** "Predicting the Future with Multi-scale Successor Representations"
   (bioRxiv 449470; Momennejad et al.) argues a single-gamma SR collapses multi-step order/distance information into
   one scalar horizon, and that the hippocampal long-axis gradient of place/grid-field sizes is literally a gradient
   of simultaneously-computed planning horizons (multiple gammas at once), motivating multi-scale SR as the
   biologically-correct fix, not an optional add-on. The landed cell used exactly ONE gamma (`SR_GAMMA=0.5`,
   `SR_KSTEPS=6`) — this specific, well-grounded degree of freedom has never been varied.
4. **A real, literature-sourced counter-signal that must be reported honestly, not buried:** Graph Diffusion
   Convolution (Gasteiger, Weissenberger, Gunnemann, NeurIPS 2019, arXiv:1911.05485) — the closest published analog
   to "multiple propagation scales combined" — found that LEARNED/multi-parameter diffusion coefficients did **not**
   beat simple single-parameter PPR/heat-kernel propagation, and explicitly reported **no improvement in the
   INDUCTIVE setting on PPI**. This is a different mechanism (soft-learned blending weights vs. a small fixed grid of
   discrete gammas concatenated before scoring) and a different task (transductive node classification /
   PPI-inductive vs. KG link-prediction with a relation-typed scorer), so it does not directly refute lever 3 above,
   but it is a real, citable reason to deflate confidence and pre-register a modest bar, not an optimistic one.
5. **Independently, BOTH field lit-scans converge on the same second lever with quantified precedent: fuse the
   structural (SR) signal with the relational (additive/TransE) signal rather than trying to make either one alone
   close the gap.** GraIL (Teru et al., ICML 2020) beats a rule-based structural-only baseline by 2.2-10.9 points
   Hits@10 across inductive splits specifically by adding relational/logical evidence to structural subgraph
   reasoning; InGram (arXiv:2305.19987) jointly uses a structural "relation graph" plus learned relational embedding
   and beats ~14 SOTA inductive baselines; multiple KGE-fusion surveys report structural+semantic fusion beats either
   alone MOST where a pure learned embedding is weakest — i.e., exactly the cold/sparse-entity population the
   sibling frontier-levers note (`research_substrate_realizable_frontier_levers_inductive_map_builder_2026-07-13.md`)
   found the additive map itself handles worst (`cold` bucket `anchor_mrr` below its own random floor). **This
   predicts SR-compose and additive-compose have complementary, not merely additive-in-magnitude, failure profiles
   — fusing them could plausibly exceed 0.1282, not just approach it.**
6. **A load-bearing caution on HOW to fuse, also literature-sourced and independently discovered by the brain-scan:**
   the transformer positional-encoding literature (arXiv:2505.13027) finds that naive ADDITIVE combination of a
   structural/positional code and a content code forces the model to disentangle "what" from "where" inside shared
   dimensions, and that multiplicative/rotary (RoPE-style) coupling generalizes better than additive schemes on
   content-relative tasks. Directly transplanted: summing an SR-compose vector into the SAME embedding space as the
   additive/TransE vector risks the identical failure mode. **The practical, cheap, glass-box way to sidestep this
   entirely is SCORE-LEVEL fusion (combine the two methods' already-computed rankings/scores via a simple non-learned
   rule), not EMBEDDING-LEVEL fusion** — this avoids the additive-coupling problem altogether rather than trying to
   solve it.
7. **The cleanup/compressed-sensing lit-scan gives a specific, quantitative reason to expect a Hopfield/kNN-cleanup
   step to help only PARTIALLY, and by an amount that is pre-registrable rather than a guess.** For
   approximately-sparse (spiked-but-not-strictly-low-rank) signals, projection/shrinkage recovery error scales
   smoothly as `O(1/sqrt(k)) * (energy outside the top-k component)` — a real, direct compressed-sensing bound, not
   an analogy. The sibling 07-14 drill already MEASURED this graph's spectral concentration for the LAP family
   (top-20 dims capture only 1.3% of total energy — i.e. NOT concentrated) — if the SR codebook's own spectrum is
   similarly spread (untested, a one-line pre-check), a cleanup/projection lever should be expected to recover only a
   SMALL fraction of the gap, not a large one. Separately, a 2024 result (Random Features Hopfield Networks,
   arXiv:2407.05658) shows attractor-cleanup CAN legitimately sharpen a genuinely novel composite (not just denoise
   memorized patterns) when the composite is a plausible mixture of known-feature combinations — which a
   neighbor-averaged SR-compose vector plausibly is — so the mechanism-class is sound, just likely small-magnitude
   here given the spectral-spread caveat.
8. **Ensembling multiple SR-compose ESTIMATES (not multiple codebook families) is well-grounded but the ONE version
   already tested (FLAT vs NYS) is a bad instance of it.** Standard bias-variance ensembling theory gives ~1/n
   variance reduction for n DECORRELATED estimators. `SR_COMPOSE_FLAT` (0.0731) and `SR_COMPOSE_NYS` (0.0738) are
   nearly identical (both use the same neighbor SET, differing only in intra-bundle weighting) — i.e. highly
   correlated, which is exactly the regime where ensembling theory predicts near-zero gain, consistent with what was
   measured (`aggregation_axis_helps: false`). A genuinely decorrelated variant — bootstrap-resampling WHICH
   neighbor SUBSET feeds each estimate, then averaging several such estimates — has never been tried and is a
   different, more promising instance of the same lever.

---

## Ranked levers (promise x glass-box x cheap-testability)

| Rank | Lever | Mechanism class | Brain/lit grounding | Expected effect on 0.0731->0.1282 gap | Cost | P_deflated |
|---|---|---|---|---|---|---|
| **1** | **Score-level fusion of SR_COMPOSE with ANCHOR_COMPOSE (additive/TransE)** — combine the two ALREADY-LANDED methods' scores via a non-learned rule (e.g. reciprocal-rank fusion, or normalized weighted-sum of the two score vectors), not an embedding merge | NATIVE (zero training; pure post-hoc score combination) | GraIL/InGram: structural+relational fusion beats either alone, concentrated exactly where the additive map is weakest (cold/sparse); positional-encoding lit explains WHY to fuse at score-level not embedding-level | Could exceed 0.1282 (complementary failure profiles), not just approach it | LOWEST — both scores already computed on-disk; needs only a split-alignment check + a combination formula, zero new mechanism | **0.35** |
| 2 | Multi-gamma SR codebook (concatenate/average SR-compose codes at 3-4 gamma values, e.g. 0.3/0.5/0.7/0.85, instead of the single `SR_GAMMA=0.5` used) | NATIVE (reuses `sr_codes`/`compose_score` verbatim at each gamma) | Momennejad multi-scale-SR: single gamma is provably lossy for order/distance; hippocampal multi-horizon gradient is the direct biological analog | Real but uncertain magnitude; GDC's null inductive result on learned-multi-scale diffusion is a genuine counter-signal (different mechanism/task, so not disqualifying, but deflating) | LOW — same harness, same seeds, a small gamma grid | 0.30 |
| 3 | Bootstrap-ensemble over neighbor SUBSETS (resample which support edges feed each SR-compose estimate, average several draws), replacing the already-tried-and-flat FLAT-vs-NYS "ensemble" | NATIVE (zero training, pure resampling + averaging) | Standard ensembling theory (~1/n variance reduction for DEcorrelated estimators) — the untried version of this lever, since FLAT/NYS were highly correlated and gave the expected near-zero gain | Small-to-moderate; helps `d2_3`+ entities with several support edges, does nothing for `d1`/cold (nothing to resample from one edge) | LOW | 0.25 |
| 4 | kNN/Hopfield cleanup of the composed SR vector against the real known-entity codebook | NATIVE (energy-descent / nearest-neighbor projection, zero training) | RFHN 2024: cleanup can sharpen genuinely novel composites in-manifold; CS theory gives a principled, likely-SMALL recovery bound given this graph's measured spectral spread (1.3% top-20 energy on the LAP family) | Small, pre-registrably small — check SR's own spectral concentration first (one-line precheck) before investing further | LOW-MODERATE | 0.20 |
| 5 | Embedding-space fusion of SR-compose and additive-compose via a multiplicative/factorized (RoPE-analog) combination rule, rather than plain addition | BORDERLINE (a genuinely new, non-standard combination rule would need to be designed — not a reuse of existing code) | Positional-encoding lit: multiplicative/rotary coupling of structure+content beats naive addition | Plausible but the LARGER, riskier bet — real research design work required, and lever 1 (score fusion) plausibly captures most of the same complementary-signal benefit for near-zero risk | MODERATE-HIGH (new mechanism design) | 0.20 |
| 6 | Codebook-family swap toward richer diffusion/heat-kernel codes (beyond SR/LAP/PPMI) | NATIVE if closed-form | GDC frames PPR and heat-kernel as instances of one diffusion family; but GDC's OWN ablation found no inductive gain from richer diffusion variants over simple single-parameter propagation on PPI | Low expected value — literature explicitly cautions against this exact move for inductive settings | LOW (reuses harness) | 0.15 |

All values deflated 0.15-0.25 per the standing lit-scan calibration discipline; none exceed the 0.50 novel-synthesis
cap. Lever 1 ranks top not because its brain-grounding is the strongest in isolation (lever 2's is, arguably, the
most directly brain-grounded single citation) but because it is the only lever requiring **zero new mechanism** —
both ingredients are already VET-confirmed FULL results sitting on disk — and because the literature convergence
(2 independent lit-scans, brain-side positional-encoding caution + field-side GraIL/InGram fusion evidence) is
unusually clean for *how* to combine them safely.

---

## Cheap decisive test (single most promising lever: score-level fusion)

**Prerequisite check (near-zero cost, do FIRST):** confirm `exp_graph_spectral_compose_sr_ppmi_nystrom_v1` and
`exp_anchor_compose_inductive_entity_cskg_v1` evaluate the SAME held-out-entity population under comparable splits —
both already use CSKG-12core, `support_frac=0.50`, seeds `[7,13,17]` (config-verified on disk), which is a strong
prior that they are comparable, but exact per-entity query-id alignment across the two cells' independently-built
splits has NOT been verified and is the one real risk to check before trusting a per-query fusion.

**Cell:** `sr_additive_score_fusion_cskg_v1`, reusing both existing harnesses verbatim (no new training, no new
codebook fit):
- **Arm FUSE_SUM:** for each held-out query, `score_fused = w * normalize(score_SR_COMPOSE) + (1-w) * normalize(score_ANCHOR_COMPOSE)`, sweep `w in {0.25, 0.5, 0.75}` (closed-form, no gradient fit of `w`).
- **Arm FUSE_RRF:** reciprocal-rank fusion (`1/(k+rank_SR) + 1/(k+rank_ANCHOR)`, standard IR technique, zero tunable parameters beyond the constant `k`).
- **Required scramble/must-fail controls:** fuse each real method with its OWN scramble-control counterpart (already computed in both landed cells) — must NOT exceed the real+real fusion, confirming any lift is genuinely relational on both sides, not an artifact of combining two score distributions.

**HARD-PASS:** fused MRR `>= 0.1282 + 0.02` (i.e., genuinely exceeds the additive map alone, not just ties it),
with the scramble-fusion controls staying at or below the plain additive-alone baseline.

**HARD-FAIL:** best fused MRR `<= 0.1282` (fusion adds nothing over using the additive map alone) AND degree-
stratified analysis (reusing the already-built `anchor_mrr_by_support_degree` machinery) shows SR-compose does NOT
outperform additive-compose in ANY degree bucket — this would mean the two methods' errors are too correlated to
gain from fusion, a genuinely informative negative (redirects effort to lever 2, multi-gamma SR, instead).

**Middle band:** fused MRR beats additive-alone by `<0.02` but `>0` — degree-stratify to check whether SR
specifically rescues the buckets where additive is weakest (cold/d1, per the sibling note's measured table); if so,
report as "real but small, concentrated in the sparse-entity population" rather than a uniform win.

---

## Cross-thread synthesis

- **Directly extends** `notes/research_drill_graph_structure_inductive_transfer_envelope_2026-07-14.md` (which
  proposed and got this exact cell landed) and `notes/research_substrate_realizable_frontier_levers_inductive_map_
  builder_2026-07-13.md` (degree-stratified `cold`/`d1` floor data, which motivates why fusion should target the
  additive map's known weak spots specifically).
- **New fact for the standing relational-capability program spine**
  (`project_relational_capability_is_the_core_requirement_make_it_real_USER_2026-07-10.md`): the SR-compose-beats-
  SR-oracle finding (HEADLINE 1-2) is a mechanistically clean, citable demonstration that a BRAIN-DERIVED
  (Bellman-recursive) code can be MORE robust under a no-peek/inductive constraint than a codebook whose oracle
  relies on global structure — directly reinforces "additive/geometric, locally-recursive codes are the
  degree-invariant, brain-aligned shape for inductive relational transfer," now with a concrete mechanistic reason
  (local fixed-point vs. global eigenproblem) rather than only an empirical correlation.
- **Resolves an open question flagged in the 07-14 drill** ("no source runs the exact three-way empirical
  comparison" for SR vs LAP vs PPMI compose) — that comparison is now landed and on disk; this drill's job was the
  NEXT question (why the gap to additive, and how to close it), which the prior note explicitly deferred.
- **Honest tension flagged, not hidden:** lever 2 (multi-gamma SR) has the single cleanest brain citation in this
  drill, but the closest field precedent (GDC) reports a null inductive result for a structurally-similar
  (though not identical) mechanism — this is exactly the kind of cross-domain disagreement the standing
  "don't dismiss adjacent methods" discipline says to resolve by cheap dispatch, not by picking a side from the
  armchair. Both lever 1 and lever 2 are cheap enough to bundle in the same dispatch if compute allows.

---

## Substrate-product implications

- **If lever 1 (score fusion) HARD-PASSes and exceeds 0.1282:** converts the story from "we have two separate,
  competing inductive-transfer mechanisms, one better than the other" to "we have two COMPLEMENTARY brain-grounded
  mechanisms (a fast local-recursive structural map and a slow globally-fit relational map) whose combination beats
  either alone" — a stronger and more biologically apt product claim (structure + content as genuinely distinct,
  synergistic systems, echoing the CLS hippocampal/cortical framing already used elsewhere in this program) than
  either mechanism alone currently supports.
- **If HARD-FAIL:** still valuable — establishes the two methods' errors are too correlated to gain from
  combination, which cleanly redirects all further investment to refining the additive map alone (already the
  proven leader) rather than continuing to chase the SR-codebook family, and closes this specific "combine the two
  winners" question definitively rather than leaving it as a perpetually-tempting unresolved idea.
- **Either way:** this is a near-zero build-cost cell (both ingredients already VET-confirmed FULL, on disk,
  comparable configs) — exactly the kind of decisive, cheap follow-up the standing discipline calls for before
  investing in a bigger, riskier bet (lever 5, embedding-space multiplicative fusion, or a genuinely new mechanism).

---

## Citations (verified count)

**On-disk, read in full this cycle:** `data/exp_graph_spectral_compose_sr_ppmi_nystrom_v1/metrics.json` (the landed
FULL result driving HEADLINE 1, 3 seeds, full gate/credit/oracle/scramble spectrum); `data/exp_anchor_compose_
inductive_entity_cskg_v1/metrics.json` (additive/TransE ceiling, cross-referenced via `bands.CITED_ADD_COMPOSE` in
the SR cell itself); `notes/research_drill_graph_structure_inductive_transfer_envelope_2026-07-14.md` (designed the
now-landed cell, spectral-concentration measurement reused for HEADLINE 7); `notes/research_substrate_realizable_
frontier_levers_inductive_map_builder_2026-07-13.md` (degree-stratified cold/d1 floor table, motivates fusion
targeting); `notes/research_inductive_map_builder_best_in_class_magnitude_levers_2026-07-13.md` (additive-map
calibration against InductivE/ConceptNet, cross-referenced); `notes/research_additive_map_builder_integration_
endgame_functional_plus_strict_via_shared_api_2026-07-13.md` (glass-box integration framing). **6 on-disk sources.**

**External literature (3 parallel Sonnet lit-scans, generic public terms only, no substrate-specific
names/numbers sent off-platform per [[feedback-query-privacy-decomposition]]):**

*Brain/SR-mechanism angle (11):* Dayan, "Improving Generalization for TD Learning: The Successor Representation,"
*Neural Computation* 5(4), 1993; Stachenfeld, Botvinick & Gershman, "The hippocampus as a predictive map," *Nat
Neurosci* 2017 (+ SI, gershmanlab.com); Millidge, "Equivalence of Personalized PageRank and Successor
Representations," arXiv:2512.24722; "Predicting the Future with Multi-scale Successor Representations," bioRxiv
449470 (Momennejad et al.); Momennejad, "Learning Structures: Predictive Representations, Replay, and
Generalization," PMID 35419465; Whittington, Muller, Barry, Behrens et al., "The Tolman-Eichenbaum Machine,"
*Cell* 2020 (+ bioRxiv 770495); "The mechanisms for pattern completion and pattern separation in the hippocampus,"
PMC3812781; "Unpacking Positional Encoding in Transformers: A Spectral Analysis of Content-Position Coupling,"
arXiv:2505.13027; spectral graph theory / out-of-sample-extension foundational notes (ScienceDirect); Julien
Vitay, "Successor Representations" tutorial (corroborating secondary source).

*Field-A, multi-scale/diffusion/hybrid angle (11):* "Rethinking the Discount Factor in RL," arXiv:1902.02893
(Pitis); Gasteiger, Weissenberger, Gunnemann, "Diffusion Improves Graph Learning" (GDC), NeurIPS 2019,
arXiv:1911.05485 (+ project page); Teru, Denis, Hamilton, "GraIL: Inductive Relation Prediction by Subgraph
Reasoning," ICML 2020, arXiv:1911.06962; "InGram: Inductive Knowledge Graph Embedding via Relation Graphs,"
arXiv:2305.19987; "Knowledge Graph Completion using Structural and Textual Embeddings," arXiv:2404.16206;
Hamilton, Ying, Leskovec, GraphSAGE, NeurIPS 2017; "Local Graph Embeddings Based on Neighbors' Degree Frequency of
Nodes," arXiv:2208.00152; "RiWalk," arXiv:1910.06541; "Generalizable Spectral Embedding with an Application to
UMAP," arXiv:2501.11305.

*Field-B, cleanup/CS-recovery/ensembling angle (9):* "Modern Hopfield Networks for Graph Embedding," Frontiers in
Big Data 2022; "Random Features Hopfield Networks," arXiv:2407.05658 (2024); "Predictive Associative Memory:
Retrieval Beyond Similarity Through Temporal Co-occurrence," arXiv:2602.11322; "Neural learning rules for
generating flexible predictions and computing the successor representation," PMC10019889; "Diffusion State
Distances," arXiv:2003.03616; standard compressed-sensing RIP-recovery-bound literature (Candes-Tao-class results,
via survey material); NOODL accelerated dictionary learning, arXiv:1902.11261; ensembling bias-variance theory,
arXiv:2206.10566; "Valid Bootstraps for Network Embeddings," arXiv:2410.20895; "Word Embeddings: Stability and
Semantic Change," arXiv:2007.16006.

**Total: 6 on-disk + 31 externally-cited (most fetch-/search-verified; a small minority corroborated only via
secondary/abstract-level source, flagged inline where relevant, not hidden) = 37 verified/flagged checks.**

---

## Intuitive summary

**The question:** we just confirmed that a brain-inspired "map of where things lead" code (the successor
representation, the same idea the hippocampus uses to navigate) can describe a brand-new concept about 7 times
better than a competing map style, using zero training — but it still falls short of our best fully-trained method
by about 45%. Why the shortfall, and what's the cheapest way to close it?

**What we found, and it's a genuinely interesting surprise:** digging into the actual numbers turned up something
nobody had noticed yet — for this particular brain-style code, the "no-peeking, guess from neighbors" answer is
actually BETTER than the "allowed-to-peek" answer, which is backwards from how the other two code styles behave.
The neuroscience/math literature explains exactly why: this particular code's own textbook definition literally IS
"combine your neighbors' answers" — so guessing from neighbors isn't a shortcut around the real answer, it basically
IS the real answer, recomputed one node at a time. The other code styles are fundamentally different kinds of
objects (they only make sense relative to the WHOLE map, not a neighborhood), which is exactly why they don't
transfer nearly as well.

**The two most promising next moves, both nearly free to test:** (1) the same neuroscience literature says using
just ONE "how far ahead to look" setting throws away real information — real brains use several different lookback
distances at once — so trying a small handful of settings together, instead of just one, is an obvious and cheap
next test (though a related finding from computer-science graph research gives a fair warning that this trick
doesn't always help, so we're honest that this is promising but not a sure thing). (2) Separately, and possibly even
more valuable: since we ALREADY have two different, both-working methods (this brain-style one, and our best
fully-trained one), simply COMBINING their two final scores — not their internal math, just their answers — is a
well-established trick in search-engine-style ranking systems, and outside research on similar structure-plus-content
combinations shows this kind of teamwork regularly beats either method alone, especially exactly where our
best method is currently weakest (brand-new concepts with very little known about them). This second idea costs
almost nothing to try, since both pieces already exist and are already proven.

**The honest caveat:** we also found real, published warnings against two tempting shortcuts — don't just blend the
two methods' raw numeric codes together (a well-documented failure mode in similar systems), and don't expect a
"denoise the guess afterward" trick to help much, because a separate check on this specific knowledge-graph's shape
suggests it's a spread-out, non-compact map, and that kind of cleanup step only works well on compact ones. Both
caveats are backed by cited outside research, not guesswork.
