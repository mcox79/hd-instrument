# Research: a stronger schema-fit / compositional-derivability signal to raise the foundation-builder gate's ceiling

Director synthesis + 2 parallel Sonnet lit-scans (brain: CA3/analogical/structural-inference derivability mechanisms;
network-science: pairwise link-prediction indices vs reachability/degree baselines), composed with a full re-read of
the landed `ingest_gate_combination_rule_race_v1` FULL+smoke metrics, `hdlab/reachability_audit.py`, the race cell's
source (`experiments/exp_ingest_gate_combination_rule_race_v1.py`), and the ALREADY-LANDED SR/resolvent machinery in
`experiments/exp_grounding_multihop_sr_reachability_routing_v1.py`. Research-only: no code written, no cell dispatched.
Generic neuroscience/network-science terms only in both external lit-scans.

## HEADLINE

**The current schema-fit signal (`build_schema_fit` in `exp_ingest_gate_consolidation_loop_pilot_v1.py`) is not a
pairwise derivability test at all — it is an aggregate PER-NODE percentile (mean of `reach_pct[h]` and `reach_pct[t]`,
each a rank-percentile of k-hop reachable MASS) that discards the specific h-to-t relationship entirely. Both brain
and network-science literatures independently and convergently say the fix is to make it PAIR-SPECIFIC and
MULTI-PATH-AGGREGATING instead of node-aggregate: the brain's derivability computation (CA3 attractor convergence,
analogical structure-mapping systematicity, Bayesian structural-form inference) integrates evidence across MANY
converging partial paths/relations, not one path or one node's generic connectivity; network science's own
answer to the identical mathematical question (Katz index / Resource-Allocation index / personalized-PageRank
resolvent) is exactly this: pairwise, multi-path-weighted proximity, and it is the literature's best-documented
beater of plain reachability and degree-based baselines. Concretely: the substrate already has the needed machinery
LANDED AND SELF-TEST-PASSED for a different task (`SRColumnSolver`, the resolvent M=(I-gamma*T)^-1 solver in
`exp_grounding_multihop_sr_reachability_routing_v1.py`) — repurposing it as a pairwise schema-fit score is a
near-zero-new-build change, not a new mechanism.** A second, independent, even cheaper finding: the reported 0.761
(smoke) / 0.836 (FULL test-split) ceiling is partly a SMALL-SAMPLE ARTIFACT of unweighted 3-seed averaging (one seed
has only 8 test-eligible facts total) — a free pooled-AUC recompute should be run before any new signal build.

## Q1 — BRAIN: how does the brain compute schema-congruency / derivability? (lit-scan, generic terms only)

Three independent literatures converge, with one explicitly confirmed gap:

1. **Hippocampal CA3 pattern completion is an aggregate convergence process, not a single-path retrieval.** CA3's
   recurrent-collateral autoassociative network (Marr 1971, *Phil Trans R Soc B*; Rolls & Kesner 2006) settles to a
   stored pattern from ANY partial cue via many weighted recurrent synaptic contributions converging simultaneously
   — functionally a multi-path VOTE, not a shortest-path search. Nakazawa et al. 2002 (*Science*, CA3-NMDAR knockout)
   behaviorally confirm this is a distinct cue-integrating computation (mutants fail specifically on completion from
   degraded cues, not on normal learning). Confidence: High for "aggregate convergence," Medium on whether the
   primary sources use an explicit "voting" framing versus this being the connectionist-mechanics interpretation.
2. **Analogical structure-mapping explicitly scores MULTI-relation systematicity, not single-predicate match.**
   Gentner 1983 / Falkenhainer, Forbus & Gentner 1989 (Structure-Mapping Engine): a candidate mapping is preferred
   when it connects MANY consistent relational matches under shared higher-order relations — literally a multi-path/
   multi-match count, not a single connection. Holyoak & Thagard's ACME (1989) formalizes this as constraint
   satisfaction over a network of many competing/supporting match hypotheses. Hummel & Holyoak's LISA (2003) is the
   partial counterweight: capacity-limited, largely sequential processing (2-3 propositions in working memory at
   once) — so the brain trades the "all paths at once" ideal against serial constraints, but mapping quality still
   depends on ACCUMULATED relational consistency across the sequence, not a single path. Confidence: High (explicit
   design principle in the primary papers, not an inference).
