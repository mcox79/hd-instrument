# Pre-registration -- NEAR vs FAR diagnostic on the 350 surviving SimLex pairs

Filed 2026-08-13. Role: exp_dev. Cell: `experiments/exp_near_vs_far_diagnostic_v1.py`.
Parent: `experiments/exp_differentia_feature_supply_v1.py`
(MEASURED@`data/exp_differentia_feature_supply_v1/metrics.json`, commit `9825510bf`),
whose own pre-reg is `preregs/2026-08-13_differentia_feature_supply.md`.

**THIS FILE IS COMMITTED BEFORE THE CELL RUNS. Nothing below is revisited after a result.**

---

## 1. What the parent measured, and why that is not enough

MEASURED@`data/exp_differentia_feature_supply_v1/metrics.json:rho_primary` (n = 350 pairs
surviving all three leak controls, UNIFORM comparator):

| arm | rho |
|---|---|
| A_DIFFERENTIA | 0.0247 |
| B_GENUS_ONLY | 0.0179 |
| B_STRICT_GENUS | -0.0464 |
| C_GROUNDED_RAW | **0.2759** |
| D_CSKG_NOLEXREL | 0.0751 |
| E_SCRAMBLE | -0.0235 |

Every symbolic arm is at chance. The one arm carrying signal is the graded sensorimotor channel
`hdlab/grounded_similarity.py`. That module's OWN docstring records
(CITED@`hdlab/grounded_similarity.py:23-38`, "HONEST, MEASURED LIMIT") that raw cosine over its
11-dim sensorimotor + concreteness vector CANNOT separate a true synonym from a same-domain
sibling: sofa/couch 0.968, happy/joyful 0.962 vs apple/orange 0.952, dog/cat 0.932 -- fully
overlapping.

The substrate's actual wall is NEAR-NEIGHBOUR discrimination (couch vs chair), not far
discrimination (couch vs democracy). If the 0.2759 is produced entirely by far-apart pairs and
collapses on near-neighbours, the one channel we own does not work on the problem we have, and
0.2759 is false comfort. **Establishing or refuting that is the entire purpose of this cell.**

## 2. What is held FIXED (change as little as possible)

- The **same 350 pairs**, re-derived by importing the parent module and replaying its eligibility
  chain (differentia coverage -> grounded lexicon -> arm-D scorability -> L1/L2/L3 leak controls).
- The **same five arms** plus the parent's B_STRICT sensitivity, at the parent's PRIMARY UNIFORM
  comparator, computed by the parent's own `supply_scores` / `make_supply` /
  `grounded_raw_cos` code paths. No re-implementation.
- The **same paired bootstrap** (`paired_bootstrap`, `delta_ci`), N_BOOTSTRAP = 5000,
  BOOTSTRAP_SEED = 20260813.
- NO FILE UNDER `hdlab/` AND NO FILE OF THE PARENT CELL IS MODIFIED.

**POSITIVE CONTROL (SCHEMA-VET gate D), evaluated before any split:** the re-derived pair set must
have n = 350 and every arm's rho on all 350 must reproduce `rho_primary` above to within 1e-4.
Outside tolerance => `HARD_FAIL_PARENT_NOT_REPRODUCED`, no split is interpreted.

## 3. The splits -- defined here, BEFORE any result is seen

### SPLIT 1 (PRIMARY, taxonomic, categorical) -- WordNet 3.0, external and non-circular

Source: NLTK WordNet 3.0 (`C:\Users\marsh\AppData\Roaming\nltk_data\corpora\wordnet.zip`;
`wn.get_version() == '3.0'`). NOTE: `data/wordnet_cache/` named in the dispatch brief is EMPTY on
disk; the nltk corpus is the actual asset.

For a pair (a, b) with SimLex POS p in {N, V, A}, let S(w) be w's synsets restricted to
p (N->NOUN, V->VERB, A->ADJ + ADJ_SAT). If S(w) is empty for either word, fall back to all-POS
synsets and count the fallback.

