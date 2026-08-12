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

## 3. STEP 2 -- the three mechanical faults

### 3a. STEMMER GARBAGE -- CONFIRMED, ROOT-CAUSED, FIXED

`hdlab/thematic_role_labeler.lemma_verb` is a SUFFIX STRIPPER, not a lemmatizer: it removes
characters whether or not the result is an English word. Root cause of every symptom the
director listed, reproduced directly:

| surface | `lemma_verb` (old) | `lemma_word` (new) |
|---|---|---|
| arteries | `arteri` | `artery` |
| added | `ad` | `add` |
| dressed | `dres` | `dress` |
| status | `statu` | `status` |
| trees | `tre` | `tree` |
| calories | `calori` | `calorie` |
| analyses | `analys` | `analysis` |
| exclusives | `exclusiv` | `exclusive` |
| loses | `los` | `lose` |

`artery -> arteri` is therefore not a near-miss: it is the SAME WORD grounded as itself, and it
escapes the tautology gate only because the two STRINGS differ. This is the mechanism by which
the tautology fix under-counted.

`cal`: NOT a stemmer artifact. `lemma_word("cal") == "cal"` and WordNet has no such lemma -- it
is a genuine corpus token being treated as a concept. The low-information gate (3b) is what
should refuse it; it is listed here so it is not mistaken for a stemming bug.

**HISTORY (checked as instructed): this was already diagnosed and never fixed.**
`notes/tonight_plan_three_ways_over_the_grounding_wall_2026-08-08.md:88` --
"LEMMATIZER MIS-STEMMING: revive->reviv, dwindle->dwindl, corrode->corrod truncate past the
[stem]" -- and line 117 lists "FIX the lemmatizer mis-stemming" as step 1 of the plan. It was
not done. All three of those exact cases are fixed by this change (`revives`->`revive`,
`dwindles`->`dwindle`, `corroded`->`corrode`).

**THE FIX** -- `hdlab/thematic_role_labeler.lemma_word`, with one invariant:
*a normalizer may only shorten a word if the result is ITSELF A KNOWN WORD; otherwise keep the
surface form.* Implemented by delegating to WordNet `morphy` (an already-vendored, already-used
resource -- nothing new is downloaded or trained) with the old suffix rules kept ONLY as a
guarded fallback for out-of-WordNet terms, each rule firing only if its output is a real word.
Out-of-WordNet technical terms are preserved intact (`rubisco` -> `rubisco`), which is correct.

**BLAST RADIUS (deliberately not smuggled):** `lemma_verb` has 105 call sites across 14 hdlab
modules (`goal_typing` alone has 30), all measured under the old stems. So `lemma_word` was
ADDED as the canonical normalizer and only the READING-GROUNDING path was migrated
(`hdlab/reading_grounding_loop.normalize_lemma`, `hdlab/definitional_extraction`). `lemma_verb`
is unchanged and now carries a warning docstring. **Migrating the other 13 modules is a real
follow-up, flagged for the director, not done here.**

KNOWN TRADE-OFF, stated rather than hidden: `lemma_word` asks WordNet noun-first, so
`running` -> `running` (the noun exists) where the old stripper gave `run`. Deverbal `-ing`
nouns are the one class where the new normalizer is less aggressive. Noun-first was chosen
because this corpus's vocabulary is noun-dominated; it is a judgement call, and reversible.

### 3b. `people` AS AN OBJECT -- CONFIRMED (20 facts, not 6), FIXED PRINCIPLEDLY

Measured: `people` is the object of **20** of the 634 facts (the director saw 6 in the 50-row
sample). Principled criterion chosen, and two rejected with evidence
(MEASURED@`data/analysis_threshold_lowinfo_v1/metrics.json`):

- REJECTED "flattest closed-class word by document frequency": the closed-class lexicon spans
  the whole frequency range, so its minimum is `forty` (df=5); that threshold refused 7293
  open-class lemmas including `nephron` and `polymerase`. Caught by the control words.
- REJECTED any pure DF/IDF rule: in a corpus about cells, `cell` (df=1439) is frequent AND
  maximally informative while `people` (df=2019) is frequent and empty. DF cannot separate them.
