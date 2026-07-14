# Drill: neuro-symbolic / logical-inference theories for inductive KG reasoning (glass-box)

**Filed:** 2026-07-13 by research (Sonnet, 3 parallel Sonnet lit-scans: brain/rule-representation,
differentiable rule induction, differentiable/probabilistic logic + path-ranking).
**Trigger:** director-directed drill on whether learned RULES (which apply to any entity by
construction) can sidestep the per-entity-code capacity wall that has closed inductive relational
inference on this substrate three times over (2026-07-09/10, confound-free FULL cells).
**Explicitly out of scope (already covered):** capacity-theory math (Plate bound, free-probability,
spin-glass), grounding/referent-acquisition drills. This drill is scoped to the RULE/LOGIC
mechanism family specifically.
**Query-privacy:** all external searches used generic public terms (paper titles, author names,
math/CS terminology) — no substrate-novel mechanism names or configs went off-platform.

## HEADLINE

Every rule/logic framework surveyed genuinely escapes the *per-entity trained embedding*
requirement (rules are relation-only Horn clauses; grounding is a symbolic join over actual edges,
not a similarity lookup in a learned vector space) — but the literature is unanimous that you can
have at most **two of three** properties {inductive, glass-box, cheap-at-scale}, and on the one
benchmark family that measures inductive (unseen-entity) accuracy directly (GraIL's inductive
splits), the best rule-only methods (RuleN, AnyBURL-family) are competitive with but not clearly
better than opaque GNN methods (GraIL, NBFNet) — sometimes losing, sometimes winning depending on
split difficulty. The most important substrate-specific finding is a **decoupling**: this
program has *already proven* the "apply a rule to new entities via forward-chaining" half of
this mechanism at HARD_PASS (PP-196 STRIPS forward-chaining, perfect recall; PP-252 defeasible
NAF, 100% accuracy, n=400) — what has never been tested is the "*induce* the rule's confidence
weights from ingested KG data and check whether the induced rule generalizes to held-out
entities" half, which is a structurally different and much cheaper test than anything in the
2026-07-09/10 negative run (it needs zero VSA training — pure graph statistics — for the rule
side, and reuses proven substrate machinery for the apply side).

## Brain-first: what does rule-based generalization actually require, mechanistically?

Four converging PFC/hippocampal literatures (Wallis, Anderson & Miller 2001 *Nature* single-unit
PFC rule cells; Kriete, Noelle, Cohen & O'Reilly 2013 *PNAS* PBWM indirection/pointer gating;
Smolensky 1990 tensor-product + Webb, Sinha & Cohen 2021 ICLR "Emergent Symbols through Binding"
key-value indirection tested on genuinely novel fillers; Whittington et al. 2020 *Cell* TEM
structure/content factorization) all describe the SAME underlying move: split the code into (a) a
reusable, entity-invariant RULE/STRUCTURE representation, and (b) a cheap, generically-computed
CONTENT slot bound into the rule via a content-agnostic operation (gating, pointer indirection,
outer product, conjunction) — not zero entity representation, *amortized* entity representation.
The Fodor & Pylyshyn (1988) systematicity debate remains explicitly contested in 2025-26 follow-up
surveys (arXiv 2506.01820 / 2606.14512): generic connectionist architectures still do not exhibit
robust systematicity without an explicit compositional/binding bias baked in.

**Implication for this drill:** biology does NOT license "rules eliminate the need for
entity-specific computation." It licenses "rules eliminate the need for a *trained, per-entity*
vector" — the entity's role in the rule is resolved by a cheap, untrained, generic operation
(symbolic pattern-match / cosine-classify-against-a-small-prototype-set), which is exactly what a
Horn-clause grounding step over an actual KG edge list already is. This is consistent with, not a
refutation of, this drill's product framing below.

## Field survey (3-way lit-scan)

### A. Differentiable rule induction (entity-independent Horn clauses)

