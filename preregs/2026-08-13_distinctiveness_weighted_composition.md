# PRE-REGISTRATION -- exp_distinctiveness_weighted_composition_v1

Filed: 2026-08-13. Role: exp_dev. Committed BEFORE any arm was run.
Implements the ONE BUILD TARGET of `notes/brain_drill_encoder_lexical_semantics_2026-08-13.md`
(commit 471798502), section 3.3, element E1.
Repo HEAD at filing: `471798502`.

---

## 1. THE BRAIN MECHANISM BEING DUPLICATED

The brain separates near-neighbours (couch/chair) with DISTINCTIVE FEATURES -- properties present
in FEW concepts -- which are PRIVILEGED: verified faster and weighted more diagnostically than
shared features (Cree, McNorgan & McRae, *JEP:LMC*, PMC3226832 -- CITED@drill sec 1.5a). Tyler &
Moss's Conceptual Structure Account (*TiCS* 2001; Devereux et al. 2014 CSLB norms) adds that
distinctive features are WEAKLY correlated with a concept's other features, making them the most
fragile part of the system -- which is why semantic dementia's FIRST errors are coordinate
confusions inside a category (couch -> "chair"; Rogers et al. 2004, *Psychol Rev* 111:205-235).

Our implementation is the PRECISE INVERSE. `hdlab/lexical_similarity.py:542-546`
(`_concept_vector_from`) stacks a concept's feature vectors with NO weights, and
`hdlab/bundling.py:34-39` (`bundle`) is a plain sum plus per-component magnitude renorm. A tag
appearing in 8 concepts counts exactly as much as one appearing in 1.

## 2. THE ONE VARIABLE

Weight each feature vector by its DISTINCTIVENESS before bundling. Everything else held fixed.

## 3. THE DISTINCTIVENESS MEASURE -- REUSE, NOT A PARALLEL BUILD

Per the standing rule that a mechanism sharing an already-built process REUSES that organ, the
weight comes from `hdlab/low_information_filter.py`, unmodified, through its own public API.

Construction: one "document" per concept = `[concept] + sorted(features)`. Then
`InformationProfile.pmi(concept, feature)` is the weight.

ANALYTIC REDUCTION (stated openly because it is load-bearing): each concept occupies exactly one
document, so `df[concept] = 1` and `pair_df[(concept, feature)] = 1`. Substituting into the
organ's own formula (`low_information_filter.py:81-83`):

    pmi(c, f) = log2( (1/N) / ((1/N) * (df_f / N)) ) = log2( N / df_f )

i.e. the organ's PMI reduces EXACTLY to the feature's inverse-document-frequency in bits over the
concept population. That IS Tyler & Moss distinctiveness (few concepts share it -> high weight).
It is always >= 0, and exactly 0 for a feature every concept has. No new measure is introduced;
no floor/gate from the module is used (`pmi_floor` is a refusal gate, not a weight, and is
reported but unused).

**Does the organ genuinely serve? YES.** Stated explicitly per the brief's requirement: no
substitution is needed and none is made.

