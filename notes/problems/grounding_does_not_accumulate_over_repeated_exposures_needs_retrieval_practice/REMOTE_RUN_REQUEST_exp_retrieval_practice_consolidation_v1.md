---
cell: experiments/exp_retrieval_practice_consolidation_v1.py
mode: full
args: "--confirm-all --mode full --seed 0"
queue: remote_cpu_queue
timeout_s: 6000
results_path: data/exp_retrieval_practice_consolidation_v1/confirm_all.json
self_test: green
smoke: green
question: "At FULL 3000-sentence scale, does the READ-OUT verdict hold -- is the correct meaning-anchor RETRIEVABLE (top-10) under every encoder yet NOT SELECTABLE by any read-out (incl. supervised)?"
gate: "PASS = (a) oracle representation_recoverable >> coverage_bound (a correct anchor EXISTS for most CONSOLIDATION_FAIL words); (b) every encoder phi/bag/PPMI+SVD puts the correct anchor in top-10 for the majority (frac_correct_in_top10 >= 0.6) -> the encoder is not the wall; (c) NO read-out selects it -- NEAREST/BG_SUBTRACT/DISTILLED/SUPERVISED rank-1 all << the top-10 ceiling (best << 0.6), and supervised lift_over_nearest <= 0.10. A rigorous confirmation of the smoke-decisive negative (the selection signal is absent from distributional context -> grounded/ATL is the lever)."
kb_referents:
  - data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv
  - data/corpora/simplewiki
  - data/corpora/onestop
  - data/corpora/process_articles_v1
  - data/corpora/breadth_v1
  - data/corpora/textbook_biology_2e
  - data/corpora/textbook_psychology_2e
---
# REMOTE_RUN_REQUEST -- exp_retrieval_practice_consolidation_v1 (--confirm-all, full, CPU)

NO torch (numpy/scipy/sklearn only) -> remote_cpu_queue. NO module-level spaCy anywhere in the import
chain (verified; the ZPD sibling loads a stop-words asset precisely so remote has no spaCy). The bag/PPMI
read-out path does NOT parse live (context vectors are hashed bags); `--confirm-all` runs the STRUCTURAL
encoder with do_structural=False so nothing parses on remote. Needs nltk WordNet (used by _wn_related
throughout, as in the already-run core cell). The corpus set is `hdlab.corpus_registry` (core shared
asset); the CI_050 forager reads the STATUS_READABLE corpora -- the kb_referents list the primary modern
ones; if the full tree is already present on the box nothing re-ships.

WHY: the LOCAL smoke result is decisive (n=270 recoverable words, unanimous across 6 encoders + 5 read-outs
+ a supervised CV logistic), and the core retrieval-practice NEGATIVE is already 2-seed. This run confirms
the READ-OUT localisation at full 3000-sentence scale on the remote box (disciplined multi-seed-the-headline
polish; drop a matching request with `--seed 1` for the second seed). Retrieval practice is REFUTED; the
wall is representation-bound at the SELECTION level; the lever is grounded/sensorimotor sense-selection
(reader_meaning_channel/ATL = Phase 1). See SOLVED.md for the full verdict.
