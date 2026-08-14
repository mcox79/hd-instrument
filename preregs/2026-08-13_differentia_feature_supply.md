# Pre-registration — differentia feature supply for the lexical comparator

Filed 2026-08-13. Role: exp_dev. Follows `exp_distinctiveness_weighted_composition_v1`
(cell `dbac1ae9c`) and brain drill `notes/brain_drill_encoder_lexical_semantics_2026-08-13.md`
(`471798502`), element E2.

**STATUS: STAGE 1 RUN AND REPORTED. STAGE 2 NOT RUN — THE PRE-FLIGHT GATE FAILED ON THE
EXISTING SUPPLY.** The Stage-2 design below is pre-registered for a SUCCESSOR cell that must
first rebuild the supply. It is NOT authorized to run against the stores measured in Stage 1.

---

## 1. Motivating finding (MEASURED, predecessor cell)

MEASURED@`data/exp_distinctiveness_weighted_composition_v1/metrics.json`:
- `per_supply.C_CSKG_NOLEXREL.rho.WEIGHTED` = 0.0804 (CSKG with synonym/relatedness edges deleted)
- `per_supply.B_CSKG.rho.WEIGHTED` = 0.5361 (same supply, lexical-relation edges intact)
- `per_supply.C_CSKG_NOLEXREL.rho.GROUNDED_RAW` = 0.3003 (raw sensorimotor cosine, same 639 pairs)

Outside a borrowed similarity lookup table our feature supply carries almost no similarity
signal, and is ~3.7x worse than the crude sensorimotor channel already running live. The binding
constraint is feature SUPPLY (E2), not feature SHAPE (E1).

## 2. Hypothesis

A definition is GENUS + DIFFERENTIA. The differentia is the brain's distinctive feature (Cree &
McRae; Tyler & Moss) — the low-redundancy property near-neighbour discrimination depends on and
that degrades first in semantic dementia. Extractor-derived differentia features should carry
real similarity signal where ConceptNet-minus-lexical-relations does not.

## 3. STAGE 1 — coverage pre-flight (RUN; this is the gate)

Probe: `experiments/_stage1_differentia_coverage_probe.py`
Output: `data/_stage1_differentia_coverage_probe.json`

Enumeration method: CONTENT grep for `definiendum_surface` over all `data/**/*.jsonl` and
`data/**/*.json` (not a name search), plus a schema-tolerant second pass for the
`(subject, GROUNDED_MEANING, object, pattern)` genus schema. Absence claims below rest on that
enumeration.

| store | rows | definitional rows | distinct terms | terms w/ definiens surface |
|---|---|---|---|---|
| `data/foundation/reading_grounding_v3_definitional/definitional_facts.jsonl` | 1751 | 1751 | 1316 | 1316 |
| `data/foundation/reading_grounding_v4_parsefix/definitional_facts_v4.jsonl` | 1956 | 1956 | 1680 | 1680 |
| `data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl` | 2092 | 2092 | 1713 | 1713 |
| `data/exp_definitional_predicate_v6/isa_facts_unchanged_v6.jsonl` | 5716 | 5716 | 4003 | 0 |
| `data/exp_definitional_predicate_v6/predicate_facts_v6.jsonl` | 250 | 250 | 118 | 0 |
| `data/exp_definitional_predicate_v61/predicate_facts_v61.jsonl` | 228 | 228 | 112 | 0 |
| `data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl` | 221 | 221 | 110 | 0 |
| `data/foundation_provenance_v1/definitional_predicate_v62_ledger.jsonl` | 221 | 221 | 110 | 0 |
| `data/foundation_provenance_v1/store/store_facts.json` (pipeline=DEFINITIONAL_EXTRACTOR) | 8187 | 221 | 110 | 0 |
| `data/exp_called_boundary_v7_smoke/called_facts_v7.jsonl` | 100 | 100 | 97 | 97 |
| `data/substrate_director_kb_v1/entities.jsonl` | 1292486 | 0 | 0 | 0 |

