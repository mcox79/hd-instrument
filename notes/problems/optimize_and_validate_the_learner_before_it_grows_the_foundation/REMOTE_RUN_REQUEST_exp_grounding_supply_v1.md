---
cell: experiments/exp_grounding_supply_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 3600
results_path: data/exp_grounding_supply_v1/metrics.json
self_test: green
smoke: green
question: Is the learner-vs-supervised-WordNet gap a closable GROUNDING-SUPPLY gap? Does RICHER grounded supply (full Lancaster-11 + Brysbaert concreteness + Binder-2016 65 brain-based attributes) beat the thin grounded supply AND add non-redundant signal to text-only on a NON-WordNet gold (MEN human relatedness), with the CROSSOVER -- grounding helps MORE on associative MEN than on WordNet-derived SimLex?
gate: HARD_PASS iff (i) RICH beats LANC CI-separated on the Binder-covered subset (richer supply adds), AND (ii) FUSED beats TEXT-alone on MEN CI-separated (grounding adds non-redundant signal to the learned distributional channel at FULL 15M scale), AND (iii) CROSSOVER -- the grounding benefit (FUSED-minus-TEXT, or RICH-vs-TEXT) is LARGER on MEN than on SimLex. RANDOM must LOSE on all. RIGOROUS_NEGATIVE (a PASS) if richer supply does not add / the crossover vanishes once the FULL-scale (not smoke) TEXT arm is used, or if Binder coverage (~434 words) is too thin to power (i)/(iii) -- report n and say so rather than forcing a verdict.
kb_referents:
  - data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl
  - data/men/men_try.txt
  - data/corpora/binder/binder2016_ratings.csv
  - data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv
  - data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt
---
# REMOTE_RUN_REQUEST -- exp_grounding_supply_v1 (fidelity phase, WALL B: the grounding-supply gap)

**RE-FIRE 2026-08-28c** (prior re-fire hit an rc=127 backslash-path bug in the fulfiller --rerun branch; retrying to test if it's fixed): cell hardened -- per-arm checkpointing (metrics.json written incrementally with
`partial: true`/`arms_done` so a late failure/timeout keeps completed arms) AND the smoke-default bug
fixed (bare invocation now == FULL; the remote runner passes no `--mode`). Self-test green.

Solver-dropped request (solvers are scope-barred from preregs/**). A STRATEGY session runs:

    .venv/Scripts/python.exe tools/fulfill_remote_run_request.py --request notes/problems/optimize_and_validate_the_learner_before_it_grows_the_foundation/REMOTE_RUN_REQUEST_exp_grounding_supply_v1.md

Add `--dry-run` first to validate + preview without writing/shipping/queuing.

## Brain claim (PINNED)
Word meaning is an OPTIMAL COMBINATION of EXPERIENTIAL (multimodal grounded) + DISTRIBUTIONAL data
(Andrews, Vigliocco & Vinson 2009; Lambon Ralph hub-and-spoke). Our grounded supply is thin (12-dim Lancaster
+ concreteness). Test whether richer grounded supply closes some of the learner-vs-WordNet gap, and whether the
value shows where taxonomic WordNet is weakest (a non-WordNet, associative gold).

## Arms (feature-vector cosine unless noted; scored on MEN primary + SimLex crossover + WordSim calibration)
- LANC        -- full Lancaster-11 sensorimotor + Brysbaert concreteness (broad coverage; the current thin supply).
- BINDER      -- Binder-2016 65 brain-based attributes (~434 words -- NARROW; report coverage).
- RICH        -- LANC (+) BINDER concatenated where both present (else LANC).
- TEXT        -- the learned DEP_TYPED distributional cosine from the 15M PRE-PARSED cache (weak at smoke; real at full).
- FUSED       -- reliability-weighted RICH (+) TEXT.
- RANDOM [INFO-FREE] -- matched-dim random vectors; MUST LOSE on all golds.

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn, NO torch). Loads the 15M PRE-PARSED cache for the TEXT arm; NEVER parses
(no module-level spaCy on the import path -- verified). --self-test + --smoke GREEN locally. KB_REFERENTs: the
15M cache + SimVerb are already shipped to marsh@home; the 3 grounding CSVs (MEN, Binder, Lancaster, Brysbaert)
queue_add.sh will ship if missing.

## Results
data/exp_grounding_supply_v1/metrics.json (verdict + per-gold rho + Delta-rho CIs + per-arm coverage). Synced back
via local_metrics_sync.ps1 (~20 min) or tools/orchestrator/scp_recover_landing.py --verify-after exp_grounding_supply_v1.
Solver reads the verdict there; strategy does NOT integrate (WIP until owner_verdict: DONE).
