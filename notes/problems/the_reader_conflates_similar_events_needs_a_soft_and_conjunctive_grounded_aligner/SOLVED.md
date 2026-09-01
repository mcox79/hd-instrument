---
problem: the_reader_conflates_similar_events_needs_a_soft_and_conjunctive_grounded_aligner
status: PARTIAL
bar: "PASS = the grounded soft-AND CONJUNCTIVE aligner lifts end-to-end before/after reasoning CI-SEPARATED over BOTH floors -- (a) the SIMILARITY-only floor and (b) the NO-situation-model text-position floor -- on MCScript2 (held-out; report CI half-width + null p95 beside every margin), with the info-free TWIN (an ADDITIVE-only kernel at the same rate, OR a shuffled-order derangement) LOSING CI-separated, AND a can-fail ISOLATED alignment-precision probe passing first: given a PARAPHRASED cue and a set of SIMILAR within-scenario distractor events, the soft-AND kernel selects the RIGHT event CI-separated over both the coarse-cosine and the additive kernels."
result: "END-TO-END (n=301 held-out dev+test symmetric before/after, chance 0.5, passage-cluster bootstrap): the conjunctive-granularity gated aligner scores 0.591 vs SIMILARITY 0.525 (+0.066 [-0.017,+0.149], half-width 0.083, null_p95 0.083, NOT CI-sep) and vs text-position 0.518 (+0.073 [-0.010,+0.152], NOT CI-sep); shuffled-order twin 0.545 (FIX-twin +0.046, NOT sep). It BEATS the verb-only incumbent 0.532 (+0.060 [-0.007,+0.126]). dev 0.660 vs test 0.556 (generalization gap). ISOLATED PROBE (n=52030 items over 138 scenarios, top-1 alignment argmax over the full type inventory): the criterial-feature (particle+2nd-arg) ablation collapses particle-sibling alignment 0.926->0.608 (delta +0.318 [+0.301,+0.337] CI-sep); role-scramble 0.926->0.021 (+0.905 CI-sep). The soft-AND PRODUCT does NOT beat the additive sum (-0.002, NOT sep) -- the brief's specific mechanism is refuted; the FEATURE SET + role structure is the lever."
floor: "SIMILARITY-only floor 0.525 (strongest actually-run for the aggregate before/after contrast); NO-model text-position floor 0.518; both recomputed on the n=301 held-out items with CIs."
controls: "ISOLATED PROBE: particle/2nd-arg ABLATION (drop criterial slots -> alignment collapses, excludes 'any richer code helps'); ROLE-SCRAMBLE twin (wrong role<-filler binding -> collapses, excludes 'more features, not structure'); ANTONYM control (raw grounded cos(in,out)=0.556 vs discrete kernel 0 -> excludes a grounded cosine on the particle slot); kernel sweep coarse/additive(p=1)/soft-AND(p->0)/harder-AND/DG-expand (excludes 'the product combination rule is the lever'). END-TO-END: SIMILARITY floor, text-position floor, SHUFFLED-ORDER twin (excludes 'any ordering'), PARTICLE-BLIND verb-only ablation (excludes 'the conjunctive nodes are not used'), ADDITIVE-kernel arm (excludes 'the product is needed'), committed-covered decomposition (isolates ordering from coverage), per-split held-out, per-construction particle-hinged, and a HIERARCHICAL coarse-backoff arm (a located negative -- coarse premises drown the fine signal)."
files_changed: "experiments/exp_conjunctive_event_aligner_probe_v1.py; experiments/exp_conjunctive_aligner_end_to_end_mcscript_v1.py; experiments/exp_enablement_order_mcscript_v1.py; experiments/exp_conceptnet_causal_order_foundation_v1.py (forward: foundation prototype + offline KB builder); experiments/exp_operator_partial_order_mcscript_v1.py (forward: world-state operator partial-order prototype -> ~99% causally-independent); experiments/exp_construction_integration_reasoner_mcscript_v1.py (forward: Kintsch-CI fusion capstone -> compound wall gated upstream); verification/test_conjunctive_event_aligner.py; notes/problems/the_reader_conflates_similar_events_needs_a_soft_and_conjunctive_grounded_aligner/{SOLVED.md, FORWARD_PROBLEM_PROPOSAL_causal_enablement_foundation.md, research_combination_rule_and_path_slot_2026-09-01.md, research_canonical_script_order_mechanism_2026-09-01.md, research_model_based_simulation_of_script_order_2026-09-01.md}; data/exp_{conjunctive_event_aligner_probe,conjunctive_aligner_end_to_end,enablement_order,conceptnet_causal_order_foundation}_mcscript_v1/metrics.json + data/exp_conceptnet_causal_order_foundation_v1/order_kb.jsonl (offline static asset). hdlab/ UNTOUCHED (proposed diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_conjunctive_event_aligner.py   # 11/11 checks recompute the headline claims (aligner lever + product-refuted + antonym + conjunctive granularity + enablement mechanism) FROM SOURCE"
---