| Method | Inspectable? | Inductive evidence | Compute |
|---|---|---|---|
| Neural-LP (Yang, Yang & Cohen, NeurIPS 2017) | Yes — attention reads out as weighted Horn clauses | Entity-independent by construction; on GraIL inductive splits, AUC-PR 74.4/68.9/46.2/67.1 (v1-v4) — underperforms RuleN and GraIL | Sparse TensorLog matmuls, ~15-40k entity KBs, chain length capped (~3 hops) |
| DRUM (Sadeghian et al., NeurIPS 2019) | Yes — fixes Neural-LP's soundness bug (zero confidence to invalid rule bodies) | Same benchmark family, similar numbers to Neural-LP | Same compute class as Neural-LP |
| RNNLogic (Qu et al., ICLR 2021) | Yes — explicit weighted Horn clauses via EM | Inductive-by-construction, not separately proven on unseen-entity splits in the primary paper | GPU-trained but moderate |
| AnyBURL / SAFRAN (Meilicke et al. 2019/2020) | Yes — fully symbolic, human-readable | Inductive-by-construction; SAFRAN reports SOTA among interpretable methods on FB15k-237/WN18RR | **Fastest of all methods surveyed** — mines rules for a full standard KB in CPU-minutes |
| RuleN (cited via GraIL benchmark) | Yes | On GraIL inductive splits: **beats Neural-LP/DRUM outright** (80.9/78.2/53.4/71.6 AUC-PR); competitive with or beats GraIL on 3/4 FB15k-237 splits | Symbolic rule mining, cheap |
| dNL-ILP / ∂ILP (Evans & Grefenstette 2018) / Neural Theorem Provers (Rocktäschel & Riedel 2017) | Yes, most expressive rule language (recursion, predicate invention) | Toy/synthetic ILP benchmarks only — no evidence of real 10k+-entity KG runs | **Confirmed exponential/combinatorial blowup** ("quickly becomes infeasible even for small KBs" — direct quote from field; NaNTP/top-k-unification exists specifically to patch this) |
| GraIL (Teru, Denis & Hamilton, ICML 2020) / NBFNet (Zhu et al. 2021) | **No** — opaque GNN message-passing, not IF-THEN rules | Best raw inductive AUC-PR of everything surveyed (GraIL beats all rule baselines on v1-v3; NBFNet +18-22% over GraIL) | GPU-trained GNN, scales to real benchmarks but NOT glass-box — excluded by this drill's constraint, kept as the numeric bar rule-methods must clear to be worth building |

### B. Differentiable/probabilistic logic + path-ranking

| Method | Inspectable? | Inductive evidence | Compute |
|---|---|---|---|
| Logic Tensor Networks (Badreddine et al., *AIJ* 2022) | Split: formula layer readable, predicate grounding is an opaque neural net | No inductive-KG-completion-at-scale evidence found; small ontology/image tasks only | Feasible small-to-moderate scale; grounding cost grows with #entities x #relations |
| DeepProbLog (Manhaeve et al., NeurIPS 2018) | Split: ProbLog program glass-box, neural predicates black-box | No KG-completion-scale unseen-entity benchmarks found | **Confirmed #P-hard / exponential exact inference** (Manhaeve et al. KR 2021; BDD/sd-DNNF blowup); successors (DeepStochLog, A-NeSI, 2025 "Scaling Neurosymbolic Programming") exist purely to buy back tractability via approximation |
| Markov Logic Networks (Richardson & Domingos 2006) | Yes, most glass-box of all 5 | No new-entity KG-completion evidence found | **Confirmed exponential grounding** in general (clique blowup with high-arity predicates); RDBMS-scale infra (Tuffy) needed to mitigate |
| Probabilistic Soft Logic (Bach et al., JMLR 2017) | Yes | Applied to KG completion, but literature scanned is mostly transductive | Polynomial/convex (ADMM on hinge-loss MRF) — genuinely lightweight, laptop-feasible |
| Path Ranking Algorithm / SFE (Lao & Cohen 2010; Gardner & Mitchell, EMNLP 2015) | Yes — each feature is a literal typed path, weights directly readable | **Structurally inductive by construction** (paths defined over relation-types, not per-entity lookups) — this is PRA's stated core advantage over TransE-style methods | Known failure mode: path/feature-count explosion; SFE cuts PRA runtime ~10x while *improving* accuracy (MAP .432→.528); no million-entity deployment found (A*Net, 2022, explicitly claims to be first path-method to scale to million-entity graphs, implying PRA/SFE themselves don't) |