3. **Cognitive-map / structural-inference literature computes a Bayesian posterior over candidate STRUCTURES, not a
   nearest-neighbor lookup.** Kemp & Tenenbaum 2008 (*PNAS*) formalize structure discovery as inference over a SPACE
   of candidate structural forms (tree/ring/chain/grid), jointly scoring fit across all candidates — a multi-
   hypothesis posterior. Gershman/Niv-lineage latent-cause models (Gershman, Norman & Niv 2015) compute a
   nonparametric Bayesian posterior over which of MANY latent causes generated an observation — again integrating
   support across all candidates simultaneously, not testing one link. Behrens et al. 2018 (*Neuron*) / Whittington
   et al. 2020 TEM (*Cell*) frame new-relation fit as generalization from a factorized structural code evaluated
   across the WHOLE code, not one retrieved neighbor (Medium confidence here specifically — not posed as a discrete
   algorithm in the primary sources).
4. **Confirmed gap, not a missed search**: no published study directly compares "shortest path length" vs "number of
   independent relational paths" as predictors of relational-inference CONFIDENCE/ACCURACY in a semantic-memory or
   analogy paradigm. The closest adjacent evidence is network-science link-prediction (multi-path/common-neighbor
   heuristics reliably beat shortest-path-only heuristics — see Q2) and semantic-priming spreading-activation work
   (convergent multi-path activation produces stronger priming than any single link; Balota & Lorch, Hutchison 2003
   review) — informative analogs, not the same paradigm.

**Sub-agent headline (verbatim judgment)**: "the weight of evidence across independent literatures ... converges
strongly toward aggregate/multi-path evidence integration rather than single-path/simple-distance — though the one
literature that would directly test this trade-off head-to-head for relational-inference confidence specifically has
not been published (confirmed gap, not refuted)."

## Q2 — SUBSTRATE: ranked stronger schema-fit signal candidates (lit-scan + director synthesis)

Network-science lit-scan headline (verbatim): "**Personalized PageRank / Random Walk with Restart (rooted PPR)**,
closely followed by the **Katz index**, is most likely to outperform a generic 'average per-node reachable-mass
percentile' proxy ... Both are pair-specific resolvent-style scores that aggregate over ALL weighted paths between
the exact two nodes in question, capturing path multiplicity and directionality that a per-node aggregate mass score
structurally cannot represent." Supporting detail: Resource-Allocation index (Zhou, Lu & Zhang 2009, *EPJ B* 71:623)
beats both Common-Neighbors and Adamic-Adar on most benchmarks specifically because it down-weights high-degree hub
common-neighbors MORE aggressively (Lu & Zhou 2011, *Physica A* 390:1150, the standard survey) — directly relevant
because degree-confound is the SAME problem the reachability-audit note (`research_reachability_audit_arena_selection_vs_fundamental_null_2026-07-15.md`)
already flagged as never cleanly dissociable from path-length signal in ANY literature scanned. Katz/PPR/SimRank are
mathematically the same family (resolvent-style "sum over all paths, weighted by length via a decay function") and
consistently outrank local indices which outrank degree/centrality baselines, at higher compute cost. Confirmed gap:
no source benchmarks Katz/PPR specifically against a plain node-aggregate reachable-mass percentile (the literature's
default weak baseline is raw degree/PageRank, not this exact aggregate-mass construction) — so the substrate's own
`schemafit_alone` arm is testing an even weaker baseline than the field's usual comparison point, which if anything
raises confidence a pair-specific upgrade will show a real gap.

Ranked candidates for THIS substrate (cost / brain-alignment / novelty-of-build, cheapest first):

1. **Resource-Allocation-index pairwise score (cheapest, near-zero build).** `RA(h,t) = sum_{z in N(h) intersect N(t)} 1/deg(z)`
   — pure local 1-hop set intersection over `adj_found` (already built by `RA.build_undirected_adj`), down-weights
   hub-mediated false commonality (directly targets the degree-entanglement the brain lit repeatedly shows is never
   fully separable from path-length). No new machinery: reuses the SAME adjacency object the current `build_schema_fit`
   already constructs. Weakest brain-analog of the three (local-similarity family), strongest cost/build ratio.
