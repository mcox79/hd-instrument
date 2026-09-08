# Multi-step / all-tier priors drill + options evaluation (owner: "attack with research + drilling priors first, then evaluate options"; "we definitely showed multihop successes clearly"; "negatives might be false — brain-foundational components fail if upstream isn't correct; strive for 100% brain-foundational")

**problem:** build_the_generative_result_state_world_model | **date:** 2026-09-07 | **method:** 4 parallel
disk deep-reads (multi-step generation/planning; scripts/chains/schema; the multihop SUCCESSES; the
other-tier priors) + `experiment_index`/`substrate_map` queries. Every number below is on disk.

## The one finding everything converges on (with the false-negative lens applied)
**The multi-step MECHANISM is proven brain-foundational and reusable; the prior "negatives" are FALSE
NEGATIVES caused by a non-brain-foundational UPSTREAM. The bottleneck is EDGE-CORRECTNESS c, not the
reasoning engine.** The decisive number is the causal reasoner's U6 phase diagram
(`reason_over_the_causal_network.../SOLVED.md:78-90`): on real narrative the multi-hop advantage over the
position floor **EQUALS edge-correctness c and is INDEPENDENT of graph density**, rising to **+0.81 at c→1**.
Every demonstrated multihop win ran on a CLEAN/CURATED graph; every real-prose miss traces to the edges
extracted from prose being wrong. So the lever is a 100%-brain-foundational GENERATIVE directed-edge
generator upstream, feeding a proven reachability engine — faithful ALL the way up (coref → meaning channel →
result-states), because the engine is only ever as correct as c.

### The prior negatives, re-classified (owner's lens)
- **Successor representation (D7) "lost 0/24, degrades with scale"** — FALSE NEGATIVE. SR is brain-PINNED
  (Dayan/Stachenfeld/Momennejad, M=(I−γP)⁻¹). It was fed **bag-of-lemma transitions** = a co-occurrence
  counter, which loses to counting. The SAME SR/PPR resolvent **HARD_PASSED** when fed **typed relations +
  goal-conditioning** (`exp_grounding_multihop_sr_reachability_routing_v1` = HARD_PASS_CG_SR_REACHABILITY,
  reach@2 0.434 = 0.87× oracle). The mechanism is fine; the upstream state representation was wrong.
- **Generative replay traversal "43%, ~7pts short"** — FALSE NEGATIVE. Mechanism sound (content-dependence
  fired, held-out replicated, no [n,n] oracle matrix); it fell short traversing the coverage-bound/topical
  CSKG graph. Fix the graph (directed generated edges) → re-openable.
- **GEK "directionless / the binding constraint"** — the STORE is co-occurrence (wrong upstream), not the
  forward-projection MECHANISM. It scores "spill the milk" ≥ "buy the milk" for a milk-goal. A directed
  result-state transition store makes the same projection work.
- **Our own full-population tie** — upstream mismatch: the single-step forward model and the multiplicative
  gate were wrong upstream *for each other*; fixing BOTH (the top-down stack) already lifted GOAL 0.380→0.467.

## The DEMONSTRATED multihop successes (owner: "shown clearly") — reusable engines, proven correct
| success | file | what it proves | on |
|---|---|---|---|
| SR/PPR resolvent (goal-conditioned reachability) | `exp_grounding_multihop_sr_reachability_routing_v1` | closed-form "is the goal reachable, chaining forward" M=(I−γT)⁻¹; reach@2 0.434, 0.87× oracle; fixed 2 prior negatives | constructed typed KG |
| causal reasoner (reachability + cut-&-re-propagate counterfactual) | `experiments/_causal_reasoner.py` | ultimate-cause 1.000, necessity 1.000 (Pearl); the ONLY method finding the human cause where position=0.000 | 5000 DAGs; TellMeWhy non-adj (17% subset, ~0.24) |
| U8 generative simulator (force+affect+event-type) | `exp_causal_reasoner_simulate_v1` | first to beat topical on REAL narrative, LLM-free (+0.030 CI-sep); SIMULATION > RETRIEVAL > topical | TellMeWhy n=299 |
| STRIPS forward-chainer (substrate-native) | `exp_stretch2_3_planning_strips_v2_...` | forward-chain to goal, bit-identical to symbolic BFS, goal-honest | synthetic STRIPS |
| goal→subgoal hierarchy graph | `hdlab/goal_hierarchy_graph.py` (wired default-on) | multi-hop why-chains 1.000, reinstatement 1.000 | 30-item battery; real-prose sparse |
| community-routing / gated-re-query micro-loop | `exp_glass_box_micro_loop_conceptnet_multihop_SCALE_v1` | ConceptNet 2-hop 0.848, re-query lift +0.383; scale-invariant routing | real ConceptNet |
| situation-conditioned means-end attachment | `exp_contextual_goal_attachment_modern_v1` (wired default-on) | which goal an action serves: K1 0.700 vs twin 0.483 | REAL modern UD-EWT n=797 |

Common thread across the WINS: **typed relations + goal-conditioning + content-sensitivity + deferred
commitment**. The LOSSES throw these away (lemma bags, topical co-occurrence, coverage-bound KB).

## Reusable inventory per loss tier (what's landed, brain-faithful, reuse verdict)
### Tier 1 — forward-model DEPTH (multi-step, +0.148; DEEP_MULTISTEP 51%)
- REUSE the proven reachability engines above. The crux (unbuilt) is the GENERATIVE directed-edge upstream:
  deepen U8 from class-level to a content-sensitive result-state rollout over COREF-RESOLVED participants,
  emitting directed cause/enable/result-state edges (not retrieval, not co-occurrence).