Two construction paths, both calling the organ:
- SUPPLY A (359 concepts): `build_profile(docs, track_pairs=True)` -- the FULL organ path.
- SUPPLY B/C (635,313 concepts): materialising 6M feature tokens for `build_profile` is not
  memory-viable, so `df` is streamed and an `InformationProfile` is constructed directly with the
  measured `df` plus the exact sparse `pair_df` entries; `prof.pmi()` (the organ's own method) is
  then called unmodified. A self-test ASSERTS this construction is bit-identical to
  `build_profile()` on a 2,000-concept subsample. That assertion is the proof no parallel measure
  was invented.

## 4. PRIMARY MEASURE + THE PRE-DECLARED TRAP

PRIMARY MEASURE: Spearman rho against held-out SimLex-999
(`data/encoder_eval_benchmarks/simlex999.txt`, 999 pairs, 1,028 words; Hill, Reichart & Korhonen
2015, *Comput Ling* 41:665-695). Coverage is reported as a FIRST-CLASS number, not a footnote.

**THE TRAP, enforced in code:** `CONCEPT_FEATURES` is CONSTRUCTED so that synonyms share nearly
all tags and siblings share only a domain tag (its own documented convention,
`hdlab/lexical_similarity.py:76-82`). Distinctiveness weighting is near-guaranteed to "win" on it
by construction. **ANY HARD-PASS MEASURED ON OUR OWN LEXICON IS VOID.** The cell hard-codes
`VOID_ON_OWN_LEXICON = True` for SUPPLY A and emits `HARD_PASS_VOID_OWN_LEXICON` rather than
`HARD_PASS` if SUPPLY A's numbers ever clear the bands. Note the trap is not fully escaped merely
by scoring on SimLex PAIRS: the 35 covered pairs are exactly the ones the lexicon was authored to
handle. Only an EXTERNAL, un-authored-by-us feature supply can license a shape claim.

## 5. FEATURE SUPPLIES (all three declared before running)

| supply | source | external? | word coverage | role |
|---|---|---|---|---|
| A | `hdlab.lexical_similarity.CONCEPT_FEATURES` (359 concepts) | NO (ours) | 90/1028 | PRIMARY, per drill sec 3.3. HARD-PASS VOID by construction. |
| B | CSKG (`data/grounding_testbed/cskg.tsv.gz`, 6,001,531 edges, 1,511,784 node1, 1,024,920 word-like) | YES | 1028/1028 | SECONDARY. Feature = `relation \| node2`. Where the SHAPE hypothesis actually gets tested. |
| C | SUPPLY B minus lexical-relation edges | YES | measured | STRICTEST. Removes the synonym-dictionary shortcut. |

MEASURED@pre-flight probe (2026-08-13, `.venv/Scripts/python.exe`, HEAD 471798502):
- SimLex pairs with BOTH words in `CONCEPT_FEATURES`: **35 / 999 = 0.0350**
- SimLex words present as a CSKG word-like `node1`: **1028 / 1028**
- CSKG features per SimLex word: min 5 / median 138 / p90 477 / max 7416 / mean 216.5
- distinct CSKG features over the SimLex vocabulary: 103,356

SUPPLY C drops these relations (a synonym/similarity dictionary would otherwise supply the answer
directly): `/r/Synonym`, `/r/Antonym`, `/r/SimilarTo`, `/r/RelatedTo`, `/r/DistinctFrom`,
`/r/DerivedFrom`, `/r/EtymologicallyRelatedTo`, `/r/EtymologicallyDerivedFrom`, `/r/FormOf`,
`/r/dbpedia/*`. SCOPE CAVEAT declared up front: CSKG is ConceptNet/WordNet-derived, so SUPPLY B
carries explicit lexical-relation structure. A win on B alone is a win for "explicit relational
structure injection" (consistent with the counter-fitting precedent, drill sec 1.5f), NOT an
independent discovery. SUPPLY C is the arm that separates the two. SimLex-999's labels are human
similarity ratings collected independently of CSKG, so there is no LABEL leakage in any supply.

## 6. ARMS (four required + two diagnostics), per supply

1. **WEIGHTED** (TREATMENT) -- `bundle(stack(feature_vecs) * w[:, None])`, `w = pmi(c, f)`.
   `hdlab.bundling.bundle` is called unmodified; the weighting happens in the experiment file.
   NO hdlab file is edited.
2. **UNIFORM** (CONTROL, the one-variable isolation and the PRIMARY comparison) -- identical
   feature sets, `w = 1`. Reduces to the live `_concept_vector_from` exactly.
3. **GROUNDED** (CONTROL) -- `hdlab.grounded_similarity`, our live OOV mechanism. Reported in TWO
   forms: `GROUNDED_CAPPED` (the literal live function, clipped to [0, 0.45]) and `GROUNDED_RAW`
   (uncapped cosine). **The gate uses GROUNDED_RAW**, the STRONGER form of the control, because
   `GROUNDED_CAP = 0.45` flattens the top of the range and would unfairly depress a rank
   correlation. Treatment must beat the control at the control's best.
4. **SCRAMBLE_ASSIGN** (FLOOR) -- permute the word -> feature-set assignment (fixed seed 999,
   matching `lexical_similarity.self_test` step 5). Must collapse.
5. **SCRAMBLE_WEIGHTS** (DIAGNOSTIC) -- permute the distinctiveness VALUES across features,
   feature sets intact.
6. **Analytic diagnostics** (not arms) -- exact weighted/uniform cosine over feature-incidence
   space, no FHRR randomisation, to bound how much of any null result is embedding noise.

**DISCREPANCY BETWEEN THE BRIEF AND THE DRILL, RESOLVED HERE BEFORE RUNNING.** The dispatch brief
defines the scramble as "distinctiveness values shuffled across features" and puts it under a
`scramble <= 0.05` band. The drill (sec 3.3, control 3) defines it as "permute word -> feature-set
assignment; must collapse". These are DIFFERENT controls and only the drill's can meet 0.05: with
feature sets intact, shuffling only the WEIGHTS leaves all genuine feature overlap in place, so
its rho must land near UNIFORM's, not near zero. A band of 0.05 on the brief's version is
internally contradictory with a non-zero UNIFORM rho. RESOLUTION: both are run;
**the `scramble <= 0.05` band is gated on SCRAMBLE_ASSIGN**; SCRAMBLE_WEIGHTS is reported as the
sharper diagnostic (it isolates whether the specific distinctiveness ORDERING is load-bearing, as
opposed to merely having non-uniform weights).

PUBLIC CALIBRATION POINTS, quoted alongside and NOT as arms (CITED@Mrksic et al. 2016,
arXiv:1603.00892 Table 2, via drill sec 1.5f): GloVe 0.41, counter-fitting 0.58, human
inter-annotator agreement 0.67.

## 7. EVALUATION SET (fair, paired)

Per supply:
- `cov_supply` = fraction of the 999 pairs where BOTH words have >= 1 feature in that supply.
  **This is the coverage number the supply band gates on.**
- `EVAL_SET` = pairs where both words have >= 1 feature in the supply AND both words are in the
  grounded (Lancaster x Brysbaert) lexicon, so EVERY arm scores the SAME pairs and all deltas are
  paired. `cov_eval` reported separately.
All rho values within a supply are computed on that supply's `EVAL_SET`.

## 8. BANDS -- PRE-DECLARED, NOT ADJUSTED AFTER SEEING RESULTS

Evaluated independently per supply, in this order (first match wins):

- **HARD_FAIL_SUPPLY**: `cov_supply < 0.20`. The wall is feature SUPPLY (E2), not metric shape
  (E1). Redirect: harvest differentia from `hdlab/definitional_extraction.py` (genus + differentia
  IS the distinctive feature, drill sec 2 / PART 3.1 item 2).
- **HARD_PASS** (all four): `rho_WEIGHTED >= 0.35` AND `(WEIGHTED - UNIFORM) >= +0.08` AND
  `(WEIGHTED - GROUNDED_RAW) >= +0.15` AND `rho_SCRAMBLE_ASSIGN <= 0.05`.
- **HARD_FAIL_SHAPE**: `(WEIGHTED - UNIFORM) < +0.03`. The shape hypothesis is REFUTED. Next
  target becomes semantic-control gain (drill element E4: `concept_similarity(a, b)` is a bare
  2-arg function with no context port, and the brain never computes context-free word-word
  similarity).
- else **MIDDLE_BAND**.

Per META_RULE_L, a HARD_PASS clearing any band by less than 5% of its width is demoted to
MIDDLE_BAND.

BOTH failure modes are INFORMATIVE and neither is to be tuned around: together they partition
"our metric shape is wrong" from "our feature supply is empty", which the project currently
cannot distinguish. No threshold in this section may be changed after any arm has run.

## 9. DISCRIMINATOR REACHABILITY / statistical feasibility (replaces CRLB)

`crlb_n/a`: Spearman rho has no Cramer-Rao noise floor of the estimator-variance kind these cells
usually declare. The equivalent feasibility floor is the standard error of rho,
`SE(rho) ~= 1/sqrt(n-1)`  THEORETICAL@Fieller-Hartley-Pearson.

- SUPPLY A: `n <= 35` -> `SE(rho) ~= 0.17`. **A +0.08 delta is NOT RESOLVABLE at this n.**
  `discriminator_reachability_A = FALSE`. Declared before running: SUPPLY A cannot decide the
  shape bands even setting coverage aside. Its shape numbers are reported as UNDERPOWERED
  DIAGNOSTIC and are explicitly non-gating.
- SUPPLY B/C: `n ~= 900-999` -> `SE(rho) ~= 0.032`; and because WEIGHTED and UNIFORM are scored on
  the SAME pairs (paired), the SE of their DIFFERENCE is substantially smaller than either.
  `discriminator_reachability_B = discriminator_reachability_C = TRUE`.

This is why SUPPLY B/C were added to the design rather than shipping a cell whose only gate is a
foregone-conclusion coverage failure at n=35.

## 10. Compute architecture

`compute_class`: (b) sequential-CPU with justification. The cell is a fixed deterministic
embedding plus 999 cosines per arm; there is no training, no matmul-bound inner loop, and total
wall is minutes. Feature-vector generation IS vectorised (`torch.rand` over chunks). No GPU.
`storage_strategy`: bundled -- and this is case (c) of the sharded-storage rule: the cell IS a
semantic-similarity query where a blended distributed representation is the desired behaviour,
and `bundle()` is precisely the substrate op under test. No chained retrieval, no composition
depth.

`N_DIM`: SUPPLY A uses 8192 with `FEATURE_SEED=7`, matching `hdlab.lexical_similarity` exactly so
its geometry reproduces the live module. SUPPLY B/C use 1024 (repo default per CLAUDE.md) because
103,356 feature vectors at 8192 complex64 would be ~6.8 GB. The analytic diagnostics (sec 6 item
6) bound the cost of that choice exactly: if FHRR sampling noise at N=1024 were suppressing the
effect, the analytic and FHRR rho values would diverge, and that divergence is reported.

## 11. Mandatory cell-template fields

```yaml
anchor_name: exp_distinctiveness_weighted_composition_v1
run_mode_default: full                       # sec 16; --smoke and --self-test are explicit
cell_chunked: false                          # no seed axis
EXPECTED_N_UNITS: 18                         # 3 supplies x 6 arms
cardinality_ok: true                         # verdict counts len(load_units()); < 18 -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H
arms_differ_verified: true                   # META_RULE_AF sha256 over per-arm score vectors
arms_differ_exempted: []
final_metrics_atomicity: tmp_replace         # META_RULE_AH; smoke writes a SEPARATE output dir
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
progress_logging: print_flush_true
deterministic_seeding: true                  # fixed ints + hashlib.sha256; no builtin hash(), no list(set())
calibration_check: default_ok_for_this_regime   # pmi_floor is NOT used; the weight is pmi itself
crlb_n/a: "Spearman rho has no CRLB; SE(rho)~=1/sqrt(n-1) feasibility declared in sec 9 instead"
discriminator_reachability: {A: false, B: true, C: true}
baseline_in_band: n/a_correlation_metric     # UNIFORM rho is unbounded-below, not a 0..1 accuracy
sweep_alignment_verdict: ALIGNED             # the swept axis (supply) is the axis every arm experiences
multi_scale_smoke: [120 pairs, 480 pairs]
N-suffix: "no _nN suffix; N_DIM = 8192 (supply A) / 1024 (supply B,C); rationale in sec 10"
```

## 12. Functional requirements (gate E)

| requirement | primitive |
|---|---|
| distinctiveness of a feature | `hdlab.low_information_filter.InformationProfile.pmi` (REUSE) |
| compose features into a concept | `hdlab.bundling.bundle` (REUSE, unmodified) |
| atomic feature symbol | `hdlab.situation_model_accumulate.unit_phase_vec` (REUSE) |
| similarity read-out | `hdlab.lexical_similarity._cos_complex` (REUSE) |
| live OOV control arm | `hdlab.grounded_similarity.grounded_similarity` (REUSE) |
| per-unit resume | `tools.exp_checkpoint` (REUSE) |

No hdlab file is modified. The weighting is implemented inside the experiment file. Wiring is a
separate decision that comes AFTER a verdict.

## 13. Timeout estimate

Pure-CPU, single foreground run. Two 30 s CSKG streaming passes (cached after the first), a
~10 s feature-matrix build, then 18 units of 999 cosines each. Estimated wall < 600 s, so this
runs FOREGROUND-TO-COMPLETION with an explicit 600 s Bash timeout per the INLINE-LOCAL mandate.
No detached launch, no queue dispatch.

## 13b. AMENDMENTS -- filed after the SMOKE, BEFORE the FULL run

Recorded here rather than silently applied. **Neither amendment touches a band in sec 8, and
neither can convert a FAIL into a PASS**: the smoke verdict was HARD_FAIL_SHAPE before and after
both.

**A1 -- CSKG concept population is keyed to CANONICAL nodes.** Sec 5 sized the population as
"word-like node1" (635,313 labels / 103,356 features). The cell instead restricts to node1
matching exactly `/c/en/<lowercase-word>`, giving **276,365 concepts / 79,815 features over the
SimLex vocabulary, still 1028/1028 SimLex words covered**. REASON: label -> node is then 1:1, so
"one document per concept" holds EXACTLY and the organ's PMI reduction (sec 3) is exact rather
than approximate. Under the looser keying a word spanning several sense-suffixed nodes would have
`df[concept] > 1` and the reduction would not hold. This is a fidelity fix to the measure, chosen
before any arm ran, and it does not change which pairs are evaluated.

**A2 -- the smoke's discriminator-fires assertion is scoped to supplies that carry signal.** As
first written the cell asserted SCRAMBLE_ASSIGN collapses on SUPPLY C specifically, and it RAISED
`VACUOUS SMOKE` at 480 pairs (SCRAMBLE_ASSIGN 0.0751 vs WEIGHTED 0.0838). The assertion was
mis-specified, not the cell: supply C's own treatment sits AT the scramble floor, so there is no
observed signal for the control to falsify. Amended: the assertion now runs on every supply whose
`rho_WEIGHTED >= 0.20`, at least one supply must clear that floor or the whole smoke is declared
vacuous, and a supply below it is logged `NO_SIGNAL_TO_FALSIFY`. Post-amendment the discriminator
fires on A and B at both smoke scales; C is logged as no-signal, which is itself a finding.

**A3 -- walk-back gate.** The smoke effect size is null-to-negative, which would normally mandate
doubling the FULL sample. SimLex-999 is a fixed 999-pair benchmark, so the FULL already uses the
maximum available n. No doubling is possible; this is recorded rather than skipped.

## 14. Discriminator

The negative control that MUST fail is SCRAMBLE_ASSIGN. The smoke asserts it fails the headline
gate at smoke scale. UNIFORM is not a must-fail control -- it is the one-variable isolation, and
it is EXPECTED to score well; the discriminator is the DELTA, not UNIFORM's absolute value.
