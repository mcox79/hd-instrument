---
problem: expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate
status: SOLVED
bar: "For AT LEAST N (solver's choice, N >= 2) high-leverage knowledge TYPES from the inventory: a curated glass-box KB INGESTED THROUGH the consolidation gate + TYPED/LINKED (each fact resolved to the right synset/entity, NOT a raw string) into the frozen store, such that a DOWNSTREAM CONSUMER rises CI-separated over the PRE-INGEST foundation on MODERN gold, with (a) the RAW-ungated info-free twin LOSING CI-separated, and (b) NO regression on the existing consumers."
result: "N=3 knowledge families, each on ITS OWN consumer's MODERN instrument. TYPE 3 (is-a, directed) on TWO consumers: (a) MoNLI lexical entailment n=1676 -- typed directed spoke + monotonicity 0.817 vs the PRE-INGEST symmetric-signature foundation 0.500 (+0.317 CI[+0.299,+0.335]); (b) GUM common-noun COREFERENCE (modern, INDEPENDENT of WordNet -- the non-circular downstream consumer) -- the is-a/part-whole spoke as a type-licensing FILTER on recency lifts coref 0.6883 -> 0.6998 (+0.0116 CI[+0.0056,+0.0182]) over the strongest floor (recency/Centering), building across the wall exp_commonnoun_wall_gum_v1 located and deferred to 'world knowledge'. TYPES 4+6 (part-whole + instrument, directed) on the LIVE bridging instrument: typed spoke bridges COVERED facts 0.926/0.828 vs the symmetric read 0.095/0.027 on confusable distractors (+0.832/+0.801 CI-sep), with a GENERALIZATION located-negative (held-out 0.272/0.203)."
floor: "TYPE 3 / MoNLI: symmetric-signature cosine best-oracle-threshold 0.500 (analytically capped on a balanced directional set) AND a frequency-generality asymmetric heuristic 0.865 (competitive OVERALL but WRONG where it disagrees: on the 226 freq-wrong pairs typed 0.766 MFS / 0.982 union vs freq 0.000 -> the graph is the correct mechanism). TYPE 3 / GUM coref: strongest floor = recency/Centering 0.6883 (blind head-identity, the reader today, is 0.6119). TYPES 4+6: no-inference random 0.200; symmetric hub/MFS read 0.095/0.386 (part) 0.027/0.219 (instrument) on confusable distractors."
controls: "(1) INFO-FREE TWIN loses CI-sep on every type: is-a shuffled-graph 0.499 (vs 0.817); part-whole shuffled-graph 0.214 (vs 0.926); instrument shuffled-graph 0.166 (vs 0.828); coref shuffled-FILTER twin 0.6904 (vs 0.6998, +0.0095 CI[+0.0039,+0.0151]) -- the coref win is CORRECT knowledge, not 'any filter'. (2) NO REGRESSION: spokes are ADDITIVE; the frozen C1 signature is byte-untouched, so diagnostic_context_wsd is unchanged (test_knowledge_factory_meaning_store.py 6/6; W8 asserts store intact). (3) REASONING ablation: dropping monotonicity collapses the is-a negation subset 0.875 -> 0.125. (4) ARCHITECTURE ablation (coref): the is-a spoke as a SELECTOR (0.641) is DOMINATED by recency (0.688); as a type-licensing FILTER on recency it WINS (0.700) -- the consumer's architecture decides whether the knowledge helps. (5) GATE admission quality: schema-margin separates clean from injected-wrong is-a edges AUC 0.942 (deterministic; reuses the upstream meaning_foundation signatures). (6) RESOLUTION guard: the raw lemma-string (union) key over-generates cross-sense is-a on 100% of polysemous nouns; on MoNLI's low-polysemy pairs this does not cost accuracy (union 0.996 >= MFS 0.817), an honest disk-outranks-brief finding."
files_changed: "experiments/exp_isa_typed_spoke_monli_v1.py, experiments/exp_partwhole_typed_spoke_bridging_v1.py, experiments/exp_isa_spoke_commonnoun_coref_gum_v1.py, experiments/exp_antonym_typed_spoke_valence_v1.py, experiments/exp_natural_logic_monotonicity_med_v1.py, verification/test_world_knowledge_typed_spokes.py, notes/problems/expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate/SOLVED.md (also: notes/research_semantic_memory_generalization_walls_2026-09-06.md by the research drill)"
reverify: ".venv/Scripts/python.exe verification/test_world_knowledge_typed_spokes.py"
---

# Expand the clean semantic-memory foundation with world knowledge via the consolidation gate

## 0. THE OPENING MOVE (how the brain does this) and WHAT I FOUND

The brain stores world knowledge as a transmodal ATL HUB with TYPED SPOKES (Lambon-Ralph 2017): concepts are
shared nodes, and each relation (is-a, part-whole, used-for) is a distinct TYPED, often DIRECTED, projection that
a task reads selectively. Taxonomic is-a is a directed hierarchy (Collins-Quillian 1969; Rogers-McClelland 2004)
consulted by monotonicity-respecting inference (natural logic; van Benthem; MacCartney-Manning 2009). This is
PINNED.

The pre-ingest frozen foundation does NOT have this organization. It superposes ALL of a synset's knowledge into
ONE dense 200-d signature (its own witness records sibling cosine 0.932, effective rank 17.4/200 -- the
SUPERPOSITION CEILING). A superposed signature is read by SYMMETRIC cosine, which cannot represent a DIRECTED or
TYPED relation. So the wall the brief names ("the store is thin on world knowledge") has a deeper cause: the
knowledge that IS there (WordNet is-a, ConceptNet relations are already in the C1 bag) is UNREADABLE in typed or
directed form because it is superposed. The brief's own thesis -- "value = CLEAN / TYPED / CORRECTLY-RESOLVED, not
more volume" -- is exactly this.

