# Pre-reg: exp_reading_comprehensible_input_zpd_v1

**Auto-generated 2026-08-28 by tools/fulfill_remote_run_request.py (strategy fulfiller) from a solver REMOTE_RUN_REQUEST.** Dispatched to `remote_cpu_queue` (marsh@home), args `--mode full`. This is a COMPUTE dispatch, not an integration.

## Question
On an INDEPENDENT machine, does comprehensible-input/ZPD source-selection beat FROZEN and RANDOM register-controlled, and does the graded per-word partial-credit selector (CI_GRADED) match the 0.5-threshold selector (CI_050) WITHOUT starving like the strict CI_085/CI_ADAPTIVE arms?

## Gate
CI_050 AND CI_GRADED each beat FROZEN AND RANDOM on register-controlled coverage, CI-separated on all seeds (bootstrap CI, delta lower bound > 0); the info-free twin CI_SHUFFLED LOSES CI-separated; the strict CI_085/CI_ADAPTIVE arms STARVE (grounded << CI_050) as a can-fail reference. Recompute floors per population; no number crosses scorers/populations.

## Compute route
- Queue: **remote_cpu_queue** (remote CPU runner -- numpy/scipy/sklearn, no torch).
- torch on the import path: no.

## Data dependencies (KB_REFERENT -- auto-shipped by queue_add.sh if missing on remote)
- `data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv`
- `data/corpora`

## Remote-safety
Verified by the fulfiller before dispatch: --self-test/--smoke present and (unless skipped) PASSED; no module-level spaCy on the cell or its imported experiments.* siblings (remote has no spaCy -> the cell LOADS a pre-parsed cache, never parses); CPU/GPU route matches the cell's torch usage.

## Solver notes (from the request)
# Remote run request — comprehensible-input/ZPD reader, independent-machine replication + graded arm

**What / why.** Independent-machine (off-laptop) replication of the SOLVED result for
`the_reader_cannot_choose_what_to_read_next`, now including the anti-starvation `CI_GRADED` arm. The
local 3-seed run gave HARD_PASS (CI_050 register-controlled 0.081 vs FROZEN 0.031 / RANDOM 0.029,
CI-separated all seeds; twin 0.015 loses; CI_GRADED 0.081 matches; CI_085/CI_ADAPTIVE starve at 0.012/0.011).
This confirms it on a second machine and exercises the remote pipeline (owner standing rule: heavy runs
go off the laptop).

**Arms (7):** FROZEN [floor], RANDOM [floor/info-free], CI_050 [proven], CI_085 & CI_ADAPTIVE [starved
can-fail refs], CI_GRADED [graded per-word x^2 partial credit — the brain-faithful anti-starvation
selector], CI_SHUFFLED [info-free twin: comprehensibility scores permuted]. Config (cell defaults, run
BARE=full): 6000 sentences/arm, seeds 0/1/2, register-controlled coverage metric, bootstrap CI (4000).

**Floor / twin / population.** Strongest floor = FROZEN (fixed 4-corpus schedule), register-controlled
0.031; second floor RANDOM 0.029. Info-free twin = CI_SHUFFLED (0.015). Grounded-subject population saved
per (arm, seed) in units.jsonl; metrics.json carries per_arm_summary + per_arm units.

**Remote-safe:** no module-level spaCy anywhere in the import chain (reading uses a glass-box lemmatizer,
`hdlab.thematic_role_labeler.lemma_word`); defaults to FULL when run bare (the documented runner gotcha);
writes a RUNNING metrics.json after EVERY (arm,seed) unit so a mid-run crash never loses completed work,
and is resumable per unit via units.jsonl. `--self-test` GREEN locally.

## ⚠️ BLOCKER FOR THE FULFILLER (strategy): the remote repo is STALE
Verified 2026-08-28 on marsh@home: `C:/dev/hd-instrument/hdlab/corpus_registry.py` is ABSENT, and
`.../base_vocabulary/cleaned/base_vocabulary_ordered.csv` is ABSENT (data/corpora dir exists but is an
older set). This cell imports `hdlab.corpus_registry`, `hdlab.information_foraging`,
`hdlab.reading_grounding_loop` (+ transitive: grounding_acquisition_loop, thematic_role_labeler,
hd_fact_store, codec, role_slot_summarizer, cleanup_family, gap_detector, ...). `queue_add.sh` Pattern 5b
only auto-ships `cleanup_family` / `reachability_audit`, NOT these — so the remote self-test will
`ModuleNotFoundError` until the remote repo's `hdlab/` is synced to current. **Please sync `hdlab/`
(and the base_vocabulary CSV) to marsh@home before/with fulfilling** (the two sibling experiment cells
auto-ship fine via Pattern 6). Run `tools/fulfill_remote_run_request.py --request <this file> --dry-run`
first to confirm the KB_REFERENT/guardrail set.