### Tier 2 — cue INTEGRATION / selection (~25%)
- **`hdlab/graded_competition.py` (LANDED, brain-PINNED)** — additive `net_activation` (Lewis-Vasishth) →
  `softmax` IS the Bayesian/FLMP posterior (McClelland-Rumelhart / Competition Model). REUSE VERBATIM as the
  shared decision layer, fed per-cue supports with learned Competition-Model validities.
- KNOWN failure modes (do-not): `normalized_recurrence` settling is MONOTONE (winner=argmax net → no accuracy
  gain, only the distribution); Kintsch uniform-inhibition settling proven NO-OP (needs signed pairwise
  coherence). Our C1 prototype already uses the additive combine (oracle 0.441→0.504; GOAL 0.467).
### Tier 3 — implicit-goal / ToM inference (~11%)
- Marked-goal detection LANDED (`goal_register`, 0.89). ToM machinery LANDED: `belief_partition` (false-belief
  1.000 oracle), `_tom_chain` (forward planner belief×goal→action, BigToM FB +0.871), `tom_inverse` (inverts
  to BELIEF). **GAP: no landed inverse-planning-to-GOAL organ** (`implicit_investment_goals` is a lexicon
  heuristic). BUILD: run `_tom_chain` in INVERSE solving for the goal, with the result-state achievement check
  as the likelihood.
### Tier 4 — the OTHER causal engines (physics/mental/affect, +0.332, non-goal 64%)
- PHYSICS: `force_dynamics_typer` LANDED, strong (typing 0.929) but a TYPER not a generator → add a physical
  result-state emitter (compose with `world_state_register`) + achievement gate. Closest to done.
- MENTAL: `event_type` is only a classifier → do NOT rebuild; the mental means-end check IS `_tom_chain`.
- AFFECT: `occ_appraisal` LANDED — already the forward directed affect achievement check (EVENT×GOAL→emotion,
  OCC) → just wire its output as a causal-plausibility boost, not an emotion read-out.

## The 100%-brain-foundational full-stack chain (every component + its upstream)
```
prose
 -> EXTRACTION (incremental predictive parse; today spaCy arc-eager, recall 0.98 here -- OK for this gold)
 -> COREF / participant binding (discourse referents; E3, needs live adapter) ...................... upstream to fix
 -> MEANING CHANNEL (resolved participants + result-state predicates; meaning_foundation, LATENT) ... upstream to fix
 -> GENERATIVE DIRECTED EDGE-GENERATOR (deepen U8: force_dynamics + goal_register + occ_appraisal +
     _tom_chain + world_state_register -> a content-sensitive result-state rollout over resolved
     participants; emits DIRECTED cause/enable/result-state edges) ............ THE CRUX (Tier 1 + 4 supply cues)
 -> REACHABILITY ENGINE (chain edges to the goal-state: SR/PPR resolvent M=(I-gammaT)^-1, goal-conditioned;
     and/or causal_reasoner traversal + counterfactual) ......................... PROVEN, reuse (Tier 1 depth)
 -> ACHIEVEMENT CHECK (inverse planning: does the reached state achieve the goal-state; DEFEAT-suppress) .. built
 -> DECISION LAYER (graded_competition additive net_activation + softmax; each engine = one directed,
     achievement-checked support vector with a learned validity) ................ PROVEN, reuse (Tier 2)
```
The false-negative lens says the reachability engine and decision layer are DONE; the whole build is the
UPSTREAM being 100% brain-foundational so c→1.

## OPTIONS (ranked; strategic fork -> prose recommendation, owner decides)
**Option A (RECOMMENDED) — reopen SR/PPR as the multi-step engine, fed correct generated edges.** Build the
generative directed result-state edge-generator over resolved participants; assemble a typed directed
transition graph; run the SR/PPR resolvent (goal-conditioned reachability) + the causal reasoner as validator;
decision layer = graded_competition; add physics/affect/mental as cue channels. This is the sharpest test of
the false-negative hypothesis (SR fed typed edges HARD_PASSED before) AND fixes every tier through the shared
decision layer. RISK: the edge-generator over DEEP-multistep still needs result-state predicate knowledge (the
meaning-channel/knowledge-foundation frontier) — but that is now the single, named, measurable dependency.
**Option B — generative replay traversal beam over the generated edges** (instead of SR/PPR). Same upstream;
beam-rollout with deferred commitment (the 43% scaffold) rather than the closed-form resolvent. Use if the
graph is too sparse/dynamic for a clean transition matrix. Slightly less clean than the closed-form SR.
**Option C — bank the landed tiers first (Tier 2 + Tier 4), then the hard Tier 1.** Land graded_competition as
the decision layer + wire force_dynamics/occ_appraisal/_tom_chain as cue channels for the non-goal 64%
(potential +0.332, mostly-landed, low-risk, measurable) BEFORE the generative multi-step edge-generator. This
is the safest "fix all tiers" SEQUENCING and de-risks by proving the shared spine first.
**Recommended path: C then A** — bank the proven decision-layer + other-engine cues first (measure the
non-goal lift), then attack the generative multi-step edge-generator with SR/PPR reopened. Every step reuses a
proven brain-foundational engine; the only genuinely-new build is the generative directed edge-generator, and
its residual dependency (result-state predicate knowledge over resolved participants) is the named next wall.

## Do-not-re-file (measured dead-ends; but re-openable ONLY with corrected upstream)
- generic lemma-transition SR (loses to counting — reopen ONLY with typed/goal-conditioned edges);
- GEK/co-occurrence as the achievement axis (directionless); topical densification (dense≠correct);
- a bigger single-step VerbNet lexicon (ties base — the wall is DEPTH not single-step coverage);
- Kintsch uniform-inhibition settling / normalized_recurrence for accuracy (monotone = argmax);
- external LLM at inference (THE invariant).
