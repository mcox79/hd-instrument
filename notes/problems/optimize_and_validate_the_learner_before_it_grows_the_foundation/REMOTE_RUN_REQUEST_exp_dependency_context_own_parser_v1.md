---
cell: experiments/exp_dependency_context_own_parser_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 14400
results_path: data/exp_dependency_context_own_parser_v1/metrics.json
self_test: green
smoke: green
question: WIRE-DONT-ISLAND -- does the BAR1 dependency-typed-context similarity win (dependency PPMI-SVD beats +/-2 window on SimLex/SimVerb) SURVIVE when the parses come from the SUBSTRATE'S OWN glass-box front-end (pos_tagger + arc_parser + arc_labeler, UD-EWT-trained) instead of spaCy? BAR1 rests on an offline spaCy parse cache; the substrate's own parser has never been wired onto anything -- this asks whether it is FIT to wire.
gate: PASS iff DEP_ARCPARSER (the substrate's own hashed parser) beats WIN2 CI-separated (paired Delta-rho lower CI > 0) on SimLex (the parse-ROBUST axis per fidelity phase 2). SimVerb (parse-SENSITIVE) is reported, not gated. DEP_SPACY_vs_WIN2 is the built-in POSITIVE CONTROL (must reproduce BAR1 at 5M -- pre-confirmed locally: SimLex +0.0594 CI[0.017,0.108], SimVerb +0.0406 CI[0.010,0.073], tracking BAR1's 15M +0.0598/+0.0342). DEP_ARCPARSER_RICHFEAT (higher-UAS UD-EWT variant) is a REPORTED second treatment (not gated) that disambiguates parser-QUALITY vs DOMAIN-transfer. RIGOROUS_NEGATIVE (a FULL PASS) if DEP_ARCPARSER does not beat WIN2: report the measured UAS/LAS + simplewiki head-agreement gap -- that IS the wire-don't-island blocker made concrete (interim smoke already shows only 46% head-agreement vs spaCy on simplewiki: a UD-EWT->reading-domain transfer gap).
kb_referents:
  - data/frontend_assets/pos_tagger_ud_ewt_upos.json
  - data/frontend_assets/arc_parser_hashed_ud_ewt.npz
  - data/frontend_assets/arc_parser_richfeat_ud_ewt.npz
  - data/frontend_assets/arc_labeler_hashed_ud_ewt.json
  - data/encoder_eval_benchmarks/simlex999.txt
  - data/encoder_eval_benchmarks/simverb3500.txt
  - data/encoder_eval_benchmarks/wordsim353_combined.csv
  - data/exp_structured_context_learner_v1/parsed_simplewiki_5000000tok.jsonl
  - experiments/data/ud_english_ewt/en_ewt-ud-test.conllu
  - experiments/exp_parser_uas_ladder_richfeat_v1.py
---
# REMOTE_RUN_REQUEST -- exp_dependency_context_own_parser_v1 (adjacent-limitation drill: wire-don't-island the learner's FRONT-END)

Solver-dropped request; the strategy/orchestrator lane runs the fulfiller (validates, writes prereg, ships code+data, queues CPU).

## Why (the adjacent limitation)
BAR1's whole result is built on offline spaCy dependency parses. Fidelity phase 2 showed the SimVerb
(verb-axis) win is PARSE-QUALITY-SENSITIVE. The substrate has its OWN glass-box parser (pos_tagger +
arc_parser + arc_labeler, UD-EWT-trained, no LLM/torch/spaCy) but it is ISLANDED. This tests whether the
learner's win survives on the substrate's real front-end -- the wire-don't-island question for the whole
result. Distinct from the prior exp_reader_parser_swap_* cells (which measured READING/extraction accuracy,
different pipeline + metric; confirmed not a rediscovery).

## Arms (ONE VARIABLE = the parse SOURCE; same 5M tokens, same PPMI-SVD k=500, same scorer, reused verbatim)
- WIN2 [FLOOR] = +/-2 window PPMI-SVD (parser-agnostic).
- DEP_SPACY [CEILING / POSITIVE CONTROL] = dependency-typed context from the EXISTING 5M spaCy cache (loaded, NEVER re-parsed). Reproduces BAR1 (pre-confirmed at 5M).
- DEP_ARCPARSER [TREATMENT, GATED] = dependency-typed context from the substrate's OWN hashed parser (pos_tagger -> arc_parser -> arc_labeler).
- DEP_ARCPARSER_RICHFEAT [TREATMENT, REPORTED] = the higher-UAS rich-feature UD-EWT variant (RichArcParser; UD-EWT gold-POS UAS 0.7925 vs base 0.7868). Its simplewiki head-agreement measures whether the domain gap is PARSER-INVARIANT (both UD-EWT parsers transfer equally poorly => domain, not quality, is the bottleneck).
- RANDOM [sentinel] random dense vectors.
Parse quality measured two ways per own-parser: true UAS/LAS vs UD-EWT test gold, AND head-agreement vs spaCy on a held-out simplewiki slice. paired_delta rho + ci_half + null_p95 + coverage; scored_population per arm.

## Compute / remote-safety
remote_cpu_queue (pos_tagger/arc_parser/arc_labeler/RichArcParser are numpy + pure-python -- NO torch, NO
spaCy on the run path; the 5M spaCy cache is LOADED via load_parsed, parse_and_cache never called). RUNNING
the own parser IS the point (that is the substrate's own tool under test, not the "never parse" rule which
is about spaCy). bare == FULL == 5M tokens (line 68: `smoke = bool(args.smoke) or (args.mode == "smoke")`;
the remote runner passes no --mode). --self-test + --smoke GREEN (arms-differ on all 4 SVD arrays). 5M
confirmed WELL-POWERED (positive control reproduces BAR1). metrics.json written INCREMENTALLY per-stage
(partial:true / arms_done; atomic tmp+os.replace); the own-parse cache is RESUMABLE PER-PARSER (a
timeout-kill loses only the in-flight parser's remaining sentences on re-dispatch, not the completed one).
timeout 14400 (4h): the own-parse runs TWICE now (hashed ~55min + richfeat ~75-90min at ~900-1500 tok/s) +
build/score/quality ~5min => ~2.3-2.6h, with margin. TEN KB_REFERENTs -- the frontend_assets (parser
weights ~25MB), the UD-EWT gold conllu, the 5M spaCy cache (~133MB), and the RichArcParser source module are
deps NOT shipped in prior runs; the fulfiller ships missing ones.

## Results
data/exp_dependency_context_own_parser_v1/metrics.json (per-arm SimLex/SimVerb/WordSim rho, paired deltas +
CIs, gate booleans, own-parser UAS/LAS vs UD-EWT + simplewiki head-agreement for both parser variants),
synced back after the run. NOTE the standing infra gotchas: hd_metrics_sync is DISABLED (pull manually via
the orchestrator) and the runner may write a double-prefixed data/exp_exp_<name>/ path (SH-4). Strategy does
NOT integrate -- WIP until owner_verdict: DONE; to be VETTED before folding into SOLVED.md.