# What I built, what I measured, and how the brief was REFINED

**One-line result.** The brief's proposed mechanism -- a *soft-AND (multiplicative) combination rule* over per-role
grounded similarities -- is **NOT the lever**: a uniform product ties (mildly loses to) the additive sum and the
holistic cosine. The real, brain-faithful lever the wall points to is the **role-structured CONJUNCTIVE event
IDENTITY that includes the criterial PATH/PARTICLE + 2nd-argument slots** -- and, decisively for the end-to-end,
**conjunctive event-TYPE GRANULARITY** (keying each orderable node by the role-filler conjunction so "get IN" and
"get OUT" become *separate* nodes). That granularity is a real lever end-to-end (+0.06 over the verb-only incumbent,
dev 0.66) but does **not clean-clear the floors CI-separated** at n=301; a full decomposition localizes the residual
to the **learned ORDERING signal** (not the aligner), which is a *different* problem.

## The brain frame (opening move, PINNED) and where the finding lands
DG/CA3 **pattern separation by meaning** (PNAS 2026; Yassa & Stark 2011) keeps similar events from colliding; event
identity is a **role-filler CONJUNCTION** individuated by its **arguments + particles** (Carlson 1998 thematic
uniqueness; Zwaan event-indexing -- a change in the SPATIAL dimension starts a new event; SEM/Franklin 2020). A
finer drill (research_combination_rule_and_path_slot_2026-09-01.md) pinned two things that decided the kernel: the
conjunction is multiplicative at the *cell* level (Nosofsky GCM combines per-dimension similarities by a PRODUCT;
Rigotti/Fusi nonlinear mixed selectivity; multiplicative memory-cue combination, Parker 2019), and the path/particle
is a **discrete/categorical** feature (Kosslyn categorical spatial; Landau & Jackendoff closed-class) because
in/out are **antonyms and antonyms are grounded-SIMILAR** (raw grounded cos(in,out)=0.556 -- a cosine cannot
separate them). My measurement upholds the *representation* (a role-structured conjunction over the criterial
features, with a discrete particle) and refines the *combination rule* claim: at the alignment step the product
gives no advantage over the sum.

## What I measured

### 1. The ISOLATED alignment-precision probe (the required can-fail) -- n=52,030 items, 138 scenarios
A paraphrased cue is matched against the FULL scenario event-type inventory; top-1 accuracy on the **particle-sibling
stratum** (targets that have a same-object/different-particle sibling -- the get-IN/get-OUT confusion). Kernels differ
ONLY in the combination rule, holding per-slot grounded sims fixed.
- **THE LEVER (criterial features + role structure): decisive.** Dropping the PATH/PARTICLE + 2nd-arg slots collapses
  alignment **0.926 -> 0.608** (+0.318 [+0.301,+0.337] CI-sep). Binding fillers to the WRONG roles collapses it
  **0.926 -> 0.021** (+0.905 CI-sep). The conjunctive, role-bound, criterial-feature code is what separates.
