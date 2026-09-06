---
problem: reason_over_the_causal_network_multi_hop_chains_and_counterfactuals
status: SOLVED
bar: "PASSES only with ALL of: (1) A glass-box reasoner OVER the extracted causal network doing BOTH (a) MULTI-HOP chain traversal -- ultimate cause (root ancestor of an outcome), mediating cause (a node on the path between two events), chain-of-consequence (forward reachability); and (b) COUNTERFACTUAL NECESSITY by SIMULATED intervention -- remove/negate a node, re-propagate reachability along the edges, and read whether the outcome still holds. NO do-calculus, NO external LLM. Copy the Trabasso/Pearl-counterfactual COMPUTATION; SWEEP the traversal-depth / abstention thresholds. (2) Answers CI-separated over BOTH controls on MODERN non-circular gold: (a) a most-recent / adjacency floor recomputed on the same population, which MUST LOSE on the multi-hop items; and (b) the info-free SHUFFLED-EDGE twin LOSES CI-separated on both the chain and the counterfactual items. Report CI half-width + null p95; recompute each floor on the item's OWN population. A POSITIVE control the metric can move. (3) Isolates the REASONING from extraction/typing -- ablate to a 1-hop readout (and to the untyped adjacency network). (4) One-screen summary. A rigorous NEGATIVE is a FULL PASS (e.g. the counterfactual simulation is sound on constructed graphs but the reader's REAL extracted network is too sparse to support multi-hop chains: median depth ~1, so N of M multi-hop items reduce to one hop and cannot separate from adjacency; the bottleneck is the extracted network's missing edges, enumerated with counts)."
result: "The reasoner is built and SOUND, the multi-hop traversal + counterfactual intervention are LOAD-BEARING on modern gold INCLUDING DIRECTED HUMAN NARRATIVE gold, and the anticipated NEGATIVE (real network too sparse) is confirmed + built-across. (L1 constructed, n=5000 DAGs) ultimate-cause reasoner 1.000 vs adjacency 0.279 (0.000 on the multi-hop subset), reasoner-adjacency +1.000 CI[1.000,1.000], reasoner-twin +0.844 CI[0.831,0.856]; counterfactual necessity by node-removal 1.000 vs adjacency 0.482 (+0.518 CI[0.510,0.527]) vs twin 0.479 (+0.521 CI[0.513,0.529], null p95 0.011); graded-necessity ordering 1.000; general Pearl cut-and-re-simulate agrees 0.920; Halpern-Pearl ACTUAL causation handles over-determination (both over-determining causes are actual though neither is but-for necessary). (L2 WIQA modern, n=5005) refutes the prior HARD_FAILs: reason 0.5852 beats polarity-echo 0.3211 (+0.2641 CI[0.247,0.281]) + majority 0.4220; multi-hop (n=996) reason 0.2560 beats 1-hop adjacency 0.0000 (+0.2560 CI[0.229,0.283]) + twin 0.0663 (+0.190 CI[0.166,0.215]); reachability-`no_effect` 0.6491 beats the prior lexical trick 0.4938. (L3 located NEGATIVE, ROCStories n=1500) the LIVE reader's narrative network is far too sparse: 0.560 edges/story (median 0), 0.077 cross-sentence, depth median 0, only 3.2% support a >=2-hop chain. (L4 build-across) a Trabasso contiguity+plausibility densification lifts multi-hop support 3.0% -> 94.8% (depth 0.39 -> 2.78), additive/no-regress. (L5 DIRECTED HUMAN GOLD, TellMeWhy n=1765 answerable) on the NON-ADJACENT-cause subset (n=299, where the cause is not the immediately-prior sentence) the dense causal network finds the human-annotated cause 0.2375 vs the adjacency floor 0.0000 (+0.2375 CI[0.191,0.288]), the recency floor 0.0000 (+0.2375), and the shuffled-edge twin 0.1171 (+0.120 CI[0.060,0.181]) -- ALL CI-separated; and beats a lexical-overlap baseline CI-sep overall. HONEST BOUND: overall the cause is the adjacent prior sentence ~69%, so the topical densification is not globally cause-correct (dense 0.32 < adjacency 0.69) and the directed event-type gate does NOT help (0.28) -> the residual is the directed causal-knowledge / world-knowledge wall, quantified."
floor: "Multiple, recomputed per population. (L1) ADJACENCY floor (immediate-predecessor / 1-hop) = 0.279 / 0.482, and 0.000 on the multi-hop subset. (L2 WIQA) ADJACENCY 0.0000 on multi-hop; POLARITY-ECHO 0.3211; MAJORITY 0.4220; the prior lexical no_effect trick reproduced at 0.4938. (L5 TellMeWhy directed human gold) the ADJACENCY floor (cause = prior sentence) is STRONG overall (0.6880) but 0.0000 on the non-adjacent-cause subset by construction; the RECENCY floor 0.0000 on that subset; the LEXICAL-overlap floor 0.2493 overall; the shuffled-edge twin 0.1171 on the non-adjacent subset. (L3/L4) the SPARSE connective+mental network supports a >=2-hop chain in 3.0% of stories; Story Cloze (affect-dominated, wrong instrument) topical 0.4950. Each floor beaten CI-separated where a positive is claimed (L1, L2, L5-multihop); the L4 Story-Cloze arm and the L5-overall arm are located sub-negatives (NOT CI-separated over the adjacency prior) and reported as such."
controls: "(1) info-free SHUFFLED-EDGE twin LOSES CI-separated everywhere a positive is claimed: L1 ultimate-cause (r-twin +0.844) + necessity (+0.521, null p95 0.011); L2 multi-hop (+0.190); L5 TellMeWhy non-adjacent cause-ID (+0.120 CI[0.060,0.181]). (2) ADJACENCY + RECENCY floors LOSE CI-separated on the multi-hop / non-adjacent subset (L1 0.000; L2 0.0000; L5 0.0000) -- the traversal, not recency, carries the answer; and L5 shows adjacency is a STRONG overall floor (0.69) that the multi-hop positive is honestly separated from. (3) REASONING-ISOLATION: L2 gold (i,j) anchors isolate reasoning from anchoring; the 1-hop ablation isolates traversal from extraction. (4) POSITIVE control the metric moves: L1 depth>=2 where ultimate!=most-recent (adjacency 0.000, reasoner 1.000); the diamond-bypass necessity + the over-determination Halpern-Pearl case; L5 the non-adjacent-cause subset. (5) LEXICAL-overlap (L5) + TEMPORAL-only / TOPICAL (L4) isolate the causal signal from lexical/positional/plausibility-free baselines. (6) DIRECTED event-type ablation (L5 0.28 < topical 0.32) shows the class-level type gate does NOT help -- a drilled negative. (7) the leaked WIQA `dj`==answer is NEVER read. Each excludes: twin -> topology load-bearing; adjacency/recency -> multi-hop load-bearing; oracle-anchors -> reasoning not anchoring; lexical/temporal -> causal not lexical/plausibility-free."
files_changed: "experiments/_causal_reasoner.py, experiments/exp_causal_reasoner_{soundness,wiqa,narrative,densify,directed,tellmewhy,phase}_v1.py, experiments/fetch_tellmewhy_v1.py, verification/test_causal_reasoner_{soundness,wiqa,narrative,densify,tellmewhy,phase}.py, data/corpora/tellmewhy/ (fetched, pinned), notes/problems/reason_over_the_causal_network_multi_hop_chains_and_counterfactuals/{SOLVED.md,RESEARCH_brain_mechanism_and_wiqa_postmortem_2026-09-06.md}"
reverify: ".venv/Scripts/python.exe verification/test_causal_reasoner_soundness.py   # 9/9, re-derives the headline (reasoner sound + multi-hop traversal + counterfactual intervention + Halpern-Pearl actual causation load-bearing vs adjacency + twin, live). Full suite: test_causal_reasoner_wiqa.py (4/4), test_causal_reasoner_narrative.py (4/4), test_causal_reasoner_densify.py (3/3), test_causal_reasoner_tellmewhy.py (4/4 -- multi-hop cause-ID CI-sep over adjacency+recency+twin on directed human gold + cue-integration), test_causal_reasoner_phase.py (4/4 -- the phase diagram: correctness is the sole binding axis)."
---

