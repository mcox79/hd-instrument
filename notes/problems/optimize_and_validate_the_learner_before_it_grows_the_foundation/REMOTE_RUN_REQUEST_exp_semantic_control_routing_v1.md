---
cell: experiments/exp_semantic_control_routing_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 3600
results_path: data/exp_semantic_control_routing_v1/metrics.json
self_test: green
smoke: green
question: Does DYNAMIC semantic control (a per-item/per-task multiplicative gain over the meaning channels, IFG-style) beat the best FIXED reliability-weighted blend on a MIXED similarity+relatedness+verb eval -- i.e. does routing the right system per query beat one static blend (which the disk shows helps relatedness but hurts similarity)?
gate: PASS iff SEM_CONTROL (TASKSET top-down task-set gain, and/or CONFLICT gold-blind gate reusing hdlab.semantic_control) beats FIXED_BLEND CI-separated on the POOLED eval (paired Delta-rho lower CI > 0), AND SHUFFLED_GATE (task tags permuted) does NOT beat FIXED_BLEND CI-separated. Report per-task rho (expect control to pick DEP/GRND for SIM, WIN for REL, SELP for VERB). RIGOROUS_NEGATIVE (a PASS) if dynamic control does not beat the fixed blend once floors are recomputed -- the fixed blend is then the right architecture.
kb_referents:
  - data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl
  - data/encoder_eval_benchmarks/simlex999.txt
  - data/encoder_eval_benchmarks/simverb3500.txt
  - data/encoder_eval_benchmarks/wordsim353_combined.csv
  - data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv
  - data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt
---
# REMOTE_RUN_REQUEST -- exp_semantic_control_routing_v1 (fidelity phase, DRILL #1: IFG semantic control)

Solver-dropped request; the 5-min watcher fulfils it (validates, writes prereg, ships code+data, queues CPU).

## Brain claim (PINNED)
The IFG / semantic-control network (Lambon Ralph; Jefferies) TASK-GATES which meaning system dominates per
query -- a controlled multiplicative gain, not a fixed blend. On disk a fixed blend helps relatedness but
hurts similarity, so the two systems need dynamic control. Test whether per-item control beats a fixed blend.

## Channels + arms (all remote-available; PPMI-SVD k=500 for DEP)
DEP (dependency-typed, similarity) / WIN (+/-2 window, relatedness) / GRND (grounded_vector, features) /
SELP (verb selectional preference). z-scored per channel; fit on split A, score on B. Eval = POOL of
SimLex(SIM) + WordSim(REL) + SimVerb(VERB), each item task-tagged.
- FIXED_BLEND [FLOOR]: one global reliability-weight vector for all items.
- SEM_CONTROL_TASKSET [top-down]: per-task reliability weights, applied by the item's true task tag.
- SEM_CONTROL_CONFLICT [gold-blind]: per-item gate reusing hdlab.semantic_control.conflict/suppression (no task label).
- SHUFFLED_GATE [INFO-FREE TWIN]: TASKSET with task tags permuted (fixed-seed rng) -> random gating. MUST LOSE.
- plus each channel alone (DEP/WIN/GRND/SELP).

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn; grounded_similarity pulls torch for CPU tensors -- same precedent as
exp_exemplar_selpref_v1 already on remote_cpu_queue). Loads the 15M PRE-PARSED cache; NEVER parses (no
module-level spaCy; parse_and_cache never called). bare == FULL. --self-test + --smoke GREEN. metrics.json
written INCREMENTALLY (partial: true / arms_done) so a late crash keeps completed arms. 150k-smoke reads
RIGOROUS_NEGATIVE because the channels are data-starved there (GRND dominates the fit) -- the fair test is
this 15M run where DEP/WIN/SELP carry task-differentiated signal.

## Results
data/exp_semantic_control_routing_v1/metrics.json (pooled + per-task rho, paired deltas + CIs, gate booleans),
synced back ~20 min. Strategy does NOT integrate -- WIP until owner_verdict: DONE.
