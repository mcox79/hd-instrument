# Pre-reg: MAVEN-ERE convergence-gated causal relation classification (decisive minimal prototype)

Filed by: exp_dev. Trigger: Director spawn prompt (first experiment on MAVEN-ERE after its
trap-check HARD-PASSed; design basis =
`notes/research_next_benchmark_after_propara_trap_check_2026-08-10.md` Section 3). Branch
`dataprep/mcguffey-graded-corpus`. NOT a full pipeline -- a design-gate smoke; STOP after this
run, no auto-scale.

## Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring)

`bash tools/substrate_query.sh "convergence gated coincidence detection relation type
classification causal precondition MAVEN-ERE"` -- top cosine=0.3955 ("Composition classification",
old preregs, unrelated compositional-binding topic, not this mechanism). Second hit cosine=0.3916:
`notes/design_crutch_discriminative_selection_multicue_convergence_2026-08-10.md` -- SAME mechanism
CLASS (multi-cue convergence discriminator, "scramble must collapse" control) applied to a
DIFFERENT benchmark (SocialIQA / CSKG spreading-activation discrimination), not MAVEN-ERE. That
build's reuse target (`arc_retrieval_multicue_ppr_discriminative_v1`) landed RETRIEVAL_MIDDLE_BAND
twice on ARC/WorldTree with the shuffled-control NOT fully collapsing -- a genuine cautionary data
point carried into this design: the bar for "scramble cleanly collapses" is empirically hard to
clear for convergence-gated discriminators, so this pre-reg treats a clean collapse as the
load-bearing, not-to-be-fudged gate (see HARD-FAIL condition 2 below). Third/fourth hits
(cosine 0.3867 confidence-permanence, 0.3857 old Store-corruption incident) are topically
unrelated. Verdict: genuinely fresh ground for MAVEN-ERE specifically; the mechanism SHAPE (not
this benchmark) has one directly-relevant prior attempt, noted and folded into the bands below.

## What (adapted from the validated ProPara mechanism)

Port the coincidence-detection GATE validated on ProPara process-selection
(`experiments/exp_propara_bridging_frame_activation_v1.py::_process_convergent`, commit
459098f52 -- boolean gate: donate only if >=2 distinct roles are each filled by >=2 distinct
participants, never an additive score) from process-type candidates to causal-relation-type
candidates: for an ordered event-mention pair (m1, m2), predict a causal relation only if
>= MIN_CONVERGENT_CUES independent textual/structural cues converge on it.

## Data slice (bounded, resumable-not-needed given wall time -- see Compute architecture)

- DEV slice: first 100 dev docs from `data/benchmark_trap_check/maven_ere/valid.jsonl`, sorted
  deterministically by `doc["id"]` (string sort, never `list(set())`/`hash()`-derived order per
  PROT-023/F.5). MEASURED@this build: 93,308 candidate pairs, 775 CAUSE + 1769 PRECONDITION gold
  positives (2544 total) -- well-powered for a stable F1 estimate.
- TRAIN slice (priors only, NEVER touches dev gold): first 400 train docs from `train.jsonl`,
  same deterministic sort. Used for (a) the majority/adjacent-sentence/bag-of-event-types
  baselines refit on THIS slice for apples-to-apples comparison (contract requirement: baselines
  "on the SAME slice"), (b) the type-pair positive-rate table for cue 4, (c) the fallback label
  when the gate fires without a connective (TRAIN-measured: PRECONDITION is the majority of the
  two positive classes, 6739 vs 2088 CAUSE at this slice size).

## Cues (4, each a boolean per ordered mention pair; NONE ever reads `doc["causal_relations"]`)

1. **connective**: a causal-connective-class regex match (CAUSE_WORDS or PRECOND_WORDS, two small
   ASCII fixed lists) inside the sentence span from `min(sent_id)` to `max(sent_id)` of (m1, m2),
   gated to sentence distance <=1 (SAME window as the already-measured
   `adjacent_sentence_heuristic` baseline, for direct comparability -- not widened, so any gain is
   attributable to the ADDED cues, not a wider window).
2. **order**: `(m1.sent_id, m1.offset) <= (m2.sent_id, m2.offset)` (forward narrative order).
   MEASURED@this build (TRAIN, first 300 train docs, throwaway diagnostic, not persisted):
   forward-order holds for 77.0% of gold CAUSE pairs (n=1671) and 81.0% of gold PRECONDITION
   pairs (n=4912) -- a real corpus-measured majority pattern (chance = 50%), not assumed.
