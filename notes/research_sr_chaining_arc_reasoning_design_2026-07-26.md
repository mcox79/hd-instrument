# Research: wiring the prior HARD_PASS SR-routing + gated-fusion mechanisms to the ARC derivation reasoner — design only

**Filed by:** research sub-agent. **Trigger:** `notes/grounding_work_lookback_synthesis_2026-07-26.md` — grounding is real+validated but redundant for reasoning; the recurring wall is CHAINING/TRANSFER; two brain-aligned mechanisms (SR-reachability routing, gated fusion) partially cracked chaining on a toy ConceptNet-allometry domain but were never wired to the ARC reasoner (`hdlab/reasoner.py`, coverage-bound meet-in-middle). Task: brain-drill first, then pin the honest ARC target, then design (not build) a can-fail cell reusing both prior mechanisms verbatim, GloVe-free.

**KB-check:** `tools/substrate_query.sh "successor representation reachability ARC reasoning chaining tie-break"` returned no prior atom wiring SR to the ARC reasoner's tie-break or coverage (top hits were the generic SR-framing note and unrelated `reasoning` concept nodes) — this is net-new ground, not a redo.

---

## STEP 1 — Brain-drill: how the brain does multi-hop relational chaining + compositional generalization

**SHAPE: the resolvent / predictive map.** Hippocampal place-cell firing encodes not "where am I" but "what states will I be in soon under my current policy" — the successor representation (SR), `M(s,s') = E[sum_t gamma^t * 1{s_t=s'}]`, solved in closed form by `M = (I - gamma*T)^-1` (Stachenfeld, Botvinick & Gershman 2017, *Nat Neurosci*, "The hippocampus as a predictive map"). This is mathematically identical to a resolvent / personalized PageRank / discounted-occupancy value function (Dayan 1993's original TD-SR; Millidge arXiv 2512.24722 states the three-way equivalence directly). **PLACE:** hippocampus (CA3 recurrent collaterals implement `T` implicitly; CA1/place cells read out `M`'s rows); **METRIC:** expected discounted future occupancy, aggregated over ALL walks of ALL lengths weighted by `gamma^t` — a graded, continuous evidential-support quantity, not a boolean "is there a path" flag.

**Mechanistic realization (not a hand-wave — actual synaptic rule).** Bono, Zannone, Pio-Lopez & Ponte Costa (2023, *eLife*) show the SR update is implementable by a temporally-asymmetric Hebbian potentiation term (pre-then-post activity across one timestep) plus a local anti-Hebbian/normalization depotentiation term, with CA3 recurrence implementing `T` and acetylcholine proposed to modulate the discount. Critically (Russek et al. 2017 *PLOS Comp Biol*; Momennejad 2020 review; already established in `notes/research_learned_partial_graph_SR_reasoning_vs_search_CG_path_2026-07-09.md`): **raw sampled/TD-learned SR never populates rows for unvisited state-action pairs** — it does NOT by itself generalize to structure never experienced. That prior drill's honest correction is load-bearing here too (see "MM not CG" honesty note below).

**Replay / preplay for multi-step reach (not just single-step TD).** Ólafsdóttir et al. (2015, *eLife*) and Dragoi & Tonegawa (2011, *Nature*, "preplay") show hippocampal sequences can traverse never-directly-experienced trajectories offline, and Pfeiffer & Foster (2013, *Nature*) show place-cell sequences ahead of a moving animal encode the future path to a GOAL before it is reached — i.e. the brain runs internally-generated multi-step lookahead over the SAME predictive map, goal-conditioned, exactly the mechanism the already-certified toy SR cell (`exp_grounding_multihop_sr_reachability_routing_v1`) operationalized as `x[v] = M[v, G]`.

**Multi-scale gamma (dorsal-ventral axis).** A bank of SR representations at different temporal scales (different `gamma`) maps onto place-field size along the hippocampal dorsal-ventral axis (short `gamma` dorsal / long `gamma` ventral) — already flagged in `notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md` section 3.2. Relevant here only as a reported diagnostic (gamma sweep), not a primary mechanism — matching the discipline the toy SR cell already used (`DIAG_GAMMAS` logged, not gated).

