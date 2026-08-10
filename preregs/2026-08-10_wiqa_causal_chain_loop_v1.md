# Pre-reg: exp_wiqa_causal_chain_loop_v1

Filed by: exp_dev (Sonnet, foreground, no nested sub-agents, no queue dispatch -- CPU-only glass-box
text processing on the real WIQA dev split, expected to run in well under 10 minutes; per Director's
task Contract, run FOREGROUND TO COMPLETION rather than routed to a remote queue).

## Prior-work check (mandatory, 2026-07-01 USER-locked)

`bash tools/substrate_query.sh "WIQA causal chain polarity propagation signed cause effect what-if
procedural text"` -> top hit cosine=0.3428 (entity='causal', source=wordnet, generic lexical entry,
not a substantive drill), second hit cosine=0.3174 (`notes/research_drill_substrate_gap_causal_
counterfactual_3x_2026-06-07.md` "Angle 5: Bayesian causal networks via substrate probability
encoding" -- a DIFFERENT, never-built idea about alpha-weighted probabilistic causal binding, not
signed multi-hop polarity propagation). Both above the 0.30 dedup threshold, so per discipline I also
read the two next-closest SUBSTANTIVE hits: `preregs/2026-07-24_read_causal_chain_on_chain_cause_v1.md`
(cosine=0.3086) + its metrics (cosine=0.3018, HARD_PASS). That cell is a DIFFERENT task: single-hop
"why did X happen" cause-of-outcome identification on 16 hand-labeled LitBank narrative passages (no
signed polarity, no multi-hop chain propagation, no 3-way more/less/no_effect classification, no real
benchmark). It validates the sibling `experiments/_causal_network.py` CAUSAL_NET mechanism (connective
+ bridging + KGStore one-hop recall), not this cell's signed-polarity multi-hop propagation over
`CausalLinkRegister`. **Prior-work check verdict: NOVEL.** This is genuinely the first cell to (a) pull
and score WIQA, (b) extend `CausalLinkRegister` with a polarity bit, (c) do multi-hop signed
propagation with anchor-retrieval VALIDATE -- not a rediscovery of the causal-network or Stage-2A
cells, which this cell composes/extends rather than repeats.

## Question

Director's task (WIQA flagship pivot, first cell): does a glass-box causal-chain-propagation system --
extending `hdlab.situation_model_accumulate.CausalLinkRegister` with a signed polarity bit, anchoring
the perturbation and outcome clauses to paragraph steps via `hdlab.cleanup_family.iterative_attractor`
pull-in (Stage-1/Stage-2A's retrieve-VALIDATE pattern, re-instantiated for real WIQA prose rather than
literally imported, since Stage-2A's codec/register objects are synthetic-micro-world-specific) --
beat MAJORITY, POLARITY-ECHO (the sharpened surface-shortcut risk), and BoW-OVERLAP on WIQA dev
(6,894 questions), with a knowledge-scramble ablation collapsing the gain and a >=2-hop oracle-labeled
subset showing a differential advantage?

## FIRST MOVE: live data pull + schema-check (COMPLETED, real, on disk)

`allenai/wiqa` load via `datasets.load_dataset("allenai/wiqa")` **FAILED** on `datasets==4.8.5`
(`RuntimeError: Dataset scripts are no longer supported, but found wiqa.py` -- the HF `datasets`
library dropped script-based dataset loaders; WIQA's HF repo still ships the legacy loader script).
**Fallback (worked, real data, not fabricated):** HF auto-converts every legacy script dataset to
parquet on the `refs/convert/parquet` branch; `datasets.load_dataset("allenai/wiqa",
revision="refs/convert/parquet")` succeeded. Confirmed split sizes EXACTLY match the scoping drill's
literature figures: train=29808, validation=6894, test=3003
MEASURED@d:/AI/hd-instrument/data/corpora/wiqa/schema_check_report_v2.json. Saved to local disk
(`data/corpora/wiqa/hf_dataset/`, Arrow format) so the cell loads offline from here, not re-pulling
from HF on every run.

**Schema (fields, MEASURED@d:/AI/hd-instrument/data/corpora/wiqa/schema_check_report_v2.json):**
`question_stem` (str, "suppose X happens, how will it affect Y."), `question_para_step` (list[str],
paragraph steps in order, some trailing empty strings), `answer_label` (str, literal `"more"` /
`"less"` / `"no_effect"` -- NOT A/B/C codes), `answer_label_as_choice` (A/B/C), `choices` (dict),
`metadata_question_id`, `metadata_graph_id`, `metadata_para_id`, `metadata_question_type` (one of
`INPARA_EFFECT` / `EXOGENOUS_EFFECT` / `OUTOFPARA_DISTRACTOR`), `metadata_path_len` (int, the gold
influence-graph path length -- **the multi-hop oracle label**, present directly in the row metadata,
no derivation needed). **The influence graph itself (nodes/edges) is NOT exposed as solver input** --
only these summary fields are in each row; confirms the scoping drill's precondition (solver never
sees the graph).

**Regex extraction of (perturbation, outcome) clauses**: `^suppose (.+?), how will it affect
(.+?)\.?$` matches **100.00% (6894/6894)** MEASURED@calibration (this session) -- fully reliable,
no fallback path needed.

## Design

### Dataset facts that shaped this design (measured on dev, MEASURED@calibration this session --
all numbers reproducible from the scratch scripts run this session; re-derivable from
`data/corpora/wiqa/hf_dataset/`)

