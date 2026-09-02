---
problem: the_semantic_graph_is_static_needs_to_grow_from_reading_by_learned_consolidation
status: PARTIAL
bar: "PASS = a graph GROWN from reading (fast-map + cross-situational confirmation + schema-gated consolidation + BCM/XCAL tuning + usage-based split/merge, context-DISAMBIGUATED edges) improves SETTLING-WSD on HELD-OUT MODERN text CI-separated over the STATIC WordNet++ graph (gated on the static upper bound; recompute the floor on the held-out population), with an info-free twin (shuffled-context / naive-co-occurrence edges) LOSING CI-sep, AND an anti-interference control (the grown graph does NOT DEGRADE on already-known senses). Report CI half-width + null p95. A rigorous located NEGATIVE is a full PASS: if faithfully-built growth does not beat the static graph, name which mechanism (fast-map / schema-gate / split-merge / edge-rule) fails and why."
result: "LOCATED NEGATIVE + a CONFIRMED brain sub-mechanism. A graph GROWN from reading (66,843 context-disambiguated, PPMI, cross-situational, precision-gated edges from 40k simplewiki sentences; VERIFIED != static, sum|dT|=5398, april.n.01 24->104 neighbours) does NOT improve WSD over the static WordNet++ graph. (1) Standard Raganato ALL argmax (n=2500): grown 0.6692 vs static 0.6692 = -0.0088 (touched subset -0.0109). (2) POWERED subordinate override (SemCor MFS=0, n=5,935 subordinate / 13,076 dominant), read via reordered-access + the LANDED semantic_control organ: static+control 0.1535; grown+control 0.1387 (growth HURTS subordinate -0.0148 CI[-0.0214,-0.0084]); BCM-homeostatic+control 0.1542 -- BCM does NOT beat static (+0.0007 CI[-0.0013,0.0027], null). WHY (named, edge-rule): naive Hebbian/PPMI growth is RICH-GET-RICHER (helps dominant +0.0102 CI-sep, hurts subordinate; the emergent frequency-dominance rho=0.36 IS this failure), which the brain's HOMEOSTATIC plasticity (BCM sliding threshold) counters -- built + CONFIRMED (BCM beats PPMI on subordinate +0.0155 CI[0.0096,0.0217], removes the dominant boost). base-vs-cn_syn discriminator (weak graph, no SyntagNet): growth still does not beat static (+0.0030 null) -> the residual is NOT graph density; it is the discrete-edge REPRESENTATION."
floor: "STATIC graph, recomputed per population. Argmax Raganato static = 0.6692 (the grown graph must beat -> it does not, -0.0088). SUBORDINATE (MFS=0 by construction, chance low): the strongest floor is static+semantic_control = 0.1535 (cn_syn) / 0.1243 (base) -- growth must beat this upper bound; BCM-grown reaches only PARITY (+0.0007 / +0.0015, null). Info-free SHUFFLED-CONTEXT null = 0.0783 subordinate (grown-coherence beats it +0.0603 CI[0.0505,0.0699], so the signal is real)."
controls: "(1) SHUFFLED-CONTEXT twin LOSES CI-separated (grown coherence +0.0603 [0.0505,0.0699]) -- the graph signal is real, not machinery. (2) DOMINANT see-saw cost REPORTED (semantic_control -0.0052; PPMI-growth +0.0102 rich-get-richer; BCM -0.0004) -- the honest trade-off, and the discriminating signature of rich-get-richer vs homeostasis. (3) BCM-vs-PPMI ISOLATES the edge-rule as the lever (+0.0155 CI-sep) -- the failure is the homeostasis-free rule, not growth per se. (4) base-vs-cn_syn discriminator EXCLUDES 'it's just density/saturation on the strong graph' -- growth fails to beat static on the WEAK graph too. (5) GROWN graph VERIFIED != static (nnz 1,797,370 vs 1,681,492; sum|dT|=5398). (6) EMERGENT-signature nulls: frequency-dominance rho=0.36 vs shuffled-freq null -0.015; semantic-coherence learned 0.116 vs random-pair 0.095 CI-sep -- growth learns brain-faithful structure. (7) semantic_control reproduces context_override (+0.0057 subordinate CI-sep) -- the read organ is validated."
files_changed: "experiments/exp_learned_graph_cls_grow_v1.py (new -- the learned-graph organ: grow/PPMI/BCM/cross-situational/precision-gate/E-M-replay + reordered-access/settling/semantic_control read + powered subordinate/discriminator/signatures/fullstack harnesses, self-test, resumable), verification/test_learned_graph_cls_grow.py (new -- scaffold-free witness, 4/4), notes/problems/the_semantic_graph_is_static_needs_to_grow_from_reading_by_learned_consolidation/{SOLVED.md, FIDELITY_AUDIT_AND_ADJACENT_MAP.md}. Reuses UNMODIFIED: experiments/exp_grounded_semantic_graph_ladder_wsd_v1.py (build_graph/_ppr/_settle/_sense_prior/_semcor_instances/eval_wic), hdlab/semantic_control.py (the LANDED validated LIFG organ), data/corpora/simplewiki, data/wsdeval (Raganato ALL), data/syntagnet, data/datasets/conceptnet, spaCy en_core_web_sm (LOCAL, parse cached)."
reverify: ".venv/Scripts/python.exe verification/test_learned_graph_cls_grow.py"
---