**Cross-cutting field verdict (converged across all 3 lit-scans independently):** no surveyed
method delivers {inductive, glass-box, cheap-at-scale} simultaneously — pick at most 2. PRA/SFE
and AnyBURL/RuleN come closest to (inductive + glass-box) at the price of scale headroom that has
not been proven past ~40k entities in the literature; PSL buys (glass-box + cheap) at the price of
unproven inductive claims; the exponential-inference family (MLN, DeepProbLog, ∂ILP/dNL/NTP) is
**flagged heavyweight/impractical** for a small self-contained system — confirmed, not suspected,
by the field's own follow-up literature (NaNTP, DeepStochLog, Tuffy all exist specifically because
the base method doesn't scale).

## Ranked methods (promise x glass-box x cheap-testability)

1. **AnyBURL/RuleN-style pure statistical rule mining -> forward-chaining application.** Best fit.
   Fully symbolic, CPU-minutes to mine, competitive-to-SOTA among interpretable methods on
   standard inductive benchmarks, and — the substrate-specific reason this ranks #1 — the
   *application* half is already CG on this substrate (PP-196, PP-252). Only the *induction* half
   (learning rule confidences from data and testing generalization to held-out entities) is
   untested.
2. **DRUM / Neural-LP** (differentiable rule confidence). Glass-box, inductive-by-construction,
   but literature shows weaker inductive numbers than RuleN/AnyBURL and needs GPU gradient
   training for a smaller apparent payoff — moderate cost, lower ceiling on current evidence.
3. **PRA/SFE** (path-ranking). Glass-box + inductive, genuinely cheap relative to GNN training, but
   path-explosion is a real, literature-documented failure mode; good complementary feature source,
   not preferred as the primary mechanism for a first test.
4. **PSL.** Glass-box + genuinely polynomial/convex compute (laptop-feasible), but no direct
   evidence found that its inductive-KG claim has ever been tested at unseen-entity granularity —
   medium promise, needs its own verification pass before betting on it.
5. **∂ILP / dNL-ILP / original Neural Theorem Provers.** FLAG: heavyweight/impractical. Confirmed
   exponential/combinatorial blowup; doesn't scale past toy KBs (tens of predicates) without a
   separate approximate-inference research line (NaNTP). Do not build.
6. **DeepProbLog.** FLAG: heavyweight/impractical. Confirmed #P-hard exact inference; only viable
   via approximate successors that are themselves separate, less-mature systems. Do not build.
7. **MLN.** FLAG: heavyweight/impractical for a self-contained system. Confirmed exponential
   grounding without RDBMS-scale infrastructure. Do not build.
8. **LTN.** FLAG: research-stage, thin inductive-KG evidence, predicate-level black box undercuts
   the glass-box premise this drill is testing for. Deprioritize.
9. **GraIL / NBFNet (GNN-based inductive methods).** Best raw numbers of everything surveyed but
   explicitly excluded by the glass-box constraint — kept only as the numeric bar that a rule-based
   mechanism should be honestly compared against, not as a build target.

## The most promising glass-box rule-inference approach to test

**Statistical Horn-rule mining (AnyBURL/RuleN-style path-counting over the ingested KG edge list,
plain graph statistics, zero VSA training) -> apply via the substrate's already-proven
forward-chaining primitive, with EXACT (oracle) adjacency lookup for the grounding step.**

Why the oracle-lookup caveat matters and is not cheating: bucket D of the relational track-record
scour (`notes/relational_capability_track_record_scour_2026-07-10.md`) already established that
*learned/typed/substrate-native graph routing* is a separate, independently-failing problem
(router SNR ~ sqrt(N/M) degrades under load; every non-oracle router collapses to the
naive-centroid floor). Using exact adjacency-list lookup for rule-grounding in this test
deliberately holds that already-answered question constant, so a pass or fail here is attributable
to the RULE-INDUCTION mechanism itself, not re-litigating the routing wall. If this test is
promising, a follow-up drill on whether rule-grounding can be made substrate-native (VSA lookup
instead of a Python dict) is the natural next step — but that is a second, separable bet.