- (a) distinct defined terms, union: **5,613** (2,472 with a definiens surface).
- (b) SimLex-999: 999 pairs / 1,028 distinct words.
  - words with >=1 definition (any store): **252 / 1028 = 24.5%**
  - pairs with BOTH words covered: **83 / 999 = 8.3%**
  - words with a definition carrying a DEFINIENS SURFACE (required to extract a differentia):
    **152 / 1028 = 14.8%**
  - pairs with BOTH words differentia-capable: **29 / 999 = 2.9%**
- (c) differentia separable from genus: **28 / 30** sampled facts yielded >=1 differentia token
  after removing closed-class words and the genus head. Mechanically separable; quality is mixed
  (several sampled definiens spans are parse faults, e.g. `Hardy-Weinberg equilibrium` ->
  "This principle is now" -> empty).

### GATE: FAILED

Pre-declared gate: both-words-covered pairs < 50 => do not run Stage 2.
Arm A (differentia) requires a definiens surface. Differentia-capable pairs = **29 < 50**.
The genus-only stores raise coverage to 83 pairs, but those can serve only Arm B (the control);
the one-variable A-vs-B contrast is bounded by the intersection, which is 29.

Power at n=29: SE(rho) ~ 1/sqrt(n-1) = **0.189**. The pre-registered discriminator (A - B) >=
+0.08 sits far inside the noise; 95% CI half-width ~0.37. The measurement could not distinguish
HARD_PASS from HARD_FAIL, so it was not run.

### ROOT CAUSE — volume is not the problem, DOMAIN is

Per-segment yield of the 2,092-fact v5 store (MEASURED, this cell):

| segment | terms | SimLex words | both-covered pairs |
|---|---|---|---|
| bio_new | 1111 | 45 | 3 |
| bootstrap | 265 | 20 | 0 |
| adv_new | 164 | 14 | 0 |
| int_cont | 138 | 10 | 1 |
| ele_cont | 127 | 14 | 0 |

1,111 extracted biology terms bought 3 SimLex pairs. Extracting more biology or news text
multiplies bio-domain terms, not SimLex-domain terms. A biology textbook never defines *roof*,
*friend*, or *sugar*. This is a vocabulary-domain mismatch, not a volume shortfall.

## 4. THE CORPUS THAT FIXES IT, AND ITS PRICE (MEASURED, not estimated)

**`data/corpora/simplewiki/simplewiki_clean_v1.txt`** — already on disk, already cleaned,
251 MB, ~2.4M+ sentences, one sentence per line. Simple English Wikipedia opens articles with a
definitional sentence over general vocabulary, which is exactly the missing domain.

Probe: `experiments/_stage1_simplewiki_yield_probe.py` (runs
`hdlab.definitional_extraction.extract_definitions` UNMODIFIED)
Output: `data/_stage1_simplewiki_yield_probe.json`

MEASURED on a uniform 1-in-20 sample (120,000 sentences, **12.6 s**, 9,520 sentences/s):
- 9,793 definitions extracted
- **410 / 1028 SimLex words hit**
- **209 / 999 pairs both-covered** — clears the 200 target from a 5% sample

Per-pattern breakdown (same sample), because the pattern mix decides the confound:

| pattern | SimLex words | both-covered pairs |
|---|---|---|
| COPULA | 322 | 147 |
| CALLED | 125 | 29 |
| APPOSITIVE | 122 | 24 |
| GLOSSARY_COLON | 31 | 0 |
| REFERS_TO | 3 | 0 |
| ALL | 410 | 209 |
| dropping CALLED + REFERS_TO | 376 | 185 |
| dropping CALLED + REFERS_TO + APPOSITIVE | 334 | 152 |

**Cost of the full run: ~4-5 minutes of extractor time** (2.4M sentences at 9,520 sentences/s),
single-core, no GPU, no network. The supply is not expensive. It was simply never built for this
vocabulary.

### 4.1 CONFOUND FOUND — the successor cell MUST control it