- ADOPTED, calibrated off the gate the project ALREADY accepts: the closed-class lexicon is the
  operational definition of "a word that says nothing", so measure the PMI a TYPICAL FUNCTION
  WORD has with these subjects and refuse any object no more informative than that. Measured
  closed-class reference PMI p50=0.96 / **p75=2.10** / p90=3.33. At the p75 floor:
  **all 20 `X -> people` facts are refused, and every known-meaningful pair survives**
  (primer/polymerase 9.1, aorta/artery 9.8, nephron/kidney 8.7, cholesterol/lipid 6.2,
  organelle/cytoplasm 6.6, tree/phylogenetic 7.0).

`hdlab/low_information_filter.py`. No blacklist; the floor is read off the corpus.

**AND A WARNING I am putting in writing because it would be easy to misuse:** PMI is a
LOW-INFORMATION gate, NOT a meaning-quality score. Measured: `shed -> quirky` scores PMI 9.9 and
`austria -> girlfriend` 8.8 -- ABOVE every known-meaningful pair -- because PMI rewards rare
co-occurrence. Anyone who reaches for PMI as a quality ranking will reproduce exactly the error
this exercise is correcting. Honest scope note also recorded in the module: the gate assumes a
meaning CO-OCCURS with what it means (automatic for definitions, an extra assumption for the
distributional path, where `artery`/`vein` similarity without co-occurrence is the point).
Measured consequence if applied to the existing store: 634 -> 293 facts.

### 3c. best_cos CLUSTERING AT 0.45-0.48 -- INVESTIGATED, THRESHOLD **NOT** CHANGED

Accepted-cosine histogram (n=634): [0.45,0.48)=252, [0.48,0.50)=95, [0.50,0.55)=144,
[0.55,0.60)=86, [0.60,0.70)=44, [0.70,1.0)=13. The clustering is real: 55% of all accepted facts
sit in the first 0.05 above the threshold.

Two nulls were tried and BOTH are invalid; recorded rather than quietly dropped:
- LABEL-PERMUTATION null is vacuous -- relabelling anchors does not change the geometry, so
  every row still finds its own vector and the null max is 1.0 by construction.
- IID-RESAMPLING extreme-value null overstates the max (null p50=0.79 EXCEEDS the real p50=0.54,
  which is the tell): a lemma's cosines are not independent draws from a pool that already
  contains every other row's upper tail.

The question is settled WITHOUT a null, by measuring how discriminating the threshold is:

| statistic | value |
|---|---|
| all-pairs cosine pool percentiles | p50=0.176, p90=0.411, **p95=0.491**, p99=0.638 |
| median anchors clearing 0.45 per lemma | 6 (mean 101 -- heavy-tailed; 44.7% of lemmas have >=10 candidates) |
| **argmax top1-minus-top2 margin, median** | **0.0147** |
| fraction of lemmas whose margin is below 0.02 | **0.593** |
| fraction below 0.05 | 0.805 |

**Reading:** 0.45 sits at roughly the 92nd percentile of ALL word-pair cosines, so it admits the
top ~8% of a purely topical similarity distribution. More decisively, for 59% of words the
winning anchor beats the runner-up by less than 0.015 cosine -- **the identity of the assigned
meaning is decided by noise.** Raising the threshold does not fix that: it reduces HOW MANY words
get grounded without making WHICH anchor wins any less arbitrary. Sensitivity, reported as
required: 0.48 keeps 382/634 (60%), 0.50 keeps 287 (45%), 0.55 keeps 143 (23%), 0.60 keeps 57
(9%). **THRESHOLD LEFT AT 0.45.** There is no independent justification to move it, and moving
it to make the audit look better would be fitting to the test.

## 4. STEP 3 -- DEFINITIONAL EXTRACTION BUILT AND RUN (result pending HUMAN B3)

Pre-reg (committed BEFORE the run, `7d937bf6b`): `preregs/2026-08-12_definitional_grounding_v3.md`
Cell: `experiments/exp_definitional_grounding_v3.py`  (self-test PASS, smoke PASS, FULL 35.7s)
Metrics: `data/exp_definitional_grounding_v3/metrics.json`, verdict `STRUCTURAL_PASS_PENDING_B3`

### Reused vs built (query-before-build, per the documented reinvention failure mode)

`python tools/capability_registry_query.py --serves "definitional sentence extraction copula
appositive parse"` -> **0 / 107 rows match**. Manual scan of all 107 registry rows for
parse/coref/frame/thematic organs found: `typed_rule_parser`, `coreference_resolver`,
`frame_induction`, `parse_goal_extraction`, `thematic_role_labeler`, `animacy_lexicon`. None
exposes a bare NP-head or definitional-construction API.