- Dev label distribution: **exactly balanced** 2298/2298/2298 (more/no_effect/less, 33.33% each) --
  majority-class baseline is a real ~33.3% floor (paper's headline 30.66% likely computed over a
  different split/pooling; dev itself is exactly balanced). Train also exactly balanced
  9936/9936/9936.
- `metadata_question_type` dev counts: EXOGENOUS_EFFECT=2941, INPARA_EFFECT=1655,
  OUTOFPARA_DISTRACTOR=2298. **`no_effect` occurs ONLY on OUTOFPARA_DISTRACTOR items** (label dist:
  EXOGENOUS_EFFECT {more:1576,less:1365}, INPARA_EFFECT {more:722,less:933}, OUTOFPARA_DISTRACTOR
  {no_effect:2298} -- zero more/less on distractors, zero no_effect on the other two types).
- `metadata_path_len` dev distribution: {0: 2298 (== all distractors exactly), 2: 1510, 3: 2145,
  4: 941}. **No path_len==1 exists in this data** -- every substantive (non-distractor) question is
  already >=2 hops, so the pre-reg's ">=2 hop multi-hop subset" == ALL non-distractor questions
  (4596/6894 = 66.67%), not a narrow slice. This is GOOD for the design (the multi-hop gate isn't
  cherry-picking a sliver) but means "multi-hop" here does not further separate from "answerable at
  all" -- disclosed honestly, not framed as a stronger claim than it is.
- **HONEST NEGATIVE FINDING (content-ceiling confirmation, measured not assumed):** neither literal
  token-overlap NOR graded HD-bag-of-words cosine between the outcome clause and the paragraph
  separates distractor (path_len=0) from non-distractor questions. MEASURED@calibration: only
  408/2298 (17.75%) of true distractors have literally zero outcome-clause/paragraph token overlap;
  a full cosine-threshold sweep over the HD-BoW anchor score gives best balanced-accuracy = 0.4997
  (chance) for distractor-detection. Outcome-clause polarity-word presence rate is also
  statistically indistinguishable (79.90% distractor vs 77.65% non-distractor). **This means: no
  cheap glass-box lexical/HD-BoW signal available to this cell can detect the no_effect/distractor
  bucket.** WIQA's distractors are deliberately crafted to be as lexically plausible as real
  questions (confirms the scoping drill's content-ceiling hypothesis from a NEW angle: the ceiling
  applies to `no_effect` detection specifically, not just to more/less sign prediction). All arms in
  this cell are held to this SAME honest limitation -- none get a free no_effect detector; verdict
  bands are evaluated on what's actually measured, not adjusted to hide this.