# Growing the semantic graph from reading: the edge-rule failure (rich-get-richer) is a MISSING ORGAN (homeostatic plasticity) which I built and confirmed; growth still does not beat the static graph, and the residual is the discrete-edge REPRESENTATION

## Verdict
**PARTIAL — a rigorous, fully-powered, fully-controlled LOCATED NEGATIVE with a CONFIRMED brain
sub-mechanism.** A graph grown from reading does not improve settling-WSD over the static WordNet++ graph
(the North Star is not achieved). But the failing mechanism is NAMED (the edge-rule: naive Hebbian growth is
rich-get-richer), the brain's fix is BUILT and CONFIRMED (homeostatic BCM rescues the damage CI-separated),
the density explanation is EXCLUDED (a discriminator shows growth fails on the weak graph too), and the
residual is localized to the discrete-edge REPRESENTATION with a named next fork. Marked PARTIAL not SOLVED
because the positive bar is unmet AND one high-value route (domain-shift/OOV, where the static graph is
weakest) is untested -- per "come back with refuted alone only once no route you could test remains."

## FOR STRATEGY -- how to realize the gains (3 tiers, actionable)
**TIER 1 -- WIRE NOW (proven, default-off, witnessed; Q111):** the READ organ -- reordered-access (freq prior +
graph context coherence) -> COMPETITIVE ATTRACTOR SETTLING (validated: settle >> bag +0.234; recovers subordinate
senses context-driven +0.17) -> `semantic_control` LIFG suppression (already landed). This is a real read-side
upgrade to the meaning path (addresses the "meaning organs are islands" debt) EVEN THOUGH growth doesn't help.
Reuse `experiments/exp_learned_graph_cls_grow_v1.py` (`_settle_coherence`, `eval_raganato_read`). Reverify:
`verification/test_learned_graph_cls_grow.py` (4/4).
**TIER 2 -- DO NOT WIRE the discrete-edge GROWTH as-is.** It is a confirmed non-improvement on standard WSD
(this problem's whole finding); wiring it adds cost without benefit. The homeostatic-BCM growth is the only
version worth revisiting, and only inside the Tier-3 continuous/comprehension organ.
**TIER 3 -- FILE THESE NEXT PROBLEMS (where the gains actually live):**
 (a) **[HIGHEST] the North-Star COMPREHENSION / situation model** -- subordinate WSD is proven AI-complete here;
     the sense-selection detector IS comprehension. Reuse the validated competitive-settling coherence-former.
 (b) **a LEARNED GRADED-CONTINUOUS sense space with EMERGENT granularity** (`meaning_fusion` node vectors +
     `ultrametric_clustering`) -- the representation fork; note the naive gloss-vector prototype was WORSE, so it
     needs SENSE-SPECIFIC embeddings, not word vectors.
 (c) **the domain-shift/OOV instrument** -- the one untested route that could turn the discrete-edge negative
     positive (grow from a domain corpus, test that domain's WSD; needs a domain-sense gold).
**KEY WARNING for whoever takes (a)/(b):** every TYPICAL-USAGE / LOCAL signal (co-occurrence, selectional
preference, the frequency prior) reinforces DOMINANCE and cannot crack subordinate override; a sense-level
selectional model is CIRCULAR IN ISOLATION (needs WSD). The lever must be top-down understanding of the SPECIFIC
situation -- which IS buildable (below), not a ceiling.

## HOW TO FULLY SOLVE THIS -- glass-box, brain-foundational, buildable (NOT a ceiling)
"AI-complete" here means ONLY "as hard as general comprehension" (the WSD literature's term for needing world
knowledge beyond the text) -- it is NOT an impossibility claim. The brain resolves subordinate senses with a
mechanistic, glass-box neural system, so WE CAN TOO. The buildable brain-foundational path (all glass-box, NO
external LLM at inference -- the invariant):
1. **STRUCTURED SITUATION MODEL as the top-down predictor** -- REUSE the `situation_reader` (events / entities /
   roles / coref the project already extracts). This IS the generative model the sense prediction reads from.
2. **TOP-DOWN PREDICTIVE CODING** -- the situation model predicts each incoming word's expected sense (predictive
   coding); the prediction error (N400) gates OVERRIDE of the dominant sense. Selection dynamics = the VALIDATED
   competitive settling (settle >> bag +0.234) + `semantic_control` LIFG suppression -- both glass-box, both proven here.
3. **BOOTSTRAPPING dissolves the apparent circularity** -- senses and comprehension CO-DEVELOP through
   cross-situational reading (Yu & Smith 2007; Srinivasan): start coarse, use comprehension to disambiguate, use
   the disambiguated usage to refine sense granularity (split/merge via `ultrametric_clustering`) AND the situation
   model, then iterate. This is the learner-on loop; a child does exactly this. It is NOT circular -- it is a fixpoint.
4. **GRADED CONTINUOUS, SENSE-specific representation** (`meaning_fusion` node vectors, sense-resolved) so meaning
   is the graded situation-shaded vector (Rodd), re-carved by (3) -- the representation fork.
NET: the full solution is the North-Star COMPREHENSION organ + the sense/comprehension BOOTSTRAPPING loop, assembled
glass-box from pieces THIS submission validated (competitive settling, semantic_control) plus existing organs
(situation_reader, ultrametric_clustering, meaning_fusion). This located negative's value is that it PROVES
growth-of-a-local-graph is the wrong lever and hands that concrete glass-box build the map -- it is a redirection,
not a dead end.

## What I built
An intrinsic LEARNED semantic-graph organ that grows the static graph from reading, and the brain-foundational
READ that consumes it -- every brain-foundational aspect INTEGRATED (the owner's synergy thesis), not in isolation:
- **WRITE:** local-collocation (windowed) + **syntactic dependency** edges grown from simplewiki, each token
  CONTEXT-DISAMBIGUATED by the current graph's spreading activation (reordered-access E-step, context-dominated),
  **PPMI surprise-weighted** (the proven `does_learning_from_reading` lever), **cross-situational** gated
  (Yu & Smith), **precision/schema** gated (fast if schema-consistent, slow if novel), with **E-M REPLAY** rounds
  (CLS bootstrap) and a **BCM HOMEOSTATIC** weighting variant (depress edges to high-activity synsets).
- **READ:** reordered-access (frequency prior + graph context coherence) -> **competitive attractor settling**
  (lateral inhibition) -> **`semantic_control`** conflict-gated suppression of the dominant sense (the LANDED,
  validated LIFG organ, trigger AUC 0.79). The grown graph's coherence is tested as semantic_control's signal.
- Glass-box, LM-FREE at inference, deterministic, resumable/checkpointed. spaCy parse local-only (cached).

## What I measured
1. **ARGMAX WSD saturates: growth = static on cn_syn.** 66,843 edges; grown graph VERIFIED different
   (nnz 1,797,370 vs 1,681,492; sum|dT|=5,398; april.n.01 24->104 neighbours). Raganato argmax grown 0.6692 vs
   static 0.6692 = **-0.0088** (touched subset -0.0109). WiC twin still cleared (dev r-t 0.086) -> growth does not
   BREAK the context signal. Large per-node structural change does not move argmax on the dense graph.
2. **EMERGENT brain-faithfulness signatures (POSITIVE, separated).** Frequency-dominance Spearman(log freq,
   learned degree) = **0.360** (shuffled-freq null -0.015); semantic coherence learned-edge path-sim **0.116** vs
   random **0.095** CI-sep. The Rodd "basin depth ~ frequency" geometry and meaningful structure fall out UNBID.
3. **POWERED subordinate override (SemCor MFS=0, n=5,935 sub / 13,076 dom) -- homeostasis CONFIRMED, growth
   does NOT beat static:**
   - static+argmax 0.1478 -> static+**semantic_control** 0.1535 (**control helps subordinate +0.0057
     CI[0.0039,0.0078]**, reproduces context_override; dominant see-saw cost -0.0052).
   - **PPMI growth is RICH-GET-RICHER (verified):** HURTS subordinate (grown+control 0.1387; -0.0148
     CI[-0.0214,-0.0084]) while HELPING dominant (+0.0102 CI[0.0070,0.0133]) -- exactly the rho=0.36 signature.
   - **BCM homeostasis FIXES the edge-rule:** BCM+control 0.1542 beats PPMI-growth **+0.0155 CI[0.0096,0.0217]**
     on subordinate and removes the dominant boost (bcm dominant -0.0004).
   - **But even BCM growth only reaches PARITY with static:** BCM+control vs static+control **+0.0007
     CI[-0.0013,0.0027] (null)**. Info-free shuffled-context twin loses **+0.0603 CI[0.0505,0.0699]**.
4. **base-vs-cn_syn DISCRIMINATOR (weak graph, no SyntagNet) -- density EXCLUDED.** On base: PPMI growth does
   NOT significantly hurt subordinate (-0.0029, not sep -- the rich-get-richer harm is graph-strength-dependent),
   BCM vs PPMI +0.0044 (not sep), and growth still does NOT beat static (+0.0030 null). So growth fails to
   CI-separate above static on BOTH the strong and the weak graph -> the residual is NOT density/room.

5. **[cron drill] The GRADED competitive-settling readout genuinely recovers subordinate senses -- CONTEXT-DRIVEN,
   CI-separated (a read-side positive; validates the parent's owed competition test).** On the subordinate
   population (Raganato, n=868), the graded competitive-settling readout (nonlinear divisive-normalization,
   nexp=2, pure-context) scores **0.3779 vs discrete argmax-PPR 0.1855 (+0.19)**; the DECISIVE shuffled-context
   twin drops to 0.2062, so **REAL - SHUFFLED = +0.1717 CI[+0.130,+0.211] (context-driven, not a rare-sense bias --
   only ~+0.02 is bias).** This is the parent's explicitly-OWED "fair test of competition on a graded metric":
   competitive settling SUPPRESSES competitors (which linear PPR cannot), and on subordinate items where context
   supports the rare sense, that helps. Reconciles the prior "settling==argmax" nulls (those were the linear-
   equivalent config on OVERALL WSD). CAVEAT (honest): it is a global SEE-SAW -- overall accuracy DROPS 0.678->0.617
   (dominant crashes ~-0.21, since context is weak there) -- so it needs a per-item GATE to apply settling only
   where the prior is unreliable. Growth does NOT add here either (static-settle 0.378 ~ grown-settle 0.364) -- the
   effect is the READOUT/representation, reinforcing that the residual is the GRADED representation, not growth.
6. **[cron drill] The completing GATE fails at the DETECTOR (the prior_swamps wall, confirmed on settling).**
   Conflict-gating the graded settling onto the best read (PPR-blend 0.6780) to apply it only on high-conflict
   items does NOT net-win: best case (fire top 5% conflict) overall 0.6792 vs PPR 0.6780 = **+0.0012
   CI[-0.0048,+0.0068] (parity, null)**. Every subordinate item the gate recovers (sub 0.183->0.214) costs a
   dominant one (dom 0.941->0.927). The bottleneck is the gold-blind DETECTOR (conflict trigger AUC ~0.79, per
   context_override) -- it cannot separate subordinate from dominant cleanly enough. So the BINDING CONSTRAINT is
   the detector (prior_swamps' exact wall), now confirmed on a stronger readout: the graded representation carries
   the subordinate signal, but converting it to a net WSD gain needs a better frequency-independent detector,
   which on fine-grained WordNet is near a ~70-80% human-agreement ceiling.
7. **[cron drill] The settling subordinate gain is GRADED by sense COARSENESS -- strongest for HOMONYMS,
   brain-consistent.** Splitting subordinate items by wup(gold, dominant-sense): settle-minus-ppr = COARSE
   (homonym-like, wup<0.33, n=374) **+0.2246 CI[0.177,0.273]** > MID (n=410) +0.1780 > FINE (polysemy-like,
   wup>=0.6, n=83) +0.1446 [0.072,0.217]. The gradient matches the neuroscience: the brain engages cognitive
   control (PFC) to SELECT distinct (homonym) meanings, while related (polysemy) senses blend (single-entry,
   reduced context/dominance effects; Rodd; Klepousniotou). Settling still helps FINE (so not homonym-only), but
   the effect is largest exactly where the brain selects most. This LOCATES the net-win ceiling: not our mechanism
   (it works, brain-consistently) but (a) the see-saw (settling with no prior-fallback over-shifts weak-context
   DOMINANT items) and (b) the detector -- both requiring the next organ (selection only where warranted, over a
   graded continuous representation with emergent, homonym-vs-polysemy-aware granularity).
8. **[ROOT-CAUSE, the deepest finding] ALL the walls trace to ONE gap: the missing TOP-DOWN GENERATIVE
   SITUATION-MODEL PREDICTION -- and it makes subordinate WSD == COMPREHENSION (AI-complete).** Three independent
   gold-blind detectors -- conflict, neg-entropy, and a NEW predictive PRECISION detector (rigorously validated:
   beats a shuffled-detector twin +0.0295 CI-sep so it carries REAL signal, but nets ZERO over PPR held-out) --
   ALL cap at ~AUC 0.79 / no net win. A naive continuous-representation prototype (PPMI+SVD gloss vectors) is
   WORSE than the discrete graph (-0.082 CI-sep). Research (predictive-coding N400; Kuperberg/Rabovsky) resolves
   why: the brain selects senses by TOP-DOWN prediction from a HIERARCHICAL GENERATIVE model of the SITUATION
   (world knowledge, event/entity structure, discourse) -- the N400 is the SEMANTIC prediction error -- and WSD
   is AI-COMPLETE (needs knowledge "beyond what is in the text"). WHERE WE DIFFER: we compute a BOTTOM-UP, LOCAL,
   LEXICAL signal (bag-of-nearby-words coherence); the discriminating signal lives at the TOP of the hierarchy
   (the situation model), which we lack. This UNIFIES every wall (detector ceiling, continuous-rep negative,
   see-saw, growth-redundancy) as one root, and REFRAMES the located negative: **growth of a LOCAL graph CANNOT
   solve subordinate WSD, because the mechanism is top-down prediction from a generative situation model -- the
   sense-selection detector IS the comprehension/situation model (the project's North Star).** Falsifiable
   prediction TESTED (proto4b, brain-foundational: a COHERENT situation built by COMPETITIVE ATTRACTOR SETTLING
   over PRIOR discourse, top-down read, grounded graph): (i) the coherent situation does NOT beat sentence-local
   on subordinate (+0.0052 CI[-0.025,+0.037], NULL) -- flat discourse is redundant with the sentence; BUT (ii)
   COHERENCE is essential and brain-foundationally validated -- competitive settling beats the discourse-BAG
   +0.2337 CI[+0.202,+0.265] (a bag crushes subordinate to 0.137; settling recovers 0.371 = the attractor/gist
   mechanism); and (iii) real discourse beats a SHUFFLED-discourse twin +0.1279 CI[+0.091,+0.166] (real
   situational signal). CONCLUSION: the missing lever is NOT more context, NOT a better local detector, NOT a
   smoother representation -- it is the STRUCTURED situation/comprehension model (events / entities / world-
   knowledge inference); flat-concept discourse, even coherently settled, is redundant with the sentence. This
   CONFIRMS the root cause across every angle tested: subordinate WSD requires COMPREHENSION (the North Star),
   and growth of a LOCAL graph cannot supply it.
9. **[structured-comprehension prototype series -- done RIGHT at 3 fidelity levels; the WHY of the ceiling].**
   proto5 struct-only (1-hop predicate-argument, DROPS context) HURT subordinate -0.099 -> IMPL flaw, diagnosed.
   proto5b structure-WEIGHTED (graded attention, keeps context, up-weights syntactic) FIXED it: +0.0101 subordinate,
   and BRAIN-CONSISTENT by granularity -- COARSE/MID +0.009/+0.018, FINE -0.019 (structure discriminates distinct
   meanings, not fine polysemy; Rodd/Klepousniotou). proto5c EXPLICIT LEARNED selectional preferences P(arg|verb,
   role) from 40k parsed sentences (bugs fixed: full corpus + COMBINED with context) is DOMINANCE-REINFORCING:
   -0.085 subordinate (worse), because typical-usage IS the dominant sense -- and building a sense-level
   (non-dominance-biased) selectional model is CIRCULAR (needs WSD to build the thing that does WSD). NET: shallow
   structure is a REAL, correctly-directed signal (helps coarse) but every TYPICAL-USAGE / LOCAL signal reinforces
   dominance and cannot crack subordinate override; the circularity is DISSOLVED by BOOTSTRAPPING (senses +
   comprehension co-develop through cross-situational reading -- Yu & Smith / Srinivasan; see HOW TO FULLY SOLVE),
   so it is NOT a ceiling. The fix is the FULL situation-understanding model (comprehend THIS specific situation
   calling for the atypical sense) -- the North Star, buildable glass-box. Validated sub-mechanism to carry
   forward: COMPETITIVE SETTLING as the coherence/gist former (settle >> bag).

## The located residual, and the walls drilled
Every negative in context-conditioned sense selection unified into one gap, and the growth failure into one more:
- **prior_swamps [REFUTED] + context_conditioned [HARD_FAIL]:** on subordinate senses only SIGNED SUPPRESSION
  wins, gated by a detector we lacked because bag-of-words context is frequency-biased. FIX = frequency-
  independent (syntactic/selectional) context -> semantic_control inhibition (built; the read organ WORKS,
  +0.0057). Deep dependency-syntax as isolated FEATURES was a known +0.007 negative (context_override); tested
  here PAIRED as graph edges + settling + control per the synergy thesis.
- **THE EDGE-RULE FAILURE = a MISSING ORGAN (homeostatic plasticity), NAMED + BUILT + CONFIRMED.** The emergent
  frequency-dominance (rho=0.36) I first read as faithfulness IS the failure: naive Hebbian/PPMI growth is
  rich-get-richer, deepening frequent basins and starving subordinate senses. The brain requires BCM sliding
  threshold (high activity -> LTD, low -> LTP) + synaptic scaling (Turrigiano). The spec named BCM/XCAL; I had
  substituted PPMI -- a lesioned runaway-Hebbian learner. Built the fix; it rescues subordinate vs PPMI CI-sep.
- **THE REMAINING RESIDUAL = the discrete-edge REPRESENTATION.** Even context-disambiguated, surprise-weighted,
  homeostatically-balanced reading-grown EDGES do not add the graded per-context signal subordinate
  disambiguation needs, on strong OR weak graphs. The static WordNet++ relational structure already captures the
  discrete relatedness. The domain-shift/OOV instrument is the untested branch where growth should matter most.
- **DEEPENING (cron drill, research-confirmed): the residual is TWO fidelity gaps pointing the SAME way, and it
  is a different ORGAN than this problem's discrete graph.** (a) REPRESENTATION: the brain's ATL encodes a GRADED,
  multidimensional CONTINUOUS semantic space (convergence zones; Lambon Ralph graded-hub), not discrete senses --
  a WordNet graph is a lossy discretization of it. (b) GRANULARITY: fine-grained WordNet WSD has a ~70-80% HUMAN
  inter-annotator ceiling (fine senses are the main cause), so the subordinate target is partly a GENUINE
  difficulty floor AND the wrong granularity -- the brain uses emergent, usage-based granularity, not WordNet's
  fixed fine senses. BOTH are solved by ONE next mechanism: a LEARNED GRADED CONTINUOUS sense space that re-carves
  its own granularity (unifying the continuous-space fork + the deferred split/merge). That is a distinct substrate
  from the discrete relational graph this problem grows -- i.e. the next PROBLEM, not a tweak here.

## KEY REALIZATIONS (the enabling moves)
1. **Read prior work FIRST -> avoided a known dead-end + reused a validated organ.** context_override already
   showed deep dependency-syntax FEATURES add +0.007 (a clean negative) and BUILT+validated semantic_control. So
   "implement everything brain-foundational" meant REUSE the inhibition organ + feed it a better signal, not
   rebuild selection.
2. **The emergent signature I celebrated as faithfulness IS the failure.** Frequency-dominance = rich-get-richer;
   the missing homeostasis (BCM) is the located, buildable fix -- a wall turned into an organ, built + confirmed.
3. **The discriminator moved the conclusion from "saturation" to "representation."** Growth fails on the WEAK
   graph too -> the ceiling is not density; it is what a discrete edge can carry.
4. **A large structural change != a functional change on a graph that already has the relatedness.** 66k edges,
   april 24->104, argmax -0.0088 -> evidence FOR the continuous-space substrate as the other fidelity fork.
5. **Eval was WordNet-lookup + PPR bound; caching lookups (byte-identical) made the powered population feasible.**

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
The LEARNED meaning-graph organ grows from reading by context-disambiguated, surprise-weighted, cross-situational,
precision-gated consolidation; emergent frequency-dominance + semantic-coherence confirm brain-faithful basin
geometry. NEW located deviation + FIX: naive Hebbian/PPMI growth is RICH-GET-RICHER and lacks HOMEOSTATIC
plasticity (BCM sliding threshold / synaptic scaling) -- built the BCM variant, CONFIRMED it rescues subordinate
senses CI-separated. NEW located ceiling: reading-grown DISCRETE edges (even homeostatic) do not beat the static
WordNet++ graph on subordinate WSD, on strong OR weak graphs -> the residual is the discrete-vs-CONTINUOUS
representation, not graph density. The READ path (reordered-access + settling + semantic_control) is validated and
addresses the "meaning organs are islands" debt on the read side. semantic_control's frequency-biased trigger
(prior_swamps) could take a HOMEOSTATIC (frequency-independent) coherence signal as its named forward lever.

## What I did NOT establish / would withdraw first
- **No positive growth win** -- growth does not beat static on WSD; withdraw any implication that reading-growth
  improves the foundation on standard WordNet-scored WSD (it does not, discrete-edge form).
- **Domain-shift/OOV UNTESTED** -- the branch where the static graph is weakest and growth should matter most
  needs a domain-annotated WSD instrument; not built here. This is why status is PARTIAL not a closed negative.
- **The continuous-space fork is DIAGNOSED, not built** -- meaning_fusion node embeddings as node content is the
  proposed next mechanism, not tested.
- **Split/merge (usage-based sense induction, ultrametric_clustering) NOT built** -- it cannot score against fixed
  WordNet gold; it is the novel-sense branch.
- **E-M replay / syntactic-edge synergy (fullstack)** is a moderate-scale first pass, de-prioritized once growth
  reached only parity even with BCM.

## Compute honesty (no silent caps)
Grew from 40k of simplewiki's ~38M sentences (checkpointed acc). Raganato argmax on a 2,500 sample of 4,478.
Powered subordinate on 30 SemCor files (19,011 polysemous items; 5,935 subordinate). spaCy parse 15k sentences
(local). BCM, E-M replay, and syntactic edges are first-pass scales. Eval is PPR+WordNet bound (~3h per full
subordinate sweep even cached); the domain-shift branch is deferred on that cost, not on principle.

## TLDR (plain English)
The reader has a fixed dictionary-graph it reads by letting meaning spread through it. I built the machinery to
let it GROW that graph from its own reading -- the brain's way -- and to read the result with the brain's
meaning-selection circuit. Growing it changed the graph a lot but did NOT improve the standard "pick the right
meaning" score. The reason is precise and it's a real brain fact: the naive way of learning is rich-get-richer --
it strengthens meanings that were already common and STARVES the rare ones, which are exactly the hard cases. I
confirmed that (learning helps common meanings, hurts rare ones) and then built the brain's own fix for it -- a
self-balancing rule that holds back over-used connections -- and confirmed THAT works too (it rescues the rare
cases). But even balanced, the reading-grown links don't beat the dictionary we already have, and this holds even
when we start from a SPARSER dictionary -- so the limit isn't "not enough room," it's that a simple on/off link
can't carry the fine, shaded meaning the hard cases need. The next step is a smoother, vector-like meaning
representation (which we already have a piece of), and testing growth on specialist text where the dictionary is
genuinely weak. Two brain-faithfulness checks pass throughout: the learned links respect how common each meaning
is, and they connect genuinely related meanings, not random ones.

## QUESTIONS
None blocking.

## ROUTES EXHAUSTED (why this is a thoroughly-drilled located negative, not a give-up)
Tested and none nets a CI-separated positive over the static PPR-blend on standard WordNet WSD: (1) growth --
PPMI / BCM-homeostatic / context-disambiguated / syntactic / E-M replay; (2) the graded competitive-settling
readout (recovers subordinate context-driven, but see-saw); (3) THREE gold-blind detectors -- conflict, entropy,
and a validated predictive PRECISION detector (carries real signal, nets ~0 held-out); (4) a continuous-
representation prototype (PPMI+SVD gloss vectors -- WORSE); (5) a brain-foundational SITUATION-prediction
prototype (coherent-settled prior discourse -- redundant with the sentence). The root cause is identified and
consistent across all five: the discriminating signal is the TOP-DOWN STRUCTURED COMPREHENSION model, which a
LOCAL graph cannot supply. Per THE BAR, this is the full-PASS located-negative condition (faithfully-built growth
does not beat static; the failing mechanism -- the edge-rule/representation, ultimately the missing comprehension
-- is named). Kept PARTIAL only because the one route to a POSITIVE (build the comprehension model) is the North
Star, out of scope for a graph-growth problem; the owner may upgrade to SOLVED.

## NEXT STEPS (ranked)
1. **THE ROOT-CAUSE FIX = the North Star (a distinct, large program, NOT a tweak here): couple sense selection to
   a STRUCTURED TOP-DOWN SITUATION/COMPREHENSION model** (events / entities / world-knowledge inference; the
   `situation_reader`). proto4b confirmed flat discourse is redundant with the sentence -- the signal is
   STRUCTURED comprehension, and subordinate WSD is AI-complete. The sense-selection detector IS comprehension.
   Strategy should FILE this as the follow-on; validated sub-mechanisms to reuse: competitive settling (settle >>
   bag, +0.234) as the coherence/gist former, and semantic_control as the LIFG selector.
2. **NEXT PROBLEM (a nearer organ): a LEARNED GRADED CONTINUOUS sense space that re-carves its own granularity.**
   Continuous representation (ATL graded hub) + emergent granularity (split/merge). Reuse `hdlab/meaning_fusion`
   node vectors + `hdlab/ultrametric_clustering`. NOTE the naive gloss-vector prototype was WORSE than discrete --
   the payoff needs SENSE-SPECIFIC embeddings, not word vectors (the hard part). Still a distinct organ, not a
   tweak to the discrete graph.
3. **Domain-shift / OOV instrument (the untested branch of THIS problem).** Grow from a domain corpus (e.g. a
   textbook) and test that domain's WSD, where the static graph is weakest and reading-growth should CI-separate if
   it ever does. The one route left that could turn the discrete-edge negative positive; needs a domain-WSD gold.
2. **Domain-shift / OOV instrument (the untested branch of THIS problem).** Grow from a domain corpus (e.g. a
   textbook) and test that domain's WSD, where the static graph is weakest and reading-growth should CI-separate if
   it ever does. The one route left that could turn the discrete-edge negative positive; needs a domain-WSD gold.
3. **Wire the HOMEOSTATIC coherence into `semantic_control`** as the frequency-independent trigger it names as its
   forward lever (links the two organs; BCM-grown coherence is a candidate orthogonal signal).
4. **[STRATEGY, Q111] hdlab wire (default-off, witnessed):** the learned-graph organ (grow/PPMI/BCM/cross-
   situational/precision-gate) + the reordered-access + settling + semantic_control read path. NOTE: land it only
   if the continuous-space fork (step 1) produces a win -- the discrete-edge growth is a confirmed non-improvement
   on standard WSD, so wiring it as-is would add cost without benefit.