**Grid cells / entorhinal relational structure + systematicity.** Entorhinal grid cells provide a compressed low-rank spectral (eigenvector) basis for the SR matrix (Stachenfeld 2017) — a metric, relation-general coordinate system reused across environments. Whittington et al. (2020, *Cell*, the Tolman-Eichenbaum Machine) formalize this: a factorized code where an entorhinal-like "structural" representation (transferable across environments) binds to a hippocampal-like "content" representation (environment-specific), and show this factorization is what lets the model generalize a learned relational structure (e.g. a graph topology) to NEW content it has never seen bound to that structure. This is the biological answer to Fodor & Pylyshyn's (1988) systematicity challenge: compositional generalization requires structure and content to be represented SEPARABLY (a role/filler or structural/content split), not fused into one undifferentiated vector — the same principle already adopted in this program's native-binding compositional-generalization design (`notes/research_native_binding_compositional_generalization_2026-07-25.md`, fixed role hypervectors + shared linear readout vs flat MLP hub).

**Synthesis for this task.** The brain's chaining mechanism is: (1) a resolvent/SR **occupancy measure** over a transition structure — SHAPE = graded, multi-path-aggregating, goal-conditioned; (2) computed over hippocampal PLACE (CA3/CA1), read out via replay for multi-step reach; (3) METRIC = discounted occupancy, not boolean reachability. The prior toy-domain HARD_PASS (`exp_grounding_multihop_sr_reachability_routing_v1`, SR_SEEDED reach@2=0.434 vs greedy 0.181, delta +0.253, gamma=0.85, non-degenerate SR column) is a faithful MM-tier (known-map, not learned) realization of this SHAPE/METRIC. The gated-fusion cell (`exp_grounding_gated_fusion_relation_inference_mammal_v1`, HARD_PASS, learned convex `(1-lambda)*A + lambda*B` recovering a channel's standalone strength without dilution, lambda grid-searched on a disjoint VAL split, endpoint lambda=1 in the search grid so it provably cannot underperform the channel it recovers) is the brain-plausible **arbitration** mechanism for combining two evidence channels — directly analogous to basal-ganglia gating / gain-modulated channel combination, and the honest fix for a documented failure mode (naive equal-weight fusion dilutes a strong channel).

**Honesty carried forward from the prior SR drill (load-bearing, not optional):** the certified SR-routing cell's own reciprocal-necessity self-test showed its routing intelligence is **closed-form graph search over a KNOWN, fully-specified transition matrix** — "PageRank on a handed map," not learned generalization (MM, not CG). The ARC typed-rule graph (`hdlab/reasoner.py`, `data/rules/arc_science_typed_rules_v1.json`, 233 hand-authored rules) is likewise a small, fully-known, static graph. Any SR transplant here is THEREFORE also honestly MM-tier — a known-graph resolvent computation, not a claim of learned structural generalization. This is fine and consistent: the existing tie-break machinery it would compete against (`chain_len`, `combiner_score` cosine, `INTENT_PATTERNS` symbolic match) are ALSO known-graph/known-lexicon mechanisms, not learned generalization. The comparison is apples-to-apples in tier; do not oversell this as a CG result.

---

## STEP 2 — Pinning the honest ARC target (argued, not hand-waved)

**The numbers that decide this** (measured, `data/exp_arc_reasoner_link_precision_tie_prune_v1/metrics.json` + `data/exp_arc_reasoner_symbolic_tiebreak_v1/metrics.json`, 1172 ARC-Challenge-test questions, 233 typed rules, graph `n_nodes=215, n_typed_edges=209`):

| bucket (link_mode=lemma_syn) | n | frac of 1172 | frac of derived (206) | acc |
|---|---|---|---|---|
| NOT derivable at all (neither gold nor any distractor reachable within depth<=3) | 966 | 82.4% | — | (similarity fallback) |
| gold_only (exactly one candidate, and it is gold) | 26 | 2.2% | 12.6% | **1.00** |
| dist_only (a distractor derivable, gold is NOT) | 114 | 9.7% | 55.3% | 0.00 (wrong by construction) |
| tie (both gold and >=1 distractor derivable) | 66 | 5.6% | 32.0% | 0.3636 |

