# Pre-reg: exp_wiqa_causal_chain_oracle_structure_v1

Filed by: exp_dev (Sonnet, foreground, no nested sub-agents, no queue dispatch -- CPU-only
glass-box text processing on the real WIQA dev split + WIQA's own official gold-explanation
release, per Director's task Contract, run FOREGROUND TO COMPLETION locally, CHEAP, no
queue_add). Filed alongside the already-executed `--self-test` / `--smoke` / `--full` runs (all
completed this session before this doc was written) because `DECISIVE_MARGIN=0.05` and
`DECISIVE_COLLAPSE_FRACTION=0.5` are exactly Director's task-contract numbers, fixed in code
BEFORE the full-dev run executed -- no post-hoc tuning against observed numbers (same discipline
as v2's pre-reg).

## Prior-work check (mandatory, 2026-07-01 USER-locked)

`bash tools/substrate_query.sh "gold oracle causal structure WIQA influence graph extraction
bottleneck diagnostic"` -> top hit `EXTRACTION_BOTTLENECK` (cosine=0.3311,
`data/exp_grounded_appraisal_transfer_to_text_v1/metrics.json`) and a meta-synthesis atom
(cosine=0.2949, `data/substrate_index/meta/cert_ledger.jsonl`) reading "given correct [causal]
structure the mechanism works ... but extraction of structure from real prose bottlenecks" -- a
CLOSELY RELATED prior finding from a DIFFERENT corpus/mechanism (grounded_appraisal_transfer /
CSKG causal-organ: causal_organ=0.9167 given links vs causal_link_detection=0.3611 in the wild),
not a duplicate of this WIQA-specific oracle-structure cell (no hit is this exact test).
**Prior-work check verdict: NOVEL for WIQA; CONSISTENT-HYPOTHESIS-CLASS with a prior CSKG-side
finding.** That prior finding predicted a HARD_PASS was plausible here; this cell's measured
result (HARD_FAIL, see below) is therefore an informative DIVERGENCE from that prior pattern, not
a redundant confirmation -- worth flagging to Director as a cross-corpus disagreement.

## Question

Director's task (decisive diagnostic): does CAUSAL-CHAIN-LOOP (the mechanism validated/landed in
`exp_wiqa_causal_chain_loop_v1`/`v2`, both of which found the mechanism's small edge over
POLARITY-ECHO was NOT causally-grounded on internally-extracted structure) beat the WIQA
baselines when handed WIQA's OWN gold perturbation/effect structure instead of the internal
weak regex+HD-BoW extraction? Isolates: is EXTRACTION the bottleneck (loop wins with gold
structure), or is the causal-composition APPROACH itself flawed (loop loses even with gold
structure)?

## What "gold structure" means here -- read before trusting any number (VET section, mandatory)

The cached HF `data/corpora/wiqa/hf_dataset` (10 columns: question_stem / question_para_step /
answer_label / answer_label_as_choice / choices / metadata_question_id / metadata_graph_id /
metadata_para_id / metadata_question_type / metadata_path_len) does **not** carry step-level
cause/effect anchors or signed edges -- MEASURED this session (`schema_check_report_v2.json` +
direct `datasets.load_from_disk` inspection).

**Gold source used:** WIQA's own EMNLP-2019 "with_explanation" release (its own official crowd
annotation, downloaded from the same S3 bucket `allenai/wiqa-dataset`'s `dataset_info.py` points
at -- not an external extractor / not an LLM):
`https://public-aristo-processes.s3-us-west-2.amazonaws.com/wiqa_dataset_with_explanation/dev.jsonl`,
cached at `data/corpora/wiqa/raw_official/dev_with_expl.jsonl`. MEASURED this session: 5005
records; every one of its `id`s is a strict subset of the HF dev split's 6894
`metadata_question_id`s (100% containment, verified by direct set intersection). Coverage of the
full HF dev split: **2893/6894 = 41.96%** have a valid in-paragraph gold anchor pair (the
remaining 5005-2893=2112 are `OUTOFPARA_DISTRACTOR` items which by WIQA's own design have
`i=j=-1`, a genuine structural negative -- these questions are provably disconnected from the
paragraph, not a coverage gap; the other 6894-5005=1889 items are simply outside the
"with_explanation" release's scope). Each covered record supplies `explanation.i` /
`explanation.j`: WIQA's own crowd-annotated PARAGRAPH-STEP INDICES (0-indexed into that record's
own `steps` list) for the perturbation-anchor and effect-anchor of that specific question.

