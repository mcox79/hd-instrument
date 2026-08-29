# Research drill: how the brain resolves world-knowledge-decisive reference on real narrative, and WHY our mechanism hit the wall

**Drill run 2026-08-29 (hdi_research, WebSearch + literature). Question set by the SOLVER after measuring the
landed discourse-fact bridge near-DEAD on real LitBank text.** Each claim tagged PINNED-BY-EVIDENCE or SPECULATION.

## The wall, measured first (so the research explains a real number, not a hypothetical)
On real LitBank narrative (100 novels, competitive pronoun references where structural/salience cues FAIL — the
cases that need semantic help, n=1055 in TEST):
- the pronoun's verb is even IN the symbolic KG only **16.9%** of the time;
- a self-extracted TYPE fact for the gold that bridges to that verb exists in only **~5% (copula) to ~11% (any
  nominal)** of them;
- and when a bridge fires it is at **chance (~47%)** — it fires on incidental/wrong-entity nouns and
  light/polysemous verbs (have/hold/carry). On the constructed jig (clean facts + exact edges) the same
  mechanism scores 0.998.

## Q1 — How the brain resolves world-knowledge-decisive reference
- **PINNED (Zwaan & Radvansky 1998; Zwaan, Langston & Graesser 1995 event-indexing):** reference is resolved by
  matching the pronoun's clause into the current SITUATION MODEL (entities-in-events, enriched with role/goal),
  not by a standalone anaphora module over the string.
- **PINNED (Quiroga et al. 2012 Nat Rev Neurosci; concept cells):** entities are carried by hippocampal/MTL
  concept cells — invariant, multimodal, semantically-linked — with delayed reactivation *specifically when a
  relational/comparison check is demanded* (a neural signature of the bridge firing ON DEMAND).
- **PINNED (Lambon Ralph et al. 2017 hub-and-spoke):** the world knowledge the bridge draws on lives in the ATL
  semantic hub as a GRADED, DISTRIBUTED, transmodal code — NOT a discrete edge list.
- **The deciding computation is GRADED, not a discrete selectional-restriction check.** PINNED (McRae, Spivey-
  Knowlton & Tanenhaus 1998 thematic fit; Metusalem et al. 2012 generalized event knowledge): comprehenders use
  continuous verb-role/filler compatibility, activated probabilistically and anticipatorily. **This directly
  indicts our design:** our KG edge (doctor->prescribe) is a boolean lookup; the brain computes a soft coherence
  score over a dense space.

## Q2 — What fraction of natural reference actually NEEDS world knowledge? (the load-bearing point)
- **PINNED that most reference is structurally decidable BY DESIGN.** The Winograd Schema Challenge (Levesque
  2011), GAP, KnowRef, Hard-CoRe were all PURPOSE-BUILT by stripping gender/number/recency cues — they exist
  precisely BECAUSE world-knowledge-decisive cases are the rare, hand-constructed minority in natural corpora.
  This is a communicative-efficiency property: speakers front-load salience/agreement so reference stays cheap.
- **HONEST GAP:** no single clean published corpus number for "% of references where world knowledge is the
  deciding cue"; the literature implies it is LOW (single-to-low-double digits). **Our measured ~17% verb-in-KG
  among the competitive cases is consistent with the semantically-decidable fraction genuinely being small — a
  real property of language, not purely our artifact.**
- **CRUCIAL (Kehler, Kertz, Rohde & Elman 2008):** even the "structural" cases are driven by coherence relations
  + graded inference, not pure morphosyntax. So the semantically-decidable slice is smaller than it looks AND the
  mechanism on it is graded coherence, not KG lookup — both halves say our sparse-symbolic approach is
  mis-specified.

## Q3 — Why the brain succeeds where a 16%-coverage KG + copula extractor fails
- **PINNED:** human semantic memory is DENSE and GRADED (ATL hub; distributional thematic-fit models have broad
  coverage) — "coverage" is never 16%; every verb has a continuous fit profile over every noun. Our sparse KG's
  boolean 16% is the single largest fidelity gap.
- **PINNED (Gernsbacher structure-building; Metusalem et al. 2012):** readers build RICH, multi-attribute
  character models and pre-activate event participants. A copula noun ("Sam is a doctor") captures a vanishing
  fraction of the reader's entity representation — hence our ~5-11% type-fact hit rate is EXPECTED. The brain's
  entity node is a concept cell wired to hundreds of graded associations, not one predicate.

## Q4 — Timing/rarity: is on-demand bridging brain-faithful?
- **PINNED (Haviland & Clark 1974):** bridging inference carries a measurable processing COST; comprehension
  RESERVES inference for when direct integration fails. With the concept-cell "reactivate only when comparison
  demanded" finding (Q1): **"fire the semantic bridge only when structural/salience cues genuinely conflict" is
  the brain-faithful gate.** Our mechanism firing on incidental nouns/light verbs (chance ~47%) is exactly the
  failure of an UNGATED bridge.

## Q5 — Bottom line: three named brain-faithful components (buildable fidelity gaps, NOT an impossibility)
Our result is a RIGOROUS BOUND on a mis-specified mechanism. The absent components:
1. **Dense graded world knowledge** (distributional thematic-fit / semantic-hub continuous coherence) replacing
   the sparse symbolic KG — kills the 16% coverage wall. [PINNED: McRae 1998; Lambon Ralph 2017]
2. **Rich multi-attribute entity/type extraction** replacing the single copula noun — kills the ~5-11% type-fact
   wall. [PINNED: Gernsbacher; Metusalem 2012]
3. **An ambiguity/coherence GATE** that fires the bridge only when structural+salience cues conflict, scored by
   graded coherence not boolean edge-presence — kills the fire-on-incidental chance behavior. [PINNED: Haviland &
   Clark 1974; Kehler et al. 2008]

**SPECULATION (flagged):** the natural-text rate of world-knowledge-decisive reference is likely low enough that
even a PERFECT bridge yields only modest aggregate lift — so the honest headline is "we built the wrong bridge
for a genuinely rare case," and the win to claim is a FIDELITY-CORRECTED bridge measured ON THE COMPETITIVE
SUBSET, not on full-corpus accuracy.

## Sources
- Zwaan & Radvansky 1998, Situation models in language comprehension and memory (Psych Bulletin).
- Zwaan, Langston & Graesser 1995, The construction of situation models (event-indexing).
- Quiroga et al. 2012, Concept cells (Nat Rev Neurosci); "20 years of concept cells" 2026 (Neuron).
- Lambon Ralph, Jefferies, Patterson & Rogers 2017, The neural and computational bases of semantic cognition (Nat Rev Neurosci).
- McRae, Spivey-Knowlton & Tanenhaus 1998, Modeling thematic fit (J. Memory & Language).
- Metusalem et al. 2012, Generalized event knowledge activation during online comprehension.
- Haviland & Clark 1974, What's new? Acquiring new information as a process in comprehension.
- Kehler, Kertz, Rohde & Elman 2008, Coherence and coreference revisited (J. Semantics).
- Winograd Schema Challenge (Levesque 2011); GAP; KnowRef (Emami et al. 2019, ACL); Hard-CoRe.