Simple Wikipedia lead sentences frequently state synonymy directly ("a movie, also called a
film, is..."). The high-similarity sample hits are exactly of this kind: movie/film 8.87,
actress/actor 7.12, friend/buddy 8.78, large/big 9.55. Harvesting CALLED / REFERS_TO /
APPOSITIVE spans would reintroduce **the same borrowed synonym lookup table this cell exists to
avoid** — structurally identical to the ConceptNet `/r/Synonym` edges named as FORBIDDEN. The
successor must restrict to COPULA (147 pairs at 5% sample; comfortably >200 at full corpus) or
justify each additional pattern with a synonym-leak control.

### 4.2 Extraction quality does NOT transfer untested

The 94% MEANINGFUL figure is CITED@ the predicate arm on a biology textbook. It is NOT a
simplewiki COPULA number. Visible faults in the sampled hits (`think`, `right`, `page`,
`people`, `begin` as definienda) indicate wrong-span picks. The successor cell must hand-score a
fresh sample on THIS corpus before any quality claim.

## 5. STAGE 2 — pre-registered design (NOT RUN; successor cell only)

PRIMARY: Spearman rho on SimLex-999 over pairs covered by the rebuilt supply. SimLex is fully
held out — nothing is fit to it. (DISCLOSURE: the predecessor cell has no train/test split
either; it evaluates all 999 pairs. "Held-out split" in the dispatch brief does not correspond to
anything in `exp_distinctiveness_weighted_composition_v1`.)

ARMS: A DIFFERENTIA features -> bundling comparator; B GENUS-ONLY -> same comparator (the
one-variable isolation, and the semantic-dementia pattern); C `grounded_similarity` RAW cosine,
uncapped; D CSKG-minus-lexical-relations = 0.080 same-pairs reference; E SCRAMBLE = the
predecessor's word-to-feature-set permutation (`_scrambled_assignment`), NOT a within-feature
value shuffle.

FORBIDDEN: no ConceptNet synonym/relatedness/similarity edges in any treatment arm; assert
absence in code and record the assertion in metrics.json. Extend the assertion to cover
simplewiki CALLED/REFERS_TO/APPOSITIVE synonym spans per 4.1.

BANDS (pre-declared, not to be adjusted after results):
- HARD_PASS: A >= 0.35 AND (A - C) >= +0.05 AND (A - B) >= +0.08 AND scramble <= 0.05
- SUPPLY_REAL_BUT_THIN: A > C but coverage < 30%
- HARD_FAIL: (A - B) < +0.03 OR A <= D

POWER: at n=200, SE(rho) ~ 1/sqrt(199) = 0.071; at n=400, 0.050. The (A - B) >= +0.08
discriminator needs n >= ~400 covered pairs to be resolvable against paired-arm noise, which the
full simplewiki run supports. Do not run the successor at n < 200.

Discriminator has range by construction (Spearman over continuous cosines). No gate depends on a
hand-scored quantity.

## 6. Engineering (unchanged from predecessor)

Thread pins above numpy import; `tools/exp_checkpoint.py` per-unit resume; metrics.json written
once, tmp + `os.replace`; smoke to a SEPARATE output dir; `sorted(set())`; `except SystemExit:
raise` before `except Exception`; no `BaseException`; no bare `except`.

---

# AMENDMENT A1 — Stage 2 authorized, supply rebuilt from simplewiki

Filed 2026-08-13 by exp_dev, **BEFORE any Stage-2 arm was computed and BEFORE the extraction
run**. Everything in this amendment is frozen at commit time. Section 5 above is SUPERSEDED by
this amendment where the two differ; section 5 is left in place unedited as the record of what
was pre-registered at Stage 1.

Cells:
- extraction  `experiments/exp_differentia_simplewiki_extract_v1.py`
- measurement `experiments/exp_differentia_feature_supply_v1.py`

## A1.1 EXTRACTION — pattern restriction, FROZEN IN ADVANCE

`hdlab.definitional_extraction.extract_definitions` is run UNMODIFIED over every sentence of
`data/corpora/simplewiki/simplewiki_clean_v1.txt` (2,779,032 lines; 10,294 with len > 600 are
skipped, matching the Stage-1 probe). All five patterns are extracted so their counts can be
reported, then:

**TREATMENT SUPPLY = `COPULA` and `GLOSSARY_COLON` ONLY. `CALLED`, `REFERS_TO` and `APPOSITIVE`
are FORBIDDEN in every treatment arm.** The cell asserts
`sorted(set(patterns_in_treatment_store)) == ["COPULA", "GLOSSARY_COLON"]` and records the
assertion plus the per-pattern counts in `metrics.json`.

Rationale is section 4.1: simplewiki lead sentences state synonymy outright, and harvesting those
spans would reimport the borrowed similarity lookup table this whole line exists to escape. This
restriction is frozen NOW, before any correlation is computed, and is not revisited afterwards.

The store is written to a NEW directory `data/exp_differentia_simplewiki_extract_v1/`. It is NOT
written into any existing foundation store and is NOT banked into the canonical fact store. This
is measurement supply, not a foundation commit.

## A1.2 LEAK CONTROLS — run BEFORE the measurement, reported regardless of outcome

Each can invalidate the result. All three are computed on the SimLex pair set before any arm is
scored, and each excluded pair set is reported with its count and a sample.

- **L1 DIRECT LEAK.** For pair (a, b): a's definiens text contains b as a whole word (surface or
  lemma), or vice versa. A definition that names the other word is the lookup table wearing a
  different hat. EXCLUDED from the primary.