**LEAK CHECK (mandatory, Director explicitly required this be vetted hard).** The same release
also carries `explanation.di` / `explanation.dj` (SituationLabel enum: `RESULTS_IN` /
`RESULTS_IN_OPP` / `NO_EFFECT`). MEASURED this session, self-test `dj_leak_check` (real sample,
n=200) and an independent full-population check (n=5005, ad hoc verification script, not part of
the committed cell): mapping `dj -> {RESULTS_IN: 'more', RESULTS_IN_OPP: 'less', NO_EFFECT:
'no_effect'}` reproduces `answer_label` at **200/200 = 1.0000** (sample) and **5005/5005 =
1.0000** (full population) match rate. This is not a coincidence: `allenai/wiqa-dataset`'s own
`WIQAQuestion.instantiate_from` computes `answer_label = chosen_label.as_less_more()` where
`chosen_label` comes directly from `explanation['dj']` -- `dj` **is** the answer, stored under a
different field name. **`di`/`dj` are therefore EXCLUDED ENTIRELY from this oracle.** Using either
would be reading the label off an alias field, exactly the vacuous-win Director warned against.

**Scope of the oracle actually implemented (PARTIAL, not full signed-graph):** ONLY the
ANCHOR-RETRIEVAL half of the internal mechanism (`anchor_step()`'s HD-BoW-cosine pull-in --
"WHERE in the paragraph does the perturbation/effect happen") is replaced by WIQA's gold `(i,
j)`. EDGE-POLARITY extraction (`has_negating_word` regex check per adjacent-step hop, feeding
`build_register`/`propagate_sign` -- "was this hop a promotes or inhibits edge") is UNCHANGED
from the internal loop. No non-leaking gold source for per-edge signed polarity was found: the
full `wiqa_influence_graphs.jsonl` graph release (also downloaded this session, 2107 graphs) was
inspected and encodes an if-then TEMPLATE (`X`, `Y`, `W`, `U`, `Z`, `V` node-phrase lists per
graph_id), not a step-index-aligned signed chain across `question_para_step` -- mapping it onto
`build_register`'s adjacent-step edges would re-solve the same extraction problem it's meant to
bypass, so it was not used. **A HARD_PASS verdict from this cell would mean anchor-retrieval
extraction is a verified bottleneck component and gold anchors + the EXISTING weak edge-sign
mechanism compose into a genuine, scramble-sensitive gain; it would NOT independently certify
that edge-sign extraction is equally fixable.** (Moot for this run -- see Results: HARD_FAIL.)

Raw `steps` field in the official release (index-aligned with `i`/`j`) is used for anchor/register
construction, NOT the HF `question_para_step`. MEASURED this session: raw-vs-HF-filtered step
COUNT differs on 707/5005 = 14.1% of matched records (trailing punctuation-artifact splits) --
using the wrong list would silently misalign gold indices.

## Design

Reuses `experiments/exp_wiqa_causal_chain_loop_v2.py`'s primitives UNCHANGED via direct import
(`build_register`, `propagate_sign`, `load_dev`, `score_item_base`, `_deterministic_perm`,
`D`, `GATE_THRESH`) -- majority / polecho / bow / loop-internal predictions per item are
byte-identical to what v2 already computed and landed (no re-implementation, no drift risk).
New code adds: `load_gold_map()` (parses the official release), `score_item_oracle()` (gold
`(i,j)` anchors + internal edge-polarity + v2's own `propagate_sign` walk), and
`score_item_oracle_scramble()` (gold anchors + the SAME deterministic negation-check-order
permutation scheme as v2's ABLATION-1, i.e. the GOLD-EDGE-SCRAMBLE control).

### Compute architecture

Sequential-CPU, same as v1/v2 (dict lookups + <=1024-dim vector sums/dots over <=10 steps per
item). MEASURED this session: FULL landed in 17.808s wall for 6894 items x 3 seeds (same order of
magnitude as v2's 17.555s).

### Arms (all subsets)

majority, polecho, bow, loop_internal (v2's mechanism, reference), loop_oracle (this cell's
gold-anchor arm), oracle_scramble (GOLD-EDGE-SCRAMBLE control on loop_oracle, median of 3 seeds
[7, 17, 29] matching v1/v2 convention).

### Subsets

- **all** (n=6894): context only, NOT the gate (loop_oracle is diluted here by the 58% of items
  with no gold anchor, which fall back to polecho -- same abstain convention as v1/v2).
- **oracle_covered** (n MEASURED=2893): items with a valid, in-bounds gold `(i,j)` anchor.
  **PRIMARY decisive subset** -- majority/polecho/bow/loop_internal/loop_oracle/oracle_scramble
  all evaluated on this SAME matched denominator (fair, apples-to-apples; the oracle can only
  ever act on items it has gold structure for, so gating baselines on the SAME subset avoids
  penalizing loop_oracle for a coverage gap unrelated to the mechanism).
- **oracle_covered_multihop** (n MEASURED=996): oracle_covered AND gold hop distance
  `|j - i| >= 2`. SECONDARY/supporting subset (genuine multi-hop composition demand, parallel to
  v2's `active_multihop`) -- reported and included as a caveat in `verdict_msg` if it disagrees
  with the primary tier, but does not override the primary gate (Director's contract specifies a
  single two-baseline-set decisive comparison, not v2's fuller 4-subset stratification).

## Pre-reg bands (Director's task contract, verbatim numbers)

Evaluated on `oracle_covered` (primary):
- **HARD_PASS** (`ANCHOR_EXTRACTION_IS_THE_BOTTLENECK`): `loop_oracle` beats majority AND
  polecho AND bow each by `>= DECISIVE_MARGIN=0.05`, AND
  `collapse_frac = (loop_oracle - oracle_scramble_median) / (loop_oracle - polecho) >=
  DECISIVE_COLLAPSE_FRACTION=0.5` -- the causal-chain mechanism is sound given correct anchors;
  the wall (scoped to this cell's PARTIAL oracle) is anchor-retrieval extraction.
- **HARD_FAIL** (`INFERENCE_APPROACH_FLAWED_EVEN_WITH_GOLD_ANCHORS`): `loop_oracle` does NOT
  beat all three baselines by `>=0.05` -- the composition/inference approach itself does not
  deliver even with WIQA's own gold anchors; deeper reconsideration warranted.
- **MIDDLE_BAND** (`ORACLE_BEATS_BASELINES_BUT_GAIN_NOT_CAUSAL`): beats all three baselines by
  `>=0.05` but `collapse_frac < 0.5` -- gain looks topological/structural, not genuine
  signed-edge reasoning (same pattern v2 found for the internal mechanism).

`arms_differ_verified` (6-arm hash-differ) overrides any tier to HARD_FAIL if arms collapse to
identical predictions (META_RULE_AF).

## SCHEMA-VET fields

`arms_differ_verified` (6 arms, all pairs confirmed differ), `final_metrics_atomicity=tmp_replace`
(via `_seed_checkpoint.write_metrics`), no bare `except:` / `except BaseException:` (grep-verified
clean), `crlb_n/a` declared (discrete classification accuracy, no capacity/noise-floor
threshold), `cardinality_ok` (`EXPECTED_N_UNITS=len(SEEDS_FULL)=3`), per-unit failure-class
instrumentation (`DEGRADED_BUDGET=0.02`, measured 0), `calibration_check=default_ok_for_this_regime`
(reuses v2's `GATE_THRESH`/lexicon unchanged; this cell adds a new gold ANCHOR SOURCE not a new
calibration knob), `deterministic_seeding=true` (hashlib-based `_deterministic_perm`, no
`hash()`/`list(set())` -- grep-verified), `progress_logging=print_flush_true`,
`real_code_path_and_signature_preflight` (self-test constructs the REAL `CausalLinkRegister` via
v2's `build_register`/`propagate_sign` + loads a real 20-item sample from the official release
through the FULL oracle pipeline; `substrate_signature` binds `CausalLinkRegister.__init__` /
`.add_causal_link` against `inspect.signature`).

Self-test additions specific to this cell: `_hand_case_oracle_vs_internal_divergence` (hand-built
4-step paragraph where BoW-pull-in would land on a decoy step but gold `(i,j)` points correctly;
asserts sign flips correctly when the true path crosses a negating word), `_hand_case_no_coverage`
(gold=None or covered=False falls back to `pred_polecho`, does not raise), `_hand_case_zero_hop_oracle`
(gold `i==j` propagates as `sign=+1`, empty trace, reusing v2's already-tested zero-hop invariant
through the new oracle code path), `_dj_leak_check_real_sample` (MEASURED, not hand-built: asserts
>=50 real records are checkable and reports the match rate numerically in metrics.json, so a
future re-run that finds a LOWER match rate is visible rather than silently passing a weaker
assert).

## Results (MEASURED, full dev, 6894 items, 3 seeds [7,17,29], elapsed_s=17.808)

| subset | n | majority | polecho | bow | loop_internal | loop_oracle | scramble (median/3) | oracle-polecho | collapse_frac |
|---|---|---|---|---|---|---|---|---|---|
| all | 6894 | 0.3333 | 0.3420 | 0.3281 | 0.3489 | 0.3567 | 0.3552 | +0.0147 | 0.099 |
| **oracle_covered (primary)** | **2893** | **0.5064** | **0.4075** | **0.4673** | **0.4276** | **0.4424** | **0.4390** | **+0.0349** | **0.099** |
| oracle_covered_multihop | 996 | 0.5100 | 0.4137 | 0.4578 | 0.4357 | 0.4588 | 0.4488 | +0.0452 | 0.222 |

**Verdict: HARD_FAIL / `INFERENCE_APPROACH_FLAWED_EVEN_WITH_GOLD_ANCHORS`.** On the primary
`oracle_covered` subset, `loop_oracle=0.4424` **loses to majority** (`-0.0639`, majority is the
label-blind always-"more" rule) and **loses to bow** (`-0.0249`); it beats polecho by only
`+0.0349`, under the `0.05` margin, and even that small edge does not survive the gold-edge-
scramble control (`collapse_frac=0.099`, far below the `0.5` decisive threshold -- almost none of
the tiny polecho-edge depends on genuine signed-edge information, the same "topology not
causality" signature v2 found for the fully-internal mechanism). The `oracle_covered_multihop`
subset tells the same story (loses to majority `-0.0512`, ties bow `+0.0010`, `collapse_frac=0.222`).
`oracle_fired_rate_within_covered=0.546` (the oracle abstains on ~45% of covered items, almost
entirely via `pp_zero` -- the perturbation-clause polarity-lexicon gate, unrelated to anchor
quality). `n_internal_anchor_diverges_from_gold_anchor=2558/2892` checked (88.4%) -- the internal
HD-BoW pull-in disagrees with the gold anchor on the large majority of items, confirming the
internal extraction really was picking different (and, per this result, not obviously worse-
performing) anchors than the gold ones.

**Honest reading (Director's framing: report the truth, do not engineer toward a collapse).**
Even freed from its most commonly-suspected weakness (anchor retrieval), the causal-chain-loop
mechanism still loses to a data-blind majority-class rule on the matched subset. Since majority
uses **zero** information about the item, `loop_oracle < majority` is about as clean a signal as
this kind of test can produce: gold ANCHOR information alone does not rescue the mechanism. This
is scoped honestly -- the edge-POLARITY half of extraction remained the internal weak regex
mechanism throughout this test (see "Scope" section above; no non-leaking gold source for it was
found), so the strictly narrowest true claim is "gold anchor-retrieval, composed with the
EXISTING weak edge-sign extraction, is not sufficient" rather than "a fully gold signed-graph
oracle would also fail." But combined with (a) `loop_oracle` losing to majority outright and (b)
the residual polecho-edge itself not surviving gold-edge-scramble (collapse_frac=0.099, an order
of magnitude below the 0.5 threshold), the weight of evidence points toward the composition
mechanism / edge-sign extraction being the deeper problem, not merely "we didn't know where to
look" -- consistent with, and now extending, v1/v2's own finding that the internal mechanism's
edge over polecho was never causally-grounded on internally-extracted structure. Diverges from
the prior-work-check's CSKG-side precedent (that arc found `causal_organ=0.9167 given links`,
i.e. gold-structure rescue DID work there) -- flagged as a genuine cross-corpus/cross-mechanism
disagreement for Director, not smoothed over.