2. **Pairwise multi-path count restricted to reach_k=2 (minimal upgrade of the EXISTING pipeline).** Instead of the
   current per-node reach-mass percentile average, count `|N(h) intersect N(t)|` (equivalent to un-weighted
   Common-Neighbors, the exact 2-hop analog of what the derivability ORACLE already checks) as a genuinely
   PAIR-SPECIFIC feature, still cheap, still reusing existing adjacency. Sits between (1) and (3) in richness.
3. **Personalized-PageRank / SR resolvent pairwise score (highest ceiling, ALSO near-zero new build — reuses a
   LANDED, SELF-TEST-PASSED component).** `experiments/exp_grounding_multihop_sr_reachability_routing_v1.py` already
   implements `SRColumnSolver`: `M = (I - gamma*T)^-1`, LU-factored once per gamma, `columns(goals_unique, gamma)`
   returns `M[:, goal]` for a batch of goals (already validated: `SELFTEST_PASS ... SR_SEEDED recovers ~SUPPLIED and
   >> memoryless on a clean-reachability planted graph`, per `data/substrate_capability_registry.jsonl`). This IS the
   Dayan-1993 successor-representation / personalized-PageRank resolvent the brain lit-scan (Q1) and the network-
   science lit-scan (Q2) both independently point to as the theoretically-correct multi-path aggregator — it is
   ALREADY brain-grounded from a prior drill (`research_successor_representation_reachability_autonomous_traversal_2026-07-09.md`,
   Stachenfeld/Botvinick/Gershman 2017 hippocampal predictive-map result, Millidge SR=PPR equivalence). Repurposing:
   treat `h` as the one-hot source/seed instead of a path-routing "current node," `t` as the goal; the schema-fit
   score for candidate `(h, r*, t)` becomes `M[t, h]` (or the symmetrized average with `M[h, t]` on the undirected
   graph) — a continuous, pair-specific, multi-path-weighted derivability score, computed on the exact same
   `adj_found` foundation graph already used for the label and the current `schema_fit`.

Embedding-composition distance (does composing known relation vectors from h land near t) is explicitly RULED OUT as
a fresh candidate — it is what the `flat`/`raw_PE` arm already measures (`additive_map.score_all`), and it already
collapsed to chance (flat deconf_test=0.542 FULL / 0.473 smoke) in the exact same race. A GNN/message-passing learned
score is also not recommended as the NEXT experiment: the `learned` arm (5-feature logreg) already partially tests
this and did NOT beat `schemafit_alone` on the held-out test split (0.628 vs 0.836), while beating it on the pooled/
full split (0.756 vs 0.719) — a pattern consistent with overfitting on very small per-seed samples (see Q3), not
evidence a full GNN would help; more data, not a heavier learned model, is the likelier lever.

## Q3 — is 0.76-0.84 a signal limit or a data limit? (director analysis of the landed metrics.json, no new compute)

**Concrete finding: it is materially BOTH, and the current headline number is inflated by unweighted small-sample
averaging.** Per-seed breakdown from `data/exp_ingest_gate_combination_rule_race_v1/metrics.json` (FULL run):

| seed | n_deriv | n_underiv | total held-out | schemafit deconf_test | schemafit deconf_full |
|---|---|---|---|---|---|
| 7  | 50 | 33 | 83 | 0.642 | 0.745 |
| 13 | 5  | 3  | 8  | **1.000** | 0.600 |
| 17 | 17 | 11 | 28 | 0.867 | 0.813 |
| **mean (equal-weight, as reported)** | | | | **0.836** | 0.719 |

Seed 13's test-split AUC of exactly 1.000 is computed over roughly 4 held-out test facts (n_calib=4, n_test=4 in the
FULL config) — a sample size at which only a small number of discrete AUC values are even reachable (0, 0.33, 0.5,
0.67, 1.0), and where a single ranking flip changes the value by 0.25-0.5. This tiny, high-variance estimate gets
EQUAL weight (1/3) in the reported aggregate as seed 7's much larger, much more stable 83-fact estimate (0.642). The
most-trustworthy SINGLE estimate we have (seed 7, largest N) puts the schema-fit-alone signal at 0.642 (test-split)
to 0.745 (pooled train+test) — **materially below the reported 0.836 headline**, which is pulled upward mainly by
the degenerate seed-13 sample. This is not a criticism of the race cell's harness (all harness-validity gates passed,
`arms_differ_verified=True`, array-recompute delta=0) — it is a property of averaging AUCs across very unevenly-sized
folds, a well-known statistical pitfall independent of anything substrate-specific.