Two decision-relevant facts:
1. **`meet_connected` is EXHAUSTIVE BFS to depth<=3 in both directions (meet-in-middle), not greedy.** (`experiments/exp_arc_derivation_connectivity_gate_v1.py::meet_connected/_reach`.) There is no "greedy hop-selection misses a path that exists within the depth budget" failure mode for SR to fix here — if a path <=3 hops exists, the existing boolean check already finds it. SR's core differentiator vs a hard-cutoff BFS (aggregating over ALL walk lengths, weighted by decay, vs a single boolean "reachable within depth 3") only has room to matter (a) beyond the depth-3 cutoff, or (b) when MULTIPLE candidates are already co-derivable and a graded strength score could rank them.
2. **The graph is tiny and near-degree-1** (`n_nodes=215, n_typed_edges=209`, mean out-degree < 1) — 22x sparser than the toy domain where SR was HARD_PASS (`n_nodes=4440, n_edges=14767`, mean degree 6.65). SR's distinguishing mechanism is aggregating over MULTIPLE alternate paths; at mean-degree < 1 most reachable node-pairs have at most one path, so SR's occupancy score is expected to closely track (not meaningfully augment) the single-path `chain_len` signal already in use. This is a real, pre-registerable risk — not an excuse to skip the test, but the honest prior.

