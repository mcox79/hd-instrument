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

## 2. STEP 1 -- DIAGNOSIS: SPLIT VERDICT (mechanism CONFIRMED, cited evidence REFUTED)

Two measurements, both read-only, both reproducible.

Tools: `tools/measure_definitional_pattern_association_v1.py` (over the 634 v2 facts' own
evidence sentences) and `..._v2.py` (over the WHOLE reading corpus, 12,155 sentences -- v1 was
underpowered, only 8/32 labelled pairs had any sentence available).
Detector: `hdlab/definitional_extraction.py` (5 glass-box surface patterns; self-test passes).

### 2a. CONFIRMED -- the grounding signal is definition-BLIND

MEASURED@`data/analysis_definitional_pattern_association_v1/metrics.json:M1_base_rates`:

| quantity | value |
|---|---|
| v2 GROUNDED_MEANING facts | 634 |
| facts whose OWN evidence sentences contain a definitional construction | 371 (58.5%) |
| facts where a definitional construction actually LINKS subject->object | **14 (2.2%)** |
| ... at HEAD strength (object IS the genus term) | 3 (0.5%) |
| bio_new: any-definitional-sentence rate / pair-linked rate | 84.8% / **2.7%** |

This is the decisive number. The definitional evidence is SITTING IN THE EVIDENCE SET of 58.5%
of facts (84.8% in bio) and the cosine mechanism lands on the definitional target 2.2% of the
time. The mechanism is not merely imperfect at using definitions -- it is orthogonal to them.
**The director's core claim ("the signal cannot distinguish 'X means Y' from 'X appears near Y'")
is CONFIRMED, and more strongly than the director stated it.**

### 2b. REFUTED -- the MEANINGFUL hits do NOT come from definitional sentences

MEASURED@`data/analysis_definitional_pattern_association_v2/metrics.json:M2prime_per_label`,
over the previous director's INDEPENDENT v1 bucket labels (32 cross-grounded pairs; labelled by
someone other than this agent, transcribed verbatim from
`notes/foundation_grounding_sample_2026-08-12.md`):

| bucket | n | co-occur in corpus | **linked by a definition** | adjacent COMPOUND TERM | median co-occ sents |
|---|---|---|---|---|---|
| MEANINGFUL | 9 | 9 | **0 (0%)** | 2 (22%) | 7 |
| RELATED | 8 | 7 | **0 (0%)** | 1 (12%) | 3 |
| NOISE | 15 | 12 | **0 (0%)** | 1 (7%) | 3 |

**Zero of 32 -- in EVERY bucket. The stated association does not exist.** The MEANINGFUL pairs
are not definitional at all: `tree->phylogenetic` and `variant->gene` are ADJACENT COMPOUND TERMS
("phylogenetic tree", "gene variant"); `primer->polymerase`, `organelle->cytoplasm`,
`alternation->haploid`, `pinch->invaginat` are tight TECHNICAL COLLOCATIONS inside a constrained
terminology. The director's own worked example (`renal artery: the artery that delivers blood to
the kidney`) is a real sentence type in the corpus -- the bio segment does have 1.5-2.1x the
definitional density of general prose
(MEASURED@`..._v1/metrics.json:M3_segment_definitional_density`: bio 17.7% vs ele_cont 8.4%,
int_cont 9.6%, adv_new 11.6%, bootstrap 12.4%) -- but that modest enrichment is NOT what makes
the bio pairs meaningful. What makes them meaningful is that bio prose co-occurrence is
*terminologically constrained*: in a genetics paragraph the nearest co-occurring word to `primer`
IS `polymerase`, so the co-occurrence signal accidentally lands on a real relation. In news prose
the nearest co-occurring word to `sky` is `status`.

### 2c. What this means for step 3 (stated before building anything)

The premise "cosine cannot read meaning" survives; the premise "definitions are where the
existing meaning came from" does not. So definitional extraction is NOT a story about recovering
signal the current path is fumbling -- it is a bid for a **disjoint** set of facts the current
path never produces (only 14/634 overlap). The honest expected-value estimate is therefore much
LOWER than the director's framing implies, and the coverage question (how many definitional facts
even exist in this corpus) becomes the decisive one. Measured next, before the build.