THE FIX, brain-foundationally: admit world-knowledge relations OFFLINE through the gate as TYPED, DIRECTED,
sense-resolved SPOKES (the phase-diagram move: superposed-dense -> indexed-typed, constraint (e); the manifest
ALREADY declares this hub-and-spoke architecture but only C1's superposed signature is read by the meaning
consumers). I prove this on two knowledge families and specify the hdlab store to add.

## 1. THE PROBLEM IN PLAIN LANGUAGE
A person's memory does not just know a dog and an animal are "related" -- it knows a dog IS a KIND OF animal (one
direction, not the other), and that a wheel is PART OF a car. Our reader has that knowledge crushed into a single
"relatedness" number per word, from which you cannot recover which-is-a-kind-of-which or which-is-part-of-which.
This job re-files the knowledge the way a brain does -- one clean, sorted list per KIND of fact -- and shows the
reader can then answer questions it provably could not before: whether one word entails another, and which whole a
part belongs to when a tempting look-alike is present.

## 2. WHY THIS ONE
The meaning channel is the program bottleneck and its foundation is thin. The proven lift so far came from ONE
knowledge type (lexical sense signatures). This shows the ARCHITECTURAL lever (typed spokes) that lets the OTHER
types pay off, on two of them, with a clean brain mechanism and the load-bearing controls.

## 3. THE TYPES I TOOK, AND WHY (bar item 2 -- the FULL inventory enumeration + priorities follows in sec 7)
- TYPE 3 (is-a / taxonomic, DIRECTED), on TWO consumers -- the cleanest proof of the thesis: a symmetric signature
  is ANALYTICALLY capped at chance on directed entailment, so any win is unambiguously the typed-directed
  organization. (a) MoNLI lexical entailment (the organizational proof; WordNet-derived, so the graph-vs-freq claim
  is defended on the freq-wrong slice). (b) GUM common-noun COREFERENCE -- a REAL downstream consumer on MODERN gold
  that is INDEPENDENT of WordNet, so it is the NON-CIRCULAR consumer win, and it builds directly across the wall a
  prior cell located and left to "world knowledge".
- TYPES 4+6 (part-whole + instrument, DIRECTED) -- the brief's readiest LIVE consumer (bridging_inference, landed
  2026-09-06). Directed relations where the symmetric read is not just capped but FOOLED below chance.

## 4. WHAT I BUILT AND MEASURED

### 4a. TYPE 3 -- the directed is-a spoke on MoNLI (experiments/exp_isa_typed_spoke_monli_v1.py)
MoNLI is a minimal-pair lexical-entailment gold: sentence1 and sentence2 differ by one word (lex1 -> lex2), and the
label flips with the DIRECTION of the taxonomic relation and with NEGATION (upward: taxi entails car; downward,
under negation: not-a-mammal entails not-a-dog). Every subset is exactly balanced (majority 0.500).

- TYPED DIRECTED SPOKE (WordNet hypernym transitive closure, MFS-resolved) + monotonicity: acc 0.817.
- PRE-INGEST symmetric-signature floor (best oracle cosine threshold): 0.500. Proven cap: each lex pair appears
  BOTH directions with opposite labels, so any function of the symmetric cos(a,b) predicts identically for both ->
  exactly 0.5. Margin +0.317 CI[+0.299,+0.335].
- FREQUENCY-GENERALITY asymmetric heuristic (b more frequent than a = more general) + monotonicity: 0.865 --
  competitive OVERALL, because hypernyms are usually more frequent. BUT it is a shortcut, not the mechanism: on the
  226 pairs where frequency predicts WRONG, the typed graph is 0.766 (MFS) / 0.982 (union) vs frequency 0.000.
  Where taxonomy and frequency disagree, taxonomy is right -- the graph is the correct, brain-foundational
  structure (Collins-Quillian), not frequency in disguise. (NON-CIRCULAR.)
- SENSE-AGNOSTIC UNION upper bound: 0.996. This is near-circular (MoNLI is WordNet-derived, so lemma-union closure
  approximates the gold-generation rule) and is reported as an upper bound, NOT the headline.
- SECOND GOLD (less WordNet-circular; med_second_gold_report()): on MED (Monotonicity Entailment Dataset,
  verypluming/MED, FraCaS/GLUE-diagnostic sources) the is-a spoke + monotonicity REPLICATES -- 0.760 CI[0.732,0.789]
  vs majority 0.563 (+0.197 CI-sep) on MED's single-noun-is-a-substitution subset (n=801). NEW quantified COVERAGE
  WALL: that subset is only 14.9% of MED; the other 85% needs FULL natural logic (modifier/quantifier/verb
  monotonicity over the parse -- MacCartney-Manning), the broad adjacent lever the single-substitution judge does
  not reach. So the is-a-spoke win is confirmed on a second gold; the ceiling of THIS mechanism is the lexical-is-a
  slice of monotonicity reasoning.
- INFO-FREE TWIN (shuffled is-a graph): 0.499 -- collapses to chance. The win is the CORRECT edges resolved to the
  right nodes, not "having a graph." Margin +0.318 CI[+0.295,+0.341].
- REASONING ablation (drop monotonicity): the negation subset collapses 0.875 -> 0.125 (below chance) -- the
  directed composition is load-bearing, not mere edge lookup.
- GATE (admission quality on a realistically-noisy source): inject 30% wrong is-a edges (real extracted is-a KBs
  carry ~20-40% errors); the consolidation-gate SCHEMA-MARGIN step (byte-equivalent to consolidate()'s
  discriminative keep, scoring child-vs-parent similarity against random competitors using the UPSTREAM
  meaning_foundation signatures) separates clean from wrong edges AUC 0.948 (basic-level 0.948 / superordinate
  0.943) -- reproduces and exceeds the proven episodic-is-a schema gate (0.868). NOTE: applied to the FULL chain the
  margin threshold prunes some superordinate edges (child/parent distributionally dissimilar -- Rosch 1976
  basic-level effect), so a CLEAN curated KB is admitted by provenance+resolution (gate degenerates to keep-all,
  the proven curated-KB result) and the schema-margin filters a NOISY source.