**Decision: PIN THE TARGET AS THE TIE BUCKET (decision quality among already co-derivable candidates), not depth-extension of the boolean reachability gate.** Argument:
- Extending `meet_connected`'s hard depth cutoff (3 -> 5 or 6) is a **near-zero-cost hyperparameter bump on the existing exhaustive BFS** — it does not require SR's resolvent machinery at all, since the graph is small enough that exhaustive BFS to depth 6 is trivial. Framing "coverage" as an SR-routing problem would be dressing up a one-line config change as a research result; that is dishonest scope-inflation, and the DEPTH bump is a separate, much cheaper experiment (see the diagnostic below, which determines whether it's even worth dispatching).
- The **dist_only bucket (55% of all derived questions — the single largest bucket)** is dominated, per the prior comprehension audit already on record (`hdlab/reasoner.py` docstring: "COMPREHENSION uses the crude `_content_words()` extractor... Rule-supply (Step 1) + grounded meaning (Step 5) expand [coverage]"; entity-linking sweep glove->lemma->lemma_syn already lifted `gold_cov` 54->60->92 out of 1172), by ENTITY-LINKING and RULE-SPARSITY, not by search depth or search quality. SR cannot invent an edge that a linking failure never created a node for. This is a separate, already-flagged build item (grounded meaning / situation_reader wiring), not the SR-transplant's job.
- The **tie bucket (66 questions, 32% of derived) is a genuine, MEASURED, currently-unsolved decision problem**: the existing symbolic-intent tie-break (`exp_arc_reasoner_symbolic_tiebreak_v1`) landed **HONEST-NEG, delta = 0.000** versus the legacy cosine/chain-length tie-break — intent-relation matching fires on only 13/66 ties and even then aligns with gold's derivation-terminal relation in just 4/13 (diagnostic: `tie_mechanism_diagnostic.intent_aligns_gold_count=4`). SR-occupancy is a genuinely DIFFERENT hypothesis from both failed levers (question-intent matching, thin bundled-evidence cosine): it scores **aggregate graph-support strength** (how many, and how short, the paths from the given nodes to each candidate are), which neither prior lever computes. This is untested, falsifiable, and cheap (the graph is tiny; a dense LU solve is sub-second).

**Coverage-first-diagnostic, decision-first-build.** Per the "audit data/setup before trusting a run" discipline, run the cheap coverage classification (below) FIRST, as a reported (non-gated) side-computation in the SAME dispatch, to settle whether a follow-on DEPTH-bump experiment is worth queuing — without conflating that separate, much-cheaper question with the SR can-fail test itself.

---

## Cheap decisive test (run first, report-only, ~free — settles the coverage question honestly)

For each of the 114 (lemma_syn) / 69 (lemma) `dist_only` questions, classify gold's failure mode using the SAME entity-linking + SAME graph already built by `DerivationReasoner`:
- **LINK_FAILURE**: `nodes_for(gold_choice_text)` is EMPTY (no graph node found at all for gold's content words) — SR/depth-extension cannot help; this bucket needs entity-linking precision or rule-supply (already-flagged separate items).
- **DEPTH_BLOCKED**: gold's node set is non-empty AND `meet_connected(..., depth=6)` (extend `_reach` past the pre-registered depth=3 cutoff — trivial cost on a 215-node graph) NOW succeeds — this bucket is recoverable by a near-zero-cost `DEPTH` hyperparameter bump, a SEPARATE, much cheaper follow-on experiment, not requiring SR.
- **STRUCTURALLY_ABSENT**: gold's node set non-empty but STILL disconnected at depth<=6 — needs more rules or a precision fix to the entity link (mapped to the wrong node).

Report the 3-way split fraction. This is the test that decides whether "coverage first" was left on the table cheaply, without pretending SR-routing is the mechanism for it.

---

## STEP 3 — Pre-registered can-fail cell design (design only — NOT built or dispatched)

**Proposed anchor name:** `exp_arc_reasoner_sr_gated_tiebreak_v1` (for `hdi_exp_dev` to author).

**Reuse, verbatim, no reinvention:**
- `hdlab/reasoner.py::DerivationReasoner` — the built typed graph (`g["fwd"]`/`g["bwd"]`/`g["edge_rel"]`, `n_nodes=215`), `meet_connected`, the existing `per_choice` fields (`derivable`, `givens_covered`, `chain_len`, `combiner_score`, `rejected_by_ci`), and the `link_mode="lemma_syn"` GloVe-free entity-linking path already measured (`data/exp_arc_reasoner_link_precision_tie_prune_v1`).
- `experiments/exp_grounding_multihop_sr_reachability_routing_v1.py::SRSolver` / `build_transition_dense` — the closed-form resolvent machinery VERBATIM (LU-factor `(I - gamma*T)` once, multi-RHS solve for goal columns; pre-registered `SR_GAMMA_PRIMARY=0.85`, NOT tuned on real data; `DIAG_GAMMAS={0.70,0.85,0.95}` reported diagnostic sweep, not gated). Trivial adapter needed: `T` here is built from `g["fwd"]` (`Dict[int,set]`) rather than the toy cell's `dir_adj` list-of-`(v,rel)` tuples — a few lines, not a new mechanism.
- `experiments/exp_grounding_gated_fusion_relation_inference_mammal_v1.py` pattern — the learned convex gate `(1-lambda)*A + lambda*B`, lambda grid-searched (`LAMBDA_GRID`, 11 points 0.0..1.0) on a disjoint split, with the pure-endpoint of EACH channel included in the grid (so the gate provably cannot underperform whichever single channel is better on the held split) — reused as the ARBITRATION pattern between the existing `combiner_score` channel and the new SR-occupancy channel.

**Mechanism (glass-box, one new scalar per candidate + one learned scalar per split):**
1. For each question, `occ(candidate) = ` SR column value `M[given_nodes, candidate_nodes]`, min-max normalized WITHIN each question's candidate set (reused pattern from `sr_boost_by_chain`'s within-candidate normalization) so `occ in [0,1]`.
2. `z(combiner_score)` similarly min-max normalized within the candidate set.
3. `gated_score(candidate) = (1-lambda)*z(combiner_score) + lambda*occ(candidate)`.
4. Decision key among CO-DERIVABLE valid candidates: `(-gated_score, -givens_covered, chain_len, choice_index)` — `gated_score` promoted above the existing discrete keys (matching how `combiner_score` already sits as the graded signal before the final index tiebreak); `givens_covered`/`chain_len`/`choice_index` retained as deterministic fallback (ONE variable changed: the graded channel).
5. `lambda` selected by 5-fold cross-validation over the tie bucket (stratified, seeded `np.random.default_rng`, `sorted()` not `list(set())` per the split-determinism discipline) — chosen because `n_tie` (44-66) is too small for a stable single train/val/test split; CV is the standard remedy and keeps methodological parity with the gated-fusion cell's "learn on a disjoint split, apply out-of-sample" discipline while being usable at this n. Grid search maximizes TIE-subset accuracy on the held-out fold; report the mean held-out `lambda*` and its distribution across folds.

**Arms (paired: identical graph + identical `link_mode="lemma_syn"` + identical CI/do-calculus; ONLY the tie-break decision differs):**
- `LEGACY` — reproduction anchor of the existing `tiebreak_mode="legacy"` (must reproduce `tie_acc=0.3636 @ n_tie=66` within tolerance — Gate-D positive control).
- `SYMBOLIC` — reproduction anchor of `tiebreak_mode="symbolic"` (must reproduce `tie_acc=0.3636`, `d=0.000` vs legacy — the already-measured prior failed lever, kept for side-by-side comparison).
- `SR_ONLY` (diagnostic) — pure `lambda=1` endpoint: rank purely by `occ`. Isolates the standalone signal.
- **`SR_GATED` (primary candidate)** — the learned convex blend described above.
- `SR_SCRAMBLED` (must-fail control #1) — identical SR machinery computed over a DEGREE-PRESERVING RANDOM RELABELING of edge destinations (a configuration-model shuffle of `g["fwd"]`, seeded) — destroys genuine graph structure while preserving degree sequence. If `SR_SCRAMBLED`'s gated tie_acc rises comparably to `SR_GATED`, that is the artifact signature (any structural-looking score would have "helped," meaning the win is not about real reachability).
- `RANDOM_OCCUPANCY` (must-fail control #2, further null) — `occ` replaced by i.i.d. uniform noise per candidate, same gate procedure. Sanity floor: must not do better than `LEGACY`.

**Pre-registered bands (mirroring `exp_arc_reasoner_symbolic_tiebreak_v1`'s exact structure for direct comparability across BOTH tested tie-break levers):**

Guardrails (all must hold, else `INCONCLUSIVE`):
- `gold_only` preserved >= 0.95 (structural regression guard; trivially expected since gate only fires on ties).
- `n_tie >= 30` (both lemma_syn=66 and lemma=44 configs clear this).
- SR column non-degenerate: mean per-question within-candidate std of `occ` >= `1e-4` (reused `SR_DEGEN_STD_MIN` from the toy cell). **This is the single most likely failure point given the mean-degree<1 graph** — expected to fail or sit near the floor; report honestly either way.

HARD_PASS (`SR_GATED_TIEBREAK_RECOVERS`):
- `SR_GATED` tie_acc − `LEGACY` tie_acc >= 0.10 absolute, AND
- `SR_GATED` tie_acc >= 0.42 absolute (matching the prior symbolic-tiebreak cell's exact bar), AND
- `SR_SCRAMBLED` tie_acc − `LEGACY` tie_acc <= 0.03 (must-fail control stays flat — real structure, not artifact), AND
- mean CV `lambda*` > 0.15 (the gate genuinely leans on SR rather than degenerating to ~legacy), AND
- `gold_only` preserved, SR column non-degenerate.

MIDDLE_BAND: `SR_GATED` rises by `[0.03, 0.10)` over legacy with guardrails holding, OR SR non-degenerate but mean `lambda*` <= 0.15 (gate correctly detects SR isn't pulling weight but the blend still nets a small positive from regularization interaction — report honestly as "mechanism present but weak at this scale").

HARD_FAIL (`SR_GATED_TIEBREAK_FAILS`): `SR_GATED` tie_acc − legacy <= 0.03 (stuck, matching the prior cell's `tie_rise_stuck=0.03`), OR SR column degenerate at this graph scale (the honest "graph too sparse for SR's multi-path signal" collapse predicted above), OR `SR_SCRAMBLED` rises comparably to `SR_GATED` (artifact).

---

## Falsifiable predictions

**HARD-PASS prediction (what must be true, jointly, for this to be a real win):** `SR_GATED` tie-subset accuracy >= 0.42 absolute AND >= 0.10 above legacy's 0.3636, on BOTH `lemma_syn` (n_tie=66) and `lemma` (n_tie=44) link-mode configs (cross-config consistency, not a single lucky split); mean CV `lambda*` > 0.15; `SR_SCRAMBLED` and `RANDOM_OCCUPANCY` both stay within 0.03 of legacy; SR column non-degenerate (std >= 1e-4); `gold_only` accuracy unchanged at 1.00.

**HARD-FAIL prediction (the most likely honest outcome, stated in advance):** given the graph's mean out-degree < 1 (22x sparser than the domain where SR was previously HARD_PASS), predict the SR column will be **near-degenerate** (most given-candidate pairs have at most one path, so `occ` collapses to a near-binary reachable/unreachable indicator that `chain_len` already captures) — expected outcome is `HARD_FAIL_SR_DEGENERATE_AT_THIS_SCALE` or, if not literally degenerate, the CV-learned `lambda*` collapsing toward 0 (the gate correctly detects SR adds nothing beyond the existing cosine channel, mirroring the symbolic-tiebreak cell's `d=0.000` outcome). This would be a THIRD independently-diagnosed instance of "meaning/decision-bound wall, not a structural lever" for this exact tie bucket — informative, not wasted, and would redirect the tie-break problem decisively toward comprehension/semantic-role features (situation_reader wiring) rather than further graph-structural levers.

**Coverage-diagnostic prediction:** most `dist_only` failures are expected to classify as `LINK_FAILURE` or `STRUCTURALLY_ABSENT` rather than `DEPTH_BLOCKED`, given the graph's small size already makes depth<=3 close to exhaustive relative to what a fully-known 215-node/209-edge graph can reach at all — i.e. depth-extension alone is predicted to recover only a small minority of the 114-question `dist_only` bucket. If this prediction is wrong (a large `DEPTH_BLOCKED` fraction), that is the signal to dispatch the trivial DEPTH-bump follow-on next, ahead of any further SR-mechanism work.

---

## Cross-thread synthesis

- Directly extends `notes/grounding_work_lookback_synthesis_2026-07-26.md`'s reframe ("the wall is chaining, not grounding") by giving the two named-but-unwired mechanisms (SR-routing, gated-fusion) their first honest ARC-facing test, rather than leaving them stranded on the toy mammal/ConceptNet domains.
- Builds on, rather than re-derives, `notes/research_learned_partial_graph_SR_reasoning_vs_search_CG_path_2026-07-09.md`'s hard-won honesty correction (raw/known-T SR is MM not CG) — this design explicitly inherits that tier-honesty rather than re-litigating it.
- Directly extends the `hdlab/reasoner.py` + `exp_arc_reasoner_symbolic_tiebreak_v1` + `exp_arc_reasoner_link_precision_tie_prune_v1` thread (MEMORY: "symbolic tie-break d=0 (29569); rule/link precision 1/66-spurious-only-by-collapsing-gold") — this is the NEXT lever in that same, still-open tie-break problem, using a mechanism (graph-support aggregation) that neither prior attempt (question-intent matching, thin cosine) computed.
- Consistent with the MEMORY brain-fidelity-element-audit discipline: this design explicitly scores the mechanism's SHAPE (resolvent occupancy) against the target graph's actual scale (mean degree < 1) BEFORE building, rather than assuming a brain-faithful mechanism must transfer regardless of structural fit — the honest prediction above is that it may not, at THIS graph density, and says so in advance.

## Substrate-product implications

- If HARD-PASS: the tie-break wall (previously flat at `d=0.000` under BOTH tested levers) gets its first genuine lift from a brain-aligned mechanism, and the reusable `SRSolver`+gated-blend pattern becomes a template for any future decision point in the reasoning stack where multiple structurally-valid candidates need raw graph-support arbitration (not just ARC).
- If HARD-FAIL via SR-degeneracy: this is a clean, informative negative that LOCALIZES the graph-density precondition SR needs (roughly the toy domain's mean-degree ~6+, not the ARC rule-graph's <1) — directly actionable: either grow the typed-rule graph's edge density (more rules per entity) before retrying a structural lever, or accept that THIS decision point is comprehension/meaning-bound (situation_reader, Step 5 grounded meaning) and stop spending structural-lever cycles on it, per the already-flagged program pivot.
- Either way, the coverage diagnostic (report-only, nearly free) settles whether a trivial DEPTH-bump follow-on is worth a separate, much cheaper dispatch — decoupling that decision from this cell's verdict.

## P_deflated

**0.22.** Raw intuition before penalty: ~0.40 (two independently-HARD_PASS brain-aligned mechanisms, reused verbatim, applied to a genuinely novel decision point neither has touched). Deflated per the standing lit-scan/novel-synthesis calibration (0.15-0.25 penalty; novel-synthesis capped at 0.50) PLUS an additional programmatic penalty specific to this transplant: (a) the toy domain's SR HARD_PASS was measured on a graph 22x denser (mean degree 6.65 vs <1) — a documented, structurally-argued reason to expect the mechanism's core value proposition (multi-path aggregation) has little room to operate at ARC's graph scale; (b) the SAME tie bucket has already produced one clean `d=0.000` negative (symbolic-intent) diagnosed as meaning-bound, raising the prior that ANY additional structural feature (including this one) fails the same way; (c) small-n (44-66 tie questions) CV-based lambda learning is a genuine, not merely cosmetic, statistical-power risk. This is an honestly-low-but-not-zero P: the mechanism is well-argued and cheap to test (the whole cell runs in seconds on a 215-node graph), and even a clean HARD-FAIL is diagnostically valuable (see predictions above) — this is a decisive, cheap, informative test regardless of outcome, which is the right property for a design gated this honestly.

## Citations (verified count)

**14 distinct sources**, all previously verified in this program's prior SR/TEM research threads (re-cited here, not re-scanned, per the "build on don't redo" KB-check finding above) plus this session's direct filesystem/metrics verification (not a citation but load-bearing evidence):
1. Stachenfeld, Botvinick & Gershman (2017, *Nat Neurosci*) — hippocampus as predictive map / SR.
2. Dayan (1993, *Neural Computation*) — original TD-SR formalism.
3. Bono, Zannone, Pio-Lopez & Ponte Costa (2023, *eLife*) — synaptic-level SR learning rule.
4. Russek, Momennejad, Botvinick, Gershman & Daw (2017, *PLOS Comp Biol*) — SR generalization boundary.
5. Momennejad (2020, *Curr Opin Behav Sci*) — SR review, generalization-to-new-reward vs new-structure boundary.
6. Millidge (arXiv 2512.24722) — SR = resolvent = personalized PageRank equivalence.
7. Ólafsdóttir et al. (2015, *eLife*) — hippocampal replay of unexplored trajectories.
8. Dragoi & Tonegawa (2011, *Nature*) — hippocampal preplay.
9. Pfeiffer & Foster (2013, *Nature*) — goal-directed place-cell sequences ahead of the animal.
10. Whittington et al. (2020, *Cell*) — Tolman-Eichenbaum Machine, structure/content factorization.
11. Fodor & Pylyshyn (1988, *Cognition*) — systematicity/compositionality argument.
12. Mattar & Daw (2018, *Nat Neurosci*) — prioritized replay, planning.
13. Barreto et al. (2017, NeurIPS) — successor features, generalization-to-new-reward boundary.
14. "When No Paths Lead to Rome" (arXiv 2510.23532) — memorization-vs-generalization discriminator design (cited for the MM/CG honesty framing carried forward from the sibling drill).

Filesystem/metrics evidence directly verified this session (not literature, but load-bearing and re-checked off disk rather than recalled): `data/exp_grounding_multihop_sr_reachability_routing_v1/metrics.json`, `experiments/exp_grounding_multihop_sr_reachability_routing_v1.py`, `experiments/exp_grounding_gated_fusion_relation_inference_mammal_v1.py`, `hdlab/reasoner.py`, `data/exp_arc_reasoner_link_precision_tie_prune_v1/metrics.json`, `data/exp_arc_reasoner_symbolic_tiebreak_v1/metrics.json`, `experiments/exp_arc_derivation_connectivity_gate_v1.py` (`meet_connected`/`_reach`).

---

## For `hdi_exp_dev` (everything actionable is here — no separate routing/hand-off file per the no-routing-files discipline)

Build `exp_arc_reasoner_sr_gated_tiebreak_v1` per the arms/bands/mechanism spec in STEP 3 above. Order of operations:
1. Run the coverage diagnostic (dist_only 3-way classification) FIRST — cheap, report-only, settles whether a separate DEPTH-bump cell is worth queuing next.
2. Build the SR adapter over `g["fwd"]` (a few lines; do not reinvent `SRSolver`).
3. Implement the 5 arms + CV-lambda selection exactly as specified; reuse `DerivationReasoner`, `SRSolver`, and the gated-fusion cell's grid-search pattern verbatim.
4. Report bands honestly per the pre-registered guardrails; a clean `HARD_FAIL_SR_DEGENERATE_AT_THIS_SCALE` is a valid, useful, expected-and-predicted outcome — do not iterate/tune to force a pass.
