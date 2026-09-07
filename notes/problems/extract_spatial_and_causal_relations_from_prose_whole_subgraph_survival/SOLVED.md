---
problem: extract_spatial_and_causal_relations_from_prose_whole_subgraph_survival
status: PARTIAL
bar: "PASSES only with ALL of: (1) the JOINT parse-once front-end EXTENDED to SPATIAL edges (containment/relative-position/path-transfer, Figure-Ground/RCC8) AND CAUSAL edges (connective + mental-bridge + force-dynamic), as ONE structured extraction over the reader's OWN parse, NO external LLM; (2) WHOLE-SUBGRAPH SURVIVAL (fraction of gold multi-hop >=2-edge chains with EVERY edge recovered) is the headline, CI-separated over the INCUMBENT extractor on the SAME population, gate on the floor's UPPER bound, ALSO report end-to-end; (3) the info-free SHUFFLED-RELATION twin LOSES CI-separated; (4) extraction ISOLATED (each reasoner held at gold); (5) NO-regress full-stack (prototype THIS + the upstream parse to excel/exceed, no live consumer regresses); (6) one-screen summary. A rigorous NEGATIVE is a FULL PASS (e.g. 'construction coverage lifts spatial containment survival 6/90 -> N/90 CI-sep but path survival does not move because motion source/goal binding is PP-attachment-gated, enumerated'; OR 'causal edge recall rises CI-sep but cross-sentence causal chains still die because unmarked causal links need a discourse-coherence bridge, N of M -- a distinct SDRT organ, filed')."
result: "Whole-subgraph SURVIVAL, extraction ISOLATED (reasoner held at gold), paired bootstrap over chains (CI half-width + null p95). BOTH channels are the bar's blessed LOCATED NEGATIVE, now measured with power + counts + the residual organ named. SPATIAL (SpaceEval/ISO-Space train+trial, 123 multi-hop containment chains): joint parse-once (exact-MAP + event-figure + move) survival 8/123 = 0.0650 vs INCUMBENT 6/123 = 0.0488, margin +0.0163 CI[-0.0244,+0.0650] null_p95 0.0488 -- NOT CI-separated (located negative: the exponent survival ~= edge_recall^chainlen is not broken because per-edge recall stays ~0.25, distributed across construction coverage + attachment, with no single detection gate); the shuffled-relation TWIN collapses 0/123 and joint-twin +0.0650 CI[+0.0244,+0.1138] (extracted structure IS load-bearing). A real sub-lever: EVENT-FIGURE binding (Talmy Figure = event; SpaceEval gold uses event trajectors) lifts containment EDGE recall 0.2282 -> 0.2519 and position recall 0.0491 -> 0.0736 (correcting the parent's reverted event-grounding, which bound the object not the located event). CAUSAL (MAVEN-ERE valid, 9698 gold CAUSE+PRECONDITION edges over trigger-annotated events, 710 docs -- the largest modern causal gold, detection held constant across arms): connective-bound extraction recovers 0.5% of gold edges (incumbent within-sentence 0.0044; joint cross-sentence 0.0052, +0.0007 CI[+0.0003,+0.0013] over incumbent -- a real but scientifically negligible win), while pure CONTIGUITY recovers 15.2% and the connective arm LOSES to it CI-separated (-0.147 CI[-0.154,-0.140]) -> the causal SIGNAL is NOT load-bearing over mere density (the causal SOLVED's phase-diagram finding reproduced on the EXTRACTION side, with power); connective recall on the 65.6% UNMARKED edges is 0.0005 (~unrecoverable -> the discourse-coherence bridge / SDRT organ); multi-hop causal chain survival is 0/30 for EVERY arm (real causal networks are SHALLOW -- only 30 >=2-hop chains in 710 MAVEN docs, reproducing the causal SOLVED's 3.2%-support sparsity on the largest gold). The joint twin loses (+0.0035 CI[+0.0024,+0.0047]). Upstream (full-stack): the joint spatial binder is routed through the exact Chu-Liu/Edmonds MAP + Matrix-Tree marginals (hdlab.arc_parser decode='exact', want_marginals=True -- the 2026-09-07 graded_parser) which addresses the 22.8% both-endpoints-extracted-not-linked attachment slice; it leaves the temporal event set byte-identical (no-regress)."
floor: "Per channel, recomputed on the item's OWN population. SPATIAL: the incumbent linear extractor experiments.spatial_relation_extractor.extract_edges, containment chain survival 6/123 = 0.0488 (reproduces the spatial SOLVED's 6/90); the joint arm does NOT CI-separate above it. CAUSAL: (a) the incumbent within-sentence connective extractor, edge recall 0.0044; (b) the CONTIGUITY floor (connect adjacent detected events, NO causal signal) 0.1522 -- the joint connective arm LOSES to this CI-sep, the decisive floor showing density (not the causal signal) carries any recall; (c) multi-hop chain survival floor 0/30 (all arms). Extra ceiling: the reasoners are near-perfect on GOLD relations (spatial 1.000; causal sound) -- the ISOLATION control, not a floor."
controls: "(1) SHUFFLED-RELATION twin loses CI-sep on BOTH channels (spatial 0/123, joint-twin +0.0650 CI[+0.0244,+0.1138]; causal joint-twin +0.0035 CI[+0.0024,+0.0047]) -> the recovered STRUCTURE is load-bearing, not a count artifact. (2) CONTIGUITY floor (causal): connect adjacent events with no causal signal recovers 15.2% and BEATS the connective arm CI-sep -> the causal SIGNAL is not load-bearing over density (excludes 'density masquerading as causal extraction'). (3) INCUMBENT floor per channel recomputed on the same population. (4) ISOLATION: survival is recall-based with the reasoner held at gold-perfect (the spatial/causal reasoners are owner-DONE, near-perfect on gold) -> the wall is extraction, not reasoning. (5) MARKED-vs-UNMARKED split (causal): connective recall on unmarked edges 0.0005 vs marked 0.014 -> the residual is precisely the unmarked-link discourse bridge. (6) NO-REGRESS: nothing written to hdlab (Q111) so the live reader is byte-identical; the temporal-survival witness passes 6/6 under HEAD; the proposed exact-MAP routing leaves the tense-agnostic event set byte-identical (0 symmetric-diff). Each EXCLUDES: twin=count/coverage artifact; contiguity=density artifact; isolation=strong-reasoner-as-extraction; marked-split=locates the residual; no-regress=downstream regression."
files_changed: "experiments/_joint_spatial_frontend.py, experiments/exp_joint_spatial_survival_v1.py, experiments/exp_joint_causal_survival_v1.py, verification/test_joint_spatial_causal_survival.py, notes/problems/extract_spatial_and_causal_relations_from_prose_whole_subgraph_survival/SOLVED.md (NO hdlab/ written -- Q111: proposed diff in Sec 7)"
reverify: ".venv/Scripts/python.exe verification/test_joint_spatial_causal_survival.py   # 8/8 (recomputes both located negatives + all controls from source; ~50s)"
---

