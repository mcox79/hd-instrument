---
cell: experiments/exp_retrieval_practice_consolidation_v1.py
mode: full
args: "--confirm-all --mode full --seed 0"
queue: remote_cpu_queue
timeout_s: 7200
results_path: data/exp_retrieval_practice_consolidation_v1/confirm_all.json
self_test: green
smoke: green
question: "At FULL 3000-sentence scale, does the BRAIN-FOUNDATIONAL FULL LIFT hold -- does a pure GROUNDED sense-selection re-rank over the distributional shortlist roughly DOUBLE correct sense selection vs the distributional read-out, with the info-free shuffle at chance, while re-fusing the distributional cue does NOT help (it is confidently-wrong for sense)?"
gate: "PASS = (a) the READ-OUT localisation still holds -- oracle representation_recoverable >> coverage_bound; every encoder puts the correct anchor in top-10 for the majority; NO distributional read-out (nearest/bg/distilled/supervised) selects it (all << the top-10 ceiling); AND (b) THE FULL LIFT: in grounded_fusion, CASCADE_MORPH (Binder-65 experiential, morphology-extended, distributional-shortlist cascade) rank1 >> DIST with ci_CASCADE_MORPH_minus_DIST_WIRE_PLUS_MORPH separated above 0 (target ~2x DIST); GRD65_SHUF (info-free grounded shuffle) CI includes 0; FUSE_BOTH <= GRD65 (re-fusing distributional does not beat grounded-alone). Report the grounded_supervised_ceiling (upper bound on extractable grounded signal) beside the unsupervised lift. The full-lift claim: the ATL grounded hub re-rank selects the sense distributional co-occurrence cannot -- the brain-foundational Phase-1 mechanism, wireable."
kb_referents:
  - data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv
  - data/corpora
  - data/closed_class_lexicon_v1.json
  - data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv
  - data/grounding_testbed/Ratings_Warriner_et_al.csv
  - data/corpora/binder/binder2016_ratings.csv
  - data/exp_selpref_unseen_lowdata_v1/_ckpt_full/artifact_BINDER65_PREDICT.npz
  - data/exp_selpref_unseen_lowdata_v1/_ckpt_full/units.jsonl
---
# REMOTE_RUN_REQUEST -- exp_retrieval_practice_consolidation_v1 (--confirm-all, full, CPU)

REMOTE-SAFE (fixes the 4x prior rejections): the cell NOW declares `# KB_REFERENT:` lines (the hard
blocker before). spaCy-free: `hdlab.closed_class_lexicon` degrades to its FROZEN stop-word snapshot +
`data/closed_class_lexicon_v1.json` when spaCy is absent (the prior spaCy WARN was a false-positive
grep; the module's `_spacy_stop_words()` has a `try/except ImportError` fallback, asserted equal to
the live set when spaCy IS present). The read forages HASHED BAGS (never parses); `--confirm-all`
runs `encoder_diagnostic(do_structural=False)` so no live parser is ever needed. numpy/scipy/sklearn
+ nltk WordNet only -> remote_cpu_queue (NO torch).

WHAT `--confirm-all` now produces (one confirm_all.json): oracle + encoder(+distributional re-rankers)
+ supervised(distributional ceiling) + grounded_rerank(the 14-dim demonstrated fix) + **grounded_fusion
(THE FULL-LIFT MECHANISM: DIST / GRD14 / GRD65 / GRD65_MORPH / GRD_BOTH / CASCADE / CASCADE_MORPH /
FUSE* / shuffle-twin, with paired-bootstrap CIs, the abstract-slice ablation, and the measured-vs-
predicted-Binder anti-artifact cross-check)** + grounded_supervised_ceiling (upper bound; NOT a wire).

WHY REMOTE + FULL: the 2-seed SMOKE result is decisive in DIRECTION (GRD65/CASCADE ~doubles sense
selection over DIST, CI-separated both seeds; shuffle at chance; fusion HURTS; measured~predicted
Binder), but the READ POPULATION is hash-randomized so smoke MAGNITUDES wobble. This full 3000-sentence
run pins the magnitude + the finer claims that smoke could NOT separate (GRD65 > GRD14 richer-spoke;
abstract-slice Binder-65 lift). Drop a matching `--seed 1` request for the second seed. See SOLVED.md.
