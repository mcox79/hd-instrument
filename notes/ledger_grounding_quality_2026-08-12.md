# LEDGER: grounding quality fix (tautology + closed-class refusal, provenance) -- 2026-08-12

Arc: correct the overstated `reading_grounding_v1` foundation ("3544 grounded concepts /
HARD_PASS") by auditing it, then fixing the acquisition loop so a grounding must be an
actual meaning link, not a same-sentence collocate or self-tautology, then re-running and
re-scoring on the same pre-registered rubric. Retroactively written from git history +
notes/grounding_quality_fix_2026-08-12.md; ledger + git log outrank recollection after
compaction.

- bce482b06 -- cycle2 reading-grounding FULL run lands, claimed HARD_PASS, foundation
  185->3544 concepts cumulative. (This is the claim later found overstated -- see next step.)
- 71a84d86f -- `exp_foundation_validation_harness_v1` cell added (3-claim store audit:
  correctness / coherence / can-reason). Built to check the cycle2 claim, not yet run.
- (uncommitted, evidence docs) `notes/landed_vet_foundation_validation_2026-08-12.md` --
  independent audit of the harness run: verdict OVERSTATED. Plumbing proven, meaning not;
  65.7% self-tautologies; 2/4 HARD_PASS band conditions cannot fail by construction.
- (uncommitted, evidence docs) `notes/foundation_grounding_sample_2026-08-12.md` -- direct
  50-pair + 20-pair (cross-only) hand audit quantifying quality: mixed 4%/6%/90%
  (MEANINGFUL/RELATED/NOISE), cross-only 35%/25%/40%.
- 3340df8d5 -- docs: correct the overstated HARD_PASS + 3544-concept claim in the living
  docs; mark stale THE_PLAN items superseded.
- 04b922c0e -- grounding quality fix landed: `hdlab/closed_class_lexicon.py` (new, UD +
  spaCy stop-word closed-class criterion), `hdlab/reading_grounding_loop.py`
  (`canonicalize(eligible=...)`, refusal gate via existing `mdl_gate_fn` hook, provenance +
  refusal ledgers), `hdlab/foundation_persistence.py` (FORMAT_VERSION 2, optional sidecars,
  v1-shape backward compatible). Pre-reg: `preregs/2026-08-12_grounding_quality_fix_v1.md`
  (bands B1-B6, anti-tuning commitment, FROZEN thresholds). Self-tests + verification suite
  green. Smoke gate PASS (discriminator fires: 401 refusals vs 211 groundings).
- (in flight, no commit yet) FULL re-run over the same 5 segments into
  `data/foundation/reading_grounding_v2_qualityfix/` (untracked by design, like all of
  data/foundation/). PID 30104. Log `data/exp_cycle3_full_run.log`. NOT YET SCORED.

## NEXT STEP FOR THIS ARC (see notes/STATUS.md for the live pointer)
Score B1-B6 once the full run completes; B3 (fresh 50-pair audit, same rubric+seed) is the
real discriminator and is NOT pre-decided. Independent landed-VET before trusting any verdict
language, same standard applied to v1. Append the result here with its commit hash when it
lands.
