# Research drill: composition-operator + rule-structure theories beyond the additive mean-bundle

**Filed by:** research sub-agent. **Trigger:** mission directive — our composer (`ANCHOR_COMPOSE`, additive mean-bundle,
`hdlab/additive_map.py`-bound per `notes/research_additive_map_builder_integration_endgame_2026-07-13.md`) already sits
at ~93.7% of its own oracle (held-out MRR 0.1282 / oracle 0.1368). This drill scours BEYOND it for a fundamentally
different composition-operator or rule-structure family — path-based reasoning, rule mining/AMIE, tensor factorization
(RESCAL/TuckER/ComplEx), and analogy/structure-mapping (Gentner) — that could raise inductive (unseen-entity)
generalization. Does NOT re-cover capacity or grounding (already scoured — see `notes/relational_capability_track_
record_scour_2026-07-10.md`, `notes/project_grounding_needs_active_intervention...md`). Extends and is complementary
to (not overlapping with) `notes/research_inductive_map_builder_best_in_class_magnitude_levers_2026-07-13.md` (SIC-peel,
hard-neg — those are magnitude LEVERS on the existing operator; this drill is about alternative/complementary OPERATOR
FAMILIES) and `notes/research_substrate_realizable_frontier_levers_inductive_map_builder_2026-07-13.md` (reciprocal-
direction bundling, cold/d1 diagnostic — read and reused below, not re-derived).

Method: 4 parallel Sonnet lit-scans (brain relational-inference mechanisms; path-based reasoning + rule mining;
tensor-factorization operators; analogy/structure-mapping), generic public math/CS/neuro terms only, no substrate-
specific framing sent off-platform. All 4 returned complete syntheses with citations.

---

## HEADLINE

1. **Brain-first finding: the Tolman-Eichenbaum Machine (Whittington/Behrens et al., Cell 2020) is the closest
   biological analog of our EXISTING mechanism, not a reason to replace it.** TEM factorizes cognition into an
   item-INDEPENDENT structural/relational code (medial entorhinal cortex, grid-like) that is reused across different
   sets of sensory items, bound combinatorially to item-specific codes (hippocampus/lateral entorhinal cortex). This
   is structurally identical to our design: gradient-derived low-dim coordinates `X` (structure) + relation
   displacement vectors `D` (structure) bound to specific entities via addition, generalizing to any new item sharing
   the same relational graph. The brain evidence is a strong VALIDATION of the additive/geometric operator family we
   already committed to, not a signal to pivot away from it — the correct reading of "go beyond the additive
   composer" is "layer better SELECTION/GATING of what enters the bundle," not "replace the bundle's arithmetic."
2. **The single most promising NEW, testable, glass-box lever found: AMIE/AnyBURL-style logical rule mining, used
   as a GATING/FILTER layer on top of the existing additive compose op — not as a replacement for it.** Rules of the
   form `R1(A,B) & R2(B,C) => R3(A,C)` generalize to unseen entities BY CONSTRUCTION (they quantify over variables,
   not specific entity embeddings) and are MORE exactly-inspectable than our current mean-bundle (AMIE's PCA-confidence
   is an exact, auditable count — support / bindings — not an approximate score). Standalone, pure rule-mining
   under-performs neural path-aggregation by ~10-20 MRR points on the standard GraIL inductive benchmarks (full-ranking
   protocol) — so rule-mining alone would be a REGRESSION versus our current number. But the field's own strongest
   quantified result (arXiv:2308.07942, "Inductive KG Completion with GNNs and Rules: An Analysis") is that a
   **rule-RESTRICTED path-aggregator ("NBFNet+NBFNet," gated to only the small subgraph a mined rule set licenses)
   simultaneously beats vanilla (unrestricted) NBFNet's accuracy AND stays rule-legible** — i.e., in the one place the
   literature directly measured "rules as a gate on a stronger base method" rather than "rules vs. neural method as
   rivals," gating WINS on both axes. This is directly portable to our situation: mine rules over the known 85% of
   CSKG, use rule PCA-confidence to select/weight WHICH 2-hop compose terms are trustworthy enough to add to a
   held-out entity's bundle — addressing the SNR-vs-dimension crosstalk risk the prior magnitude-levers note flagged
   for naive multi-hop expansion, using a symbolic (zero-dimension-cost) filter instead of blind inclusion.