**NEAR iff any of:**
- **N1 SYNONYM:** `S(a) & S(b) != {}` (the two words share a synset).
- **N2 CO-HYPONYM:** exists sa in S(a), sb in S(b) with
  `sa.hypernyms() & sb.hypernyms() != {}` (shared DIRECT hypernym -- siblings).
- **N3 ADJ-CLUSTER (author extension, disclosed):** for POS = A only, `sb in sa.similar_tos()` or
  `sa in sb.similar_tos()`. WordNet adjectives carry NO hypernym links, so without N3 every
  non-synonymous adjective pair is FAR by construction of the resource rather than by semantics.
  The count of pairs made NEAR by N3 ALONE is reported so the split can be read without it.

**FAR = everything else.** Parent/child (hypernym) pairs are NOT counted NEAR -- the brief's
definition is siblings-or-synonyms and it is followed literally.

**Why this is independent of the arms being scored:** arm A/B/E features come from the simplewiki
COPULA/GLOSSARY_COLON extractor + the v6 ISA store; arm C is the Lancaster sensorimotor +
Brysbaert concreteness norms; arm D is CSKG-minus-lexical-relations. None of them reads WordNet at
score time. **Disclosed partial exception:** CSKG is a MERGED graph that includes WordNet among its
sources, so arm D's features have partial provenance overlap with the split criterion. Arm D's
NEAR/FAR contrast is therefore reported with that caveat and is NOT used to set the read.

### SPLIT 1B (CO-PRIMARY, taxonomic, balanced) -- guaranteed powered

`wnsim(a,b) = max over sa in S(a), sb in S(b) of sa.path_similarity(sb)` (None-safe).
NEAR_G = `wnsim >= median(wnsim over the evaluated pairs with a defined wnsim)`; FAR_G = below.
Ties at the median go to NEAR_G (declared in advance). Pairs with undefined wnsim are excluded and
counted. This exists because SPLIT 1 may put fewer than 50 pairs in one half; a median split is
balanced by construction and so is powered whenever the parent set is.

### SPLIT 2 (SECONDARY, human rating) -- range restriction acknowledged UP FRONT

HIGH = `SimLex999 gold >= median(gold over the 350)`; LOW = below; ties to HIGH.
**Conditioning on the rating restricts the range of the very variable being correlated, which
mechanically depresses rho in BOTH halves.** This is reported, is NOT headlined, and no read is
taken from SPLIT 2 alone.

### SPLIT 3 (SECONDARY, dual-coding) -- SimLex concreteness quartile

CONCRETE = `concQ in {3, 4}`; ABSTRACT = `concQ in {1, 2}` (`concQ` is SimLex-999's own per-pair
concreteness quartile field, verified present on disk). Tests the drill's dual-coding prediction
(CITED@Xu et al. 2025: text recovers non-sensorimotor but not sensorimotor structure) directly.

## 4. What is computed for every (arm x split-half) cell

rho (Spearman), 95% percentile paired-bootstrap CI (5000 resamples, seed 20260813, resampling
pairs WITHIN the half and recomputing every arm on the SAME resampled index set), bootstrap sd,
`mde_95 = 1.96 * sd` (the smallest rho magnitude this half could distinguish from 0), and n.
All of it goes in one table in metrics.json.

## 5. POWER GATE (armed BEFORE the run; honoured absolutely)

`MIN_HALF_N = 50`. Any half with n < 50 is labelled **UNDERPOWERED**; its numbers are reported for
completeness but **NO READ IS DRAWN FROM IT**. If BOTH the SPLIT 1 and SPLIT 1B primary halves are
underpowered, the cell returns `UNDERPOWERED_NO_READ`.

## 6. PRE-DECLARED READS (frozen)

Read source, in this order: SPLIT 1 if both halves have n >= 50; else SPLIT 1B if both halves have
n >= 50 (disclosed as a fallback); else UNDERPOWERED_NO_READ.