3. **argument_share**: shared non-stopword NOUN/PROPN token (lowercased) between a +/-4-token
   window around m1's trigger offset and a +/-4-token window around m2's trigger offset, POS-tagged
   via the OWNED glass-box `hdlab.pos_tagger.PosTagger` (persisted UD-EWT averaged-perceptron
   model at `data/frontend_assets/pos_tagger_ud_ewt_upos.json`, loaded not retrained), tagged
   DIRECTLY on MAVEN's own pre-tokenized sentence tokens. MEASURED@this build (disk-verified,
   throwaway probe): MAVEN event triggers are frequently NOMINAL ("attack", "massacre" tag NOUN,
   not VERB), so `hdlab.candidate_generator.candidates_from_parse`'s verb-anchored
   extraction returns an EMPTY candidate set on such sentences -- the full CandidateGenerator
   (POS+arc-parse verb-argument pipeline) is therefore NOT reused here; a POS-tag nominal-window
   proxy is the practical substitute for this minimal prototype (still the real persisted tagger,
   no new model, no LLM). Declared honestly as a scope simplification, not silently substituted.
4. **type_compat**: TRAIN-slice-derived positive-rate for the ordered `(type_A, type_B)` event-type
   pair (min support 3 candidate pairs, else falls back to the TRAIN global positive rate) exceeds
   `1.5x` the TRAIN global positive rate. Adaptive threshold (not hand-tuned per pair), computed
   once from TRAIN, applied identically to every dev pair.

## Gate + label decision

- REAL arm: predict a relation iff >= 2 of the 4 cues fire (`MIN_CONVERGENT_CUES=2`, ProPara's
  validated >=2-distinct-signal pattern). ABLATION arm: >= 1 (degenerate OR-gate; isolates whether
  the >=2 GATE specifically, not just "having cues at all", is load-bearing).
- When the gate fires: CAUSE if a CAUSE-class connective matched; elif a PRECONDITION-class
  connective matched -> PRECONDITION; else -> TRAIN-slice majority label for this exact
  `(type_A, type_B)` pair among {CAUSE, PRECONDITION} (fallback = TRAIN global majority =
  PRECONDITION). This is a glass-box, cue-derived decision -- never reads dev gold.

## Controls (load-bearing; ALL run)

- **SCRAMBLE**: within each doc, a deterministic (hashlib-seeded, PROT-023/F.5-compliant) non-
  identity permutation of which mention's textual evidence (sent_id/offset/trigger/type) is used
  when computing cues FOR a given mention_id -- gold labels stay keyed to the REAL mention_id
  pairs. All 4 cues are computed against the WRONG (permuted) textual identity. If the win
  survives this, it does not depend on genuine text-content alignment. Degenerate-permutation
  assert (non-identity; docs with <2 mentions exempted, no pairs exist there).
- **ABLATION**: MIN_CONVERGENT_CUES=1 (see above) -- isolates the >=2 gate's precision
  contribution specifically.
- **NO-LEAK by construction**: cue-computation functions take ONLY doc-structural fields
  (`events`, `tokens`, `sentences`) -- `causal_relations` is passed exclusively to the evaluator
  (`official_gold_labels`), never to any cue/gate/predict function. Enforced by code structure
  (grep-checkable: no cue function has `causal_relations` in its parameter list).
- **Baselines recomputed on the SAME 100-doc dev slice** (not inherited from the full-dev-set
  `maven_ere_results.json` numbers) via the EXISTING, already-measured trap-check functions
  (`tools/benchmark_trap_check/maven_ere_trap_check.py::predict_majority` /
  `predict_adjacent_sentence_heuristic` / `predict_bag_of_event_types`, imported not
  reimplemented) refit on the 400-doc TRAIN slice.

## Metric

Official positive-only micro-F1 (causal task), via
`tools/benchmark_trap_check/maven_ere_official_eval.py::official_prf` (faithful port of the
THU-KEG/MAVEN-ERE `evaluate.py`), imported not reimplemented. Also report macro-F1-all-labels +
accuracy for context (same convention as the trap-check).

## Falsifiable bands (declared BEFORE running; `best_base = max(majority_f1, adjacent_f1, bag_f1)`
on the 100-doc slice)

- **HARD-PASS**: `real_f1 >= max(1.0, 2.0*best_base)` (meaningful beat: an absolute F1-point floor
  if baselines round to ~0, else a 2x margin) AND `scramble_f1 <= 0.5*real_f1` (scramble collapses
  by >=50%) AND (`ablation_f1 <= 0.8*real_f1` OR `ablation_precision < 0.5*real_precision`) (the
  >=2 gate is load-bearing, not just "having cues") AND `31.96 - real_f1 >= 15` (real headroom to
  SOTA survives -- this stays an honest first-experiment prototype, not a near-SOTA claim).