# SOLVED -- a glass-box causal-network REASONER (multi-hop chains + counterfactual necessity), proven sound and load-bearing on modern gold, with the real-narrative bottleneck located and built-across

## What I built (brain mechanism first)
The opening move was the brain's. Trabasso & van den Broek (1985); Trabasso, van den Broek & Suh (1989): a
reader represents a narrative as a CAUSAL NETWORK and reasons over it by REACHABILITY -- the ultimate cause is
the root ancestor of an outcome, the mediating cause is a node on the path, the chain of consequence is forward
reachability, and importance/salience is network CONNECTIVITY (degree), not recency. Counterfactual necessity
("would the outcome have occurred WITHOUT the cause?") is a SIMULATED INTERVENTION -- Pearl's abduction ->
action (do(cause=absent): cut the node's incoming, set the counterfactual value) -> re-propagate -> compare
(Kahneman & Miller norm theory governs which node a reader mutates: the abnormal/foregrounded one). I copied
that computation exactly.

`experiments/_causal_reasoner.py` is the reasoner: a `CausalGraph` over event nodes with signed, graded-necessity
cause->effect edges, and the readouts
- `ultimate_cause` (root ancestor, connectivity-ranked), `mediating_cause` / `necessary_mediators` (nodes on the
  path / on EVERY path), `descendants` (chain of consequence);
- `is_necessary` (remove the node, re-propagate reachability, check the outcome loses all remaining exogenous
  root support) and the general `intervene_and_compare` (cut-incoming + set counterfactual value + re-propagate +
  compare -- Pearl's twin-network);
- `graded_necessity` (max-product path weight -- the PINNED Trabasso/van den Broek/Suh graded rep, of which the
  discrete boolean is a lossy read-out);
- `signed_effect` (more/less/no_effect by signed forward propagation; `no_effect` == non-reachability);
- `most_mutable_cause` (Kahneman-Miller node selection);
- the info-free `shuffled` twin.

It **REUSES the traversal pattern proven in `hdlab.goal_hierarchy_graph`** (ancestors / root / connectivity +
the shuffled-EDGE twin), lifted from the GOAL graph onto CAUSAL edges -- the same walk, one relation renamed.
PINNED: the Trabasso reachability computation + the Pearl intervention. OUR-INVENTION-UNDER-TEST (swept): the
question->query mapping, the intervention rule, the plausibility/threshold parameters.

## What I measured (four layers; one-screen summary per the bar)
| layer | question | headline | controls |
|---|---|---|---|
| **L1 constructed (n=5000 DAGs)** | is the reasoner SOUND and the traversal LOAD-BEARING? | ultimate-cause **1.000** vs adjacency 0.279 (**0.000** on multi-hop); necessity **1.000** vs adjacency 0.482 / twin 0.479; graded ordering 1.000; Pearl agrees 0.920 | reasoner-adj **+1.000** CI[1.0,1.0] (multihop); reasoner-twin +0.844; necessity r-adj +0.518, r-twin +0.521 (null p95 0.011) -- all CI-sep |
| **L2 WIQA modern gold (n=5005)** | does the BRAIN-FOUNDATIONAL reasoner refute the prior HARD_FAILs? | reason 0.5852 vs polarity-echo 0.3211 / majority 0.4220; **multi-hop** reason 0.256 vs adjacency **0.000** / twin 0.066; `no_effect`=reachability 0.649 vs prior lexical trick 0.494 | reason-adj +0.256 CI[0.229,0.283]; reason-twin +0.190 CI[0.166,0.215]; reason-polarity +0.264 CI[0.247,0.281] -- all CI-sep |
| **L3 ROCStories (n=1500)** | is the reader's REAL narrative network dense enough? | **LOCATED NEGATIVE**: 0.560 edges/story (median 0), 0.077 cross-sentence, longest-chain depth median 0, **only 3.2%** support a >=2-hop chain | enumerated with counts + method breakdown (mental_bridge 574 / connective 269; zero cross-sentence bridge) |
| **L4 densify + Story Cloze** | can an upstream brain-foundational fix build across? | density FIXED **3.0% -> 94.8%** multi-hop support (depth 0.39 -> 2.78), additive; residual wall diagnosed | dense NOT CI-sep over sparse/temporal/topical/twin on Story Cloze (all ~0.5) -> the plausibility signal is topical + Story Cloze is affect-dominated |
| **L5 TellMeWhy (DIRECTED human gold)** | does the reasoner find the true cause on directed narrative gold? | on NON-ADJACENT causes (n=299) dense **0.2375** finds the human cause where adjacency/recency score **0.000**; overall adjacency-dominated (dense 0.31 < adjacency 0.69) | dense-adjacency **+0.2375** CI[0.191,0.288]; dense-recency +0.2375; dense-twin +0.120 CI[0.060,0.181]; dense-lexical +0.065 CI[0.036,0.095] -- multi-hop CI-sep over ALL |

### The upgrades (owner: "implement all real upgrades, drill every wall")
- **U1 -- HALPERN-PEARL ACTUAL CAUSATION (built, sound).** Simple but-for necessity wrongly says NEITHER cause
  matters under OVER-DETERMINATION (two rocks each shatter the bottle). `is_actual_cause` adds the witness-contingency
  test (Halpern & Pearl 2005; the psychology of causal SELECTION, Kahneman & Miller): both over-determining causes
  are ACTUAL though neither is but-for necessary; a non-reaching node is neither; necessity implies actual-causation.
  Proven on constructed graphs (witness C0e).
- **U2 -- DIRECTED event-type densification (DRILLED WALL, honest negative).** Replacing the topical associative
  gate with a DIRECTED causal-type transition (REUSE `hdlab.event_type` MENTAL_TRIGGER->MENTAL_OUTCOME + Talmy
  force dynamics) does NOT add directional signal: on ROCStories the forward-vs-reversed edge asymmetry is null
  (directed fwd 5.05 vs rev 5.57), and on TellMeWhy the directed gate is WORSE than topical (0.28 vs 0.32). WHY
  (drilled): the ontology is dominated by the SYMMETRIC PHYSICAL->PHYSICAL transition (most narrative events are
  physical motion/contact/change), so class-level event types are too coarse to encode causal DIRECTION -- the
  directed signal needs verb-pair causal knowledge (the world-knowledge wall, from a second angle).
- **U3 -- DIRECTED HUMAN GOLD acquired + validated (L5 above).** Acquired TellMeWhy (pinned) as the RIGHT instrument
  the affect-dominated Story Cloze pointed to, and it delivers the deliverable's core positive on real narrative:
  multi-hop cause identification is LOAD-BEARING (CI-sep over adjacency/recency/twin) on the non-adjacent causes.
- **U4 -- KAHNEMAN-MILLER node selection (built + tested; wiring specified).** `most_mutable_cause` + `mark_abnormal`
  implement norm theory (mutate the abnormal/foregrounded node); tested (the marked node is selected). The wiring to
  the reader's SURPRISAL register (`predict_surprisal` -> mark the norm-violating event abnormal) is the specified
  integration (no counterfactual-selection gold exists on disk to validate it end-to-end -- enumerated).
- **U5 -- CUE INTEGRATION (recency prior REFINED by the causal network; a real +0.14 readout lift).** A reader uses
  BOTH recency (narrative defaults to cause-then-effect, so the prior sentence is the causal PRIOR) and the causal
  network; the network should REFINE the prior, not replace it. `predict_cause_integrated` defaults to the adjacency
  prior and overrides to a non-adjacent sentence only on a CONFIDENT causal link. On TellMeWhy this lifts the readout
  0.3140 -> 0.4567 (+0.1427 CI[0.119,0.166]) and stays CI-sep load-bearing on the non-adjacent subset (+0.191); a
  threshold sweep shows it CONVERGES to the adjacency prior (0.69) from below -- it cannot BEAT it, because the topical
  edges are not accurate enough to safely override recency. The ceiling IS the world-knowledge wall (a 4th confirmation).
- **U6 -- THE PHASE DIAGRAM (owner insight: density is a free knob).** Separating the two axes the earlier layers
  conflated -- non-adjacency r (how much multi-hop causal structure exists; a DENSITY/topology knob, freely dialable)
  and correctness c (fraction of TRUE edges the extraction captures; the world-knowledge axis) -- and mapping the
  reasoner's cause-ID advantage over adjacency across the grid (`exp_causal_reasoner_phase_v1.py`, witness P1-P4):
    * at r=0 (all causes adjacent) the recency floor is UNBEATABLE (advantage <=0) regardless of c -- the reasoner
      earns nothing when causes are adjacent (the TellMeWhy overall regime);
    * on the NON-ADJACENT subset the reasoner's accuracy EQUALS c and is INDEPENDENT of r (r=0.2 and r=0.8 rows match)
      -- so density/topology ALONE does nothing; **CORRECTNESS is the sole binding axis**;
    * the advantage rises monotonically to **+0.81 at (high r, c=1)** -- the brain's operating point.
  This COLLAPSES the whole remaining problem to one number: the reasoner is proven to deliver exactly c on the cases
  that need it, density is free, so the entire residual is edge correctness c = the directed causal-knowledge gate.
  PLACEMENT on the diagram: current reader = sparse + low c (starved); my densification = high density + low c (the
  low-c column, reproducing TellMeWhy's ~0.24); the target = high r + c->1.

## The core finding, plainly: the prior WIQA HARD_FAILs were a NON-brain-foundational implementation, not a ceiling
A research drill (mechanism-level post-mortem, `notes/problems/<slug>/RESEARCH_brain_mechanism_and_wiqa_postmortem_2026-09-06.md`)
established that all four prior WIQA cells (loop_v1/v2, oracle_structure, learned_signs) propagated SIGNS over the
LINEAR paragraph step order (i->i+1) with negation-word edge signs, **never built an event-node causal network,
never used reachability, modeled `no_effect` as a chance-level lexical trick (0.4997), and never did a simulated
intervention**. The "flawed even with gold anchors" HARD_FAIL only replaced node POSITIONS (i,j), never the
topology, edge signs, or reachability. Supplying the three missing brain-foundational components -- (1) an
event-node network with reachability, (2) `no_effect` as non-reachability/failed-necessity, (3) counterfactual by
simulated intervention -- the reasoner cleanly beats the baselines the prior loop LOST to (reason_oracle 0.585 vs
majority 0.422; the prior loop_oracle was 0.442, BELOW majority 0.506). The multi-hop traversal is load-bearing
(adjacency 0.000, twin lose CI-sep), and reachability-`no_effect` beats the lexical trick (0.649 vs 0.494).

## What I did NOT establish (and would withdraw first if wrong)
1. **A GLOBAL narrative cause-ID win.** The multi-hop positive on directed human gold (L5) is confined to the
   NON-ADJACENT-cause subset (~17% of why-questions); OVERALL the cause is the adjacent prior sentence ~69% of the
   time, and the topical densification (dense 0.31) does NOT beat that adjacency prior globally. Withdraw any
   implication of a global cause-ID win first. What is proven is (a) the reasoner is sound + load-bearing on modern
   gold, and (b) on the subset where a position floor STRUCTURALLY fails (non-adjacent causes) the multi-hop
   traversal is the only thing that works, CI-separated over adjacency/recency/twin -- a real but narrow positive.
2. **That the densified edges are CAUSALLY CORRECT.** The associative-relatedness plausibility signal is TOPICAL,
   not directed-causal (Story Cloze non-tie accuracy 0.534 = chance -- the signal fires but does not track
   correctness). And Story Cloze is AFFECT-dominated (a topical baseline is also chance, 0.522), so it is the wrong
   instrument to validate causal-chain reasoning. The density fix is real; the correctness of narrative causal edges
   is NOT validated and needs a directed causal-knowledge prior (see NEXT STEPS).
3. **WIQA as a strong multi-hop-reasoning instrument.** Its causal structure is a monotone LINEAR process chain, so
   `no_effect` reduces to grounding (grounding 0.719 > reachability 0.649) and the multi-hop SIGN (0.256, low) is an
   edge-sign EXTRACTION problem (world-knowledge about process semantics), not a reasoning-approach flaw. It is
   procedural, the brief's non-target genre. I use it to isolate the REASONING; I do not claim a WIQA capability win.

## KEY REALIZATIONS (the enabling moves)
1. **`no_effect` is REACHABILITY, not a lexical polarity absence.** The single move that separated the reasoner
   from every prior WIQA attempt: model "the perturbation has no effect" as "the perturbation node does not reach
   the outcome in the network" (a failed necessity), not "the outcome clause has no polarity word." The prior
   lexical trick scored 0.4997 (chance) on exactly this class; reachability scores 0.649.
2. **The prior HARD_FAIL never tested the brain's mechanism.** Reading the prior cells at the mechanism level (a
   linear sign-multiply with negation-word signs) showed the "inference approach is flawed even with gold anchors"
   verdict was confounded -- gold anchors fixed WHERE, never the topology/edge-signs/reachability. The owner's steer
   ("don't trust a hard fail; it may lack an upstream brain-foundational component") was exactly right.
3. **Adjacency scores 0.000 on multi-hop by construction, and that IS the proof.** The immediate predecessor is
   never the root when depth>=2, so the 1-hop floor cannot get the ultimate cause -- the cleanest possible
   demonstration that the multi-hop traversal (not recency) is load-bearing.
4. **The sparsity is an UPSTREAM extraction gap, and it is buildable.** The reader links only on explicit
   connectives + within-sentence mental bridges; real narrative causation is UNSTATED. Inferring the Trabasso
   chain from contiguity+plausibility moved multi-hop support 3% -> 95% -- turning "the reasoner has nothing to
   traverse" into "the reasoner has chains, and the open question is now their CORRECTNESS," which is a different
   (world-knowledge) problem.
5. **Story Cloze is an affect instrument, not a causal-chain instrument.** Diagnosing that a topical baseline is
   ALSO chance (0.52) separated "our densification is wrong" from "this gold does not measure causal-chain depth" --
   the latter is true, and it redirects the validation to directed causal QA gold.
6. **Split the metric by whether a position floor CAN work.** On directed human gold the cause is the adjacent
   sentence ~69% of the time, which drowns the reasoning signal in the aggregate. Splitting on non-adjacent-cause
   (where adjacency scores 0.000 by construction) surfaced the real, CI-separated positive: the multi-hop traversal
   is the ONLY method that works exactly where the shortcut structurally fails. The aggregate hid the capability;
   the right subset revealed it -- the same "recompute the floor on the item's own population" discipline as a
   population split.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec.2b)
- **NEW organ: a glass-box causal-network REASONER over the situation model** (the first INFERENCE organ over the
  causal network). PINNED computation: Trabasso reachability (ultimate/mediating/chain) + Pearl simulated
  intervention (counterfactual necessity) + graded necessity (Trabasso/vdB/Suh). Proven SOUND on constructed graphs
  and LOAD-BEARING on modern gold (WIQA multi-hop: adjacency 0.000, twin lose CI-sep). Reuses the
  `goal_hierarchy_graph` traversal pattern. `experiments/_causal_reasoner.py`.
- **The audit's PINNED-to-BUILD "covariation-based causal-GRAPH inference (Trabasso/van den Broek)" (:854-856) is
  now MEASURED as the binding constraint for narrative causal reasoning.** The reasoner is not the bottleneck; the
  reader's extracted narrative causal network is (median chain depth 0; 3.2% of ROCStories support a >=2-hop chain).
  A contiguity+plausibility densification fixes the DENSITY (3% -> 95%); the CORRECTNESS of the inferred edges is
  bounded by the directed causal-knowledge / identifiability wall the audit already flags (:1036-1052 route-closed
  for the discourse edge-TYPER; here it recurs for edge EXISTENCE inference). This is a distinct, higher-fidelity
  successor to build, not a ceiling.
- **The prior WIQA causal-chain HARD_FAILs (2026-08-10) are a NON-brain-foundational implementation, not a
  ceiling** -- they lacked an event-node network, reachability, reachability-`no_effect`, and any intervention.
  The brain-foundational reasoner beats the baselines they lost to on the same modern gold.

## Adjacent components -- capability / limitation / opportunity / brain-foundational status (owner push)
1. **The causal-network EXTRACTION (`situation_reader._read_causation`) -- the binding upstream constraint.**
   *Capability:* connective + within-sentence mental-bridge links (landed). *Limitation:* misses ALL unstated
   cross-sentence causation -- 0.077 cross-sentence edges/story on ROCStories; the dominant narrative case.
   *Brain status:* the connective path is faithful-but-narrow; the INFERENCE of unstated links (Trabasso's actual
   claim) is MISSING. *Opportunity:* the densification prototyped here, upgraded with a directed causal-knowledge
   prior -- the single highest-leverage narrative-reasoning lift.
2. **The integrated corpus-level causal-knowledge organ (`narrative_causal_graph...`, ATOMIC/CSKG on disk).**
   *Capability:* directed causal commonsense across documents. *Limitation:* not wired as the reader's within-document
   plausibility prior (a wiring/reuse task, NOT a rebuild -- the brief fences rebuilding it). *Opportunity:* it is
   the brain-foundational plausibility signal the associative store lacks (topical vs directed-causal). REUSE it to
   gate the densification's edge existence.
3. **The counterfactual-NECESSITY read-out vs affect/regret (vmPFC).** *Capability:* graph node-removal + Pearl
   re-simulation (built, sound). *Limitation:* no coupling to the affect register -- Story Cloze shows narrative
   coherence is affect-driven. *Opportunity:* couple counterfactual necessity to the affect/regret organs (Coricelli
   vmPFC regret-magnitude) -- a second, affect-grounded consumer of the reasoner.
4. **The event-node / edge-SIGN extraction (WIQA sign wall).** *Limitation:* edge sign from negation-words is weak
   (multi-hop sign 0.256). *Brain status:* the sign is force-dynamic/world-knowledge (the force_dynamics_typer's
   measured bound). *Opportunity:* subsumed by directed causal-knowledge grounding.

## What strategy would change in hdlab/ (Q111 -- I propose, do not land)
1. **Promote `experiments/_causal_reasoner.py` as `hdlab/causal_reasoner.py`** -- a glass-box reasoner consuming
   `sm.causal_links` (build a `CausalGraph` from the CausalLinks) and exposing `ultimate_cause` / `mediating_cause` /
   `chain_of_consequence` / `is_necessary` / `counterfactual` / `graded_necessity`. Wire it to the QA read-out's
   why/causal + a new "what-if" question type. It is ADDITIVE and reuses the `goal_hierarchy_graph` pattern.
2. **Add an ADDITIVE densified-inference layer to `_read_causation`** -- populate a NEW field `sm.inferred_causal_links`
   (do NOT touch `sm.causal_links`, so connective causal QA / coref / events stay byte-identical -- no downstream
   regress by construction) from the Trabasso contiguity+plausibility densification, with the PLAUSIBILITY gated by
   the integrated corpus-level causal-knowledge organ (adjacent #2), not the topical associative store. Land only
   once its edge CORRECTNESS is validated on directed causal QA gold (NEXT STEPS) -- default-off until then.
3. Do NOT land the associative-relatedness densification as-is (topical, unvalidated for correctness). Do NOT
   rebuild do-calculus / the corpus causal-graph organ (fenced).

## TLDR (plain English)
A good reader doesn't just notice that one thing caused another -- they can trace a story's chain of causes back to
the root ("what ultimately caused this?"), name the middle link, and imagine "if that hadn't happened, would the
ending still follow?". I built that reasoning as transparent graph-walking, and proved it is exactly correct on
thousands of test maps -- where a "just look at the nearest event" shortcut gets the ultimate cause right 0% of the
time on anything more than one step away, and a scrambled-map control fails too. On a modern real dataset (WIQA),
this brain-faithful reasoner cleanly beats the baselines that an earlier attempt here had FAILED to beat -- because
that earlier attempt wasn't built the brain's way (it never built a real cause-map, never checked "does this even
reach the outcome," and guessed "no effect" from a word trick). The honest catch, which the brief predicted: when I
run our actual reader on real modern stories, it barely extracts any causal links at all (most stories get a map with
zero connections), so the reasoner has almost nothing to walk. That is an UPSTREAM problem -- the reader doesn't infer
the unstated causal links a person fills in automatically. I prototyped that inference and it fixes the emptiness
(stories with a real multi-step chain go from 3% to 95%). To grade whether the reasoner finds the RIGHT cause, I
downloaded a dataset of real people's "why did this happen?" answers about short stories (TellMeWhy). The honest result:
usually the cause is just the sentence right before, and a dumb "it's the previous sentence" rule is hard to beat there.
BUT for the ~1-in-6 questions where the cause is NOT the adjacent sentence -- the exact case that needs real reasoning --
our causal-map reasoner is the ONLY method that finds it (the "previous sentence" rule scores zero there by definition,
and a scrambled-map control loses too). Getting MORE of those right needs real-world knowledge of what causes what,
which our no-outside-AI rule makes a separate known-hard problem. Net: the reasoning engine is done and proven, it earns
its keep exactly where simple shortcuts fail, and the remaining bottleneck is real-world causal knowledge, cleanly named.

## QUESTIONS
None blocking. One judgement call for the strategy session: the brief's blessed NEGATIVE was "the reasoner is sound on
constructed graphs but the real network is too sparse" -- I met that AND showed the reasoner load-bearing on modern
gold (WIQA) AND prototyped the density fix, so I filed status SOLVED rather than PARTIAL. If you prefer the label
tied strictly to an end-to-end narrative accuracy win, this is a PARTIAL; the science is identical either way.

## NEXT STEPS
1. **Wire the integrated corpus-level causal-knowledge organ (ATOMIC/CSKG on disk) as the densification's PLAUSIBILITY
   gate** (adjacent #2) -- the DIRECTED causal prior that raises edge CORRECTNESS on the non-adjacent causes (dense
   still misses ~76% of them on TellMeWhy). This is the single highest-leverage lift and the drilled residual wall;
   the topical associative signal and the class-level event-type gate BOTH proved too coarse (U2). REUSE, do not rebuild.
   The `is_ques_answerable=Not-Answerable` TellMeWhy subset is the labelled world-knowledge population to target.
2. **Land the reasoner (hdlab change #1)** + wire it to the QA why/causal + a "what-if" question type -- it is proven
   sound + load-bearing (constructed, WIQA, TellMeWhy multi-hop) and is a pure REUSE of `sm.causal_links` + the
   goal-graph traversal pattern.
3. **Wire the reader's SURPRISAL register -> Kahneman-Miller node selection** (U4) -- the norm-violating (high-surprisal)
   event is the one a reader mutates in a counterfactual; the reasoner side (`most_mutable_cause`) is built + tested.
4. **Couple counterfactual necessity to the affect/regret organs** (adjacent #3) -- narrative coherence is affect-driven
   (Story Cloze); the reasoner's necessity read-out is the substrate for a vmPFC-style regret/blame consumer.