| REUSED (imported, unmodified) | BUILT NEW |
|---|---|
| `thematic_role_labeler.lemma_word` (extended by me, then reused) | `hdlab/definitional_extraction.py` -- 5 surface patterns + NP-head + guards |
| `closed_class_lexicon.is_closed_class` | `hdlab/low_information_filter.py` -- PMI gate calibrated off the closed-class lexicon |
| `hd_fact_store.HDFactStore` (real store, n_dim=2048, sharded) | the 3-arm harness |
| WordNet (already vendored; used by `animacy_lexicon`) | -- |
| the cycle-1/cycle-2 corpus loaders, verbatim | -- |

The ~20-line NP-head heuristic is the one place I wrote shallow syntax rather than reusing a
parser, because no owned organ exposes that API; it is documented as deliberately shallow.

### Arm sizes (MEASURED@data/exp_definitional_grounding_v3/metrics.json)

| arm | facts | note |
|---|---|---|
| DIST_ASIS | 634 | hand-scored 8% / 26% / 66% |
| DIST_LOWINFO (CONTROL) | 290 | refusals: 296 NEVER_CO_OCCURS, 48 LOW_INFORMATION_OBJECT |
| **DEF** | **1751** | **1749 of them NOT produced by the distributional path** |

DEF pattern mix: COPULA 722, APPOSITIVE 583, CALLED 458, GLOSSARY_COLON 57, REFERS_TO 9.
DEF segment mix: bio_new 1022, bootstrap 315, adv_new 182, int_cont 173, ele_cont 137.
DEF attestations: 1452 facts seen once, 248 twice, 125 three times.
DEF refusals: 434 LOW_INFORMATION_OBJECT, 9 CLOSED_CLASS_OBJECT, 1 NEVER_CO_OCCURS.

**COVERAGE IS NOT THE BLOCKER, contrary to what I expected in section 2c.** Definitional
constructions are NOT rare in this corpus: DEF banks 2.8x more facts than the distributional path
(1751 vs 634) at 35 seconds of CPU. The honesty caveat I pre-registered therefore lands the OTHER
way from the way it was framed: this is a high count, so the risk is not "high rate on 40 facts",
it is that a low rate on 1751 facts still beats 8% on 634 in ABSOLUTE terms. Arithmetic, stated
now so it cannot be spun later: DIST_ASIS yields ~51 meaningful facts (0.08 x 634). DEF needs
only **2.9%** MEANINGFUL to match that absolute count. **So the absolute-count comparison is
nearly uninformative here and the RATE band is the one that matters.** Read the pre-reg bands on
the rate; treat any absolute-count win as expected rather than as evidence.

### Two extractor faults fixed BEFORE any scoring (disclosed so the sequence is auditable)

Eyeballing the first generated sample (NOT scoring it) showed two systematic false-positive
classes, both fixed and regression-tested before the final run: (i) sentence-initial ADVERBIALS
and SUBORDINATE CLAUSES read as appositives (`Additionally, the gradual melting ...` ->
`additionally -> melting`; `While this might sound like an exaggeration, ...`); (ii) non-nominal
definienda (`disappoint -> prequels`). Fix: a definiendum must be a WordNet NOUN or absent from
WordNet entirely (technical terms and proper nouns must pass -- `arthropoda`, `rubisco` are
exactly the words a reader needs defined). Effect: 1829 -> 1751 facts. This happened BEFORE any
MEANINGFUL/RELATED/NOISE judgement was made, so it is bug-fixing, not fitting to the test; had I
scored first and then fixed, it would have been the latter.

### NOT SCORED HERE

`data/exp_definitional_grounding_v3/b3_audit_sample_DEF.json` (50 rows, seed=42, sampling
bit-identical to the v2 B3 procedure and asserted so in the cell's self-test) and
`..._DIST_LOWINFO.json` are written for the DIRECTOR to hand-score. The cell assigns no buckets
and claims no band. Residual noise IS visible in the DEF sample by eye
(`afghanistan -> catch`, `annelid -> indicate`) alongside clean hits (`anion -> ion`,
`anus -> opening`, `cadmium -> metal`, `antigen -> molecule`, `anther -> structure`); I am
deliberately not converting that impression into a number.
