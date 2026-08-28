# Pre-reg: exp_reading_comprehensible_input_zpd_v1

**Auto-generated 2026-08-28 by tools/fulfill_remote_run_request.py (strategy fulfiller) from a solver REMOTE_RUN_REQUEST.** Dispatched to `remote_cpu_queue` (marsh@home), args `--mode full`. This is a COMPUTE dispatch, not an integration.

## Question
On an INDEPENDENT machine, does comprehensible-input/ZPD source-selection beat FROZEN and RANDOM register-controlled; does the graded per-word partial-credit selector match the 0.5-threshold selector WITHOUT starving; and does judging comprehensibility over a LOCAL word window (CI_GRADED_WIN) beat the whole-sentence graded selector (CI_GRADED)?

## Gate
CI_050, CI_GRADED and CI_GRADED_WIN each beat FROZEN AND RANDOM on register-controlled coverage, CI-separated on all seeds (bootstrap CI, delta lower bound > 0); the info-free twin CI_SHUFFLED LOSES CI-separated; the strict CI_085/CI_ADAPTIVE arms STARVE (grounded << CI_050) as a can-fail reference. Recompute floors per population; no number crosses scorers/populations.

## Compute route
- Queue: **remote_cpu_queue** (remote CPU runner -- numpy/scipy/sklearn, no torch).
- torch on the import path: no.

## Data dependencies (KB_REFERENT -- auto-shipped by queue_add.sh if missing on remote)
- `data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv`
- `data/corpora`
- `data/closed_class_lexicon_v1.json`

## Remote-safety
Verified by the fulfiller before dispatch: --self-test/--smoke present and (unless skipped) PASSED; no module-level spaCy on the cell or its imported experiments.* siblings (remote has no spaCy -> the cell LOADS a pre-parsed cache, never parses); CPU/GPU route matches the cell's torch usage.

## Solver notes (from the request)
<!-- RERUN 2026-08-28: first remote attempt FAILED (exit 1, 30s) = ModuleNotFoundError: spacy.
     Cause: reading_grounding_loop -> closed_class_lexicon.get_closed_class_set() calls _spacy_stop_words()
     to BUILD the set, but it LOADS data/closed_class_lexicon_v1.json if present (spaCy-free). Fix: ship
     that pre-built cache (added to kb_referents above). Also fixed a double-"exp_" output-dir name so
     results land at results_path. -->


# Remote run — comprehensible-input/ZPD reader: independent replication + graded-selector component optimization

**What / why.** Off-laptop (independent-machine) confirmation of the SOLVED result for
`the_reader_cannot_choose_what_to_read_next`, plus a brain-foundational component optimization of the
winning selector. Local 3-seed run gave HARD_PASS (CI_050 register-controlled 0.081 vs FROZEN 0.031 /
RANDOM 0.029, CI-separated all seeds; twin 0.015 loses; CI_GRADED 0.081 matches; CI_085/CI_ADAPTIVE starve
at 0.012/0.011).

**Arms (8):** FROZEN [floor], RANDOM [floor/info-free], CI_050 [proven 0.5 threshold], CI_085 & CI_ADAPTIVE
[starved can-fail refs], CI_GRADED [graded per-word x^2 partial credit, whole-sentence — anti-starvation
fix], **CI_GRADED_WIN [graded x^2 over a LOCAL +-4-word window — the finer-locality component optimization
(N400 integration window / research 2026-08-28 granularity point)]**, CI_SHUFFLED [info-free twin:
comprehensibility scores permuted]. Config (cell defaults, run BARE=full): 6000 sentences/arm, seeds
0/1/2, register-controlled coverage metric, bootstrap CI (4000).

**Floor / twin / population.** Strongest floor = FROZEN (register-controlled 0.031); second RANDOM 0.029.
Info-free twin = CI_SHUFFLED (0.015). Grounded-subject population saved per (arm, seed) in units.jsonl.

**Remote-safe + crash-safe:** no module-level spaCy in the import chain (glass-box lemmatizer
`hdlab.thematic_role_labeler.lemma_word`); DEFAULTS TO FULL when run bare (runner gotcha handled);
writes a RUNNING metrics.json after EVERY (arm,seed) unit (a mid-run crash loses nothing) and is resumable
per unit via units.jsonl; `--self-test` GREEN locally.

**Data note (not a blocker for the watcher — hdlab deps auto-ship):** base_vocabulary_ordered.csv is small
and declared (auto-ships). `data/corpora` exists on marsh@home but may be an OLDER set; if the run fails on
missing/incompatible corpus data, that bulk data isn't in git and needs a one-time strategy/owner sync of
`data/corpora` — I'll flag it from the watcher log / results if so.
