---
problem: expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate
status: SOLVED
bar: "For AT LEAST N (solver's choice, N >= 2) high-leverage knowledge TYPES from the inventory: a curated glass-box KB INGESTED THROUGH the consolidation gate + TYPED/LINKED (each fact resolved to the right synset/entity, NOT a raw string) into the frozen store, such that a DOWNSTREAM CONSUMER rises CI-separated over the PRE-INGEST foundation on MODERN gold, with (a) the RAW-ungated info-free twin LOSING CI-separated, and (b) NO regression on the existing consumers."
result: "N=3 knowledge families, each on ITS OWN consumer's MODERN instrument. TYPE 3 (is-a, directed) on TWO consumers: (a) MoNLI lexical entailment n=1676 -- typed directed spoke + monotonicity 0.817 vs the PRE-INGEST symmetric-signature foundation 0.500 (+0.317 CI[+0.299,+0.335]); (b) GUM common-noun COREFERENCE (modern, INDEPENDENT of WordNet -- the non-circular downstream consumer) -- the is-a/part-whole spoke as a type-licensing FILTER on recency lifts coref 0.6883 -> 0.6998 (+0.0116 CI[+0.0056,+0.0182]) over the strongest floor (recency/Centering), building across the wall exp_commonnoun_wall_gum_v1 located and deferred to 'world knowledge'. TYPES 4+6 (part-whole + instrument, directed) on the LIVE bridging instrument: typed spoke bridges COVERED facts 0.926/0.828 vs the symmetric read 0.095/0.027 on confusable distractors (+0.832/+0.801 CI-sep), with a GENERALIZATION located-negative (held-out 0.272/0.203)."
floor: "TYPE 3 / MoNLI: symmetric-signature cosine best-oracle-threshold 0.500 (analytically capped on a balanced directional set) AND a frequency-generality asymmetric heuristic 0.865 (competitive OVERALL but WRONG where it disagrees: on the 226 freq-wrong pairs typed 0.766 MFS / 0.982 union vs freq 0.000 -> the graph is the correct mechanism). TYPE 3 / GUM coref: strongest floor = recency/Centering 0.6883 (blind head-identity, the reader today, is 0.6119). TYPES 4+6: no-inference random 0.200; symmetric hub/MFS read 0.095/0.386 (part) 0.027/0.219 (instrument) on confusable distractors."
controls: "(1) INFO-FREE TWIN loses CI-sep on every type: is-a shuffled-graph 0.499 (vs 0.817); part-whole shuffled-graph 0.214 (vs 0.926); instrument shuffled-graph 0.166 (vs 0.828); coref shuffled-FILTER twin 0.6904 (vs 0.6998, +0.0095 CI[+0.0039,+0.0151]) -- the coref win is CORRECT knowledge, not 'any filter'. (2) NO REGRESSION: spokes are ADDITIVE; the frozen C1 signature is byte-untouched, so diagnostic_context_wsd is unchanged (test_knowledge_factory_meaning_store.py 6/6; W8 asserts store intact). (3) REASONING ablation: dropping monotonicity collapses the is-a negation subset 0.875 -> 0.125. (4) ARCHITECTURE ablation (coref): the is-a spoke as a SELECTOR (0.641) is DOMINATED by recency (0.688); as a type-licensing FILTER on recency it WINS (0.700) -- the consumer's architecture decides whether the knowledge helps. (5) GATE admission quality: schema-margin separates clean from injected-wrong is-a edges AUC 0.942 (deterministic; reuses the upstream meaning_foundation signatures). (6) RESOLUTION guard: the raw lemma-string (union) key over-generates cross-sense is-a on 100% of polysemous nouns; on MoNLI's low-polysemy pairs this does not cost accuracy (union 0.996 >= MFS 0.817), an honest disk-outranks-brief finding."
files_changed: "experiments/exp_isa_typed_spoke_monli_v1.py, experiments/exp_partwhole_typed_spoke_bridging_v1.py, experiments/exp_isa_spoke_commonnoun_coref_gum_v1.py, verification/test_world_knowledge_typed_spokes.py, notes/problems/expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate/SOLVED.md"
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
| 2 | entity instance-of | common-noun coref/entity-KB | GUM coref (modern, on disk) | YES | NEXT (highest new leverage; is-a spoke transfers directly) |
| 9 | event scripts | temporal/predictive | story_cloze, tb_dense, ROC GEK asset on disk | YES (sequence) | NEXT (asset generalized_event_knowledge_roc_fwd.npz exists) |
| 10 | thematic-fit | who-did-what/parser | UD-EWT/QA-SRL | partial | candidate (manifest L2 MAPPED) |
| 5 | attributes | affect/plausibility | Warriner (live) | no | candidate (affect largely covered) |
| 8 | causal | causal reasoner | tellmewhy/tb_dense | YES | candidate (brief warns: often topical-not-substitutable) |
| 11 | social/ToM | ToM/affect | social_iqa, fantom, bigtom | YES | candidate (ATOMIC not on disk) |
| 7 | spatial/typical-loc | spatial | resq/spaceeval | partial | candidate |
| 12 | kinship/role | coref | GUM | YES | candidate (small KB) |
| 13 | numeric/temporal commonsense | duration/quantifier | mctaco | partial | candidate |