- **POLARITY-ECHO real measured strength (the sharpened risk, MEASURED not assumed):** the two
  candidate formulations of "echo the stated polarity" were measured directly.
  Naive direct-echo (predict the perturbation clause's own literal more/less word as the final
  answer) = **0.3210** overall (WORSE than majority 0.3333 -- refuted as a threat; a compare-to-
  outcome-clause formulation is required for `answer_label`'s actual semantics, see next). Sign-
  compare (predict "more" if the perturbation-clause polarity word matches the outcome-clause's own
  stated polarity word, "less" if opposite, "no_effect" if the outcome clause has no polarity word,
  tie-broken to "more" when the perturbation lacks one) = **0.3420** overall, **0.4125** on the
  multi-hop subset, **0.2010** on distractors (worse than chance there -- it almost never predicts
  no_effect), **0.5359** on the "clean" subset where both clauses literally state a polarity word
  (n=2161/6894, 31.3%). **This is the real POLARITY-ECHO baseline implemented below.** It turned out
  WEAKER in aggregate than the scoping drill's flagged risk (+0.0087 over majority, not a large
  threat) but genuinely informative on its "clean" subset (+0.20 over majority there) -- an honest,
  measured finding, not assumed in either direction.
- **Edge-polarity structure is SPARSE (measured, tempers the mechanism's expected edge over naive
  sign-compare):** only 77 distinct process paragraphs underlie all 6894 dev questions. Of 519 total
  paragraph steps, only 11 (2.12%) contain a blocking/negating word (stop/prevent/block/limit/reduce/
  etc.); only 7/77 paragraphs (9.09%) have >=1 such step. **This means the mechanism's per-edge
  negation-flip will fire on a small minority of paragraphs** -- disclosed honestly up front, not
  discovered post-hoc as an excuse. The mechanism's larger, more reliable source of edge over
  POLARITY-ECHO is the OTHER structural difference identified below (direct propagated-sign
  interpretation when the outcome clause has no stated polarity word, ~21.6% of items), not the rare
  negation-edge case.

### Semantic finding that shapes the mechanism (reasoned + partially spot-checked, disclosed as
reasoning not a blanket verified fact): WIQA's `answer_label` semantics are NOT "echo the
perturbation's word." Worked example (train[0], MEASURED@d:/AI/hd-instrument/data/corpora/wiqa/
schema_check_report_v2.json): perturbation "there will be fewer new trees" (polarity=less), outcome
clause "LESS forest formation" (an explicit polarity-tagged trend), gold answer = "more". Reading:
fewer trees REINFORCES the already-stated "less forest formation" trend (same direction => "more" of
that trend), not "the forest becomes less" directly. So when the outcome clause carries an explicit
polarity word, the answer is a same/opposite-direction comparison (what POLARITY-ECHO implements).
When the outcome clause does NOT carry an explicit polarity word (~21.6% of items, since 78.4% do
per the measured stat above), there's nothing to compare against -- the natural reading is that the
answer describes the outcome's OWN direction of change directly. POLARITY-ECHO (as implemented above)
treats this case as "abstain to no_effect," which is very likely wrong on the ~78% of those items that
are not actually no_effect. **This is the mechanism's designed point of leverage**: a system that
propagates an actual SIGN to the outcome position (rather than only comparing two literal words) can
answer these directly instead of abstaining. This is a genuine structural difference, not a tuned-for-
PASS parameter -- it follows from the propagation architecture itself, and the full run will show
honestly whether it helps.

### Corpus size + regime

`data/corpora/wiqa/hf_dataset/` (Arrow, offline). Held-out split = **validation (dev)**, 6894
questions, used for ALL scoring (never touches test or train labels). Train (29808) used ONLY to
compute the single MAJORITY constant (a label-frequency count, not a fit).