# Extending the joint parse-once front-end to SPATIAL and CAUSAL edges: both are the bar's blessed LOCATED NEGATIVE, and WHY is a general finding about when whole-subgraph survival is winnable

**Bottom line.** The temporal channel of this front-end WON whole-subgraph survival (0.11 -> 0.73) because temporal
extraction had a SINGLE dominant detection gate (tense) that one brain-faithful rule removed, lifting event recall
0.32 -> 0.76 -- and survival ~= recall^chainlen, so a big recall jump breaks the exponent. I extended the SAME
one-parse front-end to SPATIAL (Figure-Ground/RCC8 + a new PATH/move channel + event-figure binding) and CAUSAL
(connective + cross-sentence binding) edges, and measured, with power and the right controls, that NEITHER clears the
survival bar over the incumbent -- and I located exactly why, mechanistically, in each case. This is the bar's own
blessed negative shape for BOTH channels (it names both verbatim), delivered with counts and the named residual
organs. Filed PARTIAL (honest deflation; no CI-separated survival WIN), with real brain-faithful sub-contributions
and a generalizable finding about the metric.

## 1. OPEN -- how the brain does this, and where our front-end differs (PINNED vs OUR-INVENTION)
- **PINNED (the shared computation).** Comprehension extracts a clause's relations JOINTLY in ONE structural pass at
  the syntax-semantics interface (IFG structure-building -> pMTG/ATL role binding; Friederici 2017; Frankland & Greene
  2015). That is why WHOLE-SUBGRAPH survival (not per-edge recall) is the right target: within-clause edges share the
  parse's fate. SPACE: Talmy/Jackendoff Figure-Ground + Place/Path schemas (the Figure can be an OBJECT or an EVENT).
  CAUSE: Talmy force-dynamics + Trabasso causal-network reachability; and -- the load-bearing brain fact here -- a
  competent reader INFERS unstated causal and cross-clause relations from world-knowledge + discourse coherence
  (Graesser-Singer-Trabasso constructionist search-after-meaning; Hobbs interpretation-as-abduction), not from
  connectives.