- **NEAR_COLLAPSE** -- arm C's NEAR-half CI includes 0 AND arm C's FAR-half CI excludes 0 with
  rho > 0.
  *Read:* our one working channel does not work on the actual wall; every arm is at chance where
  it counts. The next build must CREATE near-neighbour signal from scratch rather than improve an
  existing channel.
- **NEAR_SURVIVES** -- arm C's NEAR-half CI excludes 0 (rho > 0).
  *Read:* the graded channel is a genuine partial solution to the real problem and is the right
  thing to build on. The FORMAT (graded vs symbolic) is then the load-bearing difference, since
  every symbolic arm is at chance in both halves.
- **MIXED** -- anything else (e.g. both halves null; or FAR null while NEAR positive). Stated
  plainly, NOT forced into either read.

**Reported for its own sake (does not set the read):** do any of the SYMBOLIC arms A / B / D have
a FAR-half CI excluding 0? If symbols work for coarse distinctions and fail only on fine ones,
that is a different and more hopeful diagnosis than "symbols carry nothing", and it changes what
gets built next. Flag emitted: `SYMBOLS_WORK_COARSE` / `SYMBOLS_CARRY_NOTHING`.

## 7. Compute architecture / SCHEMA-VET fields

```yaml
compute_class: sequential-CPU with justification   # 350 pairs; parent FULL was 19.4s wall
                                                    # MEASURED@parent metrics.json:elapsed_s
storage_strategy: no_storage
cardinality_ok: true                # EXPECTED_N_UNITS = 6 arms x 8 half-cells = 48, gated
final_metrics_atomicity: tmp_replace
arms_differ_verified: true          # sha256 per arm score-vector; parent's own AF check re-run
crlb_n/a: "no quantitative noise floor; the power statement IS the paired bootstrap, reported as
           per-half mde_95 = 1.96 * bootstrap sd"
discriminator_reachability: true    # a rho CI excluding 0 is reachable at n=175 whenever the
                                    # pooled rho of 0.2759 at n=350 is real
baseline_in_band: n/a               # this is a DIAGNOSTIC re-analysis, not a mechanism gate; the
                                    # parent's arms are the baseline and are already in band
calibration_check: default_ok_for_this_regime   # every arm is the parent's own frozen code
deterministic_seeding: true         # fixed ints + hashlib only; sorted(set()) everywhere
positive_control_arms:
  - arm: PARENT_REPRODUCE_ALL_350
    cited_prior_metric: {A: 0.0247, B: 0.0179, C: 0.2759, D: 0.0751, E: -0.0235}
    cited_prior_source: data/exp_differentia_feature_supply_v1/metrics.json:rho_primary
    tolerance: 0.0001
    if_outside_tolerance: HARD_FAIL_PARENT_NOT_REPRODUCED
cell_chunked: false                 # single-seed, no seed axis
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
progress_logging: print_flush_true
smoke_output_dir_separate: true     # data/exp_near_vs_far_diagnostic_v1_SMOKE_p<N>
```

## 8. Functional requirements

1. *Re-derive the parent's exact pair set* -> parent's own eligibility + leak-control code, gated
   by the n=350 + rho positive control.
2. *Score the same arms* -> parent's `make_supply` / `supply_scores` / `grounded_raw_cos`.
3. *Partition by an arm-independent difficulty criterion* -> WordNet 3.0 (new; no substrate
   primitive exists for this and none is claimed).
4. *Quantify each half honestly* -> parent's paired bootstrap + an explicit MDE + a hard n>=50
   power gate.

## 9. What would make this cell WRONG (declared in advance)

- If the re-derived set is not exactly the parent's 350 pairs, every number here is about a
  different experiment. Gated by the positive control.
- If NEAR/FAR is defined by anything the arms can see, the split is circular. Mitigated by using
  WordNet; the CSKG/WordNet provenance overlap for arm D is disclosed above and arm D is excluded
  from setting the read.
- If a half is small, its CI is wide and "CI includes 0" means "we could not tell", NOT "there is
  nothing there". That is exactly what `mde_95` and the n>=50 gate are for, and it is why
  NEAR_COLLAPSE requires the FAR half to be POSITIVE rather than merely larger.