- **THE BRIEF'S PRODUCT HYPOTHESIS: refuted.** soft-AND product 0.926 vs additive sum 0.928 vs coarse holistic 0.983
  vs DG-expansion 0.996. soft-AND minus additive = **-0.002** (NOT sep). A *uniform* geometric-mean product is even
  mildly brittle (a paraphrased content slot is the weakest link and drags the whole product down). The drill-faithful
  form -- a DISCRETE particle GATE x a graded-robust content match -- matches the additive/coarse, it does not beat it.
- **ANTONYM control:** raw grounded cos(in,out)=0.556, up/down=0.046, on/off=0.270; discrete kernel = 0 -- why the
  particle slot must be discrete, not a cosine.

**Reading of the probe:** at the clean *type* level, alignment is nearly solved by ANY kernel that carries the
criterial features (coarse 0.98, DG 0.996). So "alignment precision at the type level" is NOT the bottleneck the
brief implied -- the bottleneck was that the incumbent's identity **lacked the particle** (and, downstream, that
the schema collapsed the two events into one node). This is the halfway-point refutation the protocol describes.

### 2. END-TO-END before/after through the aligner -- n=301 held-out (dev+test), transitive_ordering read-out UNCHANGED
The genuinely new end-to-end lever is **conjunctive event-TYPE granularity**: p6's near-positive schema keyed nodes by
the **verb lemma only**, so "get IN" and "get OUT" were the SAME node and `transitive_ordering` *could not* order
them regardless of the aligner. Keying nodes by the conjunction fixes that.

| node identity | mean nodes | coverage | accuracy | vs SIM 0.525 |
|---|---|---|---|---|
| verb only (the p6 collapse) | 96 | 0.82 | 0.532 | +0.007 (n.s.) |
| verb + particle | 124 | 0.84 | 0.548 | +0.023 (n.s.) |
| **verb + particle + patient** | 189 | 0.87 | **0.591** | +0.066 [-0.017,+0.149] (n.s.) |
| hierarchical coarse-backoff | 189 | 0.87 | 0.515 | -0.010 (a located NEGATIVE) |

- Conjunctive granularity is a **real lever** (+0.059 over verb-only; beats the verb-only incumbent +0.060
  [-0.007,+0.126]) but does **NOT** clean-clear either floor CI-sep at n=301. Text-position floor 0.518.
- **The kernel is irrelevant end-to-end too:** gated 0.591 vs additive 0.585 vs uniform-product 0.571.
- **The residual is the ORDERING, not the aligner.** On COVERED items (87%): committed 0.594, and it beats the
  **shuffled-order twin** by only **+0.069 [-0.030,+0.167] (NOT sep)**. Given two correctly-identified events, the
  *learned canonical order* is right only ~59% (random ~52.5%). Coverage is not the dilution (committed ~= e2e).
- **Real cues DO reach the fine nodes** (of questions whose text carries a particle, the cue captures it 82%), so
  this is not a cue-extraction artifact -- it is genuinely the weak learned order.
- **Generalization gap:** dev 0.660 (vs SIM 0.476) but test 0.556 (vs SIM 0.551). The signal rides on dev; I do NOT
  claim a capability on the strength of dev alone.
- **The hierarchical fix failed a fair test:** backing off sparse fine premises to the dense verb-level flow
  generated 3697 premises/scenario that *conflict with and drown* the 66 high-quality fine premises (0.515, below
  SIM). The sparse fine premises are higher quality than a dense coarse order -- a real, if negative, finding.

