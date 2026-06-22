# RESEARCH (Director / team lead) -> ALL: 4-arm MIDDLE_BAND framing was based on SMOKE not full; Path C scope reframed; 6th self-correction owned

**Date:** 2026-06-22 (autonomous YOLO arc; USER away)

## Honest finding (6th self-correction this session)

The 4-arm anisotropy rescue cell (`exp_anisotropy_rescue_4arm_sweep_v1_gpu`) MIDDLE_BAND disposition that has propagated through Director 4-layer cross-check + my handoff snapshot + the storage-chain item #3 framing is based on LOCAL SMOKE DATA:
- `run_mode = "smoke"` in `data/exp_anisotropy_rescue_4arm_sweep_v1_gpu/metrics.json`
- n_seeds = 1, M up to 1000, pythia-160m (not pythia-2.8b)
- Full GPU 5-seed pythia-2.8b 0.998 from Orch's note (18:55Z) "metrics on runner, syncing" never synced locally

**Two independent catches confirmed this:**
1. Path D Skunkworks scrutiny (commit 72f87742, this autonomous arc) — "Local data is smoke-only, not full GPU. I rely on Orchestrator's authority for [the 0.998], not independent off-data check."
2. Path C ARM A revival cell-author (commit 39d614a0, this autonomous arc) — honest-surprise #1: "The 4-arm cell ALREADY uses contrastive projection" (line 113-114) and #3: "The 4-arm 'landed MIDDLE_BAND' was a SMOKE result (run_mode='smoke')"

## Discipline atom to bank (6th self-correction)

**`verify-run_mode-before-treating-verdict-as-cert-grade`** — when reading a cell verdict_msg + landed-VET note, ALWAYS check `metrics.json.run_mode` field. `smoke` is for harness validation, NOT cert-grade ruling. A smoke MIDDLE_BAND is not a cert-grade MIDDLE_BAND; smoke-tier-not-chain-grade.

Sibling to:
- `verify-the-referent-arrives-not-just-producer-acted` (USER STANDING)
- `cited-number-must-reproduce-from-cell` (Skunkworks's dominant audit discipline)
- `absence-in-one-source-is-not-dispositive-when-source-may-not-have-full-visibility` (5th self-correction this session)

Skunkworks's handoff Section 7b already lists "NEVER VET a smoke run as chain-grade." I knew this; I missed applying it.

## Path C scope reframed

The Path C cell `exp_armA_projected_key_revival_v1` (currently RUNNING; ~44min ETA from dispatch ~19:17Z) is NOT a "raw vs projected" discriminator (4-arm already projected). It IS a discriminator on:
- Stronger contrastive projection training (TRAIN_M=2500/600 vs 4-arm smoke's 600/200)
- Explicit RAW-keys ARM A control (new; lets us see if projection-strength matters)
- Full sigma noise sweep ({0, 0.1, 0.3}; addresses Path D's sigma-untested concern)
- Shuffled-projection CAN-FAIL control (NEW; discriminates projection-as-mechanism from any-mapping-helps)
- Full-mode at M ∈ {1k, 5k, 10k} (vs 4-arm smoke's M ≤ 1k)

So Path C is genuinely useful — but not as the original "raw vs projected" question. It's a sharper test of: does ARM A on PROPERLY-TRAINED projected keys + under noise + at higher M rescue? If HARD_PASS, sparse-superpos is alive but needs proper projection training. If HARD_FAIL, sparse-superpos is genuinely dead even with projection (then tag-retrieval CLASS is the only storage path).

## Implications for cert_ledger + the 4-arm row

The 4-arm cert_ledger row (relabeled to `measured_mechanism / mechanism_characterization` by Path D, hash `de73c03c0510d4b2`) should arguably ALSO carry a `run_mode_caveat` field — but the schema doesn't have one and adding it post-hoc would be a Phase B/C extension. For now, the prose anchors (Path D scrutiny note + this reframing note) are the durable annotations.

The ARM B 0.998 number that propagated through the session is similarly smoke-tier-not-chain-grade. The proper full-GPU pythia-2.8b 4-arm run was never landed locally; if USER wants definitive resolution on 4-arm storage-chain item #3, a full-GPU re-run with sync-to-local is the path. Otherwise, the smoke-tier findings (ARM A fails / ARM B succeeds at CLASS via tag-retrieval) are honest scope-bounded conclusions, not chain-grade rulings.

## What this changes for the autonomous arc

- Path C still proceeds (sharper discriminator question; cell already running)
- The "storage chain item #3 partially-resolved-at-class-level" framing in my handoff + tracker should be tightened to "smoke-tier indication; full GPU not locally verified; treat as MEASURED_MECHANISM-at-smoke until full lands"
- Phase B subsequent windows when they parse 4-arm-era notes should note the smoke-vs-full caveat in `verified_off_data` rulings (conservative null for the 0.998-class claims)
- Director discipline going forward: read `metrics.json.run_mode` before absorbing cell-author dispositions; don't conflate smoke-tier indication with cert-grade ruling

## Standing
- Path B n3 SimVQ cell RUNNING on remote_cpu (~135min ETA from dispatch); watcher armed
- Path C ARM A projected-key revival RUNNING on local_cpu (~44min ETA from dispatch); watcher armed
- Both will land + spawn fresh hdi_skunkworks for landed-VET when complete
- Background Phase B windows 2-N remain available when active hdi_skunkworks slots open up
- USER returning in few hours; arc self-sustaining via ScheduleWakeup chain + watchers

— Research (Director / team lead). CERT 584 / 177268 atoms / cert_ledger 632 rows. 6 self-corrections owned this session.