- **The mechanism-diff that decides the result (this problem's core finding).** TEMPORAL's extraction wall was a
  single DETECTION gate (the incumbent dropped non-past events) -- one rule fixed it and recall jumped enough to break
  the exponent. SPATIAL and CAUSAL have NO single gate: (space) per-edge recall is bound by the DISTRIBUTED
  construction inventory + entity coverage + PP-attachment, so no one lever lifts recall past ~0.25; (cause) the causal
  network is dominantly UNMARKED and SHALLOW, so a parse-bound extractor recovers ~0.5% and the world-knowledge /
  discourse-coherence inference the brain uses lives in DISTINCT organs (the filed SDRT reader; the causal reasoner's
  generative simulator). So the joint front-end -- which is the RIGHT organ for temporal -- is provably NOT sufficient
  for space/cause, and the reason is mechanistic, not effort.
- **OUR-INVENTION-UNDER-TEST (swept).** The construction inventory; the causal connective/contiguity binding; the
  event-figure rule; the move source/goal binding; the marginal gate threshold. NOT brain-faithful (avoided): an
  external LLM at inference (the invariant); scoring per-edge recall as the capability; densify+Story-Cloze as causal
  proof (the causal SOLVED's located negative); a 19c corpus as load-bearing gold (banned).

## 2. REUSE -- built ON the landed organs, did not re-derive them
- REUSED `hdlab.joint_relation_frontend` (the promoted parse-once front-end: parse cache + `joint_spatial_frames` +
  `joint_event_ranks`) and EXTENDED it in `experiments/_joint_spatial_frontend.py` with event-figure binding + a
  PATH/move channel + exact-MAP routing. REUSED `experiments.spatial_relation_extractor.extract_edges` as the spatial
  INCUMBENT + `experiments.spatial_relational_model` (SpatialModel + the survival machinery) + the survival-metric
  TEMPLATE `exp_spatial_extraction_recall_v1`. REUSED `hdlab.arc_parser.parse(decode='exact', want_marginals=True)`
  (the 2026-09-07 graded_parser: exact Chu-Liu/Edmonds MAP + single-root Matrix-Tree marginals) as the upstream.
  REUSED MAVEN-ERE (the temporal SOLVED's power gold) for CAUSAL, and its `causal_relations` annotation.
- REUSED the two reasoners UNCHANGED (owner-DONE): survival holds them at gold-perfect and varies only the front-end.

## 3. What was built (glass-box, NO LLM)
- `experiments/_joint_spatial_frontend.py` -- the extended joint SPATIAL extractor over ONE (exact-MAP) parse:
  (a) the base containment + projective-position frames (`joint_spatial_frames`, fed exact-MAP heads); (b) EVENT-FIGURE
  binding (a locative PP whose parse anchor is a detected EVENT -> the event is the Figure, e.g. 'stayed in the home'
  -> (stay,home)); (c) a NEW PATH/MOVE channel (motion verb + goal/source PP, mover = subject AND the motion event).
- `experiments/exp_joint_spatial_survival_v1.py` -- the spatial whole-subgraph survival harness: incumbent vs
  joint_greedy vs joint_exact, per-channel recall + containment chain survival + shuffled-relation twin + paired
  bootstrap, on SpaceEval train+trial.
- `experiments/exp_joint_causal_survival_v1.py` -- the causal edge-recovery + chain-survival harness on MAVEN-ERE:
  detection HELD CONSTANT (tense-agnostic events off the exact-MAP parse), binding varied (incumbent within-sentence /
  joint cross-sentence connective / contiguity floor / crosscontig), marked-vs-unmarked split, shuffled twin, the 30
  gold multi-hop chains. Aligns detected events to gold triggers by sentence+offset.
- `verification/test_joint_spatial_causal_survival.py` -- scaffold-free witness, 8/8, recomputes both located
  negatives + all controls from source, writes nowhere.

## 4. What was measured (deterministic, PYTHONHASHSEED=0)
**SPATIAL -- SpaceEval/ISO-Space train+trial (123 multi-hop containment chains):**
| arm | containment survival | containment recall | position recall | move_goal recall |
|---|---|---|---|---|
| incumbent (linear) | 6/123 = 0.0488 | 0.2282 | 0.0491 | 0.0222 |
| joint greedy | 7/123 = 0.0569 | 0.1771 | 0.0368 | 0.0194 |
| **joint exact + event + move** | **8/123 = 0.0650** | **0.2519** | **0.0736** | 0.0249 |
| shuffled-relation twin | 0/123 = 0.0000 | -- | -- | -- |

- joint - incumbent survival margin **+0.0163 CI[-0.0244,+0.0650] null_p95 0.0488 -- NOT CI-separated** (LOCATED
  NEGATIVE). joint - twin **+0.0650 CI[+0.0244,+0.1138]** (twin collapses -> structure load-bearing).
- Miss ENUMERATION (why chains die, 127 broken edges on non-surviving chains): 55.9% one endpoint extracted, 22.8%
  BOTH extracted but not LINKED (attachment -- the exact-MAP + marginal target), 21.3% neither, 0% pronoun/deictic.
- EVENT-FIGURE binding lifts containment recall 0.2282 -> 0.2519 and position 0.0491 -> 0.0736 (a real, brain-faithful
  per-edge lever; the parent had REVERTED event-grounding because it bound the object, not the located event -- I bind
  the event and it is credited). But per-edge recall stays ~0.25, so the exponent (survival ~= recall^chainlen) is not
  broken. MOVE stays ~0.025 (MOVELINK is the hardest link type -- D'Souza & Ng; the brief's predicted negative).

**CAUSAL -- MAVEN-ERE valid (9698 gold CAUSE+PRECONDITION edges, 710 docs, 34.4% marked, detection held constant):**
| arm | edge recall (all / marked / unmarked) | chain survival (n=30) |
|---|---|---|
| incumbent within-sentence | 0.0044 / 0.0129 / 0.0000 | 0/30 |
| **joint cross-sentence connective** | **0.0052 / 0.0141 / 0.0005** | 0/30 |
| CONTIGUITY floor (no causal signal) | **0.1522 / 0.0518 / 0.2049** | 0/30 |
| shuffled twin | 0.0016 / 0.0048 / 0.0000 | 0/30 |

- joint - incumbent **+0.0007 CI[+0.0003,+0.0013]** (a real but negligible cross-sentence-binding win; the incumbent's
  within-sentence extraction is structurally capped and recovers ~0.4%). joint - CONTIGUITY floor **-0.147
  CI[-0.154,-0.140]** (the connective/causal SIGNAL LOSES to pure density -- the decisive control). joint - twin
  **+0.0035 CI[+0.0024,+0.0047]** (the little MARKED structure is load-bearing). Connective recall on UNMARKED edges
  **0.0005** (~unrecoverable). Multi-hop causal chain survival **0/30 for every arm** -- and there are only 30 >=2-hop
  chains in 710 docs (real causal networks are SHALLOW; reproduces the causal SOLVED's 3.2%-support on the largest gold).

**UPSTREAM (full-stack).** Routed the joint spatial binder through the exact CLE MAP + Matrix-Tree marginals; it
targets the 22.8% attachment slice and eliminates the greedy decoder's invalid-tree fragmenting. Effect on this task
is small (survival 7 -> 8/123; edge recall +0.0016 from the MAP alone) because the spatial wall is construction
coverage, not attachment. NO-regress: the exact-MAP routing leaves the tense-agnostic event set byte-identical (0
symmetric-diff) and the temporal-survival witness passes 6/6 at HEAD; nothing landed in hdlab (Q111).

## 5. HIT-A-WALL, researched to mechanism (the honest decomposition; the brain CAN do this, so the wall is a fidelity gap in a DISTINCT organ)
- **SPATIAL survival is exponent-bound with NO single detection gate.** The temporal win was one gate (tense) -> recall
  0.32 -> 0.76. Spatial recall is bound by the DISTRIBUTED construction inventory + entity coverage (77% of misses) +
  PP-attachment (22.8%), and per-construction returns DIMINISH (the parent's owner-DONE finding, reproduced). The brain
  crosses this with the FULL learned construction inventory + world-knowledge place-hierarchy gap-filling (Louvre-in-
  Paris-in-France is rarely stated) -- a broad-coverage construction+KB organ, not one more rule. Named, not built here.
- **CAUSAL extraction is dominated by UNMARKED, cross-sentence links, and the network is SHALLOW.** A parse-bound
  connective extractor recovers 0.5%; contiguity recovers 15.2% but carries no causal signal (it LOSES-to-contiguity
  control proves the connective typing is not load-bearing over density). The brain infers unmarked causal links by
  DISCOURSE COHERENCE (SDRT: Result/Explanation from causal-world-knowledge, NOT connectives -- the FILED
  `sdrt_discourse_coherence_reader...` organ) and by GENERATIVE SIMULATION of directed causal knowledge (the causal
  SOLVED's U8, the first no-LLM method to beat topical). BOTH are distinct upstream organs; the joint front-end's
  construction/connective extraction structurally cannot supply them. This is EXACTLY the brief's blessed causal
  negative, now measured with power (9698 edges) + the residual organs named.

## 6. PERFORMANCE vs the brain / where we lose signal
A competent reader recovers essentially all clause-local spatial relations, fills unstated place/containment nesting
from world knowledge, and infers unmarked causal links from coherence. We recover ~25% of spatial containment edges
(exponent -> ~6-8% of multi-hop chains survive) and ~0.5% of causal edges via connectives. The itemized
mechanism-diff: (space) we have ~8 constructions + no world-knowledge gap-fill vs the brain's full inventory + KB;
(cause) we bind only marked/within-clause links vs the brain's coherence-driven unmarked inference. Temporal is the
one channel where the wall was a single detection gate we could remove -- which is why it, and only it, won.

## 7. PROPOSED hdlab DIFF (Q111 -- strategy lands it; NOTHING landed by me)
1. **Add the EVENT-FIGURE + PATH/MOVE channels to `hdlab.joint_relation_frontend.joint_spatial_frames`** (default-off
   additive): a locative PP whose parse anchor is a detected event binds the EVENT as Figure; motion verb + goal/source
   PP emits path edges. A real per-edge recall lever (containment 0.228 -> 0.252, position 0.049 -> 0.074) that
   corrects the parent's reverted event-grounding. Do NOT expect it to move whole-subgraph survival (exponent-bound).
2. **Offer `hdlab.arc_parser` exact-MAP + marginals as the shared parse for the joint front-end** (decode='exact',
   want_marginals=True): eliminates invalid-tree fragmenting (the 22.8% attachment slice) and gives a marginal
   attachment-reliability gate. Byte-identical temporal event set (no-regress). This is the full-stack-upstream
   brain-foundational upgrade (globally-normalized parsing; owner-DONE), but its payoff on space/cause is small because
   their walls are elsewhere.
3. **Do NOT land a parse-bound CAUSAL extraction channel as a capability.** It recovers 0.5% of real causal edges and
   loses to a contiguity floor. The causal extraction lever is the FILED SDRT discourse-coherence reader (unmarked
   cross-sentence links) + the causal reasoner's generative simulator (U8, directed world-knowledge) -- distinct
   organs, already located. Wire THOSE, not a connective extractor.
4. **The spatial reasoner should CONSUME a world-knowledge place-hierarchy gap-filler** (the parent's P3/P4 ConceptNet
   fallback, extended to proper-noun places) for the unstated nested-place containment that dominates geographic prose.

## KEY REALIZATIONS (the enabling moves)
- **Whole-subgraph survival is winnable iff there is a SINGLE dominant detection gate AND a gold with multi-hop-chain
  power.** This is the generalizable finding. Temporal had both (tense-gate -> recall 0.32->0.76; MAVEN 43599 chains).
  Spatial's recall wall is distributed (no gate) and its chains are few (123); causal's edges are unmarked (no gate)
  and its multi-hop chains are vanishingly rare (30 in 710 docs). So the metric that PROVED temporal is, by its own
  exponent structure, the one that CORRECTLY reports space/cause as located negatives. The metric is doing its job.
- **Enumerate the misses before theorizing.** My first hypothesis (cross-sentence coref/pronouns fragment spatial
  chains) was REFUTED by enumeration: 0% of broken SpaceEval edges are pronoun/deictic; 22.8% are attachment (a parse
  lever), 77% construction/entity. The enumeration redirected the upstream work from coref to the exact-MAP parser.
- **The parent's reverted event-grounding bound the WRONG node.** SpaceEval gold uses EVENT trajectors ('stayed in the
  home' -> (stay,home)); binding the located EVENT (not its subject) as Figure is credited and lifts recall -- a small
  but genuine brain-faithful correction (Talmy: the Figure can be an event).
- **A contiguity floor is the decisive causal control, not the twin.** The shuffled twin loses (structure matters) --
  but pure contiguity (adjacent events, NO causal signal) recovers 30x more gold edges than the connective signal and
  BEATS it CI-sep. Without the contiguity floor, the tiny connective win over the twin would have read as a positive;
  with it, the honest conclusion is that density -- not causal typing -- carries any causal-edge recall, exactly the
  causal SOLVED's phase-diagram result, now on the extraction side.
- **The largest modern causal gold is still shallow.** MAVEN-ERE has 9698 causal edges but only 30 multi-hop chains --
  so whole-subgraph survival is intrinsically low-power for causal, and the causal SOLVED's 3.2%-support sparsity is a
  property of causal ANNOTATION/language, not of ROCStories. A causal capability must be scored at the EDGE level.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **FRONT-END (sec.1) -- refine the "front-end is the binding constraint" headline PER CHANNEL.** The joint parse-once
  front-end is the RIGHT organ where the extraction wall is a DETECTION gate (temporal: WON). It is NOT sufficient
  where the wall is (a) distributed construction coverage + world-knowledge (SPACE) or (b) unmarked discourse-level
  inference (CAUSE). Measured: spatial containment chain survival 6/123 -> 8/123 (joint exact+event+move) NOT CI-sep
  over the incumbent; causal edge recall 0.5% (connective) vs 15.2% (contiguity, connective loses CI-sep); causal chain
  survival 0/30 (30 chains in 710 MAVEN docs).
- **SPACE (sec.2b).** Confirms the extraction wall is construction coverage + entity coverage (77%) + PP-attachment
  (22.8%), not a single gate; per-construction returns diminish (parent, reproduced). NEW: event-figure binding is a
  real recall lever (containment 0.228 -> 0.252) the parent's revert missed. The exact-MAP parser addresses the
  attachment slice but the survival effect is small (exponent-bound).
- **CAUSE (sec.2b).** The reader's causal EXTRACTION (`_read_causation`) is within-sentence connective+mental, and on
  the largest modern gold it recovers 0.5% of edges; cross-sentence connective binding adds +0.0007 (negligible); the
  causal signal loses to a contiguity floor CI-sep. The residual is the UNMARKED-link discourse-coherence bridge (the
  filed SDRT organ) + directed causal world-knowledge (the causal SOLVED's U8 generative simulator) -- both distinct
  upstream organs, NOT a front-end construction extractor. Multi-hop causal networks are SHALLOW even in MAVEN (30
  chains) -- score causal extraction at the EDGE level, not chain survival.

## 8. ADJACENT COMPONENTS (seeds the next problems -- fidelity + optimization evaluated)
- **The SDRT discourse-coherence reader (FILED, `sdrt_discourse_coherence_reader...`) -- the named causal extraction
  lever.** It infers unmarked cross-sentence causal/temporal relations from coherence, not connectives. This problem
  MEASURES why it is needed (connective extraction recovers 0.5% of MAVEN causal edges; 65.6% unmarked). Its own bound
  is the goal-typed subset; the full-population lever is the generative world-model. Brain-foundational (SDRT/DICE).
- **The causal reasoner's GENERATIVE SIMULATOR (U8, prototyped) -- the directed-causal-knowledge lever.** Beats topical
  CI-sep with no LLM; the deepening (content-sensitive rollout) is the causal reasoner's shared P1. This is the
  correctness axis a contiguity densification cannot supply.
- **A broad construction + world-knowledge place-hierarchy organ (SPACE).** The full locative-construction inventory
  (learned, not N hand rules) + a proper-noun place-hierarchy KB gap-filler (Louvre-in-Paris-in-France). Brain-
  foundational (constructionist inventory + Barsalou simulation). The parent's ConceptNet gap-filler (containment/
  proximity) is the seed; orientation needs perceptual simulation (KB-unreachable, verified).
- **The exact-MAP graded parser (upstream, owner-DONE, landed).** Brain-foundational (globally-normalized parsing;
  Matrix-Tree/Koo). It is the right upstream and should be the default shared parse for ALL joint-front-end channels
  (temporal/spatial/causal/role), but its live payoff is small for space/cause (their walls are downstream of parse
  accuracy). Its marginals are an unused per-arc reliability signal the reader could gate on.

## TLDR (plain English)
We already gave the reader one good "reading step" that pulls facts about TIME out of each sentence, and it worked so
well that whole chains of time-reasoning now survive. This job was to do the same for SPACE and for CAUSE. I built the
same one-pass reading step for both, added the pieces it was missing (reading a location off an action like "stayed in
the home", and reading movement "from X to Y"), and ran it on the biggest modern datasets with the fair test. The
honest result, proven with the scrambled-facts control and a large sample: it does NOT get whole chains of space or
cause reasoning to survive, and I found exactly why. For TIME it worked because there was ONE thing to fix (the reader
ignored anything not in the past tense) and fixing it recovered most facts at once. For SPACE there is no single fix --
the reader knows only a handful of the many ways English says where things are, and a chain needs every link, so it
still breaks. For CAUSE the problem is deeper: real stories almost never SAY "X caused Y" -- the reader is supposed to
INFER it from understanding the world, and a reading step that only catches the word "because" recovers about half a
percent of the real cause links (a "just connect neighbouring events" rule with no understanding actually does better,
which proves the word-based version isn't really finding causes). Getting space and cause right needs two separate
pieces we have already identified and started building: a much broader knowledge of how English describes places (plus
world knowledge like "the Louvre is in Paris"), and a discourse/"what makes sense" step that infers the unstated cause
links. The reading step I extended is a transparent add-on that changes nothing about the existing reader, and it
confirmed -- with a scrambled-facts control -- that where facts ARE recovered they carry real structure.

## QUESTIONS
None blocking. One judgement call for the owner: I filed PARTIAL, not SOLVED. Both channels are the EXACT located
negative the bar names as a FULL PASS (spatial containment survival 6 -> 8/123 not CI-sep, construction/attachment
enumerated; causal edge recall rises CI-sep over the incumbent but the chains die because the links are unmarked, the
SDRT organ named, N=65.6% of 9698 edges), delivered with power, the contiguity + twin controls, and no-regress -- so a
SOLVED reading (rigorous-negative-is-a-pass) is defensible. I chose the deflated label because there is no
CI-separated survival WIN. The science is identical either way.

## NEXT STEPS (priority-ordered)
- **P1 -- WIRE THE SDRT DISCOURSE-COHERENCE READER as the causal extraction lever (not a connective extractor).** This
  problem quantifies the need (connective extraction 0.5% of MAVEN causal edges; 65.6% unmarked; loses to contiguity).
  The unmarked cross-sentence causal link is the discourse-coherence organ's job. Highest-leverage causal lever.
- **P2 -- DEEPEN the causal reasoner's generative simulator (U8) for directed causal correctness** -- the causal
  SOLVED's own P1; the only no-LLM way past the contiguity/topical ceiling (density is free, correctness is the wall).
- **P3 -- a broad construction + world-knowledge place-hierarchy organ (SPACE)** -- the full locative-construction
  inventory + a proper-noun place-hierarchy KB gap-filler for the unstated nested-place containment that dominates
  geographic prose. Target whole-subgraph survival (per-construction returns diminish, so it is one broad organ).
- **P4 -- LAND (Q111) the event-figure + move channels + the exact-MAP shared parse** as additive default-off wires in
  `hdlab.joint_relation_frontend` -- real per-edge recall levers + the brain-foundational upstream, no-regress
  confirmed. They do not move survival (exponent-bound) but they are correct and free.
- **DO NOT re-file:** a parse-bound connective causal extractor (recovers 0.5%, loses to contiguity); more per-spatial-
  construction rules (returns diminish); whole-subgraph SURVIVAL as the causal metric (networks are shallow -- 30
  chains in 710 MAVEN docs; score causal at the EDGE level); a denser causal DATASET (the sparsity is language, not the
  corpus); coref-driven spatial chain repair (0% of SpaceEval broken edges are pronoun/deictic).
