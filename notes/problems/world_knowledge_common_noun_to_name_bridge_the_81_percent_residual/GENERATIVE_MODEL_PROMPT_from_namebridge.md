# What the GENERATIVE SITUATION-MODEL must do for the name-bridge residual (prompt from the name-bridge solver)

**Source:** `world_knowledge_common_noun_to_name_bridge_the_81_percent_residual` (SOLVED.md, located negative).
This is the ONE job the name-bridge residual proves the generative situation-model must perform, stated concretely
with the instrument, floor, twin, and the exact target subslice -- so the generative-model work can measure a
name-bridge win directly, not in the abstract.

## THE JOB (one sentence)
Resolve a common-noun anaphor ("the country", "the professor", "the mother") to its proper-name antecedent for
entities that appear ONLY in the current document, by building -- ONLINE, as the text is read -- a per-entity
identity file whose accrued TYPE is FINE-GRAINED enough to license the specific anaphor, using generative/predictive
inference over the discourse, NOT a static lookup.

## WHY THIS, AND ONLY THIS, IS LEFT (measured, from the name-bridge SOLVED)
- The retrieval/SELECT mechanism is already near-perfect: hand it the right type and the graded-competition scores
  **1.000** (distractors untyped) / **0.924** (distractors real-typed). So NO mechanism/selection work remains --
  the entire gap is knowledge about the gold entity.
- A static KB is capped: DBpedia + a Wikidata probe FITTED to the exact gold surfaces (an upper bound) lift the
  strong floor only **+0.0084 (not CI-separated)**.
- The wall is COVERAGE of DOCUMENT-LOCAL entities: **30% of gold entities (108/356)** are Betty, Gram, Koinonia,
  Chao, a tiny local town -- present in NO encyclopedic KB, because a human knows them ONLY from this document.
- Coarse discourse typing FAILS (located negative): inferring a coarse PLACE/PERSON flag from predicates
  (locative "in/at X" -> PLACE; agency -> PERSON) HURTS (-0.025, worse than floor) and does not beat its own
  shuffled twin -- because many distractor names are also loc-mentioned/agentive. **The type must be FINE and
  entity-specific**, which for a document-local entity is only recoverable by the full generative model.

## WHAT IT MUST COMPUTE (brain-foundational)
An ONLINE entity-identity file per named entity (ATL Person/Entity-Identity Node filled from the discourse; CLS
hippocampal-episodic route; Heim 1982 file-change; van den Broek Landscape online activation; Kuperberg 2016
generative predictive coding). As each clause is read, the entity accrues a FINE type/role from the STRUCTURED
predicates and relations it participates in -- not a coarse place/person flag, but "has a capital / a president /
borders" => a COUNTRY specifically; "wrote / composed / taught" => author/composer/professor; "my mother / X's
wife" => the kinship role bound to the discourse participant. At an anaphor, retrieve the entity whose accrued fine
identity licenses the anaphor head (cue-based, content-addressable).

The distinction that matters: this is GENERATIVE (the model predicts/infers the entity's kind from the situation it
builds), not a lexical or KB lookup. It is the same organ that must predict the next mention (Wall-2) -- who-is-who
inference -- specialized to yield a fine type that licenses a definite description.

## THE INSTRUMENT + BAR (reuse; measure a name-bridge win directly)
- Instrument: `experiments/exp_namebridge_coref_kb_v1.py` (name-bridge slice, GUM n=356, argmax pick == gold eid).
- Target SUBSLICE (where static KB = 0, so the generative model is the only route): the **108 document-local
  residual cases** -- enumerate via `experiments/exp_namebridge_axis_decomp_v1.py` (the `not_in_kb` + not-in-text
  cases). This is the honest population to beat; a whole-slice number understates it.
- Floors (recompute on the subslice): `kb_thematic` = 0.5843 whole-slice / ~recency on the document-local subslice
  (static KB contributes ~0 there, so recency ~0.34 is the real floor on that subslice).
- BAR: beat the floor CI-separated on the document-local subslice, with the info-free twin (shuffle the
  generatively-inferred types) LOSING, and no regress on the reachable slice. Oracle prize = **0.924** (whole slice).
- AVOID: coarse type flags (located negative here); a bigger static KB (capped +0.0084).

## REUSE (do not rebuild)
- `experiments/exp_wall2_generative_inference_v1.py` (de-leak SOLVED) -- the ACT-R + Centering salience next-mention
  predictor; the harness to extend from "predict a re-mention" to "infer the re-mentioned entity's fine type".
- The online cue-based clustering (`replace_the_entity_gate_gold_coref_inheritance...` SOLVED) -- the entity files.
- `hdlab.state_of_mind` / the WorkingOverlay -- the online situation-model substrate.
- `experiments/exp_namebridge_worldknowledge_v1.py` -- the recognition + phi + graded-competition SELECT to bolt the
  generative type onto (SELECT is proven; only the type source changes).

## SUCCESS = the name-bridge oracle gap closes on the document-local subslice
Perfect knowledge scores 0.924; static KB reaches 0.697 and stops; the generative model's job is the 0.697 -> 0.924
band, which is exactly the document-local 30%. A CI-separated lift on that subslice (twin losing) is the proof the
generative situation-model supplies the fine, online, entity-specific knowledge that no static source can.
