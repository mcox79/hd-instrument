---
problem: reason_over_the_causal_network_multi_hop_chains_and_counterfactuals
status: SOLVED
bar: "PASSES only with ALL of: (1) A glass-box reasoner OVER the extracted causal network doing BOTH (a) MULTI-HOP chain traversal -- ultimate cause (root ancestor of an outcome), mediating cause (a node on the path between two events), chain-of-consequence (forward reachability); and (b) COUNTERFACTUAL NECESSITY by SIMULATED intervention -- remove/negate a node, re-propagate reachability along the edges, and read whether the outcome still holds. NO do-calculus, NO external LLM. Copy the Trabasso/Pearl-counterfactual COMPUTATION; SWEEP the traversal-depth / abstention thresholds. (2) Answers CI-separated over BOTH controls on MODERN non-circular gold: (a) a most-recent / adjacency floor recomputed on the same population, which MUST LOSE on the multi-hop items; and (b) the info-free SHUFFLED-EDGE twin LOSES CI-separated on both the chain and the counterfactual items. Report CI half-width + null p95; recompute each floor on the item's OWN population. A POSITIVE control the metric can move. (3) Isolates the REASONING from extraction/typing -- ablate to a 1-hop readout (and to the untyped adjacency network). (4) One-screen summary. A rigorous NEGATIVE is a FULL PASS (e.g. the counterfactual simulation is sound on constructed graphs but the reader's REAL extracted network is too sparse to support multi-hop chains: median depth ~1, so N of M multi-hop items reduce to one hop and cannot separate from adjacency; the bottleneck is the extracted network's missing edges, enumerated with counts)."
result: "The reasoner is built and SOUND, the multi-hop traversal + counterfactual intervention are LOAD-BEARING on modern gold, AND the anticipated NEGATIVE is confirmed and built-across. (L1 constructed, n=5000 DAGs) ultimate-cause reasoner 1.000 vs adjacency floor 0.279 (0.000 on the multi-hop subset -- the immediate predecessor is never the root when depth>=2), reasoner-adjacency +1.000 CI[1.000,1.000], reasoner-twin +0.844 CI[0.831,0.856]; counterfactual necessity by node-removal 1.000 vs adjacency 0.482 (+0.518 CI[0.510,0.527]) vs shuffled-edge twin 0.479 (+0.521 CI[0.513,0.529], null p95 0.011); graded-necessity ordering 1.000; general Pearl cut-and-re-simulate agrees with node-removal 0.920. (L2 MODERN gold WIQA, n=5005) the brain-foundational reasoner REFUTES the prior WIQA HARD_FAILs: reason_oracle 0.5852 beats polarity-echo 0.3211 (+0.2641 CI[0.247,0.281]) and majority 0.4220; on the multi-hop subset (|j-i|>=2, n=996) reason 0.2560 beats the 1-hop adjacency floor 0.0000 (+0.2560 CI[0.229,0.283]) and the shuffled-edge twin 0.0663 (+0.190 CI[0.166,0.215]); `no_effect` modeled as REACHABILITY 0.6491 balanced-acc beats the prior chance-level lexical trick 0.4938. (L3 located NEGATIVE, ROCStories n=1500) the LIVE reader's extracted narrative causal network is far too sparse: mean 0.560 edges/story (median 0), 0.077 cross-sentence edges/story, longest-chain depth median 0, only 3.2% of stories support ANY >=2-hop chain. (L4 build-across) a Trabasso contiguity+plausibility densification lifts multi-hop-chain support from 3.0% -> 94.8% (dense depth mean 2.78 vs sparse 0.39), additive/no-regress; residual wall diagnosed to mechanism."
floor: "Multiple, recomputed per population. (L1) most-recent/ADJACENCY floor (immediate-predecessor for ultimate cause; 1-hop for necessity) = 0.279 / 0.482, and 0.000 on the multi-hop ultimate-cause subset. (L2 WIQA) the ADJACENCY floor 0.0000 on the multi-hop subset; the prior POLARITY-ECHO baseline the loop barely beat = 0.3211; MAJORITY (no_effect) = 0.4220; the prior lexical no_effect trick reproduced at 0.4938 balanced-acc. (L3/L4) the SPARSE connective+mental network (the current reader) supports a >=2-hop chain in 3.0% of stories; the TEMPORAL-only densification 0.4900 and TOPICAL overlap 0.4950 on Story Cloze. Each floor beaten CI-separated where a positive is claimed (L1, L2); the L4 Story-Cloze arm is a located sub-negative (NOT CI-separated) and is reported as such."
controls: "(1) info-free SHUFFLED-EDGE twin (same nodes + edge count, rewired acyclic) LOSES CI-separated everywhere a positive is claimed: L1 ultimate-cause (reasoner-twin +0.844) + necessity (+0.521, null p95 0.011); L2 multi-hop (+0.190). (2) ADJACENCY / 1-hop floor LOSES CI-separated on the multi-hop subset (L1 0.000; L2 0.0000) -- proving the traversal, not recency, carries the answer. (3) REASONING-ISOLATION: L2 reason_oracle uses gold (i,j) anchors (isolates reasoning from anchoring); the 1-hop adjacency ablation over the SAME network isolates traversal from extraction. (4) POSITIVE control the metric moves: L1 multi-hop items (depth>=2) where ultimate!=most-recent -- adjacency 0.000, reasoner 1.000; the diamond-bypass necessity case (a is NOT necessary, the sole root IS). (5) TEMPORAL-only + TOPICAL-overlap baselines (L4) isolate the plausibility gate + a non-causal lexical signal. (6) the leaked WIQA `dj`==answer field is NEVER read (documented). Each excludes: twin -> topology is load-bearing; adjacency -> multi-hop is load-bearing; oracle-anchors -> reasoning not anchoring; temporal/topical -> plausibility not mere edge-adding / not lexical overlap."
files_changed: "experiments/_causal_reasoner.py, experiments/exp_causal_reasoner_soundness_v1.py, experiments/exp_causal_reasoner_wiqa_v1.py, experiments/exp_causal_reasoner_narrative_v1.py, experiments/exp_causal_reasoner_densify_v1.py, verification/test_causal_reasoner_soundness.py, verification/test_causal_reasoner_wiqa.py, verification/test_causal_reasoner_narrative.py, verification/test_causal_reasoner_densify.py, notes/problems/reason_over_the_causal_network_multi_hop_chains_and_counterfactuals/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_causal_reasoner_soundness.py   # 8/8, re-derives the headline (reasoner sound + multi-hop traversal + counterfactual intervention load-bearing vs adjacency + twin, live). Full suite: also test_causal_reasoner_wiqa.py (4/4), test_causal_reasoner_narrative.py (4/4), test_causal_reasoner_densify.py (3/3)."
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
1. **A narrative multi-hop / counterfactual ACCURACY win end-to-end.** The reasoner is sound (L1) and load-bearing on
   modern gold (L2), but on REAL narrative the reader's extracted network is too sparse to feed it (L3), and the
   L4 densification, while it fixes DENSITY decisively, does NOT lift Story-Cloze reasoning CI-separated. Withdraw
   any implication of an end-to-end narrative reasoning accuracy win first. What is proven is the reasoner's
   soundness + the traversal's load-bearingness on modern gold, and the located, enumerated bottleneck.
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
(stories with a real multi-step chain go from 3% to 95%). Whether those inferred links are the RIGHT ones still needs
real-world causal knowledge (which our no-outside-AI rule makes a separate, known-hard problem), and the coherence
test I tried (Story Cloze) turns out to be decided by emotion/expectation, not by cause-chains, so it can't grade this.
Net: the reasoning engine is done and proven; the bottleneck is now clearly the reader's thin causal map, and I showed
the path to fill it.