### 4b. TYPES 4+6 -- the directed part-whole/instrument spoke on the LIVE bridging instrument
(experiments/exp_partwhole_typed_spoke_bridging_v1.py; reuses the exp_bridging_selection_v2 gold + hub)
The bridging task: given a target part/instrument, pick the correct whole/event among distractors. The typed spoke
scores a candidate whole c by the MERONYM-PROTOTYPE cos(hub(target), mean-hub of c's KNOWN parts) fused with graph
reachability -- DIRECTED (uses c's part-set), glass-box, the O(1) consolidated-store read (PINNED).

|                              | part-whole (n=1509) | instrument (n=1112) |
|------------------------------|---------------------|---------------------|
| symmetric RAW_HUB, EASY dist | 0.608               | 0.417               |
| symmetric RAW_HUB, CONFUSABLE dist | 0.095 (BELOW chance) | 0.027 (BELOW chance) |
| symmetric MEAN_FND, CONFUSABLE | 0.386             | 0.219               |
| TYPED spoke, COVERED (in-domain), confusable | 0.926     | 0.828               |
| TYPED spoke, HELD-OUT, confusable | 0.272          | 0.203               |
| INFO-FREE TWIN (shuffled graph) | 0.214            | 0.166               |

- COVERED-PAIR WIN (CI-sep): for facts the KB holds, the typed directed spoke bridges 0.926/0.828 vs the symmetric
  read 0.095/0.027 on confusable distractors (+0.832 / +0.801). The symmetric read is not merely capped -- it is
  FOOLED below chance, because it maximizes GENERIC relatedness and the confusable distractors ARE the target's
  generic neighbours. This is the superposition ceiling again, on a second relation family, and it is the N400
  "specific coherence link vs generically-related" signal. (Circularity caveat: covered pairs are the ingested
  edges, so the typed read is partly a lookup -- but the CONTRAST is against a symmetric read that ALSO has these
  pairs distributionally and still fails, so the win is "typed storage >> distributional storage of the SAME
  facts," the thesis, not a trivial retrieval claim.)
- GENERALIZATION LOCATED NEGATIVE (a full pass per the bar): on HELD-OUT pairs the typed spoke drops to 0.272/0.203
  -- part-whole/instrument do NOT have the smooth distributional geometry is-a-frequency has, so the typed spoke
  alone does not generalize to novel pairs. The measured reason: a whole's meronym-prototype needs OTHER known
  parts, which are sparse. The brain-faithful design is therefore a HYBRID: typed spoke for stored facts +
  distributional read for novel ones (the follow-on; the bridging organ's already-prototyped PPR-fuse is one
  realization -- CITED, not redone).
- INFO-FREE TWIN loses on both (shuffled part-whole graph 0.214/0.166).

### 4c. TYPE 3 on a NON-CIRCULAR downstream consumer -- GUM common-noun coreference
(experiments/exp_isa_spoke_commonnoun_coref_gum_v1.py; reuses experiments/gum_coref.py + the decomposition of
exp_commonnoun_wall_gum_v1, CREDITED)
The prior cell exp_commonnoun_wall_gum_v1 LOCATED the wall: on GUM, anaphoric common-noun mentions decompose into
same_head 0.647 (blind head-identity resolves), name_bridge 0.101 (in-text is-a covers only 0.191; 0.809 "needs
WORLD KNOWLEDGE -- the no-LLM limit"), variant 0.252 (720 different-head common antecedents, also world-knowledge).
It restricted itself to IN-TEXT is-a and left the remainder as the no-LLM limit. But OFFLINE-gated world knowledge
is ADMISSIBLE (the brief's core distinction). So I add a WORLD-KNOWLEDGE typed-spoke resolution path to the SAME
instrument (n=2855 anaphoric-common, GUM test split), MODERN gold independent of WordNet:

| arm | all anaphoric-common | note |
|-----|----------------------|------|
| BLIND head-identity (the reader today) | 0.6119 | prior floor |
| RECENCY (most-recent prior common, any head; Centering) | 0.6883 | STRONGEST floor |
| WK is-a/part-whole spoke as a SELECTOR | 0.6406 | load-bearing (> blind + > shuffled-twin CI-sep) but DOMINATED by recency |
| RECENCY + is-a/part-whole spoke as a type-licensing FILTER | 0.6998 | +0.0116 over recency CI[+0.0056,+0.0182] -- WIN |
| RECENCY + SHUFFLED-filter twin (info-free) | 0.6904 | recency_isa beats it +0.0095 CI[+0.0039,+0.0151] |

- THE WIN (CI-sep, non-circular): the typed is-a/part-whole spoke, used the BRAIN-FAITHFUL way -- as a
  type-compatibility FILTER that licenses recency-ranked candidates (Centering selection + Lambon-Ralph type
  licensing) -- lifts common-noun coref over the strongest floor (recency) on modern GUM. The win survives the
  SHUFFLED-filter twin, so it is the CORRECT is-a knowledge, not merely "restrict to a subset".
- THE ARCHITECTURE LESSON (a control, not a failure): the SAME spoke as a standalone SELECTOR (0.641) is DOMINATED
  by recency (0.688). Coref selection is recency/salience-driven; type knowledge LICENSES, it does not SELECT.
  Whether ingested knowledge helps a consumer depends on the consumer's architecture -- an adjacent-component
  finding that seeds the coref follow-on.
- OPTIMIZATION ATTEMPTS (measured, reproducible via optimization_report(); both LOCATED NEGATIVES): (i) GRADED
  taxonomic re-ranking -- prefer the Wu-Palmer-CLOSEST compatible antecedent instead of the most-recent -- SCORES
  0.6956 < binary 0.6998 (grading HURTS; recency must select, type only licenses). (ii) BROADENED licensing --
  add ConceptNet part-whole relations to the WordNet is-a/part-whole filter -- 0.6988 (-0.0011, CI incl 0, no
  gain). So the recency-primary BINARY WordNet-type-license is at its KNEE. The remaining headroom is the
  name_bridge cases (common noun -> PROPER NAME, "the artist" -> "Zurbaran", 10.1% of anaphoric-common) which
  WordNet cannot reach (proper names are not in it) -- that needs an ENTITY-TYPE KB (Wikidata P31 / DBpedia
  InstanceOf), NOT on disk => the clear next FOUNDATION acquisition (type-2 encyclopedic entity types).

## 5. CONSTRAINTS (bar item 3 -- stated and held)
(a) GLASS-BOX, NO external LLM at inference OR in gold construction. All sources are curated structured KBs
   (WordNet, ConceptNet typed relations) already on disk; MoNLI is a static provenance-pinned gold. HELD.
(b) CLEAN/TYPED/CORRECTLY-RESOLVED, admitted only through the gate; the raw-ungated info-free twin LOSES on every
   type (shuffled-graph 0.499/0.214/0.166). The resolution guard (raw-string key over-generates cross-sense edges,
   100% of polysemous nouns) is demonstrated; its consumer-level cost lands on a context-sensitive consumer, not on
   MoNLI's minimal pairs (honest disk-outranks-brief nuance). HELD.
(c) ONE unified typed store keyed by synset, consumed by directed/typed reads -- NOT siloed dumps: the proposed
   store (sec 8) is keyed by WordNet synset, the SAME hub nodes as C1/C2. HELD (design).
(d) OFFLINE foundation-build, frozen; each type measured on ITS OWN consumer's MODERN instrument (MoNLI for is-a;
   the bridging instrument for part-whole/instrument). 19c NOT used. HELD.
(e) PHASE-DIAGRAM: the store organization is the LEVER here -- superposed-dense (C1) -> indexed-typed-directed
   spokes. Swept the operating point rather than freezing it. HELD.
(f) SEQUENCING: measured through each consumer's own instrument NOW (as the +0.067 was measured through
   diagnostic_context_wsd), independent of the meaning-channel live-wire. HELD.

## 6. NO REGRESSION (bar (b)) and the UPSTREAM component
The typed spokes are ADDITIVE stores keyed by synset; I never write the C1 signature. So diagnostic_context_wsd
(the WSD consumer) and the existing bridging sources (hub/mfnd) are byte-unchanged -- structural no-regression,
witnessed (W8: C1 store intact; test_knowledge_factory_meaning_store.py 6/6 still passes). The UPSTREAM component
in the full stack is the meaning_foundation signature itself: the gate's schema-margin admission SCORES candidate
edges with it (AUC 0.948), so the spoke's admission quality DEPENDS on the upstream signature quality -- both
brain-foundational, both proven. Improving the upstream signature (a separate, proven +0.0755 win) would raise the
gate's admission AUC; it cannot regress the additive spokes.

## 7. THE FULL 13-TYPE INVENTORY, ENUMERATED + PRIORITIZED (bar item 2)
By consumer leverage, instrument availability, and how latent the consumer is. "Directed?" flags whether the
symmetric signature is analytically incapable (the strongest case for a typed spoke).

| # | type | consumer | live instrument on disk | directed? | status after this work |
|---|------|----------|-------------------------|-----------|------------------------|
| 3 | is-a/taxonomic | NLI/coref/categorization | MoNLI (modern) | YES | DONE (WIN, this work) |
| 4 | part-whole | bridging | bridging gold | YES | DONE (covered WIN + generalization located-neg) |
| 6 | instrument/affordance | bridging | bridging gold | YES | DONE (covered WIN + generalization located-neg) |
| 1 | lexical sense sig | WSD/meaning | SemCor/WiC | no | PROVEN (prior: +0.0755) |
| 2 | entity/common-noun is-a | common-noun coref | GUM coref (modern, on disk) | YES | DONE (WIN, this work: is-a spoke as type-licensing filter, +0.0116 over recency CI-sep) |
| 9 | event scripts | temporal/predictive | story_cloze, tb_dense, ROC GEK asset on disk | YES (sequence) | NEXT (asset generalized_event_knowledge_roc_fwd.npz exists) |
| 10 | thematic-fit | who-did-what/parser | UD-EWT/QA-SRL | partial | candidate (manifest L2 MAPPED) |
| 5 | attributes | affect/plausibility | Warriner (live) | no | candidate (affect largely covered) |
| 8 | causal | causal reasoner | tellmewhy/tb_dense | YES | candidate (brief warns: often topical-not-substitutable) |
| 11 | social/ToM | ToM/affect | social_iqa, fantom, bigtom | YES | candidate (ATOMIC not on disk) |
| 7 | spatial/typical-loc | spatial | resq/spaceeval | partial | candidate |
| 12 | kinship/role | coref | GUM | YES | candidate (small KB) |
| 13 | numeric/temporal commonsense | duration/quantifier | mctaco | partial | candidate |

PRIORITY for the NEXT problems (my recommendation): TYPE 2 common-noun coref is now DONE here (the is-a spoke as a
type-licensing filter beats recency CI-sep on GUM). (P-a) TYPE 9 event-scripts on story_cloze/tb_dense -- the ROC
generalized-event-knowledge asset already exists and event order is directed (symmetric fails), so a typed
event-schema spoke is a clean next win. (P-b) TYPE 10 thematic-fit (manifest L2 MAPPED) on UD-EWT/QA-SRL. Both are
directed (the strongest case) and have modern on-disk instruments.

## 8. PROPOSED hdlab CHANGE (strategy lands it -- Q111; NOT landed here)
- ADD `hdlab/typed_spokes.py`: a frozen typed-spoke store keyed by WordNet synset (same hub nodes as C1/C2),
  built OFFLINE through the gate (resolution to synset + schema-margin filtering for noisy sources), exposing
  DIRECTED reads: `isa_ancestors(synset)` (transitive hypernym closure), `entails(lex1, lex2, negated)`
  (monotonicity judge), `holonym_prototype(synset)` / `part_whole_score(part, whole)`. Assets built by the two
  experiment cells' builders; float16, mmap-able, gitignored under data/frontend_assets/ per convention.
- REGISTER two new spokes in knowledge_foundation_manifest.json: C5 "is-a directed taxonomy" (source WordNet
  hypernymy + noisy-KB via gate; consumer NLI/coref) and C6 "part-whole/instrument directed" (source WordNet
  meronymy + ConceptNet PartOf/UsedFor/HasA/MadeOf; consumer bridging). Both keyed by synset, additive.
- EXTEND `hdlab/bridging_inference.py` with a "typed" source: HYBRID = typed part-whole spoke where the whole is
  covered, else the existing hub/mfnd read. Default-OFF until the strategy session measures the live-board impact
  and turns it on (per the no-more-default-off rule: measure the consumer's live metric, flip on if net-positive).
- NO change to C1 (meaning_sense_signatures_v1.npz) -- spokes are additive; WSD is untouched.
- STORE-ORGANIZATION PRINCIPLE (earned by drilling the gate wall; a design upgrade): organize each typed spoke by
  whether its relation is TRANSITIVELY CLOSED. is-a (C5) is a CLOSURE store -- do NOT edge-filter it (pruning any
  clean edge disconnects its ancestors, which broke the gated closure to 0.52); admit by provenance + resolution
  and recompute the closure, using schema-margin only to REJECT wrong edges before closure (edge-level, AUC 0.94 /
  100% wrong-filtered). part-whole/instrument (C6) is a NON-closure typed lookup -- edge-filter freely (no chain to
  break). The gate's ROLE is thus store-type-dependent: schema-margin filtering for non-closure stores; provenance +
  reject-then-close for closure stores. (Consumers that query SPECIFIC pairs, e.g. is-a->MoNLI, are robust to
  scattered KB noise; consumers that AGGREGATE, e.g. confusable bridging, are not -- calibrate the gate to the
  consumer, not globally.)
- REVISIT downstream consumers to read the new spokes (brain-foundational upgrade): `coref.py`/`commonnoun_binder.py`
  should read C5 (is-a) + C6 (part-whole) as a type-licensing FILTER on recency-ranked candidates (DEMONSTRATED here:
  +0.0116 over recency CI-sep on GUM; recency stays the primary SELECTOR -- do NOT use the spoke to select);
  `bridging_inference.py` should read C6 (hybrid: typed where covered, distributional fallback); `grounded_semantic_graph.py`
  (C2, already PPR over the relation graph) can add the DIRECTED is-a projection. `animacy_lexicon.py` already uses a
  narrow hypernym-closure -- it is a proto-typed-spoke and could be unified under C5.

## KEY REALIZATIONS
- THE THIN-STORE WALL IS REALLY THE SUPERPOSITION CEILING. The knowledge is often already IN the C1 signature
  (WordNet is-a, ConceptNet relations are in the bag) but is UNREADABLE in typed/directed form because it is
  averaged into one dense vector. The lever is not more volume -- it is TYPED-DIRECTED organization (the brief's
  own thesis, now mechanized).
- A SYMMETRIC REPRESENTATION IS ANALYTICALLY CAPPED ON A BALANCED DIRECTIONAL TASK (exactly 0.5), and can be FOOLED
  BELOW CHANCE when distractors are generically related. This is the cleanest way to prove a typed-directed spoke
  is necessary -- the floor is provable, not just empirical.
- CHAIN THE FLOORS HONESTLY: a cheap FREQUENCY heuristic is competitive on a WordNet-derived is-a gold (0.865), so
  the win over the symmetric foundation is not enough -- the decisive, non-circular evidence is the FREQ-WRONG
  slice (typed 0.766/0.982 vs freq 0.000), where the graph and the heuristic disagree and the graph is right.
- STORED-TYPED vs DISTRIBUTIONAL ARE COMPLEMENTARY, NOT COMPETING. The typed spoke is authoritative for covered
  facts (O(1) consolidated-store read, PINNED) and does not generalize; the distributional read generalizes and is
  fooled on confusable links. The brain uses both; the hybrid is the design, and "held-out drops" is a located
  negative that MAPS the follow-on, not a failure.
- THE GATE'S SCHEMA-MARGIN IS A BASIC-LEVEL CRITERION (Rosch): it validates distributionally-coherent basic-level
  is-a edges (AUC 0.942) but abstains on superordinate ones -- so a clean curated KB is admitted by
  provenance+resolution (gate degenerates to keep-all, the proven result) and the schema-margin filters NOISY
  sources. Do not prune a clean taxonomy with a distributional coherence gate.
- THE CONSUMER'S ARCHITECTURE DECIDES WHETHER INGESTED KNOWLEDGE HELPS. On common-noun coref, the is-a spoke as a
  standalone SELECTOR (0.641) is DOMINATED by recency/Centering (0.688) -- yet as a type-licensing FILTER on
  recency-ranked candidates it WINS (0.700). Same knowledge, same spoke; the win appears only when the knowledge
  is used the brain-faithful way (LICENSE, do not SELECT). A "the knowledge does not help" reading is an
  architecture artifact until the brain-faithful integration is tested -- and the shuffled-filter twin proves the
  correct edges, not "any filter", carry the +0.0116.

## DEEPENING: WALLS DRILLED FOR MECHANISM + OPTIMIZATIONS ATTEMPTED (this session)
Every wall was drilled >=2x for the MECHANISM (not just the number); a literature research drill on the four open
walls (PINNED-limit vs fidelity-gap) is in flight and will be folded in.
- WALL: the SUPERPOSITION CEILING (core). UNDERSTOOD, not a limit: symmetric cosine is analytically incapable of a
  DIRECTED relation (capped 0.5 on MoNLI direction; fooled below chance on confusable part-whole). Built across
  with typed directed spokes. Independently CORROBORATED by an already-landed organ: hdlab/generalized_event_
  knowledge.py is a typed DIRECTED event-transition spoke (forward PPMI over ROCStories) validated on Story Cloze
  (val 0.592/test 0.582 CI-sep, twin at chance) -- a 4th relation family where the typed-directed-spoke architecture
  works. The architecture is the fix, and it is already precedented in the substrate.
- WALL: PART-WHOLE GENERALIZATION (held-out 0.27). Drilled: (i) density -- denser graph (WordNet meronymy +
  ConceptNet PartOf/HasA/MadeOf) did not lift held-out; (ii) is-a INHERITANCE (Collins-Quillian property
  inheritance: a whole inherits its hypernyms' parts; composes the is-a x part-whole spokes) lifts held-out only
  DIRECTIONALLY 0.2724 -> 0.2843 (+0.0119 CI incl 0). MECHANISM: is-a generalizes by TRANSITIVE closure to the
  right node; part-whole has no transitive closure to the antecedent, so a meronym-prototype cannot discriminate the
  gold whole from the target's own confusable hub-neighbours. Stored spoke is authoritative for COVERED facts; novel
  pairs are the distributional read's job (hybrid). (Reproducible: generalization_report() in the bridging cell.)
- WALL: the RAW-STRING / SENSE-RESOLUTION guard (the brief's load-bearing guard). Drilled 2x: on MoNLI the
  unresolved lemma-union even WINS (0.996) -- WordNet-derived, low-polysemy gold; on GUM coref (a CONTEXT-SENSITIVE
  consumer) the MFS-RESOLVED filter beats the RAW-UNION filter only +0.0028 (CI incl 0). MECHANISM: the raw-string
  key over-generates cross-sense edges on 100% of polysemous nouns (knowledge-level real), but a recency-PRIMARY
  consumer absorbs the over-generation, so the consumer-cost is small unless the consumer is adversarial / high-
  polysemy. (Reproducible: resolution_MFS_resolved vs resolution_RAW_union in optimization_report().)
- WALL: the coref licensing OPTIMIZATIONS. Two upgrades to the +0.0116 filter win, both located negatives: GRADED
  taxonomic re-ranking 0.6956 < binary 0.6998 (recency must SELECT, type only LICENSES); ConceptNet-BROADENED
  licensing 0.6988 (-0.0011 CI incl 0). The recency-primary binary-license is at its KNEE. (Reproducible:
  optimization_report().)
- WALL (FULLY DRILLED): the GATE's consumer-level "raw admission regresses" guard for is-a. I injected 50%
  adversarial wrong is-a edges over the MoNLI vocabulary and measured the consumer: clean 0.8174, RAW-NOISY 0.8186
  (NO regression -- the consumer is ROBUST: scattered wrong edges rarely hit the specific pairs queried), and the
  schema-margin gate FILTERS 100% of the wrong edges at the edge level -- but applying that edge-filter to a
  TRANSITIVE CLOSURE BREAKS it (0.5215; pruning any clean edge disconnects its ancestors). MECHANISM/CONCLUSION:
  the brief's "raw regresses at the consumer" guard genuinely does NOT hold for is-a->MoNLI (robust consumer); the
  gate's value is EDGE-LEVEL (AUC 0.94 / 100% wrong-filtered), NOT consumer-level; and a transitive-closure store
  must NOT edge-filter (filter, then keep the closure of the HIGH-CONFIDENCE + provenance edges). So the is-a
  load-bearing consumer control is the INFO-FREE shuffled-graph twin (which loses), not a raw-noisy regression --
  and this is exactly why the earlier gated-closure demo "backfired": a property (closure fragility + consumer
  robustness), not a bug. (Reproducible: gate_consumer_robustness() in the is-a cell.)
- REMAINING HEADROOM (needs a new KB, not on disk): name_bridge coref (common noun -> PROPER NAME, ~10%) needs an
  entity-type KB (Wikidata P31 / DBpedia InstanceOf). That is the next FOUNDATION acquisition, not a prototype.

### LITERATURE RESEARCH on the walls (PINNED vs fidelity-gap; full note + citations: notes/research_semantic_memory_generalization_walls_2026-09-06.md)
A research drill audited the four walls against the cognitive-science literature. Verdicts, and the MECHANISM tests
I then ran (all reproducible from the cells):
- WALL C (coref recency-primary + type-as-filter): PINNED. Lappin-Leass 1994 (hard filters then salience rank),
  Centering (Grosz-Joshi-Weinstein), Lewis-Vasishth cue-based retrieval -- our architecture is the dominant/default
  account. Coherence-relation cues (Kehler 2008) are future headroom, not a current defect. => our build is correct.
- WALL D (raw-string sense-conflation, small cost): PINNED for the measured near-zero cost. Swinney 1979 /
  Onifer-Swinney (both senses activate immediately; irrelevant sense decays), Duffy-Morris-Rayner 1988 (cost small
  when one sense dominates + context agrees = our low-polysemy regime). Kintsch 1988 construction-integration: the
  brain OVER-generates (union-like) then PRUNES to one sense before cross-sentence inference; our store does
  construction but not integration-at-commit. => deferred fidelity gap (build sense-pruning only when a HIGH-POLYSEMY
  consumer is targeted); our small measured cost is exactly brain-predicted.
- WALL A (part-whole generalization): FIDELITY GAP with a partially-PINNED residual. The brain does NOT use is-a
  transitive closure for meronymy (Collins-Loftus 1975 overturned strict hierarchy; Winston-Chaffin-Herrmann 1987:
  6 subtypes, transitive only within-subtype; Tversky-Hemenway 1984: partonomies shallow, ~5.8 parts basic /
  ~0.4 superordinate; Gentner/Osherson/Sloman: novel-property generalization is similarity-weighted nearest-exemplar
  transfer). I BUILT + TESTED the named replacement (nearest-exemplar similarity-coverage transfer): on held-out
  confusable it scored 0.216 < plain 0.272 (-0.056 CI-sep) -- naive neighbour-part pooling DILUTES discrimination
  where distractors are the target's own neighbours. => meronymy generalization is a genuine partially-pinned limit
  (shallow, subtype-heterogeneous); the stored spoke authoritative-for-covered + distributional-for-novel HYBRID is
  the right design, confirmed by the literature.
- WALL B (basic-level admission gate): PINNED effect (Rosch 1976 cue-validity; superordinates lack shared features;
  Rogers-Lambon-Ralph 2004 coarse-coded, survive degradation longer), but my earlier "gate prunes superordinate"
  was a THRESHOLD artifact, not an AUC failure: schema-margin's RANKING AUC on superordinate edges is fine (0.889;
  basic 0.952); the earlier consumer-collapse came from a fixed margin=0.05 too strict for abstract parents -> a
  DEPTH-AWARE threshold is the fix. The research's proposed consensus-across-known-children check I built + tested
  does NOT beat schema-margin on superordinate edges (consensus AUC 0.889 == schema-margin 0.889). => refine the
  gate with a depth-calibrated threshold; consensus is not needed. (Reproducible: the gate block in the is-a cell.)

### BUILT ACROSS THE MED COVERAGE WALL: GLASS-BOX NATURAL LOGIC over the is-a spoke
(built + validated this session: experiments/exp_natural_logic_monotonicity_med_v1.py; witness W13/W14)
The MED coverage wall (single-is-a-substitution = only ~15% of monotonicity NLI) is a FIDELITY GAP with a PINNED
mechanism: natural logic / monotonicity calculus (van Benthem; Sanchez-Valencia; MacCartney-Manning 2009). I built
it glass-box: (a) MONOTONICITY MARKING self-detected from downward-entailing operators (odd DE-count => downward),
(b) EDIT DETECTION (substitution / deletion / insertion via content-word diff), (c) NATURAL-LOGIC RULES (sub -> is-a
spoke per polarity; DEL upward->entail / downward->neutral; INS upward->neutral / downward->entail). RESULT on MED
(n=5382): coverage 0.855 (up from ~0.15), self-detected-monotonicity acc 0.767 vs majority 0.503 (+0.264 CI-sep)
and vs a SYMMETRIC sentence-cosine oracle 0.535 (+0.232 CI-sep -- distributional similarity cannot do the directed/
structural edit); the SHUFFLED-monotonicity info-free twin collapses to 0.540 (CI-sep -- the POLARITY is load-
bearing, not just the edit type); per-edit sub 0.720 / del 0.766 / ins 0.786. So the is-a typed spoke + natural-
logic composition is a DOWNSTREAM CONSUMER that generalizes from the 15% lexical slice to ~85% of broad monotonicity
NLI, on a modern gold, CI-separated over both a majority and a distributional floor, with the compositional polarity
proven load-bearing.
- MONOTONICITY-MARKER OPTIMIZATION (drilled the residual wall this session): the self-detected marker started at
  0.744 (agreement with gold monotonicity 0.762). Drilling the disagreements showed the failures were (i) MISSED
  operators ("at most", the conditional "if" antecedent) and (ii) OVER-triggering ("a few" is UPWARD not downward;
  blanket "every/all/each/any" over-fired via the restrictor/body asymmetry). Calibrating the marker (add phrase
  operators + "if"; guard "a few"; drop the noisy positional operators) raised agreement 0.762 -> 0.839 and
  natural-logic acc 0.744 -> 0.767. THE RESIDUAL WALL, FULLY DIAGNOSED + 100%-BRAIN-FOUNDATIONAL: the gap to the
  ORACLE-monotonicity upper bound 0.879 is POSITIONAL scope (a universal is downward in its restrictor, upward in
  its body). The brain's mechanism is MacCartney PROJECTIVITY over the SYNTACTIC parse. I built it four ways and
  drilled the WHY:
    (a) LINEAR-scope heuristic: 0.514 -- FAILED (linear position is not syntactic scope).
    (b) SHALLOW-scope (reader POS tagger, subject/predicate split): 0.669 -- FAILED (shallow split over-fires).
    (b2) CLOSED-CLASS + NP-RESTRICTOR chunking (Barwise-Cooper generalized-quantifier restrictor = the operator's
         NP complement, via the reader's own POS tagger; the function-word-grammar approach the neuroscience of
         closed-class processing predicts): 0.672 -- FAILED. Precise restrictor/body helps universals but our NP-
         boundary + per-operator scope (no/few/negation/at-most) is imperfect enough to net-lose vs sentence-level.
    (c) READER'S OWN PARSER projectivity (hdlab.arc_parser+arc_labeler, 100%-brain-foundational, NO external tool):
        0.505 -- UNDERPERFORMS. NOT a bug (its monotonicity decisions agree with a robust parser's 0.811 of the
        time); the reader's UD-EWT parser is OUT-OF-DOMAIN on MED's formal/quantified text (garbles "at most ten
        commissioners..." with a head CYCLE), matching the oracle monotonicity only 0.714.
    (d) MECHANISM CEILING with a robust parser (spaCy, EXTERNAL -> NON-ADMISSIBLE, informational only): 0.810 --
        matches the oracle monotonicity 0.863. This PROVES the mechanism is right and the LEVER is the PARSER.
  CONCLUSION (brain-foundational): the fully-brain-foundational natural-logic headline is the SENTENCE-LEVEL
  CLOSED-CLASS marker (0.767) -- it matches the oracle monotonicity 0.839, MORE robustly than the reader's own
  full parse (0.714), because the brain processes CLOSED-CLASS operators (quantifiers/negation) reliably and does
  not depend on a fragile full content-parse. Neither shallow nor full-parse scope beats it with the reader's own
  tools. The ONE upstream lever to close 0.767 -> 0.810+ is the READER'S PARSER robustness on FORMAL/quantified
  text (a competent reader parses it trivially) -- a parser-improvement build, NOT an external parser (barred) and
  NOT a heuristic (both fail). (reader_parse_projectivity_report [admissible] + parse_projectivity_report [spaCy,
  non-admissible ceiling] in the cell; witness W15.)

### NEW RELATION FAMILY SPOTTED + CONFIRMED (a 5th typed spoke): ANTONYMY (lexical opposition)
(built + validated this session: experiments/exp_antonym_typed_spoke_valence_v1.py)
The symmetric signature is not merely capped on opposition -- it is ANTI-PREDICTIVE: ConceptNet antonym pairs have
HIGHER hub cosine (0.153) than WordNet synonym pairs (0.089), so AUC(symmetric cosine separates synonym from
antonym) = 0.391 (BELOW chance) -- antonyms co-occur in the same contexts ("hot"/"cold" with "weather"). CONSUMER
(grounded in the LIVE Warriner valence lexicon, C3a): on a BALANCED same-vs-opposite-valence discrimination
(majority floor 0.5), the symmetric-cosine ORACLE-threshold scores only 0.547 (~chance -- it cannot tell opposition
from similarity), the shuffled-label twin 0.509, while a typed antonym spoke resolves it (1.000 -- by construction,
so the load-bearing result is the SYMMETRIC FAILURE at 0.547 + the twin at chance, not the typed 1.0). A typed
antonym spoke (ConceptNet Antonym, 19,066 edges on disk) is REQUIRED for opposition-aware valence -- the brain
represents antonymy as a distinct lexical relation (Deese, Murphy, Mohammad), NOT derivable from similarity. This is
a clean next typed-spoke build for the affect channel.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b / sec 7 -- strategy folds in)
- The meaning-store entry (C1) should note a NEW, measured deviation: the frozen store's SUPERPOSED single
  signature is analytically incapable of DIRECTED/TYPED relational reads (is-a direction: symmetric cap 0.500 on
  MoNLI; part-whole: symmetric fooled below chance on confusable distractors). The brain's ATL organization is
  hub-and-TYPED-SPOKE; C1 realizes only the superposed hub. Fidelity gap = the typed spokes (C5 is-a directed, C6
  part-whole/instrument directed), demonstrated brain-foundational + CI-separated here on THREE consumers. The
  manifest already DECLARES hub-and-spoke; the meaning CONSUMERS read only C1's superposition -- that is the gap.
- The consolidation-gate entry: schema-margin admission reproduces on a NEW KB (is-a, AUC 0.942) and is confirmed a
  BASIC-LEVEL (Rosch) criterion -- add the note that it abstains on superordinate edges and that a clean curated KB
  is admitted by provenance+resolution (keep-all), the schema-margin filtering NOISY sources.
- The common-noun coref entry (or exp_commonnoun_wall_gum_v1's located negative): UPDATE -- the "0.809 needs world
  knowledge, the no-LLM limit" is NOT a limit; OFFLINE-gated world-knowledge is admissible, and the typed is-a/
  part-whole spoke used as a type-licensing FILTER on recency lifts GUM common-noun coref 0.6883 -> 0.6998 CI-sep
  (shuffled-filter twin loses). Coref should read the C5/C6 spokes as a licensing filter (recency stays primary).

## TLDR
The reader's world-knowledge store crushes every kind of fact into one "relatedness" number per word, from which
you cannot tell a dog is a KIND of animal (not the reverse) or that a wheel is PART of a car. I re-filed three kinds
of knowledge the way a brain does -- one clean, directed list per kind of fact -- and showed the reader can then do
what it provably could not before. On a modern word-entailment test it goes from coin-flip (the old store is
mathematically stuck at 50 percent on direction) to about 82 percent. On a "which whole does this part belong to"
test with tempting look-alikes it goes from worse-than-chance to over 90 percent for facts the knowledge base knows.
And on a modern text where the reader must tell that "the animal" refers back to "a dog", adding the kind-of
knowledge (used the brain's way, as a filter on the most-recent candidate) beats the best simple rule -- and this
last test is on ordinary text with no connection to the dictionary the knowledge came from, so it answers the main
"did you just look up the answer" worry. Two honest limits: for word-entailment a cheap word-frequency trick is also
fairly good on that particular test (but it is wrong exactly where the real hierarchy and frequency disagree, and
there the hierarchy wins); and the part-whole knowledge does not stretch to brand-new word pairs it has never seen,
so the right design keeps the old relatedness sense too. Every check that had to fail (scrambled knowledge, a
drop-the-reasoning version, a "shuffle the filter" version) did fail, and nothing the reader already does got worse.

## QUESTIONS
- None blocking. I set SOLVED: three knowledge families clear the bar over the pre-ingest foundation with the
  required controls (info-free twin loses on every type, no regression). The one caveat worth flagging is now
  much weaker than in the first submission: TYPE 3's MoNLI gold is WordNet-derived (so its absolute magnitude /
  the union upper bound are near-circular), but the SAME is-a spoke now also wins on GUM common-noun COREFERENCE
  -- a real downstream consumer on modern gold that is INDEPENDENT of WordNet, over the strongest floor (recency),
  with the shuffled-filter twin losing. That non-circular consumer win is the answer to the circularity concern.

## NEXT STEPS (priority-ranked)
- P1 (strategy, now): land `hdlab/typed_spokes.py` (C5 is-a directed + C6 part-whole/instrument directed) + register
  the two spokes in the manifest. Wire them into TWO consumers, default-OFF -> measure live -> flip on if
  net-positive: (i) `coref.py`/`commonnoun_binder.py` as a type-licensing FILTER on recency (DEMONSTRATED win); (ii)
  `bridging_inference.py` as a HYBRID typed source. Fold the AUDIT UPDATE (incl. the common-noun-coref wall update).
- P2 (new type): TYPE 9 event-scripts on story_cloze/tb_dense using the existing ROC generalized-event-knowledge
  asset -- event order is directed, so a typed event-schema spoke is a clean next win.
- P3 (new type): TYPE 10 thematic-fit (manifest L2 MAPPED) on UD-EWT/QA-SRL.
- P4 (upstream): the HYBRID stored+distributional read for part-whole generalization (the bridging PPR-fuse is one
  realization, already prototyped -- wire it as the C6 generalizer).
- DO NOT re-file: reading-derived growth (closed); curated-store trimming (keep-all is the knee); a symmetric
  representation for a directed relation (provably capped); the bridging headline/PPR-fuse (already prototyped); the
  common-noun-coref WALL as a "no-LLM limit" (built across -- offline-gated world knowledge is admissible + wins).
