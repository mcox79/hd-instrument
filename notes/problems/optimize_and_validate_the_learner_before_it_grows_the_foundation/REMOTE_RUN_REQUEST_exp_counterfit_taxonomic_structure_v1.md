---
cell: experiments/exp_counterfit_taxonomic_structure_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 3600
results_path: data/exp_counterfit_taxonomic_structure_v1/metrics.json
self_test: green
smoke: green
question: Does injecting TAXONOMIC structure into the learned dependency-typed vectors -- counter-fitting them to WordNet synonym/hypernym ATTRACT + antonym REPEL (the computational-level instantiation of hub-and-spoke: the ATL reorganises distributional experience into an amodal taxonomic similarity space) -- GENERALISE, i.e. reorganise the geometry so it lifts similarity on HELD-OUT relations + a DISJOINT gold the fit never saw, rather than merely MEMORISE the WordNet answer for covered pairs? The research drill named this the highest-measured-leverage lever (literature 0.37->0.68-0.76); the question is whether it generalises on THIS substrate.
gate: PASS iff COUNTER_FIT beats RAW CI-separated (paired Delta-rho) on the HELD-OUT WordNet relations AND on the DISJOINT similarity gold (SimLex/SimVerb/WordSim pairs where NEITHER word was in TRAIN), AND the SHUFFLED_CONSTRAINTS info-free twin does NOT beat RAW on held-out. The WordNet-COVERED gold is reported but LABELLED memorisation-inflated, NOT gated. RIGOROUS_NEGATIVE (a FULL PASS, state which): if COUNTER_FIT only helps the COVERED pairs but NOT the held-out/disjoint gold, that is ORACLE MEMORISATION not reorganisation -- report it plainly (injected structure does not generalise on this substrate, and why). Precedent that supervised structure-injection DOES generalise here: exp_corpus_capacity_ppmi_svd_ceiling_v1 (held-out 5-fold CV AUC 0.96).
kb_referents:
  - data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl
  - data/exp_learner_safety_gate_v1/parsed_simplewiki_150000tok_posfixed.jsonl
  - data/exp_counterfit_taxonomic_structure_v1/counterfit_constraints_static.json
  - data/encoder_eval_benchmarks/simlex999.txt
  - data/encoder_eval_benchmarks/simverb3500.txt
  - data/encoder_eval_benchmarks/wordsim353_combined.csv
---
# REMOTE_RUN_REQUEST -- exp_counterfit_taxonomic_structure_v1 (the highest-leverage optimization: inject taxonomic structure, test GENERALISATION)

Solver-dropped request; the strategy/orchestrator lane runs the fulfiller (validates, writes prereg, ships code+data, queues CPU).

## Brain foundation (PINNED at the computational level -- NOT a pure NLP hack)
HUB-AND-SPOKE (Lambon Ralph et al. 2017): the anterior temporal lobe REORGANISES distributional/experiential
input into an amodal, TAXONOMICALLY-structured similarity space (the taxonomic-vs-thematic neural double-
dissociation, Schwartz 2011). Counter-fitting the learned distributional vectors with taxonomic (synonym/
hypernym ATTRACT) + contrast (antonym REPEL) relations is the computational-level instantiation of that
reorganisation. PINNED = taxonomic organisation is a real brain axis. OUR-INVENTION = WordNet as the STRUCTURE
SOURCE (an admissible OFFLINE-FOUNDATION proxy; the pivot -- build the ideal foundation from existing tools,
glass-box, NO LLM at inference; the counter-fit update is transparent attract/repel). The fully-brain-faithful
endpoint LEARNS/MINES the structure (cf. the sibling is-a-extraction drill + the research drill's Hearst-mining
recommendation) -- WordNet is the interim source.

## Arms (base = dependency-typed PPMI-SVD, k=500, 15M)
- RAW [FLOOR] = the un-retrofitted dependency-typed vectors (~0.27 SimLex).
- COUNTER_FIT [treatment] = RAW counter-fitted to TRAIN WordNet constraints (synonym/hypernym attract, antonym repel, vector-space-preservation propagating movement to each word's ORIGINAL-space top-5 neighbours -- the mechanism that lets HELD-OUT words move). Transparent Jacobi fixed-point, N_ITER=15, under-relaxation eta=0.25 (Faruqui 2015 / Mrksic 2016 spirit).
- SHUFFLED_CONSTRAINTS [INFO-FREE TWIN] = counter-fit to the SAME NUMBER of RANDOM word-pair constraints (fixed seed). MUST NOT generalise to held-out.
- SUPPLIED_WORDNET [reference, not gated] = the existing conceptual_meaning WordNet channel's number on the covered gold = the memorisation ceiling.
ORACLE GUARD: WORD-level TRAIN/HELD split (~70/30, seeded). TRAIN edges = both endpoints in TRAIN_WORDS (the ONLY edges counter-fit sees). HELD-OUT relations = both in HELD_WORDS. DISJOINT gold = SimLex/SimVerb/WordSim pairs where NEITHER word in TRAIN_WORDS. TRAIN/HELD overlap printed = 0. Static asset: 69,343 synonym + 151,160 hypernym + 3,237 antonym pairs.

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn; NO torch). Loads the 15M PRE-PARSED cache; NEVER parses. NO nltk on the
run path -- the WordNet constraints + SUPPLIED_WORDNET reference are BAKED to counterfit_constraints_static.json
(5.69MB); nltk/ConceptualChannel imported ONLY in bake_counterfit_assets() + self_test(), never on the smoke/
full path (fail loud via SystemExit if the asset is missing). bare == FULL (`smoke = bool(args.smoke) or
(args.mode == "smoke")`). --self-test GREEN (held-out pairs generalise via VSP: glad/elated 0.90->0.95,
antonyms repelled; wrong-content control generalises far less; TRAIN/HELD overlap 0). --smoke GREEN (mechanism
fires: covered SimLex 0.019->0.207 while held-out stays CI-unseparated at 150k -- honest memorisation-not-
reorganisation preview; shuffled twin does not beat RAW). Canonical line-start KB_REFERENTs; _seed_checkpoint +
exp_checkpoint (PROT-021); incremental per-arm metrics; scored_population. The static asset (3rd KB_REFERENT)
is NEW -- must ship. timeout 3600 (~2-3x margin over the k=500/15M dependency-cell precedent 634-1541s).
WATCH: RAW's held-out AP (0.908 at smoke) is near the 0.95 AG-saturation threshold -- confirm the held-out AP
task has headroom at full scale (the paired-delta SimLex/SimVerb gold is the primary generalisation signal).

## Results
data/exp_counterfit_taxonomic_structure_v1/metrics.json (per-population RAW vs COUNTER_FIT vs SHUFFLED paired
deltas + CIs on HELD-OUT relations + DISJOINT gold + covered gold, gate booleans), synced back after the run.
Standing infra gotchas: hd_metrics_sync DISABLED (pull manually via orchestrator); runner may write a double-
prefixed data/exp_exp_<name>/ path (SH-4). Strategy does NOT integrate -- WIP until owner_verdict: DONE; VET
before folding into SOLVED.md if it is a WIN.