### Mechanism: CAUSAL-CHAIN-LOOP

1. **Extract** `(pert_clause, outcome_clause)` via the 100%-match regex above.
2. **Polarity lexicon** (ASCII, hand-built, shared honestly with POLARITY-ECHO -- the differentiator
   is what's done with it, not the lexicon itself): `INCREASE_WORDS` / `DECREASE_WORDS` (~40 items
   each, common quantitative-change vocabulary: more/increase/greater/... vs less/fewer/decrease/
   reduce/without/sterile/stop/prevent/block/.... `detect_polarity(text)` returns +1 / -1 / 0
   (ambiguous-or-absent) by lexicon-hit with no-conflict requirement.
3. **Anchor retrieval** (`hdlab.cleanup_family.iterative_attractor` pull-in, Stage-1/Stage-2A pattern
   re-instantiated for real text): per item, build an HD bag-of-words codebook over the paragraph's
   steps -- each distinct content word (stopword-filtered) gets a deterministic bipolar {-1,+1}
   vector, keyed by `hashlib.sha256(f"wiqa_bow_word::{word}")` (PROT-023/F.5 compliant, no built-in
   `hash()`), D=1024 (project default). A step/clause encodes as the SUM of its content words'
   vectors (unnormalized bag-of-words bundle). `iterative_attractor(probe, step_codebook)` retrieves
   the best-matching step index; ADMISSION gate = raw cosine(probe, best step) >= `GATE_THRESH=0.05`
   MEASURED@calibration (set near the p10 of the non-distractor best-cosine distribution --
   INPARA_EFFECT pert_best p10=0.0531, EXOGENOUS_EFFECT p10=0.0331 -- low enough to preserve coverage
   on EXOGENOUS items whose perturbation is deliberately paragraph-external, high enough to reject
   genuinely empty/zero-overlap probes). Run separately for `pert_clause` -> `p_idx` and
   `outcome_clause` -> `o_idx`.
4. **Causal chain** (`hdlab.situation_model_accumulate.CausalLinkRegister`, polarity-extended): for a
   K-step paragraph, `add_causal_link(i, i+1, polarity)` for i in 0..K-2, where `polarity = -1` if
   step i+1 contains a negating/blocking word (see sparse-edge finding above) else `+1`. This is the
   REQUIRED extension point (see "CausalLinkRegister extension" below).
5. **VALIDATE gate + propagate**: if `p_idx` and `o_idx` both ADMITTED (cosine>=GATE_THRESH), `p_idx
   != o_idx`, and `pp = detect_polarity(pert_clause) != 0`: let `lo, hi = sorted([p_idx, o_idx])`;
   `path_polarity = product(edge_polarity[i] for i in range(lo, hi))`; `propagated_sign = pp *
   path_polarity`. Then: if `op = detect_polarity(outcome_clause) == 0`, predict `"more"` if
   `propagated_sign > 0` else `"less"` (direct interpretation, per the semantic finding above);
   else predict `"more"` if `propagated_sign == op` else `"less"`.
6. **ABSTAIN** (any of: an anchor not admitted, `p_idx == o_idx`, or `pp == 0`) -> fall back to
   POLARITY-ECHO's own prediction for this item -- the augment-not-replace / anti-regression pattern
   (same as E4's MCScript2.0 gate-test): CAUSAL-CHAIN-LOOP can never score below POLARITY-ECHO on the
   abstained subset by construction, since it reproduces POLARITY-ECHO's answer there exactly.

### `CausalLinkRegister` extension (the required small addition, per Director's task)

`hdlab/situation_model_accumulate.py`'s `CausalLinkRegister.add_causal_link(cause_idx, effect_idx)`
currently writes an unsigned CAUSE/EFFECT fact pair. This cell ADDS a `polarity: int` parameter
(`add_causal_link(cause_idx, effect_idx, polarity=+1)`), stored in a new
`self._link_polarity: Dict[Tuple[int,int], int]` side-dict (plain Python, not bound into the FHRR
algebra -- polarity is a scalar sign multiplier applied AFTER retrieval, not encoded via bind/bundle,
since there is nothing to "cleanup" about a +-1 scalar; the FHRR bind/bundle/cleanup_argmax chain is
unchanged and still does the CAUSE/EFFECT existence + index recovery exactly as before).
`query_link_polarity(cause_idx, effect_idx)` reads it back. This is additive-only (no existing
call site's behavior changes; `polarity` defaults to +1, matching prior unsigned behavior exactly) --
verified by a self-test that the EXISTING `read_causal_chain_on_chain_cause_v1` semantics
(query_effect_of / query_cause_of) are byte-identical before/after the extension on a hand-built
2-link case.

### Arms

- **MAJORITY**: constant `"more"` (train's majority label; train is exactly tied 3-way so this is a
  measured, not cherry-picked, first-encountered tie-break). MEASURED@calibration dev accuracy =
  **0.3333**.
- **POLARITY-ECHO** (the sharpened real baseline; implemented exactly as measured above): sign-
  compare(pert_clause polarity, outcome_clause polarity), no_effect when outcome has no polarity
  word, tie-broken to "more" when perturbation has none. MEASURED@calibration dev accuracy =
  **0.3420** overall, **0.4125** multi-hop subset.
- **BoW-OVERLAP** (secondary, expected-weak per scoping drill): predict `no_effect` if the outcome
  clause has ZERO token overlap with the full paragraph text (MEASURED weak recall: 17.75% of true
  distractors, 19.73% false-positive rate on non-distractors -- disclosed as weak going in), else
  predict the train-majority label among {more, less} (i.e. "more", same constant as MAJORITY for the
  non-flagged remainder). Included for completeness/comparability with the MCScript2.0-arc baseline
  family; expected to land close to MAJORITY, not tuned to look weaker than it is.
- **CAUSAL-CHAIN-LOOP** (the mechanism, Section "Mechanism" above).
- **ABLATION-1 (SCRAMBLE)**: identical to CAUSAL-CHAIN-LOOP except the negation-edge-flip assignment
  is computed against a deterministically-permuted step order (`hashlib.sha256(f"wiqa_scramble::
  {seed}::{metadata_para_id}")`-seeded permutation of `range(K)`, applied only to WHICH step's text
  is checked for negation words at each edge position -- anchors and admission gates are UNCHANGED,
  isolating whether the SPECIFIC edge-polarity assignment matters). Averaged over 3 independently-
  seeded draws (SEEDS=[7,17,29]) for stability (Stage-1's `N_SCRAMBLE_DRAWS` precedent, reduced from
  5 given the larger corpus, still enough to avoid a single-draw-lucky read).
- **ABLATION-2 (NO-VALIDATE)**: identical to CAUSAL-CHAIN-LOOP except the admission-gate check on
  `p_idx`/`o_idx` is SKIPPED (always trusts the best-matching anchor regardless of cosine score);
  `p_idx == o_idx` and `pp == 0` abstain conditions are UNCHANGED (structural requirements, not a
  "validate" decision) -- replicates Stage-2A's own admission-gate ablation shape (its `pull_in`
  "admitted" flag is literally part of that cell's VALIDATE check too, not a separate concept).

### Multi-hop subset (evaluation-only oracle, never fed to solver)

`metadata_path_len >= 2`, which per the measured distribution above equals ALL non-distractor
questions (4596/6894 = 66.67%). Disclosed honestly: this does not further separate "hard multi-hop"
from "answerable" within this dataset (no path_len==1 exists) -- the gate still isolates questions
where naive polarity-echo should be weakest (per the measured breakdown: sign_acc=0.4125 there vs
0.2010 on the excluded distractor bucket where it does WORSE than chance).

### Compute architecture

sequential-CPU JUSTIFIED (no GPU benefit: per-item cost is a handful of dict lookups + ~1024-dim
vector sums/dot-products over <=10 paragraph steps; 6894 items measured to complete calibration-scale
probes of similar shape in low tens of seconds this session). Storage: `CausalLinkRegister`
(FHRR complex64, per-item ephemeral instance, `max_event_slots=K<=10`) + a per-item bipolar HD-BoW
step codebook (ephemeral, not persisted across items) + a persistent hashlib-seeded word-vector cache
(grows across items, bounded by real vocabulary size, not a capacity concern at this corpus size).
No bundled multi-item storage across questions (each question is scored independently); no GPU
batching candidate (retrieval is over <=10 candidates per item, not a large codebook).

### Seeds

The scoring arms (MAJORITY, POLARITY-ECHO, BoW-OVERLAP, CAUSAL-CHAIN-LOOP, ABLATION-2) are FULLY
DETERMINISTIC given the fixed lexicons + hashlib-seeded word vectors -- there is no stochastic
component to re-seed. Only ABLATION-1 (SCRAMBLE) has genuine randomness (the permutation draw).
**Seed axis = 3 independent SCRAMBLE draws (SEEDS=[7,17,29])**, matching the pre-reg's ">=3 seeds,
report per-seed" instruction in spirit; the deterministic arms are computed ONCE and reported
identically across the 3 "seed" units for schema uniformity, with this determinism explicitly
disclosed here (not hidden or presented as 3 independent confirmations of a random quantity) --
re-running an identical deterministic computation 3x would be padding, not evidence.

### SCHEMA-VET fields (mandatory checklist)

- `arms_differ_verified`: true (5 distinct output vectors: MAJORITY constant, POLARITY-ECHO,
  BoW-OVERLAP, CAUSAL-CHAIN-LOOP, ABLATION-2 -- hash-compared at smoke gate).
- `final_metrics_atomicity`: `tmp_replace`.
- Outer try/except: `except SystemExit: raise` then `except KeyboardInterrupt: raise` then
  `except Exception` (no bare `except:`, no `except BaseException`).
- `crlb_n/a`: "3-way discrete classification accuracy comparison on a real benchmark; no Gaussian
  noise floor / capacity discriminator threshold to CRLB-check."
- `HP_SCOPE`: `{dev_full: [gate1_lift, gate2_scramble, gate3_novalidate, gate4_multihop]}` -- all 4
  gates apply to the single dev-split evaluation (no bare-baseline/sentinel arm exemption needed).
- `cardinality_ok`: `EXPECTED_N_UNITS = len(SEEDS)=3` (scramble draws; smoke=1).
- Per-unit failure-class instrumentation: any per-item exception during scoring is caught, logged
  with `failure_class` + `question_id`, and the item is scored as `no_effect` with a
  `degraded_scoring: true` flag (never silently dropped or silently continued past without a record)
  -- the cell HALTS if `n_degraded / n_total > 0.02` (2% budget for genuine edge-case text that
  defeats the regex/tokenizer; the 100%-regex-match measurement above means this should be ~0 in
  practice).
- `calibration_check`: `"adaptive_with_discriminator_gate"` -- `GATE_THRESH=0.05` was picked from the
  measured p10 of the non-distractor best-cosine distribution (a distribution-shape decision, not a
  label-peek: the calibration probe used ONLY the cosine scores + the (label-blind) `metadata_
  question_type` field to gauge coverage, never `answer_label`); the discriminator-still-fires
  check is the smoke-gate's arms-must-differ + multi-hop preview (see below).
- `real_code_path`: self-test constructs the REAL `CausalLinkRegister` (with the polarity extension)
  and the REAL `iterative_attractor` call at tiny scale (K=3 hand-built steps), not a synthetic-only
  branch.
- `substrate_signature`: self-test binds `CausalLinkRegister.__init__`'s live signature
  (`d`, `generator`, `max_event_slots`) and `add_causal_link`'s live signature (post-extension,
  `cause_idx`, `effect_idx`, `polarity`) via `inspect.signature`.
- `deterministic_seeding`: true (hashlib-seeded scramble permutation + hashlib-seeded word vectors;
  no built-in `hash()`, no `list(set(...))` ordering -- source-scanned at ship time per PROT-023).
- `progress_logging`: `print_flush_true` (declared even though the full run is expected well under
  30 minutes, per the discipline's "any cell running longer than ~15 minutes" rule of thumb --
  cheap to add, avoids ambiguity if the dev-scale run is slower than expected on the day).
- `cell_chunked`: false (single dev-split pass per scramble-seed unit; `experiments/_seed_checkpoint.
  py` used for the 3 scramble-seed units so a kill mid-run only loses the in-flight seed).
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: true (per-item heartbeat
  every 1000 items during the full-dev pass).

## Pre-registered bands (adopted verbatim from the scoping drill's Section 4; I own the exact
epsilon/margin values used to operationalize them, unchanged from the drill's proposal)

- **HARD-PASS (all four must hold):**
  1. `LOOP_overall - max(MAJORITY, POLARITY-ECHO, BoW-OVERLAP)_overall >= +0.05` (i.e. LOOP overall
     >= ~0.392, given measured POLARITY-ECHO=0.3420 is the current best-of-three).
  2. Scramble collapse: `LOOP_overall - ABLATION1_overall(median of 3 draws) >= +0.05` AND
     `ABLATION1_overall <= best-baseline_overall + 0.02`.
  3. Validate-matters: `ABLATION2_overall < LOOP_overall`.
  4. Multi-hop-specific advantage: `LOOP_multihop - POLARITY-ECHO_multihop >= +0.08` (i.e. LOOP
     multihop >= ~0.4925, given measured POLARITY-ECHO_multihop=0.4125).
- **HARD-FAIL:** no lift over the best baseline, OR scramble does not collapse (ABLATION-1 gain
  survives scrambling), OR the multi-hop subset shows no differential advantage over POLARITY-ECHO.
- **MIDDLE_BAND:** partial lift (+0.02 to +0.05 aggregate) with partial scramble-collapse -> narrow
  the flagship claim to the multi-hop subset specifically, per the scoping drill's designed exit.

## Smoke gate (before full dev run)

`--self-test`: tiny 3-step hand-built causal chain (A causes B causes C, one negating word planted on
C) + a hand-built 2-item WIQA-shaped question pair (one where propagation should give "more", one
"less") -- asserts the CAUSAL-CHAIN-LOOP mechanism recovers both by hand-trace, plus the
`CausalLinkRegister` extension's backward-compatibility check (unsigned behavior unchanged) plus
`substrate_signature`/`real_code_path` preflight.

`--smoke`: first 300 dev items (deterministically sorted by `metadata_question_id`, stratified by
construction of the dataset's own ordering -- not cherry-picked). Verifies: (a) all 5 arms produce
non-identical outputs (`arms_differ_verified`); (b) `baseline_in_band` (POLARITY-ECHO smoke accuracy
between 0.05 and 0.95, expected ~0.34 per the full-dev measurement above, i.e. this IS the
discriminator-preview arm per DISCRIMINATOR-MUST-SURVIVE-SCALE option C, run at the SAME regime as
FULL -- same lexicons, same GATE_THRESH, same D=1024, just fewer items); (c) CAUSAL-CHAIN-LOOP's
abstain rate is < 100% (mechanism actually fires, not vacuous). Reject full dispatch if the smoke
shows CAUSAL-CHAIN-LOOP abstaining on >95% of items (mechanism not firing) or if any two arms are
bit-identical.

## Report contract

Per-arm accuracy (overall dev + multi-hop subset), scramble delta (median + range over 3 draws),
no-validate delta, data-pull/schema status, concrete worked examples where CAUSAL-CHAIN-LOOP's
propagation differs from POLARITY-ECHO's comparison (both correct-vs-wrong directions), and the
honest content-ceiling / edge-sparsity findings from this pre-reg surfaced in the verdict_msg (not
buried) regardless of which way the verdict lands.
