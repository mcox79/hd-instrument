# Pre-reg: mcscript2_oracle_clustering_probe_v1 (decisive rescue-direction diagnostic)

**Filed-by:** exp_dev, 2026-08-09.
**Task:** Director task -- "is there enough chance / was it fair" oracle-upper-bound test
for the MCScript2.0 HARD_FAIL (`exp_mcscript2_real_benchmark_validation_v1`,
commit `5c1199f87`: system commonsense acc 0.5538 < text-overlap baseline 0.5859,
root cause = greedy CA3/DG keying over-merges to item purity 0.20 (33 grounded items
covering 195 TRAIN scenarios, mean n_traces=75.7, mean majority_frac=0.1999)).

**Parent (HARD_FAIL being diagnosed):** commit `5c1199f87`,
`data/exp_mcscript2_real_benchmark_validation_v1/metrics.json`,
`experiments/exp_mcscript2_real_benchmark_validation_v1.py`,
`hdlab/mcscript_extraction.py`, `hdlab/script_grain_acquisition_loop.py`.

## Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring)

`bash tools/substrate_query.sh "MCScript oracle clustering upper bound gold scenario
script grounding purity"` -- see run log in completion report. This is a same-day
follow-up diagnostic on a cell landed hours ago in this same session; the relevant
"prior work" is that landed cell itself (5c1199f87), already cited above and reused
verbatim below, not a separate KB rediscovery risk.

## CONTRACT (fixed by Director, not exp_dev's to vary)

Reuse VERBATIM: `hdlab/mcscript_extraction.py` (parse_mcscript_xml,
extract_instance_tuple, extract_root_verb, extract_args, split_sentences),
`experiments/exp_mcscript2_real_benchmark_validation_v1.py`'s Stage-2 MC-scoring
primitives (`text_overlap_decide`, `script_decide`/`script_decide_cached`,
`item_context_prototype`, `_cos`/`_bundle`/`context_vector` from
`hdlab.grounding_acquisition_loop`) and baselines (`compute_majority_answer_id`,
`baseline_accuracies`, `precheck_a_keying_discriminates` for the item-forensics
real-system reproduction only). ONLY the clustering-construction step and the
representation used for MC-scoring are swapped.

## Q-A: ORACLE UPPER BOUND (the decisive number)

**Design:** replace `ScriptLibrary.match_or_spawn` (greedy CA3/DG online clustering,
the diagnosed over-merge culprit) with GOLD grouping: one library item per TRUE
TRAIN scenario (`inst["scenario"]`), item's traces = ALL TRAIN instances of that
scenario -> purity = 1.0 by construction (195 items, matching `n_train_scenarios`).
DEV routing is ALSO oracle (DEV instance's own `scenario` field selects which
TRAIN-only-built item to score against -- zero query/routing noise on either end,
so the resulting number isolates PURELY the MC-scoring step, not clustering +
routing + scoring jointly). Anti-circularity preserved: DEV instance TEXT is never
added to any library item's traces; only the DEV-side ground-truth scenario LABEL
selects which (TRAIN-only) prototype to query -- this is the oracle/upper-bound
probe, explicitly NOT a claim about a deployable system (a deployable system does
not have DEV gold labels at inference time).

Representation = BoW `context_vector` (Amendment-1's signal, what the landed HARD_FAIL
actually scored with) for the PRIMARY oracle number (comparable apples-to-apples with
the 0.5538/0.5859 landed numbers).

**Interpretation bands (PRE-REGISTERED before running):**
- **ORACLE_BEATS_BASELINE** (clustering-fixable -> DG-separation rescue worth pursuing):
  `oracle_bow_commonsense_acc > 0.5859 + 0.02` (2-point non-trivial margin, single
  deterministic run, no seed variance available -- require a real margin, not a
  hairline beat, per META_RULE_L strictly-above-floor discipline applied here to
  "above baseline" instead of "above floor").
- **ORACLE_LOSES** (approach-insufficient -> rescue needs a different architecture,
  not better clustering): `oracle_bow_commonsense_acc <= 0.5859`.
- **MIDDLE_BAND** (marginal, inconclusive): beats by less than 0.02 -- flag for a
  bootstrap/resample check before committing to either rescue direction.

## Q-B: REPRESENTATION FAIRNESS (under the SAME oracle clustering)

**Design:** build a SECOND set of oracle item prototypes using the REAL FHRR
script role-structure representation (`hdlab.script_grain_acquisition_loop.
build_instance_register`, TRIGGER/CONSEQUENT/AGENT/PATIENT bind-bundle, the
`situation_model_accumulate`-family role-binding organ) instead of BoW:
TRAIN-side traces use `extract_instance_tuple` (the SAME full-narrative 4-slot
extraction already exercised for the landed cell's glass-box audit sample,
now run over ALL 2500 TRAIN instances instead of 20). Item prototype = FHRR
bundle of successfully-extracted TRAIN traces' registers (scenarios with zero
successful extractions fall back to a logged neutral decision, counted and
reported, not silently dropped).

