---
cell: experiments/exp_directional_hypernymy_inclusion_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 2400
results_path: data/exp_directional_hypernymy_inclusion_v1/metrics.json
self_test: green
smoke: green
question: Can the STRONGER dependency-typed learned representation (which won on taxonomic SIMILARITY, BAR1) extract DIRECTIONAL is-a / hypernymy via an ASYMMETRIC distributional-inclusion measure -- a capability every prior unsupervised is-a attempt HARD_FAILED at, but with the OLD weak inducer? Symmetric cosine similarity fundamentally CANNOT do directional is-a; an asymmetric informativeness/inclusion measure (a hypernym occupies a broader, higher-entropy context distribution than its hyponyms) can. Tests the owner's "test the stronger brain version of a failed setup" discipline.
gate: PASS iff DEP_INCLUSION (WeedsPrec asymmetric inclusion over the dependency-typed rep) extracts is-a CI-separated ABOVE chance on the directional-2AFC (forward vs reversed) AND the DIRECTIONALITY control holds (COSINE_SIM sits exactly at chance 0.5 by construction; reversed pairs score lower) AND ideally DEP_INCLUSION beats WIN_INCLUSION (grammatical-relation context helps is-a specifically). ClarkeDE reported alongside as the measure-sweep robustness check; detection_ap (vs reversed+coordinate+random) with bootstrap CI + label-permutation null reported. RIGOROUS_NEGATIVE (a FULL PASS): if the stronger representation ALSO fails directional is-a (no better than chance / no directionality), then unsupervised is-a is genuinely hard for THIS substrate as built -- NOT merely an artifact of the old weak inducer -- report the mechanism reason. Either outcome RESOLVES the standing "was it the inducer or the capability?" question.
kb_referents:
  - data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl
  - data/exp_learner_safety_gate_v1/parsed_simplewiki_150000tok_posfixed.jsonl
  - data/exp_directional_hypernymy_inclusion_v1/wordnet_isa_static.json
---
# REMOTE_RUN_REQUEST -- exp_directional_hypernymy_inclusion_v1 (capstone: directional is-a on the stronger learned rep)

Solver-dropped request; the strategy/orchestrator lane runs the fulfiller (validates, writes prereg, ships code+data, queues CPU).

## Why (the owner's "test the stronger version of a failed setup" discipline)
Unsupervised is-a induction has repeatedly HARD_FAILED on this substrate -- BUT the prior-work check
verified NONE of those was distributional is-a EXTRACTION (they are subject-verb agreement, symbolic 2-hop
KG-completion, BFS graph composition; hypernymy/inclusion/BLESS/weeds/slqs all return 0 in the archive). NO
cell has ever tried extracting directional is-a from a distributional representation. The learner just
produced a stronger representation (dependency-typed PPMI-SVD, taxonomic SIMILARITY winner). Directional
is-a is ASYMMETRIC, so a symmetric cosine cannot do it; an asymmetric distributional-inclusion measure
(Weeds & Weir 2003; Geffet & Dagan 2005; Santus 2014 SLQS) can. This fair-tests the stronger version.

## Arms (one variable = the is-a signal / representation; PPMI-SVD dependency-typed vs window)
- COSINE_SIM [FLOOR, must fail on directionality] = symmetric cosine over the dependency-typed vectors -- self-test confirms it sits at exactly 0.5 (chance) on the directional-2AFC by construction.
- DEP_INCLUSION [treatment] = WeedsPrec asymmetric inclusion over the dependency-typed context distribution (ClarkeDE reported as the sweep).
- WIN_INCLUSION [context-shape control] = the same asymmetric measure over the +/-2 window representation.
- RANDOM [floor].
Gold (BAKED static asset, NO nltk on the run path): WordNet noun direct-hypernym (hyponym, hypernym) POSITIVES + COORDINATE (sibling) + RANDOM negatives, filtered to the run's frequency-built vocab. Discriminators: directional_2AFC (forward vs reversed, chance 0.5) + detection_AP (bootstrap CI + label-permutation null). scored_population emitted.

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn; NO torch). Loads the 15M PRE-PARSED cache; NEVER parses. NO nltk on
the run-time path -- the WordNet gold is BAKED offline to data/exp_directional_hypernymy_inclusion_v1/
wordnet_isa_static.json (5.76 MB, 109,508 pos pairs + 122,793 coord pairs); the run path LOADS + filters to
vocab (pure dict membership), fails loud if the asset is missing. nltk/wn appears ONLY in the offline bake
fn + the local self-test (grep-verified: main() and load_and_filter_gold have zero nltk/wn calls). bare ==
FULL (`smoke = bool(args.smoke) or (args.mode == "smoke")`). --self-test GREEN (WeedsPrec fires directionally
dog->animal 1.0 vs animal->dog 0.727; cosine at chance; directionality guard fires). --smoke GREEN
(RIGOROUS_NEGATIVE at 150k, honest -- dep_2afc 0.583 not yet CI-separated at that scale; the claim is a 15M
question). Canonical line-start KB_REFERENTs; `_seed_checkpoint` import + tools/exp_checkpoint ledger
(PROT-021); incremental per-arm metrics. The static gold (3rd KB_REFERENT) is NEW -- must ship to remote.
timeout 2400 (~10-15 min: no parse, ~9-arm inclusion measures over the cached vocab).

## Results
data/exp_directional_hypernymy_inclusion_v1/metrics.json (per-arm directional-2AFC + detection-AP + CIs,
directionality-control result, dep-vs-window comparison), synced back after the run. NOTE the standing infra
gotchas: hd_metrics_sync is DISABLED (pull manually via the orchestrator) and the runner may write a
double-prefixed data/exp_exp_<name>/ path (SH-4). Strategy does NOT integrate -- WIP until owner_verdict:
DONE; to be VETTED before folding into SOLVED.md if it is a WIN.
