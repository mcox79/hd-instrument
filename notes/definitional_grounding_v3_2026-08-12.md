# Definitional grounding v3 -- 2026-08-12 (exp_dev, incremental)

Status: IN PROGRESS. Written incrementally; committed after each discrete change.

Task: (1) confirm/refute the director's diagnosis that the grounding signal is same-sentence
cosine co-occurrence and cannot separate "X means Y" from "X appears near Y"; (2) fix three
mechanical faults (stemmer garbage / `people` low-information object / best_cos threshold
clustering); (3) build definitional extraction as a SECOND grounding signal alongside the
existing one so the two can be compared. Pre-register bands; do NOT auto-score B3.

## 0. Prior-work check (MANDATORY, substrate-KB concept query)

`bash tools/substrate_query.sh "definitional extraction copula appositive glossary definition
sentence pattern grounding meaning"` -> confidence 0.4355, top hits above cosine 0.30:

1. `definition` (cosine 0.4355) -- generic WordNet/atoms lexical entity, not an arc cell.
2. `definition_composition_grounding_probe_v1` (cosine 0.4355) --
   `data/exp_definition_composition_grounding_probe_v1/metrics.json`, verdict MEASURED.
   READ (`experiments/exp_definition_composition_grounding_probe_v1.py` docstring): tests whether
   a WordNet GLOSS, composed over already-grounded content words, supplies an OOV outcome-VERB's
   result-VALENCE. It reads a DICTIONARY ENTRY fetched from WordNet; it does not read the corpus.
3. `dictionary definition` / `dictionary_definition` (0.4111) -- WordNet lexical entries.

**Prior-work verdict: RELATED-BUT-DISTINCT, not a rediscovery.** The shared idea is "a definition
reduces an unknown word to known words". What is new here is the SOURCE: extract the definitional
structure from the RUNNING TEXT the substrate is reading (copula / appositive / glossary-colon /
"called" / "known as" / "refers to"), rather than looking the word up in an external gloss
resource. The v1 probe presupposes a dictionary exists for the target; the reading loop has no
such oracle and must find definitions in the corpus itself. Reported per the concept-query rule.

## 1. State verified on disk (not taken on trust)

- `04b922c0e` "grounding quality fix: refuse tautologies + closed-class fillers, add per-fact
  provenance" is HEAD-1. Cell: `experiments/exp_reading_grounding_loop_cycle3_groundingfix_v1.py`.
- `data/exp_reading_grounding_loop_cycle3_groundingfix_v1/metrics.json`:
  verdict `STRUCTURAL_PASS_PENDING_B3`,
  `B1_taut 0.656885->0.0  B2_cc_obj 0.040068->0.0  B4_grounded 3544->634  B5_prov 0.0->1.0
   B6_v1_loads=True`. B3 explicitly NOT auto-scored -- correct.
- `data/foundation/reading_grounding_v2_qualityfix/grounding_provenance.jsonl` = 634 rows, each
  carrying `subject / object / segment / best_cos / n_exposures / schema_score` AND an `evidence`
  list of `{episode_id, pass_idx, sent_id, sentence}` -- i.e. source sentences ARE recoverable in
  v2 (they were NOT in v1). This is what makes the diagnosis testable at all.
- The pre-registered B3 sample is `data/exp_reading_grounding_loop_cycle3_groundingfix_v1/
  b3_audit_sample.json` (50 rows, seed=42 over GROUNDED_MEANING fid order). The director's
  hand-scored labels (8% / 26% / 66%) are **NOT persisted anywhere on disk** -- only the
  aggregate is reported in the spawn prompt. Consequence for step 1: the only per-row labelled
  data available to me is the v1 audit in `notes/foundation_grounding_sample_2026-08-12.md`
  (50 mixed rows + 20 cross-only rows, bucketed by the previous director).
