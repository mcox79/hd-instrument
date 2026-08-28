---
cell: experiments/exp_dependency_path_context_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 7200
results_path: data/exp_dependency_path_context_v1/metrics.json
self_test: green
smoke: green
question: Does adding length-2 dependency PATH contexts (grandparent + coordinate-sibling; Lin 1998 / Pado-Lapata 2007) to the immediate (deprel, filler) context DEEPEN the proven dependency win on the paradigmatic-similarity axis (SimLex/SimVerb)?
gate: PASS iff DEP_PATH beats DEP1 (immediate-only) CI-separated on SimLex and/or SimVerb (paired Delta-rho lower CI > 0) AND beats PATH_SHUFFLE (path deprel-labels shuffled across edges) CI-separated -- so the CORRECT path grammar carries any gain, not just more/sparser columns. WordSim may not move. RIGOROUS_NEGATIVE (a PASS) if paths add nothing CI-sep once floors are recomputed (the immediate context already saturates the paradigmatic signal).
kb_referents:
  - data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl
  - data/exp_learner_safety_gate_v1/parsed_simplewiki_150000tok_posfixed.jsonl
  - data/encoder_eval_benchmarks/simlex999.txt
  - data/encoder_eval_benchmarks/simverb3500.txt
  - data/encoder_eval_benchmarks/wordsim353_combined.csv
---
# REMOTE_RUN_REQUEST -- exp_dependency_path_context_v1 (fidelity phase, DRILL #2: dependency paths / 2nd-order context)

Solver-dropped request; the 5-min watcher fulfils it (validates, writes prereg, ships code+data, queues CPU).

## Brain claim (PINNED)
Words are similar when they occur in SIMILAR grammatical environments, not only identical immediate ones
(Lin 1998; Pado & Lapata 2007). So context should generalise to short dependency PATHS (grandparent,
coordinate siblings), deepening the proven win (dependency-typed context beats the window baseline on
SimLex/SimVerb).

## Arms (word x context-feature matrix; PPMI-SVD k=500; ONE variable = the columns)
- DEP1 [FLOOR] = immediate (direction+deprel, filler) typed context (the current proven arm).
- DEP_PATH [treatment] = DEP1 + length-2 PATH columns: grandparent (word->head->head-of-head, deprel-path
  keyed) + sibling (word->shared-head<-other-dependent), inverse-path-length weighted.
- WIN2 [context-shape baseline] = +/-2 window PPMI-SVD.
- PATH_SHUFFLE [INFO-FREE TWIN] = DEP_PATH with the PATH deprel-path labels shuffled ACROSS edges
  (fillers + counts + immediate cols preserved; path grammar destroyed). MUST LOSE.
Score SimLex + SimVerb (primary) + WordSim; paired Delta-rho on common coverage; rho + ci_half + null_p95.
At 150k smoke DEP1=7630 / DEP_PATH=17697 / WIN2=6344 cols (paths ~2x the column space -> needs real data).

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn; grounded not used here). Loads the 15M PRE-PARSED cache; NEVER parses
(no spaCy import; parse_and_cache never called). bare == FULL. --self-test + --smoke GREEN. metrics.json
written INCREMENTALLY (partial: true / arms_done) so a late crash keeps completed arms. timeout 7200 (the
path matrix + PATH_SHUFFLE add two large SVDs beyond the structured cell's ~673s build+score).

## Results
data/exp_dependency_path_context_v1/metrics.json (per-gold rho, paired deltas + CIs, gate booleans, col
counts), synced back ~20 min. Strategy does NOT integrate -- WIP until owner_verdict: DONE.