**Actionable, zero-new-acquisition next step, cheaper than any new signal build**: recompute a single POOLED AUC over
all seeds' held-out facts concatenated (rather than the mean of 3 unequally-sized per-seed AUCs), or an n-weighted
average. This requires no new run — it is a re-aggregation of numbers already computed and already on disk (metrics.json
per-seed fields), or, if the raw per-candidate score vectors are wanted for an exact recompute, a re-pull of the FULL
run's `per_candidate_arrays.npz` from the remote runner (only seed 7's arrays were dumped locally per the cell's
`want = (si==0)` design; the smoke/full metrics.json currently on local disk do not include the npz). **Do this before
building a new signal** — it may already show the honest current ceiling sits closer to 0.70-0.75 with a tighter,
more defensible confidence interval, which reframes "how much lift is needed" for any new signal.

**Is there real headroom beyond the honest ~0.70-0.75 estimate, i.e. is 0.76-0.84 also a genuine signal limit?** Yes,
independently of the data-limit finding above: the CURRENT signal is structurally a node-AGGREGATE (discards
pair-specificity), and BOTH lit-scans converge on pair-specific multi-path aggregation being a different, richer
computation than what is currently measured — this is not merely re-measuring the same signal more precisely, it is
testing a genuinely different, more expressive feature. The brain literature's explicit confirmed gap (Q1.4) and the
network-science literature's confirmed gap (no source benchmarks Katz/PPR against this exact node-aggregate-mass
baseline) both mean the SIZE of the expected lift is not directly citable from prior work — it must be measured on
this arena, not assumed from either literature.

## Q4 — concrete improved-signal design, ready to drop into the schema-fit-direct gate

**Two-tier recommendation, cheapest first, both pair-specific (the property the current signal lacks), both reusing
already-built components (zero new machinery, only new call sites):**

**Tier A (cheapest, ~1 new function, reuses `RA.build_undirected_adj` verbatim):**
```
def resource_allocation_pairwise(adj, h, t):
    # adj: same Adj type reachability_audit.py already returns from build_undirected_adj(base_train_int, N)
    nh = set(int(x) for x in adj[h]); nt = set(int(x) for x in adj[t])
    common = nh & nt
    if not common: return 0.0
    return sum(1.0 / len(adj[z]) for z in common if len(adj[z]) > 0)
```
Replace `schema_fit_edges`'s current `0.5*(reach_pct[h]+reach_pct[t])` with a rank-percentile of this pairwise RA
score across the candidate set (same `_rank_pct` helper already used). Cost: one BFS-adjacent set-intersection per
candidate edge, O(deg(h)+deg(t)) -- negligible next to the existing full re-fit cost this gate is meant to route
around.

**Tier B (higher ceiling, reuses the ALREADY-LANDED `SRColumnSolver` class verbatim, one new call site):**
```
# reuse experiments/exp_grounding_multihop_sr_reachability_routing_v1.py's SRColumnSolver unchanged
solver = SRColumnSolver(T=row_normalize(adj_found), device=device)   # T built from the SAME adj_found
X = solver.columns(goals_unique=held_int[:, 2], gamma=GAMMA)          # M[:, t] columns, batched over unique targets
schema_fit_pairwise = X[held_int[:, 0], col_index_of(held_int[:, 2])] # M[t, h] per (h,t) candidate pair
```
`GAMMA` should be swept conservatively (0.5, 0.6, 0.7 -- reusing the exact gamma-sweep discipline already
pre-registered and run once in the SR-routing cell) rather than defaulted, for two explicit, already-precedented
reasons: (a) too-high gamma degenerates toward the goal-agnostic global stationary distribution (the same smearing
failure already documented in the SR-routing note), losing pair-specificity; (b) too-high gamma (or too many
Neumann-series terms) risks approaching a near-exact reconstruction of the `reach_k=2` BFS-membership label itself,
which would trip the race cell's own `SCHEMAFIT_LEAK_MAX=0.95` guard (schema_fit near-copying the label -- vacuous,
per the cell's own design comment distinguishing "entity-connectivity" from "the specific h->t path"). A mid-range
gamma keeps the score a genuine multi-path PROXY, graded and pair-specific, without collapsing to either failure
mode.