PRIORITY for the NEXT problems (my recommendation): (P-a) TYPE 2 entity instance-of for COMMON-NOUN COREF on GUM --
the is-a directed spoke I built transfers DIRECTLY (an entity's type chain resolves "the animal" <- "the dog"), GUM
is modern and on disk, and coref is a scored board consumer; highest new leverage. (P-b) TYPE 9 event-scripts on
story_cloze/tb_dense -- the ROC generalized-event-knowledge asset already exists and event order is directed
(symmetric fails), so a typed event-schema spoke is a clean next win. These two are directed (the strongest case)
and have modern on-disk instruments.

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
- REVISIT downstream consumers to read the new spokes (brain-foundational upgrade): `coref.py`/`commonnoun_binder.py`
  should read C5 (is-a) for common-noun anchoring; `bridging_inference.py` should read C6; `grounded_semantic_graph.py`
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
  is-a edges (AUC 0.948) but abstains on superordinate ones -- so a clean curated KB is admitted by
  provenance+resolution (gate degenerates to keep-all, the proven result) and the schema-margin filters NOISY
  sources. Do not prune a clean taxonomy with a distributional coherence gate.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b / sec 7 -- strategy folds in)
- The meaning-store entry (C1) should note a NEW, measured deviation: the frozen store's SUPERPOSED single
  signature is analytically incapable of DIRECTED/TYPED relational reads (is-a direction: symmetric cap 0.500 on
  MoNLI; part-whole: symmetric fooled below chance on confusable distractors). The brain's ATL organization is
  hub-and-TYPED-SPOKE; C1 realizes only the superposed hub. Fidelity gap = the typed spokes (C5 is-a directed, C6
  part-whole/instrument directed), demonstrated brain-foundational + CI-separated here. The manifest already
  DECLARES hub-and-spoke; the meaning CONSUMERS read only C1's superposition -- that is the gap to close.
- The consolidation-gate entry: schema-margin admission reproduces on a NEW KB (is-a, AUC 0.948) and is confirmed a
  BASIC-LEVEL (Rosch) criterion -- add the note that it abstains on superordinate edges and that a clean curated KB
  is admitted by provenance+resolution (keep-all), the schema-margin filtering NOISY sources.

## TLDR
The reader's world-knowledge store crushes every kind of fact into one "relatedness" number per word, from which
you cannot tell a dog is a KIND of animal (not the reverse) or that a wheel is PART of a car. I re-filed two kinds
of knowledge the way a brain does -- one clean, directed list per kind of fact -- and showed the reader can then do
what it provably could not before. On a modern word-entailment test it goes from coin-flip (the old store is
mathematically stuck at 50 percent on direction) to about 82 percent; and on a "which whole does this part belong
to" test with tempting look-alikes, it goes from worse-than-chance to over 90 percent for facts the knowledge base
knows. Two honest limits: for word-entailment a cheap word-frequency trick is also fairly good on this particular
test (but it is wrong exactly where the real hierarchy and frequency disagree, and there the hierarchy wins); and
the part-whole knowledge does not stretch to brand-new word pairs it has never seen -- for those the reader still
needs its old relatedness sense, so the right design keeps both. Every check that had to fail (a scrambled-knowledge
version, a drop-the-reasoning version) did fail, and nothing the reader already does got worse.

## QUESTIONS
- One labelling call for the owner: I set SOLVED because both knowledge families clear the bar over the PRE-INGEST
  foundation with the required controls (info-free twin loses, no regression), and a directed relation is exactly
  where a typed spoke is provably necessary. A stricter reading could call TYPE 3 PARTIAL on the ground that a
  frequency heuristic (0.865) edges the MFS-resolved spoke (0.817) OVERALL on this WordNet-derived gold -- though
  the graph wins decisively where they disagree (0.766/0.982 vs 0.000) and the sense-agnostic union is 0.996. The
  content is identical either way; only the label moves.

## NEXT STEPS (priority-ranked)
- P1 (strategy, now): land `hdlab/typed_spokes.py` (C5 is-a directed + C6 part-whole/instrument directed) + register
  the two spokes in the manifest + add the HYBRID typed source to bridging_inference (default-OFF -> measure live ->
  flip on if net-positive). Fold the AUDIT UPDATE.
- P2 (highest-value new type): TYPE 2 entity instance-of for COMMON-NOUN COREF on GUM -- the is-a directed spoke
  transfers directly; modern on-disk gold; scored consumer.
- P3 (new type): TYPE 9 event-scripts on story_cloze/tb_dense using the existing ROC generalized-event-knowledge
  asset -- event order is directed, so a typed event-schema spoke is a clean next win.
- P4 (upstream): the HYBRID stored+distributional read for part-whole generalization (the bridging PPR-fuse is one
  realization, already prototyped -- wire it as the C6 generalizer).
- DO NOT re-file: reading-derived growth (closed); curated-store trimming (keep-all is the knee); a symmetric
  representation for a directed relation (provably capped); the bridging headline/PPR-fuse (already prototyped).