- **HARD-FAIL**: `real_f1 < max(1.0, 1.3*best_base)` (not a meaningful beat) OR
  `scramble_f1 > 0.8*real_f1` (scramble does NOT collapse -> the mechanism is a density artifact,
  not genuine convergent evidence -- exactly the failure mode flagged as a real risk by the
  cosine=0.3916 prior-work hit above) OR `ablation_f1 >= real_f1` (the gate isn't load-bearing).
- **MIDDLE_BAND**: neither -- a real but partial win; narrow the claim (e.g., to the subset where
  the adjacent-sentence baseline structurally cannot fire, i.e. sentence distance > 1) rather than
  claim full transfer.

## Cell-template mandates (applicable subset; this is a single bounded local pass, not a
GPU/sweep/multi-seed dispatch -- see Compute architecture)

- `arms_differ_verified`: hash-check REAL vs ABLATION vs SCRAMBLE prediction vectors (must not be
  bit-identical) at smoke gate, per META_RULE_AF.
- `final_metrics_atomicity`: `tmp_replace` (write `metrics.json.tmp`, `os.replace` at the end).
- `except SystemExit: raise` / `except KeyboardInterrupt: raise` BEFORE `except Exception` (never
  `except:` / `except BaseException:`); crash diagnostic writes `CELL_CRASHED` metrics on any
  unhandled `Exception`.
- `crlb_n/a`: "official positive-only micro-F1 comparison over a fixed real corpus slice (MAVEN-ERE
  dev), no closed-form noise floor applies; feasibility is instead the DEV-measured baseline
  distances (best_base) declared above."
- `cardinality_ok`: n/a in the sweep-axis sense (no swept parameter axis) -- EXPECTED_ARMS = 3
  (real, ablation, scramble) + 3 baselines, all computed in one deterministic pass over the fixed
  100-doc slice; the cardinality check here is `n_candidate_pairs == 93308` exactly (verified at
  runtime, HARD_FAIL_CARDINALITY_BREACH if not).
- `calibration_check`: `adaptive_with_discriminator_gate` -- the type_compat threshold (1.5x TRAIN
  global rate) is adaptive (computed from TRAIN, not hand-tuned to hit a target dev number) and
  the discriminator-fires check is `n_pairs_gated_positive_real > 0` at smoke (else STOP, no
  dispatch of the interpretation).
- `real_code_path_exercised`: self-test constructs the REAL `PosTagger.load(...)` object at tiny
  scale (a 2-sentence synthetic doc) and asserts the argument_share cue actually consults its
  `.tag()` output, not a synthetic-only branch.
- `deterministic_seeding: true` -- scramble permutation uses a local `hashlib.sha256`-seeded
  `_deterministic_perm` (never Python `hash()` / `list(set())` ordering), per PROT-023/F.5.
- `progress_logging`: n/a (`timeout_s < 1800`; wall time is estimated in minutes, not exempted
  loudly but noted -- see Compute architecture).
- `checkpoint_exempt: true` -- reason: single bounded local pass over a fixed 100-doc slice with
  no seed/arm remote-dispatch loop (estimated wall time low minutes); `tools/exp_checkpoint.py`
  per-unit resumability is disproportionate to this run's risk profile (compute-proportionality).

## Compute architecture

(a) sequential-CPU, INLINE-LOCAL, run to foreground completion (NOT dispatched to any queue).
Justification: pure Python dict/set operations + a small structured-perceptron POS-tag call per
SENTENCE (cached once per doc, not per pair) -- no GPU-batchable matmul, no torch tensors. Runtime
estimate: 100 docs x ~13 sentences/doc POS-tagging (sub-ms each per the disk-measured load/parse
timing above) + 93,308 pairs x O(1) cue lookups (dict/set ops) -- expected wall time low tens of
seconds to ~2 minutes. Matches the compute-proportionality rule (cheapest decisive method for a
gate/diagnostic question) and the INLINE-LOCAL mandate (light compute -> foreground-to-completion,
not backgrounded, not over-routed to remote/queue infra).

## HP_SCOPE

`{real: [beats_baseline, scramble_collapses, ablation_collapses, headroom_survives,
no_leak, arms_differ], ablation: [], scramble: [], baselines: []}` -- only the REAL arm inherits
the HARD-PASS gates; ABLATION/SCRAMBLE/baselines are controls/references, not claimants.

## Guardrails

Branch `dataprep/mcguffey-graded-corpus` (not main/origin). No origin push. Targeted commits only
(never `git add -A`). self-test PASS -> this decisive smoke -> STOP and report; do NOT auto-scale
to the full 613,706-pair space or dispatch remote without director steer.