**Disclosed asymmetry (found before running, not after):** `extract_instance_tuple`
requires >=2 sentences (it is a full-narrative extractor); MC candidate ANSWERS are
short spans (single words, NPs, PPs, or occasional full clauses -- verified by
direct inspection of `dev-data.xml`, e.g. "a beer" / "at the bar" / "So they could
hang the pictures up"), so the narrative-level extractor cannot apply to answers
as-is. `extract_answer_role_tuple` (NEW, this cell, reusing `extract_root_verb`/
`extract_args` from `hdlab.mcscript_extraction` verbatim) treats the whole answer
text as ONE clause: if a root verb is found, trigger=consequent=that lemma,
agent/patient from `extract_args`; if no verb is found (the common case for bare-NP
answers), trigger/consequent/agent collapse to constant placeholder fillers and
patient falls back to the answer's rightmost content word (crude head-noun proxy).
This is disclosed UP FRONT as a granularity mismatch the FHRR representation must
absorb that BoW does not (BoW's bag-of-content-words applies losslessly to text of
any length) -- if FHRR underperforms BoW, part of the explanation is expected to be
this representational mismatch, not necessarily that role-structure is worthless in
principle; the report will not overclaim past what was actually measured.

**Interpretation bands (PRE-REGISTERED before running):**
- **FHRR_ADDS_VALUE**: `oracle_fhrr_commonsense_acc > oracle_bow_commonsense_acc + 0.02`.
- **FHRR_NO_BETTER** (fairness finding -- the script-grain claim was never really
  exercised, at either the keying step [Amendment 1, already measured, gap=0.028
  vs 0.153] or the scoring step): `oracle_fhrr_commonsense_acc <=
  oracle_bow_commonsense_acc + 0.02`.

## Item forensics (real AS-RUN system, not oracle)

Deterministically REPRODUCE the landed real-arm library (same TRAIN sort order,
same `precheck_a`-calibrated `novelty_thresh`, same 5-pass `script_consolidation_pass`
sequence -- everything in the real arm is seedless/deterministic, so this must
reproduce the landed 0.5538 commonsense accuracy exactly; verified as a sanity gate
before trusting any per-item record). Log every DEV commonsense question's
(system_pred, text_pred, correct_id, matched_item_id, match_score, use_script).
Filter to `qtype=="commonsense" AND system_pred != correct_id AND text_pred ==
correct_id`; sample up to 20, diversified across distinct `matched_item_id`s
(<=2 per item) rather than a single contiguous block, deterministic sort order.
Each sampled case categorized by hand (exp_dev's own read, in the completion
report) into GENUINE_SCRIPT_INFERENCE / NOISE_OR_SCORING_ARTIFACT / AMBIGUOUS.

## Compute architecture

Sequential-CPU, justified: (b) is a hashlib-seeded deterministic FHRR-register
build over ~2500+4040 short texts through the OWNED `CandidateGenerator` (a
from-scratch hashed perceptron POS-tagger + arc-parser, not a GPU-batchable
matmul-heavy primitive) -- measured 0.093s/instance x 2500 ~= 233s TRAIN +
~40-80s DEV-answers; (a) and item-forensics reproduction are BoW/hashlib-only,
each <70s (matches the landed cell's own `elapsed_s=62.5s` for growing BOTH
real+scramble arms). Total estimated wall <= 400s, single INLINE-LOCAL foreground
run (no push/remote-persist authorized for this task -- "Local." per Director).
No GPU-batching candidate here (Stage-2 MC-scoring cell shape, not
argmax/top-k associative recall).

## Determinism / anti-circularity / no-padding

- `deterministic_seeding: true` -- hashlib-only throughout (reused primitives),
  `sorted(..., key=lambda x: x["id"])` for all TRAIN/DEV iteration order, no
  `hash()`, no `list(set())`.
- DEV never mutates any library/item (read-only oracle routing by ground-truth
  label only, TRAIN-only-built prototypes).
- No filler experiments: this is the single decisive diagnostic the Director
  requested, run once to completion.

## Self-test / smoke / full

- `--self-test`: tiny hand-built XML (2 scenarios), exercises the REAL
  `CandidateGenerator`, `extract_instance_tuple`, `extract_answer_role_tuple`,
  gold-grouping, both prototype builders, and the item-forensics reproduction
  path at N~8, per SCHEMA-VET F.1.
- `--smoke`: first 15 TRAIN/DEV scenarios (matches the landed cell's own smoke
  convention) -- full pipeline at reduced scale, sanity-checks timing + that the
  oracle numbers are not degenerate (coverage=1.0 by construction, so no
  saturation risk from a fallback path).
- full: all 2500 TRAIN / 355 DEV, single foreground run, `final_metrics_atomicity:
  tmp_replace`.
