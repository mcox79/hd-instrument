# Pre-reg: exp_exemplar_selpref_v1

**Auto-generated 2026-08-28 by tools/fulfill_remote_run_request.py (strategy fulfiller) from a solver REMOTE_RUN_REQUEST.** Dispatched to `remote_cpu_queue` (marsh@home), args `--mode full`. This is a COMPUTE dispatch, not an integration.

## Question
Does an EXEMPLAR-SET selectional-preference code beat the word-identity selectional-preference floor in the RARE/low-frequency verb regime (where a word-identity code runs out of data), even if it need not win pooled?

## Gate
HARD_PASS iff EXEMPLAR_SP beats WORDID_SELPREF CI-separated on the RARE-verb subset (paired Delta-rho lower CI > 0) AND beats FEATURE_SHUFFLE CI-separated (any subset). Pooled loss to WORDID_SELPREF is expected/OK. RIGOROUS_NEGATIVE (a PASS) if it beats neither once floors are recomputed on the RARE subset.

## Compute route
- Queue: **remote_cpu_queue** (remote CPU runner -- numpy/scipy/sklearn, no torch).
- torch on the import path: no.

## Data dependencies (KB_REFERENT -- auto-shipped by queue_add.sh if missing on remote)
- `data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl`
- `data/encoder_eval_benchmarks/simverb3500.txt`

## Remote-safety
Verified by the fulfiller before dispatch: --self-test/--smoke present and (unless skipped) PASSED; no module-level spaCy on the cell or its imported experiments.* siblings (remote has no spaCy -> the cell LOADS a pre-parsed cache, never parses); CPU/GPU route matches the cell's torch usage.

## Solver notes (from the request)
# REMOTE_RUN_REQUEST -- exp_exemplar_selpref_v1 (fidelity phase, solver problem: optimize_and_validate_the_learner...)

**This is a TEMPLATE + a live request.** A solver drops a file like this in its own problem folder to request a
remote run without writing a prereg (solvers are scope-barred from preregs/**). A STRATEGY session then runs:

    .venv/Scripts/python.exe tools/fulfill_remote_run_request.py --request notes/problems/optimize_and_validate_the_learner_before_it_grows_the_foundation/REMOTE_RUN_REQUEST_exp_exemplar_selpref_v1.md

Add `--dry-run` to validate + preview without writing/shipping/queuing.

## Arms (all built from the identical (verb, ARG) co-occurrence table -- the only variable is the FEATURE)
- EXEMPLAR_SP -- verb -> top-K count-weighted argument fillers across ARG_SLOTS; similarity over exemplar sets.
- WORDID_SELPREF [FLOOR] -- the incumbent that won pooled at 15M tokens (build_selpref_cooc -> PPMI -> SVD). Reused verbatim.
- WIN2 [context-shape baseline] -- +/-2 window co-occurrence PPMI-SVD.
- FEATURE_SHUFFLE [INFO-FREE TWIN] -- EXEMPLAR_SP's exact filler/weight/slot structure with filler identities shuffled. MUST LOSE.

## Population / scorer
SimVerb-3500 (data/encoder_eval_benchmarks/simverb3500.txt). Paired Spearman rho over covered pairs; RARE-subset split
(low-frequency verbs both real arms cover) vs pooled. Floors recomputed per subset; no number crosses subsets.

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn, NO torch). Loads the 15M-token PRE-PARSED cache; NEVER parses (no module-level
spaCy on the import path -- verified). --self-test GREEN locally (cache-free). Both KB_REFERENTs already shipped +
byte-verified on marsh@home (458169175 and 97778 bytes); queue_add.sh re-ships any that are missing.

## Results
data/exp_exemplar_selpref_v1/metrics.json (verdict + per-subset rho + Delta-rho CIs + coverage). Synced back via
local_metrics_sync.ps1 (~20 min) or tools/orchestrator/scp_recover_landing.py --verify-after exp_exemplar_selpref_v1.
The solver reads the verdict there; strategy does NOT integrate on it (WIP until owner_verdict: DONE).
