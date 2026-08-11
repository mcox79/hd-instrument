# Pre-registration: relation_canonicalization_learned_v1

## Context / motivation

`exp_representation_canonicalization_v1` (commit e65de60f1, HARD_PASS) realized the USER's
"same representation regardless of wording" principle for ENTITIES via a LEARNED mechanism
(`canon_entity` + `hdlab.lexical_similarity.concept_similarity`, fuzzy-collapse onto a known
anchor via graded cosine >= threshold), but for RELATIONS it used a hand-authored alias table.
Per the charter ("glass-box != hand-rules; earn the mechanism, don't hand-code it"), this cell
EARNS the relation-canonicalization the SAME way entities were earned: cluster/classify surface
relation-markers into canonical relation classes (PART_OF/PRODUCES/CONSUMES/MOVES) via
verb-similarity, reusing the OWNED `hdlab.verb_lexical_similarity` shared-feature FHRR
bundle-cosine organ (the SAME mechanism class already used for entities and for verb outcome/goal
typing), instead of a literal `marker -> canon` dict lookup.

## Step-0 honest re-read (task premise correction, disclosed before designing anything)

The task brief names `RELATION_DIRECTION_TABLE` as "the" hand-authored alias table. On disk
inspection (`grep -n "RELATION_DIRECTION_TABLE\|KB_ROLE_TO_CANON"
experiments/exp_representation_canonicalization_v1.py`), `RELATION_DIRECTION_TABLE` is DECLARED
(lines 131-141) but never referenced again anywhere in the 843-line file -- it is dead/vestigial
documentation, not the live mechanism. The ACTUALLY-EXECUTED hand-authored relation-class mapping
is two things: (a) `KB_ROLE_TO_CANON = {"produces": CANON_PRODUCES, "consumes": CANON_CONSUMES,
"moves": CANON_MOVES}` (line 142, used at line 198), and (b) the canonical-class constant is
literally hard-coded as a return value inside each `extract_*_triple` function (e.g.
`extract_cskg_triple` / `extract_composes_triple` / `extract_partof_triple` all directly
`return (material, CANON_PART_OF, whole)`; `extract_kb_paraphrase_triple` receives `canon` as a
parameter chosen by its caller from a dict keyed literally by `CANON_PRODUCES`/`CANON_CONSUMES`/
`CANON_MOVES`). The task's underlying diagnosis is still correct (relation-class identity is
hand-authored, unlike the learned entity path) -- only the specific artifact name is corrected.
This cell replaces BOTH the unused `RELATION_DIRECTION_TABLE`'s intended semantics and the live
`KB_ROLE_TO_CANON` + hard-coded-per-function canon literals with one LEARNED lookup.

## Prior-work check (mandatory, per exp_dev discipline)

`bash tools/substrate_query.sh "learn relation canonicalization surface marker verb similarity
clustering held-out generalization"` -- top hit cosine=0.4248 (`entity='generalization'`, a
generic WordNet/atoms concept-node entry), on inspection an unrelated dictionary-definition hit,
not substantively about learning a relation-class mapping from verb similarity. Supplementary
`grep -rli` scan of `preregs/ experiments/ notes/` for relation-canonicalization + verb-marker
terms returns zero hits outside this arc's own parent cell. This is novel, additive work building
on e65de60f1, not a rediscovery.

## Mechanism (reuse owned organs, additive extension of hdlab/verb_lexical_similarity.py only)