**Predicted lift (deflated per lit-scan calibration discipline, both capped at P<=0.50 as novel on-substrate
synthesis):**
- P(Tier A -- Resource-Allocation pairwise index -- beats the HONEST pooled/seed-7-anchored baseline of ~0.70-0.75,
  i.e. clears ~0.78-0.80 on a properly pooled re-test) = **0.40** (undeflated ~0.55-0.60; network-science evidence for
  RA beating aggregate/degree baselines is strong and general, but untested on this exact arena and this exact
  "aggregate-mass" baseline specifically).
- P(Tier B -- SR/PPR pairwise resolvent -- clears a materially higher bar, ~0.82-0.88 pooled) = **0.35** (undeflated
  ~0.50-0.55; strongest theoretical convergence of any candidate in this drill -- brain AND network-science AND an
  already-validated on-substrate implementation all point the same direction -- but deflated hardest because no
  source in either lit-scan benchmarks this exact family against this exact node-aggregate-mass baseline, and the
  gamma-vs-leak tradeoff is a real, not yet swept, risk specific to this repurposing).
- P(the pooled/n-weighted AUC recompute alone, with NO new signal, moves the honest current-signal estimate down
  from 0.836 to the 0.70-0.75 range implied by the per-seed table above) = **0.55** (this is a mechanical
  re-aggregation claim grounded directly in visible per-seed sample sizes already on disk, not novel synthesis --
  less deflation warranted than the two signal-upgrade predictions above).

## Cross-thread synthesis

- Directly extends `research_consolidation_gate_quantitative_signals_2026-07-16.md`'s fast_track/slow_track
  decomposition proposal: that note derived the COMBINATION form (schema_fit as mixing weight); this note answers the
  separate, now more decision-relevant question the landed race cell surfaced -- schema_fit ALONE, not the
  interaction, carries the fix (SCHEMAFIT_CARRIES verdict), so improving schema_fit's own quality is now the single
  highest-leverage lever for the whole gate, not the combination arithmetic.
- Directly reuses and is a second independent confirmation of `research_successor_representation_reachability_autonomous_traversal_2026-07-09.md`'s
  SR=PPR-resolvent finding -- that note applied the resolvent to PATH-ROUTING (which neighbor leads toward a distant
  goal); this note applies the SAME already-built, already-self-test-passed machinery to DERIVABILITY SCORING (does a
  candidate fact fit the schema) -- one landed component, two independent capability uses, not a new build for
  either.
- Confirms and sharpens `research_reachability_audit_arena_selection_vs_fundamental_null_2026-07-15.md`'s repeated
  finding that path-length/reachability signals are never cleanly dissociable from degree/hubness in ANY literature
  scanned -- the Resource-Allocation index (Tier A above) is the network-science field's own answer to exactly this
  problem (down-weighting hub-mediated commonality), giving that prior note's tempering finding a concrete,
  buildable fix rather than leaving it as an accepted limitation.
- The small-sample-averaging finding (Q3) is a NEW methodological caution for this cell family specifically -- flag
  for `skunkworks` landed-VET review of `ingest_gate_combination_rule_race_v1` (already routed there per the dispatch
  note) as an explicit audit item: verify whether the VET should require n-weighted or pooled aggregation for any
  future AUC-race cell with per-seed class counts this small, not just this one.

## Substrate-product implications

1. Both recommended signal upgrades (Tier A and Tier B) cost effectively ZERO new infrastructure -- Tier A is one
   ~10-line function reusing an object `reachability_audit.py` already builds; Tier B reuses a class that is already
   landed, already self-test-passed, and already proven correct on a related but distinct task. This is a genuine
   "raise the ceiling for free" opportunity if either lift materializes, not a new build investment.
2. The pooled/n-weighted AUC recompute (Q3) should happen BEFORE either signal upgrade is built -- it is strictly
   cheaper (zero new code, possibly zero new compute if the existing per-seed numbers suffice for an n-weighted
   recompute) and directly changes what "beating the current ceiling" even means.
3. If Tier B (SR/PPR) is pursued, the gamma-sweep discipline must be treated as load-bearing, not optional -- both
   the smearing failure mode (documented once already in the SR-routing note) and the SCHEMAFIT_LEAK guard (already
   coded into the race cell) are real, named risks specific to this repurposing, not generic caution.
