---
cell: experiments/exp_multiproto_sense_learner_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 5400
results_path: data/exp_multiproto_sense_learner_v1/metrics.json
self_test: green
smoke: green
question: Is the unsupervised SIMILARITY ceiling (learned dependency channel ~0.29 SimLex vs ~0.67 human) partly a SENSE-AVERAGING artifact of collapsing a word's occurrences into ONE mean vector? Does a brain-faithful CONTEXT-MODULATED representation -- keep the word's occurrence-context distribution (token cloud), let senses EMERGE, score similarity over the cloud -- beat the single mean vector, MOST on polysemous words? (Reframed per the brain-foundational verification: the brain keeps one graded representation continuously modulated by context, NOT discrete pre-stored senses; discrete k-means is kept only as a labelled engineering approximation.)
gate: PASS iff a context-modulated token-cloud readout beats SINGLE_VEC CI-separated (paired Delta-rho) on SimLex and/or SimVerb, AND the gain CONCENTRATES on high-polysemy words (polysemy x arm interaction via the WordNet sense-count stratification), AND its budget-matched info-free twin (RANDOM_CLOUD, same per-word token budget from the global pool) does NOT beat SINGLE_VEC. TWO readouts tested so a negative is CONCLUSIVE: TOKEN_CLOUD_AVGSIM (expected cosine, washes toward the mean) and TOKEN_CLOUD_MAXSIM (best-matching-sense pair, exposes sense-selectivity) -- each with its own-readout twin. RIGOROUS_NEGATIVE (a FULL PASS): if NEITHER readout beats the mean vector even on polysemes, sense-averaging is NOT the ceiling's cause -- report where the ceiling actually lives (data / dimension / grounding), not an excuse. The discrete k-means MULTIPROTO arms are SECONDARY / OUR-INVENTION and do not decide the verdict.
kb_referents:
  - data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl
  - data/exp_structured_context_learner_v1/parsed_simplewiki_150000tok.jsonl
  - data/encoder_eval_benchmarks/simlex999.txt
  - data/encoder_eval_benchmarks/simverb3500.txt
  - data/encoder_eval_benchmarks/wordsim353_combined.csv
  - data/exp_multiproto_sense_learner_v1/wordnet_polysemy_static.json
---
# REMOTE_RUN_REQUEST -- exp_multiproto_sense_learner_v1 (fidelity phase 3, DRILL #8: context-modulation vs sense-averaging, targets the similarity ceiling)

Solver-dropped request; the strategy/orchestrator lane runs the fulfiller (validates, writes prereg, ships code+data, queues CPU).

## Brain claim (PINNED at computational level; verified against literature 2026-08-28)
Word meaning is context-SELECTIVE: the brain keeps ONE graded representation that context continuously
MODULATES; senses EMERGE in processing, they are not discrete pre-stored entries (Li 2021 "Word Senses as
Clusters of Meaning Modulations"; Lambon Ralph controlled-semantic-cognition / ATL graded hub; Yee &
Thompson-Schill 2016). A single static vector per word AVERAGES incompatible senses, which the brain does
NOT do -- this sense-averaging may be part of why the learned similarity channel tops out far below human.
Discrete sense-clustering is brain-faithful ONLY at the homonymy pole and is kept here only as a labelled
engineering approximation. This EXTENDS drill #6's own finding (exemplar pooling beat mean-centroid) up to
the type representation.

## Arms (one variable = the word representation / readout; hold corpus/vocab/PPMI-SVD/scorer constant, reuse exp_structured_context_learner_v1 machinery READ-ONLY)
- SINGLE_VEC [FLOOR] = the current one-mean-vector-per-word dependency channel (the BAR1 winner; the sense-averaging baseline).
- TOKEN_CLOUD_AVGSIM [treatment, brain-faithful] = the word's occurrence-context vector DISTRIBUTION; similarity = expected/mean cosine over the two clouds (Reisinger-Mooney AvgSim). Senses emerge, no imposed k.
- TOKEN_CLOUD_MAXSIM [treatment, brain-faithful] = same cloud, MAX cosine over token pairs (best-matching sense) -- the sense-SELECTIVE readout; from the SAME assembled matrix, no extra SVD.
- RANDOM_CLOUD_AVGSIM / RANDOM_CLOUD_MAXSIM [INFO-FREE TWINS] = same per-word token budget sampled from the GLOBAL pool (word's own context structure destroyed), scored with the matching reduction. MUST LOSE -- controls the budget/maxSim inflation.
- MULTIPROTO_K{2,3,5} + MULTIPROTO_RANDSENSE_K{2,3,5} [SECONDARY / OUR-INVENTION, labelled] = discrete k-means multi-prototype + its random-sense twin. Kept as the discretized approximation; do NOT decide the verdict.
Polysemy stratification via the baked wordnet_polysemy_static.json (WordNet sense counts, 1996 words -- no nltk on remote). Score paired_delta rho + ci_half + null_p95 + coverage; scored_population emitted per arm.

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn incl. KMeans; NO torch). Loads the 15M PRE-PARSED cache; NEVER parses
(no spaCy token in the file; fails loud if the cache is missing). bare == FULL (line 936: `smoke =
bool(args.smoke) or (args.mode == "smoke")`). --self-test GREEN (colmap-reproduction, occurrence-additivity,
mechanism-fires K=2, arms-must-differ, MAXSIM + both CLOUD_BUDGET inflation guards fire). --smoke GREEN
(machinery-only RIGOROUS_NEGATIVE at 150k, per docstring -- the claim is a 15M question). metrics.json
written INCREMENTALLY per-arm (partial:true / arms_done; atomic tmp+os.replace; mode-keyed _ckpt dir);
resumable per-word cloud/cluster loops. The 6th KB_REFERENT (wordnet_polysemy_static.json) is a NEW local
asset that MUST ship to remote. timeout 5400 (agent estimate 45-80 min: ~9 SVD fits + occurrence-matrix build).

## Results
data/exp_multiproto_sense_learner_v1/metrics.json (per-arm SimLex/SimVerb/WordSim rho, paired deltas + CIs,
polysemy-stratified interaction, per-readout twins, scored_population), synced back ~20 min. NOTE the standing
infra gotchas: hd_metrics_sync is DISABLED (pull manually via the orchestrator) and the runner may write a
double-prefixed data/exp_exp_<name>/ path (SH-4). Strategy does NOT integrate -- WIP until owner_verdict:
DONE; to be VETTED before folding into SOLVED.md if it is a WIN.