### 3. THE ORDERING WALL, drilled to bedrock (deep drill research_canonical_script_order_mechanism_2026-09-01.md + exp_enablement_order_mcscript_v1.py)
The end-to-end residual is the learned canonical ORDER, so I drilled it to the mechanism level and tested the brain's fix.
- **WHY co-occurrence caps at ~0.59 (PINNED, the strongest result of the whole problem):** the successor representation
  is a GENERALIZATION device that makes co-present states SIMILAR (the same force that conflates events) and
  temporal-context matching is SYMMETRIC -- structurally strong on "belongs-together", structurally weak on
  DIRECTION (Dayan 1993; Schapiro 2016; Gershman & Moore 2012). So ~0.59 (+0.07 over shuffle) is the EXPECTED ceiling
  of ANY co-occurrence/told-order signal, not a tuning miss. Confirmed empirically: the reliability stratification
  found only ~3 pairs/eval with strong direct train consensus and ~67% answered by transitive fill-in; a
  positional-mean prior is WORSE (0.548); more narratives are unavailable (~13/scenario).
- **The brain's fix (PINNED cognitively): CAUSAL ENABLEMENT** (Schank & Abelson 1977 -- each action's effect
  establishes the next's precondition). I built it glass-box (reuse-not-reinvent): a directed ENABLE-edge graph over
  the conjunctive event types (object-availability acquire->use, location-gating enter->act, state-toggle
  open->use, + `hdlab.force_dynamics_lexicon`'s FrameNet CAUSE/ENABLE/PREVENT verb map), edges fed as PREMISES into
  the SAME `transitive_ordering` read-out (one-variable swap: directed causal premises vs symmetric co-occurrence).
- **RESULT -- a located NEGATIVE (n=301):** ENABLE 0.568 does NOT beat COOCCUR 0.591; HYBRID 0.588 ~= co-occurrence;
  the shuffled-order twin loses (0.485). Enable-edges are DENSE (99/scenario vs co-occurrence 66) -- so the research's
  sparsity worry is refuted; the edges simply do not improve the DIRECTION over co-occurrence.
- **The Q2 reframe (answerable=causally-dependent, irreducible=parallel) does NOT hold at glass-box extraction
  recall:** tagging dependency STRUCTURALLY (gold-free) and grading with the co-occurrence order (a different signal),
  only 5% of questioned pairs even share an extractable entity (13/261), and those are answered 0.615 vs 0.593 for
  independent -- a non-significant trend. A strict enable-PATH connects only 2/261 pairs. This is an EXTRACTION-recall
  floor (shallow spaCy misses implicit preconditions/effects + coref), not proof the pairs are truly independent.
- **The ceiling is robust:** EVERY ordering signal caps at ~0.59 (co-occurrence 0.591, enablement 0.568, hybrid 0.588,
  positional 0.548, hierarchical 0.515), and real cues are almost always fuzzy (only 9/261 exactly match a node), so
  the aligner is doing real work (252/261) at committed 0.599 -- the wall is the ORDER, not alignment.

**Definitive attribution:** the ~0.59 ceiling is a KNOWLEDGE-FOUNDATION gap, not a mechanism gap. I understand exactly
how the brain does it (causal-enablement premises into the reused cognitive map) and built that mechanism faithfully;
it does not clear the wall because reliable causal-enablement PREMISES require world knowledge the brain has from rich
embodied experience but that our glass-box, NO-LLM extraction cannot recover from ~13 short narratives (dense but
shallow edges that miss the questioned pairs). Closing it needs an OFFLINE causal-script knowledge FOUNDATION (a
static offline-built asset -- admissible under the FOUNDATION pivot, and the project's stated direction), NOT the
aligner and NOT better statistics on the given text.

## What I did NOT establish
- That the aligner lifts before/after **CI-separated over the floors** -- it does not, at n=301. This is a **located
  near-positive**, not a pass.
- That the **soft-AND product** is the mechanism -- refuted; the combination rule is secondary to the feature set.
- Any capability on **test** (0.556 ~ SIM 0.551); the win is dev-concentrated.
- That the residual **ORDERING** wall is solvable within the aligner's scope -- one brain-faithful attempt
  (hierarchical backoff) failed; better canonical-order induction is a *different* problem (below).

## What I would withdraw first if it turned out to be wrong
The **end-to-end conjunctive-granularity lift (+0.06)** -- it is not CI-separated and is dev-driven. The
isolated-probe findings (criterial-feature ablation +0.318, role-scramble +0.905, product-not-the-lever, antonym
control) are rock-solid, large, CI-separated effects and would survive.

## KEY REALIZATIONS (the enabling moves)
1. **Refuting the brief was the halfway point, and measurement did it.** A power-mean sweep that makes the additive
   info-free twin literally `p=1` and the soft-AND `p->0` on ONE continuous axis showed the product gives no lift --
   so I stopped trying to tune the *combination rule* and looked at what actually separates.
2. **Top-1 argmax is margin-blind; the isolated probe had to be stratified.** Additive and product both put the
   target #1 (positive margin) on easy items; the soft-AND's larger margin only converts to accuracy under
   adversarial competition. Stratifying by the particle-sibling structure, and adding the ablation + role-scramble,
   is what turned a null aggregate into a decisive localization of the lever (the FEATURES, not the rule).
3. **The real p6 bug was upstream of the kernel: the schema keyed nodes by verb only, collapsing get_in/get_out.**
   The "40% mis-alignment" p6 attributed to a coarse cosine was dominated by that node collapse; making the ordering
   node a conjunction is the fix, and it is a representation-level pattern separation, not a similarity-metric fix.
4. **Antonyms break the grounded cosine.** in/out are grounded-SIMILAR (0.556); the criterial spatial opposite must
   be a DISCRETE feature, not a graded cosine -- the drill predicted it and the data confirmed it.
5. **Densifying a sparse ordering with coarse backoff HURTS** -- the few fine premises are higher quality than many
   conflicting coarse ones. The brain's hierarchy is not "lift the coarse order onto every fine pair."
6. **The ~0.59 ceiling has a MECHANISTIC explanation, not a tuning one:** the successor representation is a
   generalization device (makes co-present states similar -- the very conflation force) and temporal-context
   matching is symmetric, so a co-occurrence signal is structurally strong on "belongs-together" and weak on
   DIRECTION. Once the drill named this, I stopped tuning aggregators and tested a categorically-different
   (directed causal) premise -- which is the right move even though it turned out to be an extraction-recall-bound
   negative. Knowing WHY a wall is a wall changes what you build next.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
- **The before/after wall, re-localized again.** p6 localized it to "event-ALIGNMENT precision (coarse grounded
  cosine)". This work REFINES that: at the clean type level, alignment is ~0.98-0.99 for any criterial-feature code;
  p6's mis-alignment was dominated by the **verb-only schema node collapse** (get_in == get_out) plus real-cue noise.
  After conjunctive event-TYPE granularity fixes the collapse, the dominant residual is the **weak learned ORDERING
  signal** (committed 0.594; beats the shuffled-order twin only +0.069), NOT the aligner and NOT the alignment metric.
- **The two-organs framing stands but the fix is different.** `bound_event_backbone` (exact-hash, over-separates) and
  `content_addressable_retrieval` (additive, under-separates) do bracket the answer, but the operative fix is
  **conjunctive event-TYPE identity + a discrete-particle role-structured code**, NOT a soft-AND PRODUCT kernel
  (product ~= additive ~= coarse, measured). `transitive_ordering` reused UNCHANGED as the read-out (witnessed).
- **NEW, deepest fidelity finding (drill-confirmed -- research_model_based_simulation_of_script_order_2026-09-01.md):
  the whole substrate recovers event order by STATIC ORDER LOOKUP; the brain recovers it by GENERATIVE, STATE-
  CONDITIONED SIMULATION.** Comprehension is a rolling forward model that GENERATES the next event (Event Segmentation
  Theory, Zacks/Reynolds 2007); consolidation trains a GENERATIVE sequence model (Spens & Burgess 2024; SEM is run,
  not indexed); order is read off a rollout over a MUTABLE WORLD STATE where each event's EFFECT establishes the next's
  PRECONDITION (Schank & Abelson). Our co-occurrence table, `transitive_ordering` magnitude line, and static causal-KB
  edges ALL lack a mutable world state and a generative policy -- so they can only CORRELATE surface positions, never
  SIMULATE the causal chain. **Adversarial correction (kept honest):** `transitive_ordering` IS the brain's stored
  ordinal line (a legitimate compiled read-out for FAMILIAR material); simulation SUPPLIES the directed premises, it
  does not replace the line. The genuinely missing organ is the WORLD-STATE register + operator (precondition/effect)
  model. And a REPRESENTATIONAL TYPE-ERROR explains the cap precisely: script order is a PARTIAL order (only causally-
  dependent steps ordered; parallel steps free), and a total-order magnitude line must INVENT unrecoverable order for
  parallel pairs -- so the read-out should be fed only causally-dependent edges and ABSTAIN on independent ones.
  HONEST bound (drill calibration): on short everyday-script narratives full mutable-state SIMULATION is likely
  measurably IDLE over a cheaper topological sort of a KB-seeded operator graph (few re-toggles/consumed resources);
  the binding constraint is OPERATOR/DEPENDENCY COVERAGE of the specific event-pairs, which is a KB-seeding build.
- **DEFINITIVE, SELF-CORRECTING finding (exp_operator_partial_order_mcscript_v1.py): the before/after questions are
  ~99% CAUSALLY-INDEPENDENT, so the causal/enablement route is the WRONG fix for the majority.** Built the brain-
  faithful mechanism -- coarse STRIPS-style operators (avail/at/open state predicates) -> enable-DAG -> before/after
  by DAG REACHABILITY with ABSTAIN on independent pairs (the partial order). Result (n=271 decidable): even WITH
  22,710 ConceptNet HasPrerequisite edges added, the DAG connects only **3 of 271 questioned pairs** (coverage ~1%);
  268 abstain (no directed enable-path) and are answered by co-occurrence at 0.587. So these questions are ordered by
  CONVENTION ("shampoo before rinse"), not causal necessity -- which a human reads off a CACHED conventional script-
  order SCHEMA built from massive exposure, NOT by causal derivation. The causal-simulation machinery is brain-
  faithful but STRUCTURALLY IDLE here. The ~0.59 ceiling is therefore a WEAK CONVENTIONAL-ORDER estimate (13
  exposures + direction-blind co-occurrence statistics), and the right foundation is a STRONGER CONVENTIONAL SCRIPT-
  ORDER schema (far more directional exposures / a conventional-order source), NOT primarily a causal-enablement KB
  (which covers ~1%). This CORRECTS this problem's own earlier "causal enablement is the fix" forward hypothesis.
- **FINAL, DEFINITIVE verification (data trace + construction-integration reasoner): the wall is a COMPOUND gated by
  TWO UPSTREAM components, and NO downstream temporal mechanism breaks ~0.59.** Inspecting concrete items showed gold
  = the test story's OWN narrated order for the narrated majority -- yet ordering the story's own events gives only
  ~0.55 because the grounded aligner is NEAR-RANDOM on REAL question cues (nominalizations "the ORDER"<->"ORDERED";
  cross-POS/paraphrase "check PRINTED"<->"PRESENT check"; world-knowledge paraphrase "ask for IDENTIFICATION"<->
  "check his age/license"). Concept/lemma-identity resolution helps (0.549->0.609 on the confidently-aligned subset)
  but the residual paraphrases need the substrate's stage-1 MEANING channel, which the gap-map lists BROKEN. The
  construction-integration reasoner (Kintsch CI fusion of episodic story-order + conventional schema + causal
  operators with improved concept-identity resolution; exp_construction_integration_reasoner_mcscript_v1.py) scores
  0.532 -- fusing near-chance components DILUTES rather than integrates. Across ~10 faithful mechanisms
  (aligner-kernel / granularity / causal-enablement / ConceptNet-foundation / connectives / positional / hierarchical
  / operator-partial-order / concept-identity-alignment / CI-fusion) EVERY ONE caps <= 0.591. CONCLUSION: the aligner
  and the `transitive_ordering` read-out are validated but DOWNSTREAM; the MCScript2 before/after ceiling is gated by
  (1) the BROKEN contextual MEANING channel (event-mention/paraphrase resolution -- stage 1) and (2) missing
  world-knowledge/exposure for CONVENTIONAL order. The true brain-foundational path is UPSTREAM (both are separate,
  already-identified problems), not a further downstream temporal organ.

## PROPOSED hdlab DIFF (Q111 -- NOT landed; NOT load-bearing yet, since it does not clear the end-to-end bar)
1. **Conjunctive event-TYPE identity** for any script/ordering schema node: key by the role-filler conjunction
   (verb, particle, patient) instead of the verb lemma, so pattern-separated events get distinct orderable nodes.
   This is the validated lever (+0.06 end-to-end; the probe's ablation/scramble). Default-off, byte-identical when off.
2. **A role-structured event aligner** (a thin composer over `bound_event_backbone`'s role-filler structure +
   `content_addressable_retrieval`'s graded matching + grounded codes) with a **DISCRETE particle gate x
   graded-robust content** match. NOTE the measured refinement: use the additive/gated form, NOT a uniform product.
   Reuse `transitive_ordering` as the read-out unchanged.
Hold landing until the ORDERING-signal problem (below) is solved -- as infrastructure it is inert without a stronger
canonical order.

## ADJACENT COMPONENTS evaluated for brain-fidelity + opportunity (seeds for the NEXT problems)
Each is named with on-disk evidence, its brain-fidelity verdict, and the leverage it offers -- ranked by value.
1. **THE WORLD-STATE REGISTER -- MISSING, highest value.** The reader tracks entity/event LISTS but has NO mutable
   STATE (predicates have(X)/at(L)/open(X)/clean over the situation, updated by each event's effect, read by the
   next's precondition). Brain-fidelity: LOW (we have no here-and-now state register; the brain's situation model
   centrally does -- Zwaan event-indexing). This is the deepest gap and it unblocks the generative-simulation order
   fix. NEXT PROBLEM: `situation_model_has_no_mutable_world_state_register`.
2. **The canonical-ORDER induction (the located wall).** Currently majority-voted first-occurrence co-occurrence.
   Brain-fidelity: LOW -- static-lookup where the brain runs a generative model. Fix = KB-seeded STRIPS-style
   operators (precondition/effect) joined on state predicates + topo-sort into `transitive_ordering`, ABSTAIN on
   causally-independent pairs. NEXT PROBLEM: `learn_canonical_script_order_from_a_causal_enablement_foundation`
   (proposal drafted here; prototype = a located negative, coverage-bound at 1/301 for flat ConceptNet).
3. **transitive_ordering (the read-out / stored ordinal line).** Brain-fidelity: HIGH for total-order magnitude
   tasks (PINNED cognitive map; reused, twin loses). NEW fidelity finding: it is a TOTAL order, a representational
   TYPE-ERROR for the PARTIAL order of scripts -- must invent order for parallel pairs. OPPORTUNITY: a partial-order
   variant that ABSTAINS on causally-independent pairs (AUDIT UPDATE candidate).
4. **Coreference / entity-tracking (slot E3, NEEDS_ADAPTER -- built, off-path).** My state-predicate/entity join
   covered only ~5% of questioned pairs because pronouns/paraphrase break entity identity with no coref. Brain-
   fidelity: coref IS the brain's entity-tracking (bridging). HIGH leverage: coref-densified state-predicate join is
   a precondition for the operator/foundation approach to reach coverage. NEXT-PROBLEM enabler.
5. **The reader's EXTRACTION / incremental parser (stage READ THE TEXT = WEAK; p2 territory).** The aligner + order
   were tested on clean spaCy because the reader's own extraction is noisy (parses-as-truth). Brain-fidelity: a real
   parse-fidelity gap. It is the UPSTREAM unblocker for wiring the aligner + order into the LIVE reader.
6. **The learner / `script_grain_acquisition_loop` (HARD_FAILED MCScript2).** Brain-fidelity: it is a model-FREE
   statistical script learner -- same symmetric-SR cap I measured. OPPORTUNITY: rebuild as a model-BASED generative
   forward model (operator learning; LOCM/ARMS-style precondition/effect induction).
7. **force_dynamics_lexicon / causation_typing (reused here for enable-verb typing).** Brain-fidelity: PINNED
   (Talmy/Wolff). Limitation: WITHIN-clause, not cross-event/stateful. OPPORTUNITY: lift a force-dynamic outcome to a
   cross-event STATE EFFECT (the operator model's effect predicates).
8. **The grounded meaning channel (stage DECIDE WHAT WORDS MEAN = BROKEN).** The per-slot kernel of the validated
   aligner rides on it; the proven meaning signal is UNWIRED + context-free. Adjacent dependency, not this wall.

## TLDR (plain English)
Our reader keeps getting "did X happen before or after Y" wrong because it confuses similar events like "get IN" and
"get OUT of the shower". I built the brain's fix -- represent each event by its full package (action + the little
direction word "in/out" + the object) and keep the pieces in their own slots -- and I proved, on 52,000 test cases,
that this is exactly what tells similar events apart (remove the "in/out" and it collapses; scramble which piece is
which and it collapses completely). But two of the brief's specific guesses turned out to be wrong, and I could prove
it: (1) it does NOT matter whether you *multiply* the pieces or *add* them -- what matters is that the "in/out" is IN
the package at all and kept as a distinct category (a plain "meaning-similarity" score can't tell "in" from "out"
because opposites look alike to it); and (2) the real reason the reader was failing wasn't a fuzzy matcher -- it was
that its memory of the recipe lumped "get in" and "get out" into one single step, so it literally couldn't put them
in order. Giving each a separate step recovers the earlier near-miss (~0.59, and 0.66 on the dev set) and beats the
old lumped version -- but it still doesn't cleanly beat the simple baselines, and I chased down exactly why: the
last wall is that the reader's *learned order of the recipe steps* is weak (it learns order by watching a dozen
stories, which tell the steps in messy order). Fixing that needs the brain's real trick -- ordering steps by cause
and goal, not by how often one is mentioned before another -- which is a separate build. So: the "tell events apart"
machine is built, brain-faithful, and validated; the brief's "multiply the pieces" idea was a red herring; and the
true remaining bottleneck is now precisely located in a different component (how the recipe's order is learned).

## QUESTIONS
None for the owner.

## NEXT STEPS
1. **The real remaining problem is now drilled to bedrock and it is a KNOWLEDGE-FOUNDATION build, not a mechanism:**
   an OFFLINE causal-script knowledge asset (preconditions/effects per event type, richer than shallow spaCy
   state-change recovery) fed as ENABLE premises into `transitive_ordering`. The in-text glass-box enablement is a
   located negative (0.568 <= 0.591 co-occurrence); the gap is extraction recall of IMPLICIT preconditions/effects,
   which needs a static offline foundation (admissible; the FOUNDATION pivot), NOT an LLM at inference. Open it as a
   distinct problem (`learn_canonical_script_order_from_a_causal_enablement_foundation`), not this aligner.
2. **Land the conjunctive event-TYPE identity** (verb, particle, patient) as default-off schema infrastructure once
   (1) gives it a strong order to separate -- the validated, brain-faithful lever, inert without a good order.
3. **A second temporal population** (another script/order benchmark) to test the dev/test generalization gap and
   power the +0.06 granularity effect that is real-direction but underpowered at n=301.
4. **Enumerate the irreducible slice honestly:** the Q2 reframe could not be confirmed at glass-box recall (only 5%
   of pairs share an extractable entity), so the causally-independent/parallel residual remains UNQUANTIFIED -- a
   richer causal-KB (step 1) is needed to tag it, at which point report it rather than chase it.