- **L2 SYNONYM-STATEMENT LEAK.** Within the kept COPULA/GLOSSARY facts for a or b, the definiens
  or its source sentence contains an explicit synonymy construction. Frozen phrase list:
  `another name for`, `also known as`, `same as`, `another word for`, `another term for`,
  `also called`. (The first four are the dispatch brief's; the last two are the same construction
  class and are included because a wider net is the stricter choice.) EXCLUDED from the primary.
- **L3 SOURCE-SENTENCE OVERLAP.** a and b are defined from the SAME source line. Flagged and
  EXCLUDED from the primary.

**POWER GATE: if fewer than 50 pairs survive all three, STOP and report. Do not run an
underpowered correlation.** This is the same gate Stage 1 enforced. The gate is armed on the FULL
run only; smoke runs at reduced pair counts by design and is exempt.

## A1.3 ARMS (all scored on the SAME surviving pair set)

| arm | supply |
|---|---|
| A DIFFERENTIA | per word, union over its COPULA/GLOSSARY definitions of the definiens content lemmas with the genus head removed (`definiens_lemmas` is already closed-class-filtered by the organ). Feature token `DIFF\|<lemma>`. |
| B GENUS_ONLY | per word, union of `GENUS\|<head>` over the new store, PLUS the genus half of `data/exp_definitional_predicate_v6/isa_facts_unchanged_v6.jsonl` where it covers (the dispatch brief names this file explicitly; it carries all five patterns). One-variable control and the semantic-dementia prediction. |
| C GROUNDED_RAW | `hdlab.grounded_similarity._raw_cos(grounded_vector(a), grounded_vector(b))` — uncapped. NOT the 0.45-capped path. |
| D CSKG_NOLEXREL | the predecessor's stripped supply, RECOMPUTED on the surviving pairs (not quoted across runs). |
| E SCRAMBLE | the predecessor's `_scrambled_assignment` word-to-feature-set permutation applied to A's supply. NOT a within-feature value shuffle (the predecessor measured that that lands near uniform, so it is not a floor). |

**COMPARATOR.** A, B, D and E go through the predecessor's FHRR bundling comparator
(`hdlab.bundling.bundle` on unit-phase feature vectors, cosine via
`hdlab.lexical_similarity._cos_complex`). The predecessor left two variants: UNIFORM and
distinctiveness-WEIGHTED. **PRIMARY = UNIFORM**, because the predecessor HARD_FAIL_SHAPE'd the
weighting hypothesis (`delta_weighted_minus_uniform` = -0.0003 on exactly this stripped supply),
so carrying the weighting would add a refuted second variable. WEIGHTED is computed and reported
for every arm as a declared secondary; no band reads it.

**FORBIDDEN, asserted in code and recorded in metrics.json:** no ConceptNet synonym / relatedness
/ similarity edge may enter A, B or E — asserted as "no feature token in A/B/E begins with `/r/`",
plus the pattern assertion of A1.1. Arm D is the ConceptNet reference arm and drops
`LEXREL_DROP` exactly as the predecessor did.