3. **Tensor factorization (RESCAL/TuckER/ComplEx) is a CONFIRMATORY negative, not a lever — and the confirmation is
   unusually clean.** A closed-form out-of-KB (OOKB) result (Dai et al. 2021, RepL4NLP, arXiv:2009.12765) proves
   ALGEBRAICALLY that training-free closed-form induction for a held-out entity requires an INVERTIBLE relation
   operator (vector addition / rotation — exactly our additive family): given one known neighbor edge, `e_new = t - r`
   (or `t ∘ r⁻¹` for rotation) has a unique solution. Full-matrix bilinear operators (RESCAL) are in general
   non-invertible/non-square, so the same construction yields an indeterminate or infinite-solution system — NO
   closed-form, zero-training induction path exists for RESCAL/TuckER-class operators. Bilinear operators (ComplEx/
   DistMult) DO beat additive TransE on held-out-entity benchmarks (OWE, AAAI 2019: ComplEx-OWE 35.2 MRR vs
   TransE-OWE 28.7 MRR on FB15k-237), but ONLY when paired with a LEARNED aggregator/text-encoder that does the actual
   generalization work for the new entity — which is precisely the zero-training/glass-box constraint we protect.
   **Read: our additive-operator choice is the literature-endorsed correct family for a zero-training, closed-form
   construction; switching to a bilinear operator would require abandoning the zero-training constraint to see any
   benefit.** Deprioritize as an operator swap.
4. **Path-based neural reasoning (NBFNet/GraIL/RED-GNN/A\*Net/ULTRA) is the strongest RAW-ACCURACY family in the
   literature but fails our glass-box constraint standalone**, and the field agrees: genuine per-path explanations
   require bolting on a separate, approximate, post-hoc explainer (PaGE-Link, Power-Link, eXpath) that "does not
   extend to embedding-based approaches" — the interpretability is not native to the model. The GENERALIZED
   BELLMAN-FORD algorithmic idea (implicitly sum over exponentially many paths via dynamic programming rather than
   enumerating them) is a useful ALGORITHMIC PATTERN worth borrowing in a fully-symbolic form — which, worked out
   concretely, collapses back into option 2 (rule-weighted bounded-depth path aggregation, the classic Path Ranking
   Algorithm lineage, is exactly this pattern minus the opaque GNN).
5. **Analogy/structure-mapping (SME, LISA/DORA, VSA role-filler binding + cleanup memory) is confirmatory, not a new
   mechanism to build.** The most practically-adaptable line found — VSA binding+cleanup (Emruli & Sandin: "bundle a
   held-out entity's known edges into a query vector, no separate learned embedding needed, one-shot") — is, on
   inspection, already what `build_anchor_compose_codes` does (mean-bundle of `X[h]+D[r]` terms IS a bundle of
   known-edge bindings). SME itself is fully inspectable and logically the right machinery for judging structural
   consistency of a candidate fact, but has no published KG-scale (thousands-of-entities) demonstration and is
   `O(N^3)` worst-case — not a cheap near-term lever. A genuinely important CAUTION surfaced here, independent of any
   lever: the word2vec-arithmetic critique (Linzen 2016; Chen/Peterson/Griffiths 2017) shows pure vector-offset
   composition captures pairwise similarity but is NOT sufficient for dependencies among 3+ items — i.e., single-shot
   mean-bundling may quietly degrade on relational chains that are truly 3-way-dependent (not just a bag of pairwise
   edges), a risk to keep in mind if/when multi-hop composition is pursued further.

---

## Cheap decisive test

**Rule-gated 2-hop augmentation of the held-out entity bundle, tested on the already-measured `d1`/`d2_3` degree
buckets (no new held-out split needed — reuse `data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json`'s
`anchor_mrr_by_support_degree` harness):**

1. Mine length<=2 Horn rules (AMIE-lite: enumerate `R1(A,B) & R2(B,C) => R3(A,C)` candidate patterns) over the KNOWN
   85% of CSKG-12core (already on disk), with exact PCA-confidence (support / body-groundings, no training).
2. For each `d1`/`d2_3` held-out entity, in addition to the current 1-hop compose terms, add mean-bundle terms
   `X[h2] + D[r1] + D[r2]` for 2-hop chains that instantiate a mined rule with PCA-confidence >= threshold (try 0.3
   and 0.5).
3. Re-score filtered MRR on the identical held-out split/query set already used for the scaling-ladder cell. Compare
   against the existing `d1`/`d2_3` anchor_mrr (0.0593 / 0.0789) and against `d8plus` (0.1277, must NOT regress —
   crosstalk check).
4. Cost: symbolic rule-mining over a known subgraph is CPU-cheap (no GPU, no gradient training) — well within
   remote_cpu budget; reuses 100% of existing scoring/eval code.

## Falsifiable predictions

**HARD-PASS thresholds:**
- `d1` anchor_mrr improves by >=20% relative (0.0593 -> >=0.071) AND `d2_3` anchor_mrr improves by >=15% relative
  (0.0789 -> >=0.091), with `d8plus` anchor_mrr NOT regressing by more than 2% relative (stays >=0.1251) — confirms
  the rule gate adds real signal to degree-starved entities without polluting well-served ones via crosstalk.
- Mined-rule PCA-confidence distribution over CSKG-12core shows a genuine bimodal split (a meaningful fraction, e.g.
  >=15% of candidate 2-hop patterns, clears confidence >=0.5) — confirms there is enough clean logical structure in
  a commonsense KG for the gate to be selective rather than admitting everything indiscriminately.

**HARD-FAIL thresholds:**
- Mined rule PCA-confidence is uniformly low (>80% of candidate 2-hop patterns fall below 0.2 confidence) — would
  confirm the standing finding that CSKG's relation vocabulary (dominated by generic SYNONYM/IS_A taxonomy edges per
  `notes/project_substrate_has_zero_grounded_measured_attribute_data_pure_symbol_graph_2026-07-10.md`) is too
  semantically flat for transitive-rule patterns to discriminate reliable from spurious 2-hop chains — the gate would
  degenerate to "admit almost everything" (no better than naive 2-hop expansion) or "admit almost nothing" (no lift).
