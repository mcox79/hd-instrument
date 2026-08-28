---
cell: experiments/exp_binder_attr_prediction_grounding_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 7200
results_path: data/exp_binder_attr_prediction_grounding_v1/metrics.json
self_test: green
smoke: green
question: Does PREDICTING Binder's 65 brain-derived semantic attributes across the WHOLE vocabulary (Ridge fit on the ~434 surveyed Binder words from Lancaster sensorimotor + Brysbaert concreteness + the learned DEP_TYPED distributional embedding) turn the narrow 434-word Binder grounding win (exp_grounding_supply_v1 HARD_PASS) into a BROAD grounded channel that still beats text-alone on the non-WordNet MEN gold with the crossover holding -- i.e. is the neurobiological attribute space a real property of concepts that generalises past the survey, not an accident of the 434 sampled words?
gate: PASS iff (a) the predictor is VALID -- held-out (out-of-fold) mean-per-attribute rho CI-separated above the SHUFFLED-target twin's own OOF rho (paired bootstrap over words); AND (b) GRND_BROAD or FUSED beats BOTH the thin LANC12 grounded floor AND TEXT-alone CI-separated (paired Delta-rho) on MEN; AND (c) CROSSOVER -- the grounding benefit is LARGER on MEN (associative) than on SimLex (WordNet-ish); AND (d) sanity -- BINDER_PRED beats its INFO-FREE BINDER_PRED_SHUF twin CI-separated on MEN and RANDOM is the lowest arm. RIGOROUS_NEGATIVE (a PASS) if the predictor carries no real signal (gate a fails) OR the valid predictor adds nothing over thin Lancaster once predictor error is accounted for (gate b fails despite a passing) -- either says the broad predicted grounding does not earn its keep and why.
kb_referents:
  - data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl
  - data/exp_learner_safety_gate_v1/parsed_simplewiki_150000tok_posfixed.jsonl
  - data/men/men_try.txt
  - data/corpora/binder/binder2016_ratings.csv
  - data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv
  - data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt
  - data/encoder_eval_benchmarks/simlex999.txt
  - data/encoder_eval_benchmarks/wordsim353_combined.csv
---
# REMOTE_RUN_REQUEST -- exp_binder_attr_prediction_grounding_v1 (fidelity phase 3, DRILL #5: BROAD brain-based grounding via Binder-attribute prediction)

Solver-dropped request; the 5-min watcher fulfils it (validates, writes prereg, ships code+data, queues CPU).

## Brain claim (PINNED)
Word meaning is organised along a modest set of neurobiologically-motivated experiential dimensions,
each traceable to a specific cortical system (Binder, Desai, Graves & Conant 2009 "Where Is the
Semantic System?"; Binder et al. 2016 "Toward a Brain-Based Componential Semantic Representation").
Those 65 attributes were surveyed on only ~434 words -- a narrow island. If the dimensions are REAL
properties of concepts (not survey accidents) they generalise: predict them for the whole vocabulary
from correlated surface features (Fernandino et al. 2022; Utsumi 2020 predict brain-derived semantic
norms from distributional vectors). This drill scales the proven-but-narrow grounding win into a
broad channel and tests whether it survives.

## Arms (word x feature-vector cosine unless noted; scored MEN primary + SimLex crossover + WordSim fit-only)
STAGE 1 predictor: X = concat(Lancaster-11+Brysbaert z-scored, DEP_TYPED SVD embedding); Y = raw
Binder-65; Ridge, alpha by out-of-fold CV; INFO-FREE TWIN = identical pipeline with Y rows permuted.
STAGE 2 similarity arms (ARM_ORDER, 8 checkpoint units):
- TEXT [context-shape baseline] = learned DEP_TYPED distributional cosine (the same SVD vectors the predictor's X used).
- LANC12 [FLOOR] = the current thin grounded supply (Lancaster-11 + Brysbaert concreteness).
- BINDER_PRED [treatment] = PREDICTED Binder-65 over the broad vocab-wide population.
- GRND_BROAD [treatment] = LANC12(+)BINDER_PRED per-pair, LANC12 fallback where BINDER_PRED undefined.
- FUSED [treatment] = reliability-weighted GRND_BROAD(+)TEXT (weights fit on WordSim, never a gate gold).
- BINDER_PRED_SHUF [INFO-FREE TWIN] = Binder predicted from the SHUFFLED-target model. MUST LOSE.
- RANDOM [FLOOR] = matched-dim random vectors. MUST LOSE on everything.
Score via paired_delta rho + ci_half + null_p95 + coverage on common-coverage intersections; no number crosses populations.

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn ONLY -- NO torch anywhere; not overnight_queue). Loads the 15M
PRE-PARSED cache; NEVER parses (no spaCy token appears in the file; parse_and_cache never called; if
the parse cache is missing it FAILS LOUD via SystemExit, it never parses). All reuse
(exp_structured_context_learner_v1 / exp_learn_from_reading_strong_arm_v1 / exp_grounding_supply_v1)
is READ-ONLY import; spaCy in those siblings lives only inside parse_and_cache, never on this path.
bare == FULL (line 790: `smoke = bool(args.smoke) or (args.mode == "smoke")`; the remote runner passes
no --mode). --self-test + --smoke GREEN. metrics.json written INCREMENTALLY per-unit (partial: true /
arms_done; atomic os.replace; mode-keyed _ckpt_full dir; TEXT persists its SVD npz, PREDICTOR_CV
persists its CV report) so a late crash/timeout keeps every completed arm. timeout 7200 (the 15M
DEP_TYPED SVD build ~673s + Ridge alpha-grid CV + bootstrap CI + 8 arms scored over 3 golds).

## Known limitation (fold into the verdict, do not re-litigate)
The exact rho values drift ~0.001-0.1 run-to-run because build_vocab's force-word-set iteration is
PYTHONHASHSEED-salted in the REUSED grounding machinery (documented in exp_grounding_supply_v1's own
_index_words docstring -- pre-existing, not introduced here). The GATE pass/fail pattern is stable
across runs; read the verdict pattern + CI-separation, not the last digit of any single rho.

## Results
data/exp_binder_attr_prediction_grounding_v1/metrics.json (per-gold rho, paired deltas + CIs, gate
booleans a-d, predictor OOF quality + chosen alpha, coverage, col counts), synced back ~20 min.
NOTE the standing infra gotchas: hd_metrics_sync is DISABLED (pull manually via the orchestrator) and
the runner writes a double-prefixed data/exp_exp_<name>/ path (SH-4). Strategy does NOT integrate --
WIP until owner_verdict: DONE.