**SENSITIVITY, reported not banded:** `B_STRICT` = arm B with the v6 ISA contribution restricted
to COPULA + GLOSSARY_COLON. Reported so a reader can see whether B's synonym-pattern content
moves the A - B delta.

## A1.4 POWER — paired bootstrap (this replaces section 5's independent SE)

All arms are scored on the SAME pairs, so the arm differences are DEPENDENT correlations and a
naive independent SE is wrong. **Paired bootstrap over pairs: 5000 resamples (>= the 2000 the
brief requires), fixed seed 20260813, percentile 95% CI.** Reported per delta (A-B, A-C, A-D):
point estimate, CI low, CI high, bootstrap SD, and the minimum detectable delta
`MDE = 1.96 * bootstrap_SD` at the surviving n. Arm rho values also get a bootstrap CI.

## A1.5 BANDS (frozen; evaluated in this order)

1. **HARD_FAIL** if `CI(A-B)` includes 0 (`CI_low <= 0 <= CI_high`) — the differentia adds
   nothing over the genus — OR `A <= D`.
2. **HARD_PASS** if `A >= 0.35` AND `CI_low(A-C) > 0` AND `CI_low(A-B) > 0` AND `E <= 0.05`.
   META_RULE_L: if either one-sided threshold gate (`A >= 0.35`, `E <= 0.05`) is cleared by less
   than 5% of its own magnitude, demote to MIDDLE_BAND.
3. **SUPPLY_REAL_BUT_THIN** if `CI_low(A-C) > 0` but coverage of the full 999 < 30% — the
   mechanism works where it reaches; the fix is more extraction, not a different mechanism.
4. **MIDDLE_BAND** otherwise.

Public calibration points are REPORTED ALONGSIDE, NOT AS ARMS: GloVe 0.41, counter-fitting 0.58,
human IAA 0.67 (CITED@Mrksic et al. 2016 arXiv:1603.00892 Table 2).

## A1.6 SCHEMA-VET fields

```yaml
cardinality_ok: true            # EXPECTED_N_UNITS = 7 arms (A,B,B_STRICT,C,D,E + A_WEIGHTED set)
discriminating_fraction: n/a    # no sweep axis; one pair set, fixed arms
sweep_alignment_verdict: ALIGNED
composition_edges: [{from: definitional_extraction, to: bundle, verdict: SHAPE_MATCH}]
positive_control_arms: [D_CSKG_NOLEXREL_REPRODUCES_PREDECESSOR]   # gate D, tolerance reported
functional_requirements: [near-neighbour separation from extracted differentia]
real_code_path_exercised: [extract_definitions, build_profile, bundle, unit_phase_vec,
                           _cos_complex, grounded_similarity]
substrate_signature_checked: [build_profile, bundle, grounded_similarity]
guard_baseline_validated: n/a   # no control-beats-baseline break-guard
deterministic_seeding: true     # fixed ints + hashlib; no builtin hash(), no list(set())
crlb_n/a: "Spearman rho over continuous cosines has no noise floor of this kind; the power
           statement is the paired bootstrap of A1.4, reported as an MDE."
final_metrics_atomicity: tmp_replace
arms_differ_verified: true      # per-arm score-vector sha256, asserted distinct
baseline_in_band: reported      # D and E are the references; A must sit in (0.05, 0.95)
calibration_check: default_ok_for_this_regime
cell_chunked: false             # no seed axis; per-arm units.jsonl resume instead
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
progress_logging: print_flush_true
```

## A1.7 Known deviations from the dispatch brief, disclosed

- The brief did not say which of the predecessor's two comparator variants to use. A1.3 declares
  UNIFORM primary with WEIGHTED reported; the predecessor measured the two to differ by 0.0003 on
  this supply.
- The brief's L2 phrase list is extended by two same-class phrases (A1.2). Strictly more
  exclusion, never less.
- Arm B follows the brief literally in using the all-pattern v6 ISA file; `B_STRICT` is added as a
  reported sensitivity, not as a band input.