- `d1`/`d2_3` improve but `d8plus` regresses by more than 2% relative — confirms the SNR-vs-dimension crosstalk risk
  the prior magnitude-levers note predicted for any bundle-size-increasing lever at fixed `n_dim`; would mean the
  rule gate needs to be paired with a dimension increase (re-opening the `n_dim` cost/O(n_dim^2) tradeoff) rather than
  being a free win.
- `cold`-bucket entities (0 usable support edges by construction, per the on-disk diagnostic) remain untouched
  (anchor_mrr stays ~0.000041) — this is EXPECTED, not a failure of this lever specifically: rules, like the additive
  bundle, need at least one visible edge to instantiate a pattern; a genuinely zero-edge entity is an oracle-degenerate
  test-construction artifact, not a mechanism gap (already flagged in the prior drill — restated here so a null result
  on `cold` is not mistakenly read as this lever's failure).

---

## Cross-thread synthesis with prior entries

- **Confirms, does not contradict,** `notes/research_additive_map_builder_integration_endgame_2026-07-13.md`'s choice
  of additive/TransE-style geometry: the OOKB closed-form-invertibility result (Dai et al. 2021) is an independent,
  purely mathematical confirmation that additive/rotational operators are the uniquely correct family for a
  zero-training, glass-box construction — bilinear alternatives (RESCAL/TuckER/ComplEx) are disqualified not by
  performance but by CONSTRUCTION (non-invertible => no closed-form solve => would require abandoning zero-training).
- **Directly extends** `notes/research_substrate_realizable_frontier_levers_inductive_map_builder_2026-07-13.md`'s
  Lever 1 (reciprocal-direction bundling) and its `cold`/`d1` diagnostic table: this drill's rule-gate proposal is a
  DIFFERENT, complementary lever targeting the same `d1`/`d2_3` degree-starved populations, via a different mechanism
  (symbolic gate vs. reciprocal-relation inclusion) — the two are stackable, not competing, and both should be tested
  before assuming the degree-starved floor is intractable.
- **Extends** `notes/research_inductive_map_builder_best_in_class_magnitude_levers_2026-07-13.md`'s Lever on multi-hop
  expansion: that note flagged multi-hop expansion as high-gain-but-SNR-costly (must pair with `n_dim` increase or
  cannibalize itself via crosstalk). This drill's rule-gate is a candidate way to capture SOME of that multi-hop gain
  cheaply (only admit rule-licensed, high-confidence 2-hop terms) without paying the full blind-inclusion crosstalk
  cost — a concrete mitigation for exactly the risk that note raised, not previously proposed.
- **Directly relates to, and must be read alongside,** `notes/research_drill_neurosymbolic_logical_inference_theories_
  2026-07-13.md` (filed the same day, independently scoped to the RULE/LOGIC family). That drill already established:
  (a) rule/logic frameworks generically escape the per-entity-trained-embedding requirement; (b) the field consensus
  that you get at most 2 of 3 of {inductive, glass-box, cheap-at-scale}; (c) this substrate has ALREADY proven rule
  APPLICATION at HARD_PASS (PP-196 forward-chaining, PP-252 defeasible NAF) but never rule INDUCTION; (d) its own top
  candidate is a STANDALONE test of "induce rule confidence weights from KG statistics, check held-out-entity
  generalization via forward-chaining" (P_deflated=0.22 HARD-PASS / 0.45 headline). **This drill's proposal is
  different and complementary, not a restatement:** rather than testing rule-induction+forward-chaining as a
  standalone mechanism, it proposes using mined rule confidence purely as a GATE deciding which 2-hop terms enter the
  ALREADY-VET-CONFIRMED additive-bundle compose op (`ANCHOR_COMPOSE`) — i.e., rules as a filter on top of a proven
  geometric mechanism, not rules as the primary inference mechanism being tested in isolation. The two tests are
  cheap to run together (same mined-rule artifact feeds both); if the standalone neurosymbolic drill's forward-
  chaining test HARD-FAILs (rules alone can't carry accuracy), the rule-GATE framing here may still HARD-PASS,
  because it only needs the rules to correctly discriminate trustworthy from spurious 2-hop paths, not to score
  facts on their own — a substantially lower bar.
- **New, not previously logged:** the brain-grounding link to TEM (Whittington/Behrens, Cell 2020) as the direct
  biological analog of the "structure-code (D) + item-code (X), bound additively" design. Worth citing going forward
  as the standing brain-first justification for the additive-map architecture (parallels the existing brain-beats
  frequency drill `notes/research_brain_beats_frequency_relational_inference_deep_drill_2026-07-10.md` but at the
  systems/TEM level rather than the oscillation level).

---

## Substrate-product implications

- **Do not swap the composition operator.** The literature independently confirms (via a clean piece of linear
  algebra, not just empirics) that our additive family is the right choice for the zero-training/glass-box contract
  we already committed to. Any switch to a bilinear/multiplicative operator would require adding a learned aggregator
  for held-out entities, which trades away the exact property (zero-training induction) that makes the current
  mechanism auditable and cheap.
- **Add a rule-mining GATE, not a rule-mining REPLACEMENT.** The actionable new capability is a small, symbolic,
  CPU-only AMIE-lite rule miner over the known 85% of the graph, whose OUTPUT (a confidence-scored set of 2-hop
  relation-composition patterns) is used purely as a FILTER deciding which additional compose terms are trustworthy
  enough to add to a held-out entity's existing mean-bundle — this is a natively glass-box addition (exact support/
  confidence counts, human-auditable, zero gradient training) that plugs into the ALREADY-EXISTING `hdlab/
  additive_map.py::AdditiveKGMap.compose_entity` surface without touching the underlying arithmetic.
- **This targets the specific weak population already measured on disk** (`d1`, `d2_3` — 15% and 64% of oracle
  headroom used respectively) rather than a generic "improve everything" hope, and is stackable with the
  already-shipping SIC-peel/hard-neg levers and the not-yet-landed reciprocal-bundling lever.
- **Cost is low and does not compete with GPU budget:** rule mining over a known subgraph is exact symbolic counting,
  remote_cpu-tractable, no training — fits the "no local smokes, route to remote" discipline without needing GPU
  time, unlike most magnitude-lever candidates.

---

## Citations (verified count: 46 distinct URLs/arXiv IDs across the 4 lit-scans, spot-checked for topical relevance
by the synthesizing agent; not independently re-fetched by this note's author — treat as sub-agent-reported, standard
lit-scan calibration applies)

