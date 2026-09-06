# Research drill: the brain mechanism + a mechanism-level post-mortem of the prior WIQA HARD_FAILs

Owner directive: "any previous hard fail shouldn't be 100% trusted... implementations require other brain
foundational components in order to work." This drill establishes (A) the pinned brain mechanism and (B) exactly
which brain-foundational component every prior WIQA cell was MISSING. Sources: on-disk notes + the prior cells'
own code/metrics (no web). File:line refs are to the on-disk files read.

## PART A -- the pinned brain mechanism
**Multi-hop chain (PINNED, copy the computation):** a reader represents a narrative as a CAUSAL NETWORK over
event nodes with INFERRED causal edges (Trabasso & van den Broek 1985; Trabasso, van den Broek & Suh 1989;
BRAIN_FOUNDATIONAL_AUDIT.md:854-856 pins "COVARIATION-based causal-GRAPH inference" as a successor to BUILD).
Reasoning = REACHABILITY on this network: ultimate cause = root ancestor; mediating cause = node on a path;
chain-of-consequence = forward reachability. Salience = CONNECTIVITY (degree), not recency. Edges carry a GRADED
necessity weight (audit :1045-1046: the discrete CAUSE/ENABLE/PREVENT is a lossy read-out of a graded rep;
reproduces Trabasso's ordering rho 1.000). FREE parameters (sweep): traversal depth K, admission/necessity
threshold.

**Counterfactual necessity (PINNED at the computational level):** Pearl SCM abduction -> action -> prediction:
do(X=x) is graph SURGERY (cut incoming to X, set X) then re-propagate; necessity = the outcome's value CHANGES
between the factual and intervened graphs. "Remove node + re-propagate reachability" is the faithful BOOLEAN
"did-not-happen" special case; the general form is NEGATE/SET-and-re-simulate. The substrate already validated the
primitive (rank-1 downdate = do(X=x); downdate+write = Pearl twin-network; K-hop replay = re-propagation --
`notes/research_drill_substrate_gap_causal_counterfactual_3x_2026-06-07.md:409-422`), but it was NEVER composed
into the WIQA reasoner. WHICH node to mutate = Kahneman & Miller norm theory (the abnormal/controllable/foregrounded
one) -- OUR-INVENTION, literature-grounded (compatible with the audit's Hopper-Thompson foregrounding filter).

**Neuroscience (established on disk):** vmPFC/frontopolar tracks counterfactual/regret MAGNITUDE (Coricelli 2005;
Boorman 2009); hippocampal K-hop relational replay (Carr/Jadhav/Frank 2011); counterfactual engagement rises with
nesting depth (De Brigard 2013), degrading beyond depth 3-4 (Byrne 2016). DMN-as-simulator is motivating background,
marked SPECULATIVE. The audit has NO counterfactual/Pearl/Kahneman entry (grep = 0 hits) -- this reasoner is new
coverage.

## PART B -- why the prior WIQA cells failed (mechanism-level; all were NON-brain-foundational)
All four cells share ONE mechanism (`build_register` loop_v1:217-238, reused verbatim by every cell): edges are
built STRICTLY over the linear paragraph step order `add_causal_link(i, i+1)`, edge sign = a negation-WORD lexical
flip (`has_negating_word`), and `propagate_sign` walks lo->hi multiplying signs. Findings:
1. **No inferred causal NETWORK.** Edges = surface sentence adjacency, not covariation/necessity-inferred causal
   edges over event nodes. There is NO reachability query anywhere -- ultimate/mediating/chain collapse into a
   product of adjacent signs.
2. **`no_effect` = a lexical trick, not disconnection.** POLARITY-ECHO predicts no_effect iff the outcome clause
   has no polarity word (loop_v1:286-291); the loop cannot predict no_effect at all. The prereg measured this
   distractor-detection at balanced-acc 0.4997 = CHANCE (loop_v1.md:85-97). The RIGHT model -- "outcome node not
   reachable from the perturbation" -- was never computed.
3. **No simulated intervention.** No cell cut a node and re-propagated; they are forward sign-multipliers.
4. **The "flawed even with gold anchors" verdict is confounded.** oracle_structure replaced ONLY the node POSITIONS
   (gold i,j), NOT the edge signs (still negation-word), NOT the topology (still linear i->i+1), NOT reachability
   (oracle_structure.py:54-66; metrics oracle_scope_note). It never tested the brain's mechanism.

Numbers (per each cell's metrics.json): loop_v1 MIDDLE_BAND (loop 0.3477 vs polecho 0.3420, scramble did NOT
collapse the gain); loop_v2 HARD_FAIL (active_multihop: scramble 0.5584 >= loop 0.5525 -- the gain is topology, not
edge-sign reasoning); oracle_structure HARD_FAIL (loop_oracle 0.4424 LOSES to majority 0.5064); learned_signs
HARD_FAIL (train edge-acc 0.982 -> test 0.412, below chance -- does not generalize).

## The missing brain-foundational triple (what this problem builds)
(1) an event-node causal NETWORK with reachability; (2) `no_effect` as NON-reachability / failed necessity;
(3) counterfactual by SIMULATED intervention (cut + re-propagate + compare). Supplying all three, the
brain-foundational reasoner beats the baselines the prior loop LOST to on the same modern gold (see SOLVED.md L2).
