# STATUS

AS OF: 2026-08-12T17:53:08Z | branch dataprep/mcguffey-graded-corpus | commit 04b922c0e

Rewritten in place every session. Never append -- if it doesn't fit in 6KB, it's an
evidence-doc claim with a pointer, not content that belongs here.

LEDGER CONVENTION: any multi-step arc keeps `notes/ledger_<arc-slug>.md`; first line names
the arc, one line per completed step with its commit hash; after compaction, the ledger +
`git log` outrank recollection. Active: `notes/ledger_grounding_quality_2026-08-12.md`.

## WHAT IS TRUE NOW (every claim sourced -- follow the pointer, don't trust this summary)
- The "3544 grounded concepts / HARD_PASS" claim for `data/foundation/reading_grounding_v1`
  is OVERSTATED. Plumbing (store/retrieve, lossless at scale) is proven; MEANING is not.
  65.7% (2328/3544) are self-tautologies `(X,GROUNDED_MEANING,X)`; top objects are function
  words (also/say/like/more/most). 2 of 4 HARD_PASS band conditions cannot fail by
  construction. -> `notes/landed_vet_foundation_validation_2026-08-12.md`
- Independent sample audit quantifies quality: mixed 50-sample = 4% MEANINGFUL / 6% RELATED
  / 90% NOISE; cross-grounded-only 20-sample = 35% / 25% / 40%. ->
  `notes/foundation_grounding_sample_2026-08-12.md`
- Fix implemented + committed (04b922c0e): refuse tautology groundings + closed-class
  filler objects at the gate, add per-fact provenance (source sentences). Self-tests green
  (closed_class_lexicon 5/5, reading_grounding_loop 8/8, foundation_persistence 7/7);
  verification suite 9/9 no regressions; smoke gate PASS (discriminator fires: 401 refusals
  vs 211 groundings). -> `notes/grounding_quality_fix_2026-08-12.md` secs 3.1-3.4
- `data/foundation/reading_grounding_v1` (7966 facts) is UNTOUCHED read-only evidence, never
  to be mutated -- confirmed by mtime + absence of v2 sidecars.
- Living docs (charter/plan/where-we-are-now) were stale by 1-4 days as of this morning's
  audit; touched today in commit 3340df8d5 to mark superseded items, but do not assume they
  are current -- this STATUS.md + the ledger are the durable source now.
  -> `notes/director_transition_digest_2026-08-12.md` Section F (contradictions)

## WHAT IS RUNNING
- FULL re-run of the grounding-quality fix (pre-registered, NOT yet scored): detached
  process PID 30104 (confirmed alive via tasklist at AS-OF time), writing
  `data/foundation/reading_grounding_v2_qualityfix/`. Progress log
  `data/exp_cycle3_full_run.log`: bootstrap segment COMPLETE (62 grounded/340 refused);
  last observed at AS-OF time was segment bio_new (5th of 5) chunk 55/76, elapsed ~388s.
  Cell: `experiments/exp_reading_grounding_loop_cycle3_groundingfix_v1.py`. When it finishes,
  metrics land at `data/exp_reading_grounding_loop_cycle3_groundingfix_v1/metrics.json`.
- No other queued/background work known at AS-OF time (director_kb continuous-ingest task
  flagged STALE by the session-start hook -- see BLOCKED).

## NEXT (ordered)
1. Poll `data/exp_cycle3_full_run.log` / PID 30104 for completion (all 5 segments done).
2. Score bands B1-B6 against `preregs/2026-08-12_grounding_quality_fix_v1.md`. B3 (fresh
   50-pair audit, same rubric+seed as the prior sample audit) is the real discriminator:
   PASS needs MEANINGFUL >= 35% AND NOISE <= 40%. Thresholds are pre-committed FROZEN
   (anti-tuning) -- do not adjust after seeing B3.
3. Independent landed-VET of the v2 result (hdi_skunkworks) before any HARD_PASS language,
   same rigor as `landed_vet_foundation_validation_2026-08-12.md` applied to v1.
4. Append the verdict + commit hash to `notes/ledger_grounding_quality_2026-08-12.md` and
   rewrite this STATUS.md's AS-OF/WHAT-IS-TRUE-NOW section in place.
5. Only after B3 lands: resume USER's "focus on 2 and 3" (validate foundation
   correctness+organization; scale/speed) -- do NOT resume foundation-size growth first.
6. Separately: capability registry audit is 17h+ stale, 69 unregistered hdlab modules
   (session-start hook durability gate) -- not this arc's blocker, but overdue.

## BLOCKED
- DO NOT TOUCH (concurrent session / detached process, standing constraint): hdlab/
  lexical_similarity.py, data/capability_registry.jsonl, hdlab/reading_grounding_loop.py,
  anything under data/foundation/. Tracking-cleanup on the registry is blocked pending the
  concurrent session finishing.
- director_kb continuous-ingest index STALE (session-start hook: scan_gap ~4198s at
  AS-OF time) -- not actioned this session, flagged for whoever picks up infra next.

## DO NOT REDO
See `notes/director_transition_digest_2026-08-12.md` Section C (Dead Ends) for the full,
sourced list -- not copied here. Highlights only: glass-box-only entity-world-knowledge
acquisition (closed, robust); passage-context binding for disambiguation (falsified);
recency-shaped relational selection as a fix class (repeatedly fails the recency-trap);
WIQA causal-chain-loop as flagship (falsified, leaky benchmark).