Key ones referenced above: Whittington/Muller/Behrens et al. "Tolman-Eichenbaum Machine," Cell 2020; Behrens et al.
"What Is a Cognitive Map?," Neuron 2018; Galárraga et al. AMIE, CIKM 2013 + AMIE3; Meilicke et al. AnyBURL,
arXiv:2004.04412; unnamed authors, "Inductive Knowledge Graph Completion with GNNs and Rules: An Analysis,"
arXiv:2308.07942; Zhu et al. NBFNet, arXiv:2106.06935; Teru et al. GraIL, arXiv:1911.06962; Nickel et al. RESCAL
review, arXiv:1503.00759; Balažević et al. TuckER, ACL D19-1522; Dai et al. OOKB closed-form, arXiv:2009.12765; Shah
et al. OWE, arXiv:1906.08382; Hamaguchi et al. OOKB-GNN, arXiv:1706.05674; Falkenhainer/Forbus/Gentner SME, AAAI 1986;
Hummel & Holyoak LISA, 2003; Doumas/Hummel/Sider DORA, 2008; Emruli & Sandin VSA+SDM analogy; Linzen 2016
arXiv:1606.07736; Chen/Peterson/Griffiths 2017 arXiv:1705.04416.

---

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: novel-synthesis P capped at 0.50; deflated further 0.15-0.25 for
uncharted-combination risk (rule-gate-on-commonsense-KG has no direct published precedent — the closest analog,
rule-restricted NBFNet, was tested on curated ontologies WN18RR/FB15k-237/NELL-995, not a noisy commonsense graph).

**P_deflated (rule-gate lever helps d1/d2_3 by the HARD-PASS margins above, on this substrate, at this scale): 0.35.**
The mechanistic case is strong (construction-generalizing, orthogonal to existing levers, zero training cost, direct
field precedent for "rules gating a stronger base method wins both axes") but CSKG's known taxonomy-heavy, semantically
flat relation vocabulary (per the zero-grounded-data finding) is a real, specific reason confidence in rule
discriminability should not be higher than this on a commonsense graph specifically.