## Does it sidestep the capacity wall?

**Partially, and in a specific, falsifiable way.** It genuinely sidesteps the *per-entity trained
embedding* piece of the wall: a Horn rule like `relation(X,Z) :- r1(X,Y), r2(Y,Z)` has zero free
parameters indexed by entity identity — confidence weights are indexed by *relation*, not by
entity, so the K/N-style superposition-capacity ceiling that closed the SR-code, TransE, and
structure-aware-encoder attempts (all three: `grounding_learned_sr_heldout_reasoning_v1`,
`inductive_relational_transfer_to_NOVEL_entities_moves_OFF_ZERO`,
`encoder_structure_aware_sharpness_v1`) simply does not apply to the rule-confidence parameters
themselves. It does **not** sidestep a second, independent risk this program has already flagged
(the 2026-07-05 frontier drill, `notes/research_frontier_drill_inductive_relational_transfer_unseen_entities_2026-07-05.md`):
if the KG's short-text/thin-relation content genuinely lacks the predictive structure needed to
distinguish one held-out entity's correct answer from another's at 2-3-hop rule length — the field
number here (GraIL v1 AUC-PR as low as 44-53% for the hardest inductive splits even for the best
methods) shows this is a real, not hypothetical, failure mode even for state-of-the-art inductive
methods on richer benchmarks than ConceptNet. So a rule-mining result could plateau for the SAME
underlying reason (content insufficiency) via a structurally different, cleaner mechanism — which
would be a stronger, more diagnostic negative than the current wall (it would rule out "it's the
embedding capacity" as the sole explanation and confirm "it's the knowledge itself").

## Cheap decisive test (single next experiment, CPU-only, no GPU needed)

Mine confidence-weighted Horn rules of length <=2 (AnyBURL/PRA-style path-counting: for each
relation R, count how often a length-1 or length-2 path pattern between X and Z co-occurs with an
R(X,Z) edge in the TRAIN partition; confidence = co-occurrence count / path-pattern count) over the
**identical graph and identical inductive/held-out entity split** already used in
`grounding_learned_sr_heldout_reasoning_v1` (3-seed FULL cell, HF verdict, Δ0.011 vs random codes).
Apply the mined rules via exact adjacency-dict lookup (no VSA) to score candidate objects for each
held-out (never-seen-in-train) subject; compute reach@2 exactly as that cell defines it. Run the
SAME real-vs-shuffled-rule-set control the cell already uses for codes (shuffle which rule-body
pattern maps to which relation, keep counts identical) as the discriminator-fires positive/negative
control.

**Pre-registered HARD-PASS:** `reach@2(real rules, held-out inductive entities) -
reach@2(shuffled rules, same entities) >= 0.05`, matching the margin used to judge the SR-code
cell's negative, AND the synthetic/no-signal control fires (shuffled-rule reach@2 collapses toward
the memoryless floor of 0.017 measured in the same prior cell) so the result is not itself
vacuous-control noise.

**Pre-registered HARD-FAIL:** real-rule reach@2 - shuffled-rule reach@2 <= 0.02 while the control
fires validly — the strong, clean negative: pure symbolic rule induction, with zero embedding
capacity involved anywhere, still cannot beat a memoryless/shuffled baseline on held-out entities.
Given the PROVEN CONSTRAINT already on record (untrained/random codebook scores exactly 0.0000;
some trained structure is necessary), this specific HARD-FAIL would be the cleanest evidence yet
that the bottleneck is the KG's content/relation richness itself (thin ConceptNet-style short-text
relations), not any property of embeddings, superposition capacity, or VSA algebra — because this
test removes ALL of those from the causal chain.

**MIDDLE_BAND:** control fires, real-rule margin lands strictly between 0.02 and 0.05, or passes on
some relations but not others — motivates sweeping rule length (2 vs 3 hops) or switching from
raw path-counting to a PSL-style convex-weighted variant before a mechanism pivot, not abandoning
the family.