## QUESTIONS
None blocking. One judgement call for the strategy session: the brief's blessed NEGATIVE was "the reasoner is sound on
constructed graphs but the real network is too sparse" -- I met that AND showed the reasoner load-bearing on modern
gold (WIQA) AND prototyped the density fix, so I filed status SOLVED rather than PARTIAL. If you prefer the label
tied strictly to an end-to-end narrative accuracy win, this is a PARTIAL; the science is identical either way.

## NEXT STEPS
1. **Wire the integrated corpus-level causal-knowledge organ (ATOMIC/CSKG) as the densification's PLAUSIBILITY gate**
   (adjacent #2) -- replace the topical associative signal with a DIRECTED causal prior; this is the brain-foundational
   upgrade the Story-Cloze null points at. REUSE, do not rebuild.
2. **Acquire a DIRECTED narrative causal QA gold** (GLUCOSE / TellMeWhy over ROCStories -- modern, pre-authorized) --
   the right instrument to validate the densified edges' CORRECTNESS and the reasoner end-to-end, since Story Cloze is
   affect-dominated.
3. **Land the reasoner (hdlab change #1)** and wire it to the QA why/causal + a "what-if" question type -- the reasoner
   is proven sound + load-bearing and is a pure REUSE of `sm.causal_links` + the goal-graph traversal pattern.
4. **Couple counterfactual necessity to the affect/regret organs** (adjacent #3) -- narrative coherence is affect-driven;
   the reasoner's necessity read-out is the substrate for a vmPFC-style regret/blame consumer.