**hdlab/verb_lexical_similarity.py additive extension (new DATA + 1 new generic function; zero
lines of existing code changed; existing `self_test()` untouched -- its own coverage loop
hardcodes `("outcome", "goal")`, so registering a 3rd "relation" domain in `_DOMAINS` does not
change its behavior at all, byte-identical regression):**
- `RELATION_MARKER_FEATURES` -- a McRae-style hand-tagged feature lexicon for relation-marker
  words (verbs/relation-phrases naming a fact's predicate), SAME shared-feature-cosine convention
  as `OUTCOME_VERB_FEATURES`/`GOAL_VERB_FEATURES` in the same file. FOUR independent axes (citing
  the SAME linguistic-theory families this file already cites elsewhere, for continuity):
  1. `RELATION_TEMPORALITY` (`STATIVE_RELATION` | `EVENT_RELATION`) -- Pustejovsky 1995 Generative
     Lexicon qualia structure: CONSTITUTIVE role (part-whole, atemporal) vs AGENTIVE/TELIC roles
     (process-linked, temporally-bound).
  2. `MATERIAL_FLOW_DIRECTION` (`NONE_NO_FLOW` | `SOURCE_CONSUMED` | `GOAL_PRODUCED` |
     `PATH_TRAVERSED`) -- Talmy 1985 Source-Path-Goal motion-event schema (already cited in this
     file's OUTCOME domain for force-dynamics).
  3. `AFFECTEDNESS_POLARITY` (`SCALE_NA` | `SCALE_DOWN` | `SCALE_UP` | `SCALE_NEUTRAL`) -- Beavers
     2011 scalar affectedness (same citation already used in this file's `SCALE_DIRECTION` tag).
  4. `LEXICAL_REGISTER` (`FORMAL_TERM` | `COLLOQUIAL_TERM` | `NEUTRAL_TERM`) -- an INDEPENDENT
     stylistic axis that does NOT co-vary with relation-class (any class can have a formal or
     colloquial member); this is deliberately the axis that keeps held-out generalization GRADED
     rather than a trivial identical-tag lookup -- held-out words share axes 1-3 with their true
     class's seeds (the discriminating structure) but may differ on axis 4 (register), so
     within-class similarity is high (~0.75) but not always a trivial 1.0, and the classifier must
     still separate that from cross-class similarity (~0.25-0.5) via a real margin.
  - 3 SEED markers per class (12 total, literal words already load-bearing in the parent cell's
    templates/roles) + 1 HELD-OUT marker per class (4 total, the ACTUAL production markers the
    parent cell's paraphrase/KB-paraphrase templates use: `compose`, `generate`, `require`,
    `transport` -- chosen because they let Test 1 and Test 2 below share the same real-data
    evidence). Register tag assigned via a fixed rubric (Latinate/technical-sounding = FORMAL,
    short/everyday = COLLOQUIAL, else NEUTRAL) applied BEFORE any classification is run
    (non-circular, same discipline as this file's existing `OUTCOME_HELDOUT_*`/`GOAL_HELDOUT_*`).
- `classify_nway(word, pools, domain, floor, margin)` -- a new GENERIC N-way argmax-with-margin
  classifier (domain-general, not relation-specific), a straightforward generalization of the
  existing `classify_2way` to >2 named pools. Returns `None` (abstain) exactly like `classify_2way`
  on OOV / below-floor / margin-too-thin; never forced to guess.

**New cell (`experiments/exp_relation_canonicalization_learned_v1.py`) owns the canonicalization
POLICY, reusing everything else read-only from the parent cell (`canon_entity`, `build_anchor_set`,
`content_repr_vector`, `render_composes`, `render_partof`, `_pair_corroboration_check`,
`CANON_PART_OF`/`CANON_PRODUCES`/`CANON_CONSUMES`/`CANON_MOVES`) and from its own upstream deps
(`build_reading_facts`, `reading_vocab`, `build_cskg_bridges`, `build_gap_set`,
`build_genuine_waves`, `compute_cskg_extra`, `compute_kb_role_hits`):**
- `LEARNED_MARKER_TABLE` -- template-key -> `{marker, swap}`. This is the SUPPLIED-STRUCTURE
  remainder the task explicitly sanctions: which literal marker-word a given text template uses,
  and whether that template's captured surface-argument order needs swapping to reach canonical
  subject-first order. NEITHER field encodes relation-CLASS identity (no `canon` field) -- the
  class is computed at run time by `learned_canon_for_marker` via `classify_nway` over the SEED
  pools only (held-out markers excluded from the pools by construction).
- `_apply_canon_order(arg_a, canon, arg_b, swap)` -- one shared helper used by all extraction
  functions, replacing the per-function hard-coded canon literals.

## Tests (all can-fail, pre-registered bands BEFORE running)

**T0 -- ANTI-COLLAPSE (mandatory, checked FIRST).** Leave-one-out classification of every SEED
marker (classify using the OTHER seeds in its own pool + all seeds of the other 3 pools) must
recover its true class 12/12, AND no PRODUCES-true marker may ever classify as CONSUMES (or
vice-versa). **Band: HARD requires 12/12 correct + the PRODUCES/CONSUMES cross-check holds, zero
tolerance** (task-mandated: "a relation-canonicalizer that merges opposite relations is broken").

**T1 -- REPRODUCE WITHOUT THE HAND-TABLE.** Re-run (a) the parent cell's own self-test worked
example (wood/cellulose MadeOf vs "cellulose composes wood" direction-flip identity + coal
anti-collapse boundary) and (b) the FULL real-data population (121 gaps, same population the
parent cell's FULL run used) through extraction functions that call `learned_canon_for_marker`
instead of any hand dict. **Band: HARD requires `same_idea_match_rate >= 0.90` and
`automatic_corroboration_rate >= 0.90` (matching the parent cell's own FULL bands), AND the worked
synthetic example reproduces identical same-rep/distinct-rep behavior to the parent cell's
self-test.** Reference (MEASURED@d:/AI/hd-instrument/data/exp_representation_canonicalization_v1/
metrics.json): `n_targets=121, n_gaps=121, n_2plus_sources=50, same_idea_match_rate=1.0,
automatic_corroboration_rate=1.0, elapsed_s=13.28`.

**T2 -- HELD-OUT GENERALIZATION (THE decisive test).** The 4 held-out markers (`compose`,
`generate`, `require`, `transport` -- never in any SEED pool, structurally verified absent)
classified via `classify_nway` against ONLY the retained seed pools. **Band: HARD_PASS requires
4/4 correct; MIDDLE_BAND for 2/4-3/4; HONEST_NEGATIVE (not HARD_FAIL -- an informative capability
finding, not a mechanism bug) for <=1/4**, per the task's explicit instruction not to force a pass
if the learnable signal (4 classes, a handful of markers) proves too thin.

## Controls

- **no_leak_ok**: (a) structural -- assert every held-out marker is absent from all 4 SEED pools
  (the classifier's input pools literally cannot contain the answer); (b) `HDFactStore.query()`
  empty before every `store()` (inherited for free via reused `_pair_corroboration_check`).
- **scramble_control_ok**: permute `RELATION_MARKER_FEATURES`' word->features assignment (fixed
  seed=999, byte-identical recipe to this file's and the parent module's own circularity checks)
  and re-run T2. **Band: real held-out rate >= 0.75 (>=3/4) AND scrambled held-out rate <= 0.25
  (<=1/4, chance-level over 4 classes)** -- corrupting the verb-similarity signal must degrade
  generalization, proving T2 depends on genuine feature structure not construction artifact.
- **core_preserved_ok**: `hdlab.lexical_similarity.self_test()`, `hdlab.hd_fact_store.
  _run_all_selftests()`, `hdlab.grounding_acquisition_loop.self_test()`, `hdlab.prelim_tier.
  self_test()`, AND `hdlab.verb_lexical_similarity.self_test()` (the file this cell extends) all
  pass byte-identically -- proves the additive `hdlab/verb_lexical_similarity.py` extension
  (new DATA + `classify_nway`, zero existing lines changed) causes zero regression anywhere.
- **pytest verification/**: must stay green (`.venv` python), confirming no cross-cutting breakage.

## Verdict tree (pre-registered, no post-hoc tuning)

- `anti_collapse_ok == False` -> `HARD_FAIL_relation_class_anti_collapse` (T0 mandatory can-fail).
- else `no_leak_ok AND scramble_control_ok AND core_preserved_ok == False` ->
  `HARD_FAIL_controls_broken`.
- else `held_out_generalization_rate == 1.0 AND same_idea_match_rate >= 0.90 AND
  automatic_corroboration_rate >= 0.90` -> `HARD_PASS_relation_canonicalization_learned_earned`.
- else `held_out_generalization_rate >= 0.50` -> `MIDDLE_BAND_relation_canon_partial_generalization`
  (some learnable signal, not fully decisive across all 4 classes).
- else -> `HONEST_NEGATIVE_relation_canon_not_earned_from_thin_signal` (task-sanctioned outcome,
  NOT forced to a pass; hand-table-equivalent lookup remains supplied structure / fallback).

## Compute architecture

Class: (b) sequential-CPU with justification -- reuses the parent cell's own real-data pipeline
verbatim (one CSKG streaming pass + one KB-role-schema JSON load, MEASURED elapsed_s=13.28 on the
parent's FULL run); this cell adds only in-memory dict/cosine classification on top, no new heavy
compute. Storage: sharded (`HDFactStore` per isolated pair, same convention as parent). Wall time
budget: self-test <10s, FULL (single mode, no smoke/full split needed at this scale) <60s.

## Dispatch

RUN LOCAL, inline, foreground (Autonomy Declaration: no queue_add, no remote, no push). Self-test
gate first, then the single real-data run. LOCAL commit, targeted `git add` (never `git add -A`).

## Schema-vet declarations

- `arms_differ_verified` analog: `anti_collapse_ok` (T0) is the direct content-level equivalent
  (leave-one-out classification must not merge PRODUCES/CONSUMES).
- `final_metrics_atomicity`: tmp_replace (single-shot).
- `except SystemExit`/`KeyboardInterrupt` re-raised BEFORE `except Exception` (no `BaseException`).
- `crlb_n/a`: discrete classification-accuracy gates, not a Gaussian noise-floor metric;
  `discriminator_reachability=TRUE` argued via the axis-overlap arithmetic in the mechanism section
  above (within-class mean similarity ~0.75 vs cross-class ~0.25-0.5, margin >= 0.15 floor) BEFORE
  touching real data.
- `baseline_in_band`: N/A -- representation-identity/classification-accuracy test, not a
  baseline-vs-mechanism accuracy gap.
- `discriminator survives scale`: T1(b) runs the REAL FULL population (121 gaps), not a toy subset.
- `HP_SCOPE`: T0/T2 (closed-form) and T1 (real-data reproduction) gates apply jointly to the
  overall verdict per the tree above; no arm is exempted.
- `cardinality_ok`: EXPECTED = 12 seed leave-one-out probes (T0) + 4 held-out probes (T2, real +
  scrambled) + the parent's full real-data population count (121 gaps / all CSKG+KB-role pairs
  therein, T1) -- every count logged, verdict counts checked against population size.
- `calibration_check`: default_ok_for_this_regime -- `RELATION_CLASS_FLOOR=0.50` /
  `RELATION_CLASS_MARGIN=0.15` set from the axis-overlap arithmetic above BEFORE running, never
  tuned post-hoc against a measured result.
- `progress_logging`: print_flush_true (declared anyway for audit parity; `--timeout` well under
  the 1800s threshold).

## Honest disclosure (pre-registered BEFORE running, per task instruction)

If `held_out_generalization_rate <= 0.25`, that is `HONEST_NEGATIVE_relation_canon_not_earned_
from_thin_signal` -- reported plainly. The task itself flags this as a live possibility ("the
relation set is small... the learnable signal may be THIN"); a miss here is NOT folded into a
pass, and the hand-table-equivalent lookup (`KB_ROLE_TO_CANON` + the per-function canon literals
in e65de60f1) remains legitimate SUPPLIED STRUCTURE (charter-acceptable) as the working fallback,
exactly as e3712e8b5's gate-matching fallback remained the working solution when
`exp_representation_canonicalization_v1` itself fell short of its own real-data floor.