4. This is a genuinely different signal category from anything already tested in the race (flat/raw_PE, the current
   node-aggregate schemafit, and the 5-feature learned arm all failed to be PAIR-SPECIFIC multi-path aggregators) --
   it is not a re-run of an already-falsified idea.

## Citations (verified count: 2 lit-scans, ~20 distinct sources combined; not independently WebFetch-verified by
director this cycle beyond what each sub-agent reported -- treat as reported-not-independently-confirmed per standing
discipline)

**Brain/cognitive-science (~11):** Marr 1971, *Phil Trans R Soc B* (CA3 autoassociative theory); Rolls & Kesner 2006
(CA3 pattern completion review); Nakazawa et al. 2002, *Science* (CA3-NMDAR knockout, degraded-cue completion
deficit); Gentner 1983 (structure-mapping theory); Falkenhainer, Forbus & Gentner 1989 (SME); Holyoak & Thagard 1989
(ACME multiconstraint theory); Hummel & Holyoak 2003 (LISA, capacity-limited relational binding); Behrens et al.
2018, *Neuron* ("What Is a Cognitive Map?"); Whittington et al. 2020, *Cell* (Tolman-Eichenbaum Machine); Kemp &
Tenenbaum 2008, *PNAS* (Bayesian structure discovery); Gershman, Norman & Niv 2015 (latent-cause models).

**Network-science (~9):** Zhou, Lu & Zhang 2009, *Eur Phys J B* 71:623 (Resource-Allocation index); Lu & Zhou 2011,
*Physica A* 390:1150 (link-prediction survey, RA>=AA>=CN>=Jaccard ranking); Liben-Nowell & Kleinberg 2007, *JASIST*
58:1019 (original systematic link-prediction comparison); Katz-index / Fast-Katz literature (Springer 2011,
"Commuters" line); SimRank/PPR/Katz-unification papers (arXiv:2410.13018); implicit-degree-bias literature
(arXiv:2405.14985); GNN link-prediction degree-bias amplification (arXiv:2309.17417, "Networked Inequality");
structure-augmented KGE + rule-learning-beats-embeddings-on-sparse-relations literature (arXiv:2406.10144).

Plus REUSED (not re-verified this cycle, already verified in their originating drills): Dayan 1993, Stachenfeld/
Botvinick/Gershman 2017 (*Nat Neurosci*), Millidge SR=PPR equivalence (arXiv:2512.24722) -- all from
`research_successor_representation_reachability_autonomous_traversal_2026-07-09.md`.

## Deflated confidence summary (lit-scan calibration: deflate 0.15-0.25; novel-synthesis capped at 0.50)

- P(the brain's derivability computation is better characterized as aggregate/multi-path than single-path/distance)
  = **0.55** (undeflated ~0.75-0.80 given 3 independent convergent literatures; deflated for the explicitly confirmed
  gap that no study directly tests this trade-off for relational-inference confidence specifically -- strong
  convergence on a related but not identical construct).
- P(Tier A -- RA pairwise index -- lifts the honest baseline) = **0.40** (see Q4 detail above).
- P(Tier B -- SR/PPR pairwise resolvent -- lifts the honest baseline more than Tier A) = **0.35** (see Q4 detail
  above; capped at novel-synthesis ceiling).
- P(pooled/n-weighted recompute alone reveals the honest current ceiling sits nearer 0.70-0.75 than the reported
  0.836) = **0.55** (mechanical claim, grounded in visible per-seed n already on disk).

## Next-drill candidate

If Tier B (SR/PPR resolvent) is built and piloted: the natural next drill is the SAME `network-science-graph-theory`
Tier-1 field the reachability-audit note already flagged (spectral-gap / expander-mixing bounds) to get a predictive,
closed-form estimate of how much relation-type/path-diversity a subgraph needs before the resolvent's gamma-sweep
avoids both smearing and leak, replacing per-arena empirical tuning with a design rule. If Tier A/B underperform the
honest pooled baseline: next drill should target whether the DERIVABILITY LABEL itself (reach_k=2 BFS membership) is
too coarse a ground truth (a binary cutoff at exactly 2 hops may itself discard the graded multi-path information any
richer signal would need to correlate against) -- i.e. test whether a GRADED derivability oracle (e.g. exact path
count at k=2, not just membership) changes which signal wins, before concluding pairwise signals in general are
capped on this arena.