## Cross-thread synthesis

- **PP-196** (`strips_planning_khop_cpu_v1`, HARD_PASS, recall=1.000, cycle 198) and **PP-252**
  (`lap1_defeasible_cpu_v1`, HARD_PASS, defeasible_acc=1.000 n=400, cycle 213) jointly establish
  that the *application* half of a symbolic rule/logic pipeline (forward-chaining k-hop
  reachability; non-monotonic default-with-exception reasoning via retrieval precedence) is
  already proven CG on this substrate. This drill's contribution is separating that from the
  *induction* half (learning which rules to trust from data, tested for held-out-entity
  generalization), which has never been run — a genuinely new axis, not a re-test of PP-196/PP-252.
- **PP-33e** (`proposed`: "symbolic primitive composition (rule-fire + disjunction + forward-chain
  + backward 4-way battery)") is a pre-registered but not-yet-run row that overlaps this drill's
  application half; worth folding the rule-INDUCTION test above into the same program rather than
  treating them as separate initiatives.
- **The relational track-record scour** (`notes/relational_capability_track_record_scour_2026-07-10.md`,
  bucket E, "THE WALLS") is the load-bearing prior result this drill responds to: held-out
  inductive inference fails identically across three independent confound-free mechanisms (learned
  SR codes, global additive TransE, structure-aware encoder training) — all three are
  EMBEDDING-family mechanisms. This drill proposes the first non-embedding mechanism class against
  the same wall.
- **PP-321/PP-327** (structural alignment / Slipnet relation-type-weighted spreading activation,
  both positive, +14pp / +15.8pp over naive-geometry baselines) are a different task shape
  (cross-domain structural correspondence, not subject->object retrieval) but are additional
  evidence that relation-TYPE-aware mechanisms beat naive-geometry baselines in this program's own
  data — mild convergent support for rule/relation-type-conditioned methods generally, not directly
  transferable numbers.
- **The 2026-07-05 frontier drill** (TEM structural/content binding, MM/untested) and this drill are
  complementary, not competing: TEM-structural-binding is a CONTENT-side fix (cluster subjects by
  content into reusable types); rule-mining is a STRUCTURE-side fix (learn which path patterns
  predict which relations, entity-content-agnostic). They could be combined in a follow-up (use
  mined rules as a coarse candidate filter, then TEM-style content clustering to disambiguate among
  rule-permitted candidates) if both show partial signal independently — flagged, not proposed as
  a first cell.

## Substrate-product implications

If HARD-PASS: a second, structurally distinct, genuinely inspectable inductive-reasoning primitive
("the substrate can tell you WHY it predicted this new fact — here is the 2-hop rule with its
learned confidence" — a concrete glass-box advantage over both black-box embedding methods and
LLM-based KG completion, neither of which can produce a literal auditable rule) — buildable at
near-zero marginal training cost (CPU rule-mining) that composes with the already-proven
forward-chaining application layer. If HARD-FAIL with a validated control: a strong, clean,
mechanism-agnostic negative that narrows the honest product claim to "this KG's relation content is
too thin for ANY structure-only (embedding OR rule) mechanism to infer held-out facts; richer
per-entity content or explicit grounding is required" — which sharpens (not defeats) the standing
"ingest more knowledge, not richer structure" conclusion from the 07-05 frontier drill by ruling
out an entire additional mechanism class as the culprit.

## Falsifiable predictions (calibration-penalized; novel-synthesis cap 0.50 applied)

- P(mined-rule reach@2 clears HARD-PASS margin >=0.05 over shuffled-rule control, valid control) =
  **0.22** (naive estimate ~0.42 based on RuleN/AnyBURL's competitive-to-SOTA field performance on
  standard inductive benchmarks; deflated -0.20 for: (a) this exact held-out-entity task on this
  exact ConceptNet-derived graph has failed identically 3/3 times already for other mechanism
  classes, raising the prior that the limitation is content-level not mechanism-level; (b) no field
  precedent tests rule-mining specifically against a Δ0.011-style memorized-search floor with this
  particular metric, so the numeric transfer from GraIL-style AUC-PR benchmarks is uncertain).
