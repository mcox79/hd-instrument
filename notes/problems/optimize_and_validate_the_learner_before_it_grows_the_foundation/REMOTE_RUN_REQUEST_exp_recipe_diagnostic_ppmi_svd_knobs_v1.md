---
cell: experiments/exp_recipe_diagnostic_ppmi_svd_knobs_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 5400
results_path: data/exp_recipe_diagnostic_ppmi_svd_knobs_v1/metrics.json
self_test: green
smoke: green
question: Our best learned SimLex is ~0.27 at 15M tokens, which the research drill says is BELOW the ~0.37-0.44 pure-distributional literature floor. Is this a FIXABLE RECIPE gap (untested PPMI/SVD tuning knobs) or are we simply DATA-LIMITED at 15M? Diagnostic, no new mechanism, no oracle.
gate: DIAGNOSTIC (report the MAP, not a single pass/fail). Answer TWO questions: (1) does any single untested knob -- shifted-PPMI (subtract log k), context-distribution alpha (0.75 vs 1.0), SVD eigenvalue-weighting U*S^p (p in {0,0.5,1}), or frequent-word subsampling -- lift SimLex CI-separated above BASE (the measured recipe: alpha=0.75, svd_p=0.5, k=300, plain PPMI), and how big is the fixable gap? (2) Where does the GENSIM word2vec (SGNS) reference land trained on the SAME 15M tokens -- if ~0.27-0.32 (near ours) the gap is DATA-SCALE (not a bug); if ~0.40+ the gap is a RECIPE we are missing. Deliver a one-sentence diagnosis: "recipe-fixable (+X on knob Y)" vs "data-limited (matched-15M reference is ~Z)".
kb_referents:
  - data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl
  - data/exp_structured_context_learner_v1/parsed_simplewiki_150000tok.jsonl
  - data/encoder_eval_benchmarks/simlex999.txt
  - data/encoder_eval_benchmarks/simverb3500.txt
  - data/encoder_eval_benchmarks/wordsim353_combined.csv
  - experiments/exp_learn_from_reading_strong_arm_v1.py
  - experiments/exp_structured_context_learner_v1.py
  - experiments/_seed_checkpoint.py
  - tools/exp_checkpoint.py
---
# REMOTE_RUN_REQUEST -- exp_recipe_diagnostic_ppmi_svd_knobs_v1 (the "free headroom" diagnostic: recipe-gap vs data-limited)

Solver-dropped request; the strategy/orchestrator lane runs the fulfiller. This is a DIAGNOSTIC surfaced by the word-meaning research drill (we sit below the text-only distributional floor -- diagnose before adding any mechanism).

## Arms (all on the dependency-typed context matrix at 15M; ONE knob varied at a time; scored SimLex/SimVerb/WordSim)
- BASE [FLOOR] = the MEASURED recipe (alpha=0.75, svd_p=0.5, k=300, plain PPMI shift=1) -- reproduces ~0.27 SimLex. (Agent corrected the config from disk: k=300/p=0.5 is the real base, NOT k=500.)
- SHIFT = shifted-PPMI (subtract log k for k in {1,5,15,50}) -- the Levy-Goldberg shift knob (UNTESTED here).
- ALPHA = context-distribution smoothing (0.75 vs 1.0) before PPMI.
- EIGENVALUE p = SVD read-out U*S^p for p in {0,0.5,1} (p=0.5 is the known SimLex-optimal symmetric weighting).
- SUBSAMPLE = word2vec-style frequent-word subsampling before building the matrix.
- GENSIM_REF = gensim Word2Vec SGNS (workers=1 for reproducibility) trained on the SAME 15M token stream -- the KEY matched-data reference (does a standard off-the-shelf model reach ~0.27 or ~0.40 at OUR data scale?).

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn + gensim 4.4.0 -- confirmed installed, no torch dep). Loads the 15M
PRE-PARSED cache; NEVER parses (fails loud if missing). bare == FULL. --self-test GREEN (SPPMI-shift +
subsampling keep-prob formulas hand-verified against closed form; arms-must-differ both ways; checkpoint
round-trip). --smoke GREEN (150k, DATA_LIMITED_NO_RECIPE_GAP -- machinery-only at that scale; the claim is
the 15M run). Two REAL bugs fixed during build: np.savez tmp-path corruption; and the reused build_vocab's
PYTHONHASHSEED force-word ordering (fixed at root via sorted() + a vocab-fingerprint cache-validation that
REJECTS a mismatch) -- verified bit-identical across fresh processes + a cache resume. Canonical line-start
KB_REFERENTs; _seed_checkpoint + exp_checkpoint (PROT-021); incremental per-arm metrics; scored_population.
timeout 5400 (~25-45 min realistic: the 15M matrix build + subsample rebuild + gensim single-threaded on ~75M
word-instances).

## Results
data/exp_recipe_diagnostic_ppmi_svd_knobs_v1/metrics.json (per-knob SimLex/SimVerb/WordSim + paired deltas vs
BASE + the gensim reference + the one-sentence diagnosis), synced back after the run. Standing infra gotchas:
hd_metrics_sync DISABLED (pull via orchestrator); runner may write a double-prefixed data/exp_exp_<name>/ path
(SH-4). Strategy does NOT integrate -- WIP until owner_verdict: DONE.