- P(HARD-FAIL: margin <=0.02, control valid) = **0.38** (the single most likely outcome given the
  3/3 prior negative base rate on this exact task, tempered downward from a naive ~0.50 because
  rule-mining is a genuinely different, content-source-orthogonal mechanism, not another
  embedding variant, so full independence of failure is not assured).
- P(MIDDLE_BAND: margin in (0.02, 0.05), or relation-dependent partial signal) = **0.30**.
- P(control itself fails to fire, i.e. shuffled-rule reach@2 does not collapse toward the
  memoryless floor — test-design risk, not a science result) = **0.10** (guarded against by
  reusing the exact prior cell's control design, which is already validated).
- P(overall headline claim: "rule-induction + forward-chaining is a genuinely novel,
  worth-testing mechanism class for inductive relational inference, distinct from every
  embedding-family attempt tried so far") = **0.45** (capped at the 0.50 novel-synthesis ceiling;
  this is a claim about mechanism-class NOVELTY and test-worthiness, which is well-supported by the
  cross-thread evidence above, not a claim that the test will pass).

## Substrate-specific caution (not a field finding, an on-disk cross-check)

The relational scour's bucket D ("every LEARNED / substrate-native / typed router = HONEST_NEG")
means any future version of this mechanism that tries to make the *grounding/lookup* step
VSA-native (rather than an exact oracle dict, as specified above) inherits that already-proven
router-SNR wall and should not be treated as a fresh test of rule-induction — it would silently
re-test an already-closed question. Keep the induction and grounding questions strictly separated
in any follow-up cell design.

## Citations (verified count: 19, distinct)

Brain/rule-representation (6): Wallis, Anderson & Miller, *Nature* 2001 (411:953); Kriete, Noelle,
Cohen & O'Reilly, *PNAS* 2013 (110:16390); Smolensky, 1990 (tensor-product representations); Webb,
Sinha & Cohen, ICLR 2021 (ESBN, "Emergent Symbols through Binding"); Whittington, Muller, Mark,
Barry, Burgess & Behrens, *Cell* 2020 (TEM); Fodor & Pylyshyn, *Cognition* 1988 (carried forward,
re-verified current via 2025-26 follow-up surveys arXiv 2506.01820 / 2606.14512).

Differentiable rule induction (7): Yang, Yang & Cohen, NeurIPS 2017 (Neural-LP, arXiv:1702.08367);
Sadeghian, Armandpour, Ding & Wang, NeurIPS 2019 (DRUM); Qu et al., ICLR 2021 (RNNLogic,
arXiv:2010.04029); Meilicke et al. 2019/2020 (AnyBURL/SAFRAN, arXiv:2004.04412); Evans &
Grefenstette, 2018 (∂ILP, arXiv:1711.04574); Rocktäschel & Riedel, 2017 (Neural Theorem Provers) +
Minervini et al. 2018 (NaNTP, arXiv:1807.08204, scale-limitation follow-up); Teru, Denis &
Hamilton, ICML 2020 (GraIL, arXiv:1911.06962) + Zhu et al., NeurIPS 2021 (NBFNet,
arXiv:2106.06935) counted together as the benchmark-family citation.

Differentiable/probabilistic logic + path-ranking (6): Badreddine, Garcez, Serafini & Spranger,
*Artificial Intelligence* 2022 (LTN, arXiv:2012.13635); Manhaeve, Dumančić, Kimmig, Demeester & De
Raedt, NeurIPS 2018 (DeepProbLog) + Manhaeve et al., KR 2021 (approximate inference follow-up,
exponential-blowup confirmation); Richardson & Domingos, *Machine Learning* 2006 (MLN); Bach,
Broecheler, Huang & Getoor, JMLR 2017 (PSL); Lao & Cohen 2010 / Lao, Mitchell & Cohen, EMNLP 2011
(PRA) + Gardner & Mitchell, EMNLP 2015 (SFE, arXiv-adjacent, path-count-reduction follow-up); Zhu
et al. 2022 (A*Net, arXiv:2206.04798, million-scale path-method claim).
